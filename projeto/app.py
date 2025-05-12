# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template
import base64
import os
from datetime import datetime
from io import BytesIO
from PIL import Image

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/plot')
def generate_plot():
    try:
        images_base64 = []

        # Define data atual
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Atualiza caminhos das imagens com a data atual
        image_paths = [
            f'/home/bingo/test_anatel/{current_date}/figure/test1.png',
            f'/home/bingo/test_uirapuru/{current_date}/figure/test1.png'
        ]
        
        for image_path in image_paths:
            print(f"Verificando imagem: {image_path}")
            if os.path.exists(image_path):
                print(f"Imagem encontrada: {image_path}")
                with Image.open(image_path) as img:
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    images_base64.append(f"data:image/png;base64,{image_base64}")
                    
        if images_base64:
            print("Imagens processadas com sucesso")
            return jsonify({
                "images": images_base64,
                "timestamp": datetime.now().isoformat()
            })
        print("Nenhuma imagem encontrada")
        return jsonify({"error": "Nenhuma imagem encontrada"}), 404
    except Exception as e:
        print("Erro ao processar imagem:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
