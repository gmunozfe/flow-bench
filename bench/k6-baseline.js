import http from "k6/http";
import { check } from "k6";
import { Trend } from "k6/metrics";

const appLatency = new Trend("app_latency", true);

export const options = {
  scenarios: {
    starts: {
      executor: "constant-arrival-rate",
      rate: __ENV.RATE ? parseInt(__ENV.RATE, 10) : 50,
      timeUnit: "1s",
      duration: __ENV.DURATION || "2m",
      preAllocatedVUs: 500,
      maxVUs: 2000,
    },
  },
};

export default function () {
  const base = __ENV.BASE_URL || "http://localhost:8080";
  const path = __ENV.PATH || "/hello-flow";

  const res = http.get(`${base}${path}`, {
    headers: { "Content-Type": "application/json" },
    tags: { path },
  });

  appLatency.add(res.timings.duration, { path });

  check(res, { "200": (r) => r.status === 200 });
}
