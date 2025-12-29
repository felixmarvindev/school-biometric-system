# Phase 2: Device Control

## Goal

Implement backend device communication to send enrollment commands to ZKTeco devices and handle device responses. This enables actual enrollment functionality.

## Duration Estimate

5-7 days

## Prerequisites

- ✅ Phase 1 complete (enrollment UI ready)
- ✅ ZKTeco SDK available or simulation mode working
- ✅ Device service infrastructure ready

## Technical Components

### Backend Changes

- [ ] Create enrollment session model
- [ ] Create POST `/api/v1/enrollment/start` endpoint
- [ ] Implement device connection logic
- [ ] Implement CMD_STARTENROLL command
- [ ] Implement enrollment event registration (EF_ENROLLFINGER)
- [ ] Implement event polling mechanism
- [ ] Add enrollment cancellation endpoint
- [ ] Add error handling for device communication
- [ ] Add timeout handling
- [ ] Create unit tests for device communication
- [ ] Create integration tests

### Frontend Changes

- [ ] Connect enrollment form to API endpoint
- [ ] Add loading state during enrollment start
- [ ] Handle API errors gracefully
- [ ] Show error messages for device issues

### DevOps/Infrastructure

- [ ] Configure device connection timeouts
- [ ] Add environment variables for device settings

## Tasks Breakdown

See [tasks/](tasks/) folder:
- Task 015: Enrollment Session Model
- Task 016: Device Connection Service
- Task 017: Enrollment Command Handler
- Task 018: Enrollment API Endpoint
- Task 019: Error Handling

## Visual Checkpoints

At the end of this phase, you should be able to:

### 1. Start Enrollment
- Fill enrollment form
- Click "Start Enrollment"
- See loading indicator
- Enrollment session created in database
- API returns success with session ID

### 2. Device Communication
- Device receives enrollment command
- Device enters enrollment mode
- Enrollment session status is "in_progress"
- Connection is maintained

### 3. Error Handling
- If device offline: Clear error message
- If connection timeout: Error message with retry option
- If device busy: Error message
- All errors are logged

### Success Screenshots

1. **Enrollment Started** - Loading state after clicking "Start Enrollment"
2. **Success Response** - API returns session ID
3. **Error State** - Clear error message for device offline
4. **Database Record** - Enrollment session in database

## Testing This Phase

### Manual Testing Steps

1. **Start Enrollment (Happy Path)**
   - Fill enrollment form
   - Click "Start Enrollment"
   - ✅ Verify loading indicator appears
   - ✅ Verify API call succeeds
   - ✅ Verify enrollment session created
   - ✅ Verify device receives command (check logs)

2. **Device Offline**
   - Select an offline device
   - Start enrollment
   - ✅ Verify clear error message
   - ✅ Verify enrollment session not created (or marked as failed)
   - ✅ Verify error is logged

3. **Connection Timeout**
   - Start enrollment on device with network issues
   - Wait for timeout
   - ✅ Verify timeout error message
   - ✅ Verify retry option available

4. **Device Busy**
   - Start enrollment on device that's already in use
   - ✅ Verify "device busy" error message
   - ✅ Verify helpful guidance

### Automated Tests

- [ ] Unit tests for device connection
- [ ] Unit tests for enrollment command
- [ ] Unit tests for error handling
- [ ] Integration tests with mock device
- [ ] Integration tests with real device (optional)

## Demo Script for This Phase

### Demonstration (2 minutes)

1. **Show Enrollment Start** (30 seconds)
   - Fill enrollment form
   - Click "Start Enrollment"
   - Show loading state
   - Show success response

2. **Show Device Communication** (1 minute)
   - Explain what happens: Command sent to device
   - Show backend logs (if available)
   - Explain device enters enrollment mode
   - Show enrollment session in database

3. **Show Error Handling** (30 seconds)
   - Try with offline device
   - Show clear error message
   - Explain error is handled gracefully

### Talking Points

- "The system sends enrollment commands directly to devices"
- "Device communication is reliable and handles errors gracefully"
- "Enrollment sessions are tracked for monitoring"
- "All errors are logged for troubleshooting"

### Expected Questions

**Q: What happens if the device loses connection during enrollment?**  
A: The system detects connection loss and shows an error. Enrollment can be retried once the device is back online.

**Q: Can multiple enrollments happen at once?**  
A: Typically one enrollment per device at a time. We'll add queue management in a future enhancement.

**Q: How do we know the device received the command?**  
A: The device responds with an acknowledgment. If no response, we show an error.

## Next Phase

**Phase 3: Real-time Progress** - Now that we can start enrollment, we need to provide real-time progress updates to the frontend via WebSocket. This phase adds the WebSocket infrastructure and progress event emission.

