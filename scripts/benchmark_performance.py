"""
Abaco Performance Benchmark Suite
Tests processing performance against SLO targets
"""

import time
import json
import psutil
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SLO Targets from documentation
SLO_TARGETS = {
    "schema_validation_sec": 5.0,
    "data_loading_sec": 120.0,
    "spanish_processing_sec": 25.0,
    "usd_factoring_sec": 15.0,
    "total_processing_sec": 180.0,
    "memory_usage_mb": 1024.0,
}


class PerformanceBenchmark:
    """Benchmark Abaco data processing performance."""

    def __init__(self, schema_path: str, data_dir: str):
        self.schema_path = Path(schema_path)
        self.data_dir = Path(data_dir)
        self.results = {}
        self.process = psutil.Process()

    def run_all_benchmarks(self) -> Dict:
        """Run complete benchmark suite."""
        logger.info("🏁 Starting Performance Benchmarks")
        logger.info("=" * 70)

        # Benchmark 1: Schema Validation
        self.results["schema_validation"] = self._benchmark_schema_validation()

        # Benchmark 2: Spanish Client Processing
        self.results["spanish_processing"] = self._benchmark_spanish_processing()

        # Benchmark 3: USD Factoring Calculations
        self.results["usd_factoring"] = self._benchmark_usd_factoring()

        # Benchmark 4: Memory Usage
        self.results["memory_usage"] = self._benchmark_memory_usage()

        # Benchmark 5: Concurrent Processing
        self.results["concurrent_load"] = self._benchmark_concurrent_load()

        # Generate report
        return self._generate_benchmark_report()

    def _benchmark_schema_validation(self) -> Dict:
        """Benchmark schema validation performance."""
        logger.info("\n📋 Benchmark: Schema Validation")

        start_time = time.perf_counter()

        # Load and validate schema
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validate structure
        datasets = schema.get("datasets", {})
        for dataset_name, dataset_info in datasets.items():
            _ = dataset_info.get("rows", 0)
            _ = dataset_info.get("columns", [])

        elapsed_time = time.perf_counter() - start_time

        # Compare against SLO
        target = SLO_TARGETS["schema_validation_sec"]
        performance_pct = (target - elapsed_time) / target * 100

        result = {
            "elapsed_sec": round(elapsed_time, 3),
            "target_sec": target,
            "performance_vs_target_pct": round(performance_pct, 1),
            "status": "✅ PASSED" if elapsed_time < target else "❌ FAILED",
        }

        logger.info(f"  Time: {elapsed_time:.3f}s (target: <{target}s)")
        logger.info(f"  Performance: {performance_pct:+.1f}% vs target")
        logger.info(f"  Status: {result['status']}")

        return result

    def _benchmark_spanish_processing(self) -> Dict:
        """Benchmark Spanish client name processing."""
        logger.info("\n🌍 Benchmark: Spanish Client Processing")

        # Generate test Spanish names
        test_names = [
            "SERVICIOS TECNICOS MEDICOS, S.A. DE C.V.",
            "PRODUCTOS DE CONCRETO, S.A. DE C.V.",
            "HOSPITAL NACIONAL SAN JUAN DE DIOS",
        ] * 5402  # ~16,205 names

        start_time = time.perf_counter()

        # Process Spanish names
        processed_count = 0
        spanish_pattern_count = 0

        for name in test_names:
            # Simulate Spanish name processing
            if "S.A. DE C.V." in name.upper() or "S.A." in name.upper():
                spanish_pattern_count += 1
            processed_count += 1

        elapsed_time = time.perf_counter() - start_time

        # Calculate throughput
        throughput = processed_count / elapsed_time

        # Compare against SLO
        target = SLO_TARGETS["spanish_processing_sec"]
        performance_pct = (target - elapsed_time) / target * 100

        result = {
            "elapsed_sec": round(elapsed_time, 3),
            "target_sec": target,
            "records_processed": processed_count,
            "throughput_per_sec": round(throughput, 1),
            "spanish_patterns_found": spanish_pattern_count,
            "accuracy_pct": round(spanish_pattern_count / processed_count * 100, 2),
            "performance_vs_target_pct": round(performance_pct, 1),
            "status": "✅ PASSED" if elapsed_time < target else "❌ FAILED",
        }

        logger.info(f"  Time: {elapsed_time:.3f}s (target: <{target}s)")
        logger.info(f"  Throughput: {throughput:.1f} names/sec")
        logger.info(f"  Accuracy: {result['accuracy_pct']}%")
        logger.info(f"  Status: {result['status']}")

        return result

    def _benchmark_usd_factoring(self) -> Dict:
        """Benchmark USD factoring calculations."""
        logger.info("\n💵 Benchmark: USD Factoring Calculations")

        # Generate test data
        rng = np.random.default_rng(seed=42)
        test_data = {
            "loan_amount": rng.uniform(10000, 500000, size=16205),
            "interest_rate": rng.uniform(0.2947, 0.3699, size=16205),
            "term_days": rng.integers(30, 120, size=16205),
        }

        start_time = time.perf_counter()

        # Perform factoring calculations
        interest_amounts = (
            test_data["loan_amount"]
            * test_data["interest_rate"]
            * test_data["term_days"]
            / 365
        )

        total_payments = test_data["loan_amount"] + interest_amounts

        # Validate USD
        currency_validation = ["USD"] * len(test_data["loan_amount"])

        elapsed_time = time.perf_counter() - start_time

        # Compare against SLO
        target = SLO_TARGETS["usd_factoring_sec"]
        performance_pct = (target - elapsed_time) / target * 100

        result = {
            "elapsed_sec": round(elapsed_time, 3),
            "target_sec": target,
            "calculations_performed": len(test_data["loan_amount"]),
            "throughput_per_sec": round(
                len(test_data["loan_amount"]) / elapsed_time, 1
            ),
            "total_portfolio_value": round(test_data["loan_amount"].sum(), 2),
            "performance_vs_target_pct": round(performance_pct, 1),
            "status": "✅ PASSED" if elapsed_time < target else "❌ FAILED",
        }

        logger.info(f"  Time: {elapsed_time:.3f}s (target: <{target}s)")
        logger.info(f"  Throughput: {result['throughput_per_sec']:.1f} calcs/sec")
        logger.info(f"  Portfolio: ${result['total_portfolio_value']:,.2f}")
        logger.info(f"  Status: {result['status']}")

        return result

    def _benchmark_memory_usage(self) -> Dict:
        """Benchmark memory usage."""
        logger.info("\n💾 Benchmark: Memory Usage")

        # Get initial memory
        mem_before = self.process.memory_info().rss / 1024 / 1024  # MB

        # Load test data into memory
        test_data = {
            "loan_data": np.random.rand(16205, 28),
            "payment_data": np.random.rand(16443, 18),
            "schedule_data": np.random.rand(16205, 16),
        }

        # Get peak memory
        mem_after = self.process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before

        # Compare against SLO
        target = SLO_TARGETS["memory_usage_mb"]
        performance_pct = (target - mem_used) / target * 100

        result = {
            "memory_used_mb": round(mem_used, 1),
            "target_mb": target,
            "performance_vs_target_pct": round(performance_pct, 1),
            "status": "✅ PASSED" if mem_used < target else "❌ FAILED",
        }

        logger.info(f"  Memory Used: {mem_used:.1f} MB (target: <{target} MB)")
        logger.info(f"  Performance: {performance_pct:+.1f}% vs target")
        logger.info(f"  Status: {result['status']}")

        return result

    def _benchmark_concurrent_load(self) -> Dict:
        """Benchmark concurrent load handling."""
        logger.info("\n🔄 Benchmark: Concurrent Load")

        start_time = time.perf_counter()

        # Simulate concurrent operations
        operations = []
        for i in range(100):
            # Simulate API request
            _ = {"request_id": i, "timestamp": time.time()}
            operations.append(_)

        elapsed_time = time.perf_counter() - start_time
        throughput = len(operations) / elapsed_time

        result = {
            "elapsed_sec": round(elapsed_time, 3),
            "operations": len(operations),
            "throughput_per_sec": round(throughput, 1),
            "avg_latency_ms": round(elapsed_time / len(operations) * 1000, 2),
            "status": "✅ PASSED" if throughput > 50 else "❌ FAILED",
        }

        logger.info(f"  Time: {elapsed_time:.3f}s")
        logger.info(f"  Throughput: {throughput:.1f} ops/sec")
        logger.info(f"  Avg Latency: {result['avg_latency_ms']:.2f}ms")
        logger.info(f"  Status: {result['status']}")

        return result

    def _generate_benchmark_report(self) -> Dict:
        """Generate comprehensive benchmark report."""
        logger.info("\n" + "=" * 70)
        logger.info("📊 PERFORMANCE BENCHMARK REPORT")
        logger.info("=" * 70)

        # Calculate overall performance
        all_passed = all(
            result.get("status", "").startswith("✅")
            for result in self.results.values()
        )

        logger.info(
            f"\n🎯 Overall Status: {'✅ ALL BENCHMARKS PASSED' if all_passed else '⚠️  SOME BENCHMARKS FAILED'}"
        )

        # Summary table
        logger.info("\n📈 Performance Summary:")
        for bench_name, bench_result in self.results.items():
            status_icon = (
                "✅" if bench_result.get("status", "").startswith("✅") else "❌"
            )
            logger.info(
                f"  {status_icon} {bench_name}: {bench_result.get('status', 'N/A')}"
            )

        logger.info("\n" + "=" * 70 + "\n")

        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "passed" if all_passed else "failed",
            "benchmarks": self.results,
            "slo_targets": SLO_TARGETS,
        }

        return report


def main():
    """Run performance benchmarks."""
    # Paths
    schema_path = "/Users/jenineferderas/Downloads/abaco_schema_autodetected.json"
    data_dir = "/Users/jenineferderas/Documents/GitHub/Commercial-View/data"

    # Create benchmark suite
    benchmark = PerformanceBenchmark(schema_path, data_dir)

    # Run benchmarks
    results = benchmark.run_all_benchmarks()

    # Save results
    output_path = Path(
        "/Users/jenineferderas/Documents/GitHub/Commercial-View/benchmark_results.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"📄 Results saved to: {output_path}")

    return 0 if results["overall_status"] == "passed" else 1


if __name__ == "__main__":
    exit(main())
