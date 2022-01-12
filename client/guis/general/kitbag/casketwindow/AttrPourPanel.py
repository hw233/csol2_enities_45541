# -*- coding: gb18030 -*-
# $Id: AttrPourPanel.py

from guis import *
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from CastKitItem import ExtractEquipItem, ExtractItem
import csconst
import csdefine
import Const

class AttrPourPanel( TabPanel ):
	"""
	���Թ�ע���
	"""
	_item_dsp = { "stone":labelGather.getText( "CasketWindow:AttrPourPanel", "stoneDsp" ),	#��Ʒ��˵��
					"equip":labelGather.getText( "CasketWindow:AttrPourPanel", "equipDsp" ),
					}
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__initialize( panel )
		self.__registerTriggers()
		self.__pyMsgBox = None
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_ITEM_EQUIPED"] = self.__onKitbagRemoveItem
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}
	
	def __initialize( self, panel ):
		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onPour )
		labelGather.setPyBgLabel( self.__pyBtnOk, "CasketWindow:main", "btnOk" )
		
		self.__pyCost = MoneyBar( panel.costBox )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0

		self.__pyEquip = ExtractEquipItem( panel.equipItem, self, "equip" )
		self.__pyEquip.update( None )

		self.__pyStone = ExtractItem( panel.stoneItem, self, "stone" )
		self.__pyStone.update( None )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		
		labelGather.setLabel( panel.costText, "CasketWindow:AttrExtractPanel", "reqMoney" )
	# -------------------------------------------------
	def __onPour( self ) :
		"""
		��ע����
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			# "�����һ��װ����"
			self.__showMessage( 0x0ea1 )
			return
		stone = self.__pyStone.itemInfo
		if stone is None :
			# "�����һ���������ꡣ"
			self.__showMessage( 0x0eab )
			return
		elemUIDs = [ equip.uid, stone.uid ]
		if stone.baseItem.isBinded() and not \
			equip.baseItem.isBinded() :
				def confirmToPour( res ) :
					if res != RS_YES : return
					if elemUIDs != self.__getElemUIDs() : 		# �����֮ǰ�ķ��벻һ��
						self.__onPour()							# �����¼��һ��
					else :
						BigWorld.player().cell.equipPour( elemUIDs )
				# "ʹ���Ѱ󶨵����������עװ����װ�������Ϊ�󶨵ģ��Ƿ������"
				self.__showMessage( 0x0eac, MB_YES_NO, confirmToPour )
		else :
			BigWorld.player().cell.equipPour( elemUIDs )

	def __getElemUIDs( self ) :
		"""
		���ȷ�Ϻ����Ķ����Ƿ��ѱ䶯
		"""
		pyItems = [ self.__pyEquip, self.__pyStone ]
		return [ e.itemInfo.uid for e in pyItems if e.itemInfo is not None ]

	def __calcCost( self ) :
		"""
		���������Ǯ
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			self.__pyCost.money = 0
			return
		stone = self.__pyStone.itemInfo
		if stone is None :
			self.__pyCost.money = 0
			return
		cost = equip.level**2 * equip.quality**2 * 10			# �߻��ļ��㹫ʽ
		self.__pyCost.money = cost

	# -------------------------------------------------
	def __onKitbagUpdateItem( self, itemInfo ) :
		"""
		����������Ʒ
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			pyItem.update( itemInfo )
			self.__calcCost()

	def __onKitbagRemoveItem( self, itemInfo ) :
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
		pyItems = [ self.__pyEquip, self.__pyStone ]
		for pyItem in pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid : return pyItem

	def __lockItems( self, locked ) :
		"""
		��/�رս���ʱ�ı䱳���ж�Ӧ��Ʒ����ɫ
		"""
		pyItems = [ self.__pyEquip, self.__pyStone ]
		for pyItem in pyItems :
			if pyItem.itemInfo is None: continue
			self.__lockItem( pyItem.itemInfo, locked )

	def __lockItem( self, itemInfo, locked ) :
		"""
		֪ͨ��������/����ĳ����Ʒ
		"""
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )

	# -------------------------------------------------
	def __reset( self ) :
		self.__pyEquip.update( None )
		self.__pyStone.update( None )
		self.__pyCost.money = 0

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


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def onStoneDrop__( self, pyTarget, pyDropped ) :
		"""
		�Ϸŷ���ʯ��Ʒ��
		"""
		itemInfo = pyDropped.itemInfo
		if itemInfo.id not in [ csconst.EQUIP_EXTRACT_PROITEM ] :
			# "������������ꡣ"
			self.__showMessage( 0x0ead )
			return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		�Ϸŵ�װ����
		"""
		itemInfo = pyDropped.itemInfo
		if not ( itemInfo.isEquip and itemInfo.level >= csconst.EQUIP_EXTRACT_LEVEL_MIN \
			and itemInfo.quality in csconst.EQUIP_EXTRACT_QUALITYS ) :
				# "�����60��������Ʒ���ڷ�ɫ���ϵ�װ����"
				self.__showMessage( 0x0ea8 )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

	def onItemRemove__( self, pyItem ) :
		"""
		�һ��Ƴ���Ʒ
		"""
		if pyItem.itemInfo is None : return
		self.__lockItem( pyItem.itemInfo, False )
		pyItem.update( None )
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

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
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
		pyItems = [ self.__pyEquip, self.__pyStone ]
		for pyItem in pyItems:
			pyItem.update( None )

	def showDragItemIndication( self, idtId, itemType ):
		if itemType == Const.CASKET_WINDOW_EQUIP :#װ��
			equip = self.__pyEquip.itemInfo
			if equip is None :
				toolbox.infoTip.showHelpTips( idtId, self.__pyEquip )
				self.pyParent.addVisibleOpIdt( idtId )
		elif itemType == Const.CASKET_WINDOW_STONE:#ʯͷ
			stone = self.__pyStone.itemInfo
			if stone is None:
				toolbox.infoTip.showHelpTips( idtId, self.__pyStone )
				self.pyParent.addVisibleOpIdt( idtId )
				
	def showOkIndication( self, idtId ):
		equip = self.__pyEquip.itemInfo
		if equip is None:return
		stone = self.__pyStone.itemInfo	
		if pyStone.itemInfo is not None :	
			toolbox.infoTip.showHelpTips( idtId, self.__pyBtnOk )
			self.pyParent.addVisibleOpIdt( idtId )
						
