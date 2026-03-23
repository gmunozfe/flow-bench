package org.acme;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;

import org.acme.model.EnrichmentResponse;

@Path("/mock/enrich")
@ApplicationScoped
@Produces(MediaType.APPLICATION_JSON)
public class MockEnrichmentResource {

    @GET
    @Path("/{orderId}")
    public EnrichmentResponse enrich(
            @PathParam("orderId") String orderId,
            @QueryParam("delayMs") Integer delayMs) throws InterruptedException {

        int delay = delayMs == null ? 10 : delayMs;
        if (delay > 0) {
            Thread.sleep(delay);
        }

        String risk = Math.abs(orderId.hashCode()) % 2 == 0 ? "LOW" : "MEDIUM";
        String segment = Math.abs(orderId.hashCode()) % 3 == 0 ? "VIP" : "STANDARD";

        return new EnrichmentResponse(risk, segment, "mock-service");
    }
}
