# -*- coding: cp950 -*-

# 消息接收器
MSGReceiver = {
	'tpGather': { 'text': "綜合" },
	'InputBoxTips' : { 'text' : "輸入頁面名稱" },
	}

# 消息分頁操作菜單
pgMenu = {
	'miLock': { 'text': "鎖定分頁" },
	'miUnlock': { 'text': "解鎖分頁" },
	'miDock' : { 'text' : "停靠分頁" },
	'miRename': { 'text': "重新命名" },
	'miReset': { 'text': "重置分頁" },
	'miBackColor': { 'text': "頁面底色" },
	'miSetChannel': { 'text': "頻道設置" },
	'miDelete': { 'text': "移除分頁" },
	'miCreate': { 'text': "創建分頁" },
	'miSetColor': { 'text': "頻道顏色" },
	}

# 消息發送者操作菜單
tMenu = {
	'miWhisper': { 'text': "私聊" },
	'miViewRole': { 'text': "查看玩家信息" },
	'miCopy': { 'text': "復製玩家名字" },
	'miInviteBuddy': { 'text': "加為好友" },
	'miBlacklist': { 'text': "加入黑名單" },
	'miMakeTeam': { 'text': "組隊" },
	'miInviteFamily': { 'text': "邀請加入家族" },
	'miInviteTong': { 'text': "邀請加入幫會" },
	}

# 角色廣播窗口
RoleBroadcaster = {
	'title': { 'text': "廣播" },
	'inputTitle': { 'color': (-2,236,203), 'text': "文字輸入" },
	'propTitle': { 'color': (-2,236,203), 'text': "道具選擇" },
	'rbTunnel': { 'text': "使用地音號角(不支持表情)" },
	'rbWelkin': { 'text': "使用天音號角" },
	'rtRemind': { 'color': (-2,236,203), 'text': "注：當物品欄中沒有相應物品時，將直接使用對應的貨幣支付。" },
	'btnSend': { 'text': "發 送" },
	'btnCancel': { 'text': "取 消" },
	'stRemain': { 'text': "剩餘字數：%s" },
	}

# 頻道設置
ChannelFilter = {
	'title' : { 'color' : 0xffffff, 'text' : "頻道設置",  'limning' : 2 },
	'tips' : { 'text' : "設置“%s”分頁" },
	'btnOk' : { 'text' : "確 定" },
	'btnCancel' : { 'text' : "取 消" },
	}

# 顏色吸取
ColorSetter = {
	'title' : { 'color' : 0xffffff, 'text' : "頻道顏色設置",  'limning' : 2 },
	'btnOk' : { 'text' : "確 定" },
	'btnCancel' : { 'text' : "取 消" },
	}

# 聊天記錄界面
ChatLogViewer = {
	'btnRefresh'	 : { 'color' : (255.0, 248.0, 158.0), 'text' : "刷 新" },	# "ChatWindow:ChatLogViewer", "btnRefresh"
	'btnCNSelect'	 : { 'color' : (255.0, 248.0, 158.0), 'text' : "頻道選擇" },	# "ChatWindow:ChatLogViewer", "btnCNSelect"
	'btnSave'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "保 存" },	# "ChatWindow:ChatLogViewer", "btnSave"
	'lbTitle'		 : { 'color' : 0xffffff, 'text' : "聊天記錄",  'limning' : 2 },	# "ChatWindow:ChatLogViewer", "lbTitle"
	'lbSelCNClew'	 : { 'text'	 : "聊天記錄" },	# "ChatWindow:ChatLogViewer", "lbSelCNClew"
}

# 世界發言確認框
YellVerifyBox = {
	'cbNotify'		 : { 'color' : (1.0, 255.0, 216.0), 'text' : "本次在線不再提示" },	# "ChatWindow:YellVerifyBox", "cbNotify"
}

# 玩伴聊天記錄窗口
PLMLogViewer = {
	# lbBtns
	'btnHide'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "關 閉" },	# "ChatWindow:PLMLogViewer", "btnHide"
	'btnSave'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "保 存" },	# "ChatWindow:PLMLogViewer", "btnSave"
	# lbTitle
	'lbTitle'		 : { 'color' : (71.0, 35.0, 0.0), 'text' : "【%s】-- 聊天記錄" },	# "ChatWindow:PLMLogViewer", "lbTitle"
	'stClew'		 : { 'text' : "為了您的隱私安全，聊天記錄不會自動存檔，如需要請使用保存功能另外保存。" },	# "ChatWindow:PLMLogViewer", "stClew"
}

# 玩伴聊天窗口
PLMChatWnd = {
	# lbBtns
	'btnSend'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "發 送" },	# "ChatWindow:PLMChatWnd", "btnSend"
	'btnLog'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "聊天記錄" },	# "ChatWindow:PLMChatWnd", "btnLog"
	'btnHide'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "關 閉" },	# "ChatWindow:PLMChatWnd", "btnHide"
	# lbTitle
	'lbTitle'		 : { 'color' : (71.0, 35.0, 0.0), 'text' : "【%s】-- 好友聊天" },	# "ChatWindow:PLMChatWnd", "lbTitle"
	# stext
	'stOffline'		 : { 'color' : (164.0, 164.0, 164.0), 'text' : "離線" },	# "ChatWindow:PLMChatWnd", "stOffline"
	# send shortcut
	'sendShortcut' : { 'text': "快捷鍵：\n－－ Ctrl + Enter" },	# "ChatWindow:PLMChatWnd", "sendShortcut"
}
