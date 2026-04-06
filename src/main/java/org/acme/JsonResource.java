package org.acme;

import jakarta.inject.Inject;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import java.util.Map;

import org.jboss.logging.Logger;

import io.smallrye.mutiny.Uni;
import io.smallrye.common.annotation.Blocking;

@Path("/bench/json")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
//@Blocking
public class JsonResource {

    private static final Logger LOG = Logger.getLogger(JsonResource.class);

    @Inject
    JsonProcessingWorkflow workflow;

    @POST
    public Uni<Map<String, Object>> start(Map<String, Object> request) {
        LOG.infov("[JSON] request={0}", request);

        return workflow.startInstance(request)
                .map(wf -> {
                    Map<String, Object> output = wf.asMap().orElse(Map.of());
                    LOG.infov("[JSON] output={0}", output);
                    return output;
                });
    }
}
