# -*- coding: gb18030 -*-

import BigWorld
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from config.client.msgboxtexts import Datas as mbmsgs

class CopyTBBattleTransPanel( Window ):
	__instance=None
	def __init__( self, pyBinder = None ):
		assert CopyTBBattleTransPanel.__instance is None, "CopyTBBattleTransPanel window has been created"
		CopyTBBattleTransPanel.__instance = self
		panel = GUI.load( "guis/general/spacecopyabout/spaceCopyTBBattle/copyTBBattleTransPanel.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )

		self.__pyBtnTrans = HButtonEx( panel.btnTrans, self )	# 参与
		self.__pyBtnTrans.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTrans.onLClick.bind( self.__onTrans )
		labelGather.setPyBgLabel( self.__pyBtnTrans, "SpaceCopyTBBattleRank:TransPanel", "btnTrans" )

		self.__pyBtnOk = HButtonEx( panel.btnOk, self )		# ...
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "SpaceCopyTBBattleRank:TransPanel", "btnOk" )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel, self )	# 传回
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "SpaceCopyTBBattleRank:TransPanel", "btnCancel" )

		self.__pyLbText = CSRichText( panel.lbText )
		self.__pyLbText.text = labelGather.getText( "SpaceCopyTBBattleRank:TransPanel", "lbText" )

		labelGather.setLabel( panel.lbTitle, "SpaceCopyTBBattleRank:TransPanel", "lbTitle" )
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.pressedOK_ = False
		self.callback_ = lambda *args : False
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.addToMgr()

		self.__triggers = {}
		self.__registerTriggers()

	@staticmethod
	def instance():
		"""
		"""
		if CopyTBBattleTransPanel.__instance is None :
			CopyTBBattleTransPanel.__instance = CopyTBBattleTransPanel()
		return CopyTBBattleTransPanel.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return CopyTBBattleTransPanel.__instance

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_TBBATTLE_TRANS_WINDOW"] = self.__onShow 	# 显示参与/回传界面
		self.__triggers["EVT_ON_HIDE_TBBATTLE_TRANS_WINDOW"] = self.__onHide	# 隐藏界面
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __onTrans( self ):
		"""
		"""
		BigWorld.player().cell.TDB_transToActPos()
		self.hide()

	def __onOk( self ):
		self.__onTrans()

	def __onCancel( self ):
		BigWorld.player().cell.TDB_transportBack()
		self.hide()

	def __onShow( self, buttonFlag ):
		self.show( buttonFlag )

	def __onHide( self ):
		self.hide()

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def show( self, buttonFlag, pyBinder = None ):
		if buttonFlag == 1:	# 参与
			self.__pyBtnOk.visible = False
			self.__pyBtnCancel.visible = False
			self.__pyBtnTrans.visible = True
			self.__pyBtnTrans.enable = True
		if buttonFlag == 2:	# 传回
			self.__pyBtnOk.visible = True
			self.__pyBtnOk.enable = False
			self.__pyBtnCancel.visible = True
			self.__pyBtnCancel.enable = True
			self.__pyBtnTrans.visible = False
		if buttonFlag == 3:	# 传送、传回都显示
			self.__pyBtnTrans.visible = False
			self.__pyBtnOk.visible = True
			self.__pyBtnOk.enable = True
			self.__pyBtnCancel.visible = True
			self.__pyBtnCancel.enable = True
			
		Window.show( self, pyBinder )
