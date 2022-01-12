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
	entity互动信息表
	"""
	def __init__( self ):
		"""
		初始化属性
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
			添加一个敌人到战斗列表
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
		将这个敌人从所有列表中删除 （取消该敌人）
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
		添加伤害列表
		@param entityID  : entityID
		@param damage	 : 伤害值
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
		添加治疗列表
		@param entityID  : entityID
		@param cure		 : 治疗值
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
		添加好友列表
		@param entityID  : entityID
		"""
		if not entityID in self.friendList:
			self.friendList.append( entityID )
			self.onFriendListChange( entityID )

	def onEnemyListChange( self, entityID ):
		"""
		战斗信息表有改动通知
		"""
		pass

	def onDamageListChange( self, entityID ):
		"""
		伤害信息表有改动通知
		"""
		pass

	def onCureListChange( self, entityID ):
		"""
		治疗信息表有改动通知
		"""
		pass

	def onFriendListChange( self, entityID ):
		"""
		友方信息表有改动通知
		"""
		pass

	def hasEnemy( self, entityID ):
		"""
		是否是自身敌人列表的敌人
		"""
		return self.enemyList.has_key( entityID )

	def hasFriend( self, entityID ):
		"""
		是否是自身敌人列表的敌人
		"""
		return entityID in self.friendList

	def findFirstEnemyByTime( self ):
		"""
		根据先后进入敌人列表的时间寻找第一个敌人(既当前此表中时间最早的)
		"""
		return self.getEnemyByIndex( 1 )
	
	def getEnemyByIndex( self, index ):
		"""
		根据进入次序获得敌人
		"""
		enemyList = sorted(self.enemyList.iteritems(), key = lambda asd:asd[1] )
		eid = 0
		if index and  len( enemyList ) >= index:
			eid = enemyList[ index - 1 ][ 0 ]
		
		return eid

	def findLastEnemyByTime( self ):
		"""
		根据先后进入敌人列表的时间寻找最后一个攻击我的敌人(既当前此表中时间最迟的)
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
		寻找对我造成伤害最大的敌人
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
		寻找治疗量最大的敌人
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
		将这个敌人从伤害列表中删除
		"""
		if self.damageList.has_key( entityID ):
			self.damageList.pop( entityID )
			self.onDamageListChange( entityID )

	def removeEnemyCureList( self, entityID ):
		"""
		将这个敌人从治疗列表中删除
		"""
		if self.cureList.has_key( entityID ):
			self.cureList.pop( entityID )
			self.onCureListChange( entityID )

	def removeAIFriend( self, entityID ):
		"""
		删除一个友方单位
		"""
		if self.hasFriend( entityID ):
			self.friendList.pop( entityID )
			self.onFriendListChange( entityID )

	def resetEnemyList( self ):
		"""
		重置所有敌人信息表
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
		重置伤害列表
		"""
		self.damageList.clear()
		self.onDamageListChange( -1 )

	def resetCureList( self ):
		"""
		重置治疗列表
		"""
		self.cureList.clear()
		self.onCureListChange( -1 )

	def resetFriendList( self ):
		"""
		重置好友信息表
		"""
		self.friendList = []
		self.onFriendListChange( -1 )
#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/04/21 07:02:42  kebiao
# 修改死亡自动复活BUG
#
# Revision 1.6  2008/04/21 00:59:56  kebiao
# 修改事件通知接口 onDamageListChange等
#
# Revision 1.5  2008/04/18 08:36:40  kebiao
# 添加重置 伤害列表 治疗 友方列表
#
# Revision 1.4  2008/04/18 07:56:29  kebiao
# 添加战斗信息表改动通知
#
# Revision 1.3  2008/04/18 07:16:13  kebiao
# ADD : resetCureList
#
# Revision 1.2  2008/04/17 07:28:58  kebiao
# 调整战斗列表相关BUG 如 宠物攻击 角色不进入战斗状态，修正
# BUFF增益技能和治疗列表的关系
#
# Revision 1.1  2008/04/16 02:17:05  kebiao
# FightTable改名 EntityRelationTable
#
#
#