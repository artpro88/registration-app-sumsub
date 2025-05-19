const User = require('../models/User');
const { validateRegistration } = require('../utils/validation');

// Register a new user
exports.registerUser = async (req, res) => {
  try {
    // Validate request body
    const { error } = validateRegistration(req.body);
    if (error) {
      return res.status(400).json({
        success: false,
        message: error.details[0].message
      });
    }

    // Check if email already exists
    const existingUser = await User.findOne({ email: req.body.email });
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'Email is already registered'
      });
    }

    // Create new user
    const user = new User({
      firstName: req.body.firstName,
      lastName: req.body.lastName,
      dob: new Date(req.body.dob),
      address: {
        street: req.body.street,
        city: req.body.city,
        postcode: req.body.postcode
      },
      phoneNumber: req.body.phoneNumber,
      email: req.body.email,
      // In a real app, you would also handle password here
    });

    // Save user to database
    await user.save();

    // Return success response
    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: {
        userId: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        verificationStatus: user.verificationStatus
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      success: false,
      message: 'An error occurred during registration',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
};

// Get user by ID
exports.getUserById = async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: {
        userId: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        phoneNumber: user.phoneNumber,
        address: user.address,
        verificationStatus: user.verificationStatus,
        createdAt: user.createdAt
      }
    });
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({
      success: false,
      message: 'An error occurred while retrieving user',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
};

// Update user verification status
exports.updateVerificationStatus = async (req, res) => {
  try {
    const { userId, status, rejectionReason } = req.body;
    
    if (!['pending', 'verified', 'rejected'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid verification status'
      });
    }
    
    const updateData = {
      verificationStatus: status,
      'verificationDetails.lastChecked': new Date()
    };
    
    if (status === 'rejected' && rejectionReason) {
      updateData['verificationDetails.rejectionReason'] = rejectionReason;
    }
    
    const user = await User.findByIdAndUpdate(
      userId,
      { $set: updateData },
      { new: true }
    );
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    res.status(200).json({
      success: true,
      message: `User verification status updated to ${status}`,
      data: {
        userId: user._id,
        verificationStatus: user.verificationStatus
      }
    });
  } catch (error) {
    console.error('Update verification status error:', error);
    res.status(500).json({
      success: false,
      message: 'An error occurred while updating verification status',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
};
