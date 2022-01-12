# -*- coding: gb18030 -*-

from guis import *
from guis.common.Window import Window
from AbstractTemplates import Singleton
from guis.controls.Button import Button
from guis.tooluis.CSTextPanel import CSTextPanel
from LabelGather import labelGather


class TbExplainWnd( Singleton, Window ) :

	__instance = None

	def __init__( self ) :
		assert TbExplainWnd.__instance is None ,"MsgBoard instance has been created"
		TbExplainWnd.__instance = self
		wnd = GUI.load( "guis/general/tanabata/explanationwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__pyBtnHide = Button( wnd.btnHide )
		self.__pyBtnHide.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.hide )

		txPanel = wnd.pnl_content
		self.__pyTextPanel = CSTextPanel( txPanel.clipPanel, txPanel.sbar )
		self.addToMgr( "tbExplainWnd" )
		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TANABATA1 )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( txPanel.bgTitle.stTitle, "Tanabata:explain", "stContent" )
		labelGather.setPyBgLabel( self.__pyBtnHide, "Tanabata:explain", "btnHide" )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_TbExplainWnd:
			INFO_MSG( str( self ) )

	@staticmethod
	def instance():
		if TbExplainWnd.__instance is None:
			TbExplainWnd.__instance = TbExplainWnd()
		return TbExplainWnd.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return TbExplainWnd.__instance
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showText( self, title, text, pyOwner = None ) :
		"""
		显示说明内容
		"""
		self.title = title
		self.__pyTextPanel.text = text
		self.show( pyOwner )
	
	def hide( self ):
		Window.hide( self )
		self.removeFromMgr()
		TbExplainWnd.__instance = None

	# -------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		退出游戏
		"""
		self.hide()