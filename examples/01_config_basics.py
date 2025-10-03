"""
Example: Basic configuration usage

Demonstrates how to load and access the manifest configuration.
"""

from abaco_core import Config


def main():
    # Load configuration
    config = Config()
    print("Configuration loaded successfully\n")
    
    # Access bucket definitions
    print("=== Bucket Definitions ===")
    apr_buckets = config.get("apr_buckets")
    print(f"APR Buckets: {', '.join(apr_buckets)}")
    
    line_buckets = config.get("line_buckets")
    print(f"Line Buckets: {', '.join(line_buckets)}")
    
    client_types = config.get("client_type")
    print(f"Client Types: {', '.join(client_types)}")
    
    # Access optimizer constraints
    print("\n=== Optimizer Constraints ===")
    optimizer = config.optimizer
    
    print("Target Mix (APR):")
    for bucket, target in optimizer["target_mix"]["apr"].items():
        print(f"  {bucket}: {target:.1%}")
    
    print("\nHard Limits (APR):")
    for bucket, limit in optimizer["hard_limits"]["apr"].items():
        print(f"  {bucket}: max {limit['max_pct']:.1%}")
    
    print("\nPriority Weights:")
    for weight, value in optimizer["priority_weights"].items():
        print(f"  {weight}: {value:.1%}")
    
    # Access alert thresholds
    print("\n=== Alert Thresholds ===")
    alerts = config.alerts
    
    print("Concentration Alerts:")
    conc = alerts["concentration"]
    print(f"  Top-1 max: {conc['top1_max_pct']:.1%}")
    print(f"  Any client max: {conc['any_gt_pct']:.1%}")
    print(f"  Growth threshold: {conc['growth_bps']} bps")
    
    print("\nRisk Alerts:")
    risk = alerts["risk"]
    print(f"  NPL≥180 MoM: {risk['npl180_mom_bps']} bps")
    print(f"  Roll-rate sigma: {risk['rollrate_sigma']}σ")
    print(f"  DPD growth (7d): {risk['dpd6090_or_180_growth_7d']:.1%}")


if __name__ == "__main__":
    main()
