import os
import unittest

from flask import jsonify
from flask_migrate import Migrate
from flask.cli import with_appcontext
from pydantic import ValidationError

from app.main import create_app, db
from app import blueprint
# Create Flask app
app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')
app.register_blueprint(blueprint)
# Push the app context to ensure it's available in the shell
app.app_context().push()

# Set up Flask-Migrate
migrate = Migrate(app, db)

# Error handler for validation errors (Pydantic)
@app.errorhandler(ValidationError)
def handle_pydantic_validation_error(error):
    """
    Handles Pydantic validation errors and returns a customized response.
    """
    print('12121')
    response = {
        "message": "Invalid input data",
        "errors": error.errors()  # This will include the validation errors from Pydantic
    }
    return jsonify(response), 422
# Set up custom 'run' command
@app.cli.command('run')
def run():
    """Runs the application."""
    app.run(debug=True)

# Set up custom 'test' command
@app.cli.command('test')
@with_appcontext
def test():
    print('a')
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    app.run(debug=True)
