# -*- coding: gb18030 -*-

import BigWorld
import Math
import random
import math
import csstatus
import csconst
import csdefine
import time
import ECBExtend
import Const

from Spell_Item import Spell_Item

class Spell_Item_Create_NPC_Visible( Spell_Item ):
	"""
	通过物品创建一个NPC
	"""
	
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.param1 = None
		self.param2 = None
		self.param3 = 0
		self.param4 = 100000
	
	def init( self, dict ):
		"""
		初始化
		"""
		Spell_Item.init( self, dict )
		self.npcClassName = str( dict[ "param1" ] )										# className
		if dict["param2"] != "":
			self.param2 = str( dict["param2"] )
			self.spaceNameXY = dict[ "param2" ].split( "|" )								# 指定的地图名字|坐标，例如：feng_ming|210:-35
			self.spaceName = str(self.spaceNameXY[0])
			self.positions = self.spaceNameXY[1]
			self.X = int(self.positions.split(":")[0])
			self.Y = int(self.positions.split(":")[1])	
		
		if dict["param3"] != "":
			self.radius = int( dict["param3"] )												# 召唤半径
		else:
			self.radius = self.param3
		
		if dict["param4"] != "":
			self.lifeTime = int( dict["param4"] )											# 召唤怪的存活时
		else:
			self.lifeTime = self.param4
			
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
		if self.param2 is not None:
			if caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) != self.spaceName:		# 指定地图
				caster.statusMessage( csstatus.SKILL_SPELL_NOT_SPACENNAME )
				return False
			positionX = int(caster.position.x)
			positionY = int(caster.position.z)
			if positionX not in  xrange( self.X-20, self.X+20 ) or positionY not in  xrange( self.Y-20, self.Y+20 ):		# 指定坐标周围20米内可召唤
				caster.statusMessage( csstatus.SKILL_SPELL_NOT_POSITION )
				return False

		return Spell_Item.useableCheck( self, caster, target )

	def cast( self, caster, target ):
		"""
		"""
		Spell_Item.cast( self, caster, target )
		newEntity = caster.createObjectNearPlanes( self.npcClassName, self._getCallPosition( caster ), caster.direction, { "spawnPos":self._getCallPosition( caster ), "lifetime" : self.lifeTime } )
		newEntity.addFlag( csdefine.ENTITY_FLAG_UNVISIBLE )				# 添加不可见标签
		newEntity.firstBruise = 1		# 避免Monster中第一次受伤害对bootyOwner处理
		
		teamMailbox = caster.getTeamMailbox()
		if teamMailbox is not None:										# 如果玩家有队伍
			teamID = caster.getTeamMailbox().id
			bootyOwners = newEntity.searchTeamMember( teamID, Const.TEAM_GAIN_EXP_RANGE )
			newEntity.bootyOwner = ( 0, teamID )						# 设置队伍为npc的战利品拥有者
			if len( bootyOwners ) == 0:
				newEntity.bootyOwner = ( 0, 0 )
			else:
				newEntity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE, teamID )
		else:
			newEntity.bootyOwner = ( caster.id, 0 )
			newEntity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, caster.id )
		newEntity.ownerVisibleInfos = newEntity.bootyOwner
