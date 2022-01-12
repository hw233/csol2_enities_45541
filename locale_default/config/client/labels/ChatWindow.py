# -*- coding: UTF-8 -*-

main = {
	"history" : { "text" : "聊天记录" },
	"setting" : { "text" : "分页设置" },
	"broadcast" : { "text" : "发送广播" },
	"set_chns" : { "text" : "设置" },
	"scroll_up" : { "text" : "聊天记录上翻" },
	"scroll_down" : { "text" : "聊天记录下翻" },
	"scroll_end" : { "text" : "聊天记录翻至底部" },
	"extend" : { "text" : "显示聊天窗口" },
	"furl" : { "text" : "隐藏聊天窗口" },
	}

# 消息接收器
MSGReceiver = {
	'tpGather': { 'text': "综合" },
	'InputBoxTips' : { 'text' : "输入页面名称" },
	}

# 消息分页操作菜单
pgMenu = {
	'miLock': { 'text': "锁定分页" },
	'miUnlock': { 'text': "解锁分页" },
	'miDock' : { 'text' : "停靠分页" },
	'miRename': { 'text': "重新命名" },
	'miReset': { 'text': "重置分页" },
	'miBackColor': { 'text': "页面底色" },
	'miSetChannel': { 'text': "频道设置" },
	'miDelete': { 'text': "移除分页" },
	'miCreate': { 'text': "创建分页" },
	'miSetColor': { 'text': "频道颜色" },
	}

# 消息发送者操作菜单
tMenu = {
	'miWhisper': { 'text': "私聊" },
	'miViewRole': { 'text': "查看玩家信息" },
	'miCopy': { 'text': "复制玩家名字" },
	'miInviteBuddy': { 'text': "加为好友" },
	'miBlacklist': { 'text': "加入黑名单" },
	'miFriendChat': {'text': "好友聊天"},
	'miMakeTeam': { 'text': "组队" },
	'miInviteFamily': { 'text': "邀请加入家族" },
	'miInviteTong': { 'text': "邀请加入帮会" },
	}

# 角色广播窗口
RoleBroadcaster = {
	'title': { 'text': "广播" ,'charSpace':2, 'limning' : 2},
	'inputTitle': { 'color': (-2,236,203), 'text': "文字输入" },
	'propTitle': { 'color': (-2,236,203), 'text': "道具选择" },
	'rbTunnel': { 'text': "使用地音号角(不支持表情)" },
	'rbWelkin': { 'text': "使用天音号角" },
	'rtRemind': { 'color': (-2,236,203), 'text': "注：当物品栏中没有相应物品时，将直接使用对应的货币支付。" },
	'btnSend': { 'text': "发 送" },
	'btnCancel': { 'text': "取 消" },
	'stRemain': { 'text': "剩余字数：%s" },
	}

# 频道设置
ChannelFilter = {
	'title' : { 'text' : "频道设置", 'charSpace':2,  'limning' : 2 },
	'tips' : { 'text' : "设置“%s”分页" },
	'btnOk' : { 'text' : "确 定" },
	'btnCancel' : { 'text' : "取 消" },
	}

# 颜色吸取
ColorSetter = {
	'title' : { 'text' : "频道颜色设置", 'charSpace':2,  'limning' : 2 },
	'btnOk' : { 'text' : "确 定" },
	'btnCancel' : { 'text' : "取 消" },
	}

# 聊天记录界面
ChatLogViewer = {
	'btnRefresh'	 : { 'color' : (255.0, 248.0, 158.0), 'text' : "刷 新" },	# "ChatWindow:ChatLogViewer", "btnRefresh"
	'btnCNSelect'	 : { 'color' : (255.0, 248.0, 158.0), 'text' : "频道选择" },	# "ChatWindow:ChatLogViewer", "btnCNSelect"
	'btnSave'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "保 存" },	# "ChatWindow:ChatLogViewer", "btnSave"
	'lbTitle'		 : { 'text' : "聊天记录",  'limning' : 2 },	# "ChatWindow:ChatLogViewer", "lbTitle"
	'lbSelCNClew'	 : { 'text'	 : "聊天记录" },	# "ChatWindow:ChatLogViewer", "lbSelCNClew"
}

# 世界发言确认框
YellVerifyBox = {
	'cbNotify'		 : { 'color' : (252.0, 235.0, 179.0), 'text' : "本次在线不再提示" },	# "ChatWindow:YellVerifyBox", "cbNotify"
}

# 玩伴聊天记录窗口
PLMLogViewer = {
	# lbBtns
	'btnHide'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "关 闭" },	# "ChatWindow:PLMLogViewer", "btnHide"
	'btnSave'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "保 存" },	# "ChatWindow:PLMLogViewer", "btnSave"
	# lbTitle
	'lbTitle'		 : { 'color' : (71.0, 35.0, 0.0), 'text' : "【%s】-- 聊天记录" },	# "ChatWindow:PLMLogViewer", "lbTitle"
	'stClew'		 : { 'text' : "为了您的隐私安全，聊天记录不会自动存档，如需要请使用保存功能另外保存。" },	# "ChatWindow:PLMLogViewer", "stClew"
}

# 玩伴聊天窗口
PLMChatWnd = {
	# lbBtns
	'btnSend'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "发 送" },	# "ChatWindow:PLMChatWnd", "btnSend"
	'btnLog'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "聊天记录" },	# "ChatWindow:PLMChatWnd", "btnLog"
	'btnHide'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "关 闭" },	# "ChatWindow:PLMChatWnd", "btnHide"
	# lbTitle
	'lbTitle'		 : { 'color' : (71.0, 35.0, 0.0), 'text' : "【%s】-- 好友聊天" },	# "ChatWindow:PLMChatWnd", "lbTitle"
	# stext
	'stOffline'		 : { 'color' : (164.0, 164.0, 164.0), 'text' : "离线" },	# "ChatWindow:PLMChatWnd", "stOffline"
	'stEmote'		 : { 'text' : "表情" },	# "ChatWindow:PLMChatWnd", "stEmote"
	# send shortcut
	'sendShortcut' : { 'text': "快捷键：\n－－ Ctrl + Enter" },	# "ChatWindow:PLMChatWnd", "sendShortcut"
}
