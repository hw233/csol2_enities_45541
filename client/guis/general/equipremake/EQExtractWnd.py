# -*- coding: gb18030 -*-

# Implement the equip attribute extract window. Player can extract
# attribute from the equip and save that in one stone, and then
# pour this attribute into another equip.

# written by gjx 2010-08-06

from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar

from guis.MLUIDefine import ItemQAColorMode
from LabelGather import labelGather
from AbstractTemplates import Singleton
import csconst
import ItemTypeEnum
import GUIFacade


class EQExtractWnd( Singleton, Window ) :

	__cc_triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/equipremake/extractwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__triggers = {}
		self.__pyMsgBox = None
		self.__pyStones = []
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
		self.__pyBtnOk.onLClick.bind( self.__onExtract )

		self.__pyBtnHide = HButtonEx( wnd.btnHide )
		self.__pyBtnHide.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.hide )

		self.__pySTRate = StaticText( wnd.stRate )
		self.__pySTRate.text = "0 %"
		self.__pyCost = MoneyBar( wnd.moneyBoxs_cost )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0

		self.__pyEquip = ExtractEquipItem( wnd.equip, self )
		self.__pyEquip.update( None )
		self.__pyHierogram = ExtractHierogramItem( wnd.hierogram, self )
		self.__pyHierogram.update( None )

		self.__initStoneItems( wnd )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnOk, "EquipRemake:extract", "btnOK" )
		labelGather.setPyBgLabel( self.__pyBtnHide, "EquipRemake:extract", "btnHide" )
		labelGather.setLabel( wnd.st_rateLabel, "EquipRemake:extract", "st_rateLabel" )
		labelGather.setLabel( wnd.st_needMoneyLabel, "EquipRemake:extract", "st_needMoneyLabel" )
		labelGather.setLabel( wnd.lbTitle, "EquipRemake:extract", "lbTitle" )

	def __initStoneItems( self, wnd ) :
		"""
		��ʼ������ʯ��Ʒ��
		"""
		for name, item in wnd.children :
			if "stone_" not in name : continue
			pyStone = ExtractItem( item, self )
			pyStone.update( None )
			self.__pyStones.append( pyStone )

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
	def __onExtract( self ) :
		"""
		ȷ����ȡ
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			# "�����һ��װ����"
			self.__showMessage( 0x0ea1 )
			return
		elemUIDs = []
		allStoneBinded = True
		for pyStone in self.__pyStones :
			stone = pyStone.itemInfo
			if stone is None : continue
			if not stone.baseItem.isBinded() :
				allStoneBinded = False
			elemUIDs.append( stone.uid )
		stoneAmount = len( elemUIDs )
		if stoneAmount == 0 :
			# "�����ٷ���һ�ŷ���ʯ�򳬼�����ʯ��"
			self.__showMessage( 0x0ea2 )
			return

		elemUIDs.append( equip.uid )
		hierogram = self.__pyHierogram.itemInfo
		if hierogram is not None : elemUIDs.append( hierogram.uid )

		def checkAttribute() :
			createEft = equip.baseItem.getCreateEffect()
			pourEft = [ i for i in createEft if i[0] != 0 ]
			if len( pourEft ) > 0 :								# װ���й�ע����
				def cb( res ) :
					if res != RS_YES : return
					if elemUIDs != self.__getElemUIDs() :		# �����֮ǰ�ķ��벻һ��
						self.__onExtract()						# �����¼��һ��
					else :
						checkStoneAmount()
				# "��ע�����Բ��ܱ���ȡ���Ƿ������"
				self.__showMessage( 0x0ea3, MB_YES_NO, cb )
			else :
				checkStoneAmount()

		def checkStoneAmount() :
			if len( equip.baseItem.getExtraEffect() ) > stoneAmount :
				def cb( res ) :
					if res != RS_YES : return
					if elemUIDs != self.__getElemUIDs() :		# �����֮ǰ�ķ��벻һ��
						self.__onExtract()						# �����¼��һ��
					else :
						BigWorld.player().cell.equipExtract( elemUIDs )
				# "���ķ���ʯ�������㣬���ܰ��������Զ���ȡ��ֻ�������ȡ���е����ԣ��Ƿ������"
				self.__showMessage( 0x0ea4, MB_YES_NO, cb )
			else :
				BigWorld.player().cell.equipExtract( elemUIDs )

		checkAttribute()

	def __getElemUIDs( self ) :
		"""
		���ȷ�Ϻ����Ķ����Ƿ��ѱ䶯
		"""
		pyItems = self.__pyStones[:]
		pyItems.extend( [ self.__pyEquip, self.__pyHierogram ] )
		return [ e.itemInfo.uid for e in pyItems if e.itemInfo is not None ]

	def __calcRate( self ) :
		"""
		����ɹ���
		"""
		if self.__pyEquip.itemInfo is None :
			self.__pySTRate.text = "0 %"
			return
		stone = None
		for pyStone in self.__pyStones :
			if pyStone.itemInfo is None : continue
			stone = pyStone.itemInfo
			break
		if stone is None :
			self.__pySTRate.text = "0 %"
			return
		rate = 0
		if stone.id == csconst.EQUIP_EXTRACT_NEEDITEMS :
			rate = 30
		elif stone.id == csconst.EQUIP_EXTRACT_SUNEEDITEMS :
			rate = 45
		if self.__pyHierogram.itemInfo and rate :
			rate = 100
		self.__pySTRate.text = "%i %%" % rate

	def __calcCost( self ) :
		"""
		���������Ǯ
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			self.__pyCost.money = 0
			return
		stones = [ st.itemInfo for st in self.__pyStones if st.itemInfo is not None ]
		amount = min( len( stones ), len( equip.baseItem.getExtraEffect() ) )
		if amount == 0 :
			self.__pyCost.money = 0
			return
		stQuality = stones[0].quality
		cost = equip.level**2 * equip.quality * 2**stQuality * 2 * amount	# �߻��ļ��㹫ʽ
		self.__pyCost.money = cost

	# -------------------------------------------------
	def __onKitbagUpdateItem( self, itemInfo ) :
		"""
		����������Ʒ
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			pyItem.update( itemInfo )
			self.__calcRate()
			if pyItem != self.__pyHierogram :
				self.__calcCost()

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""
		�����Ƴ���Ʒ
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			self.__lockItem( itemInfo, False )
			pyItem.update( None )
			self.__calcRate()
			if pyItem != self.__pyHierogram :
				self.__calcCost()

	def __getPyItemByUID( self, uid ) :
		"""
		����UID���ҽ������Ƿ��и���Ʒ
		"""
		pyItems = self.__pyStones[:]
		pyItems.extend( [ self.__pyEquip, self.__pyHierogram ] )
		for pyItem in pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid : return pyItem

	def __lockItems( self, locked ) :
		"""
		��/�رս���ʱ�ı䱳���ж�Ӧ��Ʒ����ɫ
		"""
		pyItems = self.__pyStones[:]
		pyItems.extend( [ self.__pyEquip, self.__pyHierogram ] )
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
		for pyStone in self.__pyStones :
			pyStone.update( None )
		self.__pyEquip.update( None )
		self.__pyHierogram.update( None )
		self.__pySTRate.text = "0 %"
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
		validStones = [ csconst.EQUIP_EXTRACT_NEEDITEMS, csconst.EQUIP_EXTRACT_SUNEEDITEMS ]
		if itemInfo.id not in validStones :
			# "��������ʯ�򳬼�����ʯ��"
			self.__showMessage( 0x0ea6 )
			return
		for pyStone in self.__pyStones :
			if pyStone.itemInfo is None : continue
			if pyStone == pyTarget : continue
			if pyStone.itemInfo.quality != itemInfo.quality :
				# "����ʯ���ܻ��á�"
				self.__showMessage( 0x0ea7 )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()
		self.__calcCost()

	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		�Ϸŵ�װ����
		"""
		itemInfo = pyDropped.itemInfo
		if not ( itemInfo.isEquip and itemInfo.level >= csconst.EQUIP_EXTRACT_LEVEL_MIN \
			and itemInfo.quality  in csconst.EQUIP_EXTRACT_QUALITYS ) :
				# "�����60��������Ʒ���ڷ�ɫ���ϵ�װ����"
				self.__showMessage( 0x0ea8 )
				return
		#if itemInfo.intensifyLevel > 0 or \
		#	itemInfo.baseItem.getSlot() > 0 :
		#		self.__showMessage( "���ܳ�ȡ���й�ǿ������Ƕ��װ�������ԡ�" )
		#		return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()
		self.__calcCost()

	def onHierogramDrop__( self, pyTarget, pyDropped ) :
		"""
		�Ϸŵ������Ʒ��
		"""
		itemInfo = pyDropped.itemInfo
		if itemInfo.id != csconst.EQUIP_EXTRACT_EXCITEM :
			# "ֻ�ܷ��������������ɽ���ȡ�ɹ�����ߵ�100%���ڸ������䣬Ҳ���ڵ����̳ǹ��򵽡�"
			self.__showMessage( 0x0ea9 )
			return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()

	def onItemRemove__( self, pyIcon ) :
		"""
		�һ��Ƴ���Ʒ
		"""
		if pyIcon.itemInfo is None : return
		self.__lockItem( pyIcon.itemInfo, False )
		pyIcon.update( None )
		self.__calcRate()
		if pyIcon != self.__pyHierogram :
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
		SELF.__cc_triggers[ "EVT_ON_EXTRACT_EQUIP" ] = SELF.__triggerVisible
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


class ExtractItem( Control ) :

	def __init__( self, item, pyBinder ) :
		Control.__init__( self, item, pyBinder )
		self.focus = True
		self.dropFocus = True

		self.__pyIcon = BaseObjectItem( item.item )
		self.__pyIcon.dropFocus = False
		self.__pyIcon.dragFocus = False
		self.__pyIcon.focus = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		�Ϸ���Ʒ
		"""
		Control.onDrop_( self, pyTarget, pyDropped )
		if DragMark.KITBAG_WND == pyDropped.dragMark : 			# �ӱ���������
			self.pyBinder.onStoneDrop__( pyTarget, pyDropped )
			GUIFacade.dehighLightEquipItem( pyDropped.kitbagID, pyDropped.gbIndex )
		return True

	def onRClick_( self, mods ) :
		"""
		�Ҽ�������Ƴ���Ʒ
		"""
		self.pyBinder.onItemRemove__( self )
		return Control.onRClick_( self, mods )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		self.__pyIcon.update( itemInfo )
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.gui, ( 4, 2 ), ItemQAColorMode[ quality ] )
		self.gui.lockIcon.visible = itemInfo is not None and itemInfo.baseItem.isBinded()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def itemInfo( self ) :
		return self.__pyIcon.itemInfo


class ExtractEquipItem( ExtractItem ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		�Ϸ���Ʒ
		"""
		Control.onDrop_( self, pyTarget, pyDropped )
		if DragMark.KITBAG_WND == pyDropped.dragMark : 			# �ӱ���������
			self.pyBinder.onEquipDrop__( pyTarget, pyDropped )
			GUIFacade.dehighLightEquipItem( pyDropped.kitbagID, pyDropped.gbIndex )
		return True

class ExtractHierogramItem( ExtractItem ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		�Ϸ���Ʒ
		"""
		Control.onDrop_( self, pyTarget, pyDropped )
		if DragMark.KITBAG_WND == pyDropped.dragMark : 			# �ӱ���������
			self.pyBinder.onHierogramDrop__( pyTarget, pyDropped )
			GUIFacade.dehighLightEquipItem( pyDropped.kitbagID, pyDropped.gbIndex )
		return True

EQExtractWnd.registerTriggers()