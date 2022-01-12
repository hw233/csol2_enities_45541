# -*- coding: gb18030 -*-


import BigWorld
import Math
import random
import math
import csstatus
import csconst
import utils

from Spell_Item import Spell_Item
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory

class Spell_Item_Create_Monster( Spell_Item ):
	"""
	通过物品创建一个Monster
	"""
	def init( self, dict ):
		"""
		初始化
		"""
		Spell_Item.init( self, dict )
		self.npcClassName = str( dict[ "param1" ] )										# className
		self.spaceName = str( dict[ "param2" ] )								# 指定的地图名字，例如：feng_ming
		self.radius = int( dict["param3"] )												# 可以召唤怪物的半径，玩家在召唤位置多大范围能召唤
		self.lifeTime = int( dict["param4"] )											# 召唤怪的存活时间
		self.canCallPositions = dict[ "param5" ].split( "|" )
		self.position = ( 0, 0 ,0 )
		
	def _getCallPosition( self, caster ):
		# 取得entity的位置
		newPos = Math.Vector3()
		if self.radius > 0:		
			castPos = caster.position
			newPos.x = castPos.x + random.randint( -self.radius, self.radius )
			newPos.z = castPos.z + random.randint( -self.radius, self.radius )
			newPos.y = castPos.y
			
			result = BigWorld.collide( caster.spaceID, ( newPos.x, newPos.y + 2, newPos.z ), ( newPos.x, newPos.y - 1, newPos.z ) )
			if result != None:
				newPos.y = result[0].y
		else:
			newPos = caster.position
	
		return newPos
		

	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		"""
		if caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) != self.spaceName:		# 指定地图
			caster.statusMessage( csstatus.SKILL_SPELL_NOT_SPACENNAME )
			return False
		
		positionX = int(caster.position.x)
		positionZ = int(caster.position.z)
		flag = 0
		for assignPosition in self.canCallPositions:
			if assignPosition:
				pos = utils.vector3TypeConvert( assignPosition )
				assignPositionX = pos[0]
				assignPositionZ = pos[2]
				if assignPositionX and assignPositionZ and positionX in xrange( assignPositionX - self.radius, assignPositionX + self.radius ) \
				and positionZ in xrange( assignPositionZ - self.radius, assignPositionZ + self.radius ):
					flag = 1
					self.position = tuple( pos )
					break
		if not flag:
			return False
		return Spell_Item.useableCheck( self, caster, target )


	def cast( self, caster, target ):
		"""
		"""
		Spell_Item.cast( self, caster, target )
		newEntity = caster.createObjectNearPlanes( self.npcClassName, self.position, caster.direction, { "spawnPos": self.position, "lifetime" : self.lifeTime } )
		newEntity.firstBruise = 1		# 避免Monster中第一次受伤害对bootyOwner处理
		
		teamMailbox = caster.getTeamMailbox()
		if teamMailbox is not None:										# 如果玩家有队伍
			teamID = caster.getTeamMailbox().id
			bootyOwners = newEntity.searchTeamMember( teamID, Const.TEAM_GAIN_EXP_RANGE )
			newEntity.bootyOwner = ( 0, teamID )						# 设置队伍为npc的战利品拥有者
			if len( bootyOwners ) == 0:
				newEntity.bootyOwner = ( 0, 0 )
		else:
			newEntity.bootyOwner = ( caster.id, 0 )
		newEntity.setTemp( "bootyOwner", newEntity.bootyOwner )
