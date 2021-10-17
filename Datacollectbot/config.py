import contexts
# SIMULATION_MODE
SIMULATION_MODE = "REAL_TIME"
TIME_DENSITY = 1

TELEGRAM_API_KEY_COLLECT ="YOUR-TELEGRAM-BOT-KEY-COLLECT"
# Stores credential information
TELEGRAM_API_KEY='YOUR-TELEGRAM-BOT-KEY'

# Google Drive API, credentials
GOOGLE_SERVICE_KEY='YOUR-GOOGLE-SERVICE-KEY.json'

# Google Drive API, credentials
GOOGLE_SPREAD_SHEET='YOUR-GOOGLE-SPREADSHEET-NAME'

import os
if os.path.isfile("../instance/config.py"):
	from instance.config import *