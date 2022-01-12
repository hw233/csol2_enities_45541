# -*- coding: gb18030 -*-
#
# $Id: SellWindow.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $
# rewritten by ganjinxing 2010-01-19

from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.StaticText import StaticText
from SellPanel import VendSellPanel
from LogsPanel import VendLogsPanel
from LabelGather import labelGather
from gbref import rds
import csdefine
import csstatus


class VendSellWindow( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/vendwindow/sellwindow/vendsellwindow.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# ��ӵ�MutexGroup.TRADE1������

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "vendwindow:VendSellWindow", "lbTitle" )

	def __initialize( self, wnd ):
		self.__pyTabCtrl = TabCtrl( wnd.tc )
		panelCls = [ VendSellPanel, VendLogsPanel ]
		self.__pyTabCtrl.autoSearchPages( panelCls )
		for index, pyPage in enumerate( self.__pyTabCtrl.pyPages ) :
			pyPage.pyPanel.subclass( pyPage.pyPanel.gui, self )
			labelGather.setPyBgLabel( pyPage.pyBtn, "vendwindow:VendSellWindow", "tbBtn_%i" % index )

		self.pyStStallName_ = StaticText( wnd.stStallName ) 					# ̯λ����
		self.pyStStallName_.text = ""


	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TOGGLE_VENDWINDOW"] 		= self.__onToggleVisible
		self.__triggers["EVT_ON_VEND_UI_NAME_CHANGE"] 		= self.onSignboardChange_ 		# ��̯���Ƹı�
		self.__triggers["EVT_ON_VEND_WINDOW_MUTEX"] 		= self.hide			# ���̯���⣬��̯����ر�
		self.__triggers["EVT_ON_ROLE_DEAD"] 				= self.hide			# ��ɫ���������ش���
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __onToggleVisible( self ):
		player = BigWorld.player()
		if player.level < 15:		#���ӽ�ɫ��̯�ĵȼ����ƣ�15�����ϣ�
			player.statusMessage( csstatus.VEND_LEVEL_NOT_ENOUGH )
			return
		if player.state == csdefine.ENTITY_STATE_VEND: 							# �����ɫ�ڰ�̯�У�����Ӧ
			player.statusMessage( csstatus.YOU_ARE_VENDING )
			return
		if player.hasFlag( csdefine.ROLE_FLAG_TISHOU ) :						# ���ڽ���NPC����
			player.statusMessage( csstatus.VEND_FORBID_TISHOU )
			return
		if not player.canVendInArea(): 											# �����ɫ���ڰ�̯���򣬲���Ӧ
			player.statusMessage( csstatus.VEND_FORBIDDEN_AREA )
			return
		self.visible = not self.visible

	def onSignboardChange_( self, playerID, signboard ):
		if BigWorld.player().id != playerID:
			return
		self.pyStStallName_.text = signboard


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def show( self ):
		Window.show( self )
		player = BigWorld.player()
		vendSignboard = player.vendSignboard
		if vendSignboard == "":
			self.pyStStallName_.text = labelGather.getText( "vendwindow:VendSellWindow", "stStallName" )%player.getName()
		else:
			self.pyStStallName_.text = vendSignboard
		for pyTabPanel in self.__pyTabCtrl.pyPanels :
			pyTabPanel.onParentShow()

	def hide( self ):
		Window.hide( self )
		player = BigWorld.player()
		if player.tradeState == csdefine.ENTITY_STATE_VEND:
			player.tradeState = csdefine.TRADE_NONE
		player.vend_endVend()
		for pyTabPanel in self.__pyTabCtrl.pyPanels :
			pyTabPanel.onParentHide()

	def onLeaveWorld( self ):
		for pyTabPanel in self.__pyTabCtrl.pyPanels :
			pyTabPanel.reset()
		self.hide()
