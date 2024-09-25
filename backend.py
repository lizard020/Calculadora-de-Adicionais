import pandas as pd
import datetime as dt
import locale
import os

# Tenta definir para pt_BR.UTF-8, se não funcionar, define o locale padrão
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Usa o locale padrão do sistema

# DEFINE O DATAFRAME (df)
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

# CALCULA OS DIAS TRABALHADOS POR MÊS (result_df)
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

# CALCULA A PORCENTAGEM DE DIAS TRABALHADOS POR MÊS (dias_trabalhados)
def porcentagem_mes(result_df):
    dias = {'Jan': 31, 'Feb': 28, 'Mar': 31, 'Apr': 30, 'May': 31, 'Jun': 30, 'Jul': 31, 'Aug': 31, 'Sep': 30, 'Oct': 31, 'Nov': 30, 'Dec': 31}
    df_dias = pd.DataFrame([dias])
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    colunas = [round(result_df.loc[:, i] / int(df_dias.iloc[0][i]), 2) for i in all_months]
    dias_mes = pd.concat(colunas, axis=1)
    dias_mes.columns = all_months
    return dias_mes

# CALCULA O SALÁRIO MÍNIMO POR MÊS (df_pivot)
def salario_minimo():
    data = {
        'Data': ['01/2024', '05/2023', '01/2023', '01/2022', '01/2021', '02/2020', '01/2020', '01/2019', '01/2018', '01/2017', '01/2016', '01/2015'],
        'Valor': [1412, 1320, 1302, 1212, 1100, 1045, 1039, 998, 954, 937, 880, 788]
    }
    df = pd.DataFrame(data)
    df[['Mês', 'Ano']] = df['Data'].str.split('/', expand=True)
    df['Ano'] = df['Ano'].astype(int)
    df['Mês'] = df['Mês'].astype(int)
    df = df.drop(columns=['Data'])
    df_pivot = df.pivot(index='Ano', columns='Mês', values='Valor')
    df_pivot.columns = df_pivot.columns.map({
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    })
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df_pivot = df_pivot.reindex(columns=all_months)
    df_pivot = df_pivot.ffill(axis=1)
    return df_pivot

# CALCULA O VALOR DA INSALUBRIDADE POR MÊS (insalubridade)
def insalubridade(salario_minimo, x):
    return salario_minimo * x

# MULTIPLICA O ADICIONAL COM O DATAFRAME DE DIAS TRABALHADOS
def multi_insalubridade(adicional, df):
    resultado = adicional.multiply(df, level='Ano')
    return resultado

# SOMA OS VALORES RESULTANTES PARA OBTER O VALOR FINAL DE INSALUBRIDADE
def soma_insalubridade(df_resultado, df_original):
    resultado_final = df_original.copy()
    resultado_final.update(df_resultado)
    valores = pd.DataFrame(resultado_final.sum(axis=1)).groupby('Nome').sum().rename(columns={0: 'Insalubridade Real'})
    valores['Insalubridade Real'] = valores['Insalubridade Real'].apply(lambda x: locale.currency(x, grouping=True))
    return valores

# DEFINE A FUNÇÃO FINAL
def minha_funcao(nome, inicial, final, grau):
    df = define_df(nome, inicial, final)
    dias = dias_trabalhados(df)
    porc = porcentagem_mes(dias)
    tabela_salario = salario_minimo()
    adicional_insalubridade = insalubridade(tabela_salario, grau)
    resultado_multi = multi_insalubridade(adicional_insalubridade, porc)
    adicional_devido = soma_insalubridade(resultado_multi, porc).reset_index()
    return adicional_devido, porc, resultado_multi

def calcular(trabalhadores):
    resultados = []
    for trabalhador in trabalhadores:
        nome = trabalhador['nome']
        data_inicial = trabalhador['data_inicial']
        data_final = trabalhador['data_final']
        grau = trabalhador['porcentagem']

        try:
            data_inicial = dt.datetime.strptime(data_inicial, "%Y-%m-%d").strftime("%Y-%m-%d")
            data_final = dt.datetime.strptime(data_final, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return {'error': f"Formato de data inválido para {nome}!"}

        adicional_devido, porc, adicional_insalubridade = minha_funcao(nome, data_inicial, data_final, grau)

        meses = porc.sum().sum()
        adicional_devido['Meses'] = round(meses, 2)

        valor = meses * (1412 * grau)
        adicional_devido['Insalubridade VPA'] = locale.currency(valor, grouping=True)

        resultado_trabalhador = adicional_devido.to_dict(orient='records')[0]
        resultado_trabalhador['porc'] = porc.to_dict(orient='split')
        resultados.append(resultado_trabalhador)

    if resultados:
        return resultados
    else:
        return {'error': 'Nenhum cálculo foi realizado!'}
