# -*- coding: UTF-8 -*-
#������
main = { "lbTitle": { "color": ( 255, 241, 192, 255 ), "text": "�Ի�", 'charSpace': 2 },
		"btnFulfill": { "font":"MSYHBD.TTF","fontSize":12, "text":"�������" },
		"btnAccept": { "font":"MSYHBD.TTF","fontSize":12, "text": "��������" },
		"btnQuit": { "font":"MSYHBD.TTF","fontSize":12, "text": "�� ��" },
		"btnShut": { "font":"MSYHBD.TTF","fontSize":12, "text": "�� ��" },
		"finished": { "text": "���" },
		"unfinished": { "text": "δ���" },
		"failure": { "text": "ʧ��" },
		"questAim": { "text": "����Ŀ��" },
		"followReward": { "text": "��������н���" },
		"querySubmit": { "text": "��Ҫ�ύ����Ʒ" },
		}

GroupRewards = { "followReward": { "text": "�㽫���������Ʒ����"},
			"groupExtrReward": { "text": "���һ������Ķ����ܽ���:"},
			"randomStuff": { "text": "������һ��������Ͻ�����"},
			"choiceItem": { "text": "�ɹ�ѡ����Ʒ"},
			"randomItem": { "text": "���������Ʒ"},
			"fixedRandomItem": { "text": "�̶������Ʒ����"},
		}

rewards = { "reward_fix_random" : { "text": "�̶��������:" },
		"reward_exp" : { "text": "���ﾭ�齱��:" },
		"reward_money" : { "text": "��Ǯ����:" },
		"reward_potential" : { "text": "Ǳ�ܽ���:" },
		"reward_prestige" : { "text": "��������:" },
		"reward_merchant_money" : { "text": "���̽���:" },
		"reward_tong_money" : { "text": "����ʽ���:" },
		"reward_tong_buildval" : { "text": "��Ὠ��Ƚ���:" },
		"reward_tong_contribute" : { "text": "��ṱ�׶Ƚ���:" },
		"reward_pet_exp" : { "text": "���ﾭ�齱��:" },
		"reward_ie_title" : { "text": "�ƺŽ���:" },
		"reward_deposit" : { "text": "����Ѻ��:" },
		"reward_random" : { "text": "�������:" },
		"reward_tong_fete": { "text": "���뽱��:"},
		"petLevelTip": { "text": "��ע�⣬�������ȼ�������ȼ������󣬻�����յľ��������Ӱ�졣"},
		"sacrificeReward": { "text": "����һ�����" },
		"reward_tongActionVal": { "text": "����ж�������" },
		"reward_daoheng" : { "text": "������н���" },
		"reward_skill" : { "text": "���ܽ���:" },
		"reward_tong_exp" : { "text": "��ᾭ�齱��:" },
		}

submit = { "needPet": { "text": "�������:" },
		"curPets": { "text": "���г���" },
		"questPets": { "text": "�������" },
		"btnTransfer": { "text": "ת �� �� ��" },
		"pleaseInput": { "text": "�����:%s" },
		"petLevel": { "text": "%d��" },
		}

exp2pot = {
	'cancelBtn'		 : { 'text' : "ȡ��" },
	'okBtn'			 : { 'text' : "ȷ��" },
	'lbExp'			 : { 'text' : "��Ҫ����:" },
	'lbPotential'	 : { 'text' : "�һ�Ǳ��" },
	'lbTitle'		 : { 'color' : 0xffffff, 'text' : "�һ�Ǳ��",  'limning' : 2 },
}

LVReminder = {
	'btnOk' : { 'text' : "ȷ��" },
}

ArtiRefine = {
	'lbTitle': { 'text' : "��������", 'color': ( 255,241,192,255 ) },
	'btnRefine':{ 'text': "��������" },
	'btnCancel':{'text':"ȡ��" },
	'explain':{'text': "@S{4}��Ҫ��������ô��@B@S{4}���ȣ�����������ֻ������ɫ������@B@S{4}��Σ�����Ҫ�ռ��㹻�Ĳ��ϡ��������ﹺ���Ӧ�����ȼ���δ���������ס��Ҽ�������������������֮��Ϳ��Ի�ÿ���������ס�ͬʱ�����������ȼ��ռ���Ӧ�ȼ����㹻����������������ȼ��������Ӧ���£�@B@S{10}50-59����20��1�����������@B@S{10}60-69����25��2�����������@B@S{10}70-79����30��3�����������@B@S{10}80-89����35��4�����������@B@S{10}90-99����40��5�����������@B@S{10}100-109����45��6�����������@B@S{4}��󣬽����������·��Ŀտ��У��㡰����������֮��Ϳ��Խ������������Ϊ������"},
}

UnchainPrentice = {
	'lbTitle': { 'color' : (255.0, 248.0, 158.0), 'text' : "�����ϵ" },
}

import Language
if Language.LANG == Language.LANG_BIG5:
	ArtiRefine['explain'] = {'text': "@S{4}��Ҫ��������ô��@B@S{4}���ȣ�����������ֻ������ɫ������@B@S{4}��Σ�����Ҫ�ռ��㹻�Ĳ��ϡ��������ﹺ���Ӧ�����ȼ���δ���������ס��Ҽ�������������������֮��Ϳ��Ի�ÿ���������ס�ͬʱ�����������ȼ��ռ���Ӧ�ȼ����㹻����������������ȼ��������Ӧ���£�@B@S{10}50-59����20��1�����������@B@S{10}60-69����25��2�����������@B@S{10}70-79����30��3�����������@B@S{10}80-89����35��4�����������@B@S{10}90-99����40��5�����������@B@S{10}100-109����45��6�����������@B@S{4}��󣬽����������·��Ŀտ��У��㡰����������֮��Ϳ��Խ������������Ϊ������"}
