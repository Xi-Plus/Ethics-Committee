from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class GroupName(EthicsCommitteeExtension):
    def __init__(self, hidden_in_web):
        self.hidden_in_web = hidden_in_web

    def web(self):
        EC = EthicsCommittee(0, 0)
        EC.cur.execute(
            """SELECT `chat_id`, `title`, `username` FROM `group_name`
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
            if row[0] in self.hidden_in_web:
                continue
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
