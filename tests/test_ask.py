import json

from codeglance.ask import Evidence, QueryResult, build_documents, render_answer, search
from codeglance.schema import Edge, KnowledgeGraph, Layer, Node, Project, TourStep


def _qa_graph() -> KnowledgeGraph:
    return KnowledgeGraph(
        project=Project(name="shop", languages=["python"], description="Small storefront service"),
        nodes=[
            Node(
                id="file:src/billing.py",
                type="file",
                name="billing.py",
                filePath="src/billing.py",
                summary="Coordinates invoice creation and Stripe payment capture.",
                tags=["python", "payments"],
            ),
            Node(
                id="class:src/billing.py:BillingService",
                type="class",
                name="BillingService",
                filePath="src/billing.py",
                summary="Creates invoices, charges customers, and records payment receipts.",
                tags=["billing", "stripe"],
                signature="class BillingService",
                docstring="High level payment workflow for checkout invoices.",
            ),
            Node(
                id="file:src/catalog.py",
                type="file",
                name="catalog.py",
                filePath="src/catalog.py",
                summary="Loads product records and exposes catalog search helpers.",
                tags=["python", "catalog"],
            ),
        ],
        edges=[
            Edge(source="file:src/billing.py", target="class:src/billing.py:BillingService", type="contains"),
            Edge(source="class:src/billing.py:BillingService", target="file:src/catalog.py", type="depends_on"),
        ],
        layers=[
            Layer(
                id="layer:payments",
                name="Payments",
                description="Checkout and invoice payment processing.",
                nodeIds=["file:src/billing.py", "class:src/billing.py:BillingService"],
            )
        ],
        tour=[
            TourStep(
                order=1,
                title="Start with billing",
                description="BillingService is the entry point for invoice checkout.",
                nodeIds=["class:src/billing.py:BillingService"],
                languageLesson="Python service classes group the checkout workflow.",
            )
        ],
    )


def test_build_documents_indexes_nodes_layers_and_tour():
    docs = build_documents(_qa_graph())
    ids = {doc.id for doc in docs}

    assert "node:class:src/billing.py:BillingService" in ids
    assert "layer:layer:payments" in ids
    assert "tour:1" in ids

    billing_doc = next(doc for doc in docs if doc.id == "node:class:src/billing.py:BillingService")
    assert billing_doc.node_ids == ["class:src/billing.py:BillingService"]
    assert billing_doc.paths == ["src/billing.py"]
    assert "High level payment workflow" in billing_doc.text


def test_search_ranks_relevant_evidence_with_citations():
    result = search("Where is Stripe payment capture handled?", _qa_graph(), max_results=3)

    assert isinstance(result, QueryResult)
    assert result.insufficient is False
    assert result.evidence
    assert result.evidence[0].node_id == "class:src/billing.py:BillingService"
    assert result.evidence[0].path == "src/billing.py"
    assert result.evidence[0].score > 0
    assert any(ev.source == "layer" for ev in result.evidence)


def test_render_answer_markdown_is_extractive_and_cited():
    answer = render_answer("How does checkout billing work?", _qa_graph(), max_results=2)

    assert "Based on the knowledge graph" in answer
    assert "BillingService" in answer
    assert "`src/billing.py`" in answer
    assert "`class:src/billing.py:BillingService`" in answer
    assert "Evidence" in answer


def test_render_answer_json_has_stable_shape():
    payload = json.loads(render_answer("checkout invoices", _qa_graph(), max_results=2, format="json"))

    assert payload["question"] == "checkout invoices"
    assert payload["insufficient"] is False
    assert payload["evidence"][0]["node_id"] == "class:src/billing.py:BillingService"
    assert payload["evidence"][0]["path"] == "src/billing.py"
    assert "answer" in payload


def test_render_answer_reports_insufficient_evidence():
    answer = render_answer("How is OAuth token rotation implemented?", _qa_graph())

    assert "not enough evidence" in answer.lower()
    assert "OAuth token rotation" in answer

    payload = json.loads(render_answer("OAuth token rotation", _qa_graph(), format="json"))
    assert payload["insufficient"] is True
    assert payload["evidence"] == []


def test_models_serialize_to_plain_dicts():
    evidence = Evidence(
        node_id="node-1",
        path="src/app.py",
        title="App",
        kind="function",
        snippet="Starts the app.",
        score=2.5,
        source="node",
    )
    result = QueryResult(question="what starts?", answer="App starts.", evidence=[evidence])

    assert evidence.to_dict()["score"] == 2.5
    assert result.to_dict()["evidence"][0]["node_id"] == "node-1"
