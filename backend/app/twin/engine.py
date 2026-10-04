import asyncio
import time
from typing import Optional, Callable, Awaitable
from app.twin.motor_model import MotorModel
from app.twin.parameters import MotorParameters
from app.core.config import settings
from app.core.logging import logger


class SimulationEngine:
    def __init__(self, motor_model: MotorModel = None):
        self.motor_model = motor_model or MotorModel()
        self.running = False
        self.simulation_task: Optional[asyncio.Task] = None
        self.callback: Optional[Callable[[dict], Awaitable[None]]] = None
        self.simulation_frequency = settings.simulation_frequency
        self.websocket_update_rate = settings.websocket_update_rate
        self.update_counter = 0
        self.last_websocket_update = 0
        self.start_time = time.time()
    
    def set_callback(self, callback: Callable[[dict], Awaitable[None]]):
        self.callback = callback
    
    async def start(self):
        if self.running:
            return
        self.running = True
        self.simulation_task = asyncio.create_task(self._simulation_loop())
        logger.info("Simulation engine started")
    
    async def stop(self):
        self.running = False
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass
        logger.info("Simulation engine stopped")
    
    async def _simulation_loop(self):
        dt = 1.0 / self.simulation_frequency
        websocket_interval = 1.0 / self.websocket_update_rate
        
        while self.running:
            loop_start = time.time()
            
            self.motor_model.update(dt)
            self.update_counter += 1
            
            current_time = time.time()
            if current_time - self.last_websocket_update >= websocket_interval:
                if self.callback:
                    try:
                        state = self.motor_model.get_state_dict()
                        await self.callback(state)
                    except Exception as e:
                        logger.error(f"Error in simulation callback: {e}")
                self.last_websocket_update = current_time
            
            elapsed = time.time() - loop_start
            sleep_time = max(0, dt - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    def get_uptime(self) -> float:
        return time.time() - self.start_time
    
    def get_update_count(self) -> int:
        return self.update_counter