# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.general.spacecopy.spaceCopyTBBattleRank.CopyTBBattleTransTip import CopyTBBattleTransTip

class CopyTBBattleTransBox( RootGUI ):
	def __init__( self ):
		box = GUI.load( "guis/general/spacecopyabout/spaceCopyTBBattle/copyTBBattleTransBox.gui" )
		uiFixer.firstLoadFix( box )
		RootGUI.__init__( self, box )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "BOTTOM"
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_ = False
		self.addToMgr()
		self.__flashSign = True # 用于控制窗口闪烁
		self.__initBox( box )
		self.__triggers = {}
		self.__registerTriggers()

	def __initBox( self, box ):
		self.__pyTransTip = CopyTBBattleTransTip()
		self.__pyTransItem = TransItem( box.item.item, self )
		self.__pyTransItem.onLClick.bind( self.__onClickActButton )

		self.__ringFader = box.fader
		self.__ringFader.speed = 0.4
		self.__ringFader.value = 1.0
		self.__flashID = 0

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_TBBATTLE_TRANS"] = self.__onShow	# 弹出传送界面
		self.__triggers["EVT_ON_HIDE_TBBATTLE_TRANS"] = self.__onHide 	# 隐藏传送界面
		self.__triggers["EVT_ON_SHOW_TBBATTLE_TRANS_TIP"] = self.__onShowTip
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------------
	def __flash( self ):
		"""
		窗口闪烁 淡入淡出
		"""
		BigWorld.cancelCallback( self.__flashID )
		self.__flashID = 0
		if self.__flashSign:
			self.__ringFader.value = 1.0
		else:
			self.__ringFader.value = 0.2
		self.__flashSign = not self.__flashSign
		self.__flashID = BigWorld.callback( self.__ringFader.speed + 0.1, self.__flash )
		
	def __stopFlash( self ):
		"""
		停止闪烁
		"""
		if self.__flashID:
			BigWorld.cancelCallback( self.__flashID )
			self.__flashID = 0
			self.__ringFader.value = 1.0

	def __onClickActButton( self, isSelected ):
		if isSelected:
			BigWorld.player().cell.TDB_onClickActButton()

	def __onShow( self ):
		self.show()

	def __onHide( self ):
		self.hide()
		self.__pyTransTip.hide()

	def __onShowTip( self ):
		self.__pyTransTip.show()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def show( self ):
		RootGUI.show( self )
		self.__flash()

	def hide( self ):
		self.__stopFlash()
		ECenter.fireEvent( "EVT_ON_HIDE_TBBATTLE_TRANS_WINDOW" )
		RootGUI.hide( self )

	def onLeaveWorld( self ):
		self.hide()

# -------------------------------------------------------------------------
class TransItem( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.icon = ( "guis/general/spacecopyabout/spaceCopyTBBattle/tb_xmlz.dds", ( (0.100000, 0.100000), (0.100000, 0.900000), (0.900000, 0.900000), (0.900000, 0.100000) ) )

	def onDescriptionShow_( self ):
		msg = labelGather.getText( "SpaceCopyTBBattleRank:TransBox", "transText" )
		toolbox.infoTip.showItemTips( self, msg )
