# -*- coding: gb18030 -*-
#
# $Id: Spell_LivingSkill.py,v 1.1 10:13 2009-12-12 jiangyi Exp $

"""
生活技能类（主用于描述处理）。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
from LivingConfigMgr import LivingConfigMgr
from config.client.labels.skills import lbs_Spell_LivingSkill

lvc = LivingConfigMgr.instance()

class Spell_LivingSkill( Spell ):
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )


	def getDescription( self ):
		"""
		生活技能需要单独的描述,用以增加当前复活点记录地区的信息
		"""
		player = BigWorld.player()
		skillID = int( self._datas['ID'] )
		if not player.livingskill.has_key( skillID ):
			return lbs_Spell_LivingSkill[1]
		lvSkill = player.livingskill[skillID]
		des = lvc.getDesByLevel( skillID, lvSkill[0] )
		if des is None or des == "":
			return ""
		dess = des.split("|")
		des = dess[len(dess)-1]
		return des						# self._datas[ "Description" ]
