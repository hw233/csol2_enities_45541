# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import csdefine
import csstatus
from SpellBase import *
import Love3

class Spell_in_lava( SystemSpell ):
	"""
	玩家在熔岩中
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		SystemSpell.__init__( self )
		self.param1 = 0			#skill ID

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		self.param1 = int( dict[ "param1" ] )				#技能ID
		self.param2 = int( str( self.param1 ) + "01" )		#技能对应的第一个BUFF ID

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) ):		# 只对玩家施放（不包括宠物）
			return

		if receiver.isReal():
			if receiver.findBuffByID( self.param2 ) is None:
				receiver.removeTemp( "In_lava_List" )
			ids = receiver.queryTemp( "In_lava_List", [] )
			if caster.id in ids:
				return
			ids.append( caster.id )
			receiver.setTemp( "In_lava_List", ids )
			if len( ids ) == 1:
				Love3.g_skills[self.param1].receiveLinkBuff( None, receiver )

		else:
			receiver.receiveOnReal( -1, self )								# 施法者ID传个-1，表示没施法者