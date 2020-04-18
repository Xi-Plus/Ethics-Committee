import re

import telegram

from Kamisu66 import EthicsCommitteeExtension


class CommandChatMute(EthicsCommitteeExtension):  # pylint: disable=W0223
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

        if re.search(settings['mute'], text):
            if EC.check_permission(user_id, self.PERMISSION_CHANGELOGO, chat_id):
                EC.update.effective_chat.set_permissions(
                    telegram.ChatPermissions(
                        can_send_messages=False
                    )
                )
                message.reply_text(
                    text='已全群禁言',
                    quote=True)
            else:
                message.reply_text(
                    text='你沒有權限進行全群禁言的動作',
                    quote=True)
            return

        if re.search(settings['unmute'], text):
            if EC.check_permission(user_id, self.PERMISSION_CHANGELOGO, chat_id):
                EC.update.effective_chat.set_permissions(
                    telegram.ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_polls=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_change_info=True,
                    )
                )
                message.reply_text(
                    text='已全群解除禁言',
                    quote=True)
            else:
                message.reply_text(
                    text='你沒有權限進行全群禁言的動作',
                    quote=True)
            return


def __mainclass__():
    return CommandChatMute
