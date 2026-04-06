import http from 'k6/http';
import { check } from 'k6';

const RATE = Number(__ENV.RATE || 20);
const DURATION = __ENV.DURATION || '30s';
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
  scenarios: {
    order50_test: {
      executor: 'constant-arrival-rate',
      rate: RATE,
      timeUnit: '1s',
      duration: DURATION,
      preAllocatedVUs: 10,
      maxVUs: 200,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  const payload = JSON.stringify({
    orderId: `order-${__ITER}`,
    amount: 110.0,
    customerId: 'cust-1',
  });

  const res = http.post(`${BASE_URL}/bench/order50`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  let body = {};
  try {
    body = res.json();
  } catch (e) {
    body = {};
  }

  check(res, {
    'status 200': (r) => r.status === 200,
    'completed': () => body.status === 'COMPLETED_50_STEPS',
    'orderId matches': () => body.orderId === `order-${__ITER}`,
    'customerId matches': () => body.customerId === 'cust-1',
    'amount matches': () => body.amount === 110.0,
  });
}
