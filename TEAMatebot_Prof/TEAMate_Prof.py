#데이터 수집
import pygsheets
import re

from telegram import Update
from telegram.ext import Updater, CallbackContext,MessageHandler,Filters,CommandHandler

from scoreCheck_handler import scoreCheckHandler
#from register_handler import RegisterHandler
#from survey_handler import SurveyHandler

from states import STATES
from decimal import Decimal

from bob_telegram_tools.bot import TelegramBot
import matplotlib.pyplot as plt
from config import *
from instance.config import *

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class TEAMatebot_Prof():
    def __init__(self, telegram_states:list, telegram_key:str, google_service_key:str, sheet_name:str)->None:
        self.gc = pygsheets.authorize(service_file=google_service_key)
        self.sh = self.gc.open(sheet_name)
        
        self.updater=Updater(telegram_key)
        dp = self.updater.dispatcher
        print("telegram teamate setting")
 
 
        self.state_map ={state:idx for idx, state in enumerate(telegram_states)}
        print(self.state_map)
        self.handlers =[
                        scoreCheckHandler(self.state_map,self.sh)
                        #SurveyHandler(self.state_map,self.sh)
                        #InitHandler(self.state_map,self.sh)
        ]

        for handler in self.handlers:
            dp.add_handler(handler.get_handler())
        
        dp.add_handler(CommandHandler('start', self.start))     

    def start(self, update: Update, context: CallbackContext) -> None:
        #command /start

        context.user_data.clear()

        resp = ""
        for handler in self.handlers:
            resp += handler.get_help()
            resp += "\n"
        update.message.reply_text(resp)  
        #chat_id =((update.effective_user.id))

    def execute(self):

        self.updater.start_polling()
        self.updater.idle()
               


if __name__ == "__main__":
    tb = TEAMatebot_Prof(STATES, TELEGRAM_API_KEY_PROF, GOOGLE_SERVICE_KEY, GOOGLE_SPREAD_SHEET)
    tb.execute()