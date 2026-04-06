package org.acme;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Path;

@Path("/bench/order50")
@ApplicationScoped
public class OrderResource50 extends AbstractOrderResource<OrderWorkflow50> {

    @Inject
    OrderWorkflow50 workflow;

    @Override
    protected OrderWorkflow50 workflow() {
        return workflow;
    }
}
