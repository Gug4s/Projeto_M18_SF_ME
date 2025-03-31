from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
import os
from io import BytesIO

app = Flask(__name__)

# Diretório para armazenar imagens temporárias
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar a pasta de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza a página inicial

# Função para verificar tipos de arquivo permitidos
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

# Salvar a imagem original quando for carregada
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'Nenhuma imagem carregada', 400
    image_file = request.files['image']

    if image_file and allowed_file(image_file.filename):
        img = Image.open(image_file)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original_image.jpg')
        edited_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

        img.save(original_path)  # Salva a imagem original
        img.save(edited_path)    # Salva uma cópia para edição
        
        return render_template('index.html', image_url='uploads/uploaded_image.jpg')
    
    return 'Arquivo inválido', 400

# Rota para restaurar a imagem original
@app.route('/reset', methods=['POST'])
def reset_image():
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original_image.jpg')
    edited_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    if os.path.exists(original_path):
        img = Image.open(original_path)
        img.save(edited_path)  # Restaurar a cópia de edição para a versão original
        return send_image(img)
    else:
        return 'Nenhuma imagem original encontrada', 400

# Função para redimensionar imagem
@app.route('/resize', methods=['POST'])
def resize_image():
    width = int(request.form['width'])
    height = int(request.form['height'])
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path)
    img = img.resize((width, height))
    
    img.save(img_path)
    return send_image(img)

# Função para rotacionar imagem
@app.route('/rotate', methods=['POST'])
def rotate_image():
    angle = int(request.form['angle'])
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path)
    img = img.rotate(angle)

    img.save(img_path)
    return send_image(img)

# Função para ajustar brilho e contraste
@app.route('/adjust', methods=['POST'])
def adjust_image():
    brightness = float(request.form['brightness'])
    contrast = float(request.form['contrast'])
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path)
    
    enhancer_brightness = ImageEnhance.Brightness(img)
    img = enhancer_brightness.enhance(brightness)
    
    enhancer_contrast = ImageEnhance.Contrast(img)
    img = enhancer_contrast.enhance(contrast)

    img.save(img_path)
    return send_image(img)

# Função para aplicar filtro preto e branco
@app.route('/bw', methods=['POST'])
def bw_filter():
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    img = Image.open(img_path)
    img = ImageOps.grayscale(img)

    img.save(img_path)
    return send_image(img)

# Função para aplicar filtro sepia
@app.route('/sepia', methods=['POST'])
def sepia_filter():
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    img = Image.open(img_path).convert("RGB")
    
    width, height = img.size
    pixels = img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = pixels[px, py]
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))

    img.save(img_path)
    return send_image(img)

# Função para desenhar formas simples
@app.route('/draw', methods=['POST'])
def draw_on_image():
    shape = request.form['shape']
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    if shape == 'circle':
        draw.ellipse((50, 50, 150, 150), fill='blue', outline='blue')
    elif shape == 'rectangle':
        draw.rectangle((50, 50, 150, 150), fill='red', outline='red')
    elif shape == 'line':
        draw.line((0, 0, img.width, img.height), fill='green', width=5)

    img.save(img_path)
    return send_image(img)

# Função para adicionar texto à imagem
@app.route('/add_text', methods=['POST'])
def add_text():
    text = request.form['text']
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()
    draw.text((10, 10), text, font=font, fill="white")

    img.save(img_path)
    return send_image(img)

# Função auxiliar para enviar imagem como resposta
def send_image(img):
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return send_file(img_byte_arr, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
