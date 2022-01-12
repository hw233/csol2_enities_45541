# -*- coding: gb18030 -*-

import BigWorld

import math
import Math
import random

import csdefine
import csstatus

from Spell_Item import Spell_Item
import items

RESULT_GET_ITEM			= 1		# 技能结果1：获取物品
RESULT_CREATE_ENTITY	        = 2	        # 技能结果2：创建entity
RESULT_CHANGE_MODEL		= 3		# 技能结果3：改变当前NPC模型

class Spell_ObjectFromItem( Spell_Item ):
	def __init__( self ):
		Spell_Item.__init__( self )
		self.radius = 3 # 怪物刷新的半径
		self._HP = 0.0
	
	def init( self, dict ):
		self._isDestroy = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )
		Spell_Item.init( self, dict )
		self._spellEntity = dict[ "param2" ].split( "|" ) if len( dict["param2"] ) > 0 else []
		self._spellClassName = self._spellEntity[0]
		if len( self._spellEntity ) > 1:
			self._HP = float( self._spellEntity[1] )
		self._itemInfo = dict[ "param3" ].split( "|" ) if len( dict["param3"] ) > 0 else [] #获得物品相关信息
		
		self._entityInfo = dict[ "param4" ].split( "|" ) if len( dict["param4"] ) > 0 else [] #创建entity
		
		self._cModelInfo = dict[ "param5" ].split( ":" ) if len( dict["param5"] ) > 0 else [] #改变当前NPC模型
		
	
	def receive( self, caster, receiver ):	
		# 获取物品
		if len( self._itemInfo ) > 0: 
			for r in self._itemInfo:
				itemID, itemNum = [ int( i ) for i in r.split( ":" ) ]
				item = items.instance().createDynamicItem( itemID, itemNum )
				caster.addItemAndNotify_( item, csdefine.ADD_ITEM_USE )

		# 创建entity
		if len( self._entityInfo ) > 0:
			dict = {}
			dict[ "level" ] = caster.level
			dict[ "owner" ] = caster.base
			for r in self._entityInfo:
				eid, enum, pos, lifeTime = r.split( ":" )
				dict[ "lifetime" ] = int( lifeTime )
				pos = Math.Vector3( eval( pos ) )
				for i in xrange( eval( enum ) ):
					receiver.createObjectNearPlanes( eid, pos, receiver.direction, dict )

		# 暂时改变客户端模型（指当前客户端）
		if len( self._cModelInfo ) > 0:
			modelNumber, ctime = self._cModelInfo
			caster.clientEntity( receiver.id ).setTempModelNumber( modelNumber, int( ctime ) )

		if self._isDestroy == 1:
			receiver.destroy()

	def useableCheck( self, caster, target ):
		if target.getObject().className != self._spellClassName :
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET	

		if self._HP:
			hpPercent = float( target.getObject().HP )/ float( target.getObject().HP_Max ) * 100.0
			if self._HP < hpPercent:
				return csstatus.SKILL_TARGET_HP_TO0_HIGH

		return Spell_Item.useableCheck( self, caster, target )

	def _getCallPosition( self, entity ):
		# 取得刷怪的位置
		newPos = Math.Vector3()
		if self.radius > 0:
			castPos = entity.position
			newPos.x = castPos.x + random.randint( 0, self.radius ) * random.choice( ( -1, 1 ) )
			newPos.z = castPos.z + math.sqrt( pow( self.radius, 2 ) - pow( newPos.x - castPos.x , 2 ) ) * random.choice( ( -1, 1 ) )
			newPos.y = castPos.y

			result = BigWorld.collide( entity.spaceID, ( newPos.x, newPos.y + 2, newPos.z ), ( newPos.x, newPos.y - 1, newPos.z ) )
			if result != None:
				newPos.y = result[0].y
			else:
				newPos = entity.position

		return newPos
	
#技能结果的1、2、3 随意组合的支持modify by wuxo 2012-5-19