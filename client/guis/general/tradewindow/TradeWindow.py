# -*- coding: gb18030 -*-
#
# $Id: TradeWindow.py,v 1.36 2008-08-26 02:20:25 huangyongwei Exp $

from event.EventCenter import *
from guis import *
from guis.common.Window import Window
from guis.common.TrapWindow import UnfixedTrapWindow
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabPage
from guis.controls.Button import Button
from guis.tooluis.inputbox.InputBox import AmountInputBox
from BuyPanel import BuyPanel
from BuyPanel import ItemChapmanBuyPanel
from BuyPanel import PointChapmanBuyPanel
from RedeemPanel import RedeemPanel
from LabelGather import labelGather
from gbref import rds
from bwdebug import *
import csconst
import csdefine
import GUIFacade
import event.EventCenter as ECenter
import Language

class TradeWindow( UnfixedTrapWindow ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/tradewindow/window.gui" )
		uiFixer.firstLoadFix( wnd )
		UnfixedTrapWindow.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# ��ӵ�MutexGroup.TRADE1������

	def __initialize( self, wnd ):

		self.__pyTC = TabCtrl( wnd.tc )
		self.__pyBuyPanel = BuyPanel( wnd.tc.panel_0 )
		self.__pyBuyPanel.dropFocus = True
		self.__pyBuyPanel.onDrop.bind( self.__onItemDrop )
		pyTabBtn1 = TabButton( wnd.tc.btn_0 )
		pyTabBtn1.onLClick.bind( self.__onShowBuyPanel )
		pyTabBtn1.selectedForeColor = ( 142, 216, 217, 255 )
		self.__pyBuyPage = TabPage( pyTabBtn1, self.__pyBuyPanel )
		self.__pyTC.addPage( self.__pyBuyPage )

		pyTabBtn2 = TabButton( wnd.tc.btn_1 )
		pyTabBtn2.onLClick.bind( self.__onShowRedeemPanel )
		pyTabBtn2.selectedForeColor = ( 142, 216, 217, 255 )
		self.__pyRedeemPanel = RedeemPanel( wnd.tc.panel_1 )
		self.__pyTC.addPage( TabPage( pyTabBtn2, self.__pyRedeemPanel ) )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyLabel( self.pyLbTitle_, "TradeWindow:main", "miRbTitle" )
		labelGather.setPyBgLabel( pyTabBtn1, "TradeWindow:main", "btnBuyPanel" )
		labelGather.setPyBgLabel( pyTabBtn2, "TradeWindow:main", "btnRedeemPanel" )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		# chapmanEntity; open the trading window
		self.__triggers["EVT_ON_ROLE_ENTER_WORLD"] = self.__onRoleEnterWorld
		self.__triggers["EVT_ON_TRADE_WITH_NPC" ] = self.__showWindow
		self.__triggers["EVT_ON_ROLE_END_WITHNPC_TRADE"] = self.hide
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.hide										#��ɫ���������ش���
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	# -----------------------------------------------------------
	def __showWindow( self, npc ) :
		player = BigWorld.player()
		#ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", player.tradeState )			# ע�͵��������﷢�������Ϣ��������ġ���Ϊ������������������뽻�׷��������ٴ����ģ�hyw--2008.09.17��
		player.tradeState = csdefine.TRADE_CHAPMAN
		self.setTrappedEntID( npc.id )
		self.show( npc )

	# ------------------------------------------------------------
	def __onRoleEnterWorld( self, player ):
		self.__pyBuyPanel.onMoneyChange( 0, player.money )

	def __onItemDrop( self, pyTarget, pyDropped ):
		dragMark = rds.ruisMgr.dragObj.dragMark
		if dragMark == DragMark.KITBAG_WND :
			uid = pyDropped.itemInfo.baseItem.uid
			num = pyDropped.amount
			if num == 1:
				GUIFacade.sellToNPC( uid, num )
			else:
				def sell( result, amount ) :
					if result == DialogResult.OK :
						GUIFacade.sellToNPC( uid, amount )
				rang = ( 1, num )
				AmountInputBox().show( sell, self, rang )
		return True

	def __showRedeemItems( self, itemInfos ):
		if len( itemInfos ) <= 0:return
		for itemInfo in itemInfos:
			self.__pyRedeemPanel.reSetItem( itemInfo )

	def __onShowBuyPanel( self ):
		pass

	def __onShowRedeemPanel( self ):#*
		self.__pyBuyPanel.visile = False
		self.__pyRedeemPanel.initePanelBorder()
		redeemItems = GUIFacade.getRedeemItems()
		self.__showRedeemItems( redeemItems )
	
	def __showTips( self ):
		"""
		"""
		gui = self.__pyBuyPanel.pyItemsPage_.pyViewItems[0].pyInvoice.pyItem
		toolbox.infoTip.showOperationTips( 0x00a2, gui )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTrapTriggered_( self, entitiesInTrap ) :
		"""
		���崥��
		@param	entitiesInTrap		: �������ENTITY
		@type	entitiesInTrap		: LIST
		"""
		if self.trappedEntity not in entitiesInTrap :
			GUIFacade.tradeOverWithNPC()
			self.hide()
			
	def onMove_( self, dx, dy ) :
		Window.onMove_( self, dx, dy )
#		self.__pyTabCtr.pySelPage.pyPanel.onMove( dx, dy )
		toolbox.infoTip.moveOperationTips( 0x00a2 )
#		self.relocateIndications()

	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.__pyBuyPanel.onLeaveWorld()
		self.hide()

	def show( self, chapman ):
		self.__pyTC.pySelPage = self.__pyBuyPage
		className = chapman.__class__.__name__
		canRepair = chapman.hasFlag(csdefine.ENTITY_FLAG_REPAIRER) #�������Ƿ���������
		self.__pyBuyPanel.setRepairBtn( canRepair, className )
		GUIFacade.updateLastSellItem()	#���������Ʒ���������ѡ��û��������һ��������Ʒ������
		UnfixedTrapWindow.show( self )
		rds.helper.courseHelper.interactive( "Chapman" )
		BigWorld.callback( 0.5 , self.__showTips )

	def hide( self ):
		self.__itemInfos = {}
		if rds.statusMgr.isInWorld() :
			GUIFacade.tradeOverWithNPC()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		UnfixedTrapWindow.hide( self )
		self.__pyBuyPanel.clearItems()
		self.__pyBuyPanel.clearBtns()
		self.__pyRedeemPanel.clearItems()
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def __onStateLeave( self, state ):
		if state == csdefine.TRADE_CHAPMAN:
			GUIFacade.tradeOverWithNPC()
			self.hide()
			BigWorld.player().tradeState = csdefine.TRADE_NONE


from MessageBox import *
class ItemChapmanTradeWindow( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/tradewindow/specialwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		self.__trapID = 0

	def __initialize( self, wnd ):

		self.__pyBuyPanel = ItemChapmanBuyPanel( wnd.buyPanel )
		self.__pyBuyPanel.dropFocus = True
		self.__pyBuyPanel.onDrop.bind( self.__onItemDrop )
		self.__pyFishingBox = None

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyLabel( self.pyLbTitle_, "TradeWindow:main", "miRbTitle" )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		# chapmanEntity; open the trading window
		self.__triggers["EVT_ON_ROLE_ENTER_WORLD"] = self.__onRoleEnterWorld
		self.__triggers["EVT_ON_TRADE_WITH_ITEM_TRADER" ] = self.__showWindow
		self.__triggers["EVT_ON_ROLE_END_WITHNPC_TRADE"] = self.hide
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.hide						# ��ɫ���������ش���
		self.__triggers["EVT_ON_ROLE_BEGIN_FISHING"] = self.beginFishing	# ��ʼ����
		self.__triggers["EVT_ON_ROLE_END_FISHING"] = self.endFishing				# ��������

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	# -----------------------------------------------------------
	def __showWindow( self, npc ) :
		player = BigWorld.player()
		#ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", player.tradeState )			# ע�͵��������﷢�������Ϣ��������ġ���Ϊ������������������뽻�׷��������ٴ����ģ�hyw--2008.09.17��
		player.tradeState = csdefine.TRADE_CHAPMAN
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#�򿪴��ں�Ϊ�����ӶԻ�����
		self.show()
	# -----------------------------------------------------------
	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									#ɾ����ҵĶԻ�����
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()							#��ȡ��ǰ�Ի�NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				#���NPC�뿪��ҶԻ�����
			GUIFacade.tradeOverWithNPC()
			self.hide()														#���ص�ǰ���״���

	# ------------------------------------------------------------
	def __onRoleEnterWorld( self, player ):
		self.__pyBuyPanel.onMoneyChange( 0, player.money )

	def __onItemDrop( self, pyTarget, pyDropped ):
		dragMark = rds.ruisMgr.dragObj.dragMark
		if dragMark == DragMark.KITBAG_WND :
			uid = pyDropped.itemInfo.baseItem.uid
			num = pyDropped.amount
			if num == 1:
				GUIFacade.sellToNPC( uid, num )
			else:
				def sell( result, amount ) :
					if result == DialogResult.OK :
						GUIFacade.sellToNPC( uid, amount )
				rang = ( 1, num )
				AmountInputBox().show( sell, self, rang )
		return True


	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		self.__itemInfos = {}
		if rds.statusMgr.isInWorld() :
			GUIFacade.tradeOverWithNPC()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		Window.hide( self )
		self.__pyBuyPanel.clearItems()
		self.__pyBuyPanel.clearBtns()
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def __onStateLeave( self, state ):
		if state == csdefine.TRADE_CHAPMAN:
			GUIFacade.tradeOverWithNPC()
			self.hide()
			BigWorld.player().tradeState = csdefine.TRADE_NONE

	def beginFishing( self, player, reason ):
		"""
		�������ڵ���ĶԻ���
		�Լ�ȡ������Ŀ���
		"""
		def notarize( id ) :
			if id == RS_SPE_CANCEL and player.getState() == csdefine.ENTITY_STATE_CHANGING:
				player.end_body_changing( "" )
		# "������..."
		self.__pyFishingBox = showMessage( 0x0a21, "", MB_SPE_CANCEL, notarize )

	def endFishing( self ):
		"""
		��������رնԻ���
		"""
		if self.__pyFishingBox != None:
			self.__pyFishingBox.hide()

from MessageBox import *
class PointChapmanTradeWindow( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/tradewindow/specialwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		self.__trapID = 0

	def __initialize( self, wnd ):

		self.__pyBuyPanel = PointChapmanBuyPanel( wnd.buyPanel )
		self.__pyBuyPanel.dropFocus = True
		self.__pyBuyPanel.onDrop.bind( self.__onItemDrop )
		self.__pyFishingBox = None

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyLabel( self.pyLbTitle_, "TradeWindow:main", "miRbTitle" )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		# chapmanEntity; open the trading window
		self.__triggers["EVT_ON_ROLE_ENTER_WORLD"] = self.__onRoleEnterWorld
		self.__triggers["EVT_ON_TRADE_WITH_POINT_TRADER" ] = self.__showWindow
		self.__triggers["EVT_ON_ROLE_END_WITHNPC_TRADE"] = self.hide
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.hide

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	# -----------------------------------------------------------
	def __showWindow( self, npc ) :
		player = BigWorld.player()
		player.tradeState = csdefine.TRADE_CHAPMAN
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#�򿪴��ں�Ϊ�����ӶԻ�����
		self.show()
	# -----------------------------------------------------------
	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									#ɾ����ҵĶԻ�����
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()							#��ȡ��ǰ�Ի�NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				#���NPC�뿪��ҶԻ�����
			GUIFacade.tradeOverWithNPC()
			self.hide()														#���ص�ǰ���״���

	# ------------------------------------------------------------
	def __onRoleEnterWorld( self, player ):
		self.__pyBuyPanel.onMoneyChange( 0, player.money )

	def __onItemDrop( self, pyTarget, pyDropped ):
		dragMark = rds.ruisMgr.dragObj.dragMark
		if dragMark == DragMark.KITBAG_WND :
			uid = pyDropped.itemInfo.baseItem.uid
			num = pyDropped.amount
			if num == 1:
				GUIFacade.sellToNPC( uid, num )
			else:
				def sell( result, amount ) :
					if result == DialogResult.OK :
						GUIFacade.sellToNPC( uid, amount )
				rang = ( 1, num )
				AmountInputBox().show( sell, self, rang )
		return True

	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		self.__itemInfos = {}
		if rds.statusMgr.isInWorld() :
			GUIFacade.tradeOverWithNPC()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.__pyBuyPanel.clearItems()
		self.__pyBuyPanel.clearBtns()

	def __onStateLeave( self, state ):
		if state == csdefine.TRADE_CHAPMAN:
			GUIFacade.tradeOverWithNPC()
			self.hide()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
