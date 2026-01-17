# Task 071: WebSocket Client Integration

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 3: Real-time Progress

## Description

Create WebSocket client hook and integrate it with the enrollment progress component to receive real-time updates.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
1.5 days

## Prerequisites

- ✅ Task 070 complete (progress UI component)
- ✅ WebSocket server ready

## Acceptance Criteria

1. [ ] WebSocket hook created (`useEnrollmentProgress`)
2. [ ] Hook connects to enrollment WebSocket endpoint
3. [ ] Hook receives progress events
4. [ ] Hook handles completion events
5. [ ] Hook handles error events
6. [ ] Hook handles reconnection
7. [ ] Hook cleans up on unmount

## Implementation Details

### Frontend Changes

1. **frontend/lib/hooks/useEnrollmentProgress.ts**
   - Create enrollment progress WebSocket hook
   - Handle connection
   - Handle events
   - Handle cleanup

2. **frontend/lib/api/websocket.ts** (if needed)
   - Add enrollment WebSocket URL helper

### Key Code Patterns

```typescript
// frontend/lib/hooks/useEnrollmentProgress.ts
import { useEffect, useState, useRef } from 'react';
import { useAuthStore } from '@/lib/store/authStore';

export function useEnrollmentProgress(
  sessionId: string,
  options: {
    onComplete?: () => void;
    onError?: (error: string) => void;
  } = {}
) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('ready');
  const [message, setMessage] = useState('Ready to start enrollment...');
  const wsRef = useRef<WebSocket | null>(null);
  const { token } = useAuthStore();

  useEffect(() => {
    if (!token || !sessionId) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/enrollment?token=${token}&session_id=${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Enrollment WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'enrollment_progress') {
        setProgress(data.progress);
        setStatus(data.status);
        setMessage(data.message);
      } else if (data.type === 'enrollment_complete') {
        setProgress(100);
        setStatus('complete');
        setMessage('Enrollment complete!');
        options.onComplete?.();
      } else if (data.type === 'enrollment_error') {
        setStatus('error');
        setMessage(data.error || 'Enrollment failed');
        options.onError?.(data.error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      options.onError?.('Connection error');
    };

    ws.onclose = () => {
      console.log('Enrollment WebSocket closed');
    };

    wsRef.current = ws;

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [token, sessionId]);

  return { progress, status, message };
}
```

## Testing

### Manual Testing

1. **WebSocket Connection**
   - Start enrollment
   - ✅ Verify WebSocket connects
   - ✅ Verify progress events received
   - ✅ Verify completion event received

## Definition of Done

- [ ] WebSocket hook created
- [ ] Connection works
- [ ] Events received correctly
- [ ] Cleanup works
- [ ] Reconnection works

## Next Phase

**Phase 4: Template Storage** - Now that progress tracking works, we need to capture and store fingerprint templates when enrollment completes.
