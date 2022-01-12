# -*- coding: gb18030 -*-

# Implement the equip attribute pour window. Player can extract
# attribute from the equip and save that in one stone, and then
# pour this attribute into another equip.

# written by gjx 2010-08-07

from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar

from AbstractTemplates import Singleton
from EQExtractWnd import ExtractEquipItem, ExtractItem
from LabelGather import labelGather
import csconst
import ItemTypeEnum
import GUIFacade

class EQPourWnd( Singleton, Window ) :

	__cc_triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/equipremake/pourwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__triggers = {}
		self.__pyMsgBox = None
		self.__trapID = 0
		self.__trapEntityID = 0

		self.__initialize( wnd )
		self.__registerTriggers()

		self.addToMgr()
		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )			# ��ӵ�MutexGroup.TRADE1������


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

	def __initialize( self, wnd ) :
		self.__pyBtnOk = HButtonEx( wnd.btnOK )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onPour )

		self.__pyBtnHide = HButtonEx( wnd.btnHide )
		self.__pyBtnHide.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.hide )

		self.__pyCost = MoneyBar( wnd.moneyBoxs_cost )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0

		self.__pyEquip = ExtractEquipItem( wnd.equip, self )
		self.__pyEquip.update( None )

		self.__pyStone = ExtractItem( wnd.stone, self )
		self.__pyStone.update( None )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnOk, "EquipRemake:pour", "btnOK" )
		labelGather.setPyBgLabel( self.__pyBtnHide, "EquipRemake:pour", "btnHide" )
		labelGather.setLabel( wnd.st_needMoneyLabel, "EquipRemake:pour", "st_needMoneyLabel" )
		labelGather.setLabel( wnd.lbTitle, "EquipRemake:pour", "lbTitle" )

	# -------------------------------------------------
	def __addTrap( self ) :
		self.__delTrap()
		trapNPC = self.trapEntity
		if trapNPC :
			distance = csconst.COMMUNICATE_DISTANCE
			if hasattr( trapNPC, "getRoleAndNpcSpeakDistance" ) :
				distance = trapNPC.getRoleAndNpcSpeakDistance()
			self.__trapID = BigWorld.addPot( trapNPC.matrix, distance, self.__onEntitiesTrapThrough )
		else :
			self.hide()

	def __delTrap( self ) :
		if self.__trapID :
			BigWorld.delPot( self.__trapID )
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, enter, handle ) :
		if not enter :
			self.hide()

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
		#if itemInfo.intensifyLevel > 0 or \
		#	itemInfo.baseItem.getSlot() > 0 :
		#		self.__showMessage( "���ܹ�ע���й�ǿ������Ƕ��װ����" )
		#		return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()

	def onItemRemove__( self, pyItem ) :
		"""
		�һ��Ƴ���Ʒ
		"""
		if pyItem.itemInfo is None : return
		self.__lockItem( pyItem.itemInfo, False )
		pyItem.update( None )
		self.__calcCost()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, trapEntityID ) :
		Window.show( self )
		self.__trapEntityID = trapEntityID
		self.__lockItems( True )
		self.__addTrap()

	def hide( self ) :
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.__lockItems( False )
		self.__delTrap()
		self.dispose()
		self.__unregisterTriggers()
		self.__class__.releaseInst()

	def onLeaveWorld( self ) :
		Window.onLeaveWorld( self )
		self.hide()

	@classmethod
	def registerTriggers( SELF ) :
		SELF.__cc_triggers[ "EVT_ON_POUR_EQUIP" ] = SELF.__triggerVisible
		for key in SELF.__cc_triggers.iterkeys() :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		handler = SELF.__cc_triggers.get( evtMacro )
		if handler is None and SELF.insted :
			handler = SELF.inst.__triggers.get( evtMacro )
		if handler is not None : handler( *args )

	@classmethod
	def __triggerVisible( SELF, entityID ) :
		SELF.inst.show( entityID )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def trapEntity( self ) :
		return BigWorld.entities.get( self.__trapEntityID )


EQPourWnd.registerTriggers()