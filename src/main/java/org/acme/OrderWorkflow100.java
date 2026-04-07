package org.acme;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class OrderWorkflow100 extends AbstractOrderWorkflow {

    @Override
    protected String workflowName() {
        return "order-workflow-100";
    }

    @Override
    protected int taskCount() {
        return 100;
    }
}
