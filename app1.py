import base64
import csv
import random
import time
import json
from functions import *
import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import networkx as nx
from dash.dependencies import Input, Output, State
from fa2l import force_atlas2_layout
from flask import Flask
from flask import request
import requests

app = dash.Dash()
default_stylesheet = [  # Стиль элементов графа
    {
        'selector': 'core',  # Стиль для вершин
        'style': {
            'active-bg-size': '0',
        }
    },
    {
        'selector': 'node',  # Стиль для вершин
        'style': {
            'background-color': '#BFD7B5',
            'text-valign': 'center',
            'label': 'data(label)',
            'font-size': "10px",
            'width': "20%",
            'height': "20%"
        }
    },
    {
        'selector': 'edge',  # Стиль для ребер
        'style': {
            'line-color': '#A3C4BC'
        }
    },
    {
        'selector': ':selected ',  # Стиль для выделенных вершин
        'style': {
            'background-color': 'orange',
        }
    }
]

gradient = ['#2200ff', '#5700f8', '#7400f0', '#8a00e8', '#9c00df',
            '#ab00d7', '#b900ce', '#c500c5', '#cf00bc', '#d800b3',
            '#e100a9', '#e800a0', '#ef0097', '#f4008e', '#f90085',
            '#fd007c', '#ff0073', '#ff006b', '#ff0063', '#ff005a',
            '#ff0052', '#ff004b', '#ff0043', '#ff003b', '#ff0034',
            '#ff002c', '#ff0024', '#ff001b', '#ff0010', '#ff0000']
options = [
    {"label": "Центральность", "value": "centr"},
    {"label": "Кластерность", "value": "clust"},
    {"label": "Связность", "value": "svyaz"},
    {"label": "Шарниры", "value": "sharn"},
]
options_stats = [
    {"label": "Центральность", "value": "centr_stats"},
    {"label": "Кластерность", "value": "clust_stats"},
    {"label": "Связность", "value": "svyaz_stats"},
    {"label": "Пусто", "value": "no_stats"},
]

addedEdges = []  # Массив для сохранения хода защиты , сохраняет добавленные во время хода ребра
edges = []  # Массив ребер
nodes = []  # Массив вершин
selected = None  # Массив с выделенными вершинами
global_turn = 0  # ход чет - атака     нечет - защита
turn_interface = 0  # Счетчик ходов для интерфейса
side = 'Ход атаки'  # Ходящая сторона для интерфейса
EndOfGame = False  # Флаг окончания игры
provereno = False  # Флаг проверки окончания игры по Косарайю
MaxTurns = 0  # Счетчик количества ходов
Fora = 0  # Счетчик форы
pereschitanaFora = False  # Флаг пересчета форы , как начинается игра
Pull = 0  # Количество ребер у защищающегося
added = -1  # Номер только что добавленной вершины
skip = False  # Флаг неизменности хода при попытке удалить только что добавленную вершину
start_ways = 0  # Количество путей в графе
canFindSharneers = False  # Флаг поиска шарниров , позволяющий начать их поиск
node_count = 0  # Количество вершин в графе
save_strings = []
loaded = False
loaded_strings = []
global_turn = 0
turn_pereschitan = False
global_turn_flag = False
notation_flag = False
x = 0.0
y = 0.0
children_style_source = []
children_style_target = []
children_style = []
centr_stylesheet = []
clust_stylesheet = []
svyaz_stylesheet = []
checklist = [] # галочки для хелперов
save_strings_stats = [] # сохранение для статистики
MaxFora = 0


btn_generate_pressed=False

app.layout = html.Div([  # главный
    html.Div([
        html.Div([
            html.Button('⭯', id='btn-reset', n_clicks_timestamp=0, style=dict(display='inline')),
            html.Div([dcc.Upload(id='upload-data', children=html.Div([
                    html.P('⭳', style={'margin-top':'8px'} ),], ))] ,id='uploadDiv',style=dict(display='inline')),
            html.Div([
                html.Button('Сгенерировать граф', id='btn-generate', n_clicks_timestamp=0, style=dict(display='block')),
                html.Button('Импортировать граф', id='btn-start', n_clicks_timestamp=0, style=dict(display='block')),
                html.Button('Следующий ход', id='btn-nxt-trn', n_clicks_timestamp=0, style=dict(display='none')),
                html.Button('Удалить вершину', id='btn-remove-node', n_clicks_timestamp=0, style=dict(display='none')),
            ], id='leftmenu'),
            html.Div([
                html.P(["Параметры генерируемого графа:"], style={'font-size': '18px', 'width': '100%'}),
                html.Br(),
                html.P(["Количество вершин: ",
                        html.Br(),
                        dcc.Input(id='input_countNodes', value=10, type='text')]),
                html.P(["Степень связности : ",
                        html.Br(),
                        dcc.Input(id='input_links', value=4, type='text')]),
                html.P(["Количество ходов: ",
                        html.Br(),
                        dcc.Input(id='input_countTurns', value=8, type='text')]),
                html.P(["Фора атакующего: ",
                        html.Br(),
                        dcc.Input(id='input_fora', value=0, type='text')]),
                html.P(["Пул рёбер защищающегося: ",
                        html.Br(),
                        dcc.Input(id='input_pulledges', value=20, type='text') ]),

            ], id='input_countNodesVision'),

            html.Div([
                html.P(['Помощь в игре'],
                       style={'font-size': '18px', 'position': 'absolute', "width": "20%", 'padding-left': '30px',
                              'text-align': 'left'}),
                html.Div([
                    dcc.Checklist(
                        id="checklist",
                        options=options,
                        value=[],
                        style={"height": "140px"},
                        labelStyle={"display": "flex", "flex-flow": "column wrap", "text-size": "18px",
                                    'justify-content': 'center',
                                    "height": "30px", 'text-align': 'left', "width": "60px",
                                    'font-family': 'system-ui'},
                        inputStyle={"margin": "5px", "width": "20px", 'justify-content': 'center',
                                    'border-radius': '10px'}
                    ), ], id='checklistDiv'),
            ], id='Helpers' , style=dict(display='none')),
            html.Div([
                html.P(['Cтатистика'],
                       style={'font-size': '18px', 'position': 'absolute', "width": "20%", 'padding-left': '30px',
                              'text-align': 'left'}),
                html.Div([
                        dcc.RadioItems(
                        id="radio_stats",
                        options=options_stats,
                        style={"height": "140px"},
                        labelStyle={"display": "flex", "flex-flow": "column wrap", "text-size": "18px",
                                    'justify-content': 'center',
                                    "height": "30px", 'text-align': 'left', "width": "60px",
                                    'font-family': 'system-ui'},
                        inputStyle={"margin": "5px", "width": "20px", 'justify-content': 'center',
                                    'border-radius': '10px'}),
                     ], id='checklistDivStat'),
            ], id='HelpersStat', style=dict(display='none')),

        ], id='leftbar'),
        html.Div([
            html.Div([
                html.Img(src='assets/logo.png', style={'width': '15%','position':'absolute','z-index':'1000','margin-top':'5px' }, id='logo'),
                cyto.Cytoscape(
                    id='cytoscape-elements-callbacks',
                    layout={
                        'name': 'preset',
                        'positions': {
                            node['data']['id']: node['position']
                            for node in nodes
                        }
                    },
                    stylesheet=default_stylesheet,
                    style={'width': '100%', 'height': '490px', 'border-radius': '30px',
                           'background': '#ecf0f3',
                           'box-shadow': 'inset 5px 5px 10px #d1d9e6, inset -5px -5px 10px #fff'},
                    elements=nodes + edges,
                )
            ], id='cyto'),
            html.Div([
                html.P(id='moving-side'),
                html.P(id='moves-counter'),
                html.P(id='pull-counter', style=dict(display='none'))
            ], id='move'),
        ], id='centerfield'),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.P('Ход игры', id='labelNotla'),
                    ], id='labelNot'),
                    html.Div([
                        html.P(id='first',
                               style={'whiteSpace': 'pre-line', 'margin-left': '20px', 'font-size': '20px'}),
                        html.P(id='selectedText',
                               style={'whiteSpace': 'pre-line', 'margin-left': '20px', 'font-size': '20px'}),
                        html.P(id='last', style={'whiteSpace': 'pre-line', 'margin-left': '20px', 'font-size': '20px'}),
                    ], id='textNot'),
                ], id='textnotation'),
                html.Div([
                    html.Button('Назад', id='btn-undo', n_clicks_timestamp=0,
                                style=dict(display='block', width='100px')),
                    html.Button('Вперед', id='btn-redo', n_clicks_timestamp=0,
                                style=dict(display='block', width='100px')),
                ], id='buttonnotation'),
            ], id='notcontent')
        ], id='notation'),
    ], id='up'),

    html.Div([
        html.Div([
            html.Div(dcc.Graph(id='graph',
                               figure={'data': []},
                               config={'displayModeBar': False, 'responsive': True}),
                               style={'display': 'block'}),
        ], id='Charts'),
        html.Div([
            html.P(id='average_min_max', style={'whiteSpace': 'pre-line', 'margin-left': '15px', 'font-size': '20px'}),
        ], id='ChartsStats'),
        html.Div([
            html.Button('Сохранить', id='btn-save', n_clicks_timestamp=0, style=dict(display='block')),
            html.Button('Загрузить', id='btn-load', n_clicks_timestamp=0, style=dict(display='block')),
            html.P(["Имя сохранения: ",
                    html.Br(),
                    dcc.Input(id='input_save-name', value='', type='text'),
                    html.Br(), ], id='input_save-nameDiv'),
        ], id='SaveLoad'),
    ], id='down'),
html.P(id='cytoscape-selectedNodeData-output'),
])


@app.callback(Output('cytoscape-selectedNodeData-output', 'children'),
              Input('cytoscape-elements-callbacks', 'selectedNodeData'))
def displayTapNodeData(data):
    global selected, canFindSharneers
    if data:
        if len(data) == 2:
            selected = []
            for i in data:
                selected.append(int(i['id']))
        selected = data[0].get('id')
    canFindSharneers = True


response = []


@app.callback(
    Output('cytoscape-elements-callbacks', 'elements'),
    Input('input_countNodes', 'value'),
    Input('input_links', 'value'),
    Input('input_countTurns', 'value'),
    Input('input_fora', 'value'),
    Input('input_pulledges', 'value'),
    Input('btn-generate', 'n_clicks_timestamp'),
    Input('btn-remove-node', 'n_clicks_timestamp'),
    Input('cytoscape-elements-callbacks', 'selectedNodeData'),
    Input('btn-nxt-trn', 'n_clicks_timestamp'),
    Input('btn-start', 'n_clicks_timestamp'),
    Input('upload-data', 'contents'),
    Input('btn-undo', 'n_clicks_timestamp'),
    Input('btn-redo', 'n_clicks_timestamp'),
    Input('btn-load', 'n_clicks_timestamp'),
    Input('input_save-name', 'value'),
    Input('btn-reset', 'n_clicks_timestamp'),
)
def update_elements(count, links, Max_turns, fora, pull, btn_generate, btn_remove_node, data, btn_nxt_trn, btn_start, content, btn_undo, btn_redo, btn_load, name, btn_reset):
    global btn_generate_pressed, selected, response
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-generate' in changed_id:
        url = 'http://127.0.0.1:5000/start/' + str(count) + '/' + str(links) + '/' + str(Max_turns) + '/' + str(fora) + '/' + str(pull)
        response = requests.post(url, data={}).json()['otvet']
        print(response)
        btn_generate_pressed = True
    if 'btn-start' in changed_id:
        print(content)
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string).decode("utf-8").replace('\r', '').split('\n')
        content = decoded
        jsonString = json.dumps(content)
        print(jsonString)
        url = 'http://127.0.0.1:5000/importCSV/' + str(Max_turns) + '/' + str(fora) + '/' + str(pull)
        response = requests.post(url, data={'content' : jsonString}).json()['otvet']
        print(response)
        btn_generate_pressed = True
    elif 'btn-remove-node' in changed_id:
        if len(selected) == 1:
            url = 'http://127.0.0.1:5000/delete/' + str(selected[0])
            response = requests.post(url, data={}).json()['otvet']
            selected = []
    elif 'btn-nxt-trn' in changed_id:
        url = 'http://127.0.0.1:5000/next_turn'
        response = requests.post(url, data={}).json()['otvet']
    elif 'btn-undo' in changed_id:
        url = 'http://127.0.0.1:5000/undo'
        response = requests.post(url, data={}).json()['otvet']
        print(response)
        return response
    elif 'btn-redo' in changed_id:
        url = 'http://127.0.0.1:5000/redo'
        response = requests.post(url, data={}).json()['otvet']
        return response
    elif 'btn-load' in changed_id:
        url = 'http://127.0.0.1:5000/load/'+ name
        response = requests.post(url, data={}).json()['otvet']
        print(response)
        btn_generate_pressed = True
        return response
    elif 'btn-reset' in changed_id:
        return []+[]
    else:
        if data:
            if len(data) == 2:
                print("-----------------------------")
                print(data)
                print("-----------------------------")
                src = int(data[0]['id'])
                tar = int(data[1]['id'])
                spisok = [src, tar]
                url = 'http://127.0.0.1:5000/add/' + str(spisok)
                response = requests.post(url, data={}).json()['otvet']
    return response

@app.callback(
    Output('btn-generate', 'style'),
    Output('btn-remove-node', 'style'),
    Output('btn-nxt-trn', 'style'),
    Output('moving-side', 'children'),
    Output('moves-counter', 'children'),
    Output('input_countTurns', 'style'),
    Output('input_fora', 'style'),
    Output('pull-counter', 'children'),
    Output('pull-counter', 'style'),
    Output('btn-start', 'style'),
    Output('uploadDiv', 'style'),
    Output('input_countNodesVision', 'style'),
    Input('cytoscape-elements-callbacks', 'elements'),
    Input('btn-nxt-trn', 'n_clicks_timestamp'),
    Input('btn-reset', 'n_clicks_timestamp'),
)
def UPDT(cytoscape_elements_callbacks, btn_nxt_trn, btn_reset):
    global btn_generate_pressed, Text
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    while btn_generate_pressed == False:
        pass
    if 'btn-reset' in changed_id:
        btn_generate_pressed = False
        return dict(display='block'), dict(display='none'), dict(display='none'), '', '', dict(display='block'), dict(display='block'), '', dict(display='none'), dict(display='block'), dict(display='block'), dict(
            display='block')
    url = 'http://127.0.0.1:5000/info'
    response = requests.post(url, data={})
    print(response)
    if response.json()['score'] != None:
        return dict(display='none'), dict(display='none'), dict(display='none'), 'ПОБЕДА АТАКИ ' + str(response.json()['score']), 'Фора: ' + str(
            response.json()['fora']) + ' Ход: ' + str(response.json()['turn']) + '/' + str(
            response.json()['max_turns']), dict(display='none'), dict(display='none'), str(
            response.json()['pul']), dict(display='block'), dict(display='none'), dict(display='none'), dict(
            display='none')
    if response.json()['win_d'] == True:
        return dict(display='none'), dict(display='none'), dict(display='none'), 'ПОБЕДА ЗАЩИТЫ', 'Фора: ' + str(
            response.json()['fora']) + ' Ход: ' + str(response.json()['fora']) + '/' + str(
            response.json()['max_turns']), dict(display='none'), dict(display='none'), str(
            response.json()['pul']), dict(display='block'), dict(display='none'), dict(display='none'), dict(
            display='none')
    if response.json()['fora'] > 0:
        side = 'Ход атаки'
        return dict(display='none'), dict(display='block'), dict(display='none'), str(side), 'Фора: ' + str(
            response.json()['fora']) + ' Ход: ' + str(response.json()['turn']) + '/' + str(
            response.json()['max_turns']), dict(display='none'), dict(display='none'), str(
            response.json()['pul']), dict(display='block'), dict(display='none'), dict(display='none'), dict(
            display='none')
    elif response.json()['turn'] % 2 == 0:
        side = 'Ход защиты'
        return dict(display='none'), dict(display='none'), dict(display='block'), str(side), 'Фора: ' + str(
            response.json()['fora']) + ' Ход: ' + str(response.json()['turn']) + '/' + str(
            response.json()['max_turns']), dict(display='none'), dict(display='none'), str(
            response.json()['pul']), dict(display='block'), dict(display='none'), dict(display='none'), dict(
            display='none')
    else:
        side = 'Ход атаки'
        return dict(display='none'), dict(display='block'), dict(display='none'), str(side), 'Фора: ' + str(
            response.json()['fora']) + ' Ход: ' + str(response.json()['turn']) + '/' + str(
            response.json()['max_turns']), dict(display='none'), dict(display='none'), str(
            response.json()['pul']), dict(display='block'), dict(display='none'), dict(display='none'), dict(
            display='none')


@app.callback(Output('first', 'children'),
              Output('selectedText', 'children'),
              Output('last', 'children'),
              Input('btn-load', 'n_clicks_timestamp'),
              Input('btn-undo', 'n_clicks_timestamp'),
              Input('btn-redo', 'n_clicks_timestamp'),
              Input('btn-remove-node', 'n_clicks_timestamp'),
              Input('btn-nxt-trn', 'n_clicks_timestamp'),
              Input('input_countTurns', 'style'),
              )
def Notation(cl1, cl2, cl3, cl4, cl5, cl6):
    global Text
    response = requests.post('http://127.0.0.1:5000/get_history', data={}).json()
    Text = response['otvet']
    turn = response['turn']
    fist = ''
    selected1 = ''
    last = ''
    for i in Text:
        if int(i.split(' ')[2]) < turn:
            fist += i+'\n'
        elif int(i.split(' ')[2]) == turn:
            selected1 += i+'\n'
        else:
            last += i+'\n'
    if btn_generate_pressed == False:
        return '', '', ''
    return fist, selected1, last






@app.callback(
    Output('Helpers', 'style'),
    Output('HelpersStat','style'),
    Output('logo','style'),
    Input('btn-generate', 'n_clicks_timestamp'),
    Input('btn-start', 'n_clicks_timestamp'),
    Input('btn-load', 'n_clicks_timestamp'),
    Input('btn-reset', 'n_clicks_timestamp'))
def ShowStatAndHelpers(click, click1, click3, cl4):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if ('btn-generate' in changed_id) or ('btn-start' in changed_id) or ('btn-load' in changed_id):
        return dict(display='block') , dict(display='block'), dict(display='none')
    elif 'btn-reset' in changed_id:
        return dict(display='none'), dict(display='none'), {'width': '15%', 'position': 'absolute', 'z-index': '1000',
                                                            'margin-top': '5px'}
    return dict(display='none') , dict(display='none'), {'width': '15%','position':'absolute','z-index':'1000','margin-top':'5px' }


@app.callback(Output('cytoscape-elements-callbacks', 'stylesheet'),
              Input('cytoscape-elements-callbacks', 'selectedNodeData'),
              Input('btn-generate', 'n_clicks_timestamp'),
              Input('btn-start', 'n_clicks_timestamp'),
              Input('btn-remove-node', 'n_clicks_timestamp'),
              Input('btn-nxt-trn', 'n_clicks_timestamp'),
              Input('btn-load', 'n_clicks_timestamp'),
              Input("checklist", "value"))
def color_children(nodeData, click1, click2, click3, click4, click5, helpers_selected):
    global children_style_source, children_style_target, children_style, centr_stylesheet, clust_stylesheet, svyaz_stylesheet, checklist
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'checklist.value':
        checklist = ctx.triggered[0]['value']
    input_id = ctx.triggered[0]['value']
    if type(input_id) != list:
        return default_stylesheet + children_style_source + children_style_target + centr_stylesheet + clust_stylesheet + svyaz_stylesheet + children_style
    elif nodeData:
        children_style_source = [{
            'selector': 'edge[source = "{}"]'.format(nodeData[0]['id']),
            'style': {
                'line-color': 'orange'
            }
        }]
        children_style_target = [{
            'selector': 'edge[target = "{}"]'.format(nodeData[0]['id']),
            'style': {
                'line-color': 'orange'
            }
        }]
        if 'centr' in checklist:
            print('PIZDA')
            response = requests.post('http://127.0.0.1:5000/centrality_info', data={}).json()['otvet']
            centr = response
            print(centr)
            minim = min(centr.values())
            maxim = max(centr.values())
            summa = sum(centr.values())
            for i in centr.keys():
                temp = round(round((centr[i] / maxim) * 100) * 29 / 100)
                centr_stylesheet = centr_stylesheet + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'background-color': '{}'.format(gradient[temp]),
                    }
                }]
        else:
            centr_stylesheet = []

        if 'clust' in checklist:
            response = requests.post('http://127.0.0.1:5000/clust_info', data={}).json()['otvet']
            clust = response
            minim = min(clust.values())
            maxim = max(clust.values())
            summa = sum(clust.values())
            for i in clust.keys():
                temp = round(round((clust[i] / maxim) * 100) * 29 / 100)
                centr_stylesheet = centr_stylesheet + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'border-width': '{}px'.format(3),
                        'border-color': '{}'.format(gradient[temp])
                    }
                }]
        else:
            clust_stylesheet = []

        if 'svyaz' in checklist:
            response = requests.post('http://127.0.0.1:5000/svyaz_info', data={}).json()['otvet']
            svyazn = response
            vsego = len(svyazn.keys())
            minim = min(svyazn.values())
            maxim = max(svyazn.values())
            for i in svyazn.keys():
                temp = round(round((svyazn[i] / maxim) * 100) * 30 / 100) + 5 + minim
                svyaz_stylesheet = svyaz_stylesheet + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'width': '{}%'.format(temp),
                        'height': '{}%'.format(temp)
                    }
                }]
        else:
            svyaz_stylesheet = []

        if 'sharn' in checklist:
            response = requests.post('http://127.0.0.1:5000/sharn_info', data={}).json()['otvet']
            sharneers = response
            for i in sharneers:
                children_style = children_style + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'background-color': '#db002c'
                    }
                }]
        else:
            children_style = []
        return default_stylesheet + children_style_source + children_style_target + centr_stylesheet + clust_stylesheet + svyaz_stylesheet + children_style
    else:
        children_style_target = []
        children_style_source = []
        if 'centr' in checklist:
            print('PIZDA')
            response = requests.post('http://127.0.0.1:5000/centrality_info', data={}).json()['otvet']
            centr = response
            minim = min(centr.values())
            maxim = max(centr.values())
            summa = sum(centr.values())
            for i in centr.keys():
                temp = round(round((centr[i] / maxim) * 100) * 29 / 100)
                centr_stylesheet = centr_stylesheet + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'background-color': '{}'.format(gradient[temp]),
                    }
                }]
        else:
            centr_stylesheet = []

        if 'clust' in checklist:
            response = requests.post('http://127.0.0.1:5000/clust_info', data={}).json()['otvet']
            clust = response
            minim = min(clust.values())
            maxim = max(clust.values())
            summa = sum(clust.values())
            for i in clust.keys():
                temp = round(round((clust[i] / maxim) * 100) * 29 / 100)
                centr_stylesheet = centr_stylesheet + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'border-width': '{}px'.format(3),
                        'border-color': '{}'.format(gradient[temp])
                    }
                }]

        else:
            clust_stylesheet = []

        if 'svyaz' in checklist:
            response = requests.post('http://127.0.0.1:5000/svyaz_info', data={}).json()['otvet']
            svyazn = response
            vsego = len(svyazn.keys())
            minim = min(svyazn.values())
            maxim = max(svyazn.values())
            for i in svyazn.keys():
                temp = round(round((svyazn[i] / maxim) * 100) * 30 / 100) + 5 + minim
                svyaz_stylesheet = svyaz_stylesheet + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'width': '{}%'.format(temp),
                        'height': '{}%'.format(temp)
                    }
                }]
        else:
            svyaz_stylesheet = []

        if 'sharn' in checklist:
            response = requests.post('http://127.0.0.1:5000/sharn_info', data={}).json()['otvet']
            sharneers = response
            for i in sharneers:
                children_style = children_style + [{
                    'selector': 'node[id = "{}"]'.format(i),
                    'style': {
                        'background-color': '#db002c'
                    }
                }]
        else:
            children_style = []
        return default_stylesheet + children_style_source + children_style_target + centr_stylesheet + clust_stylesheet + svyaz_stylesheet + children_style

    return default_stylesheet


@app.callback(Output('graph', 'figure'),
              Output('average_min_max', 'children'),
              Output('graph', 'style'),
              Input("radio_stats", "value"),
              Input('btn-reset', 'n_clicks_timestamp'))
def Notation(stats_selected , cl2):
    global checklist_stats
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    ctx = dash.callback_context
    input_id = ctx.triggered[0]['value']
    if 'centr_stats' == input_id:
        response = requests.post('http://127.0.0.1:5000/centrality_info', data={}).json()['otvet']
        centr = response
        minim = min(centr.values())
        maxim = max(centr.values())
        abscyss = []
        delta = (maxim-minim)/10
        for i in range(10):
            abscyss.append(str(round(minim+delta*(i), 3))+'-'+str(round(minim+delta*(i+1), 3)))
        ordinat = [0] * 10
        for i in centr.keys():
            for j in range(10):
                if minim+delta*j <= centr[i] <= minim+delta*(j+1):
                    ordinat[j] = ordinat[j] + 1
        average = sum(centr.values()) / len(centr.keys())
        return {'data': [{'x': abscyss, 'y': ordinat, 'type': 'bar', 'name': 'Ценральность'}],
                'layout': {
                    'plot_bgcolor': '#ecf0f3',
                    'paper_bgcolor': '#ecf0f3',
                    'margin': dict(l=20, r=30, b=200, t=0),
                }
                }, 'Центральность\nСреднее: ' + str(round(average, 4)) + '\nМинимальное: ' + str(round(min(centr.values()), 4)) + '\nМаксимальное: ' + str(
            round(max(centr.values()), 4)), dict(display='block')

    if 'clust_stats' == input_id:
        response = requests.post('http://127.0.0.1:5000/clust_info', data={}).json()['otvet']
        clust = response
        minim = min(clust.values())
        maxim = max(clust.values())
        abscyss = []
        delta = (maxim - minim) / 10
        for i in range(10):
            abscyss.append(str(round(minim + delta * (i), 3)) + '-' + str(round(minim + delta * (i + 1), 3)))
        ordinat = [0] * 10
        for i in clust.keys():
            for j in range(10):
                if minim + delta * j <= clust[i] <= minim + delta * (j + 1):
                    ordinat[j] = ordinat[j] + 1
        average = sum(clust.values()) / len(clust.keys())
        return {'data': [{'x': abscyss, 'y': ordinat, 'type': 'bar', 'name': 'Ценральность'}],
                'layout': {
                    'plot_bgcolor': '#ecf0f3',
                    'paper_bgcolor': '#ecf0f3',
                    'margin': dict(l=20, r=30, b=200, t=0),
                }
                }, 'Кластерность\nСреднее: ' + str(round(average, 4)) + '\nМинимальное: ' + str(round(min(clust.values()), 4)) + '\nМаксимальное: ' + str(
            round(max(clust.values()), 4)), dict(display='block')

    if 'svyaz_stats' == input_id:
        response = requests.post('http://127.0.0.1:5000/svyaz_info', data={}).json()['otvet']
        svyaz = response
        abscyss = list(range(min(svyaz.values()), max(svyaz.values()) + 1))
        ordinat = [0] * (len(abscyss))
        for i in svyaz.keys():
            ordinat[abscyss.index(svyaz[i])] = ordinat[abscyss.index(svyaz[i])] + 1

        average = sum(svyaz.values()) / len(svyaz.keys())
        return {'data': [{'x': abscyss, 'y': ordinat, 'type': 'bar', 'name': 'Ценральность'}],
                'layout': {
                    'plot_bgcolor':'#ecf0f3',
                    'paper_bgcolor': '#ecf0f3',
                    'margin' : dict(l=20,r=30,b=200,t=0),
                }
                }, 'Связность\nСреднее: ' + str(average) + '\nМинимальное: ' + str(min(svyaz.values())) + '\nМаксимальное: ' + str(
            max(svyaz.values())), dict(display='block')

    if 'no_stats' == input_id:
        return {'data': []}, '', dict(display='none')

    if 'btn-reset' in changed_id:
        return {'data': []}, '', dict(display='none')

@app.callback(Output('btn-save', 'style'),
        Input('btn-save', 'n_clicks_timestamp'),
        Input('input_save-name', 'value'))
def SaveToFile(click, name):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-save' in changed_id:
        response = requests.post('http://127.0.0.1:5000/save/' + name, data={}).json()['otvet']
        return dict(display='block')
    return dict(display='block')



if __name__ == '__main__':
    app.run_server(debug=False)