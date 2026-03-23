import http from "k6/http";
import { check } from "k6";

export const options = {
  scenarios: {
    starts: {
      executor: "constant-arrival-rate",
      rate: __ENV.RATE ? parseInt(__ENV.RATE) : 50,
      timeUnit: "1s",
      duration: __ENV.DURATION || "2m",
      preAllocatedVUs: 500,
      maxVUs: 2000,
    },
  },
};

export default function () {
  const base = __ENV.BASE_URL || "http://localhost:8080";
  

  const res = http.get(`${base}/hello-flow`,
    { headers: { "Content-Type": "application/json" } }
  );

  check(res, { "200": (r) => r.status === 200 });
}
