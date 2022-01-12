# -*- coding: gb18030 -*-

# Implement the equip quality raise window.
# written by gjx 2010-08-13

from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar

from guis.MLUIDefine import QAColorText
from AbstractTemplates import Singleton
from EQExtractWnd import ExtractEquipItem, ExtractItem
from LabelGather import labelGather
from guis.MLUIDefine import QAColorText
from config.client.msgboxtexts import Datas as mbmsgs
import math
import csconst
import ItemTypeEnum
import GUIFacade

from config.item.EquipUpNeedItem import Datas as jadeData


class EQQualityUp( Singleton, Window ) :

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
		self.__pyBtnOk.onLClick.bind( self.__onUp )

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
		labelGather.setLabel( wnd.lbTitle, "EquipRemake:QAUp", "lbTitle" )

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
	def __onUp( self ) :
		"""
		Ʒ�ʷ���
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			# "�����һ��װ����"
			self.__showMessage( 0x0ea1 )
			return
		stone = self.__pyStone.itemInfo
		if stone is None :
			# "�����һ����������"
			self.__showMessage( 0x0eae )
			return
		elemUIDs = [ equip.uid, stone.uid ]
		if stone.baseItem.isBinded() and not \
			equip.baseItem.isBinded() :
				def confirmToUp( res ) :
					if res != RS_YES : return
					if elemUIDs != self.__getElemUIDs() : 		# �����֮ǰ�ķ��벻һ��
						self.__onUp()							# �����¼��һ��
					else :
						BigWorld.player().cell.EquipUp( equip.uid, stone.uid )
				# "ʹ���Ѱ󶨵ķ�����������װ��Ʒ�ʣ�װ�������Ϊ�󶨵ģ��Ƿ������"
				self.__showMessage( 0x0eaf, MB_YES_NO, confirmToUp )
		else :
			BigWorld.player().cell.EquipUp( equip.uid, stone.uid )

	def __getElemUIDs( self ) :
		"""
		��ȡ���з�����Ʒ��UID
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
		cost = int( math.ceil( equip.level**2.1 * 4**3.5 ))		# �߻��ļ��㹫ʽ��װ���ȼ�^2.1*4^3.5
		self.__pyCost.money = int( cost )

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
		���뱦ʯ
		"""
		itemInfo = pyDropped.itemInfo
		if itemInfo.id not in [ 60101178, 60101179, 60101180 ] :
			# "������������"
			self.__showMessage( 0x0eae )
			return
		equip = self.__pyEquip.itemInfo
		if equip is not None :
			needStoneID = jadeData.get( equip.level )
			if needStoneID != itemInfo.id :
				# "������ķ���������װ���ȼ�����"
				self.__showMessage( 0x0eb0 )
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
		if not ( itemInfo.isEquip and itemInfo.level >= 60 \
			and itemInfo.quality == ItemTypeEnum.CQT_PINK ) :
				# "�����60�����ϵķ�ɫװ����"
				msg = mbmsgs[0x0eb2] % ( 60, QAColorText[ ItemTypeEnum.CQT_PINK ] )
				self.__showMessage( msg )
				return
		stone = self.__pyStone.itemInfo
		if stone is not None :
			needStoneID = jadeData.get( itemInfo.level )
			if needStoneID != stone.id :
				# "������װ���ĵȼ���������񲻷�"
				self.__showMessage( 0x0eb1 )
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
		SELF.__cc_triggers[ "EVT_ON_RAISE_EQUIP_QUALITY" ] = SELF.__triggerVisible
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


EQQualityUp.registerTriggers()