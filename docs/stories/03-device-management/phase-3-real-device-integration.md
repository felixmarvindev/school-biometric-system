# Phase 3: Real Device Integration

## Goal

Integrate with real ZKTeco devices to fetch device information, establish connections, and retrieve device details directly from hardware. This replaces the need for simulation mode and enables working with actual devices.

## Duration Estimate

5-7 days

## Prerequisites

- ✅ Phase 2 complete (devices and groups working)
- ✅ ZKTeco device available for testing
- ✅ Network connectivity to device

## Technical Components

### Backend Changes

- [ ] Integrate ZKTeco Python library
- [ ] Create device connection service (real device communication)
- [ ] Implement device discovery/fetching device info during registration
- [ ] Add endpoint to fetch device serial number from real device
- [ ] Add endpoint to fetch device model/firmware version
- [ ] Implement `CMD_GET_FREE_SIZES` to get real device capacity (max_users)
- [ ] Implement `CMD_GET_TIME` to get device time
- [ ] Add device info refresh endpoint (fetches all details from device)
- [ ] Update device registration to auto-populate fields from device
- [ ] Implement real device connection testing (not just TCP)
- [ ] Add error handling for device communication failures
- [ ] Create device communication service abstraction

### Frontend Changes

- [ ] Add "Fetch Device Info" button during device registration
- [ ] Show device info loading state
- [ ] Display fetched device details (serial, model, firmware, capacity)
- [ ] Add "Refresh Device Info" button on device detail page
- [ ] Show device connection status from real device communication
- [ ] Display real-time device capacity from device

## Visual Checkpoints

- [ ] Can connect to real device during registration
- [ ] Device serial number auto-populated from device
- [ ] Device model and firmware version displayed
- [ ] Real device capacity (max_users) fetched and displayed
- [ ] Device connection test uses real ZKTeco protocol (not just TCP)
- [ ] Device info refresh works and updates database
- [ ] Error messages shown when device communication fails

## Tasks Breakdown

See [tasks/](tasks/) folder:
- [Task 047: ZKTeco Library Integration Setup](tasks/task-047-zkteco-library-integration.md) - Set up ZKTeco library and foundational infrastructure
- [Task 048: Device Connection Service](tasks/task-048-device-connection-service.md) - Create device connection service with pooling
- [Task 049: Fetch Device Serial Number](tasks/task-049-fetch-device-serial.md) - Get serial number from real device
- [Task 050: Fetch Device Model and Firmware](tasks/task-050-fetch-device-model-firmware.md) - Get model and firmware version
- [Task 051: Fetch Device Capacity](tasks/task-051-fetch-device-capacity.md) - Get max_users using CMD_GET_FREE_SIZES
- [Task 052: Fetch Device Time](tasks/task-052-fetch-device-time.md) - Get device time using CMD_GET_TIME
- [Task 053: Auto-populate Device Info](tasks/task-053-auto-populate-device-info.md) - Auto-fetch info during registration
- [Task 054: Device Info Refresh Endpoint](tasks/task-054-device-info-refresh-endpoint.md) - Refresh all device info
- [Task 055: Real Device Connection Testing](tasks/task-055-real-device-connection-testing.md) - Enhanced connection testing with real protocol

## Next Phase

**Phase 4: Device Monitoring** - Real-time status monitoring with real device communication.

