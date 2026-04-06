package org.acme;

import jakarta.enterprise.context.ApplicationScoped;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import com.fasterxml.jackson.databind.ObjectMapper;

@ApplicationScoped
public class JsonService {

    private final ObjectMapper mapper = new ObjectMapper();

    // STEP 2
    public Map<String, Object> generate(Map<String, Object> input) {

        int items = (int) input.getOrDefault("items", 1000);

        Map<String, Object> data = new HashMap<>();

        for (int i = 0; i < items; i++) {
            data.put("item_" + i, Map.of(
                    "id", i,
                    "value", UUID.randomUUID().toString()
            ));
        }

        return Map.of(
                "data", data,
                "iterations", input.get("iterations"),
                "status", "GENERATED"
        );
    }

    // STEP 3 + 5
    public Map<String, Object> process(Map<String, Object> input) {

        try {
            Map<String, Object> data = (Map<String, Object>) input.get("data");

            long start = System.currentTimeMillis();

            String json = mapper.writeValueAsString(data);
            Map<String, Object> parsed = mapper.readValue(json, Map.class);

            long duration = System.currentTimeMillis() - start;

            return Map.of(
                    "data", parsed,
                    "iterations", input.get("iterations"),
                    "size", json.length(),
                    "durationMs", duration,
                    "status", "PROCESSED"
            );

        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // STEP 4
    public Map<String, Object> mutate(Map<String, Object> input) {

        Map<String, Object> data = (Map<String, Object>) input.get("data");
        int iterations = (int) input.getOrDefault("iterations", 3);

        for (int i = 0; i < iterations; i++) {
            data.put("mutation_" + i, UUID.randomUUID().toString());
        }

        return Map.of(
                "data", data,
                "iterations", iterations,
                "status", "MUTATED"
        );
    }
}
