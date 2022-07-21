import requests
import random

def bot_attack():
    global result
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
        count = 0
        if response != []:
            for i in response:
                otvet = requests.post('http://127.0.0.1:5000/get_theoretic_intactness/' + str(i), data={}).json()['otvet']
                if float(otvet) < float(1.0):
                    count = count + 1
                    response = requests.post('http://127.0.0.1:5000/delete/' + str(i), data={}).json()
                    #print('Победа через шарнир')
                    break
            if count == 0:
                response = requests.post('http://127.0.0.1:5000/most_clust', data={}).json()['otvet']
                a = response
                # print(a)
                response = requests.post('http://127.0.0.1:5000/delete/' + str(a), data={}).json()
        else:
            response = requests.post('http://127.0.0.1:5000/most_clust', data={}).json()['otvet']
            a = response
            #print(a)
            response = requests.post('http://127.0.0.1:5000/delete/' + str(a), data={}).json()
        #print(response)

        if len(response) == 2:
            result = response['score']
            return response['score']
            #print('Победа с интактностью = ',response['score'])
            #response = requests.post('http://127.0.0.1:5000/save/pizdec', data={}).json()
            break
