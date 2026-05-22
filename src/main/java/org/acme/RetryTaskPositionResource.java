package org.acme;

import java.util.Map;

import io.quarkiverse.flow.Flow;
import io.smallrye.common.annotation.Identifier;
import io.smallrye.mutiny.Uni;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/retry-task-position-test")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class RetryTaskPositionResource {

    @Inject
    @Identifier("bench:retry-task-position-test")
    Flow workflow;

    @POST
    public Uni<Map<String, Object>> run(Map<String, Object> input) {
        return workflow.startInstance(input)
                .onItem()
                .transform(model -> model.asMap().orElse(Map.of()));
    }
}
