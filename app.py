
from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Generates an HTML index page with links to files in the output directory."""
    output_dir = os.path.join(app.root_path, 'output')
    try:
        # List files in the output directory
        files = os.listdir(output_dir)
        # Filter out directories if any, though likely all are files in this case
        files = [f for f in files if os.path.isfile(os.path.join(output_dir, f))]

    except FileNotFoundError:
        return "Output directory not found.", 404

    # Generate HTML content
    html_content = "<h1>Files in Output Directory:</h1>"
    html_content += "<ul>"
    if files:
        for file in files:
            # Create a link for each file
            html_content += f'<li><a href="/output/{file}">{file}</a></li>'
    else:
        html_content += "<li>No files found in the output directory.</li>"

    html_content += "</ul>"

    return html_content

@app.route('/output/<path:filename>')
def serve_output_file(filename):
    """Serves files from the output directory."""
    output_dir = os.path.join(app.root_path, 'output')
    try:
        return send_from_directory(output_dir, filename)
    except FileNotFoundError:
        return "File not found.", 404

if __name__ == '__main__':
    # In a production environment, use a production-ready WSGI server like Gunicorn or uWSGI.
    # For development, you can run with: python app.py
    app.run(debug=True)
