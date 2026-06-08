# microservices — ScopingLang example

A tiny e-commerce backend split into independent services under `services/`.
Each service directory is treated as a **domain**; the imports between services
become **flows** in ScopingLang's **Domain** view (animated dashed edges).

```bash
scopinglang examples/microservices
# then click  Domain  in the header
```

Flows you should see:

- **gateway** → orders, cart, catalog
- **orders** → payments, shipping, notifications, catalog
- **cart** → catalog
- **recommendations** → catalog

`catalog` is the hub every other domain depends on.
