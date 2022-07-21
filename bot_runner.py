from threading import Thread
from time import sleep
import requests
import bot1_fix_sharnirs
import bot1_max_zvaz
import bot2_min_svyaz
import bot2_max_centrality
import bot3_max_cluster
import bot3_min_centr
import bot3_szyaz_centr_order
import bot3_szyaz_centr_random
import bot4_fix_centr
import bot4_fix_svyaz


import csv


# kol-vo uzlov, svyaznost, kol-vk hodov, fora, pull

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        #print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

# with open('stats(max_svyaz_vs_fix_svyaz).csv', "a", newline='') as csv_file:
#     writer = csv.writer(csv_file, delimiter=';')
#     writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])
#
# with open('stats(max_svyaz_vs_fix_centr).csv', "a", newline='') as csv_file:
#     writer = csv.writer(csv_file, delimiter=';')
#     writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])
#
# with open('stats(max_centrality_vs_fix_svyaz).csv', "a", newline='') as csv_file:
#     writer = csv.writer(csv_file, delimiter=';')
#     writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])

# with open('stats(max_centrality_vs_fix_centr).csv', "a", newline='') as csv_file:
#     writer = csv.writer(csv_file, delimiter=';')
#     writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])

with open('stats(svyaz_centr_order_vs_fix_svyaz).csv', "a", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])

with open('stats(svyaz_centr_order_vs_fix_centr).csv', "a", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])

with open('stats(svyaz_centr_random_vs_fix_svyaz).csv', "a", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])

with open('stats(svyaz_centr_random_vs_fix_centr).csv', "a", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    writer.writerow(['size', 'zvaz', 'max_turn', 'fora', 'pul', 'result'])

# #1
# for size in range(50, 101, 10):
#     for max_turn in range(20, 51, 10):
#         for fora in range(0, round(0.3*size), 2):
#             for pul in range(35, 75, 5):
#                 c = 0
#                 for i in range(5):
#                     response = requests.post('-, data={}).json()['otvet']
#                     twrv1 = ThreadWithReturnValue(target=bot1_max_zvaz.bot_attack)
#                     twrv1.start()
#                     twrv2 = ThreadWithReturnValue(target=bot4_fix_svyaz.bot_defence)
#                     twrv2.start()
#                     result = twrv1.join()
#                     if result != 'Поражение':
#                         result = 'Победа Атаки intactness='+str(result)
#                         c = c + 1
#                     else:
#                         result = 'Победа Защиты'
#                     #print(result)
#                     with open('stats(max_svyaz_vs_fix_svyaz).csv', "a", newline='') as csv_file:
#                         writer = csv.writer(csv_file, delimiter=';')
#                         writer.writerow([size, 5, max_turn, fora, pul, result])
#                 procent = str(c/5*100)+"%"
#                 with open('stats(max_svyaz_vs_fix_svyaz).csv', "a", newline='') as csv_file:
#                     writer = csv.writer(csv_file, delimiter=';')
#                     writer.writerow([size, 5, max_turn, fora, pul, procent])
#
# #2
# for size in range(50, 101, 10):
#     for max_turn in range(20, 51, 10):
#         for fora in range(0, round(0.3*size), 2):
#             for pul in range(35, 75, 5):
#                 c = 0
#                 for i in range(5):
#                     response = requests.post('http://127.0.0.1:5000/start/'+str(size)+'/5/'+str(max_turn)+'/'+str(fora)+'/'+str(pul), data={}).json()['otvet']
#                     twrv1 = ThreadWithReturnValue(target=bot1_max_zvaz.bot_attack)
#                     twrv1.start()
#                     twrv2 = ThreadWithReturnValue(target=bot4_fix_centr.bot_defence)
#                     twrv2.start()
#                     result = twrv1.join()
#                     if result != 'Поражение':
#                         result = 'Победа Атаки intactness='+str(result)
#                         c = c + 1
#                     else:
#                         result = 'Победа Защиты'
#                     #print(result)
#                     with open('stats(max_svyaz_vs_fix_centr).csv', "a", newline='') as csv_file:
#                         writer = csv.writer(csv_file, delimiter=';')
#                         writer.writerow([size, 5, max_turn, fora, pul, result])
#                 procent = str(c/5*100)+"%"
#                 with open('stats(max_svyaz_vs_fix_centr).csv', "a", newline='') as csv_file:
#                     writer = csv.writer(csv_file, delimiter=';')
#                     writer.writerow([size, 5, max_turn, fora, pul, procent])
#
# #3
# for size in range(50, 101, 10):
#     for max_turn in range(20, 51, 10):
#         for fora in range(0, round(0.3*size), 2):
#             for pul in range(35, 75, 5):
#                 c = 0
#                 for i in range(5):
#                     response = requests.post('http://127.0.0.1:5000/start/'+str(size)+'/5/'+str(max_turn)+'/'+str(fora)+'/'+str(pul), data={}).json()['otvet']
#                     twrv1 = ThreadWithReturnValue(target=bot2_max_centrality.bot_attack)
#                     twrv1.start()
#                     twrv2 = ThreadWithReturnValue(target=bot4_fix_svyaz.bot_defence)
#                     twrv2.start()
#                     result = twrv1.join()
#                     if result != 'Поражение':
#                         result = 'Победа Атаки intactness='+str(result)
#                         c = c + 1
#                     else:
#                         result = 'Победа Защиты'
#                     #print(result)
#                     with open('stats(max_centrality_vs_fix_svyaz).csv', "a", newline='') as csv_file:
#                         writer = csv.writer(csv_file, delimiter=';')
#                         writer.writerow([size, 5, max_turn, fora, pul, result])
#                 procent = str(c/5*100)+"%"
#                 with open('stats(max_centrality_vs_fix_svyaz).csv', "a", newline='') as csv_file:
#                     writer = csv.writer(csv_file, delimiter=';')
#                     writer.writerow([size, 5, max_turn, fora, pul, procent])

#4
for size in range(80, 101, 10):
    for max_turn in range(20, 51, 10):
        for fora in range(0, round(0.3*size), 2):
            for pul in range(35, 75, 5):
                c = 0
                for i in range(5):
                    response = requests.post('http://127.0.0.1:5000/start/'+str(size)+'/5/'+str(max_turn)+'/'+str(fora)+'/'+str(pul), data={}).json()['otvet']
                    twrv1 = ThreadWithReturnValue(target=bot2_max_centrality.bot_attack)
                    twrv1.start()
                    twrv2 = ThreadWithReturnValue(target=bot4_fix_centr.bot_defence)
                    twrv2.start()
                    result = twrv1.join()
                    if result != 'Поражение':
                        result = 'Победа Атаки intactness='+str(result)
                        c = c + 1
                    else:
                        result = 'Победа Защиты'
                    #print(result)
                    with open('stats(max_centrality_vs_fix_centr).csv', "a", newline='') as csv_file:
                        writer = csv.writer(csv_file, delimiter=';')
                        writer.writerow([size, 5, max_turn, fora, pul, result])
                procent = str(c/5*100)+"%"
                with open('stats(max_centrality_vs_fix_centr).csv', "a", newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    writer.writerow([size, 5, max_turn, fora, pul, procent])

#5
for size in range(50, 101, 10):
    for max_turn in range(20, 51, 10):
        for fora in range(0, round(0.3*size), 2):
            for pul in range(35, 75, 5):
                c = 0
                for i in range(5):
                    response = requests.post('http://127.0.0.1:5000/start/'+str(size)+'/5/'+str(max_turn)+'/'+str(fora)+'/'+str(pul), data={}).json()['otvet']
                    twrv1 = ThreadWithReturnValue(target=bot3_szyaz_centr_order.bot_attack)
                    twrv1.start()
                    twrv2 = ThreadWithReturnValue(target=bot4_fix_svyaz.bot_defence)
                    twrv2.start()
                    result = twrv1.join()
                    if result != 'Поражение':
                        result = 'Победа Атаки intactness='+str(result)
                        c = c + 1
                    else:
                        result = 'Победа Защиты'
                    #print(result)
                    with open('stats(svyaz_centr_order_vs_fix_svyaz).csv', "a", newline='') as csv_file:
                        writer = csv.writer(csv_file, delimiter=';')
                        writer.writerow([size, 5, max_turn, fora, pul, result])
                procent = str(c/5*100)+"%"
                with open('stats(svyaz_centr_order_vs_fix_svyaz).csv', "a", newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    writer.writerow([size, 5, max_turn, fora, pul, procent])

#6
for size in range(50, 101, 10):
    for max_turn in range(20, 51, 10):
        for fora in range(0, round(0.3*size), 2):
            for pul in range(35, 75, 5):
                c = 0
                for i in range(5):
                    response = requests.post('http://127.0.0.1:5000/start/'+str(size)+'/5/'+str(max_turn)+'/'+str(fora)+'/'+str(pul), data={}).json()['otvet']
                    twrv1 = ThreadWithReturnValue(target=bot3_szyaz_centr_order.bot_attack)
                    twrv1.start()
                    twrv2 = ThreadWithReturnValue(target=bot4_fix_centr.bot_defence)
                    twrv2.start()
                    result = twrv1.join()
                    if result != 'Поражение':
                        result = 'Победа Атаки intactness='+str(result)
                        c = c + 1
                    else:
                        result = 'Победа Защиты'
                    #print(result)
                    with open('stats(svyaz_centr_order_vs_fix_centr).csv', "a", newline='') as csv_file:
                        writer = csv.writer(csv_file, delimiter=';')
                        writer.writerow([size, 5, max_turn, fora, pul, result])
                procent = str(c/5*100)+"%"
                with open('stats(svyaz_centr_order_vs_fix_centr).csv', "a", newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    writer.writerow([size, 5, max_turn, fora, pul, procent])

#7
for size in range(50, 101, 10):
    for max_turn in range(20, 51, 10):
        for fora in range(0, round(0.3*size), 2):
            for pul in range(35, 75, 5):
                c = 0
                for i in range(5):
                    response = requests.post('http://127.0.0.1:5000/start/'+str(size)+'/5/'+str(max_turn)+'/'+str(fora)+'/'+str(pul), data={}).json()['otvet']
                    twrv1 = ThreadWithReturnValue(target=bot3_szyaz_centr_random.bot_attack)
                    twrv1.start()
                    twrv2 = ThreadWithReturnValue(target=bot4_fix_svyaz.bot_defence)
                    twrv2.start()
                    result = twrv1.join()
                    if result != 'Поражение':
                        result = 'Победа Атаки intactness='+str(result)
                        c = c + 1
                    else:
                        result = 'Победа Защиты'
                    #print(result)
                    with open('stats(svyaz_centr_random_vs_fix_svyaz).csv', "a", newline='') as csv_file:
                        writer = csv.writer(csv_file, delimiter=';')
                        writer.writerow([size, 5, max_turn, fora, pul, result])
                procent = str(c/5*100)+"%"
                with open('stats(svyaz_centr_random_vs_fix_svyaz).csv', "a", newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    writer.writerow([size, 5, max_turn, fora, pul, procent])

#8
for size in range(50, 101, 10):
    for max_turn in range(20, 51, 10):
        for fora in range(0, round(0.3*size), 2):
            for pul in range(35, 75, 5):
                c = 0
                for i in range(5):
                    response = requests.post('http://127.0.0.1:5000/start/'+str(size)+'/5/'+str(max_turn)+'/'+str(fora)+'/'+str(pul), data={}).json()['otvet']
                    twrv1 = ThreadWithReturnValue(target=bot3_szyaz_centr_random.bot_attack)
                    twrv1.start()
                    twrv2 = ThreadWithReturnValue(target=bot4_fix_centr.bot_defence)
                    twrv2.start()
                    result = twrv1.join()
                    if result != 'Поражение':
                        result = 'Победа Атаки intactness='+str(result)
                        c = c + 1
                    else:
                        result = 'Победа Защиты'
                    #print(result)
                    with open('stats(svyaz_centr_random_vs_fix_centr).csv', "a", newline='') as csv_file:
                        writer = csv.writer(csv_file, delimiter=';')
                        writer.writerow([size, 5, max_turn, fora, pul, result])
                procent = str(c/5*100)+"%"
                with open('stats(svyaz_centr_random_vs_fix_centr).csv', "a", newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    writer.writerow([size, 5, max_turn, fora, pul, procent])