# -*- coding: gb18030 -*-

# 随机选择位置生成多个AreaRestrictTransducer的entity(陷阱功能entity)

import BigWorld
import random
from utils import vector3TypeConvert
from SpellBase import *

class Spell_CastRandomTrap( Spell ):
	"""
	从配置中随机释放指定个数的陷阱技能
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		Spell.__init__( self )
		self.skillIDs = []				# 技能IDs
		self.skillNum = 1				# 陷阱个数
		self.probSkill = 1				# 有概率释放的技能
		self.activeRate = 0				# probSkill释放的概率

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.skillIDs = str( dict["param1"] ).strip( ";" ).split( ";" )
		self.skillNum = int( dict["param2"] )
		self.probSkill = str( dict["param3"] ).strip( ";" ).split( ";" )[0]
		self.activeRate = float( str( dict["param3"] ).strip( ";" ).split( ";" )[1] )
		
	def getRandomSkill( self ):
		"""
		获得随机释放技能
		"""
		if self.activeRate <= 0 or random.randint( 0, 100 ) > self.activeRate:			# probSkill不可以释放
			if self.skillNum > len( self.skillIDs ):
				ERROR_MSG( "Skill %i config error, its skillNum is larger than skill counts" % self.getID() )
				return []
			return random.sample( self.skillIDs, self.skillNum )
			
		if self.skillNum -1 > len( self.skillIDs ):
			ERROR_MSG( "Skill %i config error, its skillNum is larger than skill counts" % self.getID() )
			return []
		skills = []
		skills = random.sample( self.skillIDs, self.skillNum - 1 )
		skills.append( self.probSkill )
		return skills

	def cast( self, caster, target ):
		"""
		virtual method.
		技能实现的目的
		"""
		randList = self.getRandomSkill()
		for skill in randList:
			if caster:
				caster.spellTarget( int( skill ), caster.id )

class Spell_TrapSpecificPosition( Spell ):
	"""
	在指定位置生成一个AreaRestrictTransducer的entity(陷阱功能entity)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.lifetime = 0				# 陷阱销毁时间
		self.isDisposable = 0			# 是否一次性陷阱（即触发一次就销毁）
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				# 进入陷阱施放的技能
		self.leaveSpell = 0				# 离开陷阱施放的技能
		self.modelNumber =  ""			# 陷阱对应的模型(带光效的)
		self.modelScale = 1.0			# 模型缩放比例
		self.position = None			# 陷阱位置

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		timeList = str( dict["param1"] ).strip( ";" ).split( ";" )
		self.lifetime = int( timeList[0] )
		if len( timeList ) >= 2:
			self.isDisposable = int( timeList[1])
			
		self.radius = float( dict[ "param2" ] )
		spellStr = str( dict["param3"] ).strip( ";" ).split( ";" )
		self.enterSpell = int( spellStr[0] )
		if len( spellStr ) >= 2:
			self.leaveSpell = int( spellStr[1] )
		
		modelStr = str( dict[ "param4"] ).strip( ";" ).split( ";" )
		self.modelNumber = str( modelStr[0] )
		if len( modelStr ) >= 2:
			self.modelScale = float( modelStr[1] )
		
		self.position = vector3TypeConvert( str( dict[ "param5" ] ) )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		dict = { "radius" : self.radius, "enterSpell" : self.enterSpell, "destroySpell" : self.leaveSpell,\
				"modelNumber" : self.modelNumber, "lifetime" : self.lifetime, "uname" : self.getName(),\
				 "isDisposable" : self.isDisposable, }
		trap = caster.createEntityNearPlanes( "AreaRestrictTransducer", self.position, (0, 0, 0), dict )
		trap.modelScale = self.modelScale				# 设置陷阱模型的缩放比例
