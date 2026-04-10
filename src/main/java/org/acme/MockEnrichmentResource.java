package org.acme;

import java.util.LinkedHashMap;
import java.util.Map;

import io.smallrye.common.annotation.Blocking;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;

@Path("/mock/enrich")
@ApplicationScoped
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class MockEnrichmentResource {

    @POST
    @Blocking
    public Map<String, Object> enrich(Map<String, Object> input,
                                      @QueryParam("delayMs") Integer delayMs) throws InterruptedException {
        int delay = delayMs != null ? delayMs : 10;

        if (delay > 0) {
            Thread.sleep(delay);
        }

        Map<String, Object> result = new LinkedHashMap<>(input);
        result.put("risk", "MEDIUM");
        result.put("segment", "STANDARD");
        result.put("source", "mock-service");
        return result;
    }
}
