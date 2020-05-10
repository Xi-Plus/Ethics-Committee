import re

import telegram
from Kamisu66 import EthicsCommitteeExtension


class CommonGroupsInfo(EthicsCommitteeExtension):  # pylint: disable=W0223
    def __init__(self, setting):
        self.setting = setting

    def _check_user(self, EC, chat_id, user_id):
        EC.log('[commongroups] in chat {} ({}) checking {}'.format(chat_id, self.setting[chat_id]['chats'], user_id))
        EC.cur.execute(
            """SELECT `message_count`.`chat_id`, `title`, SUM(`count`) AS `count`
            FROM `message_count`
            LEFT JOIN `group_name` ON `message_count`.`chat_id` = `group_name`.`chat_id`
            WHERE `user_id` = %s AND `message_count`.`chat_id` IN ({})
            GROUP BY `message_count`.`chat_id`
            ORDER BY `count` DESC""".format(
                ", ".join(map(str, self.setting[chat_id]['chats']))
            ),
            (user_id)
        )
        rows = EC.cur.fetchall()

        response = '<a href="tg://user?id={0}">{0}</a>'.format(user_id)
        if rows:
            response += '的共同群組有'
            for i, chat in enumerate(rows[:3]):
                if i > 0:
                    response += '、'
                response += ' {} ({}) '.format(chat[1], chat[2])
            if len(rows) > 3:
                response += '及其他{}個群組'.format(len(rows) - 3)
        else:
            response += '無共同群組'

        return response

    def main(self, EC):
        if not EC.update.message:
            return

        chat_id = EC.update.effective_chat.id

        if chat_id not in self.setting:
            return

        response = None

        if EC.update.message.new_chat_members:
            if self.setting[chat_id]['joincheck']:
                user_id = EC.update.effective_message.new_chat_members[0].id
                response = self._check_user(EC, chat_id, user_id)

        elif EC.update.message.text:
            text = EC.update.message.text
            if text.startswith('/commongroups'):
                check_user_id = None
                if EC.update.message.reply_to_message:
                    check_user_id = EC.update.message.reply_to_message.from_user.id
                else:
                    m = re.search(r'^/commongroups (\d+)$', text)
                    if m:
                        check_user_id = int(m.group(1))

                response = None
                if check_user_id is None:
                    response = '需回應一則訊息或是指定參數user id'
                else:
                    response = self._check_user(EC, chat_id, check_user_id)

        if response:
            EC.update.message.reply_text(
                text=response,
                quote=True,
                parse_mode=telegram.ParseMode.HTML,
            )


def __mainclass__():
    return CommonGroupsInfo
