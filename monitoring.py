import logging
import os
import time
import json
import threading
import sqlite3
from datetime import datetime, timedelta

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Application logger
app_logger = logging.getLogger('app')
app_logger.setLevel(logging.INFO)

# Create handlers
app_file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'app.log'))
app_file_handler.setLevel(logging.INFO)

# Error logger
error_logger = logging.getLogger('error')
error_logger.setLevel(logging.ERROR)

error_file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'error.log'))
error_file_handler.setLevel(logging.ERROR)

# Access logger
access_logger = logging.getLogger('access')
access_logger.setLevel(logging.INFO)

access_file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'access.log'))
access_file_handler.setLevel(logging.INFO)

# Create formatters
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_file_handler.setFormatter(formatter)
error_file_handler.setFormatter(formatter)
access_file_handler.setFormatter(formatter)

# Add handlers to loggers
app_logger.addHandler(app_file_handler)
error_logger.addHandler(error_file_handler)
access_logger.addHandler(access_file_handler)

# Performance metrics
metrics = {
    'requests': 0,
    'errors': 0,
    'response_times': [],
    'status_codes': {},
    'endpoints': {},
    'start_time': time.time()
}

# Lock for thread-safe metrics updates
metrics_lock = threading.Lock()

def log_request(method, path, status_code, response_time, ip_address=None):
    """Log an HTTP request"""
    access_logger.info(f"{method} {path} {status_code} {response_time:.2f}ms - {ip_address or 'unknown'}")
    
    with metrics_lock:
        metrics['requests'] += 1
        metrics['response_times'].append(response_time)
        
        # Update status code counts
        metrics['status_codes'][status_code] = metrics['status_codes'].get(status_code, 0) + 1
        
        # Update endpoint counts
        endpoint = path.split('?')[0]  # Remove query parameters
        metrics['endpoints'][endpoint] = metrics['endpoints'].get(endpoint, 0) + 1

def log_error(error, context=None):
    """Log an error"""
    error_message = str(error)
    context_str = json.dumps(context) if context else ""
    error_logger.error(f"{error_message} - {context_str}")
    
    with metrics_lock:
        metrics['errors'] += 1

def get_metrics():
    """Get current performance metrics"""
    with metrics_lock:
        avg_response_time = sum(metrics['response_times']) / len(metrics['response_times']) if metrics['response_times'] else 0
        uptime = time.time() - metrics['start_time']
        
        return {
            'requests': metrics['requests'],
            'errors': metrics['errors'],
            'avg_response_time': avg_response_time,
            'status_codes': metrics['status_codes'],
            'top_endpoints': sorted(metrics['endpoints'].items(), key=lambda x: x[1], reverse=True)[:5],
            'uptime': uptime
        }

def reset_metrics():
    """Reset performance metrics"""
    with metrics_lock:
        metrics['requests'] = 0
        metrics['errors'] = 0
        metrics['response_times'] = []
        metrics['status_codes'] = {}
        metrics['endpoints'] = {}
        metrics['start_time'] = time.time()

def monitor_database():
    """Monitor database health"""
    try:
        from database import DB_FILE
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        # Check recent verifications
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM users WHERE updated_at > ? AND verification_status != 'pending'", (yesterday,))
        recent_verifications = cursor.fetchone()[0]
        
        # Check audit logs
        cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE created_at > ?", (yesterday,))
        recent_logs = cursor.fetchone()[0]
        
        conn.close()
        
        app_logger.info(f"Database health: {user_count} users, {recent_verifications} recent verifications, {recent_logs} recent logs")
        return {
            'user_count': user_count,
            'recent_verifications': recent_verifications,
            'recent_logs': recent_logs,
            'status': 'healthy'
        }
    except Exception as e:
        error_logger.error(f"Database monitoring error: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

# Start periodic monitoring
def start_monitoring(interval=3600):
    """Start periodic monitoring"""
    def monitor_task():
        while True:
            db_health = monitor_database()
            app_metrics = get_metrics()
            
            app_logger.info(f"System metrics: {json.dumps(app_metrics)}")
            app_logger.info(f"Database health: {json.dumps(db_health)}")
            
            # Sleep for the specified interval
            time.sleep(interval)
    
    # Start monitoring in a background thread
    monitor_thread = threading.Thread(target=monitor_task, daemon=True)
    monitor_thread.start()
    
    return monitor_thread
