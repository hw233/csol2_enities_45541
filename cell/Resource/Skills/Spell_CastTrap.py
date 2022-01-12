# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在怪物死亡时的位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *

class Spell_CastTrap( Spell ):
	"""
	系统技能
	生成一个AreaRestrictTransducer的entity(陷阱功能entity)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.lifetime = 0				# 陷阱销毁时间
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				# 进入陷阱施放的技能
		self.leaveSpell = 0				# 离开陷阱施放的技能
		self.isDisposable = 0			# 是否一次性陷阱（即触发一次就销毁）
		self.modelNumber =  ""			# 陷阱对应的模型(带光效的)
		self._modelScale = 1.0			# 陷阱模型缩放比例

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.lifetime = int( dict[ "param1" ] )
		self.radius = float( dict[ "param2" ] )
		spellStr = str( dict["param3"] )
		self.enterSpell = int( spellStr.split(":")[0] )
		self.leaveSpell = int( spellStr.split(":")[1] )
		self.isDisposable = int( dict[ "param4" ] )
		spellStr_ = str( dict[ "param5" ] )
		self.modelNumber = str( spellStr_.split(":")[0] )
		self._modelScale = float( spellStr_.split(":")[1] )

	def cast( self, caster, target ):
		"""
		virtual method.
		技能实现的目的
		"""
		dict = { "radius" : self.radius, "enterSpell" : self.enterSpell, "destroySpell" : self.leaveSpell, "modelNumber" : self.modelNumber, "lifetime" : self.lifetime, "uname" : self.getName(),"isDisposable" : self.isDisposable }
		trap = caster.createEntityNearPlanes( "AreaRestrictTransducer", caster.position, (0, 0, 0), dict )
		trap.modelScale = self._modelScale		# 设置陷阱模型的缩放比例
