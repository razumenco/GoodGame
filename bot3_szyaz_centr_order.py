import requests
import random

def bot_attack():
    global result
    counter = 1
    # kol-vo uzlov, svyaznost, kol-vk hodov, fora, pull
    while True:
        while True:
            response = requests.post('http://127.0.0.1:5000/can_attack', data={}).json()['otvet']
            if response == 'True' or response == 'End':
                break

        if response == 'End':
            #print('Поражение')
            result = 'Поражение'
            return 'Поражение'
            break
        response = requests.post('http://127.0.0.1:5000/sharn_info', data={}).json()['otvet']
        if response != []:
            response = requests.post('http://127.0.0.1:5000/delete/' + str(response[0]), data={}).json()
        else:
            if counter % 2 == 1:
                response = requests.post('http://127.0.0.1:5000/most_svyaz', data={}).json()['otvet']
                a = response
                #print(a)
                response = requests.post('http://127.0.0.1:5000/delete/' + str(a), data={}).json()
                counter = counter + 1
            else:
                response = requests.post('http://127.0.0.1:5000/most_centr', data={}).json()['otvet']
                a = response
                # print(a)
                response = requests.post('http://127.0.0.1:5000/delete/' + str(a), data={}).json()
                counter = counter + 1
        #print(response)
        if len(response) == 2:
            result = response['score']
            return response['score']
            #print('Победа с интактностью = ',response['score'])
            response = requests.post('http://127.0.0.1:5000/save/pizdec', data={}).json()
            break