# Registration App with Sumsub Identity Verification

This is the frontend for the Registration App with Sumsub Identity Verification. It provides a user-friendly interface for registering and verifying your identity using Sumsub's identity verification service.

## How to Use

1. Fill out the registration form with your personal information:
   - First Name and Last Name
   - Date of Birth (must be 18+ years old)
   - Phone Number (preferably in international format, e.g., +44...)
   - Email Address
   - Address details (Street, City, Postcode)
   - Accept the GDPR consent checkbox
2. Submit the form to create your account
3. Complete the Sumsub verification process:
   - Upload a valid ID document
   - Take a selfie or complete a liveness check
   - Follow any additional instructions provided by Sumsub
4. Check your verification status

## Technologies Used

- HTML, CSS, and JavaScript
- Bootstrap for responsive design
- Sumsub WebSDK for identity verification

## Backend API

The frontend communicates with a backend API for user registration and verification. The API is hosted at:

- Development: http://localhost:8080/api
- Production: https://api.registration-app.yourdomain.com/api

## Sumsub Integration

This demo uses the Sumsub Web SDK for identity verification. The integration flow is as follows:

1. User submits registration form
2. Frontend initializes Sumsub Web SDK with the access token
3. User completes the verification process in the SDK
4. Verification status is displayed to the user

## Security Considerations

In a production environment:

- Never expose Sumsub credentials in client-side code
- Always generate access tokens on the backend
- Implement proper authentication and authorization
- Encrypt sensitive user data
- Use HTTPS for all communications
- Implement proper error handling and logging

## Contact

For support or inquiries, please contact us at support@yourdomain.com.
