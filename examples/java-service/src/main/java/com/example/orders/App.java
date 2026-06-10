package com.example.orders;

import com.example.orders.model.Order;
import com.example.orders.service.OrderService;
import com.example.orders.store.InMemoryOrderRepository;

public class App {
    public static void main(String[] args) {
        OrderService service = new OrderService(new InMemoryOrderRepository());
        Order order = service.placeOrder("cust-001", "book");
        System.out.println(order.summary());
    }
}
