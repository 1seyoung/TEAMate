#데이터 수집
import pygsheets
import re

from telegram import Update
from telegram.ext import Updater, CallbackContext,MessageHandler,Filters,CommandHandler

#from scoreCheck_handler import scoreCheckHandler
#from register_handler import RegisterHandler
#from survey_handler import SurveyHandler

from states import STATES
from decimal import Decimal

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
        #chat_id =((update.effective_user.id))

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
  
    def send_graph(group): ########################  group = group_id -> list
        for i in group :
            result_score = TM.main(i)
            #print_graph(result_score, i)
            png_name = 'print_graph'+ str(i) +'png'
            #TelegramBot.send_photo(chat_id=prof, photo=open(png_name, 'rb'))

if __name__ == "__main__":
    tb = TEAMatebot_Prof(STATES, TELEGRAM_API_KEY_PROF, GOOGLE_SERVICE_KEY, GOOGLE_SPREAD_SHEET)
    tb.execute()