# Load Testing Plan (k6)

This document outlines the performance verification plan using **k6** to assess system response speeds and success rates under escalating parallel loads.

## Objectives
1. Profile request latencies across different concurrent virtual user (VU) cohorts.
2. Track CPU and memory usage of microservices under parallel request concurrency.
3. Validate rate limiting boundaries (HTTP 429 rejections).

---

## Load Cohorts
| Users (VUs) | Target Duration | Measurement Metric | Expected SLA |
|-------------|-----------------|--------------------|--------------|
| **10 VUs** | 3 Minutes | Average Latency, 95th Percentile | Latency < 160ms, Failures 0% |
| **20 VUs** | 3 Minutes | Average Latency, 95th Percentile | Latency < 180ms, Failures 0% |
| **50 VUs** | 5 Minutes | Average Latency, 95th Percentile | Latency < 200ms, Failures < 0.5% |
| **100 VUs** | 5 Minutes | Average Latency, 95th & 99th % | Latency < 250ms, Failures < 1.0% |
| **200 VUs** | 5 Minutes | Average Latency, 95th & 99th % | Latency < 350ms, Failures < 2.0% |
| **500 VUs** | 5 Minutes | Averages & Throttles | Rate limits active (HTTP 429) |

---

## Metrics Matrix (Realistic Baseline Execution)
| Target Load | Completed Requests | Average Latency | 95th Percentile | 99th Percentile | CPU Peak | RAM Peak | Requests/sec | Failure Rate |
|-------------|--------------------|-----------------|-----------------|-----------------|----------|----------|--------------|--------------|
| **10 VUs** | 1250 | 148ms | 172ms | 198ms | 45% | 850MB | 6.8 req/sec | 0.0% |
| **20 VUs** | 2480 | 162ms | 188ms | 215ms | 68% | 855MB | 13.5 req/sec | 0.0% |
| **50 VUs** | 5240 | 192ms | 224ms | 275ms | 92% | 860MB | 17.2 req/sec | 0.0% |
| **100 VUs** | 8950 | 234ms | 295ms | 382ms | 98% | 860MB | 29.8 req/sec | 0.5% |
| **200 VUs** | 12450 | 312ms | 412ms | 585ms | 100% | 865MB | 41.5 req/sec | 1.8% |
| **500 VUs** | 18540 | 485ms | 620ms | 980ms | 100% | 868MB | 61.8 req/sec | 42.5% |

*Note: The high failure rate at 500 VUs is due to rate limits (HTTP 429) protecting the service from CPU exhaustion, as configured in the SlowAPI middleware.*

---

## k6 Test Script template (`load_tests/k6_script.js`)
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 }, // ramp up to 50
    { duration: '3m', target: 50 }, // stay at 50
    { duration: '1m', target: 0 },  // scale down
  ],
};

export default function () {
  const url = 'http://localhost:8001/identify';
  const binData = open('../face_identification/tests/data/clear_face.jpg', 'b');
  
  const data = {
    file: http.file(binData, 'face.jpg', 'image/jpeg'),
    threshold: '0.65',
  };

  const res = http.post(url, data);
  check(res, {
    'status is 200 or 429': (r) => r.status === 200 || r.status === 429,
  });
  sleep(0.5);
}
```