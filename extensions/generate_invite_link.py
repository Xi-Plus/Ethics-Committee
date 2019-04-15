import re

from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class GenerateInviteLink(EthicsCommitteeExtension):
    MODULE_NAME = 'generate_invite_link'
    PERMISSION_CMD = MODULE_NAME + '_cmd'
    PERMISSION_GRANT = MODULE_NAME + '_grant'

    def __init__(self, settings, hidden_in_web):
        self.settings = settings
        self.hidden_in_web = hidden_in_web

    def main(self, EC):
        self.EC = EC

        if not EC.update.message or not EC.update.message.text:
            return

        self.chat_id = EC.update.effective_chat.id
        self.message = EC.update.message
        self.user_id = self.message.from_user.id
        text = self.message.text

        if self.chat_id in self.settings['source']:
            settings = self.settings['source'][self.chat_id]

            for gencmd in settings:
                target = settings[gencmd]
                if re.search(gencmd, text):
                    self._cmd_generate(target)
                    break

        if self.chat_id in self.settings['target']:
            settings = self.settings['target'][self.chat_id]

            if self.message.reply_to_message:
                self.is_reply = True
                self.reply_to_user_id = self.message.reply_to_message.from_user.id
                self.reply_to_full_name = self.message.reply_to_message.from_user.full_name
            else:
                self.is_reply = False

            if re.search(settings['permissions']['grant'], text):
                self._cmd_grant()

            if re.search(settings['permissions']['revoke'], text):
                self._cmd_revoke()

    def _cmd_grant(self):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GRANT, self.chat_id):
            self.message.reply_text(text='你沒有權限進行授予權限的動作', quote=True)
            return

        if not self.is_reply:
            self.message.reply_text(text='你需要回應一則訊息以授予權限', quote=True)
            return

        ok = self.EC.add_permission(
            self.reply_to_user_id, self.PERMISSION_CMD, self.chat_id)
        if ok:
            self.message.reply_text(
                text='已授予 {} 取得本群邀請連結的權限'.format(self.reply_to_full_name),
                quote=True)
        else:
            self.message.reply_text(
                text='{} 已有取得本群邀請連結的權限'.format(self.reply_to_full_name),
                quote=True)

    def _cmd_revoke(self):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GRANT, self.chat_id):
            self.message.reply_text(text='你沒有權限進行解除權限的動作', quote=True)
            return

        if not self.is_reply:
            self.message.reply_text(text='你需要回應一則訊息以解除權限', quote=True)
            return

        ok = self.EC.remove_permission(
            self.reply_to_user_id, self.PERMISSION_CMD, self.chat_id)
        if ok:
            self.message.reply_text(
                text='已解除 {} 取得本群邀請連結的權限'.format(self.reply_to_full_name),
                quote=True)
        else:
            self.message.reply_text(
                text='{} 沒有取得本群邀請連結的權限'.format(self.reply_to_full_name),
                quote=True)

    def _cmd_generate(self, setting):
        if self.EC.check_permission(self.user_id, self.PERMISSION_CMD, setting['chat_id']):
            link = self.EC.bot.export_chat_invite_link(
                chat_id=setting['chat_id'])
            self.message.reply_text(
                text=setting['accept'].format(link),
                disable_web_page_preview=True,
                quote=True)
        else:
            self.message.reply_text(
                text=setting['deny'],
                quote=True)

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
            """
        html += """
            source
            <table>
            <tr>
            <th>chat</th>
            <th>command</th>
            </tr>
            """
        for chat_id in self.settings['source']:
            if chat_id in self.hidden_in_web:
                continue
            setting = self.settings['source'][chat_id]

            html += """<tr>"""
            html += """<td>{0}<br>{1}</td>""".format(
                EC.get_group_name(chat_id),
                chat_id,
            )
            html += """
                <td>
                <table>
                <tr>
                <th>command</th>
                <th>target</th>
                <th>accept</th>
                <th>deny</th>
                </tr>
                """
            for cmd in setting:
                html += """<tr>"""
                html += """<td>{0}</td><td>{1} {2}</td><td>{3}</td><td>{4}</td>""".format(
                    cmd,
                    EC.get_group_name(setting[cmd]['chat_id']),
                    setting[cmd]['chat_id'],
                    setting[cmd]['accept'],
                    setting[cmd]['deny'],
                )
                html += """</tr>"""
            html += """</table></td>"""
            html += """</tr>"""
        html += """</table>"""

        html += """
            target
            <table>
            <tr>
            <th>chat</th>
            <th>grant permission</th>
            <th>revoke permission</th>
            </tr>
            """
        for chat_id in self.settings['target']:
            if chat_id in self.hidden_in_web:
                continue
            setting = self.settings['target'][chat_id]

            html += """<tr>"""
            html += """<td>{0}<br>{1}</td><td>{2}</td><td>{3}</td>""".format(
                EC.get_group_name(chat_id),
                chat_id,
                setting['permissions']['grant'],
                setting['permissions']['revoke'],
            )
            html += """</tr>"""
        html += """</table>"""

        return html


def __mainclass__():
    return GenerateInviteLink
