from telegram import Update
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext


from pygsheets import Spreadsheet
class RegisterHandler():
    
    def __init__(self, state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        self.sh =sh

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('team_register',self.register_start)]
        )

    def get_handler(self) -> Dispatcher:
        return self.handler

    def get_help(self):
        return f"/team_register :  자신의 정보와 참가중인 팀 정보를 등록합니다."

    def cancle(self, update: Update, context: CallbackContext) -> int:
        #이전으로 돌아가기
        #전체 취소 차이가  코드 차이 알아보기
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END
    
    def register_start(self,update: Update, context: CallbackContext) -> int:
        update.message.reply_text("학번을 입력해주세요.")
        context.user_data['next_state']="GET_STUDENT_ID"
        return self.state_map[context.user_data["next_state"]]