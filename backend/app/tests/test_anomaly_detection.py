import pytest
from app.anomaly.rules import RuleEngine, DEFAULT_RULES
from app.anomaly.detector import AnomalyDetector
from app.schemas.motor import MotorState, AnomalySeverity
from app.core.config import settings
import time


@pytest.fixture
def rule_engine():
    return RuleEngine()


@pytest.fixture
def normal_state():
    return MotorState(
        timestamp=time.time(),
        motor_id="MOTOR-001",
        running=True,
        operating_mode="NORMAL",
        target_speed=3000,
        speed=2950,
        load=50,
        torque=30,
        voltage=415,
        current=15,
        power=5.5,
        temperature=60,
        vibration=1.5,
        efficiency=92,
        health_score=95,
        status="RUNNING",
        anomaly_detected=False,
        anomaly_type=None,
        anomaly_severity=AnomalySeverity.INFO,
    )


@pytest.fixture
def overtemperature_state():
    return MotorState(
        timestamp=time.time(),
        motor_id="MOTOR-001",
        running=True,
        operating_mode="NORMAL",
        target_speed=3000,
        speed=2950,
        load=50,
        torque=30,
        voltage=415,
        current=15,
        power=5.5,
        temperature=95,
        vibration=1.5,
        efficiency=92,
        health_score=85,
        status="RUNNING",
        anomaly_detected=False,
        anomaly_type=None,
        anomaly_severity=AnomalySeverity.INFO,
    )


@pytest.fixture
def overcurrent_state():
    return MotorState(
        timestamp=time.time(),
        motor_id="MOTOR-001",
        running=True,
        operating_mode="NORMAL",
        target_speed=3000,
        speed=2950,
        load=80,
        torque=45,
        voltage=415,
        current=45,
        power=12,
        temperature=75,
        vibration=2.5,
        efficiency=85,
        health_score=70,
        status="RUNNING",
        anomaly_detected=False,
        anomaly_type=None,
        anomaly_severity=AnomalySeverity.INFO,
    )


@pytest.fixture
def overspeed_state():
    return MotorState(
        timestamp=time.time(),
        motor_id="MOTOR-001",
        running=True,
        operating_mode="NORMAL",
        target_speed=4600,
        speed=4650,
        load=30,
        torque=20,
        voltage=415,
        current=12,
        power=4,
        temperature=55,
        vibration=3.0,
        efficiency=88,
        health_score=75,
        status="RUNNING",
        anomaly_detected=False,
        anomaly_type=None,
        anomaly_severity=AnomalySeverity.INFO,
    )


@pytest.fixture
def high_vibration_state():
    return MotorState(
        timestamp=time.time(),
        motor_id="MOTOR-001",
        running=True,
        operating_mode="NORMAL",
        target_speed=3000,
        speed=2950,
        load=50,
        torque=30,
        voltage=415,
        current=15,
        power=5.5,
        temperature=60,
        vibration=6.5,
        efficiency=90,
        health_score=60,
        status="RUNNING",
        anomaly_detected=False,
        anomaly_type=None,
        anomaly_severity=AnomalySeverity.INFO,
    )


def test_rule_engine_normal_state(rule_engine, normal_state):
    anomalies = rule_engine.evaluate(normal_state)
    assert len(anomalies) == 0


def test_rule_engine_overtemperature_warning(rule_engine, overtemperature_state):
    anomalies = rule_engine.evaluate(overtemperature_state)
    assert len(anomalies) > 0
    temp_anomalies = [a for a in anomalies if "TEMPERATURE" in a["anomaly_type"]]
    assert len(temp_anomalies) > 0
    assert temp_anomalies[0]["severity"] == AnomalySeverity.HIGH


def test_rule_engine_overtemperature_critical(rule_engine):
    state = overtemperature_state
    state.temperature = 115
    
    anomalies = rule_engine.evaluate(state)
    critical_anomalies = [a for a in anomalies if a["severity"] == AnomalySeverity.CRITICAL]
    assert len(critical_anomalies) > 0


def test_rule_engine_overcurrent_warning(rule_engine, overcurrent_state):
    anomalies = rule_engine.evaluate(overcurrent_state)
    current_anomalies = [a for a in anomalies if "CURRENT" in a["anomaly_type"]]
    assert len(current_anomalies) > 0
    assert current_anomalies[0]["severity"] == AnomalySeverity.HIGH


def test_rule_engine_overspeed_warning(rule_engine, overspeed_state):
    anomalies = rule_engine.evaluate(overspeed_state)
    speed_anomalies = [a for a in anomalies if "SPEED" in a["anomaly_type"]]
    assert len(speed_anomalies) > 0
    assert speed_anomalies[0]["severity"] == AnomalySeverity.HIGH


def test_rule_engine_high_vibration_warning(rule_engine, high_vibration_state):
    anomalies = rule_engine.evaluate(high_vibration_state)
    vib_anomalies = [a for a in anomalies if "VIBRATION" in a["anomaly_type"]]
    assert len(vib_anomalies) > 0
    assert vib_anomalies[0]["severity"] == AnomalySeverity.MEDIUM


def test_rule_engine_persistent_speed_deviation(rule_engine):
    state = MotorState(
        timestamp=time.time(),
        motor_id="MOTOR-001",
        running=True,
        operating_mode="NORMAL",
        target_speed=3000,
        speed=2500,
        load=50,
        torque=30,
        voltage=415,
        current=15,
        power=5.5,
        temperature=60,
        vibration=1.5,
        efficiency=92,
        health_score=95,
        status="RUNNING",
        anomaly_detected=False,
        anomaly_type=None,
        anomaly_severity=AnomalySeverity.INFO,
    )
    
    for _ in range(10):
        anomalies = rule_engine.evaluate(state)
    
    dev_anomalies = [a for a in anomalies if "SPEED_DEVIATION" in a["anomaly_type"]]
    assert len(dev_anomalies) > 0


def test_anomaly_detector_integration(overtemperature_state):
    detector = AnomalyDetector()
    anomalies = detector.detect(overtemperature_state)
    
    assert len(anomalies) > 0
    assert overtemperature_state.anomaly_detected == True
    assert overtemperature_state.anomaly_type is not None


def test_anomaly_severity_ranking():
    detector = AnomalyDetector()
    
    assert detector._severity_rank(AnomalySeverity.INFO) == 0
    assert detector._severity_rank(AnomalySeverity.LOW) == 1
    assert detector._severity_rank(AnomalySeverity.MEDIUM) == 2
    assert detector._severity_rank(AnomalySeverity.HIGH) == 3
    assert detector._severity_rank(AnomalySeverity.CRITICAL) == 4


def test_default_rules_exist():
    assert len(DEFAULT_RULES) > 0
    
    rule_names = [r.name for r in DEFAULT_RULES]
    assert "overtemperature_warning" in rule_names
    assert "overtemperature_critical" in rule_names
    assert "overcurrent_warning" in rule_names
    assert "overcurrent_critical" in rule_names
    assert "overspeed_warning" in rule_names
    assert "overspeed_critical" in rule_names
    assert "high_vibration_warning" in rule_names
    assert "high_vibration_critical" in rule_names
    assert "overload_warning" in rule_names
    assert "undervoltage_warning" in rule_names


def test_add_remove_rule(rule_engine):
    initial_count = len(rule_engine.config.rules)
    
    from app.schemas.anomaly import AnomalyRule
    new_rule = AnomalyRule(
        name="test_rule",
        parameter="temperature",
        condition=">",
        threshold=100,
        severity=AnomalySeverity.HIGH,
        description="Test rule",
    )
    
    rule_engine.add_rule(new_rule)
    assert len(rule_engine.config.rules) == initial_count + 1
    
    rule_engine.remove_rule("test_rule")
    assert len(rule_engine.config.rules) == initial_count