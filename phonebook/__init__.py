import logging

from flask import current_app, Flask, redirect, request, session, abort, url_for, flash, render_template
from google.cloud import error_reporting
import google.cloud.logging


def create_app(config, debug=False, testing=False, config_overrides=None):
    print (__name__)
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # [START setup_logging]
    if not app.testing:
        client = google.cloud.logging.Client(app.config['PROJECT_ID'])
        # Attaches a Google Stackdriver logging handler to the root logger
        client.setup_logging(logging.INFO)
    # [END setup_logging]

    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)

    # Add a logout handler.
    @app.route('/logout')
    def logout():
        # Delete the logged_in in session
        del session['logged_in']  #session['profile']
        session.modified = True
        return redirect('/')

    @app.route('/')
    def index():
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return redirect(url_for('crud.list'))

    @app.route('/login', methods=['POST'])
    def do_admin_login():
        if request.form['password'] == 'ArashIsAwesome' and request.form['username'] == 'admin':
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return index()

    # Register the Phonebook CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/contacts')


    # Add an error handler that reports exceptions to Stackdriver Error
    # Reporting. Note that this error handler is only used when debug
    # is False
    # [START setup_error_reporting]
    @app.errorhandler(500)
    def server_error(e):
        client = error_reporting.Client(app.config['PROJECT_ID'])
        client.report_exception(
            http_context=error_reporting.build_flask_context(request))
        return """
        An internal error occurred.
        """, 500
    # [END setup_error_reporting]

    return app


def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'datastore':
        from . import model_datastore
        model = model_datastore
    else:
        raise ValueError(
            "No appropriate databackend configured. "
            "Please specify datastore, cloudsql, or mongodb")

    return model

