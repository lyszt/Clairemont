import json
import token
import os

from Methods.system_methods import console_log


class AcquireKey():

    def get_key(self):
        token_file = "token.json"
        if os.path.isfile(token_file) and os.access(token_file, os.R_OK):
            console_log("Token detected.")
            with open(token_file, "r") as file:
                token_data = json.load(file)
                bot_token = token_data.get("token")
                ai_token = token_data.get("openaitoken")
                voice_token = token_data.get("elevenlabsapikey")
                keys = {"bot_token": bot_token, "ai_token": ai_token, "voice_token": voice_token}
            return keys
        else:
            console_log("Token not found.")
            return None
