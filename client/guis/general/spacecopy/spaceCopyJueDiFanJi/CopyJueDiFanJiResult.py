# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import Timer
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText

class CopyJueDiFanJiResult( Window ):
	def __init__( self ):
		panel = GUI.load( "guis/general/spacecopyabout/spaceCopyJueDiFanJi/copyJueDiFanJiResult.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )

		self.__pyBtnContinue = HButtonEx( panel.btnContinue, self )	# 继续
		self.__pyBtnContinue.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnContinue.onLClick.bind( self.__jueDiContinue )
		labelGather.setPyBgLabel( self.__pyBtnContinue, "SpaceCopyJueDiFanJi:JueDiResult", "btnContinue" )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel, self )	# 不继续
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__jueDiLeave )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "SpaceCopyJueDiFanJi:JueDiResult", "btnCancel" )

		self.__pyBtnLeave = HButtonEx( panel.btnLeave, self )	# 离开
		self.__pyBtnLeave.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnLeave.onLClick.bind( self.__jueDiLeave )
		labelGather.setPyBgLabel( self.__pyBtnLeave, "SpaceCopyJueDiFanJi:JueDiResult", "btnLeave" )

		self.__pyLbText = CSRichText( panel.lbText )
		self.__pyLbText.fontSize = 16
		self.__pyLbText.align = "C"
		self.__pyLbText.text = ""

		labelGather.setLabel( panel.lbTitle, "SpaceCopyJueDiFanJi:JueDiResult", "lbTitle" )
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.pressedOK_ = False
		self.callback_ = lambda *args : False
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.addToMgr()

		self.__jueDiScore = 0
		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_JUEDI_RESULT"] = self.__onShow	#显示面板
		self.__triggers["EVT_ON_HIDE_JUEDI_RESULT"] = self.__onHide #隐藏面板
		self.__triggers["EVT_ON_JUEDI_RANK_SCORE"] = self.__onJueDiScore #胜场积分
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __jueDiContinue( self ):
		BigWorld.player().selectRepeatedVictory()
		self.hide()

	def __jueDiLeave( self ):
		BigWorld.player().selectLeave()
		self.hide()

	def __onShow( self, status ):
		self.show( status )

	def __onHide( self ):
		self.hide()

	def __onJueDiScore( self, score ):
		self.__jueDiScore = score

	def __update( self, status ):
		elements = self.getGui().elements
		frm_result = elements["frm_result"]
		frm_result.texture = ""
		if status == csdefine.JUE_DI_FAN_JI_VICTORY_STATUS:	#胜利
			self.__pyBtnContinue.visible = True
			self.__pyBtnContinue.enable = True
			self.__pyBtnCancel.visible = True
			self.__pyBtnCancel.enable = True
			self.__pyBtnLeave.visible = False
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiResult", "lbText", self.__jueDiScore )
#			frm_result.texture = "icons/tb_rw_z_011.dds"
		elif status == csdefine.JUE_DI_FAN_JI_DRAW_STATUS:	#平局
			self.__pyBtnContinue.visible = False
			self.__pyBtnCancel.visible = False
			self.__pyBtnLeave.visible = True
			self.__pyBtnLeave.enable = True
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiResult", "lbText", 1 )
#			frm_result.texture = "icons/skill_person_008.dds"
		elif status == csdefine.JUE_DI_FAN_JI_FAILED_STATUS: #失败
			self.__pyBtnContinue.visible = False
			self.__pyBtnCancel.visible = False
			self.__pyBtnLeave.visible = True
			self.__pyBtnLeave.enable = True
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiResult", "lbText", 0 )

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def show( self, status, pyOwner = None ):
		self.__update( status )
		Window.show( self, pyOwner )

	def onLeaveWorld( self ):
		self.hide()