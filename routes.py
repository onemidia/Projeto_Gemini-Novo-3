import os
import csv
from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template
from models import Produto
from database import get_db
from werkzeug.utils import secure_filename

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(url_for('routes.index'))

        arquivo = request.files['file']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('routes.index'))

        if arquivo and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            arquivo.save(os.path.join(UPLOAD_FOLDER, filename))

            with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as file:
                reader = csv.reader(file, delimiter=';')
                produtos = []

                with next(get_db()) as db:
                    db.query(Produto).delete()
                    db.commit()

                    for row in reader:
                        try:
                            id_produto = int(row[0])
                            descricao = row[1]
                            valor = float(row[2])
                            unidade = row[3]

                            produto = Produto(id=id_produto, codigo=str(id_produto), descricao=descricao, valor=valor, unidade=unidade)
                            db.add(produto)
                            produtos.append(produto)
                        except ValueError:
                            flash('Erro ao processar linha do arquivo. Verifique o formato.', 'error')
                            db.rollback()
                            break  

                    if produtos:
                        db.commit()
                        flash('Arquivo enviado e atualizado com sucesso!', 'success')
                    else:
                        flash('Nenhum produto processado. Verifique o arquivo.', 'warning')

            return redirect(url_for('routes.index'))

    return render_template('index.html')

@routes.route('/produtos', methods=['GET'])
def get_produtos():
    with next(get_db()) as db:
        produtos = db.query(Produto).all()
        return jsonify([
            {
                'id': produto.id,
                'codigo': produto.codigo,
                'descricao': produto.descricao,
                'valor': produto.valor,
                'unidade': produto.unidade
            } for produto in produtos
        ])
