import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],   // falha se >1% de erro
    checks:          ['rate>0.99'],
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

  sleep(0.5);
}
