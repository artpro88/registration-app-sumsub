import React, { useState } from 'react';
import RegistrationForm from './components/RegistrationForm';
import SumsubVerification from './components/SumsubVerification';
import VerificationStatus from './components/VerificationStatus';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [userData, setUserData] = useState(null);
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [accessToken, setAccessToken] = useState(null);

  // Handle form submission
  const handleRegistrationSubmit = async (formData) => {
    try {
      // In a real app, you would send this data to your backend
      console.log('Registration data submitted:', formData);
      
      // Simulate API call to register user and get access token
      // In a real app, this would be an actual API call
      setTimeout(() => {
        setUserData(formData);
        // Simulate getting an access token from the backend
        setAccessToken('sample-access-token');
        setCurrentStep(2);
      }, 1000);
      
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    }
  };

  // Handle verification status update
  const handleVerificationComplete = (status) => {
    setVerificationStatus(status);
    setCurrentStep(3);
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-12 col-lg-10">
          <div className="card">
            <div className="card-header">
              <h2 className="text-center mb-0">User Registration & Verification</h2>
            </div>
            <div className="card-body">
              {/* Step indicator */}
              <div className="step-indicator">
                <div className={`step ${currentStep >= 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
                  <div className="step-number">1</div>
                  <div className="step-title">Registration</div>
                </div>
                <div className={`step ${currentStep >= 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
                  <div className="step-number">2</div>
                  <div className="step-title">Identity Verification</div>
                </div>
                <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
                  <div className="step-number">3</div>
                  <div className="step-title">Verification Status</div>
                </div>
              </div>

              {/* Step content */}
              {currentStep === 1 && (
                <RegistrationForm onSubmit={handleRegistrationSubmit} />
              )}
              
              {currentStep === 2 && accessToken && (
                <SumsubVerification 
                  accessToken={accessToken}
                  userData={userData}
                  onComplete={handleVerificationComplete}
                />
              )}
              
              {currentStep === 3 && verificationStatus && (
                <VerificationStatus status={verificationStatus} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
