import React, { useEffect, useState } from 'react';

const SumsubVerification = ({ accessToken, userData, onComplete }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // Load Sumsub WebSDK script
    const script = document.createElement('script');
    script.src = 'https://static.sumsub.com/idensic/static/sns-websdk-builder.js';
    script.async = true;
    script.onload = initSumsubSDK;
    script.onerror = () => setError('Failed to load Sumsub SDK');
    document.body.appendChild(script);
    
    return () => {
      // Clean up script when component unmounts
      document.body.removeChild(script);
    };
  }, []);
  
  const initSumsubSDK = () => {
    if (!window.snsWebSdk) {
      setError('Sumsub SDK not available');
      return;
    }
    
    setIsLoading(false);
    
    try {
      // Initialize Sumsub WebSDK
      const snsWebSdkInstance = window.snsWebSdk
        .init(
          accessToken,
          // Token update callback - in a real app, this would call your backend
          () => getNewAccessToken()
        )
        .withConf({
          lang: 'en',
          email: userData.email,
          phone: userData.phoneNumber,
          // In a real app, you would use the actual user data
          // firstName: userData.firstName,
          // lastName: userData.lastName,
        })
        .withOptions({ addViewportTag: false, adaptIframeHeight: true })
        .on('idCheck.onStepCompleted', (payload) => {
          console.log('Step completed:', payload);
        })
        .on('idCheck.onStatusChanged', (status) => {
          console.log('Status changed:', status);
          if (status === 'completed' || status === 'approved') {
            onComplete('verified');
          } else if (status === 'rejected') {
            onComplete('rejected');
          }
        })
        .on('idCheck.onError', (error) => {
          console.error('Verification error:', error);
          setError(`Verification error: ${error.message || 'Unknown error'}`);
        })
        .build();
      
      // Launch the WebSDK
      snsWebSdkInstance.launch('#sumsub-websdk-container');
    } catch (err) {
      console.error('Error initializing Sumsub SDK:', err);
      setError(`Error initializing verification: ${err.message}`);
    }
  };
  
  // In a real app, this would call your backend to get a new token
  const getNewAccessToken = () => {
    console.log('Token expired, getting a new one...');
    // This is a mock implementation
    return Promise.resolve(accessToken);
  };
  
  if (isLoading) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading verification...</span>
        </div>
        <p className="mt-3">Loading identity verification...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        <h4 className="alert-heading">Verification Error</h4>
        <p>{error}</p>
        <hr />
        <p className="mb-0">Please try again later or contact support.</p>
      </div>
    );
  }
  
  return (
    <div>
      <div className="alert alert-info mb-4" role="alert">
        <h4 className="alert-heading">Identity Verification</h4>
        <p>Please complete the identity verification process below. You'll need to:</p>
        <ul>
          <li>Upload a valid government-issued ID document</li>
          <li>Take a selfie or complete a liveness check</li>
          <li>Follow any additional instructions provided</li>
        </ul>
        <p className="mb-0">This process helps us verify your identity and comply with regulations.</p>
      </div>
      
      <div id="sumsub-websdk-container"></div>
      
      <div className="text-center mt-4">
        <p className="text-muted small">
          Your data is securely processed in accordance with our privacy policy and applicable regulations.
        </p>
      </div>
    </div>
  );
};

export default SumsubVerification;
