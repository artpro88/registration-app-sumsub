import React from 'react';

const AddressFields = ({ formData, handleChange, errors }) => {
  return (
    <div className="row mb-4">
      <div className="col-12">
        <h3 className="mb-4">Address Information</h3>
      </div>
      
      {/* Street */}
      <div className="col-12 mb-3">
        <label htmlFor="street" className="form-label">Street Address</label>
        <input
          type="text"
          className={`form-control ${errors.street ? 'is-invalid' : ''}`}
          id="street"
          name="street"
          value={formData.street}
          onChange={handleChange}
          required
        />
        {errors.street && <div className="invalid-feedback">{errors.street}</div>}
      </div>
      
      {/* City */}
      <div className="col-md-6 mb-3">
        <label htmlFor="city" className="form-label">City</label>
        <input
          type="text"
          className={`form-control ${errors.city ? 'is-invalid' : ''}`}
          id="city"
          name="city"
          value={formData.city}
          onChange={handleChange}
          required
        />
        {errors.city && <div className="invalid-feedback">{errors.city}</div>}
      </div>
      
      {/* Postcode */}
      <div className="col-md-6 mb-3">
        <label htmlFor="postcode" className="form-label">Postcode</label>
        <input
          type="text"
          className={`form-control ${errors.postcode ? 'is-invalid' : ''}`}
          id="postcode"
          name="postcode"
          value={formData.postcode}
          onChange={handleChange}
          required
        />
        {errors.postcode && <div className="invalid-feedback">{errors.postcode}</div>}
      </div>
    </div>
  );
};

export default AddressFields;
