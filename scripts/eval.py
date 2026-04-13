"""
Evaluation Script — KnowledgeAgent RAG System
----------------------------------------------
Measures retrieval precision@k, answer relevance, and latency against a
ground-truth Q&A dataset. Outputs a JSON report and prints a summary table.

Usage:
    python scripts/eval.py --url http://localhost:8000
    python scripts/eval.py --url http://localhost:8000 --top-k 3
    python scripts/eval.py --url http://localhost:8000 --output results/eval_run1.json
"""

import argparse
import json
import time
import statistics
import requests
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime


# ── Ground-truth Q&A dataset ──────────────────────────────────────────────────
# Each entry: question, expected_answer_keywords, expected_sources
GROUND_TRUTH = [
    {
        "id": "RW-01",
        "question": "How many days per week can employees work remotely?",
        "expected_keywords": ["3 days", "three days", "remotely"],
        "expected_sources": ["sample_policy.md"],
        "category": "remote_work",
    },
    {
        "id": "RW-02",
        "question": "What approval is needed for full remote work?",
        "expected_keywords": ["VP approval", "VP"],
        "expected_sources": ["sample_policy.md"],
        "category": "remote_work",
    },
    {
        "id": "RW-03",
        "question": "What are the core hours for remote employees?",
        "expected_keywords": ["10am", "4pm", "IST", "core hours"],
        "expected_sources": ["sample_policy.md"],
        "category": "remote_work",
    },
    {
        "id": "OB-01",
        "question": "How long is the onboarding program for new engineers?",
        "expected_keywords": ["2 weeks", "two weeks", "two-week"],
        "expected_sources": ["sample_policy.md"],
        "category": "onboarding",
    },
    {
        "id": "OB-02",
        "question": "What does week 1 of onboarding cover?",
        "expected_keywords": ["tool setup", "codebase", "security training"],
        "expected_sources": ["sample_policy.md"],
        "category": "onboarding",
    },
    {
        "id": "OB-03",
        "question": "What system is used to track the onboarding checklist?",
        "expected_keywords": ["Notion"],
        "expected_sources": ["sample_policy.md"],
        "category": "onboarding",
    },
    {
        "id": "LV-01",
        "question": "How many days of paid leave do employees receive per year?",
        "expected_keywords": ["24 days"],
        "expected_sources": ["sample_policy.md"],
        "category": "leave",
    },
    {
        "id": "LV-02",
        "question": "How far in advance must leave be requested?",
        "expected_keywords": ["5 business days"],
        "expected_sources": ["sample_policy.md"],
        "category": "leave",
    },
    {
        "id": "LV-03",
        "question": "How many leave days can be carried forward each year?",
        "expected_keywords": ["10 days"],
        "expected_sources": ["sample_policy.md"],
        "category": "leave",
    },
    {
        "id": "PA-01",
        "question": "How do I request production database access?",
        "expected_keywords": ["#infra-access", "Slack", "manager"],
        "expected_sources": ["sample_policy.md"],
        "category": "access",
    },
    {
        "id": "PA-02",
        "question": "How long before unused production access is revoked?",
        "expected_keywords": ["90 days"],
        "expected_sources": ["sample_policy.md"],
        "category": "access",
    },
    {
        "id": "EQ-01",
        "question": "What is the equity vesting period?",
        "expected_keywords": ["4 years", "four years"],
        "expected_sources": ["sample_policy.md"],
        "category": "equity",
    },
    {
        "id": "EQ-02",
        "question": "When does the cliff vest for equity?",
        "expected_keywords": ["1-year cliff", "one year", "cliff"],
        "expected_sources": ["sample_policy.md"],
        "category": "equity",
    },
    {
        "id": "TL-01",
        "question": "What tool does the engineering team use for issue tracking?",
        "expected_keywords": ["Linear"],
        "expected_sources": ["sample_policy.md"],
        "category": "tools",
    },
    {
        "id": "TL-02",
        "question": "What is the monthly tool stipend for engineers?",
        "expected_keywords": ["$200", "200"],
        "expected_sources": ["sample_policy.md"],
        "category": "tools",
    },
]


# ── Evaluation helpers ────────────────────────────────────────────────────────

@dataclass
class EvalResult:
    id: str
    question: str
    category: str
    answer: str
    sources_returned: List[str]
    expected_sources: List[str]
    expected_keywords: List[str]
    keyword_hit: bool
    source_hit: bool
    latency_s: float
    status_code: int
    error: Optional[str] = None


def keyword_match(answer: str, keywords: List[str]) -> bool:
    """Return True if ANY expected keyword appears in the answer (case-insensitive)."""
    answer_lower = answer.lower()
    return any(kw.lower() in answer_lower for kw in keywords)


def source_match(returned_sources: List[str], expected_sources: List[str]) -> bool:
    """Return True if ANY expected source appears in the returned sources."""
    returned_lower = [s.lower() for s in returned_sources]
    return any(exp.lower() in " ".join(returned_lower) for exp in expected_sources)


def query(base_url: str, question: str, top_k: int) -> dict:
    resp = requests.post(
        f"{base_url}/query",
        json={"question": question, "top_k": top_k},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def run_eval(base_url: str, top_k: int, verbose: bool = True) -> List[EvalResult]:
    results = []

    for item in GROUND_TRUTH:
        start = time.perf_counter()
        error = None
        answer = ""
        sources_returned = []
        status_code = 0

        try:
            data = query(base_url, item["question"], top_k)
            latency = time.perf_counter() - start
            answer = data.get("answer", "")
            sources_returned = [s["source"] for s in data.get("sources", [])]
            status_code = 200
        except requests.HTTPError as e:
            latency = time.perf_counter() - start
            status_code = e.response.status_code
            error = str(e)
        except Exception as e:
            latency = time.perf_counter() - start
            error = str(e)

        result = EvalResult(
            id=item["id"],
            question=item["question"],
            category=item["category"],
            answer=answer,
            sources_returned=sources_returned,
            expected_sources=item["expected_sources"],
            expected_keywords=item["expected_keywords"],
            keyword_hit=keyword_match(answer, item["expected_keywords"]),
            source_hit=source_match(sources_returned, item["expected_sources"]),
            latency_s=round(latency, 3),
            status_code=status_code,
            error=error,
        )
        results.append(result)

        if verbose:
            kw = "✓" if result.keyword_hit else "✗"
            src = "✓" if result.source_hit else "✗"
            err_str = f" [ERR: {error}]" if error else ""
            print(f"  [{item['id']}] kw:{kw} src:{src} {result.latency_s:.2f}s  {item['question'][:55]}{err_str}")

    return results


def summarize(results: List[EvalResult]) -> dict:
    total = len(results)
    successful = [r for r in results if r.error is None]
    n = len(successful)

    keyword_hits = sum(1 for r in successful if r.keyword_hit)
    source_hits = sum(1 for r in successful if r.source_hit)
    both_hits = sum(1 for r in successful if r.keyword_hit and r.source_hit)

    latencies = [r.latency_s for r in successful]

    # Per-category breakdown
    categories = {}
    for r in successful:
        cat = r.category
        if cat not in categories:
            categories[cat] = {"total": 0, "keyword_hits": 0, "source_hits": 0}
        categories[cat]["total"] += 1
        if r.keyword_hit:
            categories[cat]["keyword_hits"] += 1
        if r.source_hit:
            categories[cat]["source_hits"] += 1

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_questions": total,
        "successful_queries": n,
        "failed_queries": total - n,
        "answer_accuracy": round(keyword_hits / n, 4) if n else 0,
        "source_precision": round(source_hits / n, 4) if n else 0,
        "joint_accuracy": round(both_hits / n, 4) if n else 0,
        "latency": {
            "mean_s": round(statistics.mean(latencies), 3) if latencies else 0,
            "median_s": round(statistics.median(latencies), 3) if latencies else 0,
            "p95_s": round(sorted(latencies)[int(len(latencies) * 0.95)], 3) if latencies else 0,
            "min_s": round(min(latencies), 3) if latencies else 0,
            "max_s": round(max(latencies), 3) if latencies else 0,
        },
        "categories": categories,
    }


def print_summary(summary: dict):
    print("\n" + "=" * 60)
    print("  EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Total questions   : {summary['total_questions']}")
    print(f"  Successful queries: {summary['successful_queries']}")
    print(f"  Failed queries    : {summary['failed_queries']}")
    print()
    print(f"  Answer accuracy   : {summary['answer_accuracy'] * 100:.1f}%  (keyword match)")
    print(f"  Source precision  : {summary['source_precision'] * 100:.1f}%  (correct doc cited)")
    print(f"  Joint accuracy    : {summary['joint_accuracy'] * 100:.1f}%  (both correct)")
    print()
    print(f"  Latency mean      : {summary['latency']['mean_s']}s")
    print(f"  Latency median    : {summary['latency']['median_s']}s")
    print(f"  Latency p95       : {summary['latency']['p95_s']}s")
    print()
    print("  Per-category breakdown:")
    for cat, data in summary["categories"].items():
        kw_pct = data["keyword_hits"] / data["total"] * 100 if data["total"] else 0
        src_pct = data["source_hits"] / data["total"] * 100 if data["total"] else 0
        print(f"    {cat:<15} kw:{kw_pct:5.1f}%  src:{src_pct:5.1f}%  ({data['total']} questions)")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Evaluate KnowledgeAgent RAG quality.")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--top-k", type=int, default=5, help="Top-K chunks to retrieve")
    parser.add_argument("--output", default="eval_results.json", help="Output JSON path")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-question output")
    args = parser.parse_args()

    print(f"\nEvaluating KnowledgeAgent at {args.url} (top_k={args.top_k})")
    print(f"Questions: {len(GROUND_TRUTH)}\n")

    results = run_eval(args.url, args.top_k, verbose=not args.quiet)
    summary = summarize(results)
    print_summary(summary)

    output = {
        "summary": summary,
        "results": [asdict(r) for r in results],
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFull results saved to: {args.output}")


if __name__ == "__main__":
    main()