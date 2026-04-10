package org.acme;

import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.post;
import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.set;

import jakarta.enterprise.context.ApplicationScoped;

import io.quarkiverse.flow.Flow;
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.FuncWorkflowBuilder;

@ApplicationScoped
public class ExternalCallWorkflow extends Flow {

    @Override
    public Workflow descriptor() {
        return FuncWorkflowBuilder.workflow("order-external-call-workflow")
                .tasks(
                        set("""
                            {
                              orderId: .orderId,
                              amount: .amount,
                              customerId: .customerId,
                              delayMs: (.delayMs // 10),
                              status: "RECEIVED"
                            }
                            """),
                        post(
                            "${ . }",
                            "${ \"http://localhost:8080/mock/external?delayMs=\" + ((.delayMs // 10) | tostring) }"
                        ),
                        set("""
                            {
                              orderId: .orderId,
                              amount: .amount,
                              customerId: .customerId,
                              delayMs: .delayMs,
                              risk: .risk,
                              segment: .segment,
                              source: .source,
                              status: "COMPLETED"
                            }
                            """)
                )
                .build();
    }
}
