
Introdução: Este documento descreve a estrutura técnica e o funcionamento do Editor de Imagens.

Tecnologias utilizadas:
    Frontend: CSS, HTML, JS

    Backend: Python

Bbliotecas:
    Pillow(PIL)
    Flask
    BityIO 

Armazenamento: Sistema de ficheiros local

Estrutura do projeto



Fluxo de funcionamento:

   /Projeto_M18_SF_ME
    |-- Static      #Estilo do site
    |-- Templates   #Aparência do site
    |-- Uploads     #imagens carregadas
    |-- app.py      #código fonte


Fluxo de funcionamento
    1. O utilizador carrega uma imagem através do input file.
    2. A imagem é enviada para o servidor via POST request e armazenada temporariamente.
    3. O utilizador pode aplicar transformações (redimensionar, rodar, aplicar filtros).
    4. As modificações são enviadas para o backend, onde a biblioteca Sharp processa a imagem.
    5. Após o processamento, o utilizador pode visualizar e transferir a imagem editada.


API do backend  
    1. /upload   - Envia a imagem
    2. /resize   - Redimensiona a imaagem
    3. /rotate   - Aplica rotação na imagem
    4. /sepia    - Aplica um filtro "vintage" à imagem
    5. /draw     - Desenha uma forma ou linhas na imagem
    6. /add_text - Adiciona texto na imagem
    7. /reset    - Dá reset à imagem


    


