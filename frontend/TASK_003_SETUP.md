# Task 003: School Registration Form - Setup Checklist

## ✅ Placeholder Files Created

The following placeholder files have been created and are ready for implementation:

1. ✅ `lib/validations/school.ts` - Zod validation schema (complete)
2. ✅ `lib/api/schools.ts` - API client functions (needs implementation)
3. ✅ `components/features/school/SchoolRegistrationForm.tsx` - Form component (placeholder, needs v0.dev generation)
4. ✅ `app/(auth)/register/page.tsx` - Registration page (placeholder, needs integration)

## 📋 Next Steps

### Step 1: Install Required shadcn/ui Components

Run these commands to install the required UI components:

```bash
cd frontend
npx shadcn@latest add card
npx shadcn@latest add form
npx shadcn@latest add input
npx shadcn@latest add textarea
npx shadcn@latest add label
npx shadcn@latest add alert
npx shadcn@latest add separator
```

### Step 2: Generate Form Component with v0.dev

1. Use the v0 prompt provided to generate the `SchoolRegistrationForm` component
2. Replace the placeholder in `components/features/school/SchoolRegistrationForm.tsx`
3. Ensure the component:
   - Uses the validation schema from `lib/validations/school.ts`
   - Accepts the props defined in the interface
   - Uses shadcn/ui components for styling
   - Is fully accessible and responsive

### Step 3: Implement API Client

1. Open `lib/api/schools.ts`
2. Uncomment and implement the `registerSchool` function
3. Handle error responses:
   - **422**: Validation errors - map to form fields
   - **409**: Duplicate code - show specific error message
   - **500**: Server error - show generic error message

### Step 4: Integrate Form in Page

1. Open `app/(auth)/register/page.tsx`
2. Uncomment the API call in `handleSubmit`
3. Implement success handling:
   - Show success message
   - Optionally redirect to login page
   - Reset form state
4. Implement error handling:
   - Map 422 errors to form fields
   - Show 409 errors in error state
   - Show 500 errors in error state

### Step 5: Test the Form

1. Start the backend services:
   ```bash
   # Terminal 1: API Gateway
   cd backend/api_gateway
   uvicorn main:app --reload --port 8000
   
   # Terminal 2: School Service
   cd backend/school_service
   uvicorn main:app --reload --port 8001
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to `http://localhost:3000/register`
4. Test form validation
5. Test form submission
6. Test error handling
7. Test success flow

## 📝 File Structure

```
frontend/
├── app/
│   └── (auth)/
│       └── register/
│           └── page.tsx          ✅ Created (needs integration)
├── components/
│   ├── features/
│   │   └── school/
│   │       └── SchoolRegistrationForm.tsx  ✅ Created (needs v0.dev generation)
│   └── ui/                       ⚠️  Needs: card, form, input, textarea, label
└── lib/
    ├── api/
    │   └── schools.ts            ✅ Created (needs implementation)
    └── validations/
        └── school.ts             ✅ Complete
```

## 🔗 API Endpoint

- **URL**: `POST http://localhost:8000/api/v1/schools/register`
- **Request Body**: Matches `SchoolRegistrationFormData` type
- **Success Response**: `SchoolResponse` type (201 status)
- **Error Responses**: 
  - 422: Validation errors
  - 409: Duplicate code
  - 500: Server error

## ✨ Acceptance Criteria Checklist

- [ ] Registration page route exists at `/register`
- [ ] `SchoolRegistrationForm` component created
- [ ] Form includes all required fields (name, code, address, phone, email)
- [ ] Client-side validation works for all fields
- [ ] Form submission calls registration API
- [ ] Loading state shown during submission
- [ ] Success message displayed on successful registration
- [ ] Error messages displayed for validation failures
- [ ] Form is responsive (desktop, tablet, mobile)
- [ ] Form is accessible (keyboard navigation, screen readers)

## 🎨 Design Notes

- Use shadcn/ui New York style
- Neutral color scheme
- Card-based layout
- Proper spacing and typography
- Mobile-first responsive design
- Accessible focus states and ARIA labels

