# -*- coding:gb18030 -*-

from Monster import Monster
from bwdebug import *
import Const
import items
import random
import BigWorld
import csdefine
from LevelEXP import TeachSpaceAmendExp

g_items = items.instance()

class TeachBossMonster( Monster ):
	"""
	师徒副本boss
	"""
	def dropItemBox( self, selfEntity, bootyOwner ):
		"""
		掉落箱子
		"""
		pos = selfEntity.position
		spaceID = selfEntity.spaceID
		direction = selfEntity.direction
		
		x1 = random.random() * 4 - 2
		z1 = random.random() * 4 - 2
		x, y, z = x1 + pos[0], pos[1], z1 + pos[2]
		collide = BigWorld.collide( selfEntity.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
		if collide != None:
			# 掉落物品的时候对地面进行碰撞检测避免物品陷入地下
			y = collide[0].y
			
		tempList = []
		itemsList = self.getDropItems( selfEntity )
		
		params = { "dropType" : csdefine.DROPPEDBOX_TYPE_MONSTER, "droperName" : selfEntity.getName() }
		itemBox = BigWorld.createEntity( "DroppedBox", spaceID, (x, y, z), direction, params )
		itemBox.init( bootyOwner, itemsList )
		
		players = []
		if bootyOwner[1] != 0:
			players = [ e for e in selfEntity.entitiesInRangeExt( 30.0, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == bootyOwner[1] ]
			if len(players) == 0:
				return
			players[0].addTeamMembersTasksItem(  itemBox.id, self.className )
		else:
			entity = BigWorld.entities.get( bootyOwner[0], None )
			if entity:
				player = None
				if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					player = entity
				elif entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
					owner = BigWorld.entities.get( entity.ownerID, None )
					if owner:
						player = owner
				if player:
					player.addTasksItem(  itemBox.id, self.className )
					players.append( player )
		# 特殊掉落大潜能丹，潜能丹级别和拥有者级别一致，要求每个玩家只能看到并获得对应于自己级别的潜能丹
		for owner in players:
			itemInstance = g_items.createDynamicItem( Const.TEACH_KILL_MONSTER_DROP_ITEM )
			itemInstance.setLevel( owner.level )
			itemBox.insertItem( itemInstance, owner.id )
			
	def getExpAmendRate( self, levelFall ):
		"""
		根据等级差获得经验修正值
		
		@param levelFall : 玩家和怪物的等级差
		"""
		return TeachSpaceAmendExp.instance().getLevelRate( levelFall )
		