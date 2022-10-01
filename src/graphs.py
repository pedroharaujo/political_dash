import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

######################################## INDICADORES SOCIOECONÔMICOS ########################################
data_ise = pd.read_excel(
    './data.xlsx', sheet_name='indicadores_socioeconomicos')
data_ise = data_ise.iloc[5:-2, :].reset_index(drop=True)
data_ise.rename({'Homícidos (/100k)': 'Homicídios (/100k)'},
                axis=1, inplace=True)

color_dict = {"FHC": "blue", "Lula": "red", "Dilma": "purple",
              "Temer": "orange", "Bolsonaro": "green"}

titles = {'PIB (US$)': 'Produto Interno Bruto (PIB) em Doláres (US$)',
          'PIB Per Capita (US$)': 'Produto Interno Bruto (PIB) per capita em Doláres (US$)',
          'Desemprego (%)': 'Taxa de Desemprego (%)',
          'Inflação (%)': 'Taxa de Inflação - Índice de Preços ao Consumidor (IPC)',
          'Homicídios (/100k)': 'Número de Homicídios para cada 100 mil habitantes',
          'IDH': 'Índice de Desenvolvimento Humano (IDH)',
          'IDH (posicao)': 'IDH (posição no ranking mundial)',
          'Índice de Gini': 'Índice de Gini'}

data_ise['color'] = [color_dict[candidato]
                     for candidato in data_ise['Governo']]


def lineGraph(data, col, color_dict, titles):
    fig = go.Figure()

    for governo in list(color_dict.keys()):
        tmp = data.iloc[data[data['Governo'] == governo].index[0]:data[data['Governo'] == governo].index[-1]+2]
        if col == 'PIB (US$)':
            text = [f'{round(k / 10**12, 2)}T' for k in tmp[col].astype(float)]
        elif col == 'PIB Per Capita (US$)':
            text = [f'{round(k / 10**3, 2)}K' for k in tmp[col].astype(float)]
        elif col == 'Desemprego (%)':
            text = [f'{round(k*100, 2)}%' for k in tmp[col].astype(float)]
        elif col == 'IDH (posicao)':
            text = [f'{round(k, 0)}' for k in tmp[col].astype(float)]
        else:
            text = [f'{round(k, 2)}' for k in tmp[col].astype(float)]
        fig.add_trace(go.Scatter(x=tmp['Ano'], y=tmp[col],
                                 text=text, textposition="top center",
                                 line=dict(color=color_dict[governo]), mode='markers+lines+text', showlegend=True, name=governo))

    for i in range(len(color_dict)):
        candidato = list(color_dict.keys())[i]
        color = list(color_dict.values())[i]
        if i == len(color_dict)-1:
            fig.add_vrect(
                x0=int(data[data['Governo'] == candidato].iloc[0]
                       ['Ano'])-int(data.loc[0, 'Ano']),
                x1=int(data[data['Governo'] == candidato].iloc[-1]
                       ['Ano'])-int(data.loc[0, 'Ano']),
                fillcolor=color,
                opacity=0.075,
                line_width=0)
        else:
            fig.add_vrect(
                x0=int(data[data['Governo'] == candidato].iloc[0]
                       ['Ano'])-int(data.loc[0, 'Ano']),
                x1=int(data[data['Governo'] == candidato].iloc[-1]
                       ['Ano'])-int(data.loc[0, 'Ano'])+1,
                fillcolor=color,
                opacity=0.075,
                line_width=0)

        fig.update_layout(title=titles[col],
                          xaxis_title="Ano",
                          yaxis_title=col,
                          legend_title="Presidente",
                          plot_bgcolor='#f5f5f5'
                          )
        fig.update_xaxes(showgrid=False)
    return fig


pib = lineGraph(data_ise, 'PIB (US$)', color_dict=color_dict, titles=titles)
pib_per_capita = lineGraph(
    data_ise, 'PIB Per Capita (US$)', color_dict, titles)
desemprego = lineGraph(data_ise, 'Desemprego (%)',
                       color_dict=color_dict, titles=titles)
inflacao = lineGraph(data_ise, 'Inflação (%)',
                     color_dict=color_dict, titles=titles)
homicidios = lineGraph(data_ise, 'Homicídios (/100k)',
                       color_dict=color_dict, titles=titles)
idh = lineGraph(data_ise, 'IDH',
                color_dict=color_dict, titles=titles)
idh_pos = lineGraph(data_ise, 'IDH (posicao)',
                    color_dict=color_dict, titles=titles)
gini = lineGraph(data_ise, 'Índice de Gini',
                 color_dict=color_dict, titles=titles)

######################################## GASTOS DA UNIÃO POR SETOR ########################################
data_gastos = pd.read_excel('./data.xlsx', sheet_name='gastos_união_por_setor')
data_gastos = data_gastos.iloc[:-2, :]
