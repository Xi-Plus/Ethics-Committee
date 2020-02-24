from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class UserNameChanges(EthicsCommitteeExtension):  # pylint: disable=W0223
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
