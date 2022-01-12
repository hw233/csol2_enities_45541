# -*- coding: gb18030 -*-

from bwdebug import *
import event.EventCenter as ECenter

class RoleDestinyTransInterface:
	"""
	 天命轮回副本接口
	 """
	def __init__( self ):
		self.livePoint = 0
	
	def openBoardInterface( self, boardNo, gateInfo, livePointInfo ):
		"""
		define method
		打开棋盘界面
		"""
		INFO_MSG( "Open board interface, board number is %i, gateInfo is %s, livePointInfo %s " % ( boardNo, gateInfo, livePointInfo ) )
		for dbid, livePoint in livePointInfo.items():
			if self.databaseID == dbid:
				self.livePoint = livePoint
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_INTERFACE_SHOW", boardNo, gateInfo, livePointInfo )

	def onCountDown( self, time ):
		"""
		define method
		开始倒计时
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_COUNTDOWN", time )
		INFO_MSG( "Start to count down, time is %i s" % time )

	def throwSieve( self ):
		"""
		掷筛子
		"""
		self.cell.throwSieve()

	def onGetSievePoint( self, point ):
		"""
		define method
		获得掷筛子点数
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_SIEVE_POINT", point )
		INFO_MSG( " Get sieve point %i from server" % point )

	def endPlaySieveAnimation(  self ):
		"""
		播放掷筛子动画结束
		"""
		self.cell.endPlaySieveAnimation()

	def onMoveRoleChess( self, roleID, step ):
		"""
		define method
		移动棋子
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_MOVE_CHESS", roleID, step )
		INFO_MSG( "Move role %i chess to point %i" % ( roleID, step ) )

	def onMoveRoleChessToStart( self, roleID ):
		"""
		define method
		移动棋子到起点
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_MOVE_TO_START", roleID )
		INFO_MSG( "Move role %i chess to start point !" % roleID )
		
	def endMoveChess( self ):
		"""
		移动棋子结束
		"""
		self.cell.endMoveChess()

	def closeBoardInterface( self, dispose = False ):
		"""
		define method
		关闭棋盘界面
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_INTERFACE_CLOSE", dispose )
		INFO_MSG( " Close Board interface!! " )

	def onRoleLivePointChanged( self, dbid, livePoint ):
		"""
		define mehtod
		玩家复活点数发生变化
		"""
		if self.databaseID == dbid:
			self.livePoint = livePoint
		INFO_MSG( "Change role %i livePoint to point %i" % ( dbid, livePoint ) )
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_LIVE_POINT_CHANGED", dbid, livePoint )

	def desTrans_msgs( self, msgType ):
		"""
		define method
		显示提示信息
		msgType在csdefine 中定义,eg:DESTINY_TRANS_FAILED_GATE
		"""
		INFO_MSG( "Show info msg , msgType %i " % msgType )
		ECenter.fireEvent( "EVT_ON_ROLE_DESTINYTRANS_DESTRANS_MSGS", msgType )
		
