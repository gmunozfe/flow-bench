package org.acme;

import org.acme.model.OrderRequest;
import org.jboss.resteasy.reactive.ResponseStatus;

import io.quarkiverse.flow.Flow;
import io.smallrye.mutiny.Uni;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public abstract class AbstractOrderResource<T extends Flow> {

    protected abstract T workflow();

    @POST
    @ResponseStatus(200)
    public Uni<Object> start(OrderRequest request) {
        return workflow()
                .startInstance(request)
                .onItem()
                .transform(w -> w.as(Object.class).orElseThrow());
    }
}
