# Task 045: Simulation Mode Backend

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 4: Simulation Mode

## Description

Implement simulation mode for device operations, allowing demos and testing without physical ZKTeco devices.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Simulation mode toggle via environment variable
2. [ ] Simulated device connection service exists
3. [ ] Simulated connection tests always succeed (with delay)
4. [ ] Simulated device status is random (online/offline)
5. [ ] Simulated device capacity available
6. [ ] Health checks work in simulation mode
7. [ ] All device operations work in simulation mode
8. [ ] Simulation mode clearly indicated in responses/logs

## Technical Details

### Files to Create/Modify

```
backend/device_service/services/device_simulator.py
backend/device_service/services/device_connection.py (add simulation support)
backend/device_service/core/config.py (add SIMULATION_MODE setting)
```

### Key Code Patterns

```python
# services/device_simulator.py
import asyncio
import random
from datetime import datetime
from typing import Optional, Dict
from device_service.core.config import settings

class DeviceSimulator:
    """Simulates ZKTeco device behavior for testing and demos."""
    
    def __init__(self):
        self.simulated_devices: Dict[str, dict] = {}
    
    async def simulate_connection_test(
        self,
        ip_address: str,
        port: int,
        timeout: int = 5
    ) -> dict:
        """Simulate device connection test."""
        # Simulate connection delay (1-3 seconds)
        delay = random.uniform(1.0, 3.0)
        await asyncio.sleep(min(delay, timeout))
        
        # Simulate success (95% success rate)
        success = random.random() > 0.05
        
        if success:
            return {
                "success": True,
                "message": "Simulated connection successful",
                "response_time_ms": int(delay * 1000),
                "device_info": {
                    "model": "ZK-Teco F18 (Simulated)",
                    "firmware": "6.60.1.0 (Simulated)",
                    "serial": f"SIM-{ip_address.replace('.', '')}-{port}",
                }
            }
        else:
            return {
                "success": False,
                "message": "Simulated connection failed (timeout)",
            }
    
    async def simulate_device_status(self, device_id: int) -> str:
        """Simulate device status (random online/offline)."""
        # 90% online rate in simulation
        return "online" if random.random() > 0.1 else "offline"
    
    async def simulate_device_capacity(self, device_id: int) -> dict:
        """Simulate device capacity information."""
        # Random capacity between 500-2000 users
        max_users = random.randint(500, 2000)
        enrolled_users = random.randint(0, int(max_users * 0.7))  # 0-70% enrolled
        
        return {
            "max_users": max_users,
            "enrolled_users": enrolled_users,
            "available": max_users - enrolled_users,
        }
    
    async def simulate_health_check(self, device_id: int) -> dict:
        """Simulate health check result."""
        status = await self.simulate_device_status(device_id)
        
        return {
            "device_id": device_id,
            "status": status,
            "last_seen": datetime.utcnow().isoformat() if status == "online" else None,
            "response_time_ms": random.randint(100, 500),
        }

# services/device_connection.py
from device_service.core.config import settings
from device_service.services.device_simulator import DeviceSimulator

class DeviceConnectionService:
    """Service for device connection operations."""
    
    def __init__(self):
        self.simulator = DeviceSimulator() if settings.SIMULATION_MODE else None
    
    async def test_connection(
        self,
        ip_address: str,
        port: int,
        timeout: int = 5
    ) -> dict:
        """Test device connection (real or simulated)."""
        if settings.SIMULATION_MODE:
            return await self.simulator.simulate_connection_test(
                ip_address, port, timeout
            )
        
        # Real device connection logic
        # ... (from Task 034)
    
    async def get_device_capacity(
        self,
        ip_address: str,
        port: int
    ) -> int:
        """Get device capacity (real or simulated)."""
        if settings.SIMULATION_MODE:
            # Return simulated capacity
            return random.randint(500, 2000)
        
        # Real device capacity retrieval
        # ... (using ZKTeco protocol)
```

### Dependencies

- Task 041 (Health check service - add simulation support)
- Task 034 (Connection test API - add simulation support)

## Visual Testing

### Before State
- Requires physical devices for testing
- Cannot demo without hardware

### After State
- Can test and demo without devices
- Simulated responses work correctly
- Simulation mode clearly indicated

### Testing Steps

1. Enable simulation mode
2. Test device registration
3. Test connection test - verify simulated success
4. Test health checks - verify simulated status
5. Test capacity retrieval - verify simulated capacity
6. Verify all operations work in simulation mode

## Definition of Done

- [ ] Code written and follows standards
- [ ] Simulation mode implemented
- [ ] All device operations work in simulation
- [ ] Simulated responses realistic
- [ ] Simulation mode clearly indicated
- [ ] Configuration via environment variable
- [ ] Unit tests written and passing
- [ ] Code reviewed

## Time Estimate

4-5 hours

## Notes

- Simulation mode enabled via `SIMULATION_MODE=true` environment variable
- Simulated responses should be realistic (delays, success rates)
- 90% online rate in simulation (for realistic demos)
- Simulated device info includes "Simulated" label
- Consider configurable simulation parameters (delays, success rates)

