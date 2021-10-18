from system_simulator import SystemSimulator
from behavior_model_executor import BehaviorModelExecutor
from system_message import SysMessage
from definition import *

import pygsheets

from config import *
import re

class TelegramModel(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name, updater):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("IDLE")
        self.insert_state("IDLE", Infinite)
        self.insert_state("WAKE", 2)
  
        self.insert_input_port("msg")

        self.recv_msg = []
        self.updater = updater
         
    def ext_trans(self,port, msg):
        if port == "msg":
            print("[Model] Received Msg")
            self._cur_state = "WAKE"
            self.recv_msg.append(msg.retrieve())
            self.cancel_rescheduling()
                        
    def output(self):
        if self._cur_state == "WAKE":
            for _ in range(30):
                if self.recv_msg:
                    msg = self.recv_msg.pop(0)
                    gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
                    sh = gc.open(GOOGLE_SPREAD_SHEET)
                    wks = sh.worksheet('title','chat_data')
                    chat_data_df = wks.get_as_df()
                    #print(stu_list_df)
                    preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', msg[0])
                    wks.update_value('A' + str(len(chat_data_df)+2), msg[1])
                    wks.update_value('B' + str(len(chat_data_df)+2), msg[2])
                    wks.update_value('C' + str(len(chat_data_df)+2), msg[3])        
                    wks.update_value('D' + str(len(chat_data_df)+2), preprocessing_chat)
                
            #self.recv_msg = []
            pass

    def int_trans(self):
        if self._cur_state == "WAKE":
            self._cur_state = "IDLE"
    
    def __del__(self):
        pass