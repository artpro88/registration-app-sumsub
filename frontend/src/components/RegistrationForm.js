import React, { useState } from 'react';
import AddressFields from './AddressFields';

const RegistrationForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    dob: '',
    street: '',
    city: '',
    postcode: '',
    phoneNumber: '',
    email: '',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  // Validate form data
  const validateForm = () => {
    const newErrors = {};
    
    // First Name validation
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }
    
    // Last Name validation
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }
    
    // Date of Birth validation
    if (!formData.dob) {
      newErrors.dob = 'Date of birth is required';
    } else {
      // Check if user is at least 18 years old
      const dobDate = new Date(formData.dob);
      const today = new Date();
      const eighteenYearsAgo = new Date(
        today.getFullYear() - 18,
        today.getMonth(),
        today.getDate()
      );
      
      if (dobDate > eighteenYearsAgo) {
        newErrors.dob = 'You must be at least 18 years old';
      }
    }
    
    // Address validation
    if (!formData.street.trim()) {
      newErrors.street = 'Street address is required';
    }
    
    if (!formData.city.trim()) {
      newErrors.city = 'City is required';
    }
    
    if (!formData.postcode.trim()) {
      newErrors.postcode = 'Postcode is required';
    }
    
    // Phone Number validation
    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (!/^\+?[0-9\s\-()]{8,20}$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = 'Please enter a valid phone number (preferably in international format)';
    }
    
    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      setIsSubmitting(true);
      try {
        await onSubmit(formData);
      } catch (error) {
        console.error('Form submission error:', error);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="row mb-4">
        <div className="col-12">
          <h3 className="mb-4">Personal Information</h3>
        </div>
        
        {/* First Name */}
        <div className="col-md-6 mb-3">
          <label htmlFor="firstName" className="form-label">First Name</label>
          <input
            type="text"
            className={`form-control ${errors.firstName ? 'is-invalid' : ''}`}
            id="firstName"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            required
          />
          {errors.firstName && <div className="invalid-feedback">{errors.firstName}</div>}
        </div>
        
        {/* Last Name */}
        <div className="col-md-6 mb-3">
          <label htmlFor="lastName" className="form-label">Last Name</label>
          <input
            type="text"
            className={`form-control ${errors.lastName ? 'is-invalid' : ''}`}
            id="lastName"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            required
          />
          {errors.lastName && <div className="invalid-feedback">{errors.lastName}</div>}
        </div>
        
        {/* Date of Birth */}
        <div className="col-md-6 mb-3">
          <label htmlFor="dob" className="form-label">Date of Birth</label>
          <input
            type="date"
            className={`form-control ${errors.dob ? 'is-invalid' : ''}`}
            id="dob"
            name="dob"
            value={formData.dob}
            onChange={handleChange}
            required
          />
          {errors.dob && <div className="invalid-feedback">{errors.dob}</div>}
          <small className="form-text text-muted">You must be at least 18 years old</small>
        </div>
        
        {/* Phone Number */}
        <div className="col-md-6 mb-3">
          <label htmlFor="phoneNumber" className="form-label">Phone Number</label>
          <input
            type="tel"
            className={`form-control ${errors.phoneNumber ? 'is-invalid' : ''}`}
            id="phoneNumber"
            name="phoneNumber"
            value={formData.phoneNumber}
            onChange={handleChange}
            placeholder="+44..."
            required
          />
          {errors.phoneNumber && <div className="invalid-feedback">{errors.phoneNumber}</div>}
          <small className="form-text text-muted">Preferably in international format (e.g., +44...)</small>
        </div>
        
        {/* Email */}
        <div className="col-12 mb-3">
          <label htmlFor="email" className="form-label">Email Address</label>
          <input
            type="email"
            className={`form-control ${errors.email ? 'is-invalid' : ''}`}
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          {errors.email && <div className="invalid-feedback">{errors.email}</div>}
        </div>
      </div>
      
      {/* Address Fields */}
      <AddressFields 
        formData={formData} 
        handleChange={handleChange} 
        errors={errors} 
      />
      
      {/* GDPR Consent */}
      <div className="mb-4">
        <div className="form-check">
          <input
            className="form-check-input"
            type="checkbox"
            id="gdprConsent"
            required
          />
          <label className="form-check-label" htmlFor="gdprConsent">
            I consent to the processing of my personal data in accordance with GDPR
          </label>
        </div>
      </div>
      
      {/* Submit Button */}
      <div className="d-grid">
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Continue to Verification'}
        </button>
      </div>
    </form>
  );
};

export default RegistrationForm;
