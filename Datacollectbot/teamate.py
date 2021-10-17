import contexts
from config import *

from telegram_mgr import TelegramManager

from system_simulator import SystemSimulator
from behavior_model_executor import BehaviorModelExecutor
from system_message import SysMessage
from definition import *

# System Simulator Initialization
se = SystemSimulator()

se.register_engine("sname", SIMULATION_MODE, TIME_DENSITY)

se.get_engine("sname").insert_input_port("start")
se.get_engine("sname").insert_input_port("msg")

# Telegram Manager Initialization
tm = TelegramManager(se.get_engine("sname"), TELEGRAM_API_KEY)

# Monitoring System Start
tm.start()