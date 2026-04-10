package org.acme;

import org.acme.model.ExternalCallResponse;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/mock/external")
@RegisterRestClient(configKey = "external-call-api")
@Produces(MediaType.APPLICATION_JSON)
public interface ExternalCallClient {

    @GET
    @Path("/{orderId}")
    ExternalCallResponse call(
            @PathParam("orderId") String orderId,
            @QueryParam("delayMs") Integer delayMs);
}
