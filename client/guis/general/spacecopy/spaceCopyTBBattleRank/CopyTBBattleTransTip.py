# -*- coding: gb18030 -*-

import BigWorld
import Timer
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText

class CopyTBBattleTransTip( Window ):
	def __init__( self, pyBinder = None ):
		panel = GUI.load( "guis/general/spacecopyabout/spaceCopyTBBattle/copyTBBattleTransTip.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )

		self.__pyBtnOk = HButtonEx( panel.btnOk, self )		# 传回
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "SpaceCopyTBBattleRank:TransTip", "btnOk" )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel, self )	# 原地
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "SpaceCopyTBBattleRank:TransTip", "btnCancel" )

		self.__pyLbText = CSRichText( panel.lbText )
		self.__pyLbText.align = "C"
		self.__pyLbText.text = ""

		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "BOTTOM"
		self.pressedOK_ = False
		self.callback_ = lambda *args : False
		self.posZSegment = ZSegs.L2
		self.activable_ = True
		self.escHide_ = False
		self.addToMgr()
		self.movable_ = False	# 窗口不能拖动
		self.__lifeTime = 0.0	# 窗口存活时间
		self.__lifeTimerID = 0

	# -------------------------------------------------
	def __onOk( self ):
		BigWorld.player().cell.TDB_transportBack()
		self.hide()

	def __onCancel( self ):
		self.hide()

	def __countDown( self ):
		if not self.visible: return
		self.__lifeTime -= 1
		if self.__lifeTime <= 0:
			Timer.cancel( self.__lifeTimerID )
			self.__lifeTimerID = 0
			self.hide()
			return
		self.__pyLbText.text = labelGather.getText( "SpaceCopyTBBattleRank:TransTip", "lbText", self.__lifeTime )

	def show( self, pyBinder = None ):
		self.__lifeTime = 15.0
		Timer.cancel( self.__lifeTimerID )
		self.__lifeTimerID = Timer.addTimer( 1.0, 1.0, self.__countDown )
		self.__pyLbText.text = labelGather.getText( "SpaceCopyTBBattleRank:TransTip", "lbText", self.__lifeTime )
		Window.show( self, pyBinder )