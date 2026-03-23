package org.acme;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.acme.model.EnrichmentResponse;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@ApplicationScoped
public class EnrichmentService {

    @Inject
    @RestClient
    EnrichmentClient enrichmentClient;

    public EnrichmentResponse enrich(String orderId, int delayMs) {
        return enrichmentClient.enrich(orderId, delayMs);
    }
}
