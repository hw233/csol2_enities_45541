# -*- coding: gb18030 -*-
# TreasureMonster.py

#################################################################################
# TreasureMonster,������һ��Ĺ��������ڱ�ʱ�����ģ�һ����������Ȩȷ�����ǿ��Ը��ĵĹ���
# �˹���һ����Ҳ����ˣ���������ʧ��AI����ʵ�֣�
# ��д�������ӿ�
#################################################################################

from Monster import Monster
from bwdebug import *
from interface.CombatUnit import CombatUnit
import BigWorld
import csconst
import csstatus
import csdefine
import ECBExtend
import random
import items
import sys

g_items = items.instance()

class TreasureMonster( Monster ):
	"""
	���ع�����
	"""
	def __init__(self):
		Monster.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		Monster.initEntity( self, selfEntity )
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_TREASURE_MONSTER )

	def getOwner( self, selfEntity ):
		"""
		��������ߵ�baseMailBox
		"""
		return selfEntity.queryTemp( "ownerBaseMailBox", None )
		
	def getOwnerID( self, selfEntity ):
		"""
		"""
		return selfEntity.queryTemp( "ownerID", 0 )

	def setOwner( self, selfEntity, owner ):
		"""
		�����Լ���������(ͬʱ��������Ȩ)
		"""
		selfEntity.setTemp( "ownerID", owner.id )
		selfEntity.setTemp( "ownerName", owner.getName() )
		if owner.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			selfEntity.bootyOwner = ( owner.id, 0 )

	def dropTreasure( self, selfEntity, bootyOwner ):
		"""
		���䱦��
		"""
		dropItem = selfEntity.queryTemp( "dropItem", 0 )
		if dropItem == 0:
			return
		x1 = random.randint(-2,2)
		z1 = random.randint(-2,2)
		pos = selfEntity.position							# �����λ�ã���ҵ�λ�ã�
		x, y, z = x1 + pos[0], pos[1], z1 + pos[2]	# ����ƫ�������������λ��
		direction = (0.0, 0.0, 0.0)					# ����
		item = g_items.createDynamicItem( dropItem , 1 )
		item.set( 'treasure_space', selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		item.set( "level", selfEntity.level )
		itemsData = [item]
		collide = BigWorld.collide( selfEntity.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
		if collide != None:
			# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
			y = collide[0].y
		itemBox = BigWorld.createEntity( "DroppedBox", selfEntity.spaceID, (x, y, z), direction, {} )
		itemBox.init( bootyOwner, itemsData )


	def onMonsterDie( self, selfEntity, killerID ):
		"""
		"""
		Monster.onMonsterDie( self, selfEntity, killerID )
		bootyOwner = selfEntity.getBootyOwner()
		self.dropTreasure( selfEntity, bootyOwner )	# ���䱦��

		# ����ڱ��˴��ڵ��ǲ����ڱ��˴����Ĺ�,�ڱ���ҲҪ��þ��齱��
		ownerID = self.getOwnerID( selfEntity )
		if BigWorld.entities.has_key( ownerID ) and killerID != ownerID:
		 	treasureScooper = BigWorld.entities[ ownerID ]
		 	if not treasureScooper.state == csdefine.ENTITY_STATE_DEAD:
		 		# �ڱ������û��������ʹ���Ǳ��ڱ�����ɱ��ҲҪ���ڱ�����Ҳ�������
				if selfEntity.bootyOwner[0] != 0 and selfEntity.bootyOwner[0] != ownerID and selfEntity.bootyOwner[1] == 0:
					# �����������Ȩ�����ڱ��˶���������
					selfEntity.gainSingleReward( treasureScooper )
					treasureScooper.statusMessage( csstatus.TREATURE_MONSTER_KILLED_BY_OTHERS, selfEntity.exp )
				elif selfEntity.bootyOwner[1] != 0 and not ownerID in selfEntity.searchTeamMember( selfEntity.bootyOwner[1], 50 ):
					# �����������Ȩ�Ƕ��飬���Ƕ�����û���ڱ���
					selfEntity.gainSingleReward( treasureScooper )
					treasureScooper.statusMessage( csstatus.TREATURE_MONSTER_KILLED_BY_OTHERS, selfEntity.exp )

	def setBirthTime( self, selfEntity ):
		"""
		������������ʱ��
		"""
		birthTime = BigWorld.time()
		selfEntity.setTemp( "entity_birth_time", int( birthTime ) )
		
	def getRelationEntity( self ):
		"""
		��ȡ��ϵ�ж�����ʵentity
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		else:
			return owner
		
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner.queryCombatRelation( entity )
		else:
			return csdefine.RELATION_FRIEND