import base64
import csv
import random
import time

from example.Network.functoins import *
import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import networkx as nx
from dash.dependencies import Input, Output, State
from fa2l import force_atlas2_layout

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


@app.callback(
    Output('cytoscape-elements-callbacks', 'elements'),
    Output('pull-counter', 'children'),
    Input('input_countNodes', 'value'),
    Input('input_links', 'value'),
    Input('btn-nxt-trn', 'n_clicks_timestamp'),
    Input('cytoscape-elements-callbacks', 'selectedNodeData'),
    Input('btn-generate', 'n_clicks_timestamp'),
    Input('btn-remove-node', 'n_clicks_timestamp'),
    Input('input_pulledges', 'value'),
    Input('btn-start', 'n_clicks_timestamp'),
    Input('upload-data', 'contents'),
    Input('btn-load', 'n_clicks_timestamp'),
    Input('input_save-name', 'value'),
    Input('btn-undo', 'n_clicks_timestamp'),
    Input('btn-redo', 'n_clicks_timestamp'),
    Input('btn-reset','n_clicks_timestamp'),
    State('cytoscape-elements-callbacks', 'elements')
)
def update_elements(count, links, btn_next, data, btn_remove, btn_generate, pull, btn_start, content, btn_load,
                    name, bnt_undo, btn_redo, elements, reset):
    global selected, node_count, global_turn, EndOfGame, provereno, \
        Pull, added, x, y, skip, start_ways, canFindSharneers, \
        loaded, nodes, edges, loaded_strings, pereschitanaFora, addedEdges, \
        turn_pereschitan, save_strings, global_turn, global_turn_flag, notation_flag, Fora, MaxTurns, MaxFora
    EndOfGame = False
    provereno = False
    skip = False
    canFindSharneers = False
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-generate' in changed_id:
        Pull = int(pull)
        nodes = []
        edges = []
        n_generation = int(count)
        node_count = n_generation
        G = nx.barabasi_albert_graph(int(n_generation), int(links))
        positions = force_atlas2_layout(G,
                                        iterations=100,
                                        pos_list=None,
                                        node_masses=None,
                                        outbound_attraction_distribution=False,
                                        lin_log_mode=False,
                                        prevent_overlapping=False,
                                        edge_weight_influence=1.0,

                                        jitter_tolerance=1.0,
                                        barnes_hut_optimize=True,
                                        barnes_hut_theta=0.8,

                                        scaling_ratio=30.0,
                                        strong_gravity_mode=False,
                                        multithread=False,
                                        gravity=1.0)
        for i in range(len(positions)):
            nodes.append({'data': {'id': i, 'label': i},
                          'position': {'x': positions[i][0], 'y': positions[i][1]}})
        for i in G.edges():
            edges.append({'data': {'source': i[0], 'target': i[1]}})
        print(positions)
        start_ways = check_ways(edges)
        canFindSharneers = True
        save_all()
        return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
    elif 'btn-reset' in changed_id:
        global MaxTurns,turn_interface,side,Fora,children_style_target,clust_stylesheet,centr_stylesheet,\
            children_style_source,children_style,svyaz_stylesheet,checklist,save_strings_stats
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
        checklist = []  # галочки для хелперов
        save_strings_stats = []  # сохранение для статистики
        MaxFora = 0

        return nodes+edges, ''
    elif 'btn-start' in changed_id:
        Pull = int(pull)
        G, node_count = CSV_to_NX(content, node_count)
        positions = force_atlas2_layout(G,
                                        iterations=1000,
                                        pos_list=None,
                                        node_masses=None,
                                        outbound_attraction_distribution=False,
                                        lin_log_mode=False,
                                        prevent_overlapping=False,
                                        edge_weight_influence=1.0,

                                        jitter_tolerance=1.0,
                                        barnes_hut_optimize=True,
                                        barnes_hut_theta=0.8,

                                        scaling_ratio=30.0,
                                        strong_gravity_mode=False,
                                        multithread=False,
                                        gravity=1.0)
        for i in range(len(positions)):
            nodes.append({'data': {'id': i, 'label': i},
                          'position': {'x': positions[i][0], 'y': positions[i][1]}})
        for i in G.edges():
            edges.append({'data': {'source': i[0], 'target': i[1]}})

        start_ways = check_ways(edges)
        canFindSharneers = True
        save_all()
        return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'

    elif 'btn-remove-node' in changed_id:
        notation_flag = False
        canFindSharneers = True
        if len(nodes) > 0 and int(selected) != added:
            c = 0
            for g in nodes:
                if g['data']['id'] == int(selected):
                    pos = nodes[c]
                    nodes.pop(c)
                c = c + 1
            removedEdges = []
            c = 0
            while c < len(edges):
                if (edges[c]['data']['source'] == int(selected)) or (edges[c]['data']['target'] == int(selected)):
                    removedEdges.append(edges[c])
                    edges.pop(c)
                else:
                    c = c + 1

            if CosarajuEndOfGame(nodes, edges) == True:
                provereno = True
                EndOfGame = True
                canFindSharneers = True
                while turn_pereschitan == False:
                    pass
                turn_pereschitan = False
                global_turn = global_turn + 1
                save_step('remove', selected, pos['position']['x'], pos['position']['y'], removedEdges, Pull, Fora)
                save_step_stats(edges)
                notation_flag = True
                return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
            else:
                provereno = True
                canFindSharneers = True
            while pereschitanaFora == False:
                pass
            pereschitanaFora = False
            if Fora <= 0:
                global_turn = global_turn + 1
                if global_turn == MaxTurns:
                    EndOfGame = True
                if Pull > 0:
                    if global_turn % 2 == (MaxFora % 2) or (MaxFora==0 and (global_turn % 2 == 1)):  # ход нечетный - защита
                        # сделать интерфейс для защиты
                        if EndOfGame != True:
                            next_node_idx = node_count
                            node_count = node_count + 1
                            added = next_node_idx
                            positions = {}
                            for i in nodes:
                                positions[i['data']['id']] = (i['position']['x'],i['position']['y'])
                            print(positions)
                            G = nx.Graph()
                            for edge in edges:
                                G.add_edge(edge['data']['source'], edge['data']['target'])
                            G.add_node(next_node_idx)
                            positions[next_node_idx] = (0,0)
                            positions2 = force_atlas2_layout(G , pos_list=positions,iterations=20,scaling_ratio=30.0)
                            print(positions2)
                            x = positions2[next_node_idx][0]
                            y = positions2[next_node_idx][1]
                            nodes.append({'data': {'id': next_node_idx, 'label': str(next_node_idx)},
                                          'position': {'x': positions2[next_node_idx][0], 'y': positions2[next_node_idx][1]}})
                        canFindSharneers = True
                        while turn_pereschitan == False:
                            pass
                        turn_pereschitan = False
                        save_step('remove', selected, pos['position']['x'], pos['position']['y'], removedEdges, Pull,
                                  Fora)
                        save_step_stats(edges)
                        notation_flag = True
                        return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
                else:
                    global_turn = global_turn + 1
                    canFindSharneers = True
                    while turn_pereschitan == False:
                        pass
                    turn_pereschitan = False
                    save_step('remove', selected, pos['position']['x'], pos['position']['y'], removedEdges, Pull, Fora)
                    save_step_stats(edges)
                    notation_flag = True
                    return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
            else:
                global_turn = global_turn + 1
            canFindSharneers = True
            while turn_pereschitan == False:
                pass
            turn_pereschitan = False
            save_step('remove', selected, pos['position']['x'], pos['position']['y'], removedEdges, Pull, Fora)
            save_step_stats(edges)
            notation_flag = True
            return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
        else:
            provereno = True
            skip = True
            canFindSharneers = True
            return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
    elif 'btn-nxt-trn' in changed_id:
        notation_flag = False
        global_turn = global_turn + 1
        canFindSharneers = True
        while turn_pereschitan == False:
            pass
        turn_pereschitan = False
        if global_turn == MaxTurns:
            EndOfGame = True
        save_step('add', added, x, y, addedEdges, Pull, Fora)
        save_step_stats(edges)
        notation_flag = True
        addedEdges = []
        return nodes+ edges, 'Осталось ' + str(Pull) + ' рёбер'

    elif 'btn-load' in changed_id:
        res = []
        save_strings = []
        file = open(name + '.csv')
        reader = csv.reader(file, delimiter=';')
        for line in reader:
            res.append(line)
            loadStrings(line)
        nodes, edges = load(res[0])
        start_ways = check_ways(edges)
        node_count = len(nodes)
        global_turn = 0
        loaded = True
        canFindSharneers = True
        return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
    elif 'btn-undo' in changed_id:
        global_turn_flag = False
        if (global_turn == (len(save_strings) - 1)) and (save_strings[global_turn][-1] != True):
            c = 0
            for g in nodes:
                if g['data']['id'] == added:
                    nodes.pop(c)
                    break
                c = c + 1
            c = 0
            while c < len(edges):
                if (edges[c]['data']['source'] == added) or (edges[c]['data']['target'] == added):
                    edges.pop(c)
                else:
                    c = c + 1
        if global_turn == 0:
            global_turn_flag = True
        elif (save_strings[global_turn][1] == 'remove'):
            move = save_strings[global_turn][2].split(':')
            node_count = node_count + 1
            nodes.append({'data': {'id': int(move[0]), 'label': move[0]},
                          'position': {'x': float(move[1]), 'y': float(move[2])}})
            for i in range(3, len(save_strings[global_turn]) - 3):
                edge = save_strings[global_turn][i].split(':')
                edges.append({'data': {'source': int(edge[0]), 'target': int(edge[1])}})
            Pull = save_strings[global_turn][-3]
            global_turn = global_turn - 1
            global_turn_flag = True
            return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'

        else:
            move = save_strings[global_turn][2].split(':')
            c = 0
            for g in nodes:
                if g['data']['id'] == int(move[0]):
                    nodes.pop(c)
                    break
                c = c + 1
            c = 0
            while c < len(edges):
                if (edges[c]['data']['source'] == int(move[0])) or (edges[c]['data']['target'] == int(move[0])):
                    edges.pop(c)
                else:
                    c = c + 1
            Pull = save_strings[global_turn][-3]
            global_turn = global_turn - 1
            global_turn_flag = True
            return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'


    elif 'btn-redo' in changed_id:
        global_turn_flag = False
        if ((global_turn + 1) == len(save_strings) - 1) and (save_strings[global_turn + 1][1] == 'remove') and (
                save_strings[global_turn + 1][-1] != True):
            next_node_idx = node_count
            node_count = node_count + 1
            added = next_node_idx
            x = len(nodes) * random.choice([-10, 10]) + random.randint(-6, 6)
            y = len(nodes) * random.choice([-10, 10]) + random.randint(-6, 6)
            nodes.append({'data': {'id': next_node_idx, 'label': str(next_node_idx)},
                          'position': {'x': x, 'y': y}})
        if (global_turn != len(save_strings) - 1):
            if (save_strings[global_turn + 1][1] == 'remove'):
                move = save_strings[global_turn + 1][2].split(':')
                c = 0
                for g in nodes:
                    if g['data']['id'] == int(move[0]):
                        nodes.pop(c)
                        break
                    c = c + 1
                c = 0
                while c < len(edges):
                    if (edges[c]['data']['source'] == int(move[0])) or (edges[c]['data']['target'] == int(move[0])):
                        edges.pop(c)
                    else:
                        c = c + 1
                Pull = int(save_strings[global_turn + 1][-3])
                global_turn = global_turn + 1
                global_turn_flag = True
                return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
            else:
                move = save_strings[global_turn + 1][2].split(':')
                node_count = node_count + 1
                nodes.append({'data': {'id': int(move[0]), 'label': move[0]},
                              'position': {'x': float(move[1]), 'y': float(move[2])}})
                for i in range(3, len(save_strings[global_turn + 1]) - 3):
                    edge = save_strings[global_turn + 1][i].split(':')
                    edges.append({'data': {'source': int(edge[0]), 'target': int(edge[1])}})
                Pull = int(save_strings[global_turn + 1][-3])
                global_turn = global_turn + 1
                global_turn_flag = True
                return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
        else:
            global_turn_flag = True
            return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
    else:
        if data:
            if len(data) == 2 and (global_turn % 2 == (MaxFora % 2) or (MaxFora==0 and (global_turn % 2 == 1))):  # если ход защищающегося
                src = int(data[0]['id'])
                tar = int(data[1]['id'])
                if (src == nodes[len(nodes) - 1]['data']['id'] or tar == nodes[len(nodes) - 1]['data']['id']) and (
                        Pull > 0):
                    addedEdges.append({'data': {'source': int(data[0]['id']), 'target': int(data[1]['id'])}})
                    edges.append({'data': {'source': int(data[0]['id']), 'target': int(data[1]['id'])}})
                    Pull = Pull - 1
                    return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'
            elif len(data) != 2:
                return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'

    canFindSharneers = True
    return nodes + edges, 'Осталось ' + str(Pull) + ' рёбер'


@app.callback(
    Output('btn-generate', 'style'),
    Output('btn-remove-node', 'style'),
    Output('btn-nxt-trn', 'style'),
    Output('moving-side', 'children'),
    Output('moves-counter', 'children'),
    Output('input_countTurns', 'style'),
    Output('input_fora', 'style'),
    Output('pull-counter', 'style'),
    Output('btn-start', 'style'),
    Output('uploadDiv', 'style'),
    Input('btn-generate', 'n_clicks_timestamp'),
    Input('btn-remove-node', 'n_clicks_timestamp'),
    Input('btn-nxt-trn', 'n_clicks_timestamp'),
    Input('input_countTurns', 'value'),
    Input('input_fora', 'value'),
    Input('btn-start', 'n_clicks_timestamp'),
    Input('btn-load', 'n_clicks_timestamp'),
    Input('btn-redo', 'n_clicks_timestamp'),
    Input('btn-undo', 'n_clicks_timestamp'),
    Input('btn-reset', 'n_clicks_timestamp'),
)
def UPDT(click1, click2, click3, maxturns, fora, click4, click5, click6, click7 , cl8):
    global turn_interface, side, MaxTurns, Fora, pereschitanaFora, turn_pereschitan, MaxFora
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-generate' in changed_id:
        MaxTurns = int(maxturns)
        Fora = int(fora)
        MaxFora = Fora
        return dict(display='none'), dict(display='block'), dict(display='none'), str(side), 'Фора ' + str(
            Fora) + ' ходов', dict(display='none'), dict(display='none'), dict(display='block'), dict(
            display='none'), dict(display='none')
    elif 'btn-reset' in changed_id:
        return dict(display='block'), dict(display='none'), dict(display='none'), '', '', dict(
            display='block'), dict(display='block'), dict(display='none'), dict(display='block'), dict(display='block')
    elif 'btn-start' in changed_id:
        MaxTurns = int(maxturns)
        Fora = int(fora)
        MaxFora = Fora
        return dict(display='none'), dict(display='block'), dict(display='none'), str(side), 'Фора ' + str(
            Fora) + ' ходов', dict(display='none'), dict(display='none'), dict(display='block'), dict(
            display='none'), dict(display='none')
    elif 'btn-remove-node' in changed_id:
        Fora = Fora - 1
        pereschitanaFora = True
        if Fora > 0:
            turn_pereschitan = True
            side = 'Ход атаки'
            while provereno == False:
                pass
            if skip == True:
                return dict(display='none'), dict(display='block'), dict(display='none'), str(side), str(
                    turn_interface + 1) + '/' + str(MaxTurns), dict(display='none'), dict(display='none'), dict(
                    display='block'), dict(display='none'), dict(display='none')
            if EndOfGame == True:
                won = check_winning(edges)
                return dict(display='none'), dict(display='none'), dict(
                    display='none'), 'Игра Окончена (победа атаки)\n' + str(won), '', dict(
                    display='none'), dict(display='none'), dict(display='block'), dict(display='none'), dict(
                    display='none')
            return dict(display='none'), dict(display='block'), dict(display='none'), str(side), 'Фора ' + str(
                Fora) + ' ходов', dict(display='none'), dict(display='none'), dict(display='block'), dict(
                display='none'), dict(display='none')
        turn_interface = turn_interface + 1
        turn_pereschitan = True

        if turn_interface + 1 > MaxTurns:
            return dict(display='none'), dict(display='none'), dict(
                display='none'), 'Игра Окончена (победа защиты)', '', dict(display='none'), dict(display='none'), dict(
                display='block'), dict(display='none'), dict(display='none')

        while provereno == False:
            pass
        if skip == True:
            side = 'Ход атаки'
            turn_interface = turn_interface - 1
            return dict(display='none'), dict(display='block'), dict(display='none'), str(side), str(
                turn_interface + 1) + '/' + str(MaxTurns), dict(display='none'), dict(display='none'), dict(
                display='block'), dict(display='none'), dict(display='none')
        if EndOfGame == True:
            won = check_winning(edges)
            return dict(display='none'), dict(display='none'), dict(
                display='none'), 'Игра Окончена (победа атаки)\n' + str(won), '', dict(
                display='none'), dict(display='none'), dict(display='block'), dict(display='none'), dict(display='none')
        side = 'Ход защиты'
        if Pull <= 0:
            turn_interface = turn_interface + 1
            turn_pereschitan = True
            if turn_interface + 1 > MaxTurns:
                return dict(display='none'), dict(display='none'), dict(
                    display='none'), 'Игра Окончена (победа защиты)', '', dict(display='none'), dict(
                    display='none'), dict(display='block'), dict(display='none'), dict(display='none')
            side = 'Ход атаки'
            return dict(display='none'), dict(display='block'), dict(display='none'), str(side), str(
                turn_interface + 1) + '/' + str(MaxTurns), dict(display='none'), dict(display='none'), dict(
                display='block'), dict(display='none'), dict(display='none')
        return dict(display='none'), dict(display='none'), dict(display='block'), str(side), str(
            turn_interface + 1) + '/' + str(MaxTurns), dict(display='none'), dict(display='none'), dict(
            display='block'), dict(display='none'), dict(display='none')
    elif 'btn-nxt-trn' in changed_id:
        turn_interface = turn_interface + 1
        turn_pereschitan = True
        if turn_interface + 1 > MaxTurns:
            return dict(display='none'), dict(display='none'), dict(
                display='none'), 'Игра Окончена (победа защиты)', '', dict(display='none'), dict(display='none'), dict(
                display='block'), dict(display='none'), dict(display='none')
        side = 'Ход атаки'
        return dict(display='none'), dict(display='block'), dict(display='none'), str(side), str(
            turn_interface + 1) + '/' + str(MaxTurns), dict(display='none'), dict(display='none'), dict(
            display='block'), dict(display='none'), dict(display='none')
    elif 'btn-load' in changed_id:
        while loaded == False:
            pass
        return dict(display='none'), dict(display='none'), dict(display='none'), str(side), 'Фора ' + str(
            Fora) + ' ходов', dict(display='none'), dict(display='none'), dict(display='block'), dict(
            display='none'), dict(display='none')
    elif 'btn-redo' in changed_id:
        while global_turn_flag == False:
            pass
        if (global_turn == len(save_strings) - 1) and (save_strings[global_turn][-1] != True):
            if (save_strings[global_turn][1] == 'add'):
                return dict(display='none'), dict(display='block'), dict(display='none'), 'Ход атаки', str(
                    int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                       dict(display='none'), dict(display='none'), dict(display='block'), dict(
                    display='none'), dict(display='none')
            else:
                return dict(display='none'), dict(display='none'), dict(display='block'), 'Ход защиты', str(
                    int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                       dict(display='none'), dict(display='none'), dict(display='none'), dict(
                    display='none'), dict(display='none')
        elif (save_strings[global_turn][-1] == True):
            return dict(display='none'), dict(display='none'), dict(display='none'), 'Игра окончена', str(
                int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                   dict(display='none'), dict(display='none'), dict(display='none'), dict(
                display='none'), dict(display='none')
        elif (save_strings[global_turn][1] == 'add'):
            return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход атаки', str(
                int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                   dict(display='none'), dict(display='none'), dict(display='block'), dict(display='none'), dict(
                display='none')
        else:
            if (int(save_strings[global_turn][-2]) <= 0):
                return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход защиты', str(
                    int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                       dict(display='none'), dict(display='none'), dict(display='block'), dict(display='none'), dict(
                    display='none')
            else:
                return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход атаки', 'Фора ' + str(
                    save_strings[global_turn][-2]) + ' ходов', \
                       dict(display='none'), dict(display='none'), dict(display='block'), dict(display='none'), dict(
                    display='none')

    elif 'btn-undo' in changed_id:
        while global_turn_flag == False:
            pass
        if (global_turn == 0):
            if (int(save_strings[global_turn][-2]) <= 0):
                return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход атаки', str(
                    int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                       dict(display='none'), dict(display='none'), dict(display='block'), dict(
                    display='none'), dict(display='none')
            else:
                return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход атаки', 'Фора ' + \
                       str(save_strings[global_turn][-2]) + ' ходов', \
                       dict(display='none'), dict(display='none'), dict(display='block'), dict(
                    display='none'), dict(display='none')
        elif (save_strings[global_turn][1] == 'add'):
            return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход атаки', str(
                int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                   dict(display='none'), dict(display='none'), dict(display='block'), dict(
                display='none'), dict(display='none')
        else:
            if (int(save_strings[global_turn][-2]) <= 0):
                return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход защиты', str(
                    int(save_strings[global_turn][0]) + 1) + '/' + str(MaxTurns), \
                       dict(display='none'), dict(display='none'), dict(display='block'), dict(
                    display='none'), dict(display='none')
            else:
                return dict(display='none'), dict(display='none'), dict(display='none'), 'Ход атаки', 'Фора ' + \
                       str(save_strings[global_turn][-2]) + ' ходов', \
                       dict(display='none'), dict(display='none'), dict(display='block'), dict(
                    display='none'), dict(display='none')
    else:
        return dict(display='block'), dict(display='none'), dict(display='none'), '', '', dict(
            display='block'), dict(display='block'), dict(display='none'), dict(display='block'), dict(display='block')


@app.callback(
    Output('input_countNodesVision', 'style'),
    Input('btn-generate', 'n_clicks_timestamp'),
    Input('btn-start', 'n_clicks_timestamp'),
    Input('btn-load', 'n_clicks_timestamp'),
    Input('btn-reset', 'n_clicks_timestamp'))
def HideInputs(click, click1, click3, cl4):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if ('btn-generate' in changed_id) or ('btn-start' in changed_id) or ('btn-load' in changed_id):
        return dict(display='none')
    elif 'btn-reset' in changed_id:
        return dict(display='block')
    return dict(display='block')


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
            centr = find_centr(edges)
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
            clust = find_clust(edges)
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
            svyazn = find_svyazn(edges)
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
            sharneers = find_sharneers(edges)
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
            centr = find_centr(edges)
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
            clust = find_clust(edges)
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
            svyazn = find_svyazn(edges)
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
            sharneers = find_sharneers(edges)
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


def save_all():
    step_string = []
    step_string.append(turn_interface)
    for i in nodes:
        step_string.append(str(i['data']['id']) + ':' + str(i['position']['x']) + ':' + str(i['position']['y']))
    for i in edges:
        step_string.append(str(i['data']['source']) + ':' + str(i['data']['target']))
    step_string.append(str(MaxTurns))
    step_string.append(str(Pull))
    step_string.append(str(Fora))
    step_string.append(side)
    save_strings.append(step_string)


def save_step(action, node, x, y, edgeses, pull, fora):
    global turn_interface
    turn_interface = global_turn
    step_string = []
    step_string.append(turn_interface)
    step_string.append(action)
    step_string.append(str(node) + ':' + str(x) + ':' + str(y))
    for i in edgeses:
        step_string.append(str(i['data']['source']) + ':' + str(i['data']['target']))
    step_string.append(pull)
    step_string.append(fora)
    step_string.append(EndOfGame)
    save_strings.append(step_string)


@app.callback(
    Output('btn-save', 'style'),
    Input('btn-save', 'n_clicks_timestamp'),
    Input('input_save-name', 'value'))
def SaveToFile(click, name):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-save' in changed_id:
        with open(name + '.csv', "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in save_strings:
                writer.writerow(line)
        with open(name + '_stats.csv', "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in save_strings_stats:
                writer.writerow(line)

            time.sleep(2)
        return dict(display='block')
    return dict(display='block')


@app.callback(Output('first', 'children'),
              Output('selectedText', 'children'),
              Output('last', 'children'),
              Input('btn-load', 'n_clicks_timestamp'),
              Input('btn-undo', 'n_clicks_timestamp'),
              Input('btn-redo', 'n_clicks_timestamp'),
              Input('btn-remove-node', 'n_clicks_timestamp'),
              Input('btn-nxt-trn', 'n_clicks_timestamp'), )
def Notation(cl1, cl2, cl3, cl4, cl5):
    global global_turn
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-load' in changed_id:
        while loaded == False:
            pass
        Text = ''
        for i in range(1, len(save_strings)):
            if save_strings[i][1] == 'remove':
                k = '🗡'
            else:
                k = '⨮'
            Text += 'Ход №' + str(int(save_strings[i][0])) + k + str(
                save_strings[i][2].split(':')[0]) + '\n'
        return '', '', Text
    elif ('btn-nxt-trn' in changed_id) or ('btn-remove-node' in changed_id):
        while notation_flag == False:
            pass
        if (global_turn == 0):
            first = ''
            selected = ''
            last = ''
            for i in range(1, len(save_strings)):
                if save_strings[i][1] == 'remove':
                    k = '🗡'
                else:
                    k = '⨮'
                last += 'Ход №' + str(int(save_strings[i][0])) + k + str(
                    save_strings[i][2].split(':')[0]) + '\n'
            return first, selected, last
        else:
            if save_strings[global_turn][1] == 'remove':
                k = '🗡'
            else:
                k = '⨮'
            selected = 'Ход №' + str(int(save_strings[global_turn][0])) + k + str(
                save_strings[global_turn][2].split(':')[0]) + '\n'
            first = ''
            last = ''
            for i in range(1, global_turn):
                if save_strings[i][1] == 'remove':
                    k = '🗡'
                else:
                    k = '⨮'
                first += 'Ход №' + str(int(save_strings[i][0])) + k + str(
                    save_strings[i][2].split(':')[0]) + '\n'
            for i in range(global_turn + 1, len(save_strings)):
                if save_strings[i][1] == 'remove':
                    k = '🗡'
                else:
                    k = '⨮'
                last += 'Ход №' + str(int(save_strings[i][0])) + k + str(
                    save_strings[i][2].split(':')[0]) + '\n'
            return first, selected, last
    elif ('btn-undo' in changed_id) or ('btn-redo' in changed_id):
        while global_turn_flag == False:
            pass
        if (global_turn == 0):
            first = ''
            selected = ''
            last = ''
            for i in range(1, len(save_strings)):
                if save_strings[i][1] == 'remove':
                    k = '🗡'
                else:
                    k = '⨮'
                last += 'Ход №' + str(int(save_strings[i][0])) + k + str(
                    save_strings[i][2].split(':')[0]) + '\n'
            return first, selected, last
        else:
            if save_strings[global_turn][1] == 'remove':
                k = '🗡'
            else:
                k = '⨮'
            selected = 'Ход №' + str(int(save_strings[global_turn][0])) + k + str(
                save_strings[global_turn][2].split(':')[0]) + '\n'
            first = ''
            last = ''
            for i in range(1, global_turn):
                if save_strings[i][1] == 'remove':
                    k = '🗡'
                else:
                    k = '⨮'
                first += 'Ход №' + str(int(save_strings[i][0])) + k + str(
                    save_strings[i][2].split(':')[0]) + '\n'
            for i in range(global_turn + 1, len(save_strings)):
                if save_strings[i][1] == 'remove':
                    k = '🗡'
                else:
                    k = '⨮'
                last += 'Ход №' + str(int(save_strings[i][0])) + k + str(
                    save_strings[i][2].split(':')[0]) + '\n'
            return first, selected, last
    else:
        return '', '', ''


def load(string):
    global turn_interface, MaxTurns, Pull, Fora, side, save_strings
    turn_interface = int(string[0])
    nodes = []
    edges = []
    i = 1
    while ':' in string[i]:
        temp = string[i].split(':')
        if len(temp) == 3:
            nodes.append({'data': {'id': int(temp[0]), 'label': int(temp[0])},
                          'position': {'x': float(temp[1]), 'y': float(temp[2])}})
        else:
            edges.append({'data': {'source': int(temp[0]), 'target': int(temp[1])}})
        i = i + 1
    MaxTurns = int(string[i])
    i = i + 1
    Pull = int(string[i])
    i = i + 1
    Fora = int(string[i])
    i = i + 1
    side = string[i]
    return nodes, edges

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


def loadStrings(string):
    save_strings.append(string)


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
    if not nodes:
        return {'data': []}, '', dict(display='none')
    if 'centr_stats' == input_id:
        centr = find_centr(edges)
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
        clust = find_clust(edges)
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
        svyaz = find_svyazn(edges)
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

def save_step_stats(edges):
    centr = find_centr(edges)
    centr1 = {}
    for i in sorted(centr):
        centr1[i] = centr[i]
    clust = find_clust(edges)
    clust1 = {}
    for i in sorted(clust):
        clust1[i] = clust[i]
    svyazn = find_svyazn(edges)
    svyazn1 = {}
    for i in sorted(svyazn):
        svyazn1[i] = svyazn[i]
    string_stats = ['Centrality', centr1, 'Cluster', clust1, 'Connectivity', svyazn1]
    save_strings_stats.append(string_stats)

if __name__ == '__main__':
    app.run_server(debug=False)