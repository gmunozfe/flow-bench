package org.acme;

import java.util.Map;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import org.jboss.logging.Logger;
import org.jboss.resteasy.reactive.ResponseStatus;

import io.serverlessworkflow.impl.WorkflowDefinition;
import io.serverlessworkflow.impl.WorkflowInstance;
import io.smallrye.common.annotation.Identifier;
import io.smallrye.mutiny.Uni;

@Path("/hello-flow")
@ApplicationScoped
public class HelloResource {

    private static final Logger LOG = Logger.getLogger(HelloResource.class);

    @Inject
    @Identifier("org.acme.HelloWorkflow")
    WorkflowDefinition helloWorkflowDefinition;

    @GET
    @ResponseStatus(200)
    public Uni<Object> hello() {
        WorkflowInstance instance = helloWorkflowDefinition.instance(Map.of());
        //LOG.infof("Workflow instance id=%s", instance.id());

        return Uni.createFrom().completionStage(
                instance.start().thenApply(output -> {
                    return output.as(Message.class).orElseThrow();
                })
        );
    }
}
