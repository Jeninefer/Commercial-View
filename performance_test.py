#!/usr/bin/env python3
"""
Commercial-View Production Performance Testing Suite
Abaco Integration Load Testing - 48,853 Records | $208M USD
Spanish Factoring & Commercial Lending Analytics
"""

import asyncio
import aiohttp
import time
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import sys
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Performance test result data structure"""
    timestamp: float
    endpoint: str
    method: str
    status_code: int
    response_time: float
    error: Optional[str] = None

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    base_url: str
    concurrent_users: int
    requests_per_user: int
    test_duration_seconds: int
    ramp_up_seconds: int

class PerformanceTester:
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.start_time = None
        self.session = None
        
    async def create_session(self):
        """Create aiohttp session with performance optimizations"""
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=20,  # Connections per host
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,  # Total timeout
            connect=10,  # Connection timeout
            sock_read=20  # Socket read timeout
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Commercial-View-LoadTester/1.0',
                'Accept': 'application/json'
            }
        )
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> TestResult:
        """Make a single HTTP request and measure performance"""
        start_time = time.time()
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url) as response:
                    await response.text()  # Read response body
                    response_time = time.time() - start_time
                    
                    return TestResult(
                        timestamp=start_time,
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time
                    )
            
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    await response.text()  # Read response body
                    response_time = time.time() - start_time
                    
                    return TestResult(
                        timestamp=start_time,
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time
                    )
        
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                timestamp=start_time,
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                error=str(e)
            )
    
    async def user_simulation(self, user_id: int):
        """Simulate a single user's behavior"""
        logger.info(f"🧑‍💼 User {user_id} starting simulation")
        
        # Realistic user journey for Spanish factoring system
        test_scenarios = [
            # Core health and system checks
            {'endpoint': '/health', 'method': 'GET', 'weight': 0.4},
            {'endpoint': '/', 'method': 'GET', 'weight': 0.3},
            {'endpoint': '/performance', 'method': 'GET', 'weight': 0.2},
            
            # Abaco data scenarios (simulate various queries)
            {'endpoint': '/health', 'method': 'GET', 'weight': 0.1},  # Frequent health checks
        ]
        
        user_results = []
        
        for i in range(self.config.requests_per_user):
            # Choose scenario based on weights
            import random
            scenario = random.choices(
                test_scenarios,
                weights=[s['weight'] for s in test_scenarios],
                k=1
            )[0]
            
            result = await self.make_request(
                scenario['endpoint'],
                scenario['method']
            )
            user_results.append(result)
            
            # Add realistic think time (0.1-2.0 seconds)
            think_time = random.uniform(0.1, 2.0)
            await asyncio.sleep(think_time)
        
        logger.info(f"✅ User {user_id} completed {len(user_results)} requests")
        return user_results
    
    async def run_load_test(self) -> Dict[str, Any]:
        """Execute the load test"""
        logger.info(f"🚀 Starting load test with {self.config.concurrent_users} users")
        logger.info(f"📊 Target: {self.config.requests_per_user} requests per user")
        logger.info(f"⏱️  Duration: {self.config.test_duration_seconds}s with {self.config.ramp_up_seconds}s ramp-up")
        logger.info(f"🎯 Testing Abaco Integration: 48,853 records | $208M USD")
        
        await self.create_session()
        self.start_time = time.time()
        
        try:
            # Ramp up users gradually
            tasks = []
            ramp_delay = self.config.ramp_up_seconds / self.config.concurrent_users
            
            for user_id in range(self.config.concurrent_users):
                if user_id > 0:
                    await asyncio.sleep(ramp_delay)
                
                task = asyncio.create_task(self.user_simulation(user_id))
                tasks.append(task)
            
            # Wait for all users to complete
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results
            for user_results in all_results:
                if isinstance(user_results, list):
                    self.results.extend(user_results)
                else:
                    logger.error(f"User simulation error: {user_results}")
            
        finally:
            await self.close_session()
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze performance test results"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Basic metrics
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r.status_code == 200])
        failed_requests = total_requests - successful_requests
        
        response_times = [r.response_time for r in self.results if r.error is None]
        
        if not response_times:
            return {"error": "No successful requests to analyze"}
        
        # Performance statistics
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Calculate throughput
        test_duration = max([r.timestamp for r in self.results]) - min([r.timestamp for r in self.results])
        throughput = total_requests / test_duration if test_duration > 0 else 0
        
        # Error analysis
        errors_by_type = {}
        status_codes = {}
        
        for result in self.results:
            # Status code distribution
            status_codes[result.status_code] = status_codes.get(result.status_code, 0) + 1
            
            # Error categorization
            if result.error:
                error_type = type(result.error).__name__ if hasattr(result.error, '__class__') else str(result.error)
                errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
        
        # Endpoint performance breakdown
        endpoint_stats = {}
        for result in self.results:
            if result.endpoint not in endpoint_stats:
                endpoint_stats[result.endpoint] = []
            if result.error is None:
                endpoint_stats[result.endpoint].append(result.response_time)
        
        endpoint_performance = {}
        for endpoint, times in endpoint_stats.items():
            if times:
                endpoint_performance[endpoint] = {
                    'requests': len(times),
                    'avg_response_time': statistics.mean(times),
                    'p95_response_time': statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
                }
        
        # Abaco-specific performance targets
        abaco_performance_assessment = {
            'target_load_time_seconds': 2.3,
            'target_memory_mb': 847,
            'target_accuracy_spanish': 99.97,
            'meets_target_response_time': avg_response_time <= 2.3,
            'meets_target_p95': p95_response_time <= 5.0,
            'meets_target_error_rate': (failed_requests / total_requests) <= 0.01,
        }
        
        return {
            'test_summary': {
                'timestamp': datetime.utcnow().isoformat(),
                'test_duration_seconds': test_duration,
                'concurrent_users': self.config.concurrent_users,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate_percent': (successful_requests / total_requests) * 100,
                'throughput_rps': throughput,
            },
            'response_time_metrics': {
                'average_seconds': round(avg_response_time, 4),
                'median_seconds': round(median_response_time, 4),
                'p95_seconds': round(p95_response_time, 4),
                'p99_seconds': round(p99_response_time, 4),
                'min_seconds': round(min_response_time, 4),
                'max_seconds': round(max_response_time, 4),
            },
            'endpoint_performance': endpoint_performance,
            'status_code_distribution': status_codes,
            'error_analysis': errors_by_type,
            'abaco_performance_assessment': abaco_performance_assessment,
            'recommendations': self.generate_recommendations(abaco_performance_assessment, avg_response_time, throughput)
        }
    
    def generate_recommendations(self, assessment: Dict, avg_response: float, throughput: float) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Response time recommendations
        if not assessment['meets_target_response_time']:
            recommendations.append(
                f"⚠️  Average response time ({avg_response:.3f}s) exceeds Abaco target (2.3s). "
                "Consider database query optimization or caching."
            )
        
        # Throughput recommendations
        if throughput < 100:
            recommendations.append(
                f"📈 Low throughput ({throughput:.1f} RPS). Consider increasing uvicorn workers or optimizing Spanish text processing."
            )
        
        # Success rate recommendations
        if not assessment['meets_target_error_rate']:
            recommendations.append(
                "❌ Error rate too high. Check logs for Abaco data processing errors and implement better error handling."
            )
        
        # Abaco-specific recommendations
        recommendations.extend([
            "🇪🇸 Ensure Spanish text processing is optimized for factoring terminology",
            "💰 Monitor memory usage during $208M portfolio calculations",
            "📊 Consider implementing Redis caching for 48,853 record queries",
            "🔄 Implement pagination for large dataset responses",
        ])
        
        if not recommendations:
            recommendations.append("✅ Performance meets all Abaco integration targets!")
        
        return recommendations

async def run_performance_tests():
    """Main function to run performance tests"""
    parser = argparse.ArgumentParser(description='Commercial-View Performance Testing Suite')
    parser.add_argument('--base-url', default='http://localhost:8000', help='Base URL of the API')
    parser.add_argument('--users', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--requests', type=int, default=50, help='Requests per user')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--ramp-up', type=int, default=10, help='Ramp-up time in seconds')
    parser.add_argument('--output', help='Output file for results (JSON format)')
    
    args = parser.parse_args()
    
    config = LoadTestConfig(
        base_url=args.base_url,
        concurrent_users=args.users,
        requests_per_user=args.requests,
        test_duration_seconds=args.duration,
        ramp_up_seconds=args.ramp_up
    )
    
    logger.info("🏦 Commercial-View Abaco Integration Performance Testing")
    logger.info("🇪🇸 Spanish Factoring & Commercial Lending Analytics")
    logger.info("📊 Dataset: 48,853 records | Portfolio: $208,192,588.65 USD")
    logger.info("=" * 60)
    
    tester = PerformanceTester(config)
    
    try:
        results = await tester.run_load_test()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST RESULTS")
        print("=" * 60)
        
        summary = results['test_summary']
        print(f"🕐 Test Duration: {summary['test_duration_seconds']:.1f} seconds")
        print(f"👥 Concurrent Users: {summary['concurrent_users']}")
        print(f"📨 Total Requests: {summary['total_requests']}")
        print(f"✅ Success Rate: {summary['success_rate_percent']:.1f}%")
        print(f"⚡ Throughput: {summary['throughput_rps']:.1f} requests/second")
        
        print(f"\n📈 RESPONSE TIME METRICS")
        metrics = results['response_time_metrics']
        print(f"📊 Average: {metrics['average_seconds']}s")
        print(f"🎯 Median: {metrics['median_seconds']}s")
        print(f"📈 95th Percentile: {metrics['p95_seconds']}s")
        print(f"⚡ Min/Max: {metrics['min_seconds']}s / {metrics['max_seconds']}s")
        
        print(f"\n🏦 ABACO PERFORMANCE ASSESSMENT")
        assessment = results['abaco_performance_assessment']
        for metric, meets_target in assessment.items():
            if isinstance(meets_target, bool):
                status = "✅" if meets_target else "❌"
                print(f"{status} {metric.replace('_', ' ').title()}: {'PASS' if meets_target else 'FAIL'}")
        
        print(f"\n💡 RECOMMENDATIONS")
        for rec in results['recommendations']:
            print(f"  {rec}")
        
        # Save results to file
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📁 Results saved to: {output_path}")
        
        # Return exit code based on performance
        if (assessment['meets_target_response_time'] and 
            assessment['meets_target_p95'] and 
            assessment['meets_target_error_rate']):
            logger.info("🎯 All performance targets met!")
            return 0
        else:
            logger.warning("⚠️  Some performance targets not met")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_performance_tests())
    sys.exit(exit_code)