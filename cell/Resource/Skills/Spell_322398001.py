# -*- coding: gb18030 -*-
"""
模糊的纸条，模糊的纸条使用时触发
"""
import csstatus
import csdefine
import csconst
import Math
import math
import random
import BigWorld
from Spell_Item import Spell_Item
from ObjectScripts.GameObjectFactory import g_objFactory
from bwdebug import *

class Spell_322398001( Spell_Item ):
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
		Spell_Item.init( self, dict )
		self._monsterIDs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split('|')		# 要生成的盗宝贼怪物的ID（className）
		self._monsterDropItemID = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) 				# 生成的怪物将会掉落的物品

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		#----坐标偏移量---- #
		rad = math.pi * 2.0 * random.random()
		pos = Math.Vector3( caster.position )
		distance = 2 + 2 * random.random()
		pos.x += distance * math.sin( rad )
		pos.z += distance * math.cos( rad )
		index = random.randint( 0, len( self._monsterIDs ) - 1 )
		( x, y, z ) = pos
		collide = BigWorld.collide( caster.spaceID, ( x, y + 2, z ), ( x, y - 2, z ) )
		if collide != None:
			y = collide[0].y
		pos = ( x, y, z )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		level = item.query('level')

		newEntity = caster.createObjectNearPlanes( self._monsterIDs[index], pos, caster.direction, { "spawnPos" : tuple( pos ), "level":level } )
		if newEntity.isEntityType( csdefine.ENTITY_TYPE_TREASURE_MONSTER ):
			newEntity.setOwner( caster )					# 所有权归该玩家所有
			newEntity.setTemp( "dropItem", self._monsterDropItemID )# 设置掉落的物品，此怪必掉一级藏宝图
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s] ." % uid )
			return

		treasureSpace = item.query( "treasure_space", "" )		# 取出模糊的纸条中的地图信息
		treasurePosStr = item.query( "treasure_position", None )# 取出模糊的纸条中的坐标信息
		treasurePosArr = treasurePosStr.split(',')
		treasurePos = ( int( treasurePosArr[0] ), int(treasurePosArr[1]) )
		if treasureSpace == "" or treasurePos == None:
			# 如果没取出来，说明当初没有设置这些信息，地图信息和坐标信息是必须要有的，并且是由程序主动设置生成的
			ERROR_MSG( "Your treasure paper has lost location messages!" )
			return csstatus.SKILL_CANT_CAST
		self._treatureLevel = int( item.getLevel() )	# 用来存储宝图级别
		if not self.isTreasurePosValid( caster, treasureSpace, treasurePos, 5 ):
			# 如果不在对应的坐标位置附近则不能挖宝
			return csstatus.SKILL_TREASURE_POS_NOT_VALID
		return Spell_Item.useableCheck( self, caster, target)

	def isTreasurePosValid( self, player, spaceName, position, offset ):
		"""
		检查玩家挖宝位置是否合法（是否处于某个地图spaceName的坐标position范围内）
		@param 	player		:	被检查的玩家
		@type 	player		:	Role
		@param 	spaceName	:	地图名
		@type 	spaceName	:	STRING
		@param 	position	:	二维坐标位置
		@type 	position	:	Tuple
		@param 	offset		:	允许的范围差距，必须为正值
		@type 	offset		:	Tuple
		"""
		if player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) != spaceName:
			return False
		negativeOffset = 0 - offset
		currPos = player.position
		x = float(currPos[0]) - float(position[0])
		z = float(currPos[2]) - float(position[1])
		return ( x >= negativeOffset and x <= offset and z >= negativeOffset and z <= offset )