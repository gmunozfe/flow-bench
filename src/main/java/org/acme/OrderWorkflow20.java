package org.acme;

import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.set;

import jakarta.enterprise.context.ApplicationScoped;

import io.quarkiverse.flow.Flow;
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.FuncWorkflowBuilder;

@ApplicationScoped
public class OrderWorkflow20 extends Flow {

    @Override
    public Workflow descriptor() {
        return FuncWorkflowBuilder.workflow("order-workflow-20")
                .tasks(
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "RECEIVED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "VALIDATED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "PRICING_STARTED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "PRICED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "INVENTORY_CHECK_STARTED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "INVENTORY_CONFIRMED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "RESERVATION_STARTED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "RESERVED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "PAYMENT_INITIATED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "PAYMENT_AUTHORIZED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "PAYMENT_CAPTURED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "FULFILLMENT_STARTED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "PICKED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "PACKED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "READY_TO_SHIP"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "SHIPPED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "IN_TRANSIT"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "OUT_FOR_DELIVERY"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "DELIVERED"
                        }
                        """),
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "COMPLETED_20_STEPS"
                        }
                        """)
                )
                .build();
    }
}

