package org.acme.model;

public record OrderResult(
        String orderId,
        double amount,
        String customerId,
        String status,
        String risk,
        String segment,
        String source) {
}
