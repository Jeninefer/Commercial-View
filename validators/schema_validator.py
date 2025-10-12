#!/usr/bin/env python3
"""
Schema Validator for Commercial-View Configuration Files

This module validates configuration files against their expected schemas
to ensure data integrity and catch configuration errors early.
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')
try:
    import yaml
except ImportError:
    logging.error("PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


class ConfigValidator:
    """Validates configuration files against schemas."""

    def __init__(self, config_dir: str = "./config"):
        """Initialize the validator with configuration directory."""
        self.config_dir = Path(config_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_yaml(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file and return parsed content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parse error in {filepath}: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Error loading {filepath}: {e}")
            return None

    def validate_column_maps(self, config: Dict[str, Any]) -> bool:
        """Validate column mapping configuration."""
        valid = True

        # Check for required top-level sections
        required_sections = ['loan_data', 'dpd_frame_output', 'buckets_output']
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section: {section}")
                valid = False

        # Validate loan_data mappings
        if 'loan_data' in config:
            required_loan_fields = [
                'loan_id', 'customer_id', 'loan_amount', 'outstanding_balance',
                'origination_date', 'days_past_due', 'past_due_amount'
            ]
            for field in required_loan_fields:
                if field not in config['loan_data']:
                    self.warnings.append(f"Recommended field missing in loan_data: {field}")

        # Validate DPD frame output mappings
        if 'dpd_frame_output' in config:
            required_dpd_fields = [
                'past_due_amount', 'days_past_due', 'first_arrears_date',
                'last_payment_date', 'last_due_date', 'is_default', 'reference_date'
            ]
            for field in required_dpd_fields:
                if field not in config['dpd_frame_output']:
                    self.errors.append(f"Required DPD output field missing: {field}")
                    valid = False

        # Validate buckets output mappings
        if 'buckets_output' in config:
            required_bucket_fields = [
                'dpd_bucket', 'dpd_bucket_value', 'dpd_bucket_description', 'default_flag'
            ]
            for field in required_bucket_fields:
                if field not in config['buckets_output']:
                    self.errors.append(f"Required bucket output field missing: {field}")
                    valid = False

        return valid

    def validate_pricing_config(self, config: Dict[str, Any]) -> bool:
        """Validate pricing configuration."""
        valid = True

        # Check for required sections
        if 'pricing_files' not in config:
            self.errors.append("Missing required section: pricing_files")
            valid = False

        if 'band_keys' not in config:
            self.errors.append("Missing required section: band_keys")
            valid = False

        # Validate band_keys structure
        if 'band_keys' in config:
            required_bands = ['tenor_days', 'amount']
            required_fields = ['lower_bound', 'upper_bound']
            for band in required_bands:
                if band not in config['band_keys']:
                    self.errors.append(f"Required band key missing: {band}")
                    valid = False
                else:
                    band_config = config['band_keys'][band]
                    for field in required_fields:
                        if field not in band_config:
                            self.errors.append(f"Band {band} missing {field}")
                            valid = False

        # Validate pricing grid structure
        if 'pricing_grid' in config:
            if 'required_columns' in config['pricing_grid']:
                required_cols = config['pricing_grid']['required_columns']
                if not isinstance(required_cols, list):
                    self.errors.append("pricing_grid.required_columns must be a list")
                    valid = False

        return valid

    def validate_dpd_policy(self, config: Dict[str, Any]) -> bool:
        """Validate DPD policy configuration."""
        valid = True

        # Check for required sections
        if 'default_threshold' not in config:
            self.errors.append("Missing required section: default_threshold")
            valid = False
        else:
            if 'days' not in config['default_threshold']:
                self.errors.append("default_threshold missing 'days' field")
                valid = False
            else:
                days = config['default_threshold']['days']
                if not isinstance(days, int) or days < 0:
                    self.errors.append(f"default_threshold.days must be a positive integer, got: {days}")
                    valid = False

        # Validate DPD buckets
        if 'dpd_buckets' not in config:
            self.errors.append("Missing required section: dpd_buckets")
            valid = False
        else:
            buckets = config['dpd_buckets']
            if not isinstance(buckets, list) or len(buckets) == 0:
                self.errors.append("dpd_buckets must be a non-empty list")
                valid = False
            else:
                for i, bucket in enumerate(buckets):
                    required_fields = ['bucket', 'value', 'min_dpd', 'description', 'default_flag']
                    for field in required_fields:
                        if field not in bucket:
                            self.errors.append(f"Bucket {i} missing required field: {field}")
                            valid = False

                    # Validate min_dpd and max_dpd relationship
                    if 'min_dpd' in bucket and 'max_dpd' in bucket:
                        min_dpd = bucket['min_dpd']
                        max_dpd = bucket['max_dpd']
                        if max_dpd is not None and min_dpd > max_dpd:
                            self.errors.append(f"Bucket {i}: min_dpd ({min_dpd}) > max_dpd ({max_dpd})")
                            valid = False

        return valid

    def validate_export_config(self, config: Dict[str, Any]) -> bool:
        """Validate export configuration."""
        valid = True

        # Check for required sections
        required_sections = ['export_paths', 'file_naming', 'export_formats']
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section: {section}")
                valid = False

        # Validate export paths
        if 'export_paths' in config:
            if 'base_path' not in config['export_paths']:
                self.errors.append("export_paths missing base_path")
                valid = False

        # Validate file naming
        if 'file_naming' in config:
            if 'timestamp_format' not in config['file_naming']:
                self.warnings.append("file_naming missing timestamp_format, using default")

        # Validate export formats
        if 'export_formats' in config:
            for format_name in ['dpd_frame', 'buckets', 'kpi']:
                if format_name not in config['export_formats']:
                    self.warnings.append(f"Export format not defined: {format_name}")

        return valid

    def validate_all(self) -> bool:
        """Validate all configuration files."""
        print("=" * 70)
        print("Configuration Validation Report")
        print("=" * 70)

        all_valid = True

        # Column maps validation
        column_maps_path = self.config_dir / "column_maps.yml"
        if column_maps_path.exists():
            print(f"\n[1/4] Validating: {column_maps_path}")
            config = self.load_yaml(column_maps_path)
            if config:
                valid = self.validate_column_maps(config)
                all_valid = all_valid and valid
                print(f"  Status: {'✓ PASSED' if valid else '✗ FAILED'}")
            else:
                all_valid = False
                print("  Status: ✗ FAILED (could not load file)")
        else:
            print(f"\n[1/4] WARNING: {column_maps_path} not found")
            self.warnings.append(f"Configuration file not found: {column_maps_path}")

        # Pricing config validation
        pricing_config_path = self.config_dir / "pricing_config.yml"
        if pricing_config_path.exists():
            print(f"\n[2/4] Validating: {pricing_config_path}")
            config = self.load_yaml(pricing_config_path)
            if config:
                valid = self.validate_pricing_config(config)
                all_valid = all_valid and valid
                print(f"  Status: {'✓ PASSED' if valid else '✗ FAILED'}")
            else:
                all_valid = False
                print("  Status: ✗ FAILED (could not load file)")
        else:
            print(f"\n[2/4] WARNING: {pricing_config_path} not found")
            self.warnings.append(f"Configuration file not found: {pricing_config_path}")

        # DPD policy validation
        dpd_policy_path = self.config_dir / "dpd_policy.yml"
        if dpd_policy_path.exists():
            print(f"\n[3/4] Validating: {dpd_policy_path}")
            config = self.load_yaml(dpd_policy_path)
            if config:
                valid = self.validate_dpd_policy(config)
                all_valid = all_valid and valid
                print(f"  Status: {'✓ PASSED' if valid else '✗ FAILED'}")
            else:
                all_valid = False
                print("  Status: ✗ FAILED (could not load file)")
        else:
            print(f"\n[3/4] WARNING: {dpd_policy_path} not found")
            self.warnings.append(f"Configuration file not found: {dpd_policy_path}")

        # Export config validation
        export_config_path = self.config_dir / "export_config.yml"
        if export_config_path.exists():
            print(f"\n[4/4] Validating: {export_config_path}")
            config = self.load_yaml(export_config_path)
            if config:
                valid = self.validate_export_config(config)
                all_valid = all_valid and valid
                print(f"  Status: {'✓ PASSED' if valid else '✗ FAILED'}")
            else:
                all_valid = False
                print("  Status: ✗ FAILED (could not load file)")
        else:
            print(f"\n[4/4] WARNING: {export_config_path} not found")
            self.warnings.append(f"Configuration file not found: {export_config_path}")

        # Print summary
        print("\n" + "=" * 70)
        print("Validation Summary")
        print("=" * 70)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
        elif not self.errors:
            print("\n✅ No errors found (but there are warnings)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)")

        print("=" * 70)

        return all_valid


def main():
    """Main entry point for the validator."""
    # Determine config directory
    script_dir = Path(__file__).parent.parent
    config_dir = script_dir / "config"

    if not config_dir.exists():
        print(f"ERROR: Config directory not found: {config_dir}")
        sys.exit(1)

    # Run validation
    validator = ConfigValidator(str(config_dir))
    all_valid = validator.validate_all()

    # Exit with appropriate code
    if all_valid:
        sys.exit(0)
    else:
        print("\nERROR: Validation failed. See errors above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
