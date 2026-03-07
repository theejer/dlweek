"""Tests for connectivity expectation model used by CURE monitoring."""

from app.services.connectivity_model import (
    estimate_offline_window_minutes,
    should_trigger_alert,
)


def test_estimate_offline_severe_zone():
    """Severe connectivity zones should expect 180-minute offline windows."""
    location = {"connectivity_zone": "severe"}
    result = estimate_offline_window_minutes(location)
    assert result == 180


def test_estimate_offline_high_zone():
    """High connectivity zones should expect 90-minute offline windows."""
    location = {"connectivity_zone": "high"}
    result = estimate_offline_window_minutes(location)
    assert result == 90


def test_estimate_offline_moderate_zone():
    """Moderate connectivity zones should expect 45-minute offline windows."""
    location = {"connectivity_zone": "moderate"}
    result = estimate_offline_window_minutes(location)
    assert result == 45


def test_estimate_offline_default_zone():
    """Locations without severe/high/moderate zones default to 20 minutes."""
    location = {"connectivity_zone": "low"}
    result = estimate_offline_window_minutes(location)
    assert result == 20


def test_estimate_offline_no_zone_field():
    """Locations without connectivity_zone field default to 20 minutes."""
    location = {"name": "Some Location"}
    result = estimate_offline_window_minutes(location)
    assert result == 20


def test_should_trigger_alert_exceeds_threshold():
    """Alert should trigger when actual exceeds expected * 1.5."""
    assert should_trigger_alert(actual_offline_minutes=100, expected_offline_minutes=60) is True
    assert should_trigger_alert(actual_offline_minutes=91, expected_offline_minutes=60) is True


def test_should_trigger_alert_at_threshold():
    """Alert should trigger exactly at 1.5x threshold (int conversion)."""
    # 60 * 1.5 = 90
    assert should_trigger_alert(actual_offline_minutes=90, expected_offline_minutes=60) is False
    # 61 * 1.5 = 91.5, int(91.5) = 91
    assert should_trigger_alert(actual_offline_minutes=91, expected_offline_minutes=61) is False
    assert should_trigger_alert(actual_offline_minutes=92, expected_offline_minutes=61) is True


def test_should_trigger_alert_below_threshold():
    """Alert should NOT trigger when actual is below expected * 1.5."""
    assert should_trigger_alert(actual_offline_minutes=60, expected_offline_minutes=60) is False
    assert should_trigger_alert(actual_offline_minutes=80, expected_offline_minutes=60) is False
    assert should_trigger_alert(actual_offline_minutes=89, expected_offline_minutes=60) is False


def test_should_trigger_alert_zero_expected():
    """Alert should trigger for any actual offline time when expected is zero."""
    assert should_trigger_alert(actual_offline_minutes=0, expected_offline_minutes=0) is False
    assert should_trigger_alert(actual_offline_minutes=1, expected_offline_minutes=0) is True


def test_risk_adaptive_threshold_reduces_false_positives():
    """Verify 1.5x multiplier provides buffer against false positives."""
    # Expected 20 min, actual 25 min -> no alert (within tolerance)
    assert should_trigger_alert(25, 20) is False
    # Expected 20 min, actual 31 min -> alert (exceeds 1.5x = 30)
    assert should_trigger_alert(31, 20) is True
    
    # Expected 180 min (severe zone), actual 250 min -> no alert
    assert should_trigger_alert(250, 180) is False
    # Expected 180 min, actual 271 min -> alert (exceeds 1.5x = 270)
    assert should_trigger_alert(271, 180) is True


def test_connectivity_zones_for_real_scenarios():
    """Test realistic Bihar connectivity scenarios."""
    # Rural highway segment with poor tower coverage
    rural_segment = {"connectivity_zone": "severe", "name": "NH-31 rural stretch"}
    assert estimate_offline_window_minutes(rural_segment) == 180
    
    # District town with intermittent coverage
    town_location = {"connectivity_zone": "high", "name": "Muzaffarpur district"}
    assert estimate_offline_window_minutes(town_location) == 90
    
    # Urban area with reliable coverage
    urban_location = {"connectivity_zone": "moderate", "name": "Patna city center"}
    assert estimate_offline_window_minutes(urban_location) == 45
    
    # Well-connected tourist spot
    tourist_spot = {"connectivity_zone": "low", "name": "Bodh Gaya temple complex"}
    assert estimate_offline_window_minutes(tourist_spot) == 20
