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
	ʦͽ����boss
	"""
	def dropItemBox( self, selfEntity, bootyOwner ):
		"""
		��������
		"""
		pos = selfEntity.position
		spaceID = selfEntity.spaceID
		direction = selfEntity.direction
		
		x1 = random.random() * 4 - 2
		z1 = random.random() * 4 - 2
		x, y, z = x1 + pos[0], pos[1], z1 + pos[2]
		collide = BigWorld.collide( selfEntity.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
		if collide != None:
			# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
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
		# ��������Ǳ�ܵ���Ǳ�ܵ������ӵ���߼���һ�£�Ҫ��ÿ�����ֻ�ܿ�������ö�Ӧ���Լ������Ǳ�ܵ�
		for owner in players:
			itemInstance = g_items.createDynamicItem( Const.TEACH_KILL_MONSTER_DROP_ITEM )
			itemInstance.setLevel( owner.level )
			itemBox.insertItem( itemInstance, owner.id )
			
	def getExpAmendRate( self, levelFall ):
		"""
		���ݵȼ����þ�������ֵ
		
		@param levelFall : ��Һ͹���ĵȼ���
		"""
		return TeachSpaceAmendExp.instance().getLevelRate( levelFall )
		