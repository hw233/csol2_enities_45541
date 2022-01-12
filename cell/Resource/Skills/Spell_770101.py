# -*- coding: gb18030 -*-

# 2009-1-6 gjx

import csdefine
import csstatus
from SpellBase import *

class Spell_770101( SystemSpell ):
	"""
	系统技能
	离开PK限制区时施放此技能
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
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# 只对玩家施放（不包括宠物）
			return
		if not receiver.isReal() :
			receiver.receiveOnReal( -1, self )							# 施法者ID传个-1，表示没施法者
			return

		receiver.removeFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# 移除玩家身上的安全区域的标志
		receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )		# 允许PK
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) - 1 )
		tempFlag = receiver.queryTemp( "RestrictAreaFlag" )
		if tempFlag < 1 :
			receiver.statusMessage( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA )
			receiver.removeTemp( "RestrictAreaFlag" )
