from flask import Blueprint, render_template

periculosidade_bp = Blueprint('periculosidade', __name__, template_folder='templates', static_folder='static')

@periculosidade_bp.route('/')
def periculosidade_home():
    return render_template('periculosidade.html')