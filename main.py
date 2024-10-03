from flask import Flask, request, jsonify, render_template
import webbrowser
from threading import Timer
from backend import calcular_periculosidade

app = Flask(__name__)

# Rota para a página principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para realizar o cálculo
@app.route('/calcular_periculosidade', methods=['POST'])
def calcular_view():
    trabalhadores = request.json.get('trabalhadores', [])
    if not trabalhadores:
        return jsonify({'error': 'Nenhum trabalhador foi adicionado!'}), 400

    resultado = calcular_periculosidade(trabalhadores)
    if 'error' in resultado:
        return jsonify({'error': resultado['error']}), 400
    return jsonify(resultado)

# Função para abrir o navegador
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=False)
