# -*- coding: gb18030 -*-

from config.skill.Skill.SkillDataMgr import Datas as scs
SKILL_CONFIG_HEAD = "Datas"

k = "\"\"\""

#合并技能配置的工具，只要调用就能把技能脚本全部合并. (这个合并后的结果可能在 Datas下)
def mergeAllConfigs( ):
	"""
	"""
	newConfigfiles = open( "skillConfig.py", "w" )
	for i in dir(scs._skillcfgs):
		if SKILL_CONFIG_HEAD in i:
			newConfigfiles.write( i + " = " + k + getattr( scs._skillcfgs, i ) + k + "\n" )
	newConfigfiles.close()