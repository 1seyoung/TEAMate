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
class scoreCheckHandler():
    def __init__(self, state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        print(state_map)
        self.sh =sh

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('scorecheck', self.handle_score_check)],
            states={
                self.state_map["GET_TEAM_ID"]:[
                    MessageHandler(
                        Filters.regex(r'\w+'), self.handle_check_team
                    ),
                    MessageHandler(Filters.text & ~(Filters.command), self.handle_unwanted_data),
                ],
                self.state_map["TEAM_CHECKED"]: [
                    CommandHandler(
                        'teamscore', self.get_graph
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
    def get_handler(self) -> Dispatcher:
        return self.handler

    def get_help(self):
        
        return f"/scorecheck : 팀의 참여도를 확인하고싶으면 클릭해주세요"

    def handle_score_check(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("확인할 팀 코드를 입력해주세요")
        context.user_data['next_state'] = "GET_TEAM_ID"
        return self.state_map[context.user_data['next_state']]      

    def check_valid_user(self, team_id:int) -> bool:
        wks = self.sh.worksheet('title','참여자 정보')
        df = wks.get_as_df()

        user_data = df.index[df['classcode'] == team_id].tolist()
        print(user_data)
        if user_data:
            return user_data[0]
        else:
            return -1

    def handle_check_team(self, update: Update, context: CallbackContext) -> int:
        #print(update.message.text)
        self.team_id = str(update.message.text)
        if (row := self.check_valid_user(self.team_id)) > 0:
            context.user_data['id'] = self.team_id        
            context.user_data['row'] = row + 2
            context.user_data['next_state'] = "TEAM_CHECKED"

            update.message.reply_text("등록된 팀 입니다.\n 팀 점수를 확인하려면 /teamscore 을 클릭하세요 ")
            return self.state_map[context.user_data['next_state']]
        else:
            update.message.reply_text("없는 정보입니다.\n학생들에게 다시 확인하시길 바랍니다.")
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

    def get_graph(self,update: Update, context: CallbackContext) -> int:
        group = self.class_group_list(self.team_id)
        group_idd = int(group)
        result_score = TM.main(group_idd)
        self.print_graph(result_score, group)
        self.analysis_score_update(result_score, group)
        self.print_graph_indi(result_score,group)
        png_name = 'print_graph' + str(group) + '.png'
        png_name_indi = 'print_graph' + str(group) + '_indi.png'
        cv2.imread('png_name', cv2.IMREAD_COLOR)
        context.bot.send_photo(chat_id=update.effective_user.id, photo=open(png_name, 'rb'))
        context.bot.send_photo(chat_id=update.effective_user.id, photo=open(png_name_indi, 'rb'))
        return ConversationHandler.END

    def class_group_list(self,class_id):
        
        wks = self.sh.worksheet('title','참여자 정보')

        
        df = wks.get_as_df()
        
        user_data=df.index[df['classcode'] == class_id].tolist()
        

        group_id =wks.get_value('D'+str(user_data[0]+2))
        #user_df = user_df.loc['classcode' == str(class_id)]
        print(group_id)
        return group_id
    def analysis_score_update(self, direc_score, group_id): 
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


        score_df = self.print_score_df(group_id)
        score_df['analysis'] = analysis
        
        wks = self.sh.worksheet('title', '팀평가')
        for index, row in score_df.iterrows() :
            p_value = list(row)
            wks.update_row(index+2, p_value)

    def print_graph(self,score, group_id):
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
  
    def print_graph_indi(self,score, group_id):
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
            plt.xticks(x_l, labels=label_name)
            #for idx, item in enumerate(data):
        save_name = str(group_id) + "_indi"
        plt.savefig('print_graph_' + save_name)

    def result_print_graph(self, group_id):
        result_score_df = self.print_score_df(group_id)
        label_name=[]
        
        for i in range(len(result_score_df)) :
            label_name.append('user'+ str(i+1))
        #label 이름 설정
        
        # x = np.arange(divi)
        x = [1]
        for i in range(1, len(result_score_df)):
            x.append(round(x[0] + 0.5*i*i))
        
        # block에 따라 score 출력
        # x축: 블록
        # y축: 점수   
        width = 0.5
        c = ['lavenderblush', 'thistle', 'lightpink', 'plum', 'palevioletred']
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
    def grade(self, group_id) :
        score_df = self.print_score_df(group_id)

        user = score_df['user_id'].tolist()
        analysis = score_df['analysis'].tolist()
        contribute = score_df['contribute'].tolist()
        contri = []
        for i in contribute :
            contri.append(round(i/len(contribute), 1))
        outcome =  score_df['outcome'].tolist()
        result = []
        for i in range(len(user)) :
            result.append(int(analysis[i])*(2*int(contri[i])*int(outcome[i])))
        score_df= score_df.drop(['result'], axis = 1)
        score_df['result'] = result
        wks = self.sh.worksheet('title','참여자 정보')        
        for index, row in score_df.iterrows() :
            p_value = list(row)
            wks.update_row(index+2, p_value)