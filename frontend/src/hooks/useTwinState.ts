import { useCallback } from 'react';
import { websocketService } from '../services/websocket';
import { useTwinStore } from '../store/twinStore';
import { 
  startMotor, stopMotor, resetMotor, emergencyStop,
  setTargetSpeed, setLoad, setVoltage, setOperatingMode,
  injectFault, clearFault
} from '../services/api';
import type { FaultType } from '../types/twin';

export function useTwinControls() {
  const addEvent = useTwinStore((s) => s.addEvent);

  const sendCommand = useCallback((type: string, value?: number, fault?: string) => {
    websocketService.sendCommand(type, value, fault);
  }, []);

  const handleStart = useCallback(async () => {
    try {
      await startMotor();
      sendCommand('start_motor');
      addEvent({ timestamp: Date.now(), message: 'Motor started', type: 'command' });
    } catch (e) {
      console.error('Failed to start motor:', e);
    }
  }, [sendCommand, addEvent]);

  const handleStop = useCallback(async () => {
    try {
      await stopMotor();
      sendCommand('stop_motor');
      addEvent({ timestamp: Date.now(), message: 'Motor stopped', type: 'command' });
    } catch (e) {
      console.error('Failed to stop motor:', e);
    }
  }, [sendCommand, addEvent]);

  const handleReset = useCallback(async () => {
    try {
      await resetMotor();
      sendCommand('reset_motor');
      addEvent({ timestamp: Date.now(), message: 'Motor reset', type: 'command' });
    } catch (e) {
      console.error('Failed to reset motor:', e);
    }
  }, [sendCommand, addEvent]);

  const handleEmergencyStop = useCallback(async () => {
    try {
      await emergencyStop();
      sendCommand('emergency_stop');
      addEvent({ timestamp: Date.now(), message: 'EMERGENCY STOP ACTIVATED', type: 'emergency' });
    } catch (e) {
      console.error('Failed to emergency stop:', e);
    }
  }, [sendCommand, addEvent]);

  const handleSetTargetSpeed = useCallback(async (value: number) => {
    try {
      await setTargetSpeed(value);
      sendCommand('set_target_speed', value);
      addEvent({ timestamp: Date.now(), message: `Target speed set to ${value} RPM`, type: 'command' });
    } catch (e) {
      console.error('Failed to set target speed:', e);
    }
  }, [sendCommand, addEvent]);

  const handleSetLoad = useCallback(async (value: number) => {
    try {
      await setLoad(value);
      sendCommand('set_load', value);
      addEvent({ timestamp: Date.now(), message: `Load set to ${value}%`, type: 'command' });
    } catch (e) {
      console.error('Failed to set load:', e);
    }
  }, [sendCommand, addEvent]);

  const handleSetVoltage = useCallback(async (value: number) => {
    try {
      await setVoltage(value);
      sendCommand('set_voltage', value);
      addEvent({ timestamp: Date.now(), message: `Voltage set to ${value}V`, type: 'command' });
    } catch (e) {
      console.error('Failed to set voltage:', e);
    }
  }, [sendCommand, addEvent]);

  const handleSetOperatingMode = useCallback(async (mode: string) => {
    try {
      await setOperatingMode(mode);
      sendCommand('set_operating_mode', undefined, mode);
      addEvent({ timestamp: Date.now(), message: `Operating mode set to ${mode}`, type: 'command' });
    } catch (e) {
      console.error('Failed to set operating mode:', e);
    }
  }, [sendCommand, addEvent]);

  const handleInjectFault = useCallback(async (fault: FaultType, intensity: number = 1.0) => {
    try {
      await injectFault(fault, intensity);
      sendCommand('inject_fault', intensity, fault);
      addEvent({ timestamp: Date.now(), message: `Fault injected: ${fault}`, type: 'fault' });
    } catch (e) {
      console.error('Failed to inject fault:', e);
    }
  }, [sendCommand, addEvent]);

  const handleClearFault = useCallback(async () => {
    try {
      await clearFault();
      sendCommand('clear_fault');
      addEvent({ timestamp: Date.now(), message: 'Fault cleared', type: 'command' });
    } catch (e) {
      console.error('Failed to clear fault:', e);
    }
  }, [sendCommand, addEvent]);

  return {
    start: handleStart,
    stop: handleStop,
    reset: handleReset,
    emergencyStop: handleEmergencyStop,
    setTargetSpeed: handleSetTargetSpeed,
    setLoad: handleSetLoad,
    setVoltage: handleSetVoltage,
    setOperatingMode: handleSetOperatingMode,
    injectFault: handleInjectFault,
    clearFault: handleClearFault,
  };
}