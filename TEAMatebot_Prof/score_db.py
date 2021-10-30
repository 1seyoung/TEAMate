import re
from telegram import Update
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import TM_analysis_function as TM
from bob_telegram_tools.bot import TelegramBot
import pygsheets
from decimal import Decimal
import copy

def score_update(direc_score, group_id):
    key_ = direc_score[0].keys()
    value_ = [0 for i in range(len(key_))]
    for i in direc_score :
        for idx, j in enumerate(key_) :
            value_[idx] += i[j]
    analysis = []
    for i in value_ :
        if i < sum(value_) / (len(value_)*2) :
            analysis.append(0)
        else :
            analysis.append(1)

    pd.set_option('mode.chained_assignment',  None)
    json_file_name = 'fit-union-324504-8305b813e2b8.json'

    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-FrwLOMx47lTOZuQZfxKdHxDl1w-HC0AvYhXv22LWGM/edit?usp=sharing'

    gc = pygsheets.authorize(service_file=json_file_name)
    sh = gc.open('TM_DB')
    wks = sh.worksheet('title','팀평가')
    score_df = wks.get_as_df()
    
    score_df = score_df.loc[score_df["group_id"]==group_id]

    if score_df.empty :
        for idx, i in enumerate(key_) :
            wks.append_row([group_id, i, analysis[idx]])
    else :
        cell_list = list(score_df.index)
        for idx, i in enumerate(key_):
            wks.insert_row([group_id, i, analysis[idx]], cell_list[idx]+2)




def make_score_df(group_id):
    pd.set_option('mode.chained_assignment',  None)
    json_file_name = 'fit-union-324504-8305b813e2b8.json'

    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-FrwLOMx47lTOZuQZfxKdHxDl1w-HC0AvYhXv22LWGM/edit?usp=sharing'

    gc = pygsheets.authorize(service_file=json_file_name)
    sh = gc.open('TM_DB')
    wks = sh.worksheet('title','팀평가')
    score_df = wks.get_as_df()
    
    result_score_df = score_df.loc[score_df["group_id"]==group_id]
    
    return result_score_df

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
        #plt.show()
        save_name = group_id
        plt.savefig('print_graph' + str(group_id))


score = [{1750342024: 2.0, 1937944242: 0.0, 1739915236: 1.6}, {1750342024: 11.2, 1937944242: 0, 1739915236: 11.8}, {1750342024: 10.2, 1937944242: 24.1, 1739915236: 25.1}, {1750342024: 0, 1937944242: 1.0, 1739915236: 2.0}, {1750342024: 6.3, 1937944242: 0, 1739915236: 6.6}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 6.5, 1937944242: 0, 1739915236: 8.3}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}]
score_update(score, -3333)
#make_score_df(-3333)