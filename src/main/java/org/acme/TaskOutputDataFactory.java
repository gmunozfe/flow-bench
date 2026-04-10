package org.acme;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class TaskOutputDataFactory {

    // Estimation from previous tests
    private static final int BYTES_PER_ITEM = 256;

    private final Map<Integer, Map<String, Object>> prebuiltBySizeKb = new LinkedHashMap<>();

    @PostConstruct
    void init() {
        // Add the sizes you want ready at startup.
       /* prebuiltBySizeKb.put(100, buildPrebuiltTaskOutput(100));
        prebuiltBySizeKb.put(250, buildPrebuiltTaskOutput(250));
        prebuiltBySizeKb.put(500, buildPrebuiltTaskOutput(500));
        prebuiltBySizeKb.put(1000, buildPrebuiltTaskOutput(1000));
        prebuiltBySizeKb.put(2500, buildPrebuiltTaskOutput(2500));
        prebuiltBySizeKb.put(5000, buildPrebuiltTaskOutput(5000));
	prebuiltBySizeKb.put(10000, buildPrebuiltTaskOutput(10000));
	prebuiltBySizeKb.put(20000, buildPrebuiltTaskOutput(20000));*/
	//prebuiltBySizeKb.put(50000, buildPrebuiltTaskOutput(50000));
	prebuiltBySizeKb.put(100000, buildPrebuiltTaskOutput(100000));
    }

    public Map<String, Object> getPrebuiltTaskOutput(int sizeKb) {
        Map<String, Object> result = prebuiltBySizeKb.get(sizeKb);
        if (result == null) {
            throw new IllegalArgumentException(
                    "Unsupported prebuiltSizeKb=" + sizeKb +
                    ". Supported values: " + prebuiltBySizeKb.keySet());
        }
        return result;
    }

    private Map<String, Object> buildPrebuiltTaskOutput(int targetSizeKb) {
        int targetBytes = Math.max(1, targetSizeKb) * 1024;

        List<Map<String, Object>> items = new ArrayList<>();
        int currentBytes = 0;
        int i = 0;

        while (currentBytes < targetBytes) {
            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("id", i);
            entry.put("name", "item-" + i);
            entry.put("category", "benchmark");
            entry.put("status", "ACTIVE");
            entry.put("description", "x".repeat(180));

            items.add(Map.copyOf(entry));

            // Approximate size control, calibrated from previous measurements.
            currentBytes += BYTES_PER_ITEM;
            i++;
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("items", List.copyOf(items));
        result.put("itemsCount", items.size());
        result.put("targetSizeKb", targetSizeKb);

        return Map.copyOf(result);
    }
}
