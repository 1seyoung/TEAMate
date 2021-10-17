#데이터 수집
import pygsheets
import re

from telegram import Update
from telegram.ext import Updater, CallbackContext,MessageHandler,Filters,CommandHandler

from config import *
from instance.config import *

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class TEAMatebot():
    def __init__(self, telegram_key:str, google_service_key:str, sheet_name:str)->None:
        self.gc = pygsheets.authorize(service_file=google_service_key)
        self.sh = self.gc.open(sheet_name)
        
        self.updater=Updater(telegram_key)
        dp = self.updater.dispatcher

        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.collect_msg))

        #for handler in self.handlers:
            #dp.add_handler(handler.get_handler())
        
        #dp.add_handler(CommandHandler('start', self.start))

    def collect_msg(self,update: Update, context: CallbackContext) -> None:
        if update.message.chat_id < 0:
            
            wks = self.sh.worksheet('title','chat_data')
            chat_data_df = wks.get_as_df()
            preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', update.message.text)
            wks.update_value('A' + str(len(chat_data_df)+2), str(update.message.date))
            wks.update_value('B' + str(len(chat_data_df)+2), update.message.chat_id)
            wks.update_value('C' + str(len(chat_data_df)+2), update.effective_user.id)        
            wks.update_value('D' + str(len(chat_data_df)+2), preprocessing_chat)
        else:
            pass
    def execute(self):

        self.updater.start_polling()
        self.updater.idle()       

    def start(self, update: Update, context: CallbackContext) -> None:
        #command /start

        context.user_data.clear()

        resp = "/info : TEAMate가 무엇인지 알고싶으면 클릭해주세요\n/register_info  :  프로젝트 관리에 필요한 개인정보를 등록해야합니다.자세한 방법을 알고싶으면 클릭해주세요\n/calss_code  : 교수님께 받은 수업 코드를 입력해주세요 모든 팀원이 한 번 씩 입력해야합니다!"
        update.message.reply_text(resp)    
    
    def info(self, update: Update, context: CallbackContext) -> None:

        resp = "/info : TEAMate란 "
        update.message.reply_text(resp) 


if __name__ == "__main__":  
    tb = TEAMatebot(TELEGRAM_API_KEY_COLLECT, GOOGLE_SERVICE_KEY, GOOGLE_SPREAD_SHEET)
    tb.execute()