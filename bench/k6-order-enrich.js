import http from "k6/http";
import { check } from "k6";

export const options = {
  scenarios: {
    starts: {
      executor: "constant-arrival-rate",
      rate: __ENV.RATE ? parseInt(__ENV.RATE) : 100,
      timeUnit: "1s",
      duration: __ENV.DURATION || "1m",
      preAllocatedVUs: 500,
      maxVUs: 2000,
    },
  },
};

export default function () {
  const base = __ENV.BASE_URL || "http://localhost:8080";
  const id = `${__VU}-${__ITER}-${Date.now()}`;

  const payload = JSON.stringify({
    orderId: id,
    amount: 42.5,
    customerId: "cust-1"
  });

  const res = http.post(`${base}/bench/order-enrich`, payload, {
    headers: { "Content-Type": "application/json" }
  });

  check(res, { "200": (r) => r.status === 200 });
}
