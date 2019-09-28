from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class GroupName(EthicsCommitteeExtension):  # pylint: disable=W0223
    def __init__(self, extra_group):
        self.extra_group = extra_group

    def web(self):
        EC = EthicsCommittee(0, 0)

        group_set = {}
        EC.cur.execute(
            """SELECT `chat_id`, `value` FROM `group_setting`
            WHERE `key` = 'group_set' AND `value` != 'hidden'
            ORDER BY `value` ASC""")
        rows = EC.cur.fetchall()
        for row in rows:
            chat_id = int(row[0])
            if chat_id not in group_set:
                group_set[chat_id] = []
            group_set[chat_id].append(row[1])
        for sql, name in self.extra_group:
            EC.cur.execute(sql)
            rows = EC.cur.fetchall()
            for row in rows:
                chat_id = int(row[0])
                if chat_id not in group_set:
                    group_set[chat_id] = []
                group_set[chat_id].append(name)

        EC.cur.execute(
            """SELECT `chat_id`, `title`, `username`, (SELECT `time` FROM `message` WHERE `group_name`.`chat_id`=`message`.`chat_id` ORDER BY `date` DESC LIMIT 1) AS `last_message_time`
            FROM `group_name`
            WHERE `chat_id` NOT IN (
                SELECT `chat_id` FROM `group_setting` WHERE `key` = 'group_set' AND `value` = 'hidden'
            )
            ORDER BY `title` ASC""")
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
                <th>chat_id</th>
                <th>title</th>
                <th>username</th>
                <th>last_message_time</th>
                <th>set</th>
            </tr>
            </thead>
            <tbody>
            """
        for row in rows:
            chat_id = int(row[0])

            gset = ''
            if chat_id in group_set:
                gset = ', '.join(group_set[chat_id])

            text += """<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>""".format(
                chat_id,
                row[1],
                row[2],
                row[3],
                gset,
            )
        text += """
            </tbody>
            </table>
            </body>
            </html>
            """
        return text


def __mainclass__():
    return GroupName
