
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from pygsheets import Spreadsheet

class InitHandler():
    def __init__(self,state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        self.sh = sh

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('init', self.handle_init_start)],
            states={
                self.state_map["GET_STUDENT_ID"]: [
                    MessageHandler(
                        Filters.regex(r'\d{5}'), self.handle_change_password
                    ),
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex(r'\d{5}')), self.handle_unwanted_data),
                ],
                self.state_map["GET_NEW_PWD"]: [
                    MessageHandler(
                        Filters.text & ~(Filters.command), self.handle_register_password
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

    def get_handler(self) -> Dispatcher:
        return self.handler
    
    def get_help(self):
        return f"/init: 다른 사람은 개인 점수를 확인하지 않도록 자기만의 암호를 등록합니다. 평소 사용하지 않는 암호를 사용하기 바랍니다."

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """Display the gathered info and end the conversation."""
        context.user_data.clear()
        return ConversationHandler.END

    def check_valid_user(self, user_id:int) -> int:
        wks = self.sh.worksheet('title','참여자 정보')
        df = wks.get_as_df()

        user_data = df.index[df['학번'] == user_id].tolist()
        if user_data:
            return user_data[0]
        else:
            return -1

    def check_register_user(self, idx:int) -> bool:
        wks = self.sh.worksheet('title','참여자 정보')
        #print(type(wks.get_value('E'+str(idx))))
        if int(wks.get_value('F'+str(idx))) != 0:
            return True
        else:
            return False

    def handle_unwanted_data(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("다시 입력해주세요.")
        return self.state_map[context.user_data['next_state']]
    
    def handle_init_start(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("학번을 입력해주세요.")
        context.user_data['next_state'] = "GET_STUDENT_ID"
        return self.state_map[context.user_data['next_state']]

    def handle_change_password(self, update: Update, context: CallbackContext) -> int:
        user_id = int(update.message.text)
        
        if (row := self.check_valid_user(user_id)) > 0:
            context.user_data['id'] = user_id        
            context.user_data['row'] = row +2

            if self.check_register_user(context.user_data['row']):
                update.message.reply_text("이미 등록되어 있는 사용자입니다.\n비밀번호를 초기화하기 위해서는 담당교수님께 연락바랍니다.")
                context.user_data.clear()
                return ConversationHandler.END
            else:
                context.user_data['next_state'] = "GET_NEW_PWD"

                update.message.reply_text("변경할 비밀번호를 입력해주세요. \n평소에 사용하는 비밀번호를 사용하면 안됩니다.\n비밀번호를 공유할 경우 발생하는 문제는 개인책임입니다.")
                return self.state_map[context.user_data['next_state']]
        else:
            update.message.reply_text("수강신청 등록이 안된 사용자입니다.\n담당교수님께 확인하시길 바랍니다.")
            context.user_data.clear()
            return ConversationHandler.END

    def handle_register_password(self, update: Update, context: CallbackContext) -> int:
        wks = self.sh.worksheet('title','참여자 정보')
        wks.update_value('F'+str(context.user_data['row']), update.message.text)
        
        update.message.reply_text("새로운 비밀번호가 등록되었습니다.\n사용자등록을 해주시길 바랍니다.")
        
        context.user_data.clear()
        return ConversationHandler.END
