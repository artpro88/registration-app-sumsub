const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

// Register a new user
router.post('/register', userController.registerUser);

// Get user by ID
router.get('/:id', userController.getUserById);

// Update user verification status (internal use)
router.put('/verification-status', userController.updateVerificationStatus);

module.exports = router;
