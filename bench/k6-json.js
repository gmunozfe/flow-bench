import http from 'k6/http';
import { check } from 'k6';

const RATE = Number(__ENV.RATE || 1);
const DURATION = __ENV.DURATION || '30s';
const ITEMS = Number(__ENV.ITEMS || 1000);
const ITERATIONS = Number(__ENV.ITERATIONS || 3);
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
  scenarios: {
    json_test: {
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
    items: ITEMS,
    iterations: ITERATIONS,
  });

  const res = http.post(`${BASE_URL}/bench/json`, payload, {
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
    'completed': () => body.status === 'COMPLETED',
    'itemsCount matches': () => body.itemsCount === ITEMS,
    'iterations match': () => body.iterations === ITERATIONS,
    'totalMutationEntries matches': () =>
      body.totalMutationEntries === ITEMS * ITERATIONS,
  });
}
