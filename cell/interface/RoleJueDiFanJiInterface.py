# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Const
import ECBExtend
import csdefine
import csstatus
import VehicleHelper

import csconst

# 临时退出副本的位置
TEMP_FORET_POSITION = ( 98.295, 12.108, 135.196 )
TEMP_FORET_DIRECTION = ( 0, 0, 0.1964 )
TEMP_FORET_SPACE = "fengming"



class RoleJueDiFanJiInterface:
	"""
	绝地反击接口
	"""
	def __init__( self ):
		pass

	def initJueDiFanJiButtonState( self, srcEntityID ):
		"""
		Exposed method
		登录时初始化绝地反击活动按钮状态
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ):
			state = self.queryTemp( "jueDiFanJi_state", 0 )
			repeatedVictoryCount = self.queryTemp( "jueDiFanJi_repeatedVictoryCount", 0 )
			if state == csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP:
				self.client.jueDiVictoryCountChange( repeatedVictoryCount )
			self.client.showJueDiFanJiPanel( state )
		else:
			self.client.showJueDiFanJiPanel( csdefine.JUE_DI_FAN_JI_SHOW_RANK_LIST )
			if self.queryTemp( "jueDiFanJi_state", 0 ):
				self.removeTemp( "jueDiFanJi_state" )
				self.removeTemp( "jueDiFanJi_repeatedVictoryCount" )

	def jueDiFanJiSignUp( self, srcEntityID ):
		"""
		绝地反击报名
		"""
		if self.id != srcEntityID:
			return
		if self.level < csconst.JUE_DI_FAN_JI_LEVEL_LIMIT:
			return
		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiSignUp( self.base, self.databaseID, self.getName(), self.getLevel(), self.getClass() )

	def jueDiFanJiEnterConfirm( self, srcEntityID ):
		"""
		绝地反击进入确认
		"""
		if self.id != srcEntityID:
			return
		if not self.transConditionCheck():
			return

		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiEnterConfirm( self.base, self.databaseID )
		
	def noticeAddTimer( self, time ):
		self.jueDiFanJiTimer = self.addTimer( time, 0, ECBExtend.JUE_DI_FAN_JI_CONFIRM )
		
	def onTimer_jueDiFanJiConfirm( self, timerID, cbID ):
		"""
		绝地反击确认时间到达timer
		"""
		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiReachTimeConfirm( self.databaseID )

	def jueDiFanJiCancelEnter( self, srcEntityID ):
		"""
		绝地反击玩家主动取消进入
		"""
		if self.id != srcEntityID:
			return
		self.jueDiFanJiCanCelTimer()
		BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiCancelEnter( self.base, self.databaseID )

	def selectRepeatedVictory( self, srcEntityID ):
		"""
		玩家选择连胜
		"""
		if self.id != srcEntityID:
			return
		self.gotoForetime()
		self.setTemp( "selectRepeatedVictory", 1)
		BigWorld.globalData[ "JueDiFanJiMgr" ].onSelectRepeatedVictory( self.base, self.databaseID, self.HP, self.getName(), self.getLevel(), self.getClass() )

	def selectLeave( self, srcEntityID ):
		"""
		玩家选择离开
		"""
		if self.id != srcEntityID:
			return
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #刷新速度
		self.gotoForetime()
		#self.gotoSpace( TEMP_FORET_SPACE, TEMP_FORET_POSITION, TEMP_FORET_DIRECTION )
		BigWorld.globalData[ "JueDiFanJiMgr" ].clearVictoryCountDict( self.databaseID )

	def onRoleReviveCallBack( self, spaceName, position, direction ):
		"""
		玩家在副本中死亡后复活
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #刷新速度
		self.teleport( None, position, direction )


	def onJueDiFanJiLogin( self, srcEntityID ):
		"""
		Exposed method
		玩家重新登陆
		"""
		if self.id != srcEntityID: return
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) or self.query( "jueDiFanJi_scoreList", None ) != None:
			self.client.onShowJueDiFanJiBox()

	def onReceiveStateInfo( self, state, repeatedVictoryCount ):
		"""
		接收状态信息
		"""
		if state == csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP:
			self.client.onJueDiSignUp()
		elif state == csdefine.JUE_DI_FAN_JI_HAS_MATCHED:
			self.client.onJueDiMatchSuccess()
		elif state == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
			self.client.onJueDiConfirm()
		self.setTemp( "jueDiFanJi_state", state )
		self.setTemp( "jueDiFanJi_repeatedVictoryCount", repeatedVictoryCount )

	def jueDiFanJiCanCelTimer( self ):
		"""
		取消绝地反击活动Timer
		"""
		self.cancel( self.jueDiFanJiTimer )

	def receiveBulletin( self, scoreList ):
		"""
		接收绝地反击活动前20名的榜单
		"""
		self.set( "jueDiFanJi_scoreList", scoreList )
		self.client.receiveBulletin( scoreList )

	def showJueDiFanJiRankList( self, srcEntityID ):
		"""
		Exposed method
		显示榜单
		"""
		if self.id != srcEntityID: return
		if self.query( "jueDiFanJi_scoreList", None ) != None:
			scoreList = self.query( "jueDiFanJi_scoreList", None )
			self.client.receiveBulletin( scoreList )
		else:
			self.statusMessage( csstatus.JUE_DI_SHOW_RANK_LIST_NOT_JOIN )

	def removeBulletin( self ):
		"""
		移除榜单相关数据
		"""
		self.remove( "jueDiFanJi_scoreList" )
		