from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class GroupName(EthicsCommitteeExtension):
    def web(self):
        EC = EthicsCommittee(0, 0)
        EC.cur.execute(
            """SELECT `chat_id`, `title`, `username` FROM `group_name`
            WHERE `chat_id` NOT IN (
                SELECT `chat_id` FROM `group_setting` WHERE `key` = 'group_set' AND `value` = 'hidden'
            )
            ORDER BY `title` DESC""")
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
            </tr>
            </thead>
            <tbody>
            """
        for row in rows:
            text += """<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>""".format(
                row[0], row[1], row[2])
        text += """
            </tbody>
            </table>
            </body>
            </html>
            """
        return text


def __mainclass__():
    return GroupName
