import json
import traceback

from Kamisu66 import EthicsCommitteeExtension


class Record(EthicsCommitteeExtension):
    def __init__(self, full_log_chat_id):
        self.full_log_chat_id = full_log_chat_id

    def main(self, EC):
        update = EC.update

        chat = update.effective_chat
        chat_id = chat.id
        chat_title = chat.title
        chat_username = chat.username

        user = update.effective_user
        if user:
            user_id = user.id
            username = user.username
            full_name = user.full_name
        else:
            user_id = 0
            username = ''
            full_name = ''

        message = update.effective_message
        date = int(message.date.timestamp())
        message_id = message.message_id
        reply_to_message_id = 0
        reply_to_user_id = 0
        if message.reply_to_message:
            reply_to_message_id = message.reply_to_message.message_id
            reply_to_user_id = message.reply_to_message.from_user.id

        EC.cur.execute("""INSERT INTO `user_name` (`user_id`, `full_name`, `username`)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE `full_name` = %s, `username` = %s""",
                       (user_id, full_name, username, full_name, username))
        if chat_id < 0 and user:
            EC.cur.execute("""INSERT INTO `group_name` (`chat_id`, `title`, `username`) VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE `title` = %s, `username` = %s""",
                           (chat_id, chat_title, chat_username, chat_title, chat_username))
        EC.db.commit()

        if chat_id in self.full_log_chat_id:
            EC.log("[record] " + json.dumps(update.to_dict()))

        if update.message or update.edited_message:
            type_prefix = ''
            if update.edited_message:
                type_prefix = 'edited_'

            try:
                mtype = []
                if message.text:
                    mtype.append("text")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "text",
                                  message.text, date, reply_to_message_id,
                                  reply_to_user_id)
                if message.sticker:
                    mtype.append("sticker")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "sticker",
                                  message.sticker.file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.document:
                    mtype.append("document")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "document",
                                  message.document.file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.audio:
                    mtype.append("audio")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "audio",
                                  message.audio.file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.voice:
                    mtype.append("voice")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "voice",
                                  message.voice.file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.photo:
                    mtype.append("photo")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "photo",
                                  message.photo[-1].file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.video:
                    mtype.append("video")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "video",
                                  message.video.file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.caption:
                    mtype.append("caption")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "caption",
                                  message.caption, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.video_note:
                    mtype.append("video_note")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "video_note",
                                  message.video_note.file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.contact:
                    mtype.append("contact")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "contact",
                                  json.dumps(message.contact.to_dict()), date,
                                  reply_to_message_id, reply_to_user_id)
                if message.venue:
                    mtype.append("venue")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "venue",
                                  json.dumps(message.venue.to_dict()), date,
                                  reply_to_message_id, reply_to_user_id)
                if message.location:
                    mtype.append("location")
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "location",
                                  json.dumps(message.location.to_dict()), date,
                                  reply_to_message_id, reply_to_user_id)
                if message.new_chat_members:
                    mtype.append("new_chat_member")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "new_chat_member",
                                  message.new_chat_members[0].id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.left_chat_member:
                    mtype.append("left_chat_member")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "left_chat_member",
                                  message.left_chat_member.id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.pinned_message:
                    mtype.append("pinned_message")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "pinned_message",
                                  message.pinned_message.message_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.new_chat_title:
                    mtype.append("new_chat_title")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "new_chat_title",
                                  message.new_chat_title,
                                  date, reply_to_message_id, reply_to_user_id)
                if message.new_chat_photo:
                    mtype.append("new_chat_photo")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "new_chat_photo",
                                  message.new_chat_photo[-1].file_id, date,
                                  reply_to_message_id, reply_to_user_id)
                if message.delete_chat_photo:
                    mtype.append("delete_chat_photo")
                    EC.addmessage(user_id, message_id, full_name,
                                  type_prefix + "delete_chat_photo", "", date,
                                  reply_to_message_id, reply_to_user_id)
                if len(mtype) == 0:
                    EC.addmessage(user_id, message_id, full_name, type_prefix + "unknown",
                                  json.dumps(message.to_dict()), date,
                                  reply_to_message_id, reply_to_user_id)
            except Exception:
                traceback.print_exc()
                EC.log("[record] " + traceback.format_exc())

        elif update.channel_post:
            try:
                if message.text:
                    EC.addmessage(user_id, message_id, full_name, "text",
                                  message.text, date, reply_to_message_id,
                                  reply_to_user_id)
                else:
                    EC.log("[record] " + json.dumps(update.to_dict()))
            except Exception:
                traceback.print_exc()
                EC.log("[record] " + traceback.format_exc())

        elif update.edited_channel_post:
            pass

        else:
            EC.log("[record] " + json.dumps(update.to_dict()))


def __mainclass__():
    return Record
