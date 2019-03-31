# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Kamisu66 import EthicsCommittee

EC = EthicsCommittee(0, 0)


def r2i(right):
    if right is None:
        return -1
    if right is True:
        return 1
    return 0


EC.cur.execute("""SELECT `chat_id`, `title` FROM `group_name`""")
rows = EC.cur.fetchall()
for row in rows:
    chat_id = row[0]
    title = row[1]
    print(chat_id, title)

    admins = EC.bot.get_chat_administrators(chat_id)
    for a in admins:
        user_id = a.user.id

        EC.cur.execute(
            """INSERT INTO `admins`
			(`chat_id`, `user_id`,
				`can_add_web_page_previews`, `can_be_edited`, `can_change_info`,
				`can_delete_messages`, `can_edit_messages`, `can_invite_users`,
				`can_pin_messages`, `can_post_messages`, `can_promote_members`,
				`can_restrict_members`, `can_send_media_messages`, `can_send_messages`,
				`can_send_other_messages`) VALUES
			(%s, %s,
				%s, %s, %s,
				%s, %s, %s,
				%s, %s, %s,
				%s, %s, %s,
				%s) ON DUPLICATE KEY UPDATE 
				`can_add_web_page_previews` = %s, `can_be_edited` = %s, `can_change_info` = %s,
				`can_delete_messages` = %s, `can_edit_messages` = %s, `can_invite_users` = %s,
				`can_pin_messages` = %s, `can_post_messages` = %s, `can_promote_members` = %s,
				`can_restrict_members` = %s, `can_send_media_messages` = %s, `can_send_messages` = %s,
				`can_send_other_messages` = %s""",
            (chat_id, user_id,
             r2i(a.can_add_web_page_previews), r2i(a.can_be_edited),
             r2i(a.can_change_info), r2i(a.can_delete_messages),
             r2i(a.can_edit_messages), r2i(a.can_invite_users),
             r2i(a.can_pin_messages), r2i(a.can_post_messages),
             r2i(a.can_promote_members), r2i(a.can_restrict_members),
             r2i(a.can_send_media_messages), r2i(a.can_send_messages),
             r2i(a.can_send_other_messages),
             r2i(a.can_add_web_page_previews), r2i(a.can_be_edited),
             r2i(a.can_change_info), r2i(a.can_delete_messages),
             r2i(a.can_edit_messages), r2i(a.can_invite_users),
             r2i(a.can_pin_messages), r2i(a.can_post_messages),
             r2i(a.can_promote_members), r2i(a.can_restrict_members),
             r2i(a.can_send_media_messages), r2i(a.can_send_messages),
             r2i(a.can_send_other_messages)
             )
        )
        EC.db.commit()

        print('\t', a.user.full_name)
