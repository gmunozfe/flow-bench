package org.acme;

import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.set;

import jakarta.enterprise.context.ApplicationScoped;

import io.quarkiverse.flow.Flow;
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.FuncWorkflowBuilder;

@ApplicationScoped
public class JsonProcessingWorkflow extends Flow {

    @Override
    public Workflow descriptor() {
        return FuncWorkflowBuilder.workflow("json-processing-workflow")
                .tasks(

                    set("""
                    {
                      items: (.items // 1000),
                      iterations: (.iterations // 3),
                      status: "STARTED"
                    }
                    """),

                    set("""
                    {
                      data: [range(0; .items) | {
                        id: .,
                        value: ("val-" + (. | tostring))
                      }],
                      iterations: .iterations,
                      status: "GENERATED"
                    }
                    """),

                    set("""
                    . as $root |
                    {
                      data: [$root.data[] | . + {processed: true}],
                      iterations: $root.iterations,
                      status: "PROCESSED"
                    }
                    """),

                    set("""
                    . as $root |
                    {
                      data: [
                        $root.data[] | . + {
                          mutations: [range(0; $root.iterations) | ("m-" + (. | tostring))]
                        }
                      ],
                      iterations: $root.iterations,
                      status: "MUTATED"
                    }
                    """),

                    set("""
                    . as $root |
                    {
                      itemsCount: ($root.data | length),
                      iterations: $root.iterations,
                      mutationsPerItem: $root.iterations,
                      totalMutationEntries: (($root.data | length) * $root.iterations),
                      status: "COMPLETED"
                    }
                    """)

                )
                .build();
    }
}
