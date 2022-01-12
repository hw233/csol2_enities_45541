# -*- coding: gb18030 -*-
#
# $Id: BuyPanel.py,v 1.14 2008-09-01 10:02:33 zhangdengshan Exp $


import csarithmetic
import csdefine
import GUIFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.SelectableButton import SelectableButton
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import ObjectItem
from WareItem import WareItem
from Repairer import Repairer
from guis.tooluis.CSRichText import CSRichText
from event.EventCenter import *
from config.client import GoodsType
from LabelGather import labelGather
import ItemTypeEnum
import csstring

g_image =  PL_Image.getSource("%s")	#��ȡ��ʽ����ͼƬ

# ��Ʒ������
class BasePanel( TabPanel ):
	
	_cc_items_rows = ( 6, 2 )
	_item_dragMark = DragMark.NPC_TRADE_BUY #��Ʒ�Ϸű��
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.dropFocus = True
		self.itemTypies_ = {} #��Ʒ����,keyΪ��Ʒ���ͣ�valuesΪ��Ʒ��intemInfo�б�
		self.npcClassName = ""
		self.triggers_ = {}
		self.registerTriggers_()
		self.__height = 0.0
		self.__initialize( panel )
		self.__borderIndex = 0 # ��¼��Ʒ����
		self.__firstBorder = None # ��¼��һ���Ա߰�ť
	
	def __initialize( self, panel ):
		self.__pyLbGold = StaticText( panel.moneyPanel.lbGold )
		self.__pyLbGold.text = ""
		self.__pyLbSilver = StaticText( panel.moneyPanel.lbSilver )
		self.__pyLbSilver.text = ""
		self.__pyLbCopper = StaticText( panel.moneyPanel.lbCoin )
		self.__pyLbCopper.text = ""
	
		self.pyItemsPage_ = ODPagesPanel( panel.itemsPanel, panel.pgIdxBar )
		self.pyItemsPage_.onViewItemInitialized.bind( self.__initListItem )
		self.pyItemsPage_.onDrawItem.bind( self.__drawListItem )
		self.pyItemsPage_.selectable = True
		self.pyItemsPage_.onItemSelectChanged.bind( self.__onItemSelectedChange )
		self.pyItemsPage_.viewSize = self._cc_items_rows
		
		self.__pySelectGroup = SelectorGroup()

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_ROLE_MONEY_CHANGED"] = self.onMoneyChanged_ #��Ǯ�ı�
		for key in self.triggers_ :
			GUIFacade.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		for key in self.triggers_.iterkeys() :
			GUIFacade.registerEvent( key, self )
			
	# ---------------------------------------------------------
	def onMoneyChanged_( self, oldMoney, newMoney ):
		goldNum = newMoney/10000
		silverNum = ( newMoney - goldNum*10000 )/100
		copperNum = newMoney - goldNum*10000 - silverNum*100
		self.__pyLbGold.text = csarithmetic.toUSValue( goldNum )
		self.__pyLbSilver.text = csarithmetic.toUSValue( silverNum )
		self.__pyLbCopper.text = csarithmetic.toUSValue( copperNum )
		
	def __initListItem( self, pyViewItem ):
		"""
		��ʼ����ӵ���Ʒ�б���
		"""
		item = GUI.load( "guis/general/tradewindow/item.gui" )
		uiFixer.firstLoadFix( item )
		pyInvoice = WareItem( item, self._item_dragMark, self )
		pyViewItem.pyInvoice = pyInvoice
		pyViewItem.addPyChild( pyInvoice )
		pyViewItem.dragFocus = False
		pyInvoice.left = 0
		pyInvoice.top = 0

	def __drawListItem( self, pyViewItem ) :
		"""
		�ػ���Ʒ�б���
		"""
		itemInfo = pyViewItem.pageItem
		pyInvoice = pyViewItem.pyInvoice
		pyViewItem.focus = itemInfo is not None
		pyInvoice.crossFocus = itemInfo is not None
		pyInvoice.selected = pyViewItem.selected
		pyInvoice.update( itemInfo )
		curPageIndex = self.pyItemsPage_.pageIndex
		totalPageIndex = self.pyItemsPage_.maxPageIndex

	def __onItemSelectedChange( self, index ):
		player = BigWorld.player()
		itemInfo = self.pyItemsPage_.selItem
		if itemInfo is None:return
		baseInfo = itemInfo.baseInfo
		baseItem = baseInfo.baseItem
	
	def addItemInfo_( self, index, itemInfo, tradeObject = "" ):
		btnpaths = { 2: "guis/general/tradewindow/typebtn_2.gui",
				3: "guis/general/tradewindow/typebtn_3.gui",
				4: "guis/general/tradewindow/typebtn_4.gui",		
				}
		self.npcClassName = tradeObject
		type = itemInfo.invoiceType #��Ʒ����		
		pySelBtn = None
		if not self.itemTypies_.has_key( type ): #û�и�������Ʒ
			typeStr = self.__getItemTypeStr( type )
			typeLen = len( csstring.toWideString( typeStr ) )
			btnpath = btnpaths.get( typeLen )
			if not btnpath:
				btnpath = "guis/general/tradewindow/typebtn_4.gui"
			tabBtn = GUI.load( btnpath )
			uiFixer.firstLoadFix( tabBtn )
			pyBtn = BorderBtn( tabBtn )
			pyBtn.text = typeStr
			pyBtn.type = type
			pyBtn.setStatesMapping( UIState.MODE_R1C3 )
			pyBtn.onSelectChanged.bind( self.__onTypeBtnSelected )
			# ------------------------------------------------------------
			# ���ڶ������͵���Ʒ����ʱ����ʾ��ҳ
			# �˲��ִ�������Ϊ�߻�Ҫ��ֻ��һҳ��Ʒ��ʱ����ʾ�ұ߷�ҳ --pj
			self.__borderIndex += 1
			if not self.__firstBorder: # ��һ����Ʒ����ʱ
				self.__layoutBorders() # ��ֹֻ��һ�����͵���Ʒʱ�ұߵı߿򲻻��Զ�����
				self.__firstBorder = pyBtn
				self.__pySelectGroup.addSelector( pyBtn )
				if self.__pySelectGroup.pyCurrSelector is None:
					self.__pySelectGroup.pyCurrSelector = self.__pySelectGroup.pySelectors[0]
			if self.__borderIndex == 2: # �ڶ�����Ʒ����ʱ
				self.__addBtn( self.__firstBorder )
				self.__pySelectGroup.addSelector( pyBtn )
				self.__addBtn( pyBtn )
				if self.__pySelectGroup.pyCurrSelector is None:
					self.__pySelectGroup.pyCurrSelector = self.__pySelectGroup.pySelectors[0]
			elif self.__borderIndex > 2: # ��������Ʒ�������������
				self.__pySelectGroup.addSelector( pyBtn )
				self.__addBtn( pyBtn )
				if self.__pySelectGroup.pyCurrSelector is None:
					self.__pySelectGroup.pyCurrSelector = self.__pySelectGroup.pySelectors[0]
					pySelBtn = self.__pySelectGroup.pySelectors[0]
			# ------------------------------------------------------------------
			self.itemTypies_[type] = [( index, itemInfo)]
		else: #�Ѿ����ڸ�������
			self.itemTypies_[type].append( ( index, itemInfo ) )

		# ��ȡ��ҳ��Btn
		pySelBtn = self.__pySelectGroup.pyCurrSelector
		if not pySelBtn : # �����ǰֻ��һ����ҳ�������÷�ҳ��Btn
			pySelBtn = self.__firstBorder
		#���Ĭ�����
		btnType = pySelBtn.type
		if type == btnType:
			self.__showBuyItems( type )

	def __addBtn( self, pyBtn ):
		self.addPyChild( pyBtn )
		parentGui = self.pyTopParent.getGui()
		rt = parentGui.elements["frm_rt"]
		r = parentGui.elements["frm_r"]
		rtBottom = rt.position.y + rt.size.y
		if self.__pySelectGroup.count<= 1:
			pyBtn.top = rtBottom - 1.0
		else:
			pyBtn.top = self.__pySelectGroup.pySelectors[-2].bottom - 2.0
		pyBtn.left = r.position.x + r.size.x - 7.0
		self.__layoutBorders()

	def __layoutBorders( self ): #��̬�����Աߵ�borders
		parentGui = self.pyTopParent.getGui()
		rt = parentGui.elements["frm_rt"]
		r = parentGui.elements["frm_r"]
		rb = parentGui.elements["frm_rb"]
		btnCount = self.__pySelectGroup.count
		if btnCount < 1:
			rTop = rt.position.y + rt.size.y			
		else:
			rTop = self.__pySelectGroup.pySelectors[-1].bottom		
		r.position.y = rTop - 1.0
		r.size.y = rb.position.y - rTop

	def __getItemTypeStr( self, type ):
		"""
		������Ʒ���ͻ����������
		"""
		return GoodsType.Datas[ type ]
		
	def __onTypeBtnSelected( self, pyBtn, selected ):
		if not selected : return
		type = pyBtn.type
		self.__showBuyItems( type )

	def __showBuyItems( self, type ):
		self.pyItemsPage_.clearItems()
		invoices = self.itemTypies_.get( type, [] )
		for invoice in invoices:
			index = invoice[0]
			baseInfo = invoice[1] 
			itemInfo = ItemInfo( baseInfo, index, self.npcClassName )
			if itemInfo not in self.pyItemsPage_.items:
				self.pyItemsPage_.addItem( itemInfo )
	
	def __removeBtn( self, pyBtn ):
		if pyBtn in self.__pySelectGroup.pySelectors:
			self.delPyChild( pyBtn )
			self.__pySelectGroup.removeSelector( pyBtn )
			self.__height -= pyBtn.height
		if self.__height <= 0:
			self.__height = 0
		self.__layoutBorders()

	def clearBtns( self ):
		self.__borderIndex =0
		self.__firstBorder = None
		count = self.__pySelectGroup.count
		for index in xrange( count - 1, -1, -1 ) :
			self.__removeBtn( self.__pySelectGroup.pySelectors[index] )
	
	def clearItems( self ):
		self.pyItemsPage_.clearItems()
		self.itemTypies_ = {}

class ItemInfo:
	def __init__( self, baseInfo, index, npcName = "" ):
		self.baseInfo = baseInfo
		self.index = index
		self.npcName = npcName

# ---------------------------------------------------------------------
# ��ͨ������Ʒ���
class BuyPanel( BasePanel ):
	
	def __init__( self, panel = None ):
		BasePanel.__init__( self, panel )
		self.__repairType = csdefine.EQUIP_REPAIR_NORMAL
		self.__height = 0.0
		self.__pyRepairer = Repairer()
		self.__initialize( panel )

	def __initialize( self, panel ):
		self.__pyAllFixBtn = AllFixBtn( panel.allFixBtn )
		self.__pyAllFixBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyAllFixBtn.crossFocus = True
		self.__pyAllFixBtn.visible = False
		self.__pyAllFixBtn.onMouseEnter.bind( self.__onAllEnter )
		self.__pyAllFixBtn.onMouseLeave.bind( self.__onAllLeave )
		self.__pyAllFixBtn.onLClick.bind( self.__onAllFix )

		self.__pyOneFixBtn = Button( panel.oneFixBtn )
		self.__pyOneFixBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyOneFixBtn.onLClick.bind( self.__onOneFix )

		self.__pyCheckBg = PyGUI( panel.speCheck )
		self.__pyCheck = CheckBoxEx( panel.speCheck )
		self.__pyCheck.checked = False
		self.__pyCheck.onCheckChanged.bind( self.__onCheck )
		
		self.__pyLastSellItem = WareItem( panel.selledItem, DragMark.NPC_TRADE_REDEEM, self )
		self.__pyLastSellItem.index = -1

		self.__pySundriesBtn = Button( panel.sundriesBtn ) # һ�����ӻ���ť
		self.__pySundriesBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pySundriesBtn.onLClick.bind( self.__onSellAllSundries )

		labelGather.setLabel( panel.speCheck.stext, "TradeWindow:buyPanel", "imSpeCheck" )
		labelGather.setPyBgLabel( self.__pySundriesBtn, "TradeWindow:buyPanel", "btnSundries" )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_INVOICES_BAG_INFO_CHANGED"] = self.__onAddItemInfo #�����Ʒ
		self.triggers_["EVT_ON_REDEEM_UPDATE_LAST_SELLED"] = self.__onUpdateSellItem #���������Ʒ
		self.triggers_["EVT_ON_ROLE_EQUIP_REPAIR_COMPLETE"] = self.__onEquipRepairComplete #װ��ȫ������ɹ��Ļص�
		self.triggers_["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onMountVehicle #������
		self.triggers_["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onDisMountVehicle #������
		self.triggers_["EVT_ON_VEHICLE_EXP_UPDATE"] = self.__onVehicleExpUpdate # ��辭��ֵ����
		self.triggers_["EVT_ON_TONG_CHAPMAN_RECEIVE_GOODS_INFO_CHANGE"] = self.__onReceiveGoodsInfoChange # ���շ������İ����Ʒ�����ı�֪ͨ
		self.triggers_["EVT_ON_TOGGLE_TONG_BUILD_INFO"] = self.__onReciveBuildInfo	#��ȡ��������Ϣ
		BasePanel.registerTriggers_( self )

	def deregisterTriggers_( self ) :
		BasePanel.deregisterTriggers_( self )
	# -----------------------------------------------------
	
	def __onAddItemInfo( self, index, itemInfo, tradeObject = "" ):
		if index == 0 and itemInfo is None :
			return
		BuyPanel.addItemInfo_( self, index, itemInfo, tradeObject )

	def __onUpdateSellItem( self, index, baseInfo ): # ��ʾ���һ��������Ʒ
		itemInfo = ItemInfo( baseInfo, index, self.npcClassName )
		self.__pyLastSellItem.update( itemInfo )

	def __onEquipRepairComplete( self ):
		if self.__pyAllFixBtn.isMouseHit():
			toolbox.infoTip.showToolTips(self, labelGather.getText( "TradeWindow:buyPanel", "allHaveRepaired" ) )
			self.__pyAllFixBtn.setState( UIState.DISABLE )

	def __onMountVehicle( self ):
		player = BigWorld.player()
		if player is None: return
		vehicleData = player.vehicleDatas.get( player.vehicleDBID )
		if vehicleData is None: return
		for pyViewItem in self.pyItemsPage_.pyViewItems:
			itemInfo = pyViewItem.pageItem
			if itemInfo is None:continue
			baseItem = itemInfo.baseItem
			pyInvoice = pyViewItem.pyInvoice
			if baseItem.getType() in ItemTypeEnum.VEHICLE_EQUIP_LIST:
				vLevel = vehicleData[ "level" ]
				if vLevel < baseItem.getReqLevel():
					pyInvoice.pyItem.color = 255, 100, 100, 200
				else:
					pyInvoice.pyItem.color = 255, 255, 255, 255

	def __onDisMountVehicle( self ):
		for pyViewItem in self.pyItemsPage_.pyViewItems:
			pyInvoice = pyViewItem.pyInvoice
			pyInvoice.pyItem.color = 255, 100, 100, 200

	def __onVehicleExpUpdate( self, dbid ):
		player = BigWorld.player()
		if player is None: return
		if player.vehicleDBID != dbid:return
		for pyViewItem in self.pyItemsPage_.pyViewItems:
			itemInfo = pyViewItem.pageItem
			if itemInfo is None:continue
			baseItem = itemInfo.baseItem
			pyInvoice = pyViewItem.pyInvoice
			if baseItem.getType() in ItemTypeEnum.VEHICLE_EQUIP_LIST:
				vLevel = player.vehicleDatas[ player.vehicleDBID ][ "level" ]
				if vLevel < baseItem.getReqLevel():
					pyInvoice.pyItem.color = 255, 100, 100, 200
				else:
					pyInvoice.pyItem.color = 255, 255, 255, 255

	def __onRemoveSellItem( self, index, itemInfo ):
		if self.__pyLastSellItem.index == index:
			self.__pyLastSellItem.update( index, itemInfo )
			GUIFacade.updateLastSellItem()

	def __onReciveBuildInfo( self, buildData ):
		if not self.__pyAllFixBtn.visible:return
		if buildData["type"] == csdefine.TONG_BUILDING_TYPE_TJP:
			if GUIFacade.calcuAllRepairPrice( self.__repairType ) > 0:
				self.__pyAllFixBtn.setState( UIState.COMMON )
			else:
				self.__pyAllFixBtn.setState( UIState.DISABLE )

	def __clearItems( self ):
		self.pyItemsPage_.clearItems()
	# -------------------------------------------------------------
	def __onOneFix( self, pyBtn ):
		self.__pyRepairer.enterUsing( pyBtn )

	def __onAllFix( self ):
		if not self.__pyAllFixBtn.visible:return
		def query( rs_id ):
			if rs_id == RS_OK:
				GUIFacade.repairAllEquip( self.__repairType )
		msg =GUIFacade.calcuAllRepairPrice( self.__repairType )
		if msg == "":return
		# "%s���Ƿ�ȷ����Ҫ����?"
		showMessage( mbmsgs[0x0a01] % msg, "", MB_OK_CANCEL, query, pyOwner = self )
		return True

	def __onAllEnter( self ):
		if not self.__pyAllFixBtn.visible:return
		msg = GUIFacade.calcuAllRepairPrice( self.__repairType )
		if msg == "":
			msg = labelGather.getText( "TradeWindow:buyPanel", "noneNeedRepair" )
		toolbox.infoTip.showToolTips( self, msg )

	def __onAllLeave( self ):
		toolbox.infoTip.hide()

	def __onCheck( self, checked ):
		if checked:
			self.__repairType = csdefine.EQUIP_REPAIR_SPECIAL
		else:
			self.__repairType = csdefine.EQUIP_REPAIR_NORMAL
		GUIFacade.setRepairType( self.__repairType )

	def __onReceiveGoodsInfoChange( self, uid, itemInfo, chapman ):
		"""
		���շ������İ����Ʒ�����ı�֪ͨ

		@param	uid:		��ƷID
		@param	itemInfo:	��Ʒʵ��
		@param	chapman:	����
		"""
		if uid < 1:
			return
		else:
			for pyViewItem in self.pyItemsPage_.pyViewItems:
				pyInvoice = pyViewItem.pyInvoice
				if pyInvoice.itemInfo is None:continue
				if pyInvoice.uid == uid:
					newInfo = ItemInfo( itemInfo, pyInvoice.index, self.npcClassName )
					pyInvoice.update( newInfo )

	def __onSellAllSundries( self ):
		"""
		��������������NPC
		"""
		player = BigWorld.player()
		kitbagDict = player.kitbags
		uids = []
		amounts = []
		commKitBagIDs=[ kitID for kitID in kitbagDict if kitID in range(csdefine.KB_COMMON_ID,csdefine.KB_CASKET_ID)]
		for kitbagID in commKitBagIDs:
			for item in player.getItems( kitbagID ):
				if item.canSell() and item.getType() == ItemTypeEnum.ITEM_NORMAL_SUNDRIES: # ��������ﲢ�ҿ��Գ���
					uids.append( item.uid )
					amounts.append( item.amount )
		GUIFacade.sellArrayToNPC( uids, amounts )

	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.triggers_[eventMacro]( *args )

	def onMoneyChange( self, oldValue, newValue ):
		BasePanel.onMoneyChanged_( self, oldValue, newValue )

	def onLeaveWorld( self ):
		"""
		"""
		self.__pyCheck.checked = False

	def clearItems( self ):
		BasePanel.clearItems( self )
		itemInfo = ItemInfo( None, self.__pyLastSellItem.index )
		self.__pyLastSellItem.update( itemInfo )
		
	def setRepairBtn( self, canRepair, className ):
		self.npcClassName = className
		self.__pyAllFixBtn.visible = canRepair
		self.__pyOneFixBtn.visible = canRepair
		self.__pyCheckBg.visible = canRepair
		if className != "TongChapman": #��ͨ����NPC
			if GUIFacade.calcuAllRepairPrice( self.__repairType ) > 0:
				self.__pyAllFixBtn.setState( UIState.COMMON )
			else:
				self.__pyAllFixBtn.setState( UIState.DISABLE )

# -------------------------------------------------------------
#��߷�ҳ��ť
class BorderBtn( SelectableButton ):
	def __init__( self, borderBtn ):
		SelectableButton.__init__( self, borderBtn )
		self.__pyRich = CSRichText( borderBtn.richText)
		self.__pyRich.maxWidth = 20.0
		self.__pyRich.spacing = -1
		self.__pyRich.foreColor = ( 255,227,184,255 )
		
	def onStateChanged_( self, state ):
		SelectableButton.onStateChanged_( self, state )
		if state == UIState.SELECTED:
			self.__pyRich.foreColor = ( 142, 216, 217, 255 )
		else:
			self.__pyRich.foreColor = ( 255,227,184,255 )

	def _getText( self ):
		return self.__pyRich.text

	def _setText( self, text ):
		textLen = len( csstring.toWideString( text ) )
		if textLen >= 3:
			self.__pyRich.spacing = -2.0
		else:
			self.__pyRich.spacing = 12.0
		self.__pyRich.text = text

	text = property( _getText, _setText )

# --------------------------------------------------------------------
# ȫ������ť
class AllFixBtn( Button ):
	def __init__( self, button ):
		Button.__init__( self, button )

	def onMouseEnter_( self ) :
		Control.onMouseEnter_( self )
		if GUIFacade.calcuAllRepairPrice( csdefine.EQUIP_REPAIR_NORMAL ) > 0:	# �������������û�ж�����Ҫ������ť����Ҫ�ı�״̬����������Ϊnormal������Ҫ���ʵ�ʵ��������ͣ�
			if uiHandlerMgr.getCapUI() == self :
				self.setState( UIState.PRESSED )
			elif self.enable:
				self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		if self.enable and GUIFacade.calcuAllRepairPrice( csdefine.EQUIP_REPAIR_NORMAL ) > 0:	# �������������û�ж�����Ҫ������ť����Ҫ�ı�״̬����������Ϊnormal������Ҫ���ʵ�ʵ��������ͣ�
			self.setState( UIState.COMMON )
		return True

	def onLMouseUp_( self, mods ) :
		uiHandlerMgr.uncapUI( self )
		isMouseHit = self.isMouseHit()
		if not self.enable :
			self.setState( UIState.DISABLE )
		elif GUIFacade.calcuAllRepairPrice( csdefine.EQUIP_REPAIR_NORMAL ) > 0:
			if isMouseHit :
				self.setState( UIState.HIGHLIGHT )
			else :
				self.setState( UIState.COMMON )
		Control.onLMouseUp_( self, mods )
		return isMouseHit

	def onLMouseDown_( self, mods ) :
		isMouseHit = self.isMouseHit()
		if isMouseHit :
			uiHandlerMgr.capUI( self )
			if GUIFacade.calcuAllRepairPrice( csdefine.EQUIP_REPAIR_NORMAL ) > 0:
				self.setState( UIState.PRESSED )
		Control.onLMouseDown_( self, mods )
		return isMouseHit

# -------------------------------------------------------------------------
class ItemChapmanBuyPanel( BasePanel ):
	"""
	���ﻻ�ｻ�׽���
	"""
	def __init__( self, panel = None ):
		BasePanel.__init__( self, panel )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_ITEM_CHAPMAN_BAG_INFO_CHANGED"] = self.__onAddItemInfo #�����Ʒ
		BasePanel.registerTriggers_( self )

	def deregisterTriggers_( self ) :
		BasePanel.deregisterTriggers_( self )
	# -----------------------------------------------------
	def __onAddItemInfo( self, index, itemInfo ):
		if index == 0 and itemInfo is None :
			return
		BasePanel.addItemInfo_( self, index, itemInfo )

	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.triggers_[eventMacro]( *args )

	def onMoneyChange( self, oldValue, newValue ):
		BasePanel.onMoneyChanged_( self, oldValue, newValue )

	def clearItems( self ):
		BasePanel.clearItems( self )

	def clearBtns( self ):
		BasePanel.clearBtns( self )

# ---------------------------------------------------------------------------
# �Ե�ֵ�������
class PointChapmanBuyPanel( BasePanel ):

	def __init__( self, panel = None ):
		BasePanel.__init__( self, panel )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_POINT_CHAPMAN_BAG_INFO_CHANGED"] = self.__onAddItemInfo #�����Ʒ
		BasePanel.registerTriggers_( self )

	def deregisterTriggers_( self ) :
		BasePanel.deregisterTriggers_( self )
	# -----------------------------------------------------
	
	def __onAddItemInfo( self, index, itemInfo ):
		if index == 0 and itemInfo is None :
			return
		BasePanel.addItemInfo_( self, index, itemInfo )
	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.triggers_[eventMacro]( *args )

	def onMoneyChange( self, oldValue, newValue ):
		BasePanel.onMoneyChanged_( self, oldValue, newValue )

	def clearItems( self ):
		BasePanel.clearItems( self )

	def clearBtns( self ):
		BasePanel.clearBtns( self )
