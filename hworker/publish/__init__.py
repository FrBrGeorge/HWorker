import os


from .app import app


def run_server():
    if "DEBUG_ENVIRONMENT" in os.environ:
        app.run(debug=True, use_debugger=True, use_reloader=False)
