#데이터 수집
import pygsheets
import re

from telegram import Update
from telegram.ext import Updater, CallbackContext,MessageHandler,Filters,CommandHandler

#from scoreCheck_handler import scoreCheckHandler
#from register_handler import RegisterHandler
#from survey_handler import SurveyHandler

from states import STATES

from bob_telegram_tools.bot import TelegramBot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import *
from instance.config import *
import Data_analysis.TM_analysis_function as TM

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class TEAMatebot_Prof():
    def __init__(self, telegram_states:list, telegram_key:str, google_service_key:str, sheet_name:str)->None:
        self.gc = pygsheets.authorize(service_file=google_service_key)
        self.sh = self.gc.open(sheet_name)
        
        self.updater=Updater(telegram_key)
        dp = self.updater.dispatcher
        print("telegram teamate setting")
 
 
        self.state_map ={state:idx for idx, state in enumerate(telegram_states)}
        print(self.state_map) 
        self.handlers =[
                        #scoreCheckHandler(self.state_map,self.sh),
                        #RegisterHandler(self.state_map,self.sh),
                        #SurveyHandler(self.state_map,self.sh)
        ]

        for handler in self.handlers:
            dp.add_handler(handler.get_handler())
        
        dp.add_handler(CommandHandler('start', self.start))

    def execute(self):

        self.updater.start_polling()
        self.updater.idle()
               
    def class_group_list(class_id):
        json_file_name = 'fit-union-324504-8305b813e2b8.json'

        spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-FrwLOMx47lTOZuQZfxKdHxDl1w-HC0AvYhXv22LWGM/edit?usp=sharing'

        gc = pygsheets.authorize(service_file=json_file_name)
        sh = gc.open('TM_DB')
        wks = sh.worksheet('title','참여자 정보')

        user_df = wks.get_as_df()
        user_df = user_df['classcode' == class_id] 

        return list(set(user_df['group_id']))
        
        return 
    def print_graph(score): ########################  print graph 수정 필요
        label_name=[]
    
        key_ = score[0].keys()
        #value_ = []
        
        for i in range(len(score)) :
            label_name.append('block'+ str(i+1))
        #label 이름 설정
        
        # x = np.arange(divi)
        x = [1]
        for i in range(1, len(key_)):
            x.append(TM.double_plus(x[0] , 0.5*i))
        
        
        # block에 따라 score 출력
        # x축: 블록
        # y축: 점수   
        width = 0.5
        c = ['black', 'dimgrey', 'darkgray', 'silver', 'lightgrey']
        fig, ax = plt.subplots()
        for i in score:
            data = list(i.values())
            rects1 = ax.bar(x, data, width, color=c)
            #for idx, item in enumerate(data):
                
            for k in range(0, len(key_)):
                x[k] += 3
        
        x_l = []
        x_l.append(int(len(key_)/2)+0.5)
        for i in range(len(score)-1):
            x_l.append(x_l[0] + 3*(i+1))

        print(x_l)

        plt.xticks(x_l, labels=label_name)
        #plt.show()
        plt.savefig('print_graph.png')
    """
    def start(self, update: Update, context: CallbackContext) -> None:
        #command /start
        context.user_data.clear()
        resp = ""
        for handler in self.handlers:
            resp += handler.get_help()
            resp += "\n"
        update.message.reply_text(resp)    
        def region_graph(self,threshold,userid_list,current_data,pre_data):
    
        labels = ['up', 'mid', 'down']
        pre = [] #전데이터 들어갈곳
        current = [] #현재데이터 들어갈곳
        for i in range(len(pre_data)):
            pre.append(pre_data[i])
            current.append(current_data[i])
        x = np.arange(len(labels))  # the label locations
        width = 0.25  # the width of the bars
        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, pre, width, label='pre')
        rects2 = ax.bar(x + width/2, current, width, label='current')
        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('water-level')
        ax.set_title('--- flooding risk ---')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        # ax.bar_label(rects1, padding=3)
        # ax.bar_label(rects2, padding=3)
        fig.tight_layout()
        for userid in userid_list:
            bot = TelegramBot(TELEGRAM_TOKEN, userid[0])
            if threshold == "caution":
                text = "\t"+chr(0X1F6A8)+"현재 침수 주의 단계 입니다."+chr(0X1F6A8)
                bot.send_text(text)
            elif threshold == "danger":
                text = "\t"+chr(0X1F6A8)+"현재 침수 경고 단계 입니다."+chr(0X1F6A8)
                bot.send_text(text)
            bot.send_plot(plt)
            bot.clean_tmp_dir()
    """

if __name__ == "__main__":
    tb = TEAMatebot_Prof(STATES, TELEGRAM_API_KEY_PROF, GOOGLE_SERVICE_KEY, GOOGLE_SPREAD_SHEET)
    tb.execute()