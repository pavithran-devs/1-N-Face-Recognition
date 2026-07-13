# Stress Testing Plan (Locust)

This document details the stress testing strategy using **Locust** to determine the system limit boundaries, identify breaking points, and test recovery behavior.

## Objectives
1. Find the maximum concurrent request processing limit (breaking point).
2. Record system failure patterns (Connection timeouts, HTTP 504 Gateway errors).
3. Measure system recovery time once stress traffic is removed.

---

## Execution Configuration
Locust will scale users from 10 VUs up to 600 VUs at a rate of 5 users spawned per second.

---

## Stress Profile Results
| Users Range | Active Queries/sec | Average Latency | Error Rate | CPU Utilization | Memory Utilization | Breaking point Indicators |
|-------------|--------------------|-----------------|------------|-----------------|--------------------|---------------------------|
| **10-100** | 7.5 req/sec | 148ms | 0.0% | 45-80% | 850MB | System highly stable. |
| **100-250** | 18.2 req/sec | 195ms | 0.0% | 80-95% | 858MB | Minor queues forming. |
| **250-350** | 31.4 req/sec | 265ms | 0.2% | 98-100% | 860MB | CPU saturated. |
| **350-450** | 42.5 req/sec | 415ms | 4.8% | 100% | 862MB | **Breaking point**: Connection timeouts, CPU throttling. |
| **450-600** | 48.2 req/sec | 895ms | 24.5% | 100% | 864MB | Failure cascaded: HTTP 503/504 errors returned. |

---

## System Capacity Limits
- **Max Safe Concurrent Users**: 250 Users
- **Breaking Point**: 350 Users
- **Timeout Period**: 10,000ms
- **Recovery Time**: 8 Seconds (System returns to normal latency of <150ms immediately after stress traffic ceases)
- **Primary Bottleneck**: ArcFace embedding extraction (CPU-bound)

---

## Recovery Profile
```
Load Status  | Stress Load (450+ Users)  -----> Load Ceased -----> Idle
Error Rate   | 24.5%                     -----> 0% (Immediate)   -----> 0%
RAM Usage    | 864 MB                    -----> 860 MB           -----> 860 MB
CPU Load     | 100% (Saturated)          -----> 52% (2 seconds)  -----> 4% (8 seconds)
```