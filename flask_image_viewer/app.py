# app.py (Backend Flask)
from flask import Flask, jsonify, send_from_directory
import base64
import os
from datetime import datetime
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Configurações
IMAGE_PATH = '/home/uirapuru/disco/anatel_data/figure/test1.png'
STATIC_FOLDER = 'static'

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/plot')
def generate_plot():
    try:
        if os.path.exists(IMAGE_PATH):
            with Image.open(IMAGE_PATH) as img:
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                return jsonify({
                    "image": f"data:image/png;base64,{image_base64}",
                    "timestamp": datetime.now().isoformat()
                })
        return jsonify({"error": "Imagem não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)