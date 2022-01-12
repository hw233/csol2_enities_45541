# -*- coding: gb18030 -*-

# 2009-1-6 gjx

import csdefine
import csstatus
from SpellBase import *

class Spell_770100( SystemSpell ):
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

		receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# 玩家身上加一个安全区域的标志，用于一些其他的判定
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# 禁止PK
		receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )
		# 设置下面这个标记是为了离开时能根据标记状态决定是否发送离开安全区的消息
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) + 1 )
