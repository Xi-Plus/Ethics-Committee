from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class Admin_matrix(EthicsCommitteeExtension):
    def __init__(self, chat_id):
        self.chat_id_list = ', '.join([str(v) for v in chat_id])

    def web(self):
        EC = EthicsCommittee(0, 0)
        EC.cur.execute(
            """SELECT `chat_id`, `admins`.`user_id`, `full_name`, `creator` FROM `admins`
            LEFT JOIN `user_name` ON `admins`.`user_id` = `user_name`.`user_id`
            WHERE `chat_id` IN
            ({})""".format(self.chat_id_list))
        rows = EC.cur.fetchall()
        admin_in_chats = set()
        admins = set()
        creators = set()
        for row in rows:
            admin_in_chats.add((row[0], row[1]))
            admins.add((row[1], row[2]))
            if row[3]:
                creators.add((row[0], row[1]))
        EC.cur.execute(
            """SELECT `chat_id`, `title` FROM `group_name`
            WHERE `chat_id` IN ({})""".format(self.chat_id_list))
        groups = EC.cur.fetchall()
        text = """<!DOCTYPE html>
            <html>
            <head>
                <style>
                table {
                    border-collapse: collapse;
                    table-layout: fixed;
                    width: 100%;
                }
                thead tr th {
                    position:sticky;
                    top:0;
                }
                th {
                    background-color: #bbeeaa;
                    word-break: break-all;
                }
                th, td {
                    vertical-align: top;
                    border: 1px solid black;
                    padding: 3px;
                }
                th:first-child {
                    z-index:2;
                    background-color: #bbeeaa;
                }
                td:first-child, th:first-child {
                    position:sticky;
                    left:0;
                    z-index:1;
                    background-color: #ffffbb;
                }
                td {
                    word-break: break-all;
                }
                .groupname {
                    width: 80px;
                }
                .username {
                    width: 100px;
                }
                .creator {
                    background-color: #ffaaff;
                }
            </style>
            </head>
            <body>
            <table>
            <thead>
            <tr>
            <th class="username"></th>
            """
        for group in groups:
            text += """<th class="groupname"><span title="{0}">{1}</span></th>""".format(
                group[0], group[1])
        text += """
            </tr>
            </thead>
            <tbody>
            """
        for admin in admins:
            text += """<tr><td class="username"><span title="{0}">{1}</span></td>""".format(
                admin[0], admin[1])
            for group in groups:
                if (group[0], admin[0]) in creators:
                    text += """<td class="creator">"""
                else:
                    text += "<td>"
                if (group[0], admin[0]) in admin_in_chats:
                    text += '&#10003;'
                text += "</td>"
            text += "</tr>"
        text += """
            </tbody>
            </table>
            </body>
            </html>
            """
        return text


def __mainclass__():
    return Admin_matrix
