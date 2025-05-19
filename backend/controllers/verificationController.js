const User = require('../models/User');
const sumsubService = require('../services/sumsubService');

// Generate Sumsub access token
exports.generateAccessToken = async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Check if user exists
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    // Generate access token using Sumsub service
    const accessToken = await sumsubService.generateAccessToken(user);
    
    res.status(200).json({
      success: true,
      token: accessToken
    });
  } catch (error) {
    console.error('Generate access token error:', error);
    res.status(500).json({
      success: false,
      message: 'An error occurred while generating access token',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
};

// Get verification status
exports.getVerificationStatus = async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Check if user exists
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    // Get verification status from Sumsub
    const verificationStatus = await sumsubService.getApplicantStatus(user.verificationDetails.applicantId);
    
    // Update user's verification status in database if it has changed
    if (verificationStatus !== user.verificationStatus) {
      user.verificationStatus = verificationStatus;
      user.verificationDetails.lastChecked = new Date();
      await user.save();
    }
    
    res.status(200).json({
      success: true,
      status: user.verificationStatus,
      lastChecked: user.verificationDetails.lastChecked,
      rejectionReason: user.verificationStatus === 'rejected' ? user.verificationDetails.rejectionReason : null
    });
  } catch (error) {
    console.error('Get verification status error:', error);
    res.status(500).json({
      success: false,
      message: 'An error occurred while getting verification status',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
};

// Webhook handler for Sumsub status updates
exports.webhookHandler = async (req, res) => {
  try {
    // Verify webhook signature (in a real app)
    // const isValid = sumsubService.verifyWebhookSignature(req);
    // if (!isValid) {
    //   return res.status(401).json({
    //     success: false,
    //     message: 'Invalid webhook signature'
    //   });
    // }
    
    const { applicantId, reviewStatus, reviewResult } = req.body;
    
    // Find user by applicantId
    const user = await User.findOne({ 'verificationDetails.applicantId': applicantId });
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found for this applicant'
      });
    }
    
    // Map Sumsub status to our status
    let verificationStatus = 'pending';
    if (reviewStatus === 'completed') {
      verificationStatus = reviewResult.reviewAnswer === 'GREEN' ? 'verified' : 'rejected';
    }
    
    // Update user verification status
    user.verificationStatus = verificationStatus;
    user.verificationDetails.lastChecked = new Date();
    
    // If rejected, store rejection reason
    if (verificationStatus === 'rejected' && reviewResult.moderationComment) {
      user.verificationDetails.rejectionReason = reviewResult.moderationComment;
    }
    
    await user.save();
    
    // Acknowledge webhook receipt
    res.status(200).json({
      success: true,
      message: 'Webhook processed successfully'
    });
  } catch (error) {
    console.error('Webhook handler error:', error);
    res.status(500).json({
      success: false,
      message: 'An error occurred while processing webhook',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
};
