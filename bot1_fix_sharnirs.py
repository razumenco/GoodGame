import requests
import random
import time

def bot_defence():
    global result1
    while True:
        while True:
            response = requests.post('http://127.0.0.1:5000/can_defend', data={}).json()['otvet']
            if response == 'True' or response == 'End' or response == 'Win':
                break

        if response == 'End':
            #print('You lose')
            result1 = 'Поражение'
            return 'lose'
            break
        if response == 'Win':
            #print('You win')
            result1 = 'Победа'
            return 'win'
            break
        #response = requests.post('http://127.0.0.1:5000/spisok_nodes', data={}).json()['otvet']
        a = response
        response = requests.post('http://127.0.0.1:5000/biconnected_to_fix', data={}).json()['otvet']
        #print('to connect = ',response)
        if response != 'net':
            spisok = response
        else:
            a.pop()
            spisok = random.choices(a, k=2)
        #print(spisok)
        response = requests.post('http://127.0.0.1:5000/add/' + str(spisok), data={}).json()['otvet']
        #print(response)
        response = requests.post('http://127.0.0.1:5000/next_turn', data={}).json()['otvet']