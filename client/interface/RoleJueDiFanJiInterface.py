# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
import csstatus
import event.EventCenter as ECenter

class RoleJueDiFanJiInterface:
	"""
	绝地反击接口
	"""
	def __init__( self ):
		pass

	def onCacheCompleted( self ):
		"""
		"""
		self.cell.onJueDiFanJiLogin()

	def jueDiFanJiSignUp( self ):
		"""
		绝地反击报名
		"""
		self.cell.jueDiFanJiSignUp()

	def jueDiFanJiEnterConfirm( self ):
		"""
		绝地反击进入确认
		"""
		self.cell.jueDiFanJiEnterConfirm()

	def jueDiFanJiCancelEnter( self ):
		"""
		绝地反击玩家主动取消进入
		"""
		self.cell.jueDiFanJiCancelEnter()

	def selectLeaveOrNot( self, status ):
		"""
		绝地反击玩家客户端弹出对话框让玩家选择是否连胜
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_RESULT", status )

	def jueDiFanJiStart( self ):
		"""
		绝地反击活动开始
		"""
		if self.level < csconst.JUE_DI_FAN_JI_LEVEL_LIMIT:
			return
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_BOX" )

	def jueDiFanJiEnd( self ):
		"""
		绝地反击活动结束后关闭榜单
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_BOX" )
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_RANK_LIST" )

	def selectRepeatedVictory( self ):
		"""
		绝地反击玩家选择连胜
		"""
		self.cell.selectRepeatedVictory()

	def selectLeave( self ):
		"""
		玩家选择离开
		"""
		#弹出提示让玩家确认是否离开，离开将会清除连胜
		self.cell.selectLeave()
		
	def receiveBulletin( self, scoreList ):
		"""
		接收绝地反击活动前20名的榜单
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_RANK", scoreList )

	def initJueDiFanJiButtonState( self ):
		"""
		初始化传送图标状态
		"""
		self.cell.initJueDiFanJiButtonState()

	def leaveJueDiFanJiSpace( self ):
		"""
		玩家离开绝地反击活动副本
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_BOX" )
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_RESULT" )

	def jueDiVictoryCountChange( self, repeatedVictoryCount ):
		"""
		define method
		连胜次数改变
		"""
		ECenter.fireEvent( "EVT_ON_VICTORY_COUNT_CHANGE", repeatedVictoryCount )

	def showJueDiFanJiPanel( self, state ):
		"""
		define method
		根据状态信息显示面板
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_PANEL", state )
		if state == csdefine.JUE_DI_FAN_JI_HAS_ENTERED:	# 已经进入副本
			ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_BOX" )

	def onJueDiSignUp( self ):
		"""
		define method
		报名成功
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_SIGN_UP" )

	def onJueDiMatchSuccess( self ):
		"""
		define method
		匹配成功
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_MATCH_SUCCESS" )

	def onJueDiConfirm( self ):
		"""
		define method
		确认进入
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_CONFIRM" )

	def onJueDiEnter( self ):
		"""
		define method
		成功进入
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_BOX" )

	def onShowJueDiFanJiBox( self ):
		"""
		define method
		玩家重新登陆
		"""
		if self.level < csconst.JUE_DI_FAN_JI_LEVEL_LIMIT:
			return
		ECenter.fireEvent( "EVT_ON_SHOW_JUEDI_BOX" )

	def showJueDiFanJiRankList( self ):
		"""
		显示排行榜
		"""
		self.cell.showJueDiFanJiRankList()

	def receiveScoreInfo( self, score ):
		"""
		绝地反击活动接收连胜积分
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_RANK_SCORE", score )

	def onJueDiFanJiCountDown( self, time ):
		"""
		绝地反击活动PK保护时间结束
		"""
		ECenter.fireEvent( "EVT_ON_JUEDI_COUNT_DOWN", time )
		