from telegram.ext.conversationhandler import ConversationHandler
import contexts
from telegram import Update, ForceReply, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

#2021.08.26
from system_simulator import SystemSimulator
from behavior_model_executor import BehaviorModelExecutor
from system_message import SysMessage
from definition import *
from states import STATES
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
	def __init__(self,engine, tel_token):
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
		self.state_map ={state:idx for idx, state in enumerate(STATES)}

	def greet(self, update: Update, context: CallbackContext) -> None:
		"""Send a message when the command /start is issued."""
		update.message.reply_text("안녕하세요 TEAMate의 그룹 봇입니다.\n먼저 @teamate_user_setting_bot 을 통해 사용자 등록을 해주세요!\n등록 후 /info_teamate 를 클릭하여 그룹 봇의 사용법을 확인하세요")

	def info(self, update: Update, context: CallbackContext) -> None:
		"""Send a message when the command /start is issued."""
		update.message.reply_text("사용자 등록을 끝내셨나요?\n그렇다면 팀 등록을 진행합니다.\n/classcode 를 클릭하여 모두 서버에 팀을 등록해야합니다. 모든 학생이 실행해주세요\n")

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
		dispatcher.add_handler(CommandHandler("info_teamate", self.info))
		dispatcher.add_handler(CommandHandler("update", self.update_freq))
		dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.collect_msg))
		dispatcher.add_handler(MessageHandler(Filters.photo& ~Filters.command,self.collect_photo))
		dispatcher.add_error_handler(MessageHandler(Filters.document& ~Filters.command, self.collect_file))
		dispatcher.add_handler(ConversationHandler(
			entry_points=[CommandHandler("classcode", self.handle_register_start)],states={
				self.state_map["GET_STUDENT_ID"]:[CommandHandler("code_add",self.get_stu_id)]
			},fallbacks=[CommandHandler('cancel', self.cancel)],))
		# Start the Bot
		self.updater.start_polling()
		self.se.simulate()
		
	def collect_photo(self, update: Update, context: CallbackContext) -> None:
		msg = []
		preprocessing_chat = "photophotophotophoto_hellophoto___"
		
		msg.append(preprocessing_chat)
		msg.append(str(update.message.date))
		msg.append((update.message.chat_id))
		msg.append((update.effective_user.id))

		self.se.insert_custom_external_event("msg", msg)

	def collect_file(self, update: Update, context: CallbackContext) -> None:
		msg = []
		preprocessing_chat = "filefilefilefilefilefile_hellofile___"
		
		msg.append(preprocessing_chat)
		msg.append(str(update.message.date))
		msg.append((update.message.chat_id))
		msg.append((update.effective_user.id))

		self.se.insert_custom_external_event("msg", msg)

	def collect_msg(self, update: Update, context: CallbackContext) -> None:
		print("SDF")

		msg = []
		preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', update.message.text)
		
		msg.append(preprocessing_chat)
		msg.append(str(update.message.date))
		msg.append((update.message.chat_id))
		msg.append((update.effective_user.id))

		self.se.insert_custom_external_event("msg", msg)

	def cancel(self, update: Update, context: CallbackContext) -> int:
		"""Display the gathered info and end the conversation."""
		context.user_data.clear()
		update.message.reply_text("취소 되었습니다.")
		return ConversationHandler.END
	
	def handle_register_start(self, update: Update, context: CallbackContext) -> int:
		update.message.reply_text("팀 코드를 등록하려면 /code_add 를 클릭하세요.\n 취소하려면 /cancel 을 클릭하세요..")
		context.user_data['next_state'] = "GET_STUDENT_ID"
		
		return self.state_map[context.user_data['next_state']]
	
	def get_stu_id(self, update: Update, context: CallbackContext) -> None:
		update.message.reply_text("등록을 진행합니다")
		print(update.message.chat.title)
		self.classcode_add(update.message.chat.title,update.effective_user.id,update.message.chat_id)

		update.message.reply_text("등록이 완료되었습니다.")

		
	def classcode_add(self, classcode,user_id,group_id) -> None:
		gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
		sh = gc.open(GOOGLE_SPREAD_SHEET)
		wks = sh.worksheet('title','참여자 정보')
		df = wks.get_as_df()
		user_data=df.index[df['user_id'] == user_id].tolist()
		
		wks.update_value('E' + str(user_data[0]+2), str(classcode))
		wks.update_value('D' + str(user_data[0]+2), str(group_id))

		

	def signal_handler(self, sig, frame):
		print("Terminating Monitoring System")
		
		if not self.is_terminating:
			self.is_terminating = True
			self.updater.stop()
			del self.se
		
		sys.exit(0)