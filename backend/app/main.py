from flask import Flask, jsonify
from app.config.database import Database
from app.middleware.cors import init_cors
from app.middleware.error_handlers import register_error_handlers
from app.controllers.auth_controller import auth_api
from app.controllers.user_controller import user_api
from app.controllers.bus_controller import bus_api
from app.controllers.driver_controller import driver_api
from app.controllers.route_controller import route_api, stop_api
import logging

from app.services.factory import ServiceFactory

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

# Register global error handlers
register_error_handlers(app)

# Initialize database connection pool
try:
    db = Database()
    factory = ServiceFactory(db)
    logger.info("Database and ServiceFactory initialized successfully")

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

# Register API blueprints with URL prefixes
app.register_blueprint(auth_api, url_prefix='/api/auth')
app.register_blueprint(user_api, url_prefix='/api/users')
app.register_blueprint(bus_api, url_prefix='/api/buses')
app.register_blueprint(driver_api, url_prefix='/api/drivers')
app.register_blueprint(route_api, url_prefix='/api/routes')
app.register_blueprint(stop_api, url_prefix='/api/stops')

logger.info("All API blueprints registered successfully")

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

