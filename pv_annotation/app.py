from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from utils import annotate_image, annotate_video


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


ALLOWED_IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.bmp'}
ALLOWED_VIDEO_EXT = {'.mp4', '.mov', '.avi', '.mkv'}


def is_image(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_IMAGE_EXT


def is_video(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_VIDEO_EXT


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    return render_template('index.html', result=None)


@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    if not file or file.filename.strip() == '':
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    in_path = os.path.join(UPLOAD_DIR, filename)
    file.save(in_path)

    if is_image(filename):
        out_name = os.path.splitext(filename)[0] + '_annotated.png'
        out_path = os.path.join(OUTPUT_DIR, out_name)
        annotate_image(in_path, out_path)
        result = {
            'kind': 'image',
            'input_url': url_for('static_file', folder='uploads', filename=filename),
            'output_url': url_for('static_file', folder='outputs', filename=out_name)
        }
    elif is_video(filename):
        out_name = os.path.splitext(filename)[0] + '_annotated.mp4'
        out_path = os.path.join(OUTPUT_DIR, out_name)
        annotate_video(in_path, out_path)
        from time import time
        result = {
            'kind': 'video',
            'input_url': url_for('static_file', folder='uploads', filename=filename) + f"?t={int(time())}",
            'output_url': url_for('static_file', folder='outputs', filename=out_name) + f"?t={int(time())}"
        }
    else:
        return redirect(url_for('index'))

    return render_template('index.html', result=result)


@app.route('/files/<path:folder>/<path:filename>')
def static_file(folder, filename):
    root = UPLOAD_DIR if folder == 'uploads' else OUTPUT_DIR
    return send_from_directory(root, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5600, debug=True)


