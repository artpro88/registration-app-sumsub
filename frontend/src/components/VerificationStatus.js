import React from 'react';

const VerificationStatus = ({ status }) => {
  // Define content based on verification status
  const getStatusContent = () => {
    switch (status) {
      case 'verified':
        return {
          icon: '✅',
          iconClass: 'status-verified',
          title: 'Verification Successful',
          message: 'Your identity has been successfully verified. You can now proceed with using our services.',
          buttonText: 'Continue to Dashboard',
          buttonClass: 'btn-success'
        };
      
      case 'pending':
        return {
          icon: '⏳',
          iconClass: 'status-pending',
          title: 'Verification Pending',
          message: 'Your documents are under review. We\'ll notify you once the verification process is complete. This usually takes 24-48 hours.',
          buttonText: 'Check Status Later',
          buttonClass: 'btn-warning'
        };
      
      case 'rejected':
        return {
          icon: '❌',
          iconClass: 'status-rejected',
          title: 'Verification Failed',
          message: 'Unfortunately, we couldn\'t verify your identity. This could be due to document quality issues or information mismatch. Please try again with clearer documents.',
          buttonText: 'Try Again',
          buttonClass: 'btn-danger'
        };
      
      default:
        return {
          icon: '❓',
          iconClass: '',
          title: 'Unknown Status',
          message: 'We couldn\'t determine the status of your verification. Please contact support for assistance.',
          buttonText: 'Contact Support',
          buttonClass: 'btn-secondary'
        };
    }
  };
  
  const statusContent = getStatusContent();
  
  return (
    <div className="status-container">
      <div className={`status-icon ${statusContent.iconClass}`}>
        {statusContent.icon}
      </div>
      
      <h3 className="mb-3">{statusContent.title}</h3>
      
      <p className="mb-4">{statusContent.message}</p>
      
      {status === 'rejected' && (
        <div className="alert alert-warning mb-4">
          <h5>Common reasons for rejection:</h5>
          <ul className="mb-0 text-start">
            <li>Document is blurry or has poor image quality</li>
            <li>Document is expired or damaged</li>
            <li>Information doesn't match registration details</li>
            <li>Face in selfie doesn't match ID document</li>
            <li>Liveness check failed</li>
          </ul>
        </div>
      )}
      
      <button className={`btn ${statusContent.buttonClass} px-4 py-2`}>
        {statusContent.buttonText}
      </button>
      
      {status !== 'verified' && (
        <div className="mt-4">
          <p className="text-muted">
            Need help? <a href="#contact-support">Contact our support team</a>
          </p>
        </div>
      )}
    </div>
  );
};

export default VerificationStatus;
