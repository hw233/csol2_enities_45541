# -*- coding: gb18030 -*-


import Resource
from Resource.SkillLoader import g_skills
from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA
import cPickle
import binascii
import Language
import csstatus

SKILL_CONFIG_HEAD = "Datas_"

def updateSkill( srcEntity, floder, skillID ):
	"""
	"""
	#update some skillcfgs
	moduleNames = Language.searchConfigModuleName( "config/SkillTest/" + floder  )
	for moduleName in moduleNames:
		s = moduleName.split("_")
		if len(s) > 1 and s[1] == str(skillID):
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_SKILL_FIND_CONFIG_IN_SERVER, str( ( str(skillID),)) )
			moduleFullName = "config.SkillTest." + floder + "." + moduleName
			compons = moduleFullName.split( "." )
			mod = __import__( moduleFullName )
			for com in compons[1:]:
				mod = getattr( mod, com )
			attrs = dir( mod )
			for attr in attrs:
				if SKILL_CONFIG_HEAD in attr:
					d = cPickle.loads( binascii.a2b_hex( getattr( mod, attr ) ))
					if skillID in g_skills._datas:
						del g_skills._datas[skillID]
						srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_SKILL_CLEAN_OLD_SKILL_IN_SERVER, str( ( str(skillID),)) )
					for i in xrange( 0, 10 ):
						if ( skillID*100 + i ) in g_skills._datas:
							del g_skills._datas[ (skillID*100 + i) ]
					SKILL_DATA._SkillDataMgr__data[skillID] = d
					srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_SKILL_OK_IN_SERVER, str( ( str(skillID),)) )

