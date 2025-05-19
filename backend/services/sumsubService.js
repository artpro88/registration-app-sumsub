const axios = require('axios');
const crypto = require('crypto');

// Sumsub API configuration
const SUMSUB_APP_TOKEN = process.env.SUMSUB_APP_TOKEN || 'your-app-token';
const SUMSUB_SECRET_KEY = process.env.SUMSUB_SECRET_KEY || 'your-secret-key';
const SUMSUB_BASE_URL = 'https://api.sumsub.com';

// Create a timestamp for request
const getTimestamp = () => Math.floor(Date.now() / 1000);

// Generate signature for Sumsub API request
const generateSignature = (method, url, timestamp, body = '') => {
  const hmac = crypto.createHmac('sha256', SUMSUB_SECRET_KEY);
  hmac.update(timestamp + method + url + body);
  return hmac.digest('hex');
};

// Create headers for Sumsub API request
const createHeaders = (method, url, body = '') => {
  const timestamp = getTimestamp();
  const signature = generateSignature(method, url, timestamp, body);
  
  return {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-App-Token': SUMSUB_APP_TOKEN,
    'X-App-Access-Sig': signature,
    'X-App-Access-Ts': timestamp
  };
};

// Generate access token for Sumsub Web SDK
exports.generateAccessToken = async (user) => {
  try {
    // Check if user already has an applicant ID
    let applicantId = user.verificationDetails?.applicantId;
    
    // If not, create a new applicant
    if (!applicantId) {
      applicantId = await createApplicant(user);
      
      // Update user with applicant ID
      user.verificationDetails = {
        ...user.verificationDetails,
        applicantId
      };
      await user.save();
    }
    
    // Generate access token
    const method = 'POST';
    const url = `/resources/accessTokens?userId=${applicantId}&ttlInSecs=3600`;
    
    const headers = createHeaders(method, url);
    
    const response = await axios({
      method,
      url: SUMSUB_BASE_URL + url,
      headers
    });
    
    return response.data.token;
  } catch (error) {
    console.error('Error generating access token:', error);
    throw new Error('Failed to generate access token');
  }
};

// Create a new applicant in Sumsub
const createApplicant = async (user) => {
  try {
    const method = 'POST';
    const url = '/resources/applicants';
    
    const body = JSON.stringify({
      externalUserId: user._id.toString(),
      email: user.email,
      phone: user.phoneNumber,
      firstName: user.firstName,
      lastName: user.lastName,
      dob: user.dob.toISOString().split('T')[0], // Format as YYYY-MM-DD
      country: 'GBR', // Default to UK, adjust as needed
      requiredIdDocs: {
        docSets: [
          {
            idDocSetType: 'IDENTITY',
            types: ['PASSPORT', 'ID_CARD', 'DRIVERS']
          },
          {
            idDocSetType: 'SELFIE',
            types: ['SELFIE']
          }
        ]
      }
    });
    
    const headers = createHeaders(method, url, body);
    
    const response = await axios({
      method,
      url: SUMSUB_BASE_URL + url,
      headers,
      data: body
    });
    
    return response.data.id;
  } catch (error) {
    console.error('Error creating applicant:', error);
    throw new Error('Failed to create applicant');
  }
};

// Get applicant status from Sumsub
exports.getApplicantStatus = async (applicantId) => {
  try {
    const method = 'GET';
    const url = `/resources/applicants/${applicantId}/status`;
    
    const headers = createHeaders(method, url);
    
    const response = await axios({
      method,
      url: SUMSUB_BASE_URL + url,
      headers
    });
    
    // Map Sumsub status to our status
    const reviewStatus = response.data.reviewStatus;
    const reviewResult = response.data.reviewResult;
    
    if (reviewStatus === 'completed') {
      return reviewResult.reviewAnswer === 'GREEN' ? 'verified' : 'rejected';
    }
    
    return 'pending';
  } catch (error) {
    console.error('Error getting applicant status:', error);
    throw new Error('Failed to get applicant status');
  }
};

// Verify webhook signature from Sumsub
exports.verifyWebhookSignature = (req) => {
  try {
    const signature = req.headers['x-payload-digest'];
    if (!signature) return false;
    
    const hmac = crypto.createHmac('sha1', SUMSUB_SECRET_KEY);
    hmac.update(JSON.stringify(req.body));
    const calculatedSignature = hmac.digest('hex');
    
    return signature === calculatedSignature;
  } catch (error) {
    console.error('Error verifying webhook signature:', error);
    return false;
  }
};
