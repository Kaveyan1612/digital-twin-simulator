import pytest
import asyncio
import time
from app.twin.engine import SimulationEngine
from app.twin.motor_model import MotorModel
from app.twin.state import DigitalTwin


@pytest.fixture
def simulation_engine():
    motor_model = MotorModel()
    engine = SimulationEngine(motor_model)
    return engine


@pytest.mark.asyncio
async def test_simulation_engine_start_stop(simulation_engine):
    assert simulation_engine.running == False
    
    await simulation_engine.start()
    assert simulation_engine.running == True
    
    await asyncio.sleep(0.2)
    
    await simulation_engine.stop()
    assert simulation_engine.running == False


@pytest.mark.asyncio
async def test_simulation_engine_updates_motor(simulation_engine):
    motor_model = simulation_engine.motor_model
    motor_model.start()
    motor_model.target_speed = 3000
    motor_model.load = 50
    
    await simulation_engine.start()
    await asyncio.sleep(0.5)
    await simulation_engine.stop()
    
    assert motor_model.speed > 0
    assert motor_model.temperature >= 25


@pytest.mark.asyncio
async def test_simulation_callback(simulation_engine):
    received_states = []
    
    async def callback(state):
        received_states.append(state)
    
    simulation_engine.set_callback(callback)
    motor_model = simulation_engine.motor_model
    motor_model.start()
    motor_model.target_speed = 3000
    
    await simulation_engine.start()
    await asyncio.sleep(0.5)
    await simulation_engine.stop()
    
    assert len(received_states) > 0
    assert "speed" in received_states[0]
    assert "temperature" in received_states[0]


@pytest.mark.asyncio
async def test_digital_twin_integration():
    twin = DigitalTwin(motor_id="TEST-MOTOR")
    received_states = []
    
    async def callback(state):
        received_states.append(state)
    
    twin.set_state_callback(callback)
    await twin.start()
    
    twin.start_motor()
    twin.set_target_speed(3000)
    twin.set_load(50)
    
    await asyncio.sleep(0.5)
    
    await twin.stop()
    
    assert len(received_states) > 0
    state = twin.get_state()
    assert state.motor_id == "TEST-MOTOR"
    assert state.running == True
    assert state.target_speed == 3000
    assert state.load == 50


@pytest.mark.asyncio
async def test_digital_twin_controls():
    twin = DigitalTwin()
    await twin.start()
    
    twin.start_motor()
    state = twin.get_state()
    assert state.running == True
    
    twin.set_target_speed(2500)
    state = twin.get_state()
    assert state.target_speed == 2500
    
    twin.set_load(75)
    state = twin.get_state()
    assert state.load == 75
    
    twin.set_voltage(400)
    state = twin.get_state()
    assert state.voltage == 400
    
    twin.stop_motor()
    await asyncio.sleep(0.2)
    state = twin.get_state()
    assert state.running == False
    
    await twin.stop()


@pytest.mark.asyncio
async def test_digital_twin_fault_injection():
    twin = DigitalTwin()
    await twin.start()
    
    twin.start_motor()
    twin.set_target_speed(3000)
    twin.set_load(50)
    await asyncio.sleep(0.2)
    
    initial_temp = twin.motor_model.temperature
    twin.inject_fault("overtemperature", 1.0)
    await asyncio.sleep(0.5)
    
    assert twin.motor_model.temperature > initial_temp
    assert twin.motor_model.fault_state.active == True
    
    twin.clear_fault()
    assert twin.motor_model.fault_state.active == False
    
    await twin.stop()


@pytest.mark.asyncio
async def test_digital_twin_emergency_stop():
    twin = DigitalTwin()
    await twin.start()
    
    twin.start_motor()
    twin.set_target_speed(3000)
    await asyncio.sleep(0.1)
    
    twin.emergency_stop()
    state = twin.get_state()
    assert state.status == "EMERGENCY_STOP"
    
    await twin.stop()


@pytest.mark.asyncio
async def test_digital_twin_reset():
    twin = DigitalTwin()
    await twin.start()
    
    twin.start_motor()
    twin.set_target_speed(3000)
    twin.set_load(80)
    await asyncio.sleep(0.2)
    
    twin.reset_motor()
    state = twin.get_state()
    assert state.speed == 0
    assert state.target_speed == 0
    assert state.load == 0
    assert state.temperature == 25
    assert state.running == False
    
    await twin.stop()