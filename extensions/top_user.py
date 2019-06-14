from Kamisu66 import EthicsCommitteeExtension


class TopUser(EthicsCommitteeExtension):  # pylint: disable=W0223
    async def main(self, event):
        message = event.message

        if not message.is_group:
            return

        if message.message == '/topuser':
            chat_id = event.chat_id
            self.EC.cur.execute("""SELECT `count`, `full_name` FROM( SELECT COUNT(*) AS `count`, `user_id` FROM `message` WHERE `chat_id` = %s GROUP BY `user_id` ORDER BY `count` DESC LIMIT 10 ) t LEFT JOIN `user_name` ON t.user_id = user_name.user_id""",
                                (chat_id))
            row = self.EC.cur.fetchall()
            response = ''
            for user in row:
                response += user[1] + ' : ' + str(user[0]) + '\n'
            await message.reply(response)


def __mainclass__():
    return TopUser
