# Visual Testing Guide

## Overview

This guide explains how to visually test each phase and story to ensure the system works correctly and looks good.

## Principles

1. **Visual-First**: What you see is what matters
2. **User Perspective**: Test from user's point of view
3. **Realistic Data**: Use realistic demo data
4. **Multiple Scenarios**: Test happy path and error cases

## Testing Tools

### Browser DevTools
- **Elements Tab**: Inspect HTML and CSS
- **Network Tab**: Monitor API calls and WebSocket connections
- **Console Tab**: Check for JavaScript errors
- **Responsive Mode**: Test different screen sizes

### Screenshot Tools
- Browser built-in (Chrome DevTools)
- Snipping Tool (Windows)
- Screenshot extensions

### Video Recording
- Browser DevTools (Chrome: More tools > Recorder)
- OBS Studio (for full screen recording)
- Loom (for quick screen recordings)

## Testing Each Phase

### 1. Page Load
- ✅ Page loads without errors
- ✅ No console errors
- ✅ Loading states appear correctly
- ✅ Content displays as expected

### 2. Form Testing
- ✅ All fields are visible
- ✅ Labels are clear
- ✅ Placeholders are helpful
- ✅ Required fields are marked
- ✅ Validation errors appear correctly
- ✅ Form submission works

### 3. Data Display
- ✅ Data displays correctly
- ✅ Formatting is correct (dates, numbers)
- ✅ Empty states are clear
- ✅ Loading states are shown
- ✅ Error states are helpful

### 4. Interactions
- ✅ Buttons work correctly
- ✅ Links navigate properly
- ✅ Dropdowns open/close
- ✅ Modals appear/disappear
- ✅ Animations are smooth

### 5. Responsive Design
- ✅ Desktop (1920px, 1366px)
- ✅ Tablet (1024px, 768px)
- ✅ Mobile (375px, 414px)
- ✅ Text is readable
- ✅ Buttons are clickable
- ✅ Layout doesn't break

## Testing Real-time Features

### WebSocket Testing
1. Open DevTools Network tab
2. Filter by WS (WebSocket)
3. Verify connection established
4. Monitor messages being sent/received
5. Verify messages match expected format

### Real-time Updates
1. Trigger event (e.g., enrollment, attendance)
2. Watch for UI update
3. Verify update happens quickly (< 1 second)
4. Verify update is accurate
5. Check console for errors

## Testing Error Scenarios

### Network Errors
1. Disconnect network
2. Trigger action
3. Verify error message appears
4. Verify error is helpful
5. Reconnect and retry

### Validation Errors
1. Submit form with invalid data
2. Verify error messages appear
3. Verify errors are specific
4. Fix errors and resubmit
5. Verify form accepts valid data

### Server Errors
1. Simulate server error (if possible)
2. Verify error message appears
3. Verify error doesn't expose sensitive info
4. Verify retry option available

## Screenshot Guidelines

### What to Capture
- **Success States**: After successful operations
- **Error States**: When errors occur
- **Loading States**: During async operations
- **Empty States**: When no data exists
- **Form States**: Before and after submission

### Screenshot Format
- Full page screenshots
- Include browser chrome (optional)
- Use consistent browser size
- Name files descriptively: `enrollment-success.png`

## Video Recording Guidelines

### When to Record
- **Complete User Flows**: End-to-end processes
- **Real-time Features**: Enrollment progress, attendance updates
- **Complex Interactions**: Multi-step processes

### Recording Setup
- Use 1920x1080 resolution
- Clear browser history/cache
- Use realistic demo data
- Speak clearly if narrating
- Keep recordings focused (2-5 minutes)

## Testing Checklist

### For Each Phase

- [ ] All pages load without errors
- [ ] All forms work correctly
- [ ] All buttons/links work
- [ ] Data displays correctly
- [ ] Error states are helpful
- [ ] Loading states appear
- [ ] Responsive design works
- [ ] Real-time updates work (if applicable)
- [ ] Screenshots captured
- [ ] Video recorded (if needed)

## Common Issues

### Layout Breaking
- Check CSS for fixed widths
- Test with different content lengths
- Verify responsive breakpoints

### Performance Issues
- Check Network tab for slow requests
- Verify images are optimized
- Check for unnecessary re-renders

### Real-time Not Working
- Check WebSocket connection
- Verify event names match
- Check browser console for errors

---

**Remember**: Visual testing ensures the system not only works, but works well. Take time to test thoroughly!

