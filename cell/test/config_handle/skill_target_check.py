# -*- coding: gb18030 -*-

import BigWorld
from config.skill.Skill.SkillDataMgr import Datas
SKILL_CONFIG_HEAD = "Datas"

def findErrorInAllConfigs():
	"""
	���ң�
	 ʩչ������entity����
	 ���������ǵ���
	���ֲ��������õ�����
	"""
	for i in dir(Datas._skillcfgs):
		if SKILL_CONFIG_HEAD in i:
			id = int(i.split("_")[1])
			if Datas[id]["CastObjectType"]["type"] == 1 and Datas[id]["ReceiverCondition"]["Area"] == 0:
				print "findErrorInAllConfigs1:%s"%i
			elif Datas[id]["CastObjectType"]["type"] == 0 and Datas[id]["ReceiverCondition"]["Area"] == 0:
				print "findErrorInAllConfigs0:%s"%i