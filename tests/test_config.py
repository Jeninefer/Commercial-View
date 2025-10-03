"""
Test configuration module.
"""

import pytest
from config import validate_config, get_config_summary, BRAND_COLORS, AI_PERSONAS


def test_brand_colors():
    """Test brand colors are configured."""
    assert 'primary_dark' in BRAND_COLORS
    assert 'primary_purple' in BRAND_COLORS
    assert BRAND_COLORS['primary_dark'] == '#030E19'
    assert BRAND_COLORS['primary_purple'] == '#221248'


def test_ai_personas():
    """Test AI personas are configured."""
    assert 'ceo' in AI_PERSONAS
    assert 'cfo' in AI_PERSONAS
    assert 'treasury_manager' in AI_PERSONAS
    
    ceo_persona = AI_PERSONAS['ceo']
    assert 'name' in ceo_persona
    assert 'perspective' in ceo_persona
    assert 'focus' in ceo_persona


def test_config_summary():
    """Test configuration summary."""
    summary = get_config_summary()
    assert isinstance(summary, dict)
    assert 'daily_job_time' in summary
    assert 'timezone' in summary
    assert 'output_format' in summary


def test_validate_config():
    """Test configuration validation."""
    is_valid, errors = validate_config()
    
    # Should return tuple
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)
    
    # If invalid, should have error messages
    if not is_valid:
        assert len(errors) > 0
        for error in errors:
            assert isinstance(error, str)
