# -*- coding: UTF-8 -*-

main = {
	"history" : { "text" : "�����¼" },
	"setting" : { "text" : "��ҳ����" },
	"broadcast" : { "text" : "���͹㲥" },
	"set_chns" : { "text" : "����" },
	"scroll_up" : { "text" : "�����¼�Ϸ�" },
	"scroll_down" : { "text" : "�����¼�·�" },
	"scroll_end" : { "text" : "�����¼�����ײ�" },
	"extend" : { "text" : "��ʾ���촰��" },
	"furl" : { "text" : "�������촰��" },
	}

# ��Ϣ������
MSGReceiver = {
	'tpGather': { 'text': "�ۺ�" },
	'InputBoxTips' : { 'text' : "����ҳ������" },
	}

# ��Ϣ��ҳ�����˵�
pgMenu = {
	'miLock': { 'text': "������ҳ" },
	'miUnlock': { 'text': "������ҳ" },
	'miDock' : { 'text' : "ͣ����ҳ" },
	'miRename': { 'text': "��������" },
	'miReset': { 'text': "���÷�ҳ" },
	'miBackColor': { 'text': "ҳ���ɫ" },
	'miSetChannel': { 'text': "Ƶ������" },
	'miDelete': { 'text': "�Ƴ���ҳ" },
	'miCreate': { 'text': "������ҳ" },
	'miSetColor': { 'text': "Ƶ����ɫ" },
	}

# ��Ϣ�����߲����˵�
tMenu = {
	'miWhisper': { 'text': "˽��" },
	'miViewRole': { 'text': "�鿴�����Ϣ" },
	'miCopy': { 'text': "�����������" },
	'miInviteBuddy': { 'text': "��Ϊ����" },
	'miBlacklist': { 'text': "���������" },
	'miFriendChat': {'text': "��������"},
	'miMakeTeam': { 'text': "���" },
	'miInviteFamily': { 'text': "����������" },
	'miInviteTong': { 'text': "���������" },
	}

# ��ɫ�㲥����
RoleBroadcaster = {
	'title': { 'text': "�㲥" ,'charSpace':2, 'limning' : 2},
	'inputTitle': { 'color': (-2,236,203), 'text': "��������" },
	'propTitle': { 'color': (-2,236,203), 'text': "����ѡ��" },
	'rbTunnel': { 'text': "ʹ�õ����Ž�(��֧�ֱ���)" },
	'rbWelkin': { 'text': "ʹ�������Ž�" },
	'rtRemind': { 'color': (-2,236,203), 'text': "ע������Ʒ����û����Ӧ��Ʒʱ����ֱ��ʹ�ö�Ӧ�Ļ���֧����" },
	'btnSend': { 'text': "�� ��" },
	'btnCancel': { 'text': "ȡ ��" },
	'stRemain': { 'text': "ʣ��������%s" },
	}

# Ƶ������
ChannelFilter = {
	'title' : { 'text' : "Ƶ������", 'charSpace':2,  'limning' : 2 },
	'tips' : { 'text' : "���á�%s����ҳ" },
	'btnOk' : { 'text' : "ȷ ��" },
	'btnCancel' : { 'text' : "ȡ ��" },
	}

# ��ɫ��ȡ
ColorSetter = {
	'title' : { 'text' : "Ƶ����ɫ����", 'charSpace':2,  'limning' : 2 },
	'btnOk' : { 'text' : "ȷ ��" },
	'btnCancel' : { 'text' : "ȡ ��" },
	}

# �����¼����
ChatLogViewer = {
	'btnRefresh'	 : { 'color' : (255.0, 248.0, 158.0), 'text' : "ˢ ��" },	# "ChatWindow:ChatLogViewer", "btnRefresh"
	'btnCNSelect'	 : { 'color' : (255.0, 248.0, 158.0), 'text' : "Ƶ��ѡ��" },	# "ChatWindow:ChatLogViewer", "btnCNSelect"
	'btnSave'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "�� ��" },	# "ChatWindow:ChatLogViewer", "btnSave"
	'lbTitle'		 : { 'text' : "�����¼",  'limning' : 2 },	# "ChatWindow:ChatLogViewer", "lbTitle"
	'lbSelCNClew'	 : { 'text'	 : "�����¼" },	# "ChatWindow:ChatLogViewer", "lbSelCNClew"
}

# ���緢��ȷ�Ͽ�
YellVerifyBox = {
	'cbNotify'		 : { 'color' : (252.0, 235.0, 179.0), 'text' : "�������߲�����ʾ" },	# "ChatWindow:YellVerifyBox", "cbNotify"
}

# ��������¼����
PLMLogViewer = {
	# lbBtns
	'btnHide'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "�� ��" },	# "ChatWindow:PLMLogViewer", "btnHide"
	'btnSave'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "�� ��" },	# "ChatWindow:PLMLogViewer", "btnSave"
	# lbTitle
	'lbTitle'		 : { 'color' : (71.0, 35.0, 0.0), 'text' : "��%s��-- �����¼" },	# "ChatWindow:PLMLogViewer", "lbTitle"
	'stClew'		 : { 'text' : "Ϊ��������˽��ȫ�������¼�����Զ��浵������Ҫ��ʹ�ñ��湦�����Ᵽ�档" },	# "ChatWindow:PLMLogViewer", "stClew"
}

# ������촰��
PLMChatWnd = {
	# lbBtns
	'btnSend'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "�� ��" },	# "ChatWindow:PLMChatWnd", "btnSend"
	'btnLog'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "�����¼" },	# "ChatWindow:PLMChatWnd", "btnLog"
	'btnHide'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "�� ��" },	# "ChatWindow:PLMChatWnd", "btnHide"
	# lbTitle
	'lbTitle'		 : { 'color' : (71.0, 35.0, 0.0), 'text' : "��%s��-- ��������" },	# "ChatWindow:PLMChatWnd", "lbTitle"
	# stext
	'stOffline'		 : { 'color' : (164.0, 164.0, 164.0), 'text' : "����" },	# "ChatWindow:PLMChatWnd", "stOffline"
	'stEmote'		 : { 'text' : "����" },	# "ChatWindow:PLMChatWnd", "stEmote"
	# send shortcut
	'sendShortcut' : { 'text': "��ݼ���\n���� Ctrl + Enter" },	# "ChatWindow:PLMChatWnd", "sendShortcut"
}
