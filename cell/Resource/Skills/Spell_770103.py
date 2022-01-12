# -*- coding: gb18030 -*-

#新的离开安全区陷进触发技能
#增加安全区陷阱的高度判断
# wuxo  2012-6-5

import csdefine
import csstatus
from SpellBase import *
SAFE_AREA_BUFF_ID = 22020 #安全区陷进Buff

class Spell_770103( SystemSpell ):
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
			receiver.receiveOnReal( -1, self )	# 施法者ID传个-1，表示没施法者
			return
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) - 1 )
		tempFlag = receiver.queryTemp( "RestrictAreaFlag" )
		if tempFlag < 1 :
			#中断安全区陷阱buff
			if receiver.findBuffByBuffID( SAFE_AREA_BUFF_ID ) :
				receiver.removeBuffByBuffID( SAFE_AREA_BUFF_ID, ( csdefine.BUFF_INTERRUPT_NONE, ) )
				receiver.removeTemp( "RestrictAreaFlag" )