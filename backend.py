import locale
import pandas as pd
import datetime as dt

# Tenta definir para pt_BR.UTF-8, se não funcionar, define o locale padrão
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Usa o locale padrão do sistema

# Função para definir o DataFrame de datas
def define_df(nome, data_inicial, data_final):
    data = {
        'Nome': [nome],
        'Data_Inicio': [data_inicial],
        'Data_Termino': [data_final]
    }
    df = pd.DataFrame(data)
    df['Data_Inicio'] = pd.to_datetime(df['Data_Inicio'])
    df['Data_Termino'] = pd.to_datetime(df['Data_Termino'])
    return df

# Função para calcular os dias trabalhados por mês
def dias_trabalhados(df):
    def count_days_by_month(row):
        date_range = pd.date_range(start=row['Data_Inicio'], end=row['Data_Termino'], freq='D')
        temp_df = pd.DataFrame({'Date': date_range})
        temp_df['Year'] = temp_df['Date'].dt.year
        temp_df['Month'] = temp_df['Date'].dt.month
        temp_df['Day'] = 1
        grouped = temp_df.groupby(['Year', 'Month']).count().unstack(level=-1)['Day'].fillna(0)
        all_months = pd.Index(range(1, 13), name='Month')
        grouped = grouped.reindex(all_months, axis=1, fill_value=0)
        return grouped

    result = df.apply(count_days_by_month, axis=1)
    result_df = pd.concat(result.values, keys=df['Nome'], names=['Nome', 'Ano'])
    result_df.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return result_df

# Função para calcular a porcentagem de dias trabalhados por mês
def porcentagem_mes(result_df):
    dias = {'Jan': 31, 'Feb': 28, 'Mar': 31, 'Apr': 30, 'May': 31, 'Jun': 30, 'Jul': 31, 'Aug': 31, 'Sep': 30, 'Oct': 31, 'Nov': 30, 'Dec': 31}
    df_dias = pd.DataFrame([dias])
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    colunas = [round(result_df.loc[:, i] / int(df_dias.iloc[0][i]), 2) for i in all_months]
    dias_mes = pd.concat(colunas, axis=1)
    dias_mes.columns = all_months
    return dias_mes

# Função para calcular o adicional de periculosidade
def periculosidade(salario):
    salario_limpo = float(salario.replace("R$", "").replace(".", "").replace(",", ".").strip())
    return salario_limpo * 0.3

# Função principal que realiza os cálculos e retorna os valores
def minha_funcao(nome, data_inicial, data_final, salario):
    df = define_df(nome, data_inicial, data_final)
    dias = dias_trabalhados(df)
    porc = porcentagem_mes(dias)
    meses_trabalhados = porc.sum().sum()  # Total de meses trabalhados baseado nos dias
    adicional_periculosidade = periculosidade(salario)  # Calcula o adicional
    adicional_total = adicional_periculosidade * meses_trabalhados  # Adicional total de periculosidade

    return adicional_total, porc, meses_trabalhados

# Função que itera sobre os trabalhadores e retorna os resultados calculados
def calcular_periculosidade(trabalhadores):
    resultados = []
    for trabalhador in trabalhadores:
        nome = trabalhador['nome']
        salario = trabalhador['salario']
        data_inicial = trabalhador['data_inicial']
        data_final = trabalhador['data_final']

        try:
            data_inicial = dt.datetime.strptime(data_inicial, "%Y-%m-%d").strftime("%Y-%m-%d")
            data_final = dt.datetime.strptime(data_final, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return {'error': f"Formato de data inválido para {nome}!"}

        adicional_total, porc, meses = minha_funcao(nome, data_inicial, data_final, salario)

        # Criamos um dicionário para armazenar os resultados
        resultado_trabalhador = {
            'Nome': nome,
            'Meses': round(meses, 2),
            'Salário': f"R$ {float(salario.replace('R$', '').replace('.', '').replace(',', '.').strip()):,.2f}",
            'Adicional Total': f"R$ {adicional_total:,.2f}",
            'porc': porc.to_dict(orient='split')
        }

        resultados.append(resultado_trabalhador)

    if resultados:
        return resultados
    else:
        return {'error': 'Nenhum cálculo foi realizado!'}
