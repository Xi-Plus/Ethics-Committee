# spam_ban
根據發言文字進行自動封鎖，以及多個群組聯合封鎖

## 指令集
以下指令的底線可省略

### /global_ban
進行全域封鎖，需要權限`spam_ban_global_ban`
```
usage: /globalban user [-d 時長] [-r 原因] [-h]

positional arguments:
  user        欲封鎖用戶ID，不指定時需回覆訊息

optional arguments:
  -h, --help  show this help message and exit
  -d 時長       接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m。預設：1w
  -r 原因       預設：Spam
```
範例：
- `/global_ban`(Reply) - 封鎖被回應的用戶
- `/global_ban -r 廣告`(Reply) - 封鎖被回應的用戶，理由為廣告
- `/global_ban -r "spam or scam"`(Reply) - 封鎖被回應的用戶，理由為spam or scam
- `/global_ban 12345 -r 廣告` - 封鎖ID為12345的用戶，理由為廣告
- `/global_ban -d 30d`(Reply) - 封鎖被回應的用戶，期限為30天
- `/global_ban -d 2w`(Reply) - 封鎖被回應的用戶，期限為2週

### /global_unban
進行全域封鎖，需要權限`spam_ban_global_ban`
```
usage: /global_unban user [-r 原因] [-h]

positional arguments:
  user        欲解除封鎖用戶ID，不指定時需回覆訊息

optional arguments:
  -h, --help  show this help message and exit
  -r 原因       預設：無原因
```
範例：
- `/global_unban`(Reply) - 解除封鎖被回應的用戶
- `/global_unban -r 誤判`(Reply) - 封鎖被回應的用戶，理由為誤判
- `/global_unban -r "block review"`(Reply) - 封鎖被回應的用戶，理由為block review
- `/global_unban 12345 -r 誤判` - 封鎖ID為12345的用戶，理由為誤判

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

### /enable_global_ban
將本群納入全域封鎖範圍，需要權限`spam_ban_setting`

### /disable_ban_text
在本群停用文字自動封鎖，需要權限`spam_ban_setting`

### /disable_ban_username
在本群停用文字自動封鎖，需要權限`spam_ban_setting`

### /disable_warn_text
在本群停用文字警示，需要權限`spam_ban_setting`

### /disable_warn_username
在本群停用用戶名警示，需要權限`spam_ban_setting`

### /disable_global_ban
將本群移出全域封鎖範圍，需要權限`spam_ban_setting`

## 權限表
- `spam_ban_global_ban` - 可封鎖和解除封鎖用戶，可由持有`spam_ban_grant`權限的用戶授予
- `spam_ban_grant` - 可授予封鎖權限，目前無人可授予
- `spam_ban_setting` - 可設定機器人，目前無人可授予
