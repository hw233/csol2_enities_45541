# -*- coding: gb18030 -*-
from gbref import rds
import event.EventCenter as ECenter

class RoleCopyInterface:
	"""
	副本的公用接口
	"""
	def __init__( self ):
		self.pickAnima_maxContinuousPick = 0 #最大连续数
		self.pickAnima_maxZhadan = 0 #炸弹数
	
	#---------------------------------------------------
	# 拾取灵气玩法
	#---------------------------------------------------
	def pickAnima_enterSpace( self ):
		"""
		define method
		进入回调
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_START" )
		
	def pickAnima_reqStart( self ):
		"""
		向服务器请求玩法开始
		"""
		self.cell.pickAnima_reqStart()
	
	def pickAnima_start( self ):
		"""
		拾取灵光玩法开始
		"""
		self.changeWorldCamHandler( 2, 1.532, 3.2 )
		self.pickAnima_maxContinuousPick = 0
		self.pickAnima_maxZhadan = 0
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_ONGOING" )
		
	def pickAnima_stop( self ):
		"""
		拾取灵光副本结束
		"""
		self.changeWorldCamHandler( 1 )
#		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_END" )
		
	
	def pickAnima_upPickInfos( self, allPickNum, continuousPickNum ):
		"""
		define method
		allPickNum 总共获得数量
		continuousPickNum 当前连续数量
		"""
		if self.pickAnima_maxContinuousPick < continuousPickNum:
			self.pickAnima_maxContinuousPick = continuousPickNum
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_PICKNUM_CHANGED", allPickNum, continuousPickNum )
	
	def pickAnima_triggerZhaDan( self ):
		"""
		define method.
		触碰炸弹
		"""
		self.pickAnima_maxZhadan += 1
	
	def pickAnima_overReport( self, allPickNum, potentialCount ):
		"""
		define method
		拾取灵气玩法结果
		allPickNum 一共拾取总数
		potentialCount 一共获得的潜能点数
		"""
		#self.pickAnima_maxContinuousPick 最大连续数
		#self.pickAnima_maxZhadan 炸弹数
		#评级按JIRA上的算法算一下
		ECenter.fireEvent( "EVT_ON_PLAYER_REIKIPICK_OVER_REPORT", allPickNum, potentialCount )
	
	def pickAnima_confirmQuitSpace( self ):
		"""
		玩家确定退出位面
		"""
		self.cell.pickAnima_confirmQuitSpace()
