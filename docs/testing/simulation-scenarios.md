# Simulation Scenarios

## Overview

Test scenarios for simulation mode - testing without physical devices.

## Simulation Mode Setup

### Enable Simulation
```bash
# In backend/.env
SIMULATION_MODE=true
```

### Configuration
```python
SIMULATION_SUCCESS_RATE=0.95  # 95% success rate
SIMULATION_DELAY_MIN=1.0      # Minimum delay (seconds)
SIMULATION_DELAY_MAX=3.0      # Maximum delay (seconds)
```

## Test Scenarios

### Scenario 1: Successful Enrollment

**Steps**:
1. Select student
2. Select device (simulated)
3. Start enrollment
4. Progress updates: 0% → 33% → 66% → 100%
5. Success message appears
6. Enrollment record created

**Expected**:
- ✅ Progress updates smoothly
- ✅ Success message appears
- ✅ Enrollment record in database
- ✅ Template stored (simulated)

---

### Scenario 2: Enrollment Timeout

**Steps**:
1. Configure simulation to timeout
2. Start enrollment
3. Wait for timeout
4. Error message appears

**Expected**:
- ✅ Timeout error appears
- ✅ Clear error message
- ✅ Retry option available
- ✅ Enrollment session marked as failed

---

### Scenario 3: Poor Fingerprint Quality

**Steps**:
1. Configure simulation to reject poor quality
2. Start enrollment
3. Progress reaches 66%
4. Quality error appears

**Expected**:
- ✅ Quality error message
- ✅ Guidance to retry
- ✅ Retry option available

---

### Scenario 4: Device Offline

**Steps**:
1. Mark device as offline in simulation
2. Try to start enrollment
3. Error message appears

**Expected**:
- ✅ Device offline error
- ✅ Clear error message
- ✅ Cannot start enrollment

---

### Scenario 5: Real-time Attendance

**Steps**:
1. Enable simulation mode
2. Simulate attendance event
3. Event appears in dashboard

**Expected**:
- ✅ Event appears instantly
- ✅ Student matched correctly
- ✅ IN/OUT determined correctly
- ✅ WebSocket event received

---

### Scenario 6: Bulk Enrollment

**Steps**:
1. Select 5 students
2. Start bulk enrollment
3. Progress tracked for each
4. Summary appears

**Expected**:
- ✅ Each enrollment processes
- ✅ Progress tracked individually
- ✅ Summary shows results
- ✅ Failed enrollments identified

---

## Simulation Configuration

### Success Rates
- **High Success**: 95% success rate (realistic)
- **Medium Success**: 80% success rate (some failures)
- **Low Success**: 50% success rate (many failures, for testing)

### Delays
- **Fast**: 1-2 seconds (quick demo)
- **Realistic**: 2-4 seconds (normal speed)
- **Slow**: 4-8 seconds (testing patience)

### Error Types
- **Timeout**: Connection timeout
- **Quality**: Poor fingerprint quality
- **Device Busy**: Device in use
- **Network Error**: Network failure

---

## Testing Checklist

- [ ] Successful enrollment works
- [ ] Timeout error handled
- [ ] Quality error handled
- [ ] Device offline handled
- [ ] Real-time updates work
- [ ] Bulk enrollment works
- [ ] Error messages are clear
- [ ] Retry logic works

---

**Simulation mode enables full testing and demos without hardware!**

