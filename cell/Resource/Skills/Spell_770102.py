# -*- coding: gb18030 -*-

#新的进入安全区陷进触发技能
#增加安全区陷阱的高度判断
# wuxo  2012-6-5

import csdefine
from SpellBase import *

class Spell_770102( SystemSpell ):
	"""
	系统技能
	进入PK限制区时施放此技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		SystemSpell.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# 只对玩家施放（不包括宠物）
			return
		if not receiver.isReal():
			receiver.receiveOnReal( -1, self )						# 施法者ID传个-1，表示没施法者
			return
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) + 1 )
		self.receiveLinkBuff( caster, receiver )# 接收额外的CombatSpell效果，通常是buff(如果存在的话)