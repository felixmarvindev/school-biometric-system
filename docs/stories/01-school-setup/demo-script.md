# Story 01: School Setup - Demo Script

## Demo Overview

**Duration**: 5-7 minutes  
**Audience**: School administrators, stakeholders, investors  
**Goal**: Show how schools register and get started with the system

## Pre-Demo Setup

### Data Preparation
- Clear any existing test data (optional, for clean demo)
- Have sample school data ready:
  - School Name: "Greenfield Academy"
  - School Code: "GFA-001"
  - Address: "Nairobi, Kenya"
  - Phone: "+254 712 345 678"
  - Email: "admin@greenfield.ac.ke"
  - Admin Name: "John Doe"
  - Admin Email: "john.doe@greenfield.ac.ke"
  - Password: "SecurePass123!"

### Browser Setup
- Open browser in incognito/private mode (for clean session)
- Navigate to registration page
- Have browser DevTools ready (optional, for showing network requests)

## Demo Script

### Introduction (30 seconds)

**Script**:
> "Today I'll show you how a school gets started with our biometric attendance system. The process is simple: register the school, create an admin account, and you're ready to go. Let me walk you through it."

**Action**: Navigate to registration page

---

### Part 1: School Registration (1.5 minutes)

#### Show Registration Form (30 seconds)

**Script**:
> "This is our school registration form. Schools provide their basic information here. Notice the school code - this is a unique identifier for each school, like a registration number."

**Actions**:
- Point out each field
- Explain school code uniqueness
- Show form layout

**Highlights**:
- Clean, professional design
- Clear field labels
- Required field indicators

#### Fill and Submit Form (1 minute)

**Script**:
> "Let me register a sample school. I'll enter Greenfield Academy with code GFA-001. Notice how the form validates as I type - the email format, phone number format. Once I've filled everything, I click Register."

**Actions**:
1. Start filling form slowly
2. Show email validation (type invalid email, show error)
3. Fill all fields with sample data
4. Click "Register"
5. Show loading state
6. Show success message

**Highlights**:
- Real-time validation
- Loading feedback
- Success confirmation

**Key Talking Point**:
> "Registration completes in under 2 seconds. The school is now in our system."

---

### Part 2: Admin Account Creation (1.5 minutes)

#### Show Admin Form (30 seconds)

**Script**:
> "After school registration, we create the admin account. This is the account that will manage the school's data. Notice the password strength indicator - we want strong passwords for security."

**Actions**:
- Show admin account form
- Point out password requirements
- Show password strength indicator

**Highlights**:
- Password requirements visible
- Strength indicator
- Security-focused design

#### Create Admin Account (1 minute)

**Script**:
> "I'll create an admin account for John Doe. As I type the password, watch the strength indicator update. When passwords match, the form is ready. Let me submit."

**Actions**:
1. Fill name and email
2. Type password slowly, show strength indicator
3. Type password confirmation
4. Show password match validation
5. Click "Create Account"
6. Show success message

**Highlights**:
- Password strength feedback
- Password matching validation
- Secure account creation

**Key Talking Point**:
> "Passwords are securely hashed before storage - we never see or store plain text passwords."

---

### Part 3: First Login (1 minute)

#### Login Process (30 seconds)

**Script**:
> "Now the admin can log in. I'll use the credentials we just created."

**Actions**:
1. Navigate to login page (or show redirect)
2. Enter email and password
3. Click "Login"
4. Show loading
5. Show redirect to dashboard

**Highlights**:
- Simple login process
- Secure authentication
- Automatic redirect

#### Dashboard Overview (30 seconds)

**Script**:
> "This is the school dashboard. Admins see their school information prominently, and they have access to all features through the navigation menu. Notice the quick stats - these will populate as they add students and devices."

**Actions**:
- Show dashboard layout
- Point out school information card
- Show navigation menu
- Point out empty state stats

**Highlights**:
- Personalized dashboard
- Clear navigation
- Empty states guide next steps

**Key Talking Point**:
> "Everything is ready. The admin can now start adding students or registering devices."

---

### Part 4: Settings (Optional - 1 minute)

#### Show Settings (30 seconds)

**Script**:
> "Admins can also update their school information at any time. Let me show you the settings page."

**Actions**:
1. Click "Settings" in navigation
2. Show settings form pre-populated
3. Point out read-only school code

**Highlights**:
- Easy access to settings
- Pre-populated form
- School code protection

#### Update Information (30 seconds)

**Script**:
> "I can update the phone number, for example. Notice the school code is read-only - we keep that stable for system integrity. Let me save the changes."

**Actions**:
1. Change phone number
2. Click "Save Changes"
3. Show success message
4. Navigate back to dashboard
5. Show updated information

**Highlights**:
- Simple update process
- Immediate feedback
- Data persists

---

### Closing (30 seconds)

**Script**:
> "That's the complete school setup process. In just a few minutes, a school can register, create their admin account, and be ready to use the system. The foundation is set for adding students, devices, and managing attendance. Questions?"

**Actions**:
- Return to dashboard
- Summarize what was shown
- Be ready for questions

---

## Expected Questions & Answers

### Q: How long does registration take?
**A**: The entire process takes about 2-3 minutes. Most of that is the admin filling out forms. The actual system processing is under 2 seconds.

### Q: Can a school have multiple admins?
**A**: Currently, each school has one primary admin. Multi-admin support is planned for a future release. For now, the admin can share credentials if needed, though we'd recommend waiting for proper multi-user support.

### Q: What if someone forgets their password?
**A**: Password reset functionality will be added in a future phase. For now, we'd recommend keeping credentials secure. In production, password reset will be available.

### Q: Can schools change their school code?
**A**: No, the school code is designed to be permanent for system integrity and data consistency. Schools can update all other information through settings.

### Q: Is the data secure?
**A**: Yes, we use industry-standard security practices:
- Passwords are hashed with bcrypt
- All communication is over HTTPS
- Each school's data is isolated
- JWT tokens for secure authentication

### Q: What happens if two schools want the same code?
**A**: The system validates uniqueness and prevents duplicate codes. If a code is already taken, the admin will see a clear error message and can choose a different code.

### Q: Can schools customize the dashboard?
**A**: Not in this initial version, but that's a great feature idea for future phases. The dashboard will evolve based on user feedback.

---

## Demo Tips

### Do's
✅ **Practice the flow** - Run through it once before the demo  
✅ **Have data ready** - Write down sample data before starting  
✅ **Explain as you go** - Don't just click, explain what's happening  
✅ **Show errors** - Demonstrate validation by making mistakes  
✅ **Be enthusiastic** - Show excitement about the system  

### Don'ts
❌ **Don't rush** - Take time to explain each step  
❌ **Don't skip validation** - Show that the system catches errors  
❌ **Don't ignore empty states** - Explain what will appear there  
❌ **Don't forget to pause** - Give audience time to process  

---

## Troubleshooting

### If registration fails:
- Check browser console for errors
- Verify backend services are running
- Check database connection
- Show error message and explain it's handled gracefully

### If login doesn't work:
- Verify user was created in database
- Check JWT configuration
- Verify password was hashed correctly
- Show helpful error message

### If dashboard doesn't load:
- Check API endpoint is working
- Verify authentication token
- Check network tab for errors
- Show loading state (it's part of the UX)

---

## Post-Demo Notes

After the demo, note:
- Questions asked (for future FAQ)
- Features requested (for backlog)
- Confusion points (for UX improvements)
- Positive feedback (for marketing)

---

**Remember**: The goal is to show that getting started is simple, fast, and secure. Emphasize the user experience and ease of use!

