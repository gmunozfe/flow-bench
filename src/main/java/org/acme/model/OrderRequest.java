package org.acme.model;

public record OrderRequest(String orderId, double amount, String customerId) {
}
