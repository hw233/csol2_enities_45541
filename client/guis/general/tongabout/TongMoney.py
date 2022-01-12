# -*- coding: gb18030 -*-
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
import GUIFacade
import csdefine
import csconst
import Language
import Const
import utils

class TongMoneyGUI( Window ) :
	__instance=None
	def __init__( self ) :
		assert TongMoneyGUI.__instance is None,"TongMoneyGUI.__instance has been created"
		TongMoneyGUI.__instance=self
		wnd = GUI.load( "guis/general/tongabout/tongMoney/tongMoney.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4			# in uidefine.py
		self.activable_ = True				# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__trapID = None
		self.__initialize( wnd )
		self.addToMgr("TongMoneyGUI")
		
	@staticmethod
	def instance():
		if TongMoneyGUI.__instance is None:
			TongMoneyGUI.__instance=TongMoneyGUI()
		return TongMoneyGUI.__instance
		
	@staticmethod
	def getInstance():
		"""
		return None or the instance of TongMoneyGUI
		"""
		return TongMoneyGUI.__instance

	def __initialize( self, wnd ) :
		self.__pyInfoPanel = CSTextPanel( wnd.infoPanel.clipPanel, wnd.infoPanel.sbar )
		self.__pyInfoPanel.foreColor = 255, 241, 192
		self.__pyInfoPanel.text = ""
		self.__pyBtnShut = HButtonEx( wnd.btnShut )
		self.__pyBtnShut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.__pyBtnShut, "TongAbout:TongMoney", "btnShut" )
	
		labelGather.setLabel( wnd.lbTitle, "TongAbout:TongMoney", "lbTitle" )

	# -------------------------------------------------

	def __addTrap( self ):

		if self.__trapID is not None:
			self.__delTrap()
		distance = csconst.COMMUNICATE_DISTANCE
		target=GUIFacade.getGossipTarget()
		if hasattr( target, "getRoleAndNpcSpeakDistance" ):
			distance = target.getRoleAndNpcSpeakDistance() # + 2		# 去掉这莫名其妙的"+2" modify by gjx 2009-4-2
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
	def onEvent( self, eventMacro, *args ) :
		"""
		event triggering
		"""
		self.__triggers[eventMacro]( *args )
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers["EVT_OPEN_TONG_MONEY_WINDOW"] = self.__onShowTongMoneyWindow	# show window for talking trigger
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
			
	def instanceShow(self,spendingMoney):
		self.__onShowTongMoneyWindow( spendingMoney )

	# ---------------------------------------
	def __onShowTongMoneyWindow( self, spendingMoney ) :
		"""
		"""
		self.__pyInfoPanel.text = PL_NewLine.getSource()
		player = BigWorld.player()
		totalMoney = player.tongMoney
		jkLevel = player.tong_buildDatas[csdefine.TONG_BUILDING_TYPE_JK]["level"]
		limitMoney = Const.TONG_MONEY_LIMIT[ jkLevel ][ 0 ]
		validMoney = totalMoney - limitMoney
		chiefWage =  Const.TONG_CHIEF_WAGE["right"][player.tongLevel]
		viceChiefWage = Const.TONG_CHIEF_WAGE["left"][player.tongLevel]

		totalMoney = utils.currencyToViewText( totalMoney )
		limitMoney = utils.currencyToViewText( limitMoney )
		validMoney = utils.currencyToViewText( validMoney )
		chiefWage =  utils.currencyToViewText( chiefWage )
		viceChiefWage = utils.currencyToViewText( viceChiefWage )
		buildWage = utils.currencyToViewText( spendingMoney )

		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:TongMoney", "totalMoney" )%( PL_Space.getSource(3),totalMoney,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:TongMoney", "validMoney" )%( PL_Space.getSource(3),validMoney,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:TongMoney", "limitMoney" )%( PL_Space.getSource(3),limitMoney,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:TongMoney", "chiefWage" )%( PL_Space.getSource(3),chiefWage,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:TongMoney", "viceChiefWage" )%( PL_Space.getSource(3),viceChiefWage,PL_NewLine.getSource(2) )
		self.__pyInfoPanel.text += labelGather.getText( "TongAbout:TongMoney", "buildWage" )%( PL_Space.getSource(3),buildWage,PL_NewLine.getSource(2) )
		self.__addTrap()
		self.show()

	def __onShut( self ):
		self.hide( )
		

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __reset( self ) :
		self.__delTrap()
		self.__pyInfoPanel.text = ""

	def __onEndTalking( self ) :
		self.__reset()
		self.hide()

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
		TongMoneyGUI.__instance=None
		self.__deregisterTriggers()
		self.__triggers={}
		
		
	def __del__(self):
		Window.__del__( self )
		if Debug.output_del_TongMoneyGUI :
			INFO_MSG( str( self ) )