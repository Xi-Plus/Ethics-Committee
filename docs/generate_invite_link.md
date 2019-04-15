# spam_ban
使用指令取得其他群組的邀請連結

## 注意事項
- 授予權限應於需邀請連結的群組為之，而不是可使用指令的群組
- 授予權限後用戶即可於所有可使用指令的群組使用指令，無法單獨禁止某個群組無法取得邀請連結

## 權限表
- `generate_invite_link_cmd` - 可使用取得邀請連結的指令，可由持有`generate_invite_link_grant`權限的用戶授予
- `generate_invite_link_grant` - 可授予取得邀請連結權限，目前無人可授予
