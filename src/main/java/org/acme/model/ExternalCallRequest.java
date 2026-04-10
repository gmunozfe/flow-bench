package org.acme.model;

public class ExternalCallRequest {

    public String orderId;
    public double amount;
    public String customerId;
    public Integer delayMs;

    public ExternalCallRequest() {
    }

    public ExternalCallRequest(String orderId, double amount, String customerId, Integer delayMs) {
        this.orderId = orderId;
        this.amount = amount;
        this.customerId = customerId;
        this.delayMs = delayMs;
    }
}
