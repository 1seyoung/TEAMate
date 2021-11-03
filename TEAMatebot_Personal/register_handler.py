
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from pygsheets import Spreadsheet

class RegisterHandler():
    def __init__(self,state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        self.sh = sh

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('register', self.handle_register_start)],
            states={
                self.state_map["GET_STUDENT_ID"]: [
                    MessageHandler(
                        Filters.regex(r'\d{5}'), self.handle_check_user
                    ),
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex(r'\d{5}')), self.handle_unwanted_data),
                ],
                self.state_map["ID_CHECKED"]: [
                    MessageHandler(
                        Filters.text & ~(Filters.command), self.handle_check_password
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

    def get_handler(self) -> Dispatcher:
        return self.handler
    
    def get_help(self):
        return f"/register: Tutor봇으로 사용자 등록을 합니다. 다른 사람은 개인 점수를 확인하지 않도록 변경한 암호를 확인합니다."

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """Display the gathered info and end the conversation."""
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END

    def handle_unwanted_data(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("다시 입력해주세요.")
        return self.state_map[context.user_data['next_state']]
    
    def handle_register_start(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("학번을 입력해주세요.")
        context.user_data['next_state'] = "GET_STUDENT_ID"
        return self.state_map[context.user_data['next_state']]

    def check_valid_user(self, user_id:int) -> bool:
        wks = self.sh.worksheet('title','참여자 정보')
        df = wks.get_as_df()

        user_data = df.index[df['학번'] == user_id].tolist()
        if user_data:
            return user_data[0]
        else:
            return -1

    def handle_check_user(self, update: Update, context: CallbackContext) -> int:
        user_id = int(update.message.text)
        if (row := self.check_valid_user(user_id)) >= 0:
            context.user_data['id'] = user_id        
            context.user_data['row'] = row + 2
            context.user_data['next_state'] = "ID_CHECKED"

            update.message.reply_text("비밀번호를 입력해주세요.")
            return self.state_map[context.user_data['next_state']]
        else:
            update.message.reply_text("수강신청 등록이 안된 사용자입니다.\n담당교수님께 확인하시길 바랍니다.")
            context.user_data.clear()
            return ConversationHandler.END

    def check_pasword(self, idx:int, pwd:str) -> bool:
        wks = self.sh.worksheet('title','참여자 정보')
        if wks.get_value('F'+str(idx)) == pwd:
            return True
        else:
            return False

    def handle_check_password(self, update: Update, context: CallbackContext) -> int:
        if self.check_pasword(context.user_data['row'], update.message.text):
            wks = self.sh.worksheet('title','참여자 정보')
            wks.update_value('C'+str(context.user_data['row']), update.effective_user.id)


            update.message.reply_text("챗봇 서비스에 등록되었습니다. 팀 채팅 방에서 classcode 등록을 진행해 주시길 바랍니다.")
        else:
            update.message.reply_text("비밀번호가 맞지 않습니다. \n다시 시작하길 바랍니다.")
        
        context.user_data.clear()
        return ConversationHandler.END
