import os
from datetime import datetime

# --- Bot Credentials ---
API_ID = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"
BOT_TOKEN = "8411080834:AAE85QH-LpaiOpht-RSMpwYQPus1jHONnu4"
SESSION_STRING = "BQE-4i0ASxu8TXk4s870tFMn-D2Ijs-7DaTep8qcmRnZuowGYTiKDzzy9fKRT3pCc7aFI9oql0Rp5k1FkymDhRbewYPN11p5G7exMCs-z2bdMPuRoJCF60r7p_xq0TBjtLw5P1f-pXHHRxeXSAq0nKyNglv2pZ-GVCbYL4J-OwIkfck4wZyfiU0H58LZla5Il4VmVww-ewK3roa4mVjIxGKYoFva7LqYEf9Iti77jLz7HW7gCfuNessLDXqH1se4DuOSmoJzbacJxofENDQJChGjP4K7gbkMQQKwjCQfndvTmHLyDnc5jDqwfngZK1ogepmyiXZhhzHVebIieznK4DXTM1Q7pAAAAAHKarFXAA"
# --- Random image links ---" # Apni session string yahan puri daal dena

# --- Global Tracking ---
queues = {}
playing_messages = {} # {chat_id: message_id} - Timer edit karne ke liye
current_playing = {} # {chat_id: song_details} - Currently playing track ke liye
BOT_START_TIME = datetime.now()
