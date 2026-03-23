package org.acme;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import org.acme.model.OrderRequest;
import org.jboss.resteasy.reactive.ResponseStatus;

import io.smallrye.mutiny.Uni;

@Path("/bench/order-enrich")
@ApplicationScoped
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class OrderEnrichmentResource {

    @Inject
    OrderEnrichmentWorkflow workflow;

    @POST
    @ResponseStatus(200)
    public Uni<Object> start(OrderRequest request) {
        return workflow
                .startInstance(request)
                .onItem()
                .transform(w -> w.as(Object.class).orElseThrow());
    }
}
