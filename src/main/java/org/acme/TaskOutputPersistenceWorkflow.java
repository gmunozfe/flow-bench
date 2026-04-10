package org.acme;

import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.set;

import jakarta.enterprise.context.ApplicationScoped;

import io.quarkiverse.flow.Flow;
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.FuncWorkflowBuilder;

@ApplicationScoped
public class TaskOutputPersistenceWorkflow extends Flow {

    @Override
    public Workflow descriptor() {
        return FuncWorkflowBuilder.workflow("json-taskoutput-workflow")
                .tasks(
                        set("""
                            {
                              taskOutput: .taskOutput,
                              taskOutputSizeKb: .taskOutputSizeKb,
                              status: "LOADED"
                            }
                            """),
                        set("""
                            {
                              taskOutput: .taskOutput,
                              taskOutputSizeKb: .taskOutputSizeKb,
                              status: "COMPLETED"
                            }
                            """)
                )
                .build();
    }
}
