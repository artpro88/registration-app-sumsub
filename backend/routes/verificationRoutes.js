const express = require('express');
const router = express.Router();
const verificationController = require('../controllers/verificationController');

// Generate Sumsub access token
router.get('/token/:userId', verificationController.generateAccessToken);

// Get verification status
router.get('/status/:userId', verificationController.getVerificationStatus);

// Webhook handler for Sumsub status updates
router.post('/webhook', verificationController.webhookHandler);

module.exports = router;
