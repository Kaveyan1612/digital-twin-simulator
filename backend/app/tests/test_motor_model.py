import pytest
import time
from app.twin.motor_model import MotorModel
from app.twin.parameters import MotorParameters
from app.twin.faults import FaultType


@pytest.fixture
def motor_params():
    return MotorParameters()


@pytest.fixture
def motor_model(motor_params):
    return MotorModel(motor_params)


def test_motor_initial_state(motor_model):
    assert motor_model.speed == 0.0
    assert motor_model.target_speed == 0.0
    assert motor_model.load == 0.0
    assert motor_model.temperature == 25.0
    assert motor_model.running == False
    assert motor_model.status == "STOPPED"
    assert motor_model.health_score == 100.0


def test_motor_start(motor_model):
    motor_model.start()
    assert motor_model.running == True
    assert motor_model.status == "STARTING"
    assert motor_model.voltage == motor_model.params.rated_voltage


def test_motor_stop(motor_model):
    motor_model.start()
    motor_model.update(0.1)
    motor_model.stop()
    assert motor_model.running == False
    assert motor_model.target_speed == 0.0
    assert motor_model.status == "STOPPING"


def test_motor_emergency_stop(motor_model):
    motor_model.start()
    motor_model.update(0.1)
    motor_model.emergency_stop()
    assert motor_model.running == False
    assert motor_model.target_speed == 0.0
    assert motor_model.load == 0.0
    assert motor_model.status == "EMERGENCY_STOP"


def test_motor_reset(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.load = 50
    motor_model.update(0.1)
    motor_model.reset()
    assert motor_model.speed == 0.0
    assert motor_model.target_speed == 0.0
    assert motor_model.load == 0.0
    assert motor_model.temperature == 25.0
    assert motor_model.running == False
    assert motor_model.status == "STOPPED"


def test_target_speed_change(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.update(0.1)
    assert motor_model.target_speed == 3000


def test_load_change(motor_model):
    motor_model.start()
    motor_model.load = 50
    motor_model.update(0.1)
    assert motor_model.load == 50


def test_voltage_change(motor_model):
    motor_model.start()
    motor_model.voltage = 415
    motor_model.update(0.1)
    assert motor_model.voltage == 415


def test_temperature_responds_to_load(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.load = 80
    initial_temp = motor_model.temperature
    
    for _ in range(50):
        motor_model.update(0.1)
    
    assert motor_model.temperature > initial_temp


def test_current_responds_to_load(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.voltage = 415
    
    motor_model.load = 20
    motor_model.update(0.1)
    current_low = motor_model.current
    
    motor_model.load = 80
    motor_model.update(0.1)
    current_high = motor_model.current
    
    assert current_high > current_low


def test_vibration_responds_to_abnormal_conditions(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.load = 50
    
    for _ in range(20):
        motor_model.update(0.1)
    
    normal_vibration = motor_model.vibration
    
    motor_model.load = 95
    motor_model.temperature = 100
    
    for _ in range(20):
        motor_model.update(0.1)
    
    assert motor_model.vibration > normal_vibration


def test_overtemperature_detected(motor_model):
    motor_model.temperature = 95
    assert motor_model.temperature > 90


def test_overcurrent_detected(motor_model):
    motor_model.current = 45
    assert motor_model.current > 40


def test_overspeed_detected(motor_model):
    motor_model.speed = 4600
    assert motor_model.speed > 4500


def test_fault_injection_overtemperature(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.load = 50
    
    initial_temp = motor_model.temperature
    motor_model.set_fault(FaultType.OVERTEMPERATURE, 1.0)
    
    for _ in range(20):
        motor_model.update(0.1)
    
    assert motor_model.temperature > initial_temp
    assert motor_model.fault_state.active == True
    assert motor_model.fault_state.fault_type == FaultType.OVERTEMPERATURE


def test_fault_injection_overcurrent(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.voltage = 415
    motor_model.load = 50
    
    motor_model.update(0.1)
    initial_current = motor_model.current
    
    motor_model.set_fault(FaultType.OVERCURRENT, 1.0)
    motor_model.update(0.1)
    
    assert motor_model.current > initial_current * 1.5


def test_fault_injection_high_vibration(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.load = 50
    
    motor_model.update(0.1)
    initial_vibration = motor_model.vibration
    
    motor_model.set_fault(FaultType.HIGH_VIBRATION, 1.0)
    motor_model.update(0.1)
    
    assert motor_model.vibration > initial_vibration


def test_fault_injection_overspeed(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    
    motor_model.set_fault(FaultType.OVERSPEED, 1.0)
    
    assert motor_model.target_speed > 3000


def test_fault_injection_undervoltage(motor_model):
    motor_model.start()
    motor_model.voltage = 415
    
    motor_model.set_fault(FaultType.UNDERVOLTAGE, 1.0)
    motor_model.update(0.1)
    
    assert motor_model.voltage < 415


def test_fault_injection_overload(motor_model):
    motor_model.start()
    motor_model.load = 50
    
    motor_model.set_fault(FaultType.OVERLOAD, 1.0)
    
    assert motor_model.load > 50


def test_clear_fault(motor_model):
    motor_model.set_fault(FaultType.OVERTEMPERATURE, 1.0)
    assert motor_model.fault_state.active == True
    
    motor_model.clear_fault()
    assert motor_model.fault_state.active == False


def test_health_score_calculation(motor_model):
    motor_model.temperature = 50
    motor_model.vibration = 2.0
    motor_model.current = 15
    motor_model.speed = 3000
    motor_model.target_speed = 3000
    motor_model.load = 50
    motor_model.efficiency = 0.92
    motor_model.fault_state.active = False
    
    motor_model._update_health_score()
    
    assert 70 < motor_model.health_score <= 100


def test_health_score_degraded_with_fault(motor_model):
    motor_model.temperature = 50
    motor_model.vibration = 2.0
    motor_model.current = 15
    motor_model.speed = 3000
    motor_model.target_speed = 3000
    motor_model.load = 50
    motor_model.efficiency = 0.92
    motor_model.fault_state.active = True
    
    motor_model._update_health_score()
    
    assert motor_model.health_score < 70


def test_motor_state_dict(motor_model):
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.load = 50
    motor_model.update(0.1)
    
    state = motor_model.get_state_dict()
    
    assert "timestamp" in state
    assert "motor_id" in state
    assert "running" in state
    assert "speed" in state
    assert "temperature" in state
    assert "health_score" in state
    assert state["running"] == True