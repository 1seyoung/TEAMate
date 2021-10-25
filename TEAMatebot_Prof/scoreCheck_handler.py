from telegram import Update
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext 
import pygsheets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import TM_analysis_function as TM

from bob_telegram_tools.bot import TelegramBot
from pygsheets import Spreadsheet
class scoreCheckHandler():
    def __init__(self, state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        print(state_map)
        self.sh =sh

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('/scorecheck', self.send_graph)],
            states={
                self.state_map["GET_TEAM_ID"]:[
                    MessageHandler(
                        Filters.regex(r'\w+'), self.handle_check_team
                    ),
                    MessageHandler(Filters.text & ~(Filters.command), self.handle_unwanted_data),
                ],
                self.state_map["TEAM_CHECKED"]: [
                    CommandHandler(
                        'teamscore', self.handle_check_password
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
    def get_handler(self) -> Dispatcher:
        return self.handler

    def get_help(self):
        
        return f"/scorecheck :  자신의 정보와 참가중인 팀 정보를 등록합니다. 그룹 채팅방에서는 사용할 수 없습니다. 봇을 친구 추가한 뒤 대화를 걸고 이용해주세요"

    def handle_score_check(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("확인할 팀 코드를 입력해주세요")
        context.user_data['next_state'] = "GET_TEAM_ID"
        return self.state_map[context.user_data['next_state']]      

    def check_valid_user(self, team_id:int) -> bool:
        wks = self.sh.worksheet('title','참여자 정보')
        df = wks.get_as_df()

        user_data = df.index[df['classcode'] == team_id].tolist()
        if user_data:
            return user_data[0]
        else:
            return -1

    def handle_check_team(self, update: Update, context: CallbackContext) -> int:
        self.team_id = int(update.message.text)
        if (row := self.check_valid_user(self.team_id)) > 0:
            context.user_data['id'] = self.team_id        
            context.user_data['row'] = row + 2
            context.user_data['next_state'] = "TEAM_CHECKED"

            update.message.reply_text("등록된 팀 입니다.\n 팀 점수를 확인하려면 /teamscore 을 클릭하세요 ")
            return self.state_map[context.user_data['next_state']]
        else:
            update.message.reply_text("등록이 안된 팀입니다.\n학생들에게 다시 확인하시길 바랍니다.")
            context.user_data.clear()
            return ConversationHandler.END   

    def handle_unwanted_data(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("다시 입력해주세요.")
        return self.state_map[context.user_data['next_state']]

    def cancel(self, update: Update, context: CallbackContext) -> int:
        #이전으로 돌아가기
        #전체 취소 차이가  코드 차이 알아보기
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END

    def handle_check_password(self, update: Update, context: CallbackContext):
        return self.class_group_list(self.team_id)

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
