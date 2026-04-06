package org.acme;

import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.set;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import io.quarkiverse.flow.Flow;
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.FuncTaskItemListBuilder;
import io.serverlessworkflow.fluent.func.FuncWorkflowBuilder;

public abstract class AbstractOrderWorkflow extends Flow {

    protected abstract String workflowName();

    protected abstract int stepCount();

    @Override
    public Workflow descriptor() {
        FuncWorkflowBuilder builder = FuncWorkflowBuilder.workflow(workflowName());

        List<Consumer<FuncTaskItemListBuilder>> tasks = new ArrayList<>();
        for (String status : statuses(stepCount())) {
            tasks.add(set(stepExpr(status)));
        }

        @SuppressWarnings("unchecked")
        Consumer<FuncTaskItemListBuilder>[] taskArray =
                tasks.toArray(new Consumer[0]);

        return builder.tasks(taskArray).build();
    }

    protected List<String> statuses(int count) {
        List<String> result = new ArrayList<>();

        String[] base = {
                "RECEIVED",
                "VALIDATED",
                "PRICING_STARTED",
                "PRICED",
                "INVENTORY_CHECK_STARTED",
                "INVENTORY_CONFIRMED",
                "RESERVATION_STARTED",
                "RESERVED",
                "PAYMENT_INITIATED",
                "PAYMENT_AUTHORIZED",
                "PAYMENT_CAPTURED",
                "FULFILLMENT_STARTED",
                "PICKED",
                "PACKED",
                "READY_TO_SHIP",
                "SHIPPED",
                "IN_TRANSIT",
                "OUT_FOR_DELIVERY",
                "DELIVERED"
        };

        for (int i = 0; i < count - 1; i++) {
            if (i < base.length) {
                result.add(base[i]);
            } else {
                result.add("STEP_" + (i + 1));
            }
        }

        result.add("COMPLETED_" + count + "_STEPS");
        return result;
    }

    protected String stepExpr(String status) {
        return """
            {
              orderId: .orderId,
              amount: .amount,
              customerId: .customerId,
              status: "%s"
            }
            """.formatted(status);
    }
}
