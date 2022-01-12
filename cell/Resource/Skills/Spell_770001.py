# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import csdefine
import csstatus
from SpellBase import *

class Spell_770001( SystemSpell ):
	"""
	系统技能
	进入摆摊限制区域时施放此技能
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
			receiver.actCounterInc( csdefine.ACTION_ALLOW_VEND )			# 允许摆摊
			receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# 禁止PK
			#receiver.statusMessage( csstatus.VEND_ENTER_VEND_ALLOWED_AREA )
			# 设置下面这个标记是为了离开时能根据标记状态决定是否发送离开安全区的消息
			receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) + 1 )
		else:	# 加入对ghost的支持。17:31 2009-1-16，wsf
			receiver.receiveOnReal( -1, self )								# 施法者ID传个-1，表示没施法者