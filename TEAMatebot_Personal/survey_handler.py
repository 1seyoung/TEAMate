
from telegram import Update, replymarkup
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext,CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bob_telegram_tools.bot import TelegramBot
from decimal import Decimal
import copy
from pygsheets import *
class SurveyHandler():
    def __init__(self, qstate_map:dict, sh:Spreadsheet):
        self.qstate_map = qstate_map
        print(qstate_map)
        self.sh =sh
        
        #conversationhandler code

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('survey', self.check_user)],
            states={
                self.qstate_map["PWD_CHECKED"]:[
                    MessageHandler(
                        Filters.text & ~(Filters.command), self.handle_check_password
                    )
                ],
                self.qstate_map["CODE_CHECKED"]:[
                    MessageHandler(
                        Filters.text & ~(Filters.command), self.handle_check_classcode
                    )
                ],
                self.qstate_map["Q1"]:[
                    CallbackQueryHandler(self.Q1)
                ],
                self.qstate_map["Q2"]:[
                    CallbackQueryHandler(self.Q2)
                ],
                self.qstate_map["Q3"]:[
                    CallbackQueryHandler(self.Q3)
                ],
                self.qstate_map["SURVEY_FINISHED"]:[
                    CallbackQueryHandler(self.survey_finished)
                ]
                
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
    def get_handler(self) -> Dispatcher:
        return self.handler

    def get_help(self):
        
        return f"/survey 이름 : 동료평가 시작 시 입력해주세요 클릭말고 양식대로 입력해주시기바랍니다. EX)/survey 홍길동"

    def cancel(self, update: Update, context: CallbackContext) -> int:
        #이전으로 돌아가기
        #전체 취소 차이가  코드 차이 알아보기
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END
        
    def check_user(self, update: Update, context: CallbackContext) -> int:
        wks = self.sh.worksheet('title','참여자 정보')
        df =wks.get_as_df()

        user_data = df.index[df['user_id']==update.effective_user.id].tolist()
        if user_data[0]>0:
            update.message.reply_text("등록된 사용자입니다. 동료평가를 진행하려면 비밀번호를 입력해주세요")
            context.user_data['next_state'] = "PWD_CHECKED"
            context.user_data['row'] = user_data[0] + 2
            return self.qstate_map[context.user_data['next_state']]
        else:
            update.message.reply_text("등록되지 않은 사용자입니다. 교수님께 문의하세요.")
            return ConversationHandler.END
    
    def handle_check_password(self, update: Update, context: CallbackContext) -> int:
        wks = self.sh.worksheet('title','참여자 정보')
        if wks.get_value('F'+str(context.user_data['row']))==update.message.text:
            update.message.reply_text("인증 완료! classcode를 입력해주세요")
            context.user_data['next_state'] = "CODE_CHECKED"
            return self.qstate_map[context.user_data['next_state']]
        else:
            update.message.reply_text("비밀번호가 맞지 않습니다. 다시 입력해주세요!")
            context.user_data['next_state'] = "PWD_CHECKED"
            return self.qstate_map[context.user_data['next_state']]

    def handle_check_classcode(self, update: Update, context: CallbackContext) -> int:
        wks = self.sh.worksheet('title','참여자 정보')
        df =wks.get_as_df()
        if wks.get_value('E'+str(context.user_data['row']))==update.message.text:
            context.user_data['classcode'] = update.message.text
            context.user_data['name']=wks.get_value('B'+str(context.user_data['row']))
            context.user_data['group_id']= wks.get_value('D'+str(context.user_data['row']))
            context.user_data['stu_id']= wks.get_value('A'+str(context.user_data['row']))
            context.user_data['next_state'] = "Q1"
            
            
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("예", callback_data='yes')],
                [InlineKeyboardButton("아니오", callback_data='no')],
            ])
            self.__classcode=context.user_data['classcode']
            self.__name=context.user_data['name']
            self.__stuid =context.user_data['stu_id']
            self.__groupid =context.user_data['group_id']
            self.__userid =update.effective_user.id

            team_data_index=df.index[df['classcode'] == self.__classcode].tolist()
            
            self.team_data = {}
            for index in team_data_index:
                team_user_id=wks.get_value('C'+str(index+2))
                team_user_name=wks.get_value('B'+str(index+2))
                self.team_data[team_user_id] = team_user_name
            
            self.user_score = {}
            for key,value in self.team_data.items():
                self.user_score[key]=0
            
            print(self.team_data)
            print(self.user_score)
            update.message.reply_text(text=f"classcode : {self.__classcode}\n학번 : {self.__stuid}\n이름 : {self.__name} \n동료평가를 시작하시겠습니까?",reply_markup=reply_markup)
            return self.qstate_map[context.user_data['next_state']]            
    
    
    def Q1(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        

        if query.data == "yes":
 
            reply_list = [[InlineKeyboardButton("없음",callback_data="none")]]
            for key,value in self.team_data.items():
                reply_list.append([InlineKeyboardButton(value,callback_data=key)])
            reply_markup = InlineKeyboardMarkup(reply_list)   
            
            update.callback_query.message.edit_text(text="무임승차자가 있었나요? 다음 선택지에서 골라주세요", reply_markup=reply_markup)
            
            context.user_data['next_state'] = "Q2"
            return self.qstate_map[context.user_data['next_state']]
        else:
            update.message.reply_text("동료평가를 진행하지않고 종료합니다.")
            return ConversationHandler.END
    
    def Q2(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        for key,value in self.user_score.items():
            if query.data == key:
                self.user_score[key] = -2
            else:
                pass
        print("Q1")
        print(self.user_score)
        reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("상",callback_data="s")],
                [InlineKeyboardButton("중",callback_data="j")],
                [InlineKeyboardButton("하",callback_data="h")]
                ])  
        q_data= self.team_data
        q_data.pop(str(self.__userid))
        print(q_data)  
        for key,value in q_data.items():
            update.callback_query.message.edit_text(text=f"{value}의 기여도를 상중하 중에서 골라주세요",reply_markup=reply_markup)
        
            aquery = update.callback_query
            print(aquery)
            for key,value in self.user_score.items():
                if aquery.data == "s":

                    self.user_score[key] = value +5

                elif aquery.data == "j":

                    self.user_score[key] = value +4
                
                elif aquery.data == "h":

                    self.user_score[key] = value +3
                else:
                    pass

        print("Q2")
        print(self.user_score)
        context.user_data['next_state'] = "Q3"
        return self.qstate_map[context.user_data['next_state']]
           

    def Q3(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        print(query)
        reply_list = [[InlineKeyboardButton("없음",callback_data="none")]]
        for key,value in self.team_data.items():
            if value == update.effective_user.id:
                pass
            else:
                reply_list.append([InlineKeyboardButton(value,callback_data=key)])
        reply_markup = InlineKeyboardMarkup(reply_list)          
        

        update.callback_query.message.edit_text(text="가장 높은 기여를 이룬 참가자를 골라주세요", reply_markup=reply_markup)
        query = update.callback_query
        for key,value in self.user_score.items():
            if query.data == key:

                self.user_score[key] = value +2
            else:
                pass
        print("Q3")
        print(self.user_score)
        context.user_data['next_state'] = "SURVEY_FINISHED"
        return self.qstate_map[context.user_data['next_state']] 

    def survey_finished(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query

        for key,value in self.user_score.items():
            if query.data == key:

                self.user_score[key] = value +2
            else:
                pass
        print("Q3")
        print(self.user_score)
        update.callback_query.message.edit_text(text="동료평가를 종료합니다.")
        print(self.user_score)
        user = self.user_score
        group = self.__groupid
        self.contribute_up(user, group)
        return ConversationHandler.END
    def print_score_df(self, group_id): ## group id를 넣으면 group id만 있는 pandas 출력
        wks = self.sh.worksheet('title','팀평가')
        score_df = wks.get_as_df()
        score_df = score_df.loc[score_df['group_id'] == group_id]
        return score_df
    def contribute_up(self, score, group_id) : ## group id랑 새로운 score -> dictionary를 넣으면 이전의 데이터베이스 값과 합쳐서 입력
        score_df = self.print_score_df(group_id)
        print(score_df)
        contribute = score_df['contribute'].tolist()
        key_ = list(score.keys())

        print("why?")
        print(score)
        print(score_df)
        for idx, i in enumerate(key_) :
            contribute[idx] += score[i]
        score_df = score_df.drop(['contribute'], axis =1)
        print(score_df)
        score_df.insert(3, 'contribute', contribute)
        json_file_name = 'fit-union-324504-8305b813e2b8.json'
        pd.set_option('mode.chained_assignment',  None)
        spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-FrwLOMx47lTOZuQZfxKdHxDl1w-HC0AvYhXv22LWGM/edit?usp=sharing'

        gc = authorize(service_file=json_file_name)
        sh = gc.open('TM_DB')
        wks = sh.worksheet('title','팀평가')
        
        for index, row in score_df.iterrows() :
            p_value = list(row)
            wks.update_row(index+2, p_value)
    

