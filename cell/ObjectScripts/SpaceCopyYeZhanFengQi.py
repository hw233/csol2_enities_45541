# -*- coding: gb18030 -*-
import time
import random
import BigWorld

from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory

import csdefine
import csconst
import csstatus
import Const

INIT_INTEGRAL = 5	  #初始积分

TIMER_START_ACT		 = 1	# 开始战斗
TIMER_CLOSE_ACT 	 = 2 	# 关闭活动
TIMER_BOSS_REVIVE 	 = 3	# BOSS复活
TIMER_CLOSE_CD		 = 4	# 通知客户端的倒计时

class SpaceCopyYeZhanFengQi( SpaceCopy ):
	# 夜战凤栖镇
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.minLevel = 0
		self.maxLevel = 0
		self.isSpaceDesideDrop = True
		self.enterInfos = []
		self.gainSkillID = 0
		self.integralClassName = ""
		self.closeTime = 5
		self.reviveTime = 0
		self.prepareTime = 0
		self.spaceLife = 0
		self.bossRevive = 0
	
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )
		self.minLevel = section[ "Space" ][ "minLevel" ].asInt
		self.maxLevel = section[ "Space" ][ "maxLevel" ].asInt
		
		for idx, item in enumerate( section[ "Space" ][ "enterInfos" ].values() ):
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self.enterInfos.append( ( pos, direction ) )
		
		roleDieCreate = []
		for item in section[ "Space" ][ "roleDieCreate" ].values():
			roleDieCreate.append( item.asString )
		
		gainSkill, self.integralClassName = roleDieCreate
		self.gainSkillID = int( gainSkill )
		
		self.closeTime = section[ "Space" ][ "closeTime" ].asInt
		self.reviveTime = section[ "Space" ][ "reviveTime" ].asInt
		self.prepareTime = section[ "Space" ][ "prepareTime" ].asInt # 准备时间
		self.spaceLife = section[ "Space" ][ "spaceLife" ].asInt # 副本时间
		self.bossRevive = section[ "Space" ][ "bossRevive" ].asInt # Boss复活时间
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		SpaceCopy.initEntity( self, selfEntity )
		
		prepareTime = self.prepareTime * 60 - ( time.time() - selfEntity.actStartTime )
		selfEntity.addTimer( prepareTime, 0, TIMER_START_ACT )
		
		spaceTime = self.spaceLife * 60 - ( time.time() - selfEntity.actStartTime )
		selfEntity.addTimer( spaceTime - 60, 0, TIMER_CLOSE_CD )
		
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.actStartTime )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_PREPARE_TIME, self.prepareTime * 60 )
	
	def getRandomEnterPos( self ):
		"""
		随机取得一个进入的位置
		"""
		return random.choice( self.enterInfos )
	
	def packedDomainData( self, entity ):
		"""
		创建SpaceDomainShenGuiMiJing时，传递参数
		"""
		d = {}
		d[ "dbID" ] = entity.databaseID
		d[ "level" ] = entity.level
		return d
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		d = {}
		d[ "roleName" ] = entity.getName()
		d.update( SpaceCopy.packedSpaceDataOnEnter( self, entity ) )
		return d
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		进入
		"""
		selfEntity.battlefieldIntegral.add( baseMailbox, params[ "roleName" ] )
		baseMailbox.cell.fengQiOnEnter( selfEntity.warIsAction )
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		离开
		"""
		selfEntity.playerExit( baseMailbox )
		selfEntity.battlefieldIntegral.onAcitivyEnd( baseMailbox )
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		killerType = 0
		killerBase = None
		if killer:
			killerType = killer.getEntityType()
			killerBase  = killer.base
			
		role.getCurrentSpaceBase().cell.onRoleBeKill( tuple( role.position ), role.base, killerBase, killerType )
	
	def activityAction( self, selfEntity ):
		"""
		准备时间结束，开始战斗
		"""
		selfEntity.warIsAction = True
		for e in selfEntity._players:
			e.cell.fengQiAction()
		
		selfEntity.base.createSpawnEntities( { "level": selfEntity.spaceLevel } )
	
	def closeActivity( self, selfEntity ):
		for e in selfEntity._players:
			e.cell.fengQiCloseActivity()
			
		selfEntity.addTimer( self.closeTime, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( self.closeTime + 5, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
	def notifyCountDown( self, selfEntity ):
		# 结束倒计时
		for e in selfEntity._players:
			e.client.fengQiCountDown()
	
	def bossAllDie( self, selfEntity ):
		# 所有的BOSS全挂了
		selfEntity.addTimer( self.bossRevive, 0.0, TIMER_BOSS_REVIVE )
	
	def reviveBoss( self, selfEntity ):
		# 复活BOSS
		if len( selfEntity.aiRecordMonster ) == 0:
			selfEntity.base.createSpawnEntities( { "level": selfEntity.spaceLevel } )
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		时间控制器
		"""
		if userArg == TIMER_START_ACT:
			self.activityAction( selfEntity )
		
		if userArg == TIMER_CLOSE_CD:
			self.notifyCountDown( selfEntity )
		
		elif userArg == TIMER_CLOSE_ACT:
			self.closeActivity( selfEntity )
		
		elif userArg == TIMER_BOSS_REVIVE:
			self.reviveBoss( selfEntity )
			
		else:
			SpaceCopy.onTimer( self, selfEntity, id, userArg )