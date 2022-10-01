import datetime
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from .graphs import *

sidebar_width = "20rem"

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": sidebar_width,
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa"
}

CONTENT_STYLE = {
    "margin-left": sidebar_width,
    "margin-right": "2rem",
    "padding": "4rem 1rem 1rem 1rem"
}

CONTENT_STYLE2 = {
    "margin": "1rem 1rem 1rem 1rem"
}

TEXT_STYLE = {
    'line-height': '3rem',
    'font-weight': '400'
}

GRAPH_DIV_STYLE = {
    "margin": '2rem',
    'border': '3px solid #f5f5f5',
    'border-radius': '0.5rem',
    "box-shadow": '7px 7px #ededed',
}

sidebar = html.Div(
    [
        html.H2("Dados Brasil", className="display-4"),
        html.Hr(),
        html.P(
            "Análise de dados históricos dos últimos 20 anos, por presidente, partido e ano.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Indicadores Socioeconômicos",
                            href="/page-1", active="exact"),
                dbc.NavLink("Gastos da União", href="/page-2", active="exact"),
                dbc.NavLink("Referências dos Dados",
                            href="/page-3", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)


home = html.Div(id="home",
                children=[
                    html.H1('Informações Gerais',
                            style={'font-weight': '500'}),
                    html.Hr(),
                    html.H5(
                        'Pela primeira vez em muito tempo, enfrentamos uma eleição na qual os dois principais candidatos à presidência já governaram o país. Por ser um fato inédito, a situação nos permite escolher entre os presidenciáveis não com base em suas propostas, mas com base em seus mandatos passados. Podemos analisar o quadro social e/ou econômico, os gastos públicos de acordo com o setor e quaisquer outros dados disponíveis que sejam importantes para definição de voto do eleitor.', style=TEXT_STYLE),
                    html.H5(
                        'Aqui, escolheu-se alguns indicadores utilizados como referências globais para medições do quadro socioeconômico de um país, bem como a distribuição dos gastos públicos nos últimos 20 anos.', style=TEXT_STYLE),
                    html.H5(
                        'Todos os dados foram extraídos de fontes confiáveis e estão dísponíveis para download na Aba `Referência dos Dados`.', style=TEXT_STYLE),
                    html.H5(
                        'NÃO HÁ INTERESSE EM PROMOVER NENHUM CANDIDATO. Nosso objetivo consiste apenas em fornecer os dados que julgamos importantes para avaliação de um mandato para auxiliar na escolha/definição do voto.', style=TEXT_STYLE),
                    html.H5(
                        'O VOTO É UM DIREITO. EXERÇA-O!', style=TEXT_STYLE),
                    html.Hr(),
                    html.H4('Indicadores selecionados:'),
                    html.Li('PIB (US$);'),
                    html.Li('PIB per capita (US$);'),
                    html.Li('Taxa de Desemprego;'),
                    html.Li('Taxa de Inflação;'),
                    html.Li('Número de homicídios por 100 mil habitantes;'),
                    html.Li('Índice de Desenvolvimento Humano (IDH);'),
                    html.Li('IDH: posição no ranking mundial;'),
                    html.Li('Índice de Gini;'),
                    html.Li(
                        'Gastos da União por Setor (Saúde, Educação, Segurança, entre outros).'),
                    html.H6(
                        'Desenvolvido por Pedro Henrique Araujo Pinto; M.Sc', style={'line-height': '2rem', 'color': 'darkblue'})
                ],
                style=CONTENT_STYLE2)


indicadores_socioeconomicos = html.Div(id='isec',
                                       children=[
                                           html.Div(id='graph1',
                                                    children=[
                                                        dcc.Graph(figure=pib)],
                                                    style=GRAPH_DIV_STYLE),
                                           html.Div(id='graph2',
                                                    children=[
                                                        dcc.Graph(figure=pib_per_capita)],
                                                    style=GRAPH_DIV_STYLE),
                                           html.Div(id='graph3',
                                                    children=[
                                                        dcc.Graph(figure=desemprego)],
                                                    style=GRAPH_DIV_STYLE),
                                           html.Div(id='graph4',
                                                    children=[
                                                        dcc.Graph(figure=inflacao)],
                                                    style=GRAPH_DIV_STYLE),
                                           html.Div(id='graph5',
                                                    children=[
                                                        dcc.Graph(figure=homicidios)],
                                                    style=GRAPH_DIV_STYLE),
                                           html.Div(id='graph6',
                                                    children=[
                                                        dcc.Graph(figure=idh)],
                                                    style=GRAPH_DIV_STYLE),
                                           html.Div(id='graph7',
                                                    children=[
                                                        dcc.Graph(figure=idh_pos)],
                                                    style=GRAPH_DIV_STYLE),
                                           html.Div(id='graph8',
                                                    children=[
                                                        dcc.Graph(figure=gini)],
                                                    style=GRAPH_DIV_STYLE)
                                       ],
                                       style=CONTENT_STYLE2)


# gastos_uniao = html.Div(id='isec',
#                         children=[html.Div(id='graph8',
#                                            children=[
#                                                dcc.Graph(figure=gastos_uniao)],
#                                            style=GRAPH_DIV_STYLE)],
#                         style=CONTENT_STYLE2)
