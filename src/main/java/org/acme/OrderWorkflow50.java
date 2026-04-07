package org.acme;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class OrderWorkflow50 extends AbstractOrderWorkflow {

    @Override
    protected String workflowName() {
        return "order-workflow-50";
    }

    @Override
    protected int taskCount() {
        return 50;
    }
}
