package org.acme;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Path;

@Path("/bench/order100")
@ApplicationScoped
public class OrderResource100 extends AbstractOrderResource<OrderWorkflow100> {

    @Inject
    OrderWorkflow100 workflow;

    @Override
    protected OrderWorkflow100 workflow() {
        return workflow;
    }
}
