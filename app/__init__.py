"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)

# Load Configurations
app.config.from_object('config')

import server
import models
import custom_exceptions

# Set up logging for production
print('Setting up logging for {}...'.format(__name__))
if __name__ != '__main__':
    # sync with gunicorn logger
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
