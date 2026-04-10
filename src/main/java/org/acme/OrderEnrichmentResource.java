package org.acme;

import org.acme.model.OrderEnrichmentRequest;
import org.jboss.resteasy.reactive.ResponseStatus;

import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/bench/enrichment")
@ApplicationScoped
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class OrderEnrichmentResource {

    @Inject
    OrderEnrichmentWorkflow workflow;

    @POST
    @ResponseStatus(200)
    public Uni<Object> start(OrderEnrichmentRequest request) {
        return workflow
                .startInstance(request)
                .onItem()
                .transform(w -> w.as(Object.class).orElseThrow());
    }
}
