# -*- coding:gb18030 -*-

import BigWorld
from SpellBase import *

class Spell_TDBNotifyCure( Spell ):
	"""
	仙魔论战统计伤害量技能
	"""
	def __init__( self ):
		Spell.__init__( self )
		
	def springOnCure( self, caster, receiver, cureHP ):
		"""
		技能在治疗产生作用时的回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		"""
		if caster.id == receiver.id:		# 治疗自己不统计
			return
		BigWorld.globalData["TaoismAndDemonBattleMgr"].recordCureData( caster.playerName, caster.getLevel(), caster.getCamp(), caster.base, caster.tongName, cureHP )
	