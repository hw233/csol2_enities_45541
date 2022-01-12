# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import csdefine
import csstatus
from SpellBase import *

class Spell_770002( SystemSpell ):
	"""
	系统技能
	离开摆摊限制区域时施放此技能
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
		if receiver.isReal():
			receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )		# 允许PK
			receiver.actCounterDec( csdefine.ACTION_ALLOW_VEND )			# 禁止摆摊
			receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) - 1 )
			tempFlag = receiver.queryTemp( "RestrictAreaFlag" )
			if tempFlag < 1 :
				#receiver.statusMessage( csstatus.VEND_LEAVE_VEND_ALLOWED_AREA )
				receiver.removeTemp( "RestrictAreaFlag" )
		else:	# 加入对ghost的支持。17:31 2009-1-16，wsf
			receiver.receiveOnReal( -1, self )			# 施法者ID传个-1，表示没施法者