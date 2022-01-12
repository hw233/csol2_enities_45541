# -*- coding: gb18030 -*-
from bwdebug import *
import BigWorld
import random

import csdefine
import csconst
import csstatus
import utils

from SpaceCopy import SpaceCopy

ONE_BOX_INTEGRAL = 1 # 一个箱子的积分

class SpaceCopyYeZhanFengQi( SpaceCopy ):
	# 夜战凤栖镇
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.warIsAction = False

	def onEnterCommon( self, baseMailbox, params ):
		"""
		进入夜战凤栖副本
		"""
		baseMailbox.cell.enterCopyYeZhanFengQiBodyChanging()
		SpaceCopy.onEnterCommon( self, baseMailbox, params )

	def closeActivity( self, reason ):
		"""
		define method
		关闭活动
		"""
		if reason == csdefine.FENG_QI_CLOSE_REASON_MIN_PLAYER:
			for e in self._players:
				e.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_ENTER_LESS, "" )
		elif reason == csdefine.FENG_QI_CLOSE_REASON_TIME_OUT:
			for e in self._players:
				e.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_TIME_OUT, "" )
				
		self.getScript().closeActivity( self )

	def onAINotifySpaceDied( self, className, entity ):
		"""
		define method.
		AI通知NPC死亡
		"""
		SpaceCopy.onAINotifySpaceDied( self, className, entity )
		if len( self.aiRecordMonster ) == 0:
			self.getScript().bossAllDie( self )
	
	def addPlayerIntegral( self, playerID, integral ):
		"""
		define method
		添加指定玩家积分
		"""
		self.battlefieldIntegral.addIntegral( playerID, integral )
	
	def onRoleBeKill( self, pos, diePlayer, killerBase, killerType ):
		"""
		define method
		有玩家被击杀
		"""
		integral = self.battlefieldIntegral.getIntegral( diePlayer.id )
		self.battlefieldIntegral.decIntegral( diePlayer.id, max( integral - integral / 2, 1 )  )
		direction = ( 0.0, 0.0, 0.0 )
		# 积分少于0的踢出战场
		if not self.battlefieldIntegral.getIntegral( diePlayer.id ) > 0:
			diePlayer.cell.gotoForetime()
			
		if killerType == csdefine.ENTITY_TYPE_ROLE:
			self.battlefieldIntegral.kill( killerBase.id, diePlayer.id )
			self.recoverEntity( killerBase ).fengQiAddPlayerIntegral( max( integral / 2, 1)  )
			self.createObjectNear( self.getScript().integralClassName, utils.navpolyToGround( self.spaceID, pos, 0.2, 20.0 ), direction, {} )
		else:
			for i in xrange( integral / 2 ):
				newPos = ( pos[0] + random.randint( -2, 2 ), pos[1], pos[2] + random.randint( -2, 2 ) )
				self.createObjectNear( self.getScript().integralClassName, utils.navpolyToGround( self.spaceID, newPos, 0.2, 20.0 ), direction, {} )
	
	def onRolePickBox( self, pMB ):
		"""
		define method
		玩家拾取了一个箱子
		"""
		pMB.cell.fengQiAddPlayerIntegral( ONE_BOX_INTEGRAL )
		self.battlefieldIntegral.addBox( pMB.id )
	
	def playerExit( self, pMB ):
		"""
		define method
		玩家退出
		"""
		self.battlefieldIntegral.remove( pMB )
		BigWorld.globalData[ "YeZhanFengQiMgr" ].playerExit( self.spaceNumber, pMB )
	
	def recoverEntity( self, mb ):
		if BigWorld.entities.get( mb.id ):
			return BigWorld.entities[ mb.id ]
		else:
			return mb.cell
		