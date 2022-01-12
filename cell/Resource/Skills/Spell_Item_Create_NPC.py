# -*- coding: gb18030 -*-


import BigWorld
import Math
import random
import math
import csstatus
import csconst

from Spell_Item import Spell_Item
from bwdebug import *

class Spell_Item_Create_NPC( Spell_Item ):
	"""
	通过物品创建一个NPC
	"""
	def init( self, dict ):
		"""
		初始化
		"""
		Spell_Item.init( self, dict )
		self.npcClassName = str( dict[ "param1" ] )										# className
		self.spaceNameXY = dict[ "param2" ].split( "|" )								# 指定的地图名字|坐标|对召唤者可见，例如：feng_ming|210:-35
		self.radius = int( dict["param3"] )												# 召唤半径
		self.lifeTime = int( dict["param4"] )											# 召唤怪的存活时间
		self.spaceName = str(self.spaceNameXY[0])
		self.positions = self.spaceNameXY[1]
		if self.positions != "0":
			self.X = int(self.positions.split(":")[0])
			self.Y = int(self.positions.split(":")[1])
		
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
		positionY = int(caster.position.z)
		if self.positions != "0" and (positionX not in  xrange( self.X-20, self.X+20 ) or positionY not in  xrange( self.Y-20, self.Y+20 )):		# 指定坐标周围20米内
			caster.statusMessage( csstatus.SKILL_SPELL_NOT_POSITION )
			return False
		rangeEntities = caster.entitiesInRangeExt( 50, None, caster.position )
		for e in rangeEntities:			# 搜索周围50米范围内，如果有人召唤了该npc就不能再召唤了
				if e.className == self.npcClassName:
					caster.statusMessage( csstatus.SKILL_SPELL_SOMEONE_USING, e.getName() )
					return False
		return Spell_Item.useableCheck( self, caster, target )


	def cast( self, caster, target ):
		"""
		"""
		Spell_Item.cast( self, caster, target )
		newEntity = caster.createObjectNearPlanes( self.npcClassName, self._getCallPosition( caster ), caster.direction, { "lifetime" : self.lifeTime } )
		newEntity.setTemp( "npc_ownerBase", caster.base )				# 设置施法者为当前NPC的任务拥有者