from telegram import Update
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext 
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import TM_analysis_function as TM
from decimal import Decimal
from bob_telegram_tools.bot import TelegramBot
from pygsheets import *

def print_graph(score, group_id):
    label_name=[]
    key_ = score[0].keys()
    #value_ = []
    for i in range(len(score)) :
        label_name.append('b'+ str(i+1))
    #label 이름 설정
    # x = np.arange(divi)
    x = [1]
    for i in range(1, len(key_)):
        x.append(TM.double_plus(x[0] , 0.5*i))
    
    
    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수   
    width = 0.5
    c = ['slategrey', 'lightblue', 'cornflowerblue', 'royalblue', 'slateblue']
    fig, ax = plt.subplots()
    for idx, i in enumerate(score):
        data = list(i.values())
        name_g = list(i.keys())
        if idx == 0 :
            for idx2, j in enumerate(data) :
                rects1 = ax.bar(x[idx2], j, width, color=c[idx2], label = str(name_g[idx2]))
            for k in range(0, len(key_)):
                x[k] += 3
            continue
        rects1 = ax.bar(x, data, width, color=c)
        #for idx, item in enumerate(data):
            
        for k in range(0, len(key_)):
            x[k] += 3
    
    plt.legend((key_))
    x_l = []
    x_l.append(int(len(key_)/2)+0.5)
    for i in range(len(score)-1):
        x_l.append(x_l[0] + 3*(i+1))

    plt.xticks(x_l, labels=label_name)
    ax.set_ylabel('Scores')
    ax.set_title('TEAMate')
    plt.show()
    #save_name = group_id
    #plt.savefig('print_graph' + str(group_id))

def print_graph_indi(score, group_id, aver):
    avg = []
    for i in score :
        value = list(i.values())
        avg.append(round(sum(value) / len(i),2))

    print(avg)

    label_name=[]        
    key_ = score[0].keys()
    for i in range(len(score)) :
        label_name.append('b'+ str(i+1))
    #label 이름 설정

    data = []

    for idx, i in enumerate(key_) :
        c_data = []
        for j in score :
            c_data.append(j[i])
        data.append(c_data)
        """
        if idx == 0 :  ## if else 지우기
            data.append(c_data)
        else : 
            data.append([x+y for x,y in zip(data[idx-1], c_data)])
        """

    # x = np.arange(divi)
    x = [1]
    for i in range(1, len(score)):
        x.append(TM.double_plus(x[0] , i))


    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수   
    width = 0.5
    c = ['slategrey', 'lightblue', 'cornflowerblue', 'royalblue', 'slateblue']
    x_l = [1]

    for i in range(len(score)-1):
        x_l.append(x_l[0] + (i+1))

    fig, ax = plt.subplots(len(key_))
    for idx in range(len(key_)):
        #name_g = list(i.keys())
        rects1 = ax[idx].bar(x, data[len(key_)-idx-1], width, color=c[idx])
        ax[idx].plot(x, aver)
        plt.xticks(x_l, labels=label_name)
        #for idx, item in enumerate(data):
    #plt.show()
    save_name = str(group_id) + "_indi"
    plt.savefig('print_graph_' + save_name)

def result_print_graph(score, group_id):
    #result_score_df = self.print_score_df(group_id)
    label_name=[]
    
    for i in range(len(score)) :
        label_name.append('user'+ str(i+1))
    #label 이름 설정
    
    # x = np.arange(divi)
    x = [1]
    for i in range(1, len(score)):
        x.append(round(x[0] + i ,2))
    
    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수   
    width = 0.5
    c = ['thistle', 'palevioletred', 'lightpink', 'plum', 'red']
    fig, ax = plt.subplots()
    data = score
    print(x)
    rects1 = ax.bar(x, data, width, color = c)
    x_l = x
    plt.xticks(x_l, label_name)
    ax.set_ylabel('result_Scores')
    ax.set_title('TEAMate')
    plt.show()
    #save_name = str(group_id)
    #plt.savefig('result_print_graph_' + save_name)

def grade(score, analysis, contri, outcome,  group_id) :
    result = []
    for i in range(len(analysis)) :
        result.append(int(analysis[i])*(2*int(contri[i])*int(outcome)))
    return result

analysis = [1,1,1,1,0]
contri = [3,5,4,5,1]
outcome = 8

score = [{'user1' : 21.0, 'user2' : 35.0, 'user3' : 19.0, 'user4' : 28.0, 'user5' : 16.2},
{'user1' : 3.0, 'user2' : 35.0, 'user3' : 19.0, 'user4' : 28.0, 'user5' : 16.2},
{'user1' : 7.0, 'user2' : 10.0, 'user3' : 8.0, 'user4' : 12.0, 'user5' : 2.2},
{'user1' : 3.5, 'user2' : 5.0, 'user3' : 3.0, 'user4' : 5.0, 'user5' : 1.0},
{'user1' : 2.8, 'user2' : 8.0, 'user3' : 3.0, 'user4' : 9.0, 'user5' : 5.0},
{'user1' : 7.0, 'user2' : 8.0, 'user3' : 2.0, 'user4' : 2.1, 'user5' : 3.5},
{'user1' : 12.0, 'user2' : 5.0, 'user3' : 6.0, 'user4' : 5.0, 'user5' : 0.0},
{'user1' : 3.0, 'user2' : 4.0, 'user3' : 5.0, 'user4' : 7.0, 'user5' : 2.0},
{'user1' : 1.0, 'user2' : 3.5, 'user3' : 4.5, 'user4' : 0.0, 'user5' : 3.7},
{'user1' : 5.3, 'user2' : 10.0, 'user3' : 2.0, 'user4' : 6.9, 'user5' : 1.0},
{'user1' : 1.0, 'user2' : 3.0, 'user3' : 4.0, 'user4' : 10.5, 'user5' : 2.2},
{'user1' : 1.2, 'user2' : 2.0, 'user3' : 1.0, 'user4' : 3.0, 'user5' : 0.3},
{'user1' : 1.0, 'user2' : 16.0, 'user3' : 10.0, 'user4' : 18.0, 'user5' : 0.8},
{'user1' : 3.0, 'user2' : 8.0, 'user3' : 5.0, 'user4' : 6.0, 'user5' : 4.0},
{'user1' : 1.3, 'user2' : 22.0, 'user3' : 12.0, 'user4' : 17.0, 'user5' : 1.2},
{'user1' : 0.0, 'user2' : 8.0, 'user3' : 1.9, 'user4' : 4.0, 'user5' : 2.2}]

aver = [23.84,7.0,7.2,3.5, 5.56, 4.52, 5.6, 4.2, 2.48, 5.04, 4.14, 1.5, 9.16, 5.2, 10.72, 3.1]
gra = grade(score, analysis, contri, outcome, -1233)
result_print_graph(gra, -1233)
print_graph(score, -1333)
print_graph_indi(score, -1333, aver)