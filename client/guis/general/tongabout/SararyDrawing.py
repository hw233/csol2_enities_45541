# -*- coding: gb18030 -*-
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csconst
import utils

class SararyDrawing( Window ) :
	__instance=None
	def __init__( self ) :
		assert SararyDrawing.__instance is None,"SararyDrawing.__instance has been created"
		SararyDrawing.__instance=self
		wnd = GUI.load( "guis/general/tongabout/tongMoney/sararyDrawing.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4			# in uidefine.py
		self.activable_ = True				# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = True
		self.__trapID = None
		self.__pyMsgBox = None
		self.__initialize( wnd )
		self.addToMgr("SararyDrawing")
		
	@staticmethod
	def instance():
		if SararyDrawing.__instance is None:
			SararyDrawing.__instance=SararyDrawing()
		return SararyDrawing.__instance

	def __initialize( self, wnd ) :
		self.__pyInfoPanel = CSTextPanel( wnd.infoPanel.clipPanel, wnd.infoPanel.sbar )
		self.__pyInfoPanel.foreColor = 255, 241, 192
		self.__pyInfoPanel.text = ""
		self.__pyBtnShut = HButtonEx( wnd.btnShut )
		self.__pyBtnShut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.__pyBtnShut, "TongAbout:SararyDrawing", "btnShut")
		
		self.__pyBtnDraw = HButtonEx( wnd.btnDrawSarary )
		self.__pyBtnDraw.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDraw.onLClick.bind( self.__onDrawSarary )
		labelGather.setPyBgLabel( self.__pyBtnDraw, "TongAbout:SararyDrawing", "btnDraw" )
	
		labelGather.setLabel( wnd.lbTitle, "TongAbout:SararyDrawing", "lbTitle" )

	# -------------------------------------------------

	def __addTrap( self ):

		if self.__trapID is not None:
			self.__delTrap()
		distance = csconst.COMMUNICATE_DISTANCE
		target=GUIFacade.getGossipTarget()
		if hasattr( target, "getRoleAndNpcSpeakDistance" ):
			distance = target.getRoleAndNpcSpeakDistance() 
		self.__trapID = BigWorld.addPot(target.matrix, distance, self.__onEntitiesTrapThrough )		# 打开窗口后为玩家添加对话陷阱s

	def __onEntitiesTrapThrough( self, isEnter,handle ):

		if not isEnter:
			self.__onShut()														#隐藏当前与NPC对话窗口

	def __delTrap( self ) :

		if self.__trapID is not None:
			BigWorld.delPot( self.__trapID )											#删除玩家的对话陷阱
			self.__trapID = None

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
		
	def instanceShow( self,sararyInfo ):
		self.__onShowTongMoneyWindow( sararyInfo )
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------

	def __onShowTongMoneyWindow( self, sararyInfo ) :
		"""
		"""
		self.__pyInfoPanel.text = PL_NewLine.getSource()
		lastWeekTotalContribute = sararyInfo[0] 
		lastWeekSalaryChangeRate = utils.currencyToViewText( sararyInfo[1] )
		lastWeekReceivedSalary = utils.currencyToViewText( sararyInfo[2] )
		thisWeekTotalContribute = sararyInfo[3]
		thisWeekSalaryChangeRate = utils.currencyToViewText( sararyInfo[4] )
		thisWeekReceivingSarary = utils.currencyToViewText( sararyInfo[5] )
		

		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:SararyDrawing", "lastWeekTotalContribute" )%( PL_Space.getSource(3),lastWeekTotalContribute,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:SararyDrawing", "lastWeekSalaryChangeRate" )%( PL_Space.getSource(3),lastWeekSalaryChangeRate,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:SararyDrawing", "lastWeekReceivedSalary" )%( PL_Space.getSource(3),lastWeekReceivedSalary,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:SararyDrawing", "thisWeekTotalContribute" )%( PL_Space.getSource(3),thisWeekTotalContribute,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:SararyDrawing", "thisWeekSalaryChangeRate" )%( PL_Space.getSource(3),thisWeekSalaryChangeRate,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:SararyDrawing", "thisWeekReceivingSarary" )%( PL_Space.getSource(3),thisWeekReceivingSarary,PL_NewLine.getSource(2) )
		self.__addTrap()
		self.show()

	def __onShut( self ):
		self.hide( )
	def __onDrawSarary( self ):
		"""
		领取俸禄
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				player = BigWorld.player()
				player.tong_onDrawSalary()
		self.__pyMsgBox = showMessage(mbmsgs[0x0683],"", MB_OK_CANCEL, query, pyOwner = self )
		return True
		
	def __reset( self ) :
		self.__delTrap()
		self.__pyInfoPanel.text = ""

	def onLeaveWorld( self ) :
		self.hide()
		self.__reset()

	def show( self ):
		Window.show( self )
		

	def hide( self ):
		Window.hide( self )
		self.__delTrap()
		self.dispose()
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		
	def dispose(self):
		SararyDrawing.__instance = None	
		
	def __del__(self):
		Window.__del__( self )