import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    saturate: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '20s', target: 50 },
        { duration: '40s', target: 50 },
        { duration: '10s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.10'],
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8001';

export default function () {
  const payload = JSON.stringify({ url: 'https://example.com' });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const post = http.post(`${BASE}/bookmarks`, payload, params);
  check(post, { 'POST 201': (r) => r.status === 201 });
  if (post.status === 201) {
    const id = JSON.parse(post.body).id;
    const get = http.get(`${BASE}/bookmarks/${id}`);
    check(get, { 'GET 200': (r) => r.status === 200 });
  }
  // sem sleep — VU fecha iteração e imediatamente começa a próxima
}
