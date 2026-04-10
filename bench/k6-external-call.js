import http from 'k6/http';
import { check } from 'k6';
import { Trend } from 'k6/metrics';

const RATE = Number(__ENV.RATE || '20');
const DURATION = __ENV.DURATION || '30s';
const DELAY_MS = Number(__ENV.DELAY_MS || '10');
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

const flow_overhead_ms = new Trend('flow_overhead_ms');

export const options = {
  scenarios: {
    external_call_test: {
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

function asObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value : {};
}

export default function () {
  const orderId = `order-${__ITER}`;

  const payload = JSON.stringify({
    orderId: orderId,
    amount: 110.0,
    customerId: 'cust-1',
    delayMs: DELAY_MS,
  });

  const res = http.post(`${BASE_URL}/bench/enrichment`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  let parsed = {};
  try {
    parsed = asObject(res.json());
  } catch (e) {
    parsed = {};
  }

  const status = parsed.status;
  const parsedOrderId = parsed.orderId;
  const parsedCustomerId = parsed.customerId;
  const parsedAmount = parsed.amount;
  const parsedDelayMs = parsed.delayMs;
  const parsedRisk = parsed.risk;
  const parsedSegment = parsed.segment;
  const parsedSource = parsed.source;

  check(res, {
    'status 200': (r) => r.status === 200,
    'completed': () => status === 'COMPLETED',
    'orderId matches': () => parsedOrderId === orderId,
    'customerId matches': () => parsedCustomerId === 'cust-1',
    'amount matches': () => parsedAmount === 110.0,
    'delayMs matches': () => parsedDelayMs === DELAY_MS,
    'risk present': () => parsedRisk === 'MEDIUM',
    'segment present': () => parsedSegment === 'STANDARD',
    'source present': () => parsedSource === 'mock-service',
  });

  const duration =
    res &&
    res.timings &&
    typeof res.timings.duration === 'number'
      ? res.timings.duration
      : 0;

  flow_overhead_ms.add(duration - DELAY_MS);
}
