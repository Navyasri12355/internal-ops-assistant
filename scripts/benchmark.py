"""
Benchmark Script
----------------
Measures query resolution time and simulates concurrency at different scale levels.
Produces data for the scalability graphs in the paper.

Usage:
    python scripts/benchmark.py --url http://localhost:8000
"""

import argparse
import time
import json
import statistics
import concurrent.futures
import requests


BENCHMARK_QUESTIONS = [
    "What is the remote work policy?",
    "How do I request access to production systems?",
    "What is the equity vesting schedule?",
    "Summarize the onboarding process for new engineers.",
    "What are the company's core values?",
    "How do I submit expenses?",
    "What tools does the engineering team use?",
    "What is the performance review cycle?",
]


def query_once(base_url: str, question: str) -> dict:
    start = time.perf_counter()
    resp = requests.post(f"{base_url}/query", json={"question": question, "top_k": 5}, timeout=30)
    elapsed = time.perf_counter() - start
    return {"question": question, "latency_s": round(elapsed, 3), "status": resp.status_code}


def run_sequential(base_url: str) -> list:
    print("\n[Sequential Benchmark]")
    results = []
    for q in BENCHMARK_QUESTIONS:
        r = query_once(base_url, q)
        print(f"  {r['latency_s']:.3f}s  {q[:50]}")
        results.append(r)
    latencies = [r["latency_s"] for r in results]
    print(f"  Mean: {statistics.mean(latencies):.3f}s | P95: {sorted(latencies)[int(len(latencies)*0.95)]:.3f}s")
    return results


def run_concurrent(base_url: str, n_users: int) -> dict:
    print(f"\n[Concurrency: {n_users} simultaneous users]")
    questions = (BENCHMARK_QUESTIONS * ((n_users // len(BENCHMARK_QUESTIONS)) + 1))[:n_users]

    start_wall = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_users) as executor:
        futures = [executor.submit(query_once, base_url, q) for q in questions]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    wall_time = time.perf_counter() - start_wall

    latencies = [r["latency_s"] for r in results]
    summary = {
        "n_users": n_users,
        "wall_time_s": round(wall_time, 3),
        "mean_latency_s": round(statistics.mean(latencies), 3),
        "p95_latency_s": round(sorted(latencies)[int(len(latencies) * 0.95)], 3),
        "throughput_qps": round(n_users / wall_time, 2),
    }
    print(f"  Wall time: {summary['wall_time_s']}s | Mean latency: {summary['mean_latency_s']}s | P95: {summary['p95_latency_s']}s | QPS: {summary['throughput_qps']}")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--output", default="benchmark_results.json")
    args = parser.parse_args()

    print(f"Benchmarking against {args.url}")

    sequential = run_sequential(args.url)

    concurrency_results = []
    for n in [1, 5, 10, 25, 50, 100]:
        concurrency_results.append(run_concurrent(args.url, n))

    output = {"sequential": sequential, "concurrency": concurrency_results}
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
