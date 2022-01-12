# -*- coding: gb18030 -*-

"""
生活技能NPC全局实例基础类
"""

import Language
from bwdebug import *
import csdefine
import NPC


class LivingTrainer( NPC.NPC ):
	"""
	生活技能NPC全局实例基础类 for cell。

	@ivar      attrSkills: 技能列表
	@type      attrSkills dict
	"""

	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )

	def load( self, confSection ):
		"""
		读取技能列表配置文件

		@param confSection: 配置文件的section
		@type  confSection: Language.PyDataSection
		@return: 		无
		"""
		NPC.NPC.load( self, confSection )	# 先加载基层的配置

	def validLearn( self, player, skillID ):
		"""
		是否可学某个生活技能
		"""
		lvskill = player.livingskill
		if lvskill.has_key( skillID ) or len( lvskill ) >= csdefine.LIVING_SKILL_MAX:
			return False
		return True

	def validLevelUp( self, player, skillID ):
		"""
		是否可升级某个生活技能
		"""
		lvskill = player.livingskill
		isMaxLevel = player.liv_isMaxLevel( skillID )
		if lvskill.has_key( skillID ) and not isMaxLevel: return True
		return False
		
	def payMoney( self, player, skillID ):
		"""
		升级技能付钱
		"""
		reqMoney = player.getReqLevelUpMoney( skillID )
		return player.payMoney( reqMoney, csdefine.CHANGE_MONEY_LIVING_LEVEL_UP_SKILL )
		
# livingTrainer.py
