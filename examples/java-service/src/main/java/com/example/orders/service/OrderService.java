package com.example.orders.service;

import com.example.orders.model.Order;
import com.example.orders.store.OrderRepository;

public class OrderService {
    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    public Order placeOrder(String customerId, String sku) {
        Order order = new Order("ord-" + customerId, customerId, sku);
        repository.save(order);
        return order;
    }
}
