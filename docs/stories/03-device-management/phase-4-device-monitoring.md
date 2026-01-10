# Phase 4: Device Monitoring

## Goal

Implement real-time device status monitoring with health checks, last-seen tracking, and real device communication status updates.

## Duration Estimate

3-4 days

## Prerequisites

- ✅ Phase 3 complete (real device integration working)
- ✅ Real device communication established

## Technical Components

### Backend Changes

- [ ] Implement device health checks using real device communication
- [ ] Add WebSocket events for status updates
- [ ] Add last_seen timestamp updates based on real device responses
- [ ] Implement real device capacity tracking (from device)
- [ ] Add periodic health check background task
- [ ] Update device status based on real communication results

### Frontend Changes

- [ ] Add WebSocket connection for status updates
- [ ] Update status indicators in real-time
- [ ] Show last-seen timestamps from real device
- [ ] Show real device capacity information
- [ ] Display device health status

## Visual Checkpoints

- [ ] Status updates in real-time from real devices
- [ ] Last-seen timestamps update based on device communication
- [ ] Real device capacity displays (from device)
- [ ] Health checks run automatically using real device protocol
- [ ] Device status accurately reflects real device connectivity

## Next Phase

**Phase 5: Simulation Mode** - Add demo mode without physical devices (optional, for later).