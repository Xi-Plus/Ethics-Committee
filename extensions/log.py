from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class Log(EthicsCommitteeExtension):  # pylint: disable=W0223
    def web(self):
        EC = EthicsCommittee(0, 0)
        EC.cur.execute(
            """SELECT `message`, `time` FROM `log` ORDER BY `log_id` DESC LIMIT 100""")
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
                pre {
                    margin-top: 0;
                    white-space: pre-wrap;
                }
            </style>
            </head>
            <body>
            <table>
            <tr>
            <td>time</td>
            <td>log</td>
            </tr>
            """
        for row in rows:
            text += "<tr><td>{0}</td><td><pre>{1}</pre></td></tr>".format(
                row[1], row[0])
        text += """
            </table>
            </body>
            </html>
            """
        return text


def __mainclass__():
    return Log
