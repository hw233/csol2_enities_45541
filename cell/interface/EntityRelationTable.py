# -*- coding: gb18030 -*-

# $Id: EntityRelationTable.py,v 1.8 2008-05-17 01:47:37 kebiao Exp $

import csstatus
import csdefine
import BigWorld
import ECBExtend
import random
import time
from bwdebug import *
from Domain_Fight import g_fightMgr


class EntityRelationTable:
	"""
	entity������Ϣ��
	"""
	def __init__( self ):
		"""
		��ʼ������
		"""
		pass

	def addEnemyCheck( self, entityID ):
		"""
		extend method.
		"""
		if self.enemyList.has_key( entityID ):
			return False
		
		if self.id == entityID:
			return False
		
		entity = BigWorld.entities.get( entityID )
		if entity is None:
			return False

		if entity.spaceID != self.spaceID:
			return False
		
		if entity.planesID != self.planesID:
			return False

		return True


	def addEnemy( self, entityID ):
		"""
		define method.
		procedure method.
		@description
			���һ�����˵�ս���б�
		"""
		if not self.addEnemyCheck( entityID ):
			return
			
		self.enemyList[ entityID ] = BigWorld.time()
		self.enemyList = self.enemyList
		self.onAddEnemy( entityID )

	def onAddEnemy( self, entityID ):
		"""
		extend method.
		"""
		self.onEnemyListChange( entityID )


	def removeEnemy( self, entityID ):
		"""
		define method
		��������˴������б���ɾ�� ��ȡ���õ��ˣ�
		"""
		if not self.enemyList.has_key( entityID ):
			return
		self.enemyList.pop( entityID )
		self.removeEnemyDmgList( entityID )
		self.removeEnemyCureList( entityID )
		
		self.onRemoveEnemy( entityID )


	def onRemoveEnemy( self, entityID ):
		"""
		"""
		self.onEnemyListChange( entityID )



	def addDamageList( self, entityID, damage ):
		"""
		define method
		����˺��б�
		@param entityID  : entityID
		@param damage	 : �˺�ֵ
		"""
		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			return
		entity = BigWorld.entities.get(entityID)
		if entity:
			g_fightMgr.buildEnemyRelation( self, entity )
			
		if self.damageList.has_key( entityID ):
			self.damageList[ entityID ] += damage
		else:
			self.damageList[ entityID ] = damage
		self.onDamageListChange( entityID )  

	def addCureList( self, entityID, cure ):
		"""
		define method
		��������б�
		@param entityID  : entityID
		@param cure		 : ����ֵ
		"""
		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			return
		entity = BigWorld.entities.get(entityID)
		if entity:
			g_fightMgr.buildEnemyRelation( self, entity )
			
		if self.cureList.has_key( entityID ):
			self.cureList[ entityID ] += cure
		else:
			self.cureList[ entityID ] = cure
		self.onCureListChange( entityID )

	def addFriendList( self, entityID ):
		"""
		define method
		��Ӻ����б�
		@param entityID  : entityID
		"""
		if not entityID in self.friendList:
			self.friendList.append( entityID )
			self.onFriendListChange( entityID )

	def onEnemyListChange( self, entityID ):
		"""
		ս����Ϣ���иĶ�֪ͨ
		"""
		pass

	def onDamageListChange( self, entityID ):
		"""
		�˺���Ϣ���иĶ�֪ͨ
		"""
		pass

	def onCureListChange( self, entityID ):
		"""
		������Ϣ���иĶ�֪ͨ
		"""
		pass

	def onFriendListChange( self, entityID ):
		"""
		�ѷ���Ϣ���иĶ�֪ͨ
		"""
		pass

	def hasEnemy( self, entityID ):
		"""
		�Ƿ�����������б�ĵ���
		"""
		return self.enemyList.has_key( entityID )

	def hasFriend( self, entityID ):
		"""
		�Ƿ�����������б�ĵ���
		"""
		return entityID in self.friendList

	def findFirstEnemyByTime( self ):
		"""
		�����Ⱥ��������б��ʱ��Ѱ�ҵ�һ������(�ȵ�ǰ�˱���ʱ�������)
		"""
		return self.getEnemyByIndex( 1 )
	
	def getEnemyByIndex( self, index ):
		"""
		���ݽ�������õ���
		"""
		enemyList = sorted(self.enemyList.iteritems(), key = lambda asd:asd[1] )
		eid = 0
		if index and  len( enemyList ) >= index:
			eid = enemyList[ index - 1 ][ 0 ]
		
		return eid

	def findLastEnemyByTime( self ):
		"""
		�����Ⱥ��������б��ʱ��Ѱ�����һ�������ҵĵ���(�ȵ�ǰ�˱���ʱ����ٵ�)
		"""
		t = 0
		eid = 0
		for entityID, time in self.enemyList.iteritems():
			if t < time:
				eid = entityID
				t = time
		return eid

	def findEnemyByMaxDamage( self ):
		"""
		Ѱ�Ҷ�������˺����ĵ���
		"""
		d = 0
		eid = 0
		for entityID, damage in self.damageList.iteritems():
			if d < damage:
				eid = entityID
				d = damage
		return eid

	def findEnemyByMaxCure( self ):
		"""
		Ѱ�����������ĵ���
		"""
		d = 0
		eid = 0
		for entityID, cure in self.cureList.iteritems():
			if d < cure:
				eid = entityID
				d = cure
		return eid


	def removeEnemyDmgList( self, entityID ):
		"""
		��������˴��˺��б���ɾ��
		"""
		if self.damageList.has_key( entityID ):
			self.damageList.pop( entityID )
			self.onDamageListChange( entityID )

	def removeEnemyCureList( self, entityID ):
		"""
		��������˴������б���ɾ��
		"""
		if self.cureList.has_key( entityID ):
			self.cureList.pop( entityID )
			self.onCureListChange( entityID )

	def removeAIFriend( self, entityID ):
		"""
		ɾ��һ���ѷ���λ
		"""
		if self.hasFriend( entityID ):
			self.friendList.pop( entityID )
			self.onFriendListChange( entityID )

	def resetEnemyList( self ):
		"""
		�������е�����Ϣ��
		"""
		bwe = BigWorld.entities
		
		g_fightMgr.breakGroupEnemyRelationByIDs( self, self.enemyList.keys() )
		
		if len( self.enemyList ) > 0:
			self.enemyList.clear()
			self.onEnemyListChange( -1 )
		if len( self.damageList ) > 0:
			self.damageList.clear()
			self.onDamageListChange( -1 )
		if len( self.cureList ) > 0:
			self.cureList.clear()
			self.onCureListChange( -1 )


	def resetDamageList( self ):
		"""
		�����˺��б�
		"""
		self.damageList.clear()
		self.onDamageListChange( -1 )

	def resetCureList( self ):
		"""
		���������б�
		"""
		self.cureList.clear()
		self.onCureListChange( -1 )

	def resetFriendList( self ):
		"""
		���ú�����Ϣ��
		"""
		self.friendList = []
		self.onFriendListChange( -1 )
#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/04/21 07:02:42  kebiao
# �޸������Զ�����BUG
#
# Revision 1.6  2008/04/21 00:59:56  kebiao
# �޸��¼�֪ͨ�ӿ� onDamageListChange��
#
# Revision 1.5  2008/04/18 08:36:40  kebiao
# ������� �˺��б� ���� �ѷ��б�
#
# Revision 1.4  2008/04/18 07:56:29  kebiao
# ���ս����Ϣ��Ķ�֪ͨ
#
# Revision 1.3  2008/04/18 07:16:13  kebiao
# ADD : resetCureList
#
# Revision 1.2  2008/04/17 07:28:58  kebiao
# ����ս���б����BUG �� ���﹥�� ��ɫ������ս��״̬������
# BUFF���漼�ܺ������б�Ĺ�ϵ
#
# Revision 1.1  2008/04/16 02:17:05  kebiao
# FightTable���� EntityRelationTable
#
#
#