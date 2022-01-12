# -*- coding: gb18030 -*-
# $Id: SpeComPanel.py

from guis import *
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from ItemsFactory import ObjectItem
from guis.general.kitbag.Animation import Animation
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.general.kitbag.ObjectItem import ObjectItem as KitbagItem
from CastKitItem import ExtractItem
from ItemSystemExp import SpecialStuffComposeExp
g_stuffComp = SpecialStuffComposeExp.instance()
import csconst
import csdefine
import csstatus
import Const

class SpecialStuffComPanel( TabPanel ):
	"""
	����ϳ����
	"""
	_item_dsp = {}
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyMsgBox = None
		self.__initialize( panel )
	
	def __initialize( self, panel ):
		self.__pyItems = []
		for name, item in panel.itemsPanel.children:
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = ExtractItem( item, self, "item" )
			self.__pyItems.append( pyItem )

		self.__pyInfoPanel = CSTextPanel( panel.infoPanel.clipPanel, panel.infoPanel.sbar )
		self.__pyInfoPanel.opGBLink = True
		self.__pyInfoPanel.spacing = 2.0
		self.__pyInfoPanel.aglin = "C"
		self.__pyInfoPanel.text = labelGather.getText( "CasketWindow:SpeComPanel", "compInfo" )

		self.__pyCost = MoneyBar( panel.costBox )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0
		
		self.__pyBtnComp = HButtonEx( panel.btnComp )
		self.__pyBtnComp.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnComp.onLClick.bind( self.__onCompose )
		labelGather.setPyBgLabel( self.__pyBtnComp, "CasketWindow:SpeComPanel", "compose" )
		
		labelGather.setLabel( panel.infoPanel.title.stTitle, "CasketWindow:SpeComPanel", "comTitle" )
		labelGather.setLabel( panel.costText, "CasketWindow:AttrExtractPanel", "reqMoney" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_KITBAG_ADD_ITEM"] = self.__onUpdateInfo
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onUpdateInfo
		self.__triggers["EVT_ON_ITEM_EQUIPED"] = self.__onKitbagRemoveItem
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}
	
	def __onUpdateInfo( self, itemInfo ):
		"""
		������Ʒ
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			pyItem.update( itemInfo )
			self.__calcCost()
	
	def __onKitbagRemoveItem( self, itemInfo ):
		"""
		�����Ƴ���Ʒ
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			self.__lockItem( itemInfo, False )
			pyItem.update( None )
			self.__calcCost()

	def __getPyItemByUID( self, uid ) :
		"""
		����UID���ҽ������Ƿ��и���Ʒ
		"""
		for pyItem in self.__pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid : return pyItem

	def __showMessage( self, msg, style = MB_OK, cb = None ) :
		"""
		������ʾ��ͬʱֻ�ܵ���һ��
		"""
		def callback( res ) :
			self.__pyMsgBox = None
			if callable( cb ) :
				cb( res )
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", style, callback, self )
	
	def __onCompose( self, pyBtn ):
		"""
		ȷ�Ϻϳ�
		"""
		if pyBtn is None:return
		elemUIs = self.__getElemUIDs()
		BigWorld.player().cell.specialStuffCompose( elemUIs )
		self.pyParent.clearIndications()

	def __getElemUIDs( self ) :
		"""
		���ȷ�Ϻ����Ķ����Ƿ��ѱ䶯
		"""
		return [ pyItem.itemInfo.uid for pyItem in self.__pyItems if pyItem.itemInfo is not None ]
	
	def __calcCost( self ):
		"""
		���㻨��
		"""
		uids = self.__getElemUIDs()
		itemList = [ BigWorld.player().getItemByUid_( uid ) for uid in uids ]
		lvm = 0 #�շ��õĵ���ƽ���ȼ�
		qua = 0 #�շ��õĵ���ƽ��Ʒ��
		ray = 1	#�ɺϳɷ���
		money = 0 #��Ҫ����
		if len( itemList ) == 0:
			money = 0
		mItems = {}
		lqItems = {}
		for item in itemList:
			if mItems.has_key( item.id ):
				mItems[item.id] += item.amount
			else:
				mItems[item.id] = item.amount
			if not item.isFrozen() and \
				not lqItems.has_key( item.id ):
				lqItems[item.id] = ( item.getLevel(), item.getQuality())
		itemInfo = g_stuffComp.getDstItemInfo( mItems )
		if len( itemInfo ) == 0:
			money = 0
		else:
			for lqTuple in lqItems.values():
				lvm += lqTuple[0]
				qua += lqTuple[1]
			lvm = int( lvm / len( mItems ) )
			qua = int( qua / len( mItems ) )
			ray = itemInfo[0][1]
			if lvm > 0 and lvm <= 50:    #1~50 1.1^���ߵȼ�*100*Ʒ��/3
				money = 1.1 ** lvm * 100 * qua /3
			else:           #51~150 1.03^���ߵȼ�*2700 *Ʒ��/3
				money = 1.03 ** lvm * 2700 * qua /3
		self.__pyCost.money = int( money )*ray

	def __lockItem( self, itemInfo, locked ) :
		"""
		֪ͨ��������/����ĳ����Ʒ
		"""
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )

	def __lockItems( self, locked ) :
		"""
		��/�رս���ʱ�ı䱳���ж�Ӧ��Ʒ����ɫ
		"""
		for pyItem in self.__pyItems :
			if pyItem.itemInfo is None: continue
			self.__lockItem( pyItem.itemInfo, locked )

	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def onStoneDrop__( self, pyTarget, pyDropped ) :
		"""
		�Ϸźϳɲ���
		'"""
		itemInfo = pyDropped.itemInfo
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

	def onItemRemove__( self, pyIcon ) :
		"""
		�һ��Ƴ���Ʒ
		"""
		if pyIcon.itemInfo is None : return
		self.__lockItem( pyIcon.itemInfo, False )
		pyParent = pyIcon.pyParent
		if pyParent and pyParent.pyRtName_:
			pyIcon = pyParent
		pyIcon.update( None )
		self.__calcCost()

	def onItemMouseEnter__( self, pyItem ):
		"""
		��ʾ��Ʒ��������Ϣ
		"""
		tag = pyItem.tag
		dsp = self._item_dsp.get( tag, "" )
		if dsp != "":
			toolbox.infoTip.showToolTips( self, dsp )

	def onItemMouseLeave__( self ):
		"""
		������Ʒ��������Ϣ
		"""
		toolbox.infoTip.hide()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onShow( self ):
		self.__lockItems( True )
	
	def onHide( self ):
		self.__lockItems( False )

	def onLeaveWorld( self ):
		self.onHide()
		for pyItem in self.__pyItems:
			pyItem.update( None )
			
	def showDragItemIndication( self, idtId, itemType ):
		if itemType == Const.CASKET_WINDOW_STUFF :#����
			itemcount = 0
			for item in self.__pyItems:
				if item.itemInfo is not None:
					itemcount += 1
			if itemcount < 3:
				toolbox.infoTip.showHelpTips( idtId, self.__pyItems[0] )
				self.pyParent.addVisibleOpIdt( idtId )
	
	def showOkIndication( self, idtId ):
		itemcount = 0
		for item in self.__pyItems:
			if item.itemInfo is not None:
				itemcount += 1
		if itemcount >= 3:
			toolbox.infoTip.showHelpTips( idtId, self.__pyBtnComp )
			self.pyParent.addVisibleOpIdt( idtId )
		