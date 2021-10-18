from telegram.ext.conversationhandler import ConversationHandler
import contexts
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

#2021.08.26
from system_simulator import SystemSimulator
from behavior_model_executor import BehaviorModelExecutor
from system_message import SysMessage
from definition import *

from telegram_model import TelegramModel as TM
import pygsheets
import signal
from config import *
from instance.config import *
import re
import sys,os

'''
# Simulation Configuration


se.get_engine("sname").simulate()'''

class TelegramManager():
	def __init__(self, telegram_states:list,engine, tel_token):
		self.se = engine
		self.updater = Updater(tel_token)

		signal.signal(signal.SIGINT,  self.signal_handler)
		signal.signal(signal.SIGABRT, self.signal_handler)
		signal.signal(signal.SIGTERM, self.signal_handler)

		self.is_terminating = False

		model = TM(0, Infinite, "tm", "sname", self.updater)

		self.se.coupling_relation(None, "start", model, "start")
		self.se.coupling_relation(None, "msg", model, "msg")

		self.se.register_entity(model)
		self.state_map ={state:idx for idx, state in enumerate(telegram_states)}

	def greet(self, update: Update, context: CallbackContext) -> None:
		"""Send a message when the command /start is issued."""
		user = update.effective_user
		update.message.reply_markdown_v2(
		    fr'Hi {user.mention_markdown_v2()}\!',
		    reply_markup=ForceReply(selective=True),
		)

	def update_freq(self, update: Update, context: CallbackContext) -> None:
		print(update.message.text)
		user = update.effective_user
		tokens = update.message.text.split(" ")
		#self.se.simulate()
		self.se.insert_external_event("msg", [float(tokens[1]), user.id])

	def start(self) -> None:
		"""Start the bot."""
		# Create the Updater and pass it your bot's token.

		# Get the dispatcher to register handlers
		dispatcher = self.updater.dispatcher

		# on different commands - answer in Telegram
		dispatcher.add_handler(CommandHandler("start", self.greet))
		dispatcher.add_handler(CommandHandler("update", self.update_freq))
		dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.collect_msg))
		dispatcher.add_handler(ConversationHandler(
			entry_points=[CommandHandler("class_code", self.info_call_classcodeHandler)],states={
				self.state_map["GET_CLASS_CODE"]:[CommandHandler("classcode_add",self.handler_classcode_add)]
			}))
		# Start the Bot

		self.updater.start_polling()
		self.se.simulate()

	def collect_msg(self, update: Update, context: CallbackContext) -> None:
		print("SDF")

		msg = []
		preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', update.message.text)
		
		msg.append(preprocessing_chat)
		msg.append(str(update.message.date))
		msg.append((update.message.chat_id))
		msg.append((update.effective_user.id))

		self.se.insert_custom_external_event("msg", msg)

	def info_call_classcodeHandler(self, update: Update, context: CallbackContext) -> int:
		update.message.reply_text("비밀번호를 입력해주세요.")
		if (row := self.check_registered_user(update.message.text)) > 0:
			context.user_data['gs_user_row']=row
			update.message.reply_text("팀 코드를 등록하려면 /clsscode_add 를 클릭하세요.\n 취소하려면 /cancel을 클릭하세요.")

			return self.state_map["GET_CLASS_CODE"]
		else:
			update.message.reply_text("@teamate_user_setting_bot 을 통해 사용자 등록을 먼저 하시길 바랍니다.")
			return ConversationHandler.END

	def check_registered_user(self, pwd:str) -> int:

		gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
		sh = gc.open(GOOGLE_SPREAD_SHEET)
		wks = sh.worksheet('title','참여자 정보')
		df = wks.get_as_df()
		user_data = df.index[df['password]'] == pwd].tolist()
		if user_data:
			return user_data[0]
		else:
			return -1

	def check_classcode(self, _id:int) -> bool:
		gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
		sh = gc.open(GOOGLE_SPREAD_SHEET)
		wks = sh.worksheet('title','참여자 정보')
		df = wks.get_as_df()
		user_data = df.index[df['user_id]'] == update.effective_user.id].tolist()
		if user_data:
			return user_data[0]
		else:
			return -1

	def handler_classcode_add(self, update: Update, context: CallbackContext) -> int:
		update.message.reply_text("Classcode를 입력해주세요.")
		if self.check_classcode(update.effective_user.id)):
			pass

	def signal_handler(self, sig, frame):
		print("Terminating Monitoring System")
		
		if not self.is_terminating:
			self.is_terminating = True
			self.updater.stop()
			del self.se
		
		sys.exit(0)