
from telegram import Update
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext


from pygsheets import Spreadsheet
class SurveyHandler():
    def __init__(self, state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        print(state_map)
        self.sh =sh

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('survey', self.survey_start)],
            states={
                self.state_map["GET_STUDENT_ID"]: [
                    MessageHandler(
                        Filters.regex(r'\d{8}'), self.check_user
                    ),
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex(r'\d{8}')), self.wrong_data),
                ],
                self.state_map["ID_CHECKED"]: [
                    MessageHandler(
                        Filters.text & ~(Filters.command), self.check_pwd
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],)

    def get_handler(self) -> Dispatcher:
        return self.handler

    def get_help(self):
        
        return f"/team_register :  자신의 정보와 참가중인 팀 정보를 등록합니다. 그룹 채팅방에서는 사용할 수 없습니다. 봇을 친구 추가한 뒤 대화를 걸고 이용해주세요"

    def cancel(self, update: Update, context: CallbackContext) -> int:
        #이전으로 돌아가기
        #전체 취소 차이가  코드 차이 알아보기
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END
        
    def register_start(self,update: Update, context: CallbackContext) -> int:
        if update.message.chat_id < 0:
            context.bot.send_message(chat_id=update.message.chat_id, text="그룹채팅방에서는 사용할 수 없는 기능입니다. \n TEAMAtebot과의 개인 채팅을 이용해주세요 ")
        else:
            update.message.reply_text("학번을 입력해주세요.")
            context.user_data['next_state'] = "GET_STUDENT_ID"
            return self.state_map[context.user_data['next_state']]