from flask import Flask, render_template, jsonify, send_file
import os
from datetime import datetime

app = Flask(__name__)

IMG_DIR1 = "/home/bingo/disco/Data_Uirapuru/figure_uirapuru"
IMG_DIR2 = "/home/bingo/disco/anatel_data/figure"

current_index = 0

def get_all_images():
    images1 = sorted([f for f in os.listdir(IMG_DIR1) if f.endswith(('.png', '.jpg'))])
    images2 = sorted([f for f in os.listdir(IMG_DIR2) if f.endswith(('.png', '.jpg'))])
    return [("1", img) for img in images1] + [("2", img) for img in images2]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/plot/")
def get_image():
    global current_index
    images = get_all_images()
    if not images:
        return jsonify({"error": "No images found."}), 404

    folder_tag, img_name = images[current_index % len(images)]
    img_path = f"/image/1/{img_name}" if folder_tag == "1" else f"/image/2/{img_name}"

    return jsonify({
        "image": img_path,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

@app.route("/api/next")
def next_image():
    global current_index
    current_index += 1
    return get_image()

@app.route("/api/prev")
def prev_image():
    global current_index
    current_index -= 1
    return get_image()

@app.route("/image/<folder>/<filename>")
def serve_image(folder, filename):
    path = IMG_DIR1 if folder == "1" else IMG_DIR2
    return send_file(os.path.join(path, filename))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)