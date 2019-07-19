# spam_ban
根據發言文字進行自動封鎖，以及多個群組聯合封鎖

## 指令集
以下指令的底線可省略

### /global_ban
進行全域封鎖，需要權限`spam_ban_global_ban`
```
usage: /global_ban [-h] [-d 時長] [-r 原因] [--dry-run] [user]

positional arguments:
  user        欲封鎖用戶ID，不指定時需回覆訊息

optional arguments:
  -h, --help  show this help message and exit
  -d 時長       接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m，永久為inf。預設：1w
  -r 原因       預設：Spam
  --no-del    不刪除訊息
  --dry-run   在日誌記錄但不執行封鎖
```
範例：
- `/global_ban`(Reply) - 封鎖被回應的用戶
- `/global_ban -r 廣告`(Reply) - 封鎖被回應的用戶，理由為廣告
- `/global_ban -r "spam or scam"`(Reply) - 封鎖被回應的用戶，理由為spam or scam
- `/global_ban 12345 -r 廣告` - 封鎖ID為12345的用戶，理由為廣告
- `/global_ban -d 30d`(Reply) - 封鎖被回應的用戶，期限為30天
- `/global_ban -d 2w`(Reply) - 封鎖被回應的用戶，期限為2週

### /global_unban
進行全域解除封鎖，需要權限`spam_ban_global_ban`
```
usage: /global_unban [-h] [-r 原因] [--dry-run] [user]

positional arguments:
  user        欲解除封鎖用戶ID，不指定時需回覆訊息

optional arguments:
  -h, --help  show this help message and exit
  -r 原因       預設：無原因
  --dry-run   在日誌記錄但不執行解除封鎖
```
範例：
- `/global_unban`(Reply) - 解除封鎖被回應的用戶
- `/global_unban -r 誤判`(Reply) - 解除封鎖被回應的用戶，理由為誤判
- `/global_unban -r "block review"`(Reply) - 解除封鎖被回應的用戶，理由為block review
- `/global_unban 12345 -r 誤判` - 解除封鎖ID為12345的用戶，理由為誤判

### /global_restrict
進行全域禁言，需要權限`spam_ban_global_ban`
```
usage: /global_restrict [-h] [-d 時長] [-r 原因] [-s 群組集合] [--dry-run] [user]

positional arguments:
  user        欲禁言用戶ID，不指定時需回覆訊息

optional arguments:
  -h, --help  show this help message and exit
  -d 時長       接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m，永久為inf。預設：1w
  -r 原因       預設：未提供理由
  -s 群組集合     執行禁言的群組集合，預設：globalban
  --dry-run   在日誌記錄但不執行禁言
```
範例：
- `/global_restrict`(Reply) - 禁言被回應的用戶
- `/global_restrict -r 違反導則`(Reply) - 禁言被回應的用戶，理由為違反導則
- `/global_restrict -r "Gaming the system"`(Reply) - 禁言被回應的用戶，理由為Gaming the system
- `/global_restrict 12345 -r 違反導則` - 禁言ID為12345的用戶，理由為違反導則
- `/global_restrict -d 30d`(Reply) - 禁言被回應的用戶，期限為30天
- `/global_restrict -d 2w`(Reply) - 禁言被回應的用戶，期限為2週
- `/global_restrict -s official`(Reply) - 禁言被回應的用戶，執行範圍為群組集合 official

### /global_unrestrict
進行全域解除禁言，需要權限`spam_ban_global_ban`
```
usage: /global_unrestrict [-h] [-r 原因] [-s 群組集合] [--dry-run] [user]

positional arguments:
  user        欲解除禁言用戶ID，不指定時需回覆訊息

optional arguments:
  -h, --help  show this help message and exit
  -r 原因       預設：無原因
  -s 群組集合     執行禁言的群組集合，預設：globalban
  --dry-run   在日誌記錄但不執行解除禁言
```
範例：
- `/global_unrestrict`(Reply) - 解除禁言被回應的用戶
- `/global_unrestrict -r 申訴`(Reply) - 解除禁言被回應的用戶，理由為申訴
- `/global_unrestrict -r "block review"`(Reply) - 解除禁言被回應的用戶，理由為block review
- `/global_unrestrict 12345 -r 申訴` - 解除禁言ID為12345的用戶，理由為申訴
- `/global_restrict -s official`(Reply) - 解除禁言被回應的用戶，執行範圍為群組集合 official

### /grant_global_ban
授予全域封鎖權限，需要權限`spam_ban_grant`

### /revoke_global_ban
解除全域封鎖權限，需要權限`spam_ban_grant`

### /enable_ban_text
在本群啟用文字自動封鎖，需要權限`spam_ban_setting`

### /enable_ban_username
在本群啟用用戶名自動封鎖，需要權限`spam_ban_setting`

### /enable_warn_text
在本群啟用文字警示，需要權限`spam_ban_setting`

### /enable_warn_username
在本群啟用用戶名警示，需要權限`spam_ban_setting`

### /enable_ban_youtube_link
在本群啟用YouTube連結自動封鎖，需要權限`spam_ban_setting`

### /enable_warn_forward
在本群啟用轉傳新群組訊息警示，需要權限`spam_ban_setting`

### /enable_global_ban
將本群納入全域封鎖範圍，需要權限`spam_ban_setting`

### /disable_ban_text
在本群停用文字自動封鎖，需要權限`spam_ban_setting`

### /disable_ban_username
在本群停用用戶名自動封鎖，需要權限`spam_ban_setting`

### /disable_warn_text
在本群停用文字警示，需要權限`spam_ban_setting`

### /disable_warn_username
在本群停用用戶名警示，需要權限`spam_ban_setting`

### /disable_ban_youtube_link
在本群停用YouTube連結自動封鎖，需要權限`spam_ban_setting`

### /disable_warn_forward
在本群停用轉傳新群組訊息警示，需要權限`spam_ban_setting`

### /disable_global_ban
將本群移出全域封鎖範圍，需要權限`spam_ban_setting`

### /add_spam_rule_ban_text
新增文字封鎖規則，需要權限`spam_ban_rule`
> 用戶名封鎖、文字警告、用戶名警告自動繼承此規則

### /add_spam_rule_ban_username
新增用戶名封鎖規則，需要權限`spam_ban_rule`
> 用戶名警告自動繼承此規則

### /add_spam_rule_warn_text
新增文字警告規則，需要權限`spam_ban_rule`
> 用戶名警告自動繼承此規則

### /add_spam_rule_warn_username
新增用戶名警告規則，需要權限`spam_ban_rule`

### /remove_spam_rule_ban_text
移除文字封鎖規則，需要權限`spam_ban_rule`

### /remove_spam_rule_ban_username
移除用戶名封鎖規則，需要權限`spam_ban_rule`

### /remove_spam_rule_warn_text
移除文字警告規則，需要權限`spam_ban_rule`

### /remove_spam_rule_warn_username
移除用戶名警告規則，需要權限`spam_ban_rule`

### /test_spam_rule
測試文字是否符合規則

## 權限表
- `spam_ban_global_ban` - 可封鎖和解除封鎖用戶，可由持有`spam_ban_grant`權限的用戶授予
- `spam_ban_grant` - 可授予封鎖權限，目前無人可授予
- `spam_ban_setting` - 可設定機器人監視的群組，目前無人可授予
- `spam_ban_rule` - 可設定廣告規則，目前無人可授予
