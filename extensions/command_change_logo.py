import re
import tempfile

import telegram

from Kamisu66 import EthicsCommitteeExtension


class SendPhotoChangeLogo(EthicsCommitteeExtension):
    MODULE_NAME = 'command_change_logo'
    PERMISSION_CHANGELOGO = MODULE_NAME + '_change_logo'
    PERMISSION_GRANT = MODULE_NAME + '_grant'

    def __init__(self, settings):
        self.settings = settings

    def main(self, EC):
        chat_id = EC.update.effective_chat.id
        if chat_id not in self.settings:
            return

        if not EC.update.message or not EC.update.message.text:
            return

        settings = self.settings[chat_id]

        message = EC.update.message
        user_id = message.from_user.id
        text = message.text
        if message.reply_to_message:
            is_reply = True
            reply_to_user_id = message.reply_to_message.from_user.id
            reply_to_full_name = message.reply_to_message.from_user.full_name
        else:
            is_reply = False

        if re.search(settings['permissions']['grant'], text):
            if EC.check_permission(user_id, self.PERMISSION_GRANT, chat_id):
                if is_reply:
                    ok = EC.add_permission(
                        reply_to_user_id, self.PERMISSION_CHANGELOGO, chat_id)
                    if ok:
                        message.reply_text(
                            text='已授予 {} 更換頭貼的權限'.format(reply_to_full_name),
                            quote=True)
                    else:
                        message.reply_text(
                            text='{} 已有更換頭貼的權限'.format(reply_to_full_name),
                            quote=True)
                else:
                    message.reply_text(
                        text='你需要回應一則訊息以授予權限',
                        quote=True)
            else:
                message.reply_text(
                    text='你沒有權限進行修改其他人權限的動作',
                    quote=True)
            return

        if re.search(settings['permissions']['revoke'], text):
            if EC.check_permission(user_id, self.PERMISSION_GRANT, chat_id):
                if is_reply:
                    ok = EC.remove_permission(
                        reply_to_user_id, self.PERMISSION_CHANGELOGO, chat_id)
                    if ok:
                        message.reply_text(
                            text='已解除 {} 更換頭貼的權限'.format(reply_to_full_name),
                            quote=True)
                    else:
                        message.reply_text(
                            text='{} 沒有更換頭貼的權限'.format(reply_to_full_name),
                            quote=True)
                else:
                    message.reply_text(
                        text='你需要回應一則訊息以解除權限',
                        quote=True)
            else:
                message.reply_text(
                    text='你沒有權限進行修改其他人權限的動作',
                    quote=True)
            return

        for logocmd in settings['logo']:
            if re.search(logocmd, text):
                if EC.check_permission(user_id, self.PERMISSION_CHANGELOGO, chat_id):
                    logopath = settings['logo'][logocmd]

                    EC.update.effective_chat.send_action(
                        telegram.ChatAction.UPLOAD_PHOTO)

                    EC.bot.set_chat_photo(
                        chat_id=EC.update.effective_chat.id, photo=open(logopath, 'rb'))
                else:
                    message.reply_text(
                        text='你沒有權限進行更換頭貼的動作',
                        quote=True)
                return


def __mainclass__():
    return SendPhotoChangeLogo