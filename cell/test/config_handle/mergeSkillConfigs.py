# -*- coding: gb18030 -*-

from config.skill.Skill.SkillDataMgr import Datas as scs
SKILL_CONFIG_HEAD = "Datas"

k = "\"\"\""

#�ϲ��������õĹ��ߣ�ֻҪ���þ��ܰѼ��ܽű�ȫ���ϲ�. (����ϲ���Ľ�������� Datas��)
def mergeAllConfigs( ):
	"""
	"""
	newConfigfiles = open( "skillConfig.py", "w" )
	for i in dir(scs._skillcfgs):
		if SKILL_CONFIG_HEAD in i:
			newConfigfiles.write( i + " = " + k + getattr( scs._skillcfgs, i ) + k + "\n" )
	newConfigfiles.close()