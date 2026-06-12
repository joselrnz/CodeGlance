from codeglance.processes import BusinessFlow, Domain, ProcessMap, ProcessStep, extract_process_map
from codeglance.schema import Edge, KnowledgeGraph, Node, Project


def _node(path, summary="", tags=None):
    return Node(
        id=f"file:{path}",
        type="file",
        name=path.rsplit("/", 1)[-1],
        filePath=path,
        summary=summary,
        tags=tags or [],
    )


def test_process_models_are_importable():
    domain = Domain(key="cart", name="Cart", node_ids=["file:cart.py"], evidence=["cart.py"], confidence=0.9)
    step = ProcessStep(
        order=1,
        label="Cart controller",
        domain_key="cart",
        node_id="file:cart.py",
        file_path="cart.py",
        role="controller",
        evidence=["controller role"],
        confidence=0.8,
    )
    flow = BusinessFlow(
        id="flow:cart",
        name="Cart Flow",
        domain_key="cart",
        steps=[step],
        node_ids=["file:cart.py"],
        evidence=["cart domain"],
        confidence=0.8,
    )
    process_map = ProcessMap(domains=[domain], flows=[flow], evidence=["cart.py"], confidence=0.8)

    assert process_map.processes == [flow]
    assert process_map.domains[0].name == "Cart"
    assert process_map.flows[0].steps[0].role == "controller"


def test_extract_process_map_handles_empty_graph():
    process_map = extract_process_map(KnowledgeGraph(project=Project(name="empty")))

    assert process_map.domains == []
    assert process_map.flows == []
    assert process_map.processes == []
    assert process_map.confidence == 0.0
    assert process_map.evidence == []


def test_extract_process_map_groups_business_domains_with_evidence():
    graph = KnowledgeGraph(
        project=Project(name="shop"),
        nodes=[
            _node("src/api/cart_controller.py", "HTTP endpoint for cart checkout"),
            _node("src/services/cart_service.py", "Coordinates cart checkout"),
            _node("src/services/payment_service.py", "Captures payment"),
            _node("src/domain/order.py", "Order aggregate and order state"),
            _node("src/services/notification_service.py", "Sends order notifications"),
            _node("src/lib/string_utils.py", "Formatting helpers"),
        ],
        edges=[
            Edge("file:src/api/cart_controller.py", "file:src/services/cart_service.py", "imports"),
            Edge("file:src/services/cart_service.py", "file:src/services/payment_service.py", "imports"),
            Edge("file:src/services/cart_service.py", "file:src/domain/order.py", "imports"),
            Edge("file:src/services/cart_service.py", "file:src/services/notification_service.py", "imports"),
        ],
    )

    process_map = extract_process_map(graph)
    domains = {domain.key: domain for domain in process_map.domains}

    assert {"cart", "payment", "order", "notification"} <= set(domains)
    assert "lib" not in domains and "string" not in domains
    assert all(domain.confidence > 0 for domain in domains.values())
    assert any("cart_controller.py" in item for item in domains["cart"].evidence)


def test_extract_process_map_builds_ordered_evidence_backed_flow():
    graph = KnowledgeGraph(
        project=Project(name="shop"),
        nodes=[
            _node("src/api/cart_controller.py", "Receives checkout requests"),
            _node("src/services/auth_service.py", "Authorizes checkout"),
            _node("src/services/cart_service.py", "Validates cart and checkout"),
            _node("src/services/payment_service.py", "Captures customer payment"),
            _node("src/domain/order.py", "Creates order records"),
            _node("src/services/notification_service.py", "Sends order confirmation"),
        ],
        edges=[
            Edge("file:src/api/cart_controller.py", "file:src/services/auth_service.py", "imports"),
            Edge("file:src/api/cart_controller.py", "file:src/services/cart_service.py", "imports"),
            Edge("file:src/services/cart_service.py", "file:src/services/payment_service.py", "imports"),
            Edge("file:src/services/cart_service.py", "file:src/domain/order.py", "imports"),
            Edge("file:src/domain/order.py", "file:src/services/notification_service.py", "imports"),
        ],
    )

    process_map = extract_process_map(graph)
    flow = next(flow for flow in process_map.flows if flow.domain_key == "cart")

    assert flow.name == "Cart Flow"
    assert flow.confidence > 0
    assert len(flow.steps) >= 5
    assert [step.order for step in flow.steps] == list(range(1, len(flow.steps) + 1))
    assert [step.role for step in flow.steps[:5]] == ["controller", "auth", "service", "service", "domain"]
    assert flow.steps[-1].domain_key == "notification"
    assert all(step.evidence for step in flow.steps)
    assert all(step.node_id in flow.node_ids for step in flow.steps)
