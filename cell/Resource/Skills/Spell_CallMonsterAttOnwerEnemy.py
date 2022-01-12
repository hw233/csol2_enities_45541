# -*- coding: gb18030 -*-
import random
import Math
import BigWorld
from bwdebug import *
from SpellBase import Spell
from Domain_Fight import g_fightMgr


class Spell_CallMonsterAttOnwerEnemy( Spell ):
	"""
	创建怪物并让怪物攻击自己敌人列表里的指定怪物
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.callMonsterID = ""
		self.rangeRandom = 0
		self.attacIndex = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.callMonsterID = dict["param1"]
		self.rangeRandom = float( dict["param2"] )
		self.attacIndex = int( dict["param3"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell.receive( self, caster, receiver )
		e = caster.createObjectNear( self.callMonsterID, self._getCallPosition( caster ), caster.direction, { "level": caster.level, } )
		g_fightMgr.buildGroupEnemyRelationByIDs( e, caster.enemyList.keys() )
		targetID = caster.getEnemyByIndex( self.attacIndex )
		if targetID:
			e.targetID = targetID
	
	def _getCallPosition( self, caster ):
		# 取得entity的位置
		newPos = Math.Vector3()
		if self.rangeRandom > 0:		
			castPos = caster.position
			newPos.x = castPos.x + random.randint( -self.rangeRandom, self.rangeRandom )
			newPos.z = castPos.z + random.randint( -self.rangeRandom, self.rangeRandom )
			newPos.y = castPos.y
			
			result = BigWorld.collide( caster.spaceID, ( newPos.x, newPos.y + 2, newPos.z ), ( newPos.x, newPos.y - 1, newPos.z ) )
			if result != None:
				newPos.y = result[0].y
		else:
			newPos = caster.position
	
		return tuple( newPos )