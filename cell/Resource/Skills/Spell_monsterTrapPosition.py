# -*- coding: gb18030 -*-

# 系统技能，生成一个MonsterTrap的entity(陷阱功能entity)，在配置的position位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *
import random
import string

class Spell_monsterTrapPosition( Spell ):
	"""
	系统技能
	生成一个AreaRestrictTransducer的entity(陷阱功能entity)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.classNameList = []			# 所有monsterTrap的className
		self.lifetime = 0				# 陷阱销毁时间
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				# 进入陷阱施放的技能
		self.leaveSpell = 0				# 离开陷阱施放的技能


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		classNameStr = str( dict[ "param1" ] )
		classNameStrList = classNameStr.split(";")
		for e in classNameStrList:
			self.classNameList.append( e )
		self.lifetime = int( dict[ "param2" ] )
		self.radius = float( dict[ "param3" ] )
		spellStr = str( dict["param4"] )
		self.enterSpell = int( spellStr.split(";")[0] )
		self.leaveSpell = int( spellStr.split(";")[1] )


	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		if receiver.isReal():
			spaceBase = BigWorld.cellAppData["spaceID.%i" % receiver.spaceID]
			try:
				spaceEntity = BigWorld.entities[ spaceBase.id ]
			except:
				DEBUG_MSG( "not find the spaceEntity!" )
			
			# 出生点，出生油锅
			spaceEntity.base.spawnMonsters( { "entityName" : random.choice( self.classNameList ), "level": spaceEntity.params["copyLevel"], "radius" : self.radius, "enterSpell" : self.enterSpell, "leaveSpell" : self.leaveSpell, "destroySpell" : self.leaveSpell, "lifetime" : self.lifetime } )
		else:
			receiver.receiveOnReal( caster.id, self )
