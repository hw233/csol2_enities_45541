# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Key.py
"""
使用冰封珠销毁相应的怪物同时恢复成对应的水晶球和雕像
"""

from bwdebug import *
from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import ECBExtend
import BigWorld
import csconst
import csdefine

class Spell_Item_Frozen_Beads( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self.amount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )
		self.range = float( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0.0 )
		monsterMapping = str( dict[ "param3" ] )
		self.monsterMappingDict = {}
		for i in monsterMapping.split(";"):
			key = i.split("|")[0]
			value = i.split("|")[1]
			self.monsterMappingDict[ key ] = value
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		monsterAmount = 0
		entityList = caster.entitiesInRangeExt( self.range, "Monster", caster.position )
		for entity in entityList:
			if entity.className == self.monsterMappingDict.keys() and monsterAmount < self.amount:
				className = self.monsterMappingDict[ entity.className ]
				newDict = {"spawnPos": tuple(entity.position ), "level": entity.level, "spawnMB": entity.spawnMB }
				monster = receiver.createObjectNearPlanes( className, entity.position, entity.direction, newDict )
				entity.resetEnemyList()
				entity.spawnMB = None
				entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
				monsterAmount += 1
				pass
#		spaceBase = caster.getCurrentSpaceBase()
#		spaceBase.cell.destroyAndRestoreMonster( self.amount )		# 触发能够恢复相应数量的水晶球或者雕像
		
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if caster.getCurrentSpaceType() != csdefine.SPACE_TYPE_SHUIJING:		# 必须在水晶副本中才可以用
			return csstatus.CIB_MSG_ITEM_NOT_USED_IN_HERE
		return Spell_Item.useableCheck( self, caster, target)
