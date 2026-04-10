import http from 'k6/http';
import { check } from 'k6';

const RATE = Number(__ENV.RATE || '20');
const DURATION = __ENV.DURATION || '30s';
const PREBUILT_SIZE_KB = Number(__ENV.PREBUILT_SIZE_KB || '1000');
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
  scenarios: {
    taskoutput_persistence_test: {
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
    prebuiltSizeKb: PREBUILT_SIZE_KB,
  });

  const res = http.post(
    `${BASE_URL}/bench/taskoutput-persistence`,
    payload,
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  let body = {};
  try {
    body = res.json() || {};
  } catch (e) {
    body = {};
  }

  check(res, {
    'status 200': (r) => r.status === 200,
    'completed': () => body.status === 'COMPLETED',
    'taskOutputSizeKb matches': () =>
      body.taskOutputSizeKb === PREBUILT_SIZE_KB,
  });
}
