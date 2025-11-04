from flask import Flask, render_template, send_from_directory, Response
import os
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
	icon_path = os.path.join(app.root_path, 'static', 'favicon.ico')
	if os.path.exists(icon_path):
		return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
	return Response(status=204)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5100, debug=True)
