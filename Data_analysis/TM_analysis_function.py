from datetime import timedelta
from re import I
from matplotlib.pyplot import text
from numpy import False_, NaN, copysign, int16
import pygsheets
import pandas as pd
from decimal import Decimal
import copy
#import TM_analysis_graph_ as graph

def make_df(group_id):
    pd.set_option('mode.chained_assignment',  None)
    json_file_name = 'fit-union-324504-8305b813e2b8.json'

    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-FrwLOMx47lTOZuQZfxKdHxDl1w-HC0AvYhXv22LWGM/edit?usp=sharing'

    gc = pygsheets.authorize(service_file=json_file_name)
    sh = gc.open('TM_DB')
    wks = sh.worksheet('title','chat_data')
    chat_df = wks.get_as_df()
    chat_df['Datetime'] = pd.to_datetime(chat_df['Datetime'])

    group_chat_df = chat_df.loc[chat_df["group_id"]==group_id]

    group_chat_df['timegap'] = (group_chat_df.Datetime - group_chat_df.Datetime.shift())

    group_chat_df= group_chat_df.assign(timeblock = lambda x:(x['timegap']> timedelta(seconds=600)).cumsum() )
    group_chat_df = group_chat_df.dropna(axis=0)
    #print(group_chat_df)
    group_chat_df = group_chat_df.reset_index()
    group_chat_df = group_chat_df.drop(columns = ['index'])

    stick = [] 
    for i in range(0, len(group_chat_df)-1) :
        if group_chat_df.at[i,'user_id'] == group_chat_df.at[i+1, 'user_id'] and group_chat_df.at[i, 'timeblock'] == group_chat_df.at[i+1,'timeblock'] :
            stick.append(i+1)
    stick.reverse()

    for i in stick :
        group_chat_df.at[i-1, 'chat'] += group_chat_df.at[i,'chat']
        group_chat_df.at[i, 'chat'] = NaN
        group_chat_df = group_chat_df.dropna(axis=0)

    
    group_chat_df = group_chat_df.reset_index()
    group_chat_df = group_chat_df.drop(columns = ['index'])
    
    return group_chat_df

def timeblock_starter(data_text):
    time_check = list(data_text['timeblock'])
    data_text['starter'] = False
    data_text.at[0, 'starter'] = True

    for i in range(1, len(data_text)) :
        if time_check[i]-time_check[i-1] != 0 :
            data_text.at[i,'starter'] = True

    return data_text

def comunication(data_text) :
    data_text['comunication'] = False

    check = [-1]
    check = check + list(data_text['timeblock'])
    check.append(-1)

    for i in range(1, len(check)-1) :
        if check[i] != check[i-1] and check[i] != check[i+1] :
            data_text.at[i-1,'comunication'] = False
        else :
            data_text.at[i-1,'comunication'] = True

    return data_text

def name_score_clear (name_score) :
    name = name_score.keys()
    for i in name :
        name_score[i] = 0
    return name_score

def double_plus(a,b) :
    return round(float(str(a))+float(str(b)) , 1)

def set_score(text, name_score) :
  count = len(str(text['chat']))
  num = add_score(name_score, text['starter'])

  ty = 'no_ping'
  if text['comunication'] == True :
    ty = 'timeblock'
  if str(text['chat']).startswith('파일: ') :
    ty = 'file'

  name_score[text['user_id']] = double_plus(all_score(ty, count), name_score[text['user_id']])
  name_score[text['user_id']] = double_plus(num, name_score[text['user_id']])
  return name_score

def add_score(name_score, starter) :
  num = 0
  if starter == True :
    num = all_score('starter', 0)
  return num

def all_score(ty, length) :
    no_ping_score = 0                             #timeblock 참여하지 않을 시 점수
    length_score = [0.3, 1.0, 1.5, 1.7, 2.0]      #timeblock 참여시 점수
    length_check = [5, 50, 100, 200]              #글자 수에 따라서
    file_score = 1.0                              #file일 경우
    starter_score = 1.0                           #대화 시작을 할 경우 점수

    if ty == 'file' :
      return file_score
    if ty == 'starter' :
      return starter_score
    #file, starter 점수 부여
    if ty == 'no_ping' :
      return no_ping_score
    #timeblock 참여하지 않을 시 점수출력(0)

    k = 4
    if ty == 'timeblock' :
      for i in range(0, len(length_check)) :
        if length < length_check[i] :
          k = i
          break
      return length_score[k]

    return 0

def main(group):
      
    data_text = make_df(group)

    name = list(set(data_text['user_id']))
    name_score = []
    for i in range(0, len(name)) :
      name_score.append([name[i], str(0.0)])
    
    name_score = dict(name_score)
    data_text=timeblock_starter(data_text)
    data_text = comunication(data_text)

    pop_check = 0

    result_score = []

    for i in range(len(data_text)) :
      if pop_check != data_text.at[i,'timeblock'] :
        result_score.append(name_score)
        name_score = name_score_clear(copy.deepcopy(name_score))
        pop_check += 1

      name_score = set_score(data_text.loc[i, :], name_score)
          
    result_score.append(name_score)
    print(result_score)
    return result_score
