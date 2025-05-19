-- Database schema for Registration App with Sumsub Integration

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postcode VARCHAR(20) NOT NULL,
    verification_status VARCHAR(20) DEFAULT 'pending',
    applicant_id VARCHAR(100),
    verification_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table for authentication
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Audit logs table for tracking important events
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Verification history table for tracking verification status changes
CREATE TABLE IF NOT EXISTS verification_history (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    applicant_id VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Webhooks table for tracking received webhooks
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY,
    applicant_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_applicant_id ON users(applicant_id);
CREATE INDEX IF NOT EXISTS idx_users_verification_status ON users(verification_status);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_verification_history_user_id ON verification_history(user_id);
CREATE INDEX IF NOT EXISTS idx_webhooks_applicant_id ON webhooks(applicant_id);
CREATE INDEX IF NOT EXISTS idx_webhooks_processed ON webhooks(processed);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create function to log verification status changes
CREATE OR REPLACE FUNCTION log_verification_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.verification_status IS DISTINCT FROM NEW.verification_status THEN
        INSERT INTO verification_history (
            id, user_id, previous_status, new_status, applicant_id, details
        ) VALUES (
            gen_random_uuid(),
            NEW.id,
            OLD.verification_status,
            NEW.verification_status,
            NEW.applicant_id,
            NEW.verification_details
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically log verification status changes
CREATE TRIGGER log_users_verification_status_change
AFTER UPDATE OF verification_status ON users
FOR EACH ROW
EXECUTE FUNCTION log_verification_status_change();

-- Create function to clean up expired sessions
CREATE OR REPLACE FUNCTION clean_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions
    WHERE expires_at < NOW()
    RETURNING COUNT(*) INTO deleted_count;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE users IS 'Stores user registration information and verification status';
COMMENT ON TABLE sessions IS 'Stores user authentication sessions';
COMMENT ON TABLE audit_logs IS 'Stores audit logs for important actions';
COMMENT ON TABLE verification_history IS 'Stores history of verification status changes';
COMMENT ON TABLE webhooks IS 'Stores received webhooks from Sumsub';

COMMENT ON COLUMN users.verification_status IS 'Current verification status: pending, verified, rejected';
COMMENT ON COLUMN users.applicant_id IS 'Sumsub applicant ID';
COMMENT ON COLUMN users.verification_details IS 'JSON details of verification process';

COMMENT ON COLUMN sessions.token IS 'Authentication token';
COMMENT ON COLUMN sessions.expires_at IS 'Expiration timestamp for the session';

COMMENT ON COLUMN audit_logs.action IS 'Action performed: USER_CREATED, VERIFICATION_STATUS_UPDATED, etc.';
COMMENT ON COLUMN audit_logs.details IS 'Additional details about the action';

COMMENT ON COLUMN verification_history.previous_status IS 'Previous verification status';
COMMENT ON COLUMN verification_history.new_status IS 'New verification status';
COMMENT ON COLUMN verification_history.details IS 'JSON details of the verification status change';

COMMENT ON COLUMN webhooks.event_type IS 'Sumsub webhook event type';
COMMENT ON COLUMN webhooks.payload IS 'JSON payload of the webhook';
COMMENT ON COLUMN webhooks.processed IS 'Whether the webhook has been processed';
COMMENT ON COLUMN webhooks.error IS 'Error message if processing failed';
