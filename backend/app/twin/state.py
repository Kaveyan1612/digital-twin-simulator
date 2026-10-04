from app.twin.motor_model import MotorModel
from app.twin.engine import SimulationEngine
from app.twin.parameters import MotorParameters
from app.schemas.motor import MotorState, MotorConfig
from app.core.logging import logger
import time


class DigitalTwin:
    def __init__(self, motor_id: str = "MOTOR-001"):
        self.motor_id = motor_id
        self.params = MotorParameters(motor_id=motor_id)
        self.motor_model = MotorModel(self.params)
        self.simulation_engine = SimulationEngine(self.motor_model)
        self.state_callback = None
    
    def set_state_callback(self, callback):
        self.state_callback = callback
        self.simulation_engine.set_callback(callback)
    
    async def start(self):
        await self.simulation_engine.start()
        logger.info(f"Digital twin {self.motor_id} started")
    
    async def stop(self):
        await self.simulation_engine.stop()
        logger.info(f"Digital twin {self.motor_id} stopped")
    
    def get_state(self) -> MotorState:
        state_dict = self.motor_model.get_state_dict()
        return MotorState(**state_dict)
    
    def get_state_dict(self) -> dict:
        return self.motor_model.get_state_dict()
    
    def set_target_speed(self, speed: float):
        self.motor_model.target_speed = speed
        self.motor_model.operating_mode = "NORMAL"
        logger.info(f"Target speed set to {speed} RPM")
    
    def set_load(self, load: float):
        self.motor_model.load = load
        logger.info(f"Load set to {load}%")
    
    def set_voltage(self, voltage: float):
        self.motor_model.voltage = voltage
        logger.info(f"Voltage set to {voltage}V")
    
    def set_operating_mode(self, mode: str):
        self.motor_model.operating_mode = mode
        logger.info(f"Operating mode set to {mode}")
    
    def start_motor(self):
        self.motor_model.start()
    
    def stop_motor(self):
        self.motor_model.stop()
    
    def emergency_stop(self):
        self.motor_model.emergency_stop()
    
    def reset_motor(self):
        self.motor_model.reset()
        logger.info("Motor reset")
    
    def inject_fault(self, fault_type: str, intensity: float = 1.0):
        from app.twin.faults import FaultType
        try:
            fault = FaultType(fault_type)
            self.motor_model.set_fault(fault, intensity)
        except ValueError:
            logger.error(f"Unknown fault type: {fault_type}")
            raise
    
    def clear_fault(self):
        self.motor_model.clear_fault()
    
    def get_config(self) -> MotorConfig:
        return MotorConfig(
            motor_id=self.params.motor_id,
            max_speed=self.params.max_speed,
            max_temperature=self.params.max_temperature,
            max_current=self.params.max_current,
            max_vibration=self.params.max_vibration,
            max_load=self.params.max_load,
            max_voltage=self.params.max_voltage,
            rated_power=self.params.rated_power,
            rated_torque=self.params.rated_torque,
            rated_speed=self.params.rated_speed,
            rated_current=self.params.rated_current,
            rated_voltage=self.params.rated_voltage,
            inertia=self.params.inertia,
            thermal_resistance=self.params.thermal_resistance,
            thermal_capacitance=self.params.thermal_capacitance,
            cooling_coefficient=self.params.cooling_coefficient,
            friction_coefficient=self.params.friction_coefficient,
            efficiency_base=self.params.efficiency_base,
        )
    
    def get_uptime(self) -> float:
        return self.simulation_engine.get_uptime()
    
    def get_update_count(self) -> int:
        return self.simulation_engine.get_update_count()


digital_twin = DigitalTwin()