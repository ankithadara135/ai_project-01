from flask import Flask, request, jsonify, send_from_directory
from analyse import generate_report
from parser import extract_text
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)


@app.after_request
def _add_cors_headers(response):
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
	response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
	return response


@app.before_request
def _log_request():
	# Helpful lightweight logging for debugging 405/failed requests
	try:
		print(f"Incoming request: {request.method} {request.path}")
	except Exception:
		pass

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))


@app.route('/', methods=['GET'])
def index():
	return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>', methods=['GET'])
def frontend_files(filename):
	# Serve other frontend static files (css, js)
	return send_from_directory(FRONTEND_DIR, filename)


@app.route('/uploads/<path:filename>', methods=['GET'])
def download_upload(filename):
	# Serve saved uploaded files for debugging/inspection
	return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route('/upload', methods=['POST', 'OPTIONS'])
@app.route('/upload/', methods=['POST', 'OPTIONS'])
def upload_file():
	# Handle CORS preflight
	if request.method == 'OPTIONS':
		return ('', 200)
	if 'file' not in request.files:
		return jsonify({"error": "no file part"}), 400

	file = request.files['file']
	if file.filename == '':
		return jsonify({"error": "no selected file"}), 400

	filename = secure_filename(file.filename)
	if filename == '':
		return jsonify({"error": "invalid filename"}), 400

	# Avoid collisions: add a timestamp prefix
	import time
	ts = int(time.time())
	filename = f"{ts}_{filename}"
	filepath = os.path.join(UPLOAD_FOLDER, filename)
	try:
		file.save(filepath)
	except Exception as e:
		return jsonify({"error": f"Failed to save uploaded file: {e}"}), 500

	try:
		size = os.path.getsize(filepath)
	except Exception:
		size = None

	try:
		text = extract_text(filepath)
	except FileNotFoundError as e:
		return jsonify({"error": str(e)}), 400
	except Exception as e:
		return jsonify({"error": f"Could not read uploaded file: {e}"}), 500

	try:
		report = generate_report(text)
	except Exception as e:
		return jsonify({"error": f"Error generating report: {e}"}), 500

	# Include diagnostics about the saved file so the client can confirm
	response = {
		"saved": {
			"filename": filename,
			"relative_path": os.path.relpath(filepath, BASE_DIR),
			"size": size,
		},
		**report,
	}
	return jsonify(response)


if __name__ == '__main__':
	app.run(port=5000, debug=True)