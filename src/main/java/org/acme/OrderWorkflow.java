package org.acme;

import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.set;

import jakarta.enterprise.context.ApplicationScoped;

import io.quarkiverse.flow.Flow;
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.FuncWorkflowBuilder;

@ApplicationScoped
public class OrderWorkflow extends Flow {

    @Override
    public Workflow descriptor() {
        return FuncWorkflowBuilder.workflow("order-workflow")
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
                          status: "COMPLETED"
                        }
                        """)
                )
                .build();
    }
}
