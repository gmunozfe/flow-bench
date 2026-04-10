package org.acme;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.acme.model.ExternalCallResponse;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@ApplicationScoped
public class ExternalCallService {

    @Inject
    @RestClient
    ExternalCallClient externalCallClient;

    public ExternalCallResponse call(String orderId, int delayMs) {
        return externalCallClient.call(orderId, delayMs);
    }
}
