const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const UserSchema = new mongoose.Schema({
  firstName: {
    type: String,
    required: [true, 'First name is required'],
    trim: true
  },
  lastName: {
    type: String,
    required: [true, 'Last name is required'],
    trim: true
  },
  dob: {
    type: Date,
    required: [true, 'Date of birth is required'],
    validate: {
      validator: function(dob) {
        // Check if user is at least 18 years old
        const today = new Date();
        const eighteenYearsAgo = new Date(
          today.getFullYear() - 18,
          today.getMonth(),
          today.getDate()
        );
        return dob <= eighteenYearsAgo;
      },
      message: 'You must be at least 18 years old'
    }
  },
  address: {
    street: {
      type: String,
      required: [true, 'Street address is required'],
      trim: true
    },
    city: {
      type: String,
      required: [true, 'City is required'],
      trim: true
    },
    postcode: {
      type: String,
      required: [true, 'Postcode is required'],
      trim: true
    }
  },
  phoneNumber: {
    type: String,
    required: [true, 'Phone number is required'],
    trim: true,
    match: [/^\+?[0-9\s\-()]{8,20}$/, 'Please enter a valid phone number']
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    trim: true,
    lowercase: true,
    match: [/^\S+@\S+\.\S+$/, 'Please enter a valid email address']
  },
  password: {
    type: String,
    minlength: [8, 'Password must be at least 8 characters long'],
    select: false // Don't include password in query results by default
  },
  verificationStatus: {
    type: String,
    enum: ['pending', 'verified', 'rejected'],
    default: 'pending'
  },
  verificationDetails: {
    applicantId: String,
    rejectionReason: String,
    lastChecked: Date
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update the updatedAt field before saving
UserSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Hash password before saving
UserSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to compare passwords
UserSchema.methods.comparePassword = async function(candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.password);
};

// Method to get user's full name
UserSchema.methods.getFullName = function() {
  return `${this.firstName} ${this.lastName}`;
};

// Method to check if user is verified
UserSchema.methods.isVerified = function() {
  return this.verificationStatus === 'verified';
};

const User = mongoose.model('User', UserSchema);

module.exports = User;
