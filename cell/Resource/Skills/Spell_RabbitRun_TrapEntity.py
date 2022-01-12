# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在接受者位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from ObjectScripts.GameObjectFactory import g_objFactory

class Spell_trapReceive( Spell ):
	"""
	系统技能
	生成一个AreaRestrictTransducer的entity(陷阱功能entity)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.trapEntityClass = ""				# 陷阱className


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.trapEntityClass = dict[ "param1" ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		receiver.createObjectNearPlanes( self.trapEntityClass, caster.position, caster.direction, {} )
