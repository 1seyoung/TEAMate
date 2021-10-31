
from telegram import Update, replymarkup
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext,CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pygsheets import Spreadsheet
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
        if wks.get_value('E'+str(context.user_data['row']))==update.message.text:
            context.user_data['classcode'] = update.message.text
            context.user_data['group_id']= wks.get_value('D'+str(context.user_data['row']))
            context.user_data['next_state'] = "Q1"
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("예", callback_data='yes')],
                [InlineKeyboardButton("아니오", callback_data='no')],
            ])
            return self.qstate_map[context.user_data['next_state']]            
    def Q1(self, update: Update, context: CallbackContext) -> int:
        pass

    def class_group_list(self,class_id):
        
        wks = self.sh.worksheet('title','참여자 정보')

        
        df = wks.get_as_df()
        
        user_data=df.index[df['classcode'] == class_id].tolist()
        

        group_id =wks.get_value('D'+str(user_data[0]+2))
        #user_df = user_df.loc['classcode' == str(class_id)]
        print(group_id)
        return group_id
