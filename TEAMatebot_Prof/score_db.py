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

def analysis_score_update(direc_score, group_id):
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


    score_df = print_score_df(group_id)
    score_df['analysis'] = analysis
    json_file_name = 'fit-union-324504-8305b813e2b8.json'
    pd.set_option('mode.chained_assignment',  None)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-FrwLOMx47lTOZuQZfxKdHxDl1w-HC0AvYhXv22LWGM/edit?usp=sharing'

    gc = pygsheets.authorize(service_file=json_file_name)
    sh = gc.open('TM_DB')
    wks = sh.worksheet('title','팀평가')
    for index, row in score_df.iterrows() :
        p_value = list(row)
        wks.update_row(index+2, p_value)
def print_score_df(group_id):
    pd.set_option('mode.chained_assignment',  None)
    json_file_name = 'fit-union-324504-8305b813e2b8.json'

    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-FrwLOMx47lTOZuQZfxKdHxDl1w-HC0AvYhXv22LWGM/edit?usp=sharing'

    gc = pygsheets.authorize(service_file=json_file_name)
    sh = gc.open('TM_DB')
    wks = sh.worksheet('title','팀평가')
    score_df = wks.get_as_df()
    
    result_score_df = score_df.loc[score_df["group_id"]==group_id]
    print(len(result_score_df))
    return result_score_df

def result_print_graph(group_id):
    result_score_df = print_score_df(group_id)
    label_name=[]
    
    for i in range(len(result_score_df)) :
        label_name.append('user'+ str(i+1))
    #label 이름 설정
    
    # x = np.arange(divi)
    x = [1]
    for i in range(1, len(result_score_df)):
        x.append(TM.double_plus(x[0] , 0.5*i+1*i))
    
    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수   
    width = 0.5
    c = ['slategrey', 'lightblue', 'cornflowerblue', 'royalblue', 'slateblue']
    fig, ax = plt.subplots()
    data = result_score_df['result'].tolist()
    rects1 = ax.bar(x, data, width, color=c)
    x_l = x
    plt.xticks(x_l, labels=result_score_df['user_id'])
    ax.set_ylabel('result_Scores')
    ax.set_title('TEAMate')
    plt.show()
    save_name = group_id
    #plt.savefig('print_graph' + str(group_id))
def grade(group_id) :
    score_df = print_score_df(group_id)

    user = score_df['user_id'].tolist()
    analysis = score_df['anaylsis'].tolist()
    contribute = score_df['contribute'].tolist()
    outcome =  score_df['outcome'].tolist()
    result = []
    for i in range(len(user)) :
        result.append(analysis[i]*(2*contribute*outcome))
    
score = [{1750342024: 2.0, 1937944242: 0.0, 1739915236: 1.6}, {1750342024: 11.2, 1937944242: 0, 1739915236: 11.8}, {1750342024: 10.2, 1937944242: 24.1, 1739915236: 25.1}, {1750342024: 0, 1937944242: 1.0, 1739915236: 2.0}, {1750342024: 6.3, 1937944242: 0, 1739915236: 6.6}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 6.5, 1937944242: 0, 1739915236: 8.3}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}]
analysis_score_update(score, -3333)
#print_score_df(-472653938)
#result_print_graph(-472653938)