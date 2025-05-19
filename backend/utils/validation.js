const Joi = require('joi');

// Validate user registration data
exports.validateRegistration = (data) => {
  const schema = Joi.object({
    firstName: Joi.string().trim().required().messages({
      'string.empty': 'First name is required',
      'any.required': 'First name is required'
    }),
    
    lastName: Joi.string().trim().required().messages({
      'string.empty': 'Last name is required',
      'any.required': 'Last name is required'
    }),
    
    dob: Joi.date().required().max(getEighteenYearsAgo()).messages({
      'date.base': 'Date of birth must be a valid date',
      'date.max': 'You must be at least 18 years old',
      'any.required': 'Date of birth is required'
    }),
    
    street: Joi.string().trim().required().messages({
      'string.empty': 'Street address is required',
      'any.required': 'Street address is required'
    }),
    
    city: Joi.string().trim().required().messages({
      'string.empty': 'City is required',
      'any.required': 'City is required'
    }),
    
    postcode: Joi.string().trim().required().messages({
      'string.empty': 'Postcode is required',
      'any.required': 'Postcode is required'
    }),
    
    phoneNumber: Joi.string().trim().required().pattern(/^\+?[0-9\s\-()]{8,20}$/).messages({
      'string.empty': 'Phone number is required',
      'string.pattern.base': 'Please enter a valid phone number',
      'any.required': 'Phone number is required'
    }),
    
    email: Joi.string().trim().required().email().messages({
      'string.empty': 'Email is required',
      'string.email': 'Please enter a valid email address',
      'any.required': 'Email is required'
    }),
    
    password: Joi.string().min(8).messages({
      'string.min': 'Password must be at least 8 characters long'
    })
  });
  
  return schema.validate(data);
};

// Helper function to get date 18 years ago
function getEighteenYearsAgo() {
  const today = new Date();
  return new Date(
    today.getFullYear() - 18,
    today.getMonth(),
    today.getDate()
  );
}
