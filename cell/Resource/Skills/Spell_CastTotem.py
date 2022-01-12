# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在施放者位置

import BigWorld
import csdefine
import csstatus
import utils
from SpellBase import *

class Spell_CastTotem( Spell ):
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
		self.repeattime = 0				# 循环伤害时间
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				# 进入陷阱施放的技能
		self.leaveSpell = 0				# 离开陷阱施放的技能
		self.destroySpell = 0			# 陷阱死亡时释放的技能
		self.modelNumber =  ""			# 陷阱对应的模型(带光效的)
		self.isDisposable = False		# 是否一次性陷阱（即触发一次就销毁）

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		timeStr = dict[ "param1" ]
		timeList = [int( t ) for t in timeStr.split(",") ]
		self.lifetime = timeList[0]
		if len( timeList ) >= 2:
			self.repeattime = timeList[1]
			
		self.radius = float( dict[ "param2" ] )
		self.modelNumber = str( dict[ "param3" ]).split(";")[0] 
		self.casterMaxDistanceLife = int( dict[ "param4" ] )

		if len( dict[ "param5" ] ) > 0:
			self.enterSpell, self.leaveSpell, self.destroySpell, self.isDisposable = [ int(s) for s in dict[ "param5" ].split(",") ]
	
	def _getDict( self, caster, target ):
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"destroySpell" : self.destroySpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"casterMaxDistanceLife" : self.casterMaxDistanceLife, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : self.lifetime, \
			"repeattime" : self.repeattime, \
			"casterID" : caster.id, \
			"uname" : self.getName() }
			
		return dict
		
	def onArrive( self, caster, target ):
		caster.createEntityNearPlanes( "SkillTrap", target.getObjectPosition(), (0, 0, 0), self._getDict( caster, target ) )
		Spell.onArrive( self, caster, target )


class Spell_CastTotemNotCaster( SystemSpell ):
	#目标是entity
	def __init__( self ):
		"""
		构造函数。
		"""
		SystemSpell.__init__( self )
		self.lifetime = 0				# 陷阱销毁时间
		self.repeattime = 0				# 循环伤害时间
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				# 进入陷阱施放的技能
		self.leaveSpell = 0				# 离开陷阱施放的技能
		self.destroySpell = 0			# 陷阱死亡时释放的技能
		self.modelNumber =  ""			# 陷阱对应的模型(带光效的)
		self.isDisposable = False		# 是否一次性陷阱（即触发一次就销毁）

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		timeStr = dict[ "param1" ]
		timeList = [int( t ) for t in timeStr.split(",") ]
		self.lifetime = timeList[0]
		if len( timeList ) >= 2:
			self.repeattime = timeList[1]
			
		self.radius = float( dict[ "param2" ] )
		self.modelNumber = str( dict[ "param3" ]).split(";")[0] 
		self.casterMaxDistanceLife = int( dict[ "param4" ] )

		if len( dict[ "param5" ] ) > 0:
			self.enterSpell, self.leaveSpell, self.destroySpell, self.isDisposable = [ int(s) for s in dict[ "param5" ].split(",") ]
			
	def _getDict( self, caster, target ):
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"destroySpell" : self.destroySpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"casterMaxDistanceLife" : self.casterMaxDistanceLife, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : self.lifetime, \
			"repeattime" : self.repeattime, \
			"casterID" : 0, \
			"uname" : self.getName() }
			
		return dict
	
	def onArrive( self, caster, target ):
		targetEntity = target.getObject()
		targetEntity.createEntityNearPlanes( "SkillTrap", utils.navpolyToGround( targetEntity.spaceID, target.getObjectPosition(), 0.2, 20.0 ), (0, 0, 0), self._getDict( caster, target ) )
		SystemSpell.onArrive( self, caster, target )