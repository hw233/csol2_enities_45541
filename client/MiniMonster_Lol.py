# -*- coding: gb18030 -*-

from Monster import Monster
from YXLMBoss import YXLMBoss
import csdefine
from bwdebug import *
from Attack import Attack

class MiniMonster_Lol( Monster, Attack ):
	def __init__( self ):
		Monster.__init__( self )
		Attack.__init__( self )
		
	def queryRelation( self, entity ):
		"""
		��ϵ�жϣ����ǵ�������ֻ���ض��������֣�Ŀǰֻ�ж���������
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if not self.inWorld or not entity.inWorld: 
			return csdefine.RELATION_NEUTRALLY
		
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ): # �ж��Ƿ�Ϊ���
			owner = entity.getOwner()
			if owner is None:
				return csdefine.RELATION_NOFIGHT
			else:
				entity = owner
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			# GM�۲���ģʽ
			if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
				return csdefine.RELATION_NOFIGHT
			
			if entity.teamID == self.belong:
				return csdefine.RELATION_FRIEND
			return csdefine.RELATION_ANTAGONIZE
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ):
			if entity.belong == self.belong:
				return csdefine.RELATION_FRIEND
			
			return csdefine.RELATION_ANTAGONIZE
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY

		return csdefine.RELATION_NEUTRALLY		
	
	def requestNearByEnemy( self, range ):
		"""
		define method
		����õ��������Ϊ��ң�������PlayerRole������������������ݣ�
		��Ҫ�ǽ����ϵ�ж���teamID�����⣬��ΪPlayerRole��ȡ���������ҵ�teamID��Ϣ��Ĭ�ϵõ�������Ϊ0
		"""
		if not self.inWorld:
			INFO_MSG( "I'm not in world now")
			return
		bossID, bossDis, nearID, nearDis, eid, edis = 0, 100.0, 0, 100.0, 0 , 100.0
		entities = self.entitiesInRange( range )
		entities.sort( key = lambda e : e.position.distTo( self.position ) )
		for e in entities:
			if self.queryRelation( e ) ==  csdefine.RELATION_ANTAGONIZE and e.state != csdefine.ENTITY_STATE_DEAD:
				if e.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or isinstance( e, YXLMBoss ):
					if not bossID: 					# ������������һ���Boss������ѡ��
						bossID = e.id
						bossDis = e.position.distTo( self.position )
						continue
				
				if not nearID:						# ��ѡȡ�����Ŀ��
					nearID = e.id
					nearDis = e.position.distTo( self.position )
					if e.getDamageLength( ) >= 2:		# ��������Ŀ��Ĺ�����̫�࣬����ѡ����һ��Ŀ��
						continue
					break
				
				edis = e.position.distTo( self.position )
				if edis - nearDis < 3.0:			# ��һ��Ŀ�����̫Զ����������
					break
				if e.getDamageLength() < 2: 			# ���Ŀ��������Ŀ��С��3.0�����˺��б�С��2��ֹͣ����
					eid = e.id
					break
		
		# ֻ��Boss����ҡ�Boss����С��6��
		if  ( bossID and not nearID and not eid ) \
			or ( bossID and nearID and not eid and bossDis < 6.0 < nearDis and nearDis - bossDis > 3.0 ) \
			or ( bossID and eid and bossDis < 6.0 < edis and edis -  bossDis > 3.0 ):
			eid = bossID
		
		# ֻ�������Ŀ��
		if ( not bossID and not eid and nearID ) \
			or ( bossID and nearID and not eid and nearDis - bossDis < 3.0 ):
			eid = nearID
		
		if not eid:
			return
		
		target = BigWorld.entities.get( eid )
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and target.__class__.__name__ != "PlayerRole": # ����ѵ�����������ң���֪ͨ������
			return
		
		self.cell.receiveNearByEnemy( eid )
