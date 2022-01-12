# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
import csstatus
import event.EventCenter as ECenter

class RoleYiJieZhanChangInterface:
	"""
	异界战场
	"""
	def __init__( self ):
		self.yiJieReviveTime = 0
		self.yiJieKiller = ""
	
	def yiJieOnTeleportReady( self ):
		"""
		define method
		传送完成，地图加载完毕通知客户端
		"""
		ECenter.fireEvent( "EVT_ON_ANGER_POINT_WINDOW_SHOW" )
		ECenter.fireEvent( "EVT_ON_YI_JIE_BATTLE_INFOS_SHOW" )
	
	def yiJieOnExit( self ):
		"""
		<define method>
		退出战场
		"""
		ECenter.fireEvent( "EVT_ON_ANGER_POINT_WINDOW_HIDE" )
		ECenter.fireEvent( "EVT_ON_YI_JIE_BATTLE_INFOS_HIDE" )
	
	def yiJieSetReviveInfo( self, reviveTime, killerName ) :
		"""
		<define method>
		设置副本复活时间
		"""
		self.yiJieReviveTime = reviveTime
		self.yiJieKiller = killerName
	
	def yiJieShowSignUp( self ):
		"""
		define method
		打开报名界面
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JIJIE_SIGNUP_WINDOW" )
	
	def yiJieCancelSignUp( self ):
		"""
		define method
		关闭报名界面
		"""
		ECenter.fireEvent( "EVT_ON_CANCEL_JIJIE_SIGNUP_WINDOW" )
	
	def onAngerPointChanged( self, angerPoint ):
		"""
		define method
		怒气值改变回调
		@type			angerPoint : 怒气值
		@param			angerPoint : INT8
		"""
		ECenter.fireEvent( "EVT_ON_ANGER_POINT_CHANGED", angerPoint )
	
	def requestEnterYiJie( self ):
		"""
		请求进入异界战场
		"""
		self.cell.yiJieRequestEnter()
		
	def yiJieReceiveDatas( self, roleInfos ):
		"""
		define method
		接收玩家排名信息（玩家自身的排名也包含在roleInfos中）
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_YIJIE_SCORES_DATAS", roleInfos )
		
	def yiJieOnKillDataChanged( self, killNum, keepNum, maxKeepNum ) :
		"""
		< define method >
		杀人数、连斩数、最大连斩数等数据改变回调
		@type			killNum 	: 杀人数
		@param			killNum 	: INT32
		@type			keepNum 	: 连斩数
		@param			keepNum		: INT32
		@type			maxKeepNum 	: 最高连斩数
		@param			maxKeepNum 	: INT32
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_YIJIE_PLAYER_INFOS", killNum, keepNum, maxKeepNum )
	
	def canPk( self, entity ) :
		"""
		能否与 entity 进行 pk
		"""
		if self.yiJieFaction == entity.yiJieFaction or self.yiJieAlliance == entity.yiJieFaction :
			return False
		else :
			return True