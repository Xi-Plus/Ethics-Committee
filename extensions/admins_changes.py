from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class AdminChanges(EthicsCommitteeExtension):  # pylint: disable=W0223
    def web(self):
        EC = EthicsCommittee(0, 0)
        EC.cur.execute(
            """SELECT
                `admins_changes`.`chat_id`,
                `group_name`.`title`,
                `admins_changes`.`user_id`,
                `user_name`.`full_name`,
                `user_name`.`username`,
                `admins_changes`.`action`,
                `admins_changes`.`can_add_web_page_previews`,
                `admins_changes`.`can_be_edited`,
                `admins_changes`.`can_change_info`,
                `admins_changes`.`can_delete_messages`,
                `admins_changes`.`can_edit_messages`,
                `admins_changes`.`can_invite_users`,
                `admins_changes`.`can_pin_messages`,
                `admins_changes`.`can_post_messages`,
                `admins_changes`.`can_promote_members`,
                `admins_changes`.`can_restrict_members`,
                `admins_changes`.`can_send_media_messages`,
                `admins_changes`.`can_send_messages`,
                `admins_changes`.`can_send_other_messages`,
                `admins_changes`.`time`
            FROM `admins_changes`
            LEFT JOIN `group_name`
            ON `admins_changes`.`chat_id` = `group_name`.`chat_id`
            LEFT JOIN `user_name`
            ON `admins_changes`.`user_id` = `user_name`.`user_id`
            ORDER BY `time` DESC""")
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
                <th>chat_title</th>
                <th>user_id</th>
                <th>user_full_name</th>
                <th>username</th>
                <th>action</th>
                <th>can_add_web_page_previews</th>
                <th>can_be_edited</th>
                <th>can_change_info</th>
                <th>can_delete_messages</th>
                <th>can_edit_messages</th>
                <th>can_invite_users</th>
                <th>can_pin_messages</th>
                <th>can_post_messages</th>
                <th>can_promote_members</th>
                <th>can_restrict_members</th>
                <th>can_send_media_messages</th>
                <th>can_send_messages</th>
                <th>can_send_other_messages</th>
                <th>time</th>
            </tr>
            </thead>
            <tbody>
            """
        for row in rows:
            text += '<tr>'
            for i in range(20):
                text += '<td>{}</td>'.format(row[i])
            text += '</tr>'
        text += """
            </tbody>
            </table>
            </body>
            </html>
            """
        return text


def __mainclass__():
    return AdminChanges
