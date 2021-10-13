#데이터 수집
import pygsheets
import re

from telegram import Update
from telegram.ext import Updater, CallbackContext,MessageHandler,Filters

from scoreCheck_handler import scoreCheckHandler
from register_handler import RegisterHandler
from survey_handler import SurveyHandler

from states import STATES

from config import *
from instance.config import *

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class TEAMatebot():
    def __init__(self, telegram_states:list, telegram_key:str, google_service_key:str, sheet_name:str)->None:
        self.gc = pygsheets.authorize(service_file=google_service_key)
        self.sh = self.gc.open(sheet_name)
        
        self.updater=Updater(TELEGRAM_API_KEY)
        dp = self.updater.dispatcher

        print("start")
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.collect_msg))
        print("_start")
        self.state_map ={state:idx for idx, state in enumerate(telegram_states)}
        self.handlers =[
                        scoreCheckHandler(self.state_map,self.sh),
                        RegisterHandler(self.state_map,self.sh),
                        SurveyHandler(self.state_map,self.sh)
        ]

        for handler in self.handlers:
            dp.add_handler(handler.get_handler())

    def collect_msg(self,update: Update, context: CallbackContext) -> None:
        print("collect")
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
        print("execute")
        self.updater.start_polling()
        self.updater.idle()       

    def start(self, update: Update, context: CallbackContext) -> None:
        #command /start

        context.user_data.clear()

        resp = ""
        for handler in self.handlers:
            resp += handler.get_help()
            resp += "\n"
        update.message.reply_text(resp)    



if __name__ == "__main__":
    tb = TEAMatebot(STATES, TELEGRAM_API_KEY, GOOGLE_SERVICE_KEY, GOOGLE_SPREAD_SHEET)
    tb.execute()