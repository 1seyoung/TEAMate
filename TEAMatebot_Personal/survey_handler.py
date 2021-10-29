
from telegram import Update
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext


from pygsheets import Spreadsheet
class SurveyHandler():
    def __init__(self, state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        print(state_map)
        self.sh =sh

        #conversationhandler code

    def get_handler(self) -> Dispatcher:
        return self.handler

    def get_help(self):
        
        return f"/survey :  동료평가 시작 시 클릭해주세요!"

    def cancel(self, update: Update, context: CallbackContext) -> int:
        #이전으로 돌아가기
        #전체 취소 차이가  코드 차이 알아보기
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END
        
