import os
from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
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
    """
    Verifica se o arquivo possui um formato de imagem permitido.

    @param filename: Nome do arquivo a ser verificado.
    @return: Retorna True se o arquivo tiver uma extensão permitida, False caso contrário.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

@app.route('/')
def index():
    """
    Rota para a página inicial do editor de imagens.
    Renderiza a página HTML com a imagem carregada (se houver).
    
    @return: Renderiza a página inicial.
    """
    return render_template('index.html', image_url=None)

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Rota para o upload de uma imagem para o servidor.

    Verifica se o arquivo enviado é uma imagem válida, converte para o formato RGB (caso tenha transparência),
    e salva a imagem original e a imagem carregada.

    @return: Renderiza a página inicial com a imagem carregada ou retorna uma mensagem de erro.
    """
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Rota para servir a imagem carregada.

    @param filename: Nome do arquivo de imagem a ser enviado.
    @return: Envia a imagem para o cliente.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/reset', methods=['POST'])
def reset_image():
    """
    Rota para restaurar a imagem original e substituí-la pela imagem carregada.

    @return: Envia a imagem restaurada para o cliente.
    """
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original_image.jpg')
    edited_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    if os.path.exists(original_path):
        img = Image.open(original_path)
        img.save(edited_path, format='JPEG')
        return send_image(img)

    return 'Nenhuma imagem original encontrada', 400

@app.route('/resize', methods=['POST'])
def resize_image():
    """
    Rota para redimensionar a imagem carregada.

    Recebe as novas dimensões (largura e altura) e redimensiona a imagem.

    @return: Envia a imagem redimensionada.
    """
    width = int(request.form['width'])
    height = int(request.form['height'])
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path).convert('RGB')
    img = img.resize((width, height))
    img.save(img_path, format='JPEG')
    return send_image(img)

@app.route('/rotate', methods=['POST'])
def rotate_image():
    """
    Rota para rotacionar a imagem carregada.

    Recebe um ângulo (em graus) e rotaciona a imagem carregada.

    @return: Envia a imagem rotacionada.
    """
    angle = int(request.form['angle'])
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')

    img = Image.open(img_path).convert('RGB')
    img = img.rotate(angle, expand=True)
    img.save(img_path, format='JPEG')
    return send_image(img)

@app.route('/bw', methods=['POST'])
def bw_filter():
    """
    Rota para aplicar o filtro preto e branco na imagem.

    Converte a imagem carregada para escala de cinza.

    @return: Envia a imagem em preto e branco.
    """
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    img = Image.open(img_path).convert('L')
    img.save(img_path, format='JPEG')
    return send_image(img)

@app.route('/sepia', methods=['POST'])
def sepia_filter():
    """
    Rota para aplicar o filtro sépia na imagem.

    Aplica um efeito sépia na imagem carregada.

    @return: Envia a imagem com o filtro sépia.
    """
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
# Rota para adicionar texto à imagem carregada
@app.route('/add_text', methods=['POST'])
def add_text():
    """
    Rota para adicionar texto à imagem carregada.

    Recebe o texto inserido pelo usuário e desenha sobre a imagem.

    @return: Exibe a imagem com o texto adicionado.
    """
    text = request.form['text']
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    
    # Abrir a imagem
    img = Image.open(img_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Definir a fonte
    font = ImageFont.load_default()
    
    # Adicionar o texto na imagem
    draw.text((50, 50), text, fill="black", font=font)  # Posição (50, 50) e cor preta

    # Salvar a imagem modificada
    img.save(img_path, format='JPEG')
    
    return send_image(img)

# Rota para adicionar formas à imagem carregada
@app.route('/add_shape', methods=['POST'])
def add_shape():
    """
    Rota para adicionar formas (círculo, retângulo, linha) à imagem carregada.

    Recebe a forma escolhida pelo usuário e desenha sobre a imagem.

    @return: Exibe a imagem com a forma adicionada.
    """
    shape = request.form['shape']
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    
    # Abrir a imagem
    img = Image.open(img_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Adicionar a forma conforme a escolha do usuário
    if shape == 'circle':
        # Adiciona um círculo
        draw.ellipse([100, 100, 200, 200], outline="blue", width=5)
    elif shape == 'rectangle':
        # Adiciona um retângulo
        draw.rectangle([100, 100, 250, 250], outline="red", width=5)
    elif shape == 'line':
        # Adiciona uma linha
        draw.line([100, 100, 200, 200], fill="green", width=5)

    # Salvar a imagem modificada
    img.save(img_path, format='JPEG')
    
    return send_image(img)

@app.route('/download', methods=['GET'])
def download_image():
    """
    Rota para baixar a imagem editada.

    @return: Envia o arquivo de imagem editado como download.
    """
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    return send_file(img_path, as_attachment=True)

def send_image(img):
    """
    Função auxiliar para enviar a imagem como resposta HTTP.

    @param img: A imagem PIL a ser enviada.
    @return: Envia a imagem como resposta HTTP no formato JPEG.
    """
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return send_file(img_byte_arr, mimetype='image/jpeg')

@app.route('/save_canvas', methods=['POST'])
def save_canvas_image():
    """
    Rota para salvar a imagem desenhada no canvas como um arquivo de imagem.

    Recebe a imagem no formato base64, converte para um arquivo e a salva no servidor.

    @return: Envia o arquivo de imagem criada como download.
    """
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
