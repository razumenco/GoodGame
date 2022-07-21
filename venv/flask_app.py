from flask import Flask
from flask import request
import networkx as nx
from functions import *
from fa2l import force_atlas2_layout
import json
import csv
import copy


class Game(object):
    """docstring"""
    def __init__(self, lenght, st_sv, max_turns, fora, pul):
        """Constructor"""
        self.lenght = lenght
        self.st_sv = st_sv
        self.max_turns = max_turns
        self.fora = fora
        self.pul = pul
        self.nodes = []
        self.edges = []
        self.turn = 1
        self.win_a = False
        self.win_a_score = None
        self.win_d = False
        self.step_strings = []
        self.added = 0
        self.addedEdges = []
        self.x_new = 0
        self.y_new = 0
        self.history_index = 0
        if self.st_sv == -1:
            self.CSV_graph(lenght)
        else:
            self.gen_graph() #Генерация графа


    def gen_graph(self):
        self.G = nx.barabasi_albert_graph(self.lenght, self.st_sv)
        self.nodes = []
        self.edges = []
        #100 инетраций было (не забудь убрать!!!!!!!!!!)
        self.positions = force_atlas2_layout(self.G,
                                        iterations=150,
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
        for i in range(len(self.positions)):
            self.nodes.append({'data': {'id': i, 'label': i},
                          'position': {'x': self.positions[i][0], 'y': self.positions[i][1]}})
        for i in self.G.edges():
            self.edges.append({'data': {'source': i[0], 'target': i[1]}})
        self.save_all()

    def CSV_graph(self, content):
        content = content[2:len(content) - 2].split('", "')
        node_count = 0
        self.G = nx.Graph()
        for i in content:
            node_count = node_count + 1
            line = i.split(';')
            for j in line:
                if line[0] != j:
                    self.G.add_edge(int(line[0]), int(j), attr_dict=None)
        self.nodes = []
        self.edges = []
        #print(self.nodes)
        #print(self.edges)
        self.positions = force_atlas2_layout(self.G,
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
        for i in range(len(self.positions)):
            self.nodes.append({'data': {'id': i, 'label': i},
                               'position': {'x': self.positions[i][0], 'y': self.positions[i][1]}})
        for i in self.G.edges():
            self.edges.append({'data': {'source': i[0], 'target': i[1]}})
        self.save_all()

    def delete(self, v):
        self.G.remove_node(v)
        if len(self.nodes) > 0:
            c = 0
            for g in self.nodes:
                if g['data']['id'] == int(v):
                    pos = self.nodes[c]
                    self.nodes.pop(c)
                c = c + 1
            removedEdges = []
            c = 0
            while c < len(self.edges):
                if (self.edges[c]['data']['source'] == int(v)) or (self.edges[c]['data']['target'] == int(v)):
                    removedEdges.append(self.edges[c])
                    self.edges.pop(c)
                else:
                    c = c + 1
        #print('------------------------------')
        #print(removedEdges)
        self.save_step('remove', v, self.positions[v][0], self.positions[v][1], removedEdges, self.pul, self.fora-1)
        #print(self.step_strings)
        self.history_index = self.history_index + 1
        return True

    def delete_undo(self, v):
        self.G.remove_node(v)
        if len(self.nodes) > 0:
            c = 0
            for g in self.nodes:
                if g['data']['id'] == int(v):
                    pos = self.nodes[c]
                    self.nodes.pop(c)
                c = c + 1
            removedEdges = []
            c = 0
            while c < len(self.edges):
                if (self.edges[c]['data']['source'] == int(v)) or (self.edges[c]['data']['target'] == int(v)):
                    removedEdges.append(self.edges[c])
                    self.edges.pop(c)
                else:
                    c = c + 1
        return True

    def add_edges(self, spisok, new_node):
        print(spisok)
        if not spisok.isalnum():
            spisok = spisok[1:len(spisok) - 1].split(',')
        else:
            spisok = [int(spisok)]

        # if len(spisok) > self.pul:
        #     return False
        for node in spisok:
            if self.pul == 0:
                return False
            print(node)
            self.G.add_edge(int(node), new_node)
            #print(new_node, "    ", node)
            if new_node != int(node):
                self.added = new_node
                self.edges.append({'data': {'source': new_node, 'target': int(node)}})
                self.addedEdges.append({'data': {'source': new_node, 'target': int(node)}})
                self.pul = self.pul - 1
        return True

    def make_turn(self, act, nodes):
        if self.fora > 0:
            if act == 'a':
                if not self.delete(nodes):
                    return False
                if self.check_winning_a():
                    self.win_a = True
                    temp = self.winning()
                    self.win_a_score = temp
                    return temp
                self.fora = self.fora - 1
                if self.fora == 0:
                    self.turn = self.turn + 1
                    self.G.add_node(max(self.G.nodes()) + 1)
                    self.x_new = random.randint(0, 10)
                    self.y_new = random.randint(0, 10)
                    self.positions[max(self.G.nodes())] = self.x_new, self.y_new
                    self.nodes.append({'data': {'id': max(self.G.nodes()), 'label': max(self.G.nodes())},
                                       'position': {'x': self.x_new, 'y': self.y_new}})


                return True
            else:
                return False
        elif self.turn % 2 == 1:
            if act == 'a':
                if not self.delete(nodes):
                    return False
                #print(self.G.nodes())
                #print(self.G.edges())
                if self.check_winning_a():
                    #print('win a')
                    self.win_a = True
                    temp = self.winning()
                    self.win_a_score = temp
                    return temp
                self.turn = self.turn + 1
                if self.pul != 0:
                    self.G.add_node(max(self.G.nodes())+1)
                    self.x_new = random.randint(0, 10)
                    self.y_new = random.randint(0, 10)
                    self.positions[max(self.G.nodes())] = self.x_new, self.y_new
                    self.nodes.append({'data': {'id': max(self.G.nodes()) , 'label': max(self.G.nodes())},
                              'position': {'x': self.x_new, 'y': self.y_new}})
                return True
            else:
                return False
        elif self.turn % 2 == 0:
            if act == 'd':
                self.add_edges(nodes, max(self.G.nodes()))
                return True
            else:
                return False

    def check_winning_a(self):
        if nx.is_connected(self.G):
            return False
        else:
            return True

    def winning(self):
        graph = nx.Graph()
        for edge in self.G.edges():
            #print(edge)
            graph.add_edge(edge[0], edge[1])
        graphConnections = list(nx.connected_components(graph))
        intactness = 0
        #print(len(graph.nodes()))
        for i in range(len(graphConnections)):
            #print(intactness)
            nowGraph = nx.Graph()
            nowGraph.add_edges_from(graph.edges(graphConnections[i]))
            if len(nowGraph.nodes()) == 0:
                nowGraphNodes = 1
            else:
                nowGraphNodes = len(nowGraph.nodes())
            for j in range(i + 1, len(graphConnections)):
                currentGraph = nx.Graph()
                currentGraph.add_edges_from(graph.edges(graphConnections[j]))
                if len(currentGraph.nodes()) == 0:
                    currentGraphNodes = 1
                else:
                    currentGraphNodes = len(currentGraph.nodes())
                intactness += currentGraphNodes * nowGraphNodes * 2
                #print('fsdfsdfs' + str(currentGraphNodes))
            #print(nowGraphNodes)
        #print('==============================', len(graph.nodes()))
        self.win_a_score = 1 - intactness / (len(graph.nodes()) ** 2)
        return 1 - intactness / (len(graph.nodes()) ** 2)

    def check_winning_d(self):
        #print(str(self.turn) + ' ' + str(self.max_turns))
        if self.turn > self.max_turns:
            return True
        else:
            return False

    def get_centrality_info(self):
        return nx.betweenness_centrality(self.G)

    def get_clust_info(self):
        return nx.clustering(self.G)

    def get_svyaz_info(self):
        svyazn = {}
        for node in self.G.nodes():
            svyazn[node] = len(self.G.neighbors(node))
        return svyazn

    def get_sharn_info(self):
        sharneers = []
        if not nx.is_connected(self.G):
            return []
        ##print(list(nx.articulation_points(G)))
        # if len(list(nx.all_node_cuts(G))[0]) >= 2:
        #     return []
        for i in list(nx.articulation_points(self.G)):
            sharneers.append(i)
        return sharneers

    def save_step(self, action, node, x, y, edgeses, pull, fora):
        turn_interface = self.turn - 1
        step_string = []
        if action == "remove":
            turn_interface = turn_interface + 1
        step_string.append(turn_interface)
        step_string.append(action)
        step_string.append(str(node) + ':' + str(x) + ':' + str(y))
        for i in edgeses:
            step_string.append(str(i['data']['source']) + ':' + str(i['data']['target']))
        step_string.append(self.pul)
        step_string.append(self.fora)
        step_string.append(self.check_winning_a() or self.check_winning_d())
        self.step_strings.append(step_string)

    def save_all(self):
        step_string = []
        step_string.append(self.turn-1)
        for i in self.nodes:
            step_string.append(str(i['data']['id']) + ':' + str(i['position']['x']) + ':' + str(i['position']['y']))
        for i in self.edges:
            step_string.append(str(i['data']['source']) + ':' + str(i['data']['target']))
        step_string.append(str(self.max_turns))
        step_string.append(str(self.pul))
        step_string.append(str(self.fora))
        step_string.append('aaa')
        self.step_strings.append(step_string)

    def undo(self):
        if self.history_index + 1 == 1:
            return True
        string = self.step_strings[self.history_index]
        if string[1] == 'remove':
            #если удалили, то добавляем
            self.G.add_node(int(string[2].split(':')[0]))
            self.nodes.append({'data': {'id': int(string[2].split(':')[0]), 'label': int(string[2].split(':')[0])},
                               'position': {'x': float(string[2].split(':')[1]), 'y': float(string[2].split(':')[2])}})
            spisok = []
            spisok1 = string[3:len(string)-3]
            for element in spisok1:
                spisok.append(int(element.split(':')[0]))
                spisok.append(int(element.split(':')[1]))
            for i in spisok:
                self.add_edges(str([i]), int(string[2].split(':')[0]))
            #print('turn ',self.turn)
            #print('len ', len(self.step_strings))
            if self.history_index + 1 == len(self.step_strings) and string[len(string)-1] == False:
                self.delete_undo(max(self.G.nodes()))
            self.pul = int(string[len(string)-3])
            self.fora = int(string[len(string)-2])
            self.turn = int(self.step_strings[self.history_index][0])
            self.history_index = self.history_index - 1
        elif string[1] == 'add':
            #если добавили, то удаляем
            self.delete_undo(int(string[2].split(':')[0]))
            self.pul = int(self.step_strings[self.history_index-1][len(self.step_strings[self.history_index-1]) - 3])
            self.fora = int(self.step_strings[self.history_index-1][len(self.step_strings[self.history_index-1]) - 2])
            self.turn = int(self.step_strings[self.history_index][0])
            self.history_index = self.history_index - 1

    def redo(self):
        if self.history_index + 1 == len(self.step_strings):
            #print('aaaaaaaaaaaaaaaaaaaaaaaa')
            return True
        #print('bbbbbbbbbbbbbbbbbbbbbb')
        string = self.step_strings[self.history_index+1]
        if string[1] == 'remove':
            #если удалили, то удаляем
            self.delete_undo(int(string[2].split(':')[0]))
            self.pul = int(string[len(string) - 3])
            self.fora = int(string[len(string) - 2])
            #print("------------------------------")
            #for i in self.step_strings:
                #print("Info: full-string=", i)
            #print("------------------------------")
            #print("Info: string=", self.step_strings[self.history_index+1], ' ---- history index=', self.history_index)
            #self.turn = int(self.step_strings[self.history_index+2][0])
            if self.history_index+2 < len(self.step_strings):
                self.turn = int(self.step_strings[self.history_index+2][0])
            else:
                self.turn = self.turn+1
            self.history_index = self.history_index + 1
        elif string[1] == 'add':
            #если добавили, то добавляем
            self.G.add_node(int(string[2].split(':')[0]))
            self.nodes.append({'data': {'id': int(string[2].split(':')[0]), 'label': int(string[2].split(':')[0])},
                               'position': {'x': float(string[2].split(':')[1]), 'y': float(string[2].split(':')[2])}})
            spisok = []
            spisok1 = string[3:len(string) - 3]
            for element in spisok1:
                spisok.append(int(element.split(':')[0]))
                spisok.append(int(element.split(':')[1]))
            for i in spisok:
                self.add_edges(str([i]), int(string[2].split(':')[0]))
            self.pul = int(string[len(string) - 3])
            self.fora = int(string[len(string) - 2])
            #print("------------------------------")
            #for i in self.step_strings:
                #print("Info: full-string=", i)
            #print("------------------------------")
            #print("Info: string=", self.step_strings[self.history_index + 1], ' ---- history index=', self.history_index)
            #print("Info: index=",self.history_index, '  len=',len(self.step_strings))
            if self.history_index+2 < len(self.step_strings):
                self.turn = int(self.step_strings[self.history_index+2][0])
            else:
                self.turn = self.turn+1
            self.history_index = self.history_index + 1



global game

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/start/<len>/<links>/<max_turns>/<fora>/<pul>', methods=['POST', 'GET'])
def start(len, links, max_turns, fora, pul):
    global game
    error = None
    game = Game(int(len), int(links), int(max_turns), int(fora), int(pul))
    #print(game.G.nodes())
    #print(game.G.edges())
    return {'otvet' : game.nodes + game.edges}

@app.route('/importCSV/<max_turns>/<fora>/<pul>', methods=['POST', 'GET'])
def importCSV(max_turns, fora, pul):
    global game
    error = None
    #print(request.form.get('content'))
    game = Game(request.form.get('content'), -1, int(max_turns), int(fora), int(pul))
    #print(game.G.nodes())
    #print(game.G.edges())
    return {'otvet' : game.nodes + game.edges}

@app.route('/most_svyaz', methods=['POST', 'GET'])
def most_svyaz():
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    max_sv = 0
    versh = -1
    for node in game.G.nodes():
        if len(game.G.neighbors(node)) > max_sv:
            max_sv = len(game.G.neighbors(node))
            versh = node
    return {'otvet' : versh}

@app.route('/most_centr', methods=['POST', 'GET'])
def most_centr():
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    versh = -1
    centr = nx.betweenness_centrality(game.G)
    centr = list(dict(sorted(centr.items(), key=lambda item: item[1])))
    versh = int(centr[len(centr)-1])
    return {'otvet' : versh}

@app.route('/most_clust', methods=['POST', 'GET'])
def most_clust():
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    versh = -1
    clust = nx.clustering(game.G)
    clust = list(dict(sorted(clust.items(), key=lambda item: item[1])))
    versh = int(clust[len(clust)-1])
    return {'otvet' : versh}



@app.route('/spisok_nodes', methods=['POST', 'GET'])
def spisok_nodes():
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    return {'otvet' : game.G.nodes()}

@app.route('/delete/<node>', methods=['POST', 'GET'])
def delete(node):
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    score = game.make_turn('a', int(node))
    if game.check_winning_d():
        game.win_d = True
    if type(score) == float:
        return {'otvet' : game.nodes + game.edges,
                'score' : score}
    elif score == True:
        return {'otvet' : game.nodes + game.edges}
    else:
        return {'otvet' : 'Error'}

@app.route('/add/<nodes>', methods=['POST', 'GET'])
def add(nodes):
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    otvet = game.make_turn('d', nodes)
    if game.check_winning_d():
        game.win_d = True
    if otvet == 'Defense win':
        return {'otvet': otvet}
    elif otvet == True:
        return {'otvet' : game.nodes + game.edges}
    else:
        return {'otvet' : 'Error'}


@app.route('/can_attack', methods=['POST', 'GET'])
def can_attack():
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    if game.win_d == True:
        return {'otvet' : 'End'}
    if (game.fora > 0 or game.turn % 2 == 1):
        if game.win_d == False:
            return {'otvet' : 'True'}
        else:
            return {'otvet' : 'End'}
    else:
        return {'otvet' : 'False'}

@app.route('/can_defend', methods=['POST', 'GET'])
def can_defend():
    global game
    error = None
    # `request.method`: доступ к HTTP-методу
    #print(game.fora)
    #print(game.turn)
    if game.win_a == True:
        return {'otvet' : 'End'}
    if game.fora == 0 and game.turn % 2 == 0:
        #print(game.win_a)
        if game.win_a == False and game.win_d == False:
            return {'otvet' : 'True'}
        elif game.win_a == True and game.win_d == False:
            return {'otvet' : 'End'}
        elif game.win_a == False and game.win_d == True:
            return {'otvet' : 'Win'}
    else:
        return {'otvet' : 'False'}

@app.route('/info', methods=['POST', 'GET'])
def info():
    global game
    error = None
    if game.check_winning_d():
        game.win_d = True
    return {'fora' : game.fora,
            'max_turns' : game.max_turns,
            'pul' : game.pul,
            'turn' : game.turn,
            'score' : game.win_a_score,
            'win_d' : game.win_d
            }

@app.route('/next_turn', methods=['POST', 'GET'])
def next_turn():
    global game
    error = None
    game.turn = game.turn + 1
    game.save_step('add', game.added, game.x_new, game.y_new, game.addedEdges, game.pul, game.fora)
    game.history_index = game.history_index + 1
    #print('++++++++++++++++++++++++++')
    #print(game.addedEdges)
    game.addedEdges = []
    return {'otvet' : game.nodes + game.edges}

@app.route('/centrality_info', methods=['POST', 'GET'])
def centrality_info():
    global game
    error = None
    otvet = game.get_centrality_info()
    #print(otvet)
    return {'otvet' : otvet}

@app.route('/clust_info', methods=['POST', 'GET'])
def clust_info():
    global game
    error = None
    otvet = game.get_clust_info()
    #print(otvet)
    return {'otvet' : otvet}

@app.route('/svyaz_info', methods=['POST', 'GET'])
def svyaz_info():
    global game
    error = None
    otvet = game.get_svyaz_info()
    #print(otvet)
    return {'otvet' : otvet}

@app.route('/sharn_info', methods=['POST', 'GET'])
def sharn_info():
    global game
    error = None
    otvet = game.get_sharn_info()
    #print(otvet)
    return {'otvet' : otvet}

@app.route('/save/<name>', methods=['POST', 'GET'])
def save(name):
    with open(name + '.csv', "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in game.step_strings:
                writer.writerow(line)
    return {'otvet' : True}

@app.route('/undo', methods=['POST', 'GET'])
def undo():
    game.undo()
    return {'otvet' : game.nodes + game.edges}

@app.route('/redo', methods=['POST', 'GET'])
def redo():
    game.redo()
    return {'otvet' : game.nodes + game.edges}

@app.route('/load/<name>', methods=['POST', 'GET'])
def load(name):
    global game
    game = Game(5,2,1,1,1)
    res = []
    file = open(name + '.csv')
    reader = csv.reader(file, delimiter=';')
    game.step_strings = []
    for line in reader:
        res.append(line)
        game.step_strings.append(line)
    load1(res[0])
    game.G = nx.Graph()
    for edge in game.edges:
        game.G.add_edge(edge['data']['source'], edge['data']['target'])
    #print(game.step_strings)
    return {'otvet' : game.nodes + game.edges}

@app.route('/biconnected_to_fix', methods=['POST', 'GET'])
def biconnected_to_fix():
    global game
    graph = copy.deepcopy(game.G)
    graph.remove_node(max(graph.nodes()))
    sharneers = []
    to_fix = []
    for i in list(nx.articulation_points(graph)):
        sharneers.append(i)
    if len(sharneers) > 0:
        to_return = list(nx.biconnected_components(graph))
        #print('biconnected_to_fix')
        for i in to_return:
            elements = list(i)
            tmp_flag = False
            while tmp_flag == False:
                tmp_to_fix = random.choice(elements)
                #print('Все компоненты: ')
                #print(to_return)
                #print('Сейчас мы на компоненьте:')
                #print(i)
                #print('Шарниры')
                #print(sharneers)
                #print('Выранное значение')
                #print(tmp_to_fix)
                if tmp_to_fix not in sharneers:
                    to_fix.append(tmp_to_fix)
                    tmp_flag = True
                counter = 0
                for j in i:
                    if j in sharneers:
                        counter = counter+1
                if counter == len(i):
                    break
    else:
        to_fix = 'net'
        #print(to_fix)
    return {'otvet' : to_fix}

def load1(string):
    global game
    turn_interface = int(string[0])
    game.nodes = []
    game.edges = []
    i = 1
    while ':' in string[i]:
        temp = string[i].split(':')
        if len(temp) == 3:
            game.nodes.append({'data': {'id': int(temp[0]), 'label': int(temp[0])},
                          'position': {'x': float(temp[1]), 'y': float(temp[2])}})
            game.positions[int(temp[0])] = float(temp[1]), float(temp[2])
        else:
            game.edges.append({'data': {'source': int(temp[0]), 'target': int(temp[1])}})
        i = i + 1
    game.max_turns = int(string[i])
    i = i + 1
    game.pul = int(string[i])
    i = i + 1
    game.fora = int(string[i])
    i = i + 1


@app.route('/get_history', methods=['POST', 'GET'])
def get_history():
    global game
    Text = []
    if len(game.step_strings) > 1:
        for i in range(len(game.step_strings)):
            if i == 0:
                pass
            else:
                if game.step_strings[i][1] == 'remove':
                    k = '🗡'
                else:
                    k = '⨮'
                Text.append('Ход № ' + str(int(game.step_strings[i][0])) + ' ' + k + str(game.step_strings[i][2].split(':')[0]))
                #print('---------------------------------------')
                #print(game.step_strings[i])
                #print(Text)
                #print('---------------------------------------')
    return {'otvet' : Text,
            'turn' : game.turn}

@app.route('/get_theoretic_intactness/<node>', methods=['POST', 'GET'])
def get_theoretic_intactness(node):
    global game
    graph = copy.deepcopy(game.G)
    graph.remove_node(int(node))
    score = winning(graph)
    return {'otvet' : score}



def winning(G):
    graph = nx.Graph()
    for edge in G.edges():
        #print(edge)
        graph.add_edge(edge[0], edge[1])
    graphConnections = list(nx.connected_components(graph))
    intactness = 0
    #print(len(graph.nodes()))
    for i in range(len(graphConnections)):
        #print(intactness)
        nowGraph = nx.Graph()
        nowGraph.add_edges_from(graph.edges(graphConnections[i]))
        if len(nowGraph.nodes()) == 0:
            nowGraphNodes = 1
        else:
            nowGraphNodes = len(nowGraph.nodes())
        for j in range(i + 1, len(graphConnections)):
            currentGraph = nx.Graph()
            currentGraph.add_edges_from(graph.edges(graphConnections[j]))
            if len(currentGraph.nodes()) == 0:
                currentGraphNodes = 1
            else:
                currentGraphNodes = len(currentGraph.nodes())
            intactness += currentGraphNodes * nowGraphNodes * 2
            #print('fsdfsdfs' + str(currentGraphNodes))
        #print(nowGraphNodes)
    #print('==============================', len(graph.nodes()))
    win_a_score = 1 - intactness / (len(graph.nodes()) ** 2)
    return 1 - intactness / (len(graph.nodes()) ** 2)

if __name__ == '__main__':
    app.run()