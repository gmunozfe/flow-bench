package org.acme;

import org.acme.model.EnrichmentResponse;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/mock/enrich")
@RegisterRestClient(configKey = "enrichment-api")
@Produces(MediaType.APPLICATION_JSON)
public interface EnrichmentClient {

    @GET
    @Path("/{orderId}")
    EnrichmentResponse enrich(
            @PathParam("orderId") String orderId,
            @QueryParam("delayMs") Integer delayMs);
}
