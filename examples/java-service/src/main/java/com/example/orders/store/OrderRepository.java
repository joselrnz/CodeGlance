package com.example.orders.store;

import com.example.orders.model.Order;

public interface OrderRepository {
    void save(Order order);

    Order find(String id);
}
