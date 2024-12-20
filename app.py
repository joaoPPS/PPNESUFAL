import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, render_template, send_file, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

# Inicializar o aplicativo Flask
app = Flask(__name__)

# Definir o caminho para salvar os gráficos
output_dir = 'static/plots'
os.makedirs(output_dir, exist_ok=True)

# Carregar dados globais (simulando um banco de dados)
data_path = r'temperatura-mdia-diria-a.csv'  # Atualize o caminho aqui
data = pd.read_csv(data_path)
data = data['DateTime;"MACEIÓ"'].str.split(';', expand=True)
data.columns = ['DateTime', 'Temperature']
data['DateTime'] = pd.to_datetime(data['DateTime'], errors='coerce')
data['Temperature'] = pd.to_numeric(data['Temperature'], errors='coerce')
data = data.dropna()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    # Obter as datas fornecidas pelo usuário
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # Filtrar os dados
    filtered_data = data[(data['DateTime'] >= start_date) & (data['DateTime'] <= end_date)]

    if filtered_data.empty:
        return "<h3>Não há dados disponíveis para o intervalo selecionado.</h3>"

    # Identificar dias mais quente e mais frio
    hottest_day = filtered_data.loc[filtered_data['Temperature'].idxmax()]
    coldest_day = filtered_data.loc[filtered_data['Temperature'].idxmin()]

    # Calcular temperaturas médias
    daily_means = filtered_data.groupby(filtered_data['DateTime'].dt.date).mean()
    highest_mean_day = daily_means['Temperature'].idxmax()
    lowest_mean_day = daily_means['Temperature'].idxmin()

    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_data['DateTime'], filtered_data['Temperature'], label='Temperatura', color='blue')
    plt.scatter(hottest_day['DateTime'], hottest_day['Temperature'], color='red', label='Mais quente')
    plt.scatter(coldest_day['DateTime'], coldest_day['Temperature'], color='cyan', label='Mais frio')
    plt.xlabel('Data')
    plt.ylabel('Temperatura (°C)')
    plt.title('Variação de Temperatura')
    plt.legend()
    plt.grid()

    # Salvar gráfico como arquivo
    plot_filename = 'temperature_plot.png'
    plot_path = os.path.join(output_dir, plot_filename)
    plt.savefig(plot_path)
    plt.close()

    return render_template('plot.html', plot_url=plot_filename, highest_mean_day=highest_mean_day, lowest_mean_day=lowest_mean_day)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
