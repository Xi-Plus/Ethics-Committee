import json
import traceback

from Kamisu66 import EthicsCommitteeExtension


class Record(EthicsCommitteeExtension):
    def __init__(self, full_log_chat_id):
        self.full_log_chat_id = full_log_chat_id

    def main(self, EC):
        data = EC.data
        if "message" in data or "edited_message" in data:
            if "message" in data:
                message = data["message"]
                date = message["date"]
                type_prefix = ''
            elif "edited_message" in data:
                message = data["edited_message"]
                date = message["edit_date"]
                type_prefix = 'edited_'
            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            full_name = message["from"]["first_name"]
            if "last_name" in message["from"]:
                full_name += " " + message["from"]["last_name"]
            username = ""
            if "username" in message["from"]:
                username = message["from"]["username"]
            chat_title = ""
            if "title" in message["chat"]:
                chat_title = message["chat"]["title"]
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

            if chat_id in self.full_log_chat_id:
                EC.log("[record] " + json.dumps(data))

            try:
                EC.cur.execute("""INSERT INTO `user_name` (`user_id`, `full_name`, `username`)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE `full_name` = %s, `username` = %s""",
                               (user_id, full_name, username, full_name, username))
                if chat_id < 0:
                    EC.cur.execute("""INSERT INTO `group_name` (`chat_id`, `title`) VALUES (%s, %s)
                                    ON DUPLICATE KEY UPDATE `title` = %s""",
                                   (chat_id, chat_title, chat_title))
                EC.db.commit()
                mtype = []
                if "text" in message:
                    mtype.append("text")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "text",
                                  message["text"], date, reply_to_message_id,
                                  reply_to_user_id)
                if "sticker" in message:
                    mtype.append("sticker")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "sticker",
                                  message["sticker"]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "document" in message:
                    mtype.append("document")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "document",
                                  message["document"]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "audio" in message:
                    mtype.append("audio")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "audio",
                                  message["audio"]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "voice" in message:
                    mtype.append("voice")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "voice",
                                  message["voice"]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "photo" in message:
                    mtype.append("photo")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "photo",
                                  message["photo"][-1]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "video" in message:
                    mtype.append("video")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "video",
                                  message["video"]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "caption" in message:
                    mtype.append("caption")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "caption",
                                  message["caption"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "video_note" in message:
                    mtype.append("video_note")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "video_note",
                                  message["video_note"]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "contact" in message:
                    mtype.append("contact")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "contact",
                                  json.dumps(message["contact"]), date,
                                  reply_to_message_id, reply_to_user_id)
                if "venue" in message:
                    mtype.append("venue")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "venue",
                                  json.dumps(message["venue"]), date,
                                  reply_to_message_id, reply_to_user_id)
                if "location" in message:
                    mtype.append("location")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "location",
                                  json.dumps(message["location"]), date,
                                  reply_to_message_id, reply_to_user_id)
                if "new_chat_member" in message:
                    mtype.append("new_chat_member")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "new_chat_member",
                                  message["new_chat_member"]["id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "left_chat_member" in message:
                    mtype.append("left_chat_member")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "left_chat_member",
                                  message["left_chat_member"]["id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "pinned_message" in message:
                    mtype.append("pinned_message")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "pinned_message",
                                  message["pinned_message"]["message_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "new_chat_title" in message:
                    mtype.append("new_chat_title")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix +
                                  "new_chat_title", message["new_chat_title"],
                                  date, reply_to_message_id, reply_to_user_id)
                if "new_chat_photo" in message:
                    mtype.append("new_chat_photo")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "new_chat_photo",
                                  message["new_chat_photo"][-1]["file_id"], date,
                                  reply_to_message_id, reply_to_user_id)
                if "delete_chat_photo" in message:
                    mtype.append("delete_chat_photo")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "delete_chat_photo", "", date,
                                  reply_to_message_id, reply_to_user_id)
                if len(mtype) == 0:
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "unknown",
                                  json.dumps(
                                      message), date, reply_to_message_id,
                                  reply_to_user_id)
            except Exception as e:
                traceback.print_exc()
                EC.log("[record] " + traceback.format_exc())

        elif "channel_post" in data:
            message = data["channel_post"]
            chat_id = message["chat"]["id"]
            user_id = ""
            full_name = ""
            message_id = message["message_id"]
            reply_to_message_id = ""
            reply_to_user_id = ""
            if "reply_to_message" in message:
                reply_to_message = message["reply_to_message"]
                reply_to_message_id = reply_to_message["message_id"]
            date = message["date"]

            if chat_id in self.full_log_chat_id:
                EC.log("[record] " + json.dumps(data))

            try:
                if "text" in message:
                    EC.addmessage(user_id, message_id, full_name, "text",
                                  message["text"], date, reply_to_message_id,
                                  reply_to_user_id)
                else:
                    EC.log("[record] " + json.dumps(data))
            except Exception as e:
                traceback.print_exc()
                EC.log("[record] " + traceback.format_exc())

        elif "edited_channel_post" in data:
            pass

        else:
            EC.log("[record] " + json.dumps(data))


def __mainclass__():
    return Record
