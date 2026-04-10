package org.acme;

import java.util.LinkedHashMap;
import java.util.Map;

import org.acme.model.TaskOutputRequest;
import org.jboss.resteasy.reactive.ResponseStatus;

import io.smallrye.mutiny.Uni;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/bench/taskoutput-persistence")
@ApplicationScoped
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class TaskOutputResource {

    @Inject
    TaskOutputPersistenceWorkflow workflow;

    @Inject
    TaskOutputDataFactory factory;

    @POST
    @ResponseStatus(200)
    public Uni<Object> start(TaskOutputRequest request) {
        int sizeKb = request.prebuiltSizeKb > 0 ? request.prebuiltSizeKb : 250;

        Map<String, Object> input = new LinkedHashMap<>();
        input.put("taskOutput", factory.getPrebuiltTaskOutput(sizeKb));
        input.put("taskOutputSizeKb", sizeKb);

        return workflow.startInstance(input)
                .onItem()
                .transform(w -> w.as(Object.class).orElseThrow());
    }
}
