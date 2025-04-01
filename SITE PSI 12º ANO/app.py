import os
from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
from PIL import Image, ImageEnhance, ImageOps
from io import BytesIO
import base64

app = Flask(__name__)

# Configuração do diretório de uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ Criar a pasta uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Função para verificar se o arquivo tem um formato permitido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

@app.route('/')
def index():
    return render_template('index.html', image_url=None)

# Upload da imagem
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'Nenhuma imagem carregada', 400

    image_file = request.files['image']
    if image_file and allowed_file(image_file.filename):
        img = Image.open(image_file)

        # Converter para RGB se a imagem tiver transparência
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        filename = 'uploaded_image.jpg'
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original_image.jpg')
        edited_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        img.save(original_path, format='JPEG')
        img.save(edited_path, format='JPEG')

        return render_template('index.html', image_url=filename)

    return 'Arquivo inválido', 400

# Servir imagens carregadas
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Restaurar a imagem original
@app.route('/reset', methods=['POST'])
def reset_image():
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original_image.jpg')
    edited_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    if os.path.exists(original_path):
        img = Image.open(original_path)
        img.save(edited_path, format='JPEG')
        return send_image(img)

    return 'Nenhuma imagem original encontrada', 400

# Redimensionar a imagem
@app.route('/resize', methods=['POST'])
def resize_image():
    width = int(request.form['width'])
    height = int(request.form['height'])
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path).convert('RGB')
    img = img.resize((width, height))
    img.save(img_path, format='JPEG')
    return send_image(img)

# Rotacionar a imagem
@app.route('/rotate', methods=['POST'])
def rotate_image():
    angle = int(request.form['angle'])
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path).convert('RGB')
    img = img.rotate(angle, expand=True)
    img.save(img_path, format='JPEG')
    return send_image(img)

# Aplicar filtro preto e branco
@app.route('/bw', methods=['POST'])
def bw_filter():
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    img = Image.open(img_path).convert('L')
    img.save(img_path, format='JPEG')
    return send_image(img)

# Aplicar filtro sépia
@app.route('/sepia', methods=['POST'])
def sepia_filter():
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    img = Image.open(img_path).convert('RGB')

    width, height = img.size
    pixels = img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = pixels[px, py]
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))

    img.save(img_path, format='JPEG')
    return send_image(img)

# Baixar imagem editada
@app.route('/download', methods=['GET'])
def download_image():
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    return send_file(img_path, as_attachment=True)

# Enviar imagem editada como resposta
def send_image(img):
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return send_file(img_byte_arr, mimetype='image/jpeg')

# Rota para salvar a imagem criada no canvas
@app.route('/save_canvas', methods=['POST'])
def save_canvas_image():
    data = request.get_json()
    image_data = data.get('image_data')

    # Convertendo a dataURL para imagem
    image_data = image_data.split(',')[1]  # Remove a parte 'data:image/jpeg;base64,'  
    img_bytes = base64.b64decode(image_data)

    img = Image.open(BytesIO(img_bytes))
    filename = 'created_image.jpg'
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    img.save(img_path, format='JPEG')

    return send_file(img_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
