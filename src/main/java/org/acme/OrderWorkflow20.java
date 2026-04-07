package org.acme;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class OrderWorkflow20 extends AbstractOrderWorkflow {

    @Override
    protected String workflowName() {
        return "order-workflow-20";
    }

    @Override
    protected int taskCount() {
        return 20;
    }
}
