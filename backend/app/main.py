from flask import Flask, jsonify
from app.config.database import Database
from app.middleware.cors import init_cors
from app.controllers.auth_controller import auth_api
from app.core.dependencies import init_container
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize CORS middleware
init_cors(app)

# Initialize database connection pool
try:
    db = Database()
    # Store db instance in app config for backward compatibility
    app.config['db'] = db
    logger.info("Database initialized successfully")

    # Initialize dependency injection container
    container = init_container(db)
    app.config['container'] = container
    logger.info("Dependency container initialized successfully")

except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        is_healthy = db.check_health()
        if is_healthy:
            return jsonify({
                'status': 'healthy',
                'database': 'connected'
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected'
            }), 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

# Cleanup on application shutdown
@app.teardown_appcontext
def cleanup(exception=None):
    """Cleanup database connections on application shutdown"""
    if exception:
        logger.error(f"Application error: {exception}")

app.register_blueprint(auth_api, url_prefix='/auth')

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        logger.info("Application shutting down...")
        db.close_all_connections()
    except Exception as e:
        logger.error(f"Application error: {e}")
        db.close_all_connections()
        raise

