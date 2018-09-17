from Kamisu66 import EthicsCommittee
import traceback
import re
import sys
import time
import random
import json


def main(data):
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        EC = EthicsCommittee(chat_id, user_id)
        first_name = message["from"]["first_name"]
        message_id = message["message_id"]
        reply_to_message_id = ""
        reply_to_user_id = ""
        if "reply_to_message" in message:
            reply_to_message = message["reply_to_message"]
            reply_to_message_id = reply_to_message["message_id"]
            reply_to_user_id = reply_to_message["from"]["id"]
            if "first_name" in reply_to_message["from"]:
                reply_to_first_name = reply_to_message["from"]["first_name"]
            else:
                reply_to_first_name = ""
            if "last_name" in reply_to_message["from"]:
                reply_to_last_name = reply_to_message["from"]["last_name"]
            else:
                reply_to_last_name = ""
        date = message["date"]
        try:
            if "text" in message:
                EC.addmessage(user_id, message_id, first_name, "text",
                              message["text"], date, reply_to_message_id,
                              reply_to_user_id)
            elif "sticker" in message:
                EC.addmessage(user_id, message_id, first_name, "sticker",
                              message["sticker"]["file_id"], date,
                              reply_to_message_id, reply_to_user_id)
            elif "document" in message:
                EC.addmessage(user_id, message_id, first_name, "document",
                              message["document"]["file_id"], date,
                              reply_to_message_id, reply_to_user_id)
                if "caption" in message:
                    EC.addmessage(user_id, message_id, first_name, "caption",
                                  message["caption"], date,
                                  reply_to_message_id, reply_to_user_id)
            elif "voice" in message:
                EC.addmessage(user_id, message_id, first_name, "voice",
                              message["voice"]["file_id"], date,
                              reply_to_message_id, reply_to_user_id)
            elif "photo" in message:
                EC.addmessage(user_id, message_id, first_name, "photo",
                              message["photo"][-1]["file_id"], date,
                              reply_to_message_id, reply_to_user_id)
                if "caption" in message:
                    EC.addmessage(user_id, message_id, first_name, "caption",
                                  message["caption"], date,
                                  reply_to_message_id, reply_to_user_id)
            elif "video" in message:
                EC.addmessage(user_id, message_id, first_name, "video",
                              message["video"]["file_id"], date,
                              reply_to_message_id, reply_to_user_id)
                if "caption" in message:
                    EC.addmessage(user_id, message_id, first_name, "caption",
                                  message["caption"], date,
                                  reply_to_message_id, reply_to_user_id)
            elif "video_note" in message:
                EC.addmessage(user_id, message_id, first_name, "video_note",
                              message["video_note"]["file_id"], date,
                              reply_to_message_id, reply_to_user_id)
            elif "contact" in message:
                EC.addmessage(user_id, message_id, first_name, "contact",
                              json.dumps(message["contact"]), date,
                              reply_to_message_id, reply_to_user_id)
            elif "venue" in message:
                EC.addmessage(user_id, message_id, first_name, "venue",
                              json.dumps(message["venue"]), date,
                              reply_to_message_id, reply_to_user_id)
            elif "location" in message:
                EC.addmessage(user_id, message_id, first_name, "location",
                              json.dumps(message["location"]), date,
                              reply_to_message_id, reply_to_user_id)
            elif "new_chat_member" in message:
                EC.addmessage(user_id, message_id, first_name,
                              "new_chat_member",
                              message["new_chat_member"]["id"], date,
                              reply_to_message_id, reply_to_user_id)
            elif "left_chat_member" in message:
                EC.addmessage(user_id, message_id, first_name,
                              "left_chat_member",
                              message["left_chat_member"]["id"], date,
                              reply_to_message_id, reply_to_user_id)
            elif "pinned_message" in message:
                EC.addmessage(user_id, message_id, first_name,
                              "pinned_message",
                              message["pinned_message"]["message_id"], date,
                              reply_to_message_id, reply_to_user_id)
            elif "new_chat_title" in message:
                EC.addmessage(user_id, message_id, first_name,
                              "new_chat_title", message["new_chat_title"],
                              date, reply_to_message_id, reply_to_user_id)
            elif "new_chat_photo" in message:
                EC.addmessage(user_id, message_id, first_name,
                              "new_chat_photo",
                              message["new_chat_photo"][-1]["file_id"], date,
                              reply_to_message_id, reply_to_user_id)
            elif "delete_chat_photo" in message:
                EC.addmessage(user_id, message_id, first_name,
                              "delete_chat_photo", "", date,
                              reply_to_message_id, reply_to_user_id)
            else:
                EC.addmessage(user_id, message_id, first_name, "unknown",
                              json.dumps(message), date, reply_to_message_id,
                              reply_to_user_id)
        except Exception as e:
            traceback.print_exc()
            EC.log("[record] "+traceback.format_exc())

    elif "edited_message" in data:
        pass

    elif "channel_post" in data:
        message = data["channel_post"]
        chat_id = message["chat"]["id"]
        user_id = ""
        EC = EthicsCommittee(chat_id, user_id)
        first_name = ""
        message_id = message["message_id"]
        reply_to_message_id = ""
        reply_to_user_id = ""
        if "reply_to_message" in message:
            reply_to_message = message["reply_to_message"]
            reply_to_message_id = reply_to_message["message_id"]
        date = message["date"]
        try:
            if "text" in message:
                EC.addmessage(user_id, message_id, first_name, "text",
                              message["text"], date, reply_to_message_id,
                              reply_to_user_id)
            else:
                EC.log("[record] "+json.dumps(data))
        except Exception as e:
            traceback.print_exc()
            EC.log("[record] "+traceback.format_exc())

    elif "edited_channel_post" in data:
        pass

    else:
        EC = EthicsCommittee("unknown", "unknown")
        EC.log("[record] "+json.dumps(data))
