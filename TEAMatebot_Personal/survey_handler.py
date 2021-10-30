
from telegram import Update
from telegram.ext import Dispatcher,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext


from pygsheets import Spreadsheet
class SurveyHandler():
    def __init__(self, qstate_map:dict, sh:Spreadsheet):
        self.qstate_map = qstate_map
        print(qstate_map)
        self.sh =sh

        #conversationhandler code

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('survey', self.handle_score_check)],
            states={
                self.qstate_map["Q1"]:[
                    MessageHandler(Filters.regex(r'\w+'), self.handle_check_team)
                ],
                self.qstate_map["Q2"]: [
                    CommandHandler(
                        'teamscore', self.get_graph
                    )
                ],
                self.qstate_map["Q3"]: [
                    CommandHandler(
                        'teamscore', self.get_graph
                    )
                ],
                self.qstate_map["Q4"]: [
                    CommandHandler(
                        'teamscore', self.get_graph
                    )
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
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
        
