package org.acme;

import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.get;
import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.set;

import java.util.Map;

import jakarta.enterprise.context.ApplicationScoped;

import org.acme.model.EnrichmentResponse;

import io.quarkiverse.flow.Flow;
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.FuncWorkflowBuilder;
import io.serverlessworkflow.impl.TaskContextData;
import io.serverlessworkflow.impl.WorkflowContextData;

@ApplicationScoped
public class OrderEnrichmentWorkflow extends Flow {

    @Override
    public Workflow descriptor() {
        String endpoint = "http://localhost:8080/mock/enrich/${orderId}?delayMs=10";

        return FuncWorkflowBuilder.workflow("order-enrichment-workflow")
                .tasks(
                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
                          status: "RECEIVED"
                        }
                        """),

                    get(endpoint)
                        .outputAs((EnrichmentResponse body,
                                   WorkflowContextData wf,
                                   TaskContextData task) -> {
                            Map<String, Object> input = task.input().asMap().orElseThrow();

                            return Map.of(
                                    "orderId", input.get("orderId"),
                                    "amount", input.get("amount"),
                                    "customerId", input.get("customerId"),
                                    "risk", body.risk(),
                                    "segment", body.segment(),
                                    "source", body.source(),
                                    "status", "ENRICHED"
                            );
                        }, EnrichmentResponse.class),

                    set("""
                        {
                          orderId: .orderId,
                          amount: .amount,
                          customerId: .customerId,
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
