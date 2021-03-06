import re

import telegram

from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class SendPhotoChangeLogo(EthicsCommitteeExtension):
    MODULE_NAME = 'command_change_logo'
    PERMISSION_CHANGELOGO = MODULE_NAME + '_change_logo'
    PERMISSION_GRANT = MODULE_NAME + '_grant'

    def __init__(self, settings, hidden_in_web):
        self.settings = settings
        self.hidden_in_web = hidden_in_web

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

                    try:
                        EC.bot.set_chat_photo(
                            chat_id=EC.update.effective_chat.id,
                            photo=open(logopath, 'rb'),
                        )
                    except telegram.error.BadRequest as e:
                        message.reply_text(
                            text='更換圖片失敗：{}'.format(e),
                            quote=True,
                        )
                else:
                    message.reply_text(
                        text='你沒有權限進行更換頭貼的動作',
                        quote=True)
                return

    def web(self):
        EC = EthicsCommittee(0, 0)

        html = """
            <style>
                table {
                    border-collapse: collapse;
                }
                th, td {
                    vertical-align: top;
                    border: 1px solid black;
                    padding: 3px;
                }
            </style>
        <table>
        <tr>
        <th>chat</th>
        <th>command</th>
        <th>permission grant</th>
        <th>permission change_logo</th>
        </tr>
        """
        for chat_id in self.settings:
            if chat_id in self.hidden_in_web:
                continue
            setting = self.settings[chat_id]

            html += """<tr>"""
            html += """<td>{0}<br>{1}</td>""".format(
                EC.get_group_name(chat_id),
                chat_id,
            )
            html += """<td>"""
            html += """grant permission<br><ul><li>{0}</li></ul>""".format(
                setting['permissions']['grant'],
            )
            html += """revoke permission<br><ul><li>{0}</li></ul>""".format(
                setting['permissions']['revoke'],
            )
            html += """change logo<br><ul>"""
            for cmd in setting['logo']:
                html += """<li>{0}</li>""".format(cmd)
            html += """<ul>"""

            html += """</td>"""

            html += """<td><ul>"""
            EC.cur.execute(
                """SELECT `permissions`.`user_id`, `full_name` FROM `permissions` LEFT JOIN `user_name` ON `permissions`.`user_id` = `user_name`.`user_id` WHERE `chat_id` = %s AND `user_right` = %s ORDER BY `permissions`.`user_id` ASC""", (chat_id, self.PERMISSION_GRANT))
            rows = EC.cur.fetchall()
            for row in rows:
                html += """<li>{0}（{1}）</li>""".format(row[0], row[1])
            html += """<ul></td>"""

            html += """<td><ul>"""
            EC.cur.execute(
                """SELECT `permissions`.`user_id`, `full_name` FROM `permissions` LEFT JOIN `user_name` ON `permissions`.`user_id` = `user_name`.`user_id` WHERE `chat_id` = %s AND `user_right` = %s ORDER BY `permissions`.`user_id` ASC""", (chat_id, self.PERMISSION_CHANGELOGO))
            rows = EC.cur.fetchall()
            for row in rows:
                html += """<li>{0}（{1}）</li>""".format(row[0], row[1])
            html += """<ul></td>"""

            html += """</tr>"""
        html += """</table>"""

        return html


def __mainclass__():
    return SendPhotoChangeLogo
