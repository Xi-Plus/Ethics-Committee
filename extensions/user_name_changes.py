import telegram
from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class UserNameChanges(EthicsCommitteeExtension):  # pylint: disable=W0223
    def __init__(self, notice_chat_ids):
        self.chat_ids = notice_chat_ids

        EC = EthicsCommittee(0, 0)

        self.usernames = {}
        EC.cur.execute("""SELECT `user_id`, `full_name`, `username` FROM `user_name`""")
        rows = EC.cur.fetchall()
        for row in rows:
            self.usernames[row[0]] = [row[1], row[2]]
        print('[UpdateUsername] Get {} usernames'.format(len(self.usernames)))

        self.groupnames = {}
        EC.cur.execute("""SELECT `chat_id`, `title`, `username` FROM `group_name`""")
        rows = EC.cur.fetchall()
        for row in rows:
            self.groupnames[row[0]] = [row[1], row[2]]
        print('[UpdateUsername] Get {} groupnames'.format(len(self.groupnames)))

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

        if chat_id < 0 and user:
            changed = False
            if chat_id not in self.groupnames:
                for notice_id in self.chat_ids['chat_new']:
                    EC.bot.send_message(
                        chat_id=notice_id,
                        text='Chat {0} {1} {2} is a new chat'.format(chat_id, chat_title, chat_username),
                        parse_mode=telegram.ParseMode.HTML,
                    )
                changed = True
            else:
                if chat_title != self.groupnames[chat_id][0]:
                    for notice_id in self.chat_ids['chat_title']:
                        EC.bot.send_message(
                            chat_id=notice_id,
                            text='Chat {0} updated its title from {1} to {2}'.format(chat_id, self.groupnames[chat_id][0], chat_title),
                            parse_mode=telegram.ParseMode.HTML,
                        )
                    changed = True
                if chat_username != self.groupnames[chat_id][1]:
                    for notice_id in self.chat_ids['chat_username']:
                        EC.bot.send_message(
                            chat_id=notice_id,
                            text='Chat {0} updated its username from {1} to {2}'.format(chat_id, self.groupnames[chat_id][1], chat_username),
                            parse_mode=telegram.ParseMode.HTML,
                        )
                    changed = True

            if changed:
                EC.cur.execute(
                    """INSERT INTO `group_name` (`chat_id`, `title`, `username`) VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE `title` = %s, `username` = %s""",
                    (chat_id, chat_title, chat_username, chat_title, chat_username))
                EC.db.commit()
                self.groupnames[chat_id] = [chat_title, chat_username]

        if user:
            changed = False
            if user_id not in self.usernames:
                for notice_id in self.chat_ids['user_new']:
                    EC.bot.send_message(
                        chat_id=notice_id,
                        text='<a href="tg://user?id={0}">{0}</a> {1} {2} is a new user'.format(user_id, full_name, username),
                        parse_mode=telegram.ParseMode.HTML,
                    )
                changed = True
            else:
                if full_name != self.usernames[user_id][0]:
                    for notice_id in self.chat_ids['user_fullname']:
                        text = '<a href="tg://user?id={0}">{0}</a> updated his fullname from {1} to {2}'.format(user_id, self.usernames[user_id][0], full_name)
                        try:
                            EC.bot.send_message(
                                chat_id=notice_id,
                                text=text,
                                parse_mode=telegram.ParseMode.HTML,
                            )
                        except Exception as e:
                            EC.log(e)
                            EC.log(text)
                    changed = True
                if username != self.usernames[user_id][1]:
                    for notice_id in self.chat_ids['user_username']:
                        EC.bot.send_message(
                            chat_id=notice_id,
                            text='<a href="tg://user?id={0}">{0}</a> updated his username from {1} to {2}'.format(user_id, self.usernames[user_id][1], username),
                            parse_mode=telegram.ParseMode.HTML,
                        )
                    changed = True

            if changed:
                EC.cur.execute(
                    """INSERT INTO `user_name` (`user_id`, `full_name`, `username`) VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE `full_name` = %s, `username` = %s""",
                    (user_id, full_name, username, full_name, username))
                EC.db.commit()
                self.usernames[user_id] = [full_name, username]

    def web(self):
        EC = EthicsCommittee(0, 0)
        EC.cur.execute(
            """SELECT `user_id`, `old_name`, `new_name`, `time` FROM `user_name_changes`
            ORDER BY `time` DESC LIMIT 500""")
        rows = EC.cur.fetchall()
        text = """<!DOCTYPE html>
            <html>
            <head>
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
            </head>
            <body>
            <table>
            <thead>
            <tr>
                <th>user_id</th>
                <th>old_name</th>
                <th>new_name</th>
                <th>time</th>
            </tr>
            </thead>
            <tbody>
            """
        for row in rows:
            text += """<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>""".format(
                row[0], row[1], row[2], row[3])
        text += """
            </tbody>
            </table>
            </body>
            </html>
            """
        return text


def __mainclass__():
    return UserNameChanges
