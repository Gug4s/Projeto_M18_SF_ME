from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageOps
import os
from io import BytesIO

app = Flask(__name__)

# Diretório para armazenar imagens temporárias
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza o HTML da página inicial

# Rota para carregar a imagem
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'Nenhuma imagem carregada', 400
    image_file = request.files['image']
    
    # Verifica se o arquivo é uma imagem
    if image_file and allowed_file(image_file.filename):
        img = Image.open(image_file)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg'))
        return render_template('index.html', image_url='uploads/uploaded_image.jpg')
    return 'Arquivo inválido', 400

# Função para verificar tipos de arquivo permitidos
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

if __name__ == '__main__':
    app.run(debug=True)
