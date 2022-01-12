# -*- coding: gb18030 -*-

from config.skill.Skill.SkillDataMgr import Datas as SkillData
import skills
import Language
import cPickle
import binascii
import BigWorld
import csstatus
SKILL_CONFIG_HEAD = "Datas_"
def updateSkill( floder, skillID ):
	"""
	"""
	#update some skillcfgs
	srcEntity = BigWorld.player()
	moduleNames = Language.searchConfigModuleName( "config/SkillTest/" + floder  )
	for moduleName in moduleNames:
		s = moduleName.split("_")
		if len(s) > 1 and s[1] == str(skillID):
			srcEntity.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_SKILL_FIND_CONFIG_IN_CLIENT, str( ( str(skillID),)) )
			moduleFullName = "config.SkillTest." + floder + "." + moduleName
			compons = moduleFullName.split( "." )
			mod = __import__( moduleFullName )
			for com in compons[1:]:
				mod = getattr( mod, com )
			attrs = dir( mod )
			for attr in attrs:
				if SKILL_CONFIG_HEAD in attr:
					d = cPickle.loads( binascii.a2b_hex( getattr( mod, attr ) ))
					if skills._g_skills.has_key( skillID ):
						del skills._g_skills[ skillID ]
						srcEntity.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_SKILL_CLEAN_OLD_SKILL_IN_CLIENT, str( ( str(skillID),)) )

					for i in xrange( 0, 10 ):
						if  skills._g_skills.has_key((skillID*100 + i)):
							del skills._g_skills[ skillID*100 + i ]
					SkillData._SkillDataMgr__data[skillID] = d
					srcEntity.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_SKILL_OK_IN_CLIENT, str( ( str(skillID),)) )