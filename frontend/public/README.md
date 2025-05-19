# Registration Page with Sumsub Identity Verification - Demo

This is a standalone demo of the registration page with Sumsub identity verification integration. This demo showcases the user interface and flow without requiring a backend server.

## How to Use This Demo

1. Open the `demo.html` file in a modern web browser
2. Fill out the registration form with valid information:
   - First Name and Last Name
   - Date of Birth (must be 18+ years old)
   - Phone Number (preferably in international format, e.g., +44...)
   - Email Address
   - Address details (Street, City, Postcode)
   - Accept the GDPR consent checkbox
3. Submit the form to proceed to the identity verification step
4. Complete the Sumsub verification process:
   - Upload a valid ID document
   - Take a selfie or complete a liveness check
   - Follow any additional instructions provided by Sumsub
5. View your verification status

## Important Notes

- This is a demo implementation using the Sumsub sandbox environment
- In a real application, the Sumsub credentials would be securely stored on the backend
- The access token would be generated on the backend and passed to the frontend
- User data would be stored in a database and associated with the verification process
- The verification status would be tracked and updated via webhooks

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

## Next Steps for a Full Implementation

To create a full implementation:

1. Set up a backend server with Node.js and Express
2. Implement a database to store user information
3. Create secure API endpoints for user registration and verification
4. Implement proper token generation and management
5. Set up webhook handling for verification status updates
6. Add authentication and authorization
7. Implement error handling and logging
8. Deploy to a production environment with HTTPS
