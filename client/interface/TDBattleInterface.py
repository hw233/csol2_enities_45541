# -*- coding: gb18030 -*-

import event.EventCenter as ECenter
class TDBattleInterface:
	"""
	仙魔论战接口
	"""
	def __init__( self ):
		pass
	
	def onCacheCompleted( self ):
		"""
		"""
		self.cell.TDB_onPlayerLogin()

	def TDB_receiveReslut( self, dict ):
		"""
		define method
		接收到活动结果
		"""
		ECenter.fireEvent("EVT_ON_TBBATTLE_SHOW_RANKLIST", dict )

	def TDB_showTransWindow( self, buttonFlag ):
		"""
		define method
		显示传送界面
		
		@buttonFlag: 区分显示的按钮：1为参与按钮，2为回传按钮
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TBBATTLE_TRANS_WINDOW", buttonFlag )

	def TDB_showActButton( self ):
		"""
		define method
		显示活动图标
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TBBATTLE_TRANS" )

	def TDB_hideActButton( self ):
		"""
		define method
		隐藏活动图标
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_TBBATTLE_TRANS" )

	def TDB_showActTip( self ):
		"""
		define method
		结束显示活动传回界面
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TBBATTLE_TRANS_TIP" )
