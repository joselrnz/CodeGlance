package com.example.orders.model;

public class Order {
    private final String id;
    private final String customerId;
    private final String sku;

    public Order(String id, String customerId, String sku) {
        this.id = id;
        this.customerId = customerId;
        this.sku = sku;
    }

    public String id() {
        return id;
    }

    public String summary() {
        return id + " for " + customerId + " contains " + sku;
    }
}
