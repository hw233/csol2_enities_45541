# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine
from Monster import Monster
from interface.CombatUnit import CombatUnit

class TongNagual( Monster ):
	"""
	帮会守护神
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Monster.__init__( self )
		if self.level <= 0:
			self.setLevel( 1 )
		self.getCurrentSpaceBase().cell.onNagualCreated( self.level, self.queryTemp( "shenshouType", 0 ) )
		self.utype = csdefine.ENTITY_TYPE_TONG_NAGUAL

		fixModel = self.queryTemp( "fixModel", -1 )
		if fixModel != -1 and fixModel == False:
			self.removeFlag( csdefine.ENTITY_FLAG_SPEAKER )

		self.think( 0.1 )

	def disableNagual( self ):
		"""
		define method.
		神兽归位
		回归到固定供奉点，回归后不允许移动和战斗
		"""
		self.clearBuff( [csdefine.BUFF_INTERRUPT_NONE] )
		self.setTemp( "fixModel", True )
		self.resetEnemyList()
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.stopMoving()
		self.openVolatileInfo()				# 打开坐标信息传送功能
		self.teleport( None, self.fixPlace, self.fixDirection )	# 神兽归位
		self.full()
		self.addFlag( csdefine.ENTITY_FLAG_SPEAKER )
		self.enemyTongDBIDList = []
		
	def activeNagual( self, enemyTongDBID ):
		"""
		define method.
		激活神兽
		"""
		self.setTemp( "fixModel", False )
		self.changeSubState( csdefine.M_SUB_STATE_NONE )
		self.think( 1.0 )
		self.removeFlag( csdefine.ENTITY_FLAG_SPEAKER )
		
		# 当前可以攻击神兽的敌对帮会
		if enemyTongDBID > 0:
			self.enemyTongDBIDList.append( enemyTongDBID )
			self.enemyTongDBIDList = self.enemyTongDBIDList

	def canThink( self ):
		"""
		virtual method.
		判定是否可以think
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD or self.isDestroyed: 									# 死亡了停止think
			return False
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK: 					# 如果目前没有玩家看见我或正在回走，那么我将停止think
			return False
		return True

	def onThink( self ):
		"""
		virtual method.
		"""
		if self.queryTemp( "fixModel" ):
			self.think( 1.0 )
			return
		Monster.onThink( self )

	def updateLevel( self, level ):
		"""
		define method.
		更新神兽等级
		"""
		if self.level == level:
			return
		self.setLevel( level )
		self.getCurrentSpaceBase().cell.onNagualUpdateLevel( self.level, self.queryTemp( "shenshouType" ) )

	def beforeDie( self, killerID ):
		"""
		virtual method.
		"""
		k = "tong.%i" % self.ownTongDBID
		try:
			tongMailbox = BigWorld.globalData[ k ]
		except KeyError:
			ERROR_MSG( "tong %s not found." % k )
			return
			
		DEBUG_MSG( "通知base准备复活流程.." )
		tongMailbox.addNagualReviveTimer()		
		return Monster.beforeDie( self, killerID )
		
	def onDestroy( self ):
		"""
		entity 销毁的时候由BigWorld.Entity自动调用
		"""
		DEBUG_MSG( "%i神兽死亡了!" % self.id )
		spaceBase = self.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.onShenShouDestroy()
			spaceBase.cell.onShenShouDestroy()
		Monster.onDestroy( self )

	def isEnemyTong( self, entityID ):
		"""
		是否是敌对帮会的人
		"""
		p = BigWorld.entities[ entityID ]
		
		# 增加对目标为NPC的判断
		if p.isEntityType( csdefine.ENTITY_TYPE_NPC ):
			return False
		
		if p.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = p.getOwner()
			if owner.etype == "MAILBOX" :
				return False
				
			p = owner.entity


		if p.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if p.tong_dbID in self.enemyTongDBIDList:
				return True
		else:
			# 如果目标不是role， 那么判断是否是自己帮会的entity
			if hasattr( p, "ownTongDBID" ) :
				if self.ownTongDBID == p.ownTongDBID:
					return False
				else :
					return True
			else :
				return True

		return self.ownTongDBID != p.tong_dbID

	def addBuff( self, buff ):
		"""
		添加一个Buff。

		@param buff			:	instance of BUFF
		@type  buff			:	BUFF
		"""
		if self.queryTemp( "fixModel" ):
			return
		spell = buff["skill"]
		# 判断将领统帅是否和玩家帮会是一边的
		if buff[ "caster" ] > 0 and buff[ "caster" ] != self.id:
			if not self.isEnemyTong( buff[ "caster" ] ):
				return
		Monster.addBuff( self, buff )

	def receiveSpell( self, casterID, skillID, param1, param2, param3 ):
		"""
		Define method.
		接受技能处理

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		if self.queryTemp( "fixModel" ):
			return
			
		caster = BigWorld.entities.get( casterID )
		if not caster:
			return
			
		if casterID != self.id:
			if not self.isEnemyTong( casterID ):
				return
				
		Monster.receiveSpell( self, casterID, skillID, param1, param2, param3 )

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		"""
		if self.queryTemp( "fixModel" ):
			return
		if self.getState() == csdefine.ENTITY_STATE_FREE:
			if not self.isEnemyTong( casterID ):
				return
		Monster.receiveDamage( self, casterID, skillID, damageType, damage )

	def addEnemyCheck( self, entityID ):
		"""
		"""
		if not Monster.addEnemyCheck( self, entityID ):
			return False
		if self.queryTemp( "fixModel" ):
			return False
		if not self.isEnemyTong( entityID ):
			return False
		return True


	def addDamageList( self, entityID, damage ):
		"""
		添加伤害列表
		@param entityID  : entityID
		@param damage	 : 伤害值
		"""
		if self.queryTemp( "fixModel" ):
			return
		if not self.isEnemyTong( entityID ):
			return
		Monster.addDamageList( self, entityID, damage )

	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )

		if entity.id == self.id:
			return csdefine.RELATION_FRIEND
		if self.queryTemp( "fixModel" ):
			return csdefine.RELATION_FRIEND
		elif not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND
		elif entity.isState( csdefine.ENTITY_STATE_PENDING ):
			return csdefine.RELATION_NOFIGHT
		elif entity.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return csdefine.RELATION_NOFIGHT
		elif entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_ANTAGONIZE
		elif entity.__class__.__name__ == "TongCampaignMonster":
			return csdefine.RELATION_ANTAGONIZE
		elif self.isEnemyTong( entity.id ):
			return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_FRIEND


# TongNagual.py
