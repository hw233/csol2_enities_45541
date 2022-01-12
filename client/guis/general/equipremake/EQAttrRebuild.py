# -*- coding: gb18030 -*-

# װ��������������
# by gjx 2010-08-18

from guis import *
from guis.UIFixer import hfUILoader
from guis.common.TrapWindow import FixedTrapWindow
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.ODListPanel import ODListPanel, ViewItem
from EQExtractWnd import ExtractEquipItem as EquipItem
from guis.general.kitbag.Animation import Animation

import re
import items
import csstring
import ItemTypeEnum
import GUIFacade
from LabelGather import labelGather
from cscollections import MapList
from guis.MLUIDefine import QAColorText
from AbstractTemplates import Singleton
from items.EquipEffectLoader import EquipEffectLoader
from config.client.msgboxtexts import Datas as mbmsgs
from config.item.EquipAttrRebuildItem import Datas as pearlData
g_equipEffect = EquipEffectLoader.instance()


class AttrInfo( object ) :

	__slots__ = ( "value", "effectID", "effectType", "improvable" )

	def __init__( self, equip, value, effectID, effectType ) :
		self.value = value
		self.effectID = effectID
		self.effectType = effectType
		maxValue = g_equipEffect.getEffectMax( equip, effectID )
		print ">>>value:",value
		print ">>>maxValue:",maxValue
		print ">>>effectID:",effectID
		print ">>>eequipID:",equip.id		
		self.improvable = value < maxValue 


class EQAttrRebuild( Singleton, FixedTrapWindow ) :

	__cc_triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/equipremake/attr_rebuild_wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		FixedTrapWindow.__init__( self, wnd )

		self.__triggers = {}
		self.__pyMsgBox = None

		self.__initialize( wnd )
		self.__registerTriggers()

		# ������ʼ��
		succeedWnd = GUI.load( "guis/general/kitbag/casketwindow/succeed.gui" )
		self.__succeedAnimGui = Animation( succeedWnd )
		self.__succeedAnimGui.initAnimation( "succeedWnd",1.3 )

		self.addToMgr()
		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )			# ��ӵ�MutexGroup.TRADE1������


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :

		class AttrPanel( ODListPanel ) :
			def getViewItem_( SELF ) :
				return AttrItem( SELF )

		self.__pyAttrPanel = AttrPanel( wnd.panel.clipPanel, wnd.panel.sbar )
		self.__pyAttrPanel.itemHeight = 30
		self.__pyAttrPanel.ownerDraw = True
		self.__pyAttrPanel.autoSelect = False
		self.__pyAttrPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyAttrPanel.onItemSelectChanged.bind( self.__onAttrSelected )
		self.__pyAttrPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyAttrPanel.addItems( [False]*7 )				# ��ʼ��7��Ԫ��

		self.__pyEquip = EquipItem( wnd.equip, self )
		self.__pyEquip.update( None )

		self.__pyBtnOk = HButtonEx( wnd.btnOK )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onRebuild )
		self.__pyBtnOk.enable = False

		self.__pyBtnHide = HButtonEx( wnd.btnHide )
		self.__pyBtnHide.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.hide )

		self.__pySTClew = StaticText( wnd.stClew )
		self.__pySTClew.text = labelGather.getText( "EquipRemake:rebuild", "stClew1" )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnOk, "EquipRemake:rebuild", "btnOk" )
		labelGather.setPyBgLabel( self.__pyBtnHide, "EquipRemake:rebuild", "btnHide" )
		labelGather.setLabel( wnd.lbTitle, "EquipRemake:rebuild", "lbTitle" )

	def __onInitItem( self, pyAttrItem ) :
		pyAttrItem.left = 0

	def __onDrawItem( self, pyAttrItem ) :
		pyAttrItem.update()

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

	# -------------------------------------------------
	def __onAttrSelected( self, index ) :
		"""
		ѡ����ĳ������
		"""
		attrInfo = self.__pyAttrPanel.selItem
		clewText = ""
		textColor = 255,255,255,255
		btnEnable = False
		args = ()
		if not attrInfo :
			if self.__pyEquip.itemInfo :
				clewText = "stClew1"
			else :
				clewText = "stClew2"
		elif attrInfo.improvable :
			equip = self.__pyEquip.itemInfo
			pearlId = pearlData[ equip.level ]
			pearl = items.instance().createDynamicItem( pearlId )
			args = ( pearl.name(), )
			clewText = "stClew3"
			textColor = 0,255,0,255
			btnEnable = True
		else :
			clewText = "stClew4"
			textColor = 255,0,0,255
		self.__pySTClew.text = labelGather.getText( "EquipRemake:rebuild", clewText, *args )
		self.__pySTClew.color = textColor
		self.__pyBtnOk.enable = btnEnable

	def __onRebuild( self ) :
		"""
		ȷ������
		"""
		attrInfo = self.__pyAttrPanel.selItem
		if not attrInfo : return
		equip = self.__pyEquip.itemInfo
		if equip is None : return
		BigWorld.player().cell.EquipAttrRebuild( equip.uid, attrInfo.effectType, attrInfo.effectID )

	# -------------------------------------------------
	def __onKitbagUpdateItem( self, itemInfo ) :
		"""
		����������Ʒ
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			pyItem.update( itemInfo )
			attributes = self.__extractAttributes()
			self.__updateAttrs( attributes.values() )

		attrInfo = self.__pyAttrPanel.selItem
		clewText = ""
		textColor = 255,255,255,255
		btnEnable = False
		args = ()
		if not attrInfo :
			if self.__pyEquip.itemInfo :
				clewText = "stClew1"
			else :
				clewText = "stClew2"
		elif attrInfo.improvable :
			equip = self.__pyEquip.itemInfo
			pearlId = pearlData[ equip.level ]
			pearl = items.instance().createDynamicItem( pearlId )
			args = ( pearl.name(), )
			clewText = "stClew3"
			textColor = 0,255,0,255
			btnEnable = True
		else :
			clewText = "stClew4"
			textColor = 255,0,0,255
		self.__pySTClew.text = labelGather.getText( "EquipRemake:rebuild", clewText, *args )
		self.__pySTClew.color = textColor
		self.__pyBtnOk.enable = btnEnable

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""
		�����Ƴ���Ʒ
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			self.__lockItem( itemInfo, False )
			pyItem.update( None )
			self.__updateAttrs( [] )
			self.__pyAttrPanel.selIndex = -1

	def __getPyItemByUID( self, uid ) :
		"""
		����UID���ҽ������Ƿ��и���Ʒ
		"""
		equip = self.__pyEquip.itemInfo
		if equip and equip.uid == uid : return self.__pyEquip

	def __extractAttributes( self ) :
		"""
		�ӷ����װ���г�ȡ�����п���������
		"""
		equipInfo = self.__pyEquip.itemInfo
		if equipInfo is None : return					# û�з���װ��
		attributes = MapList()
		equip = equipInfo.baseItem
		extraEffect = equip.getExtraEffect()			# һ�㸽������
		for effectID, value in extraEffect.iteritems() :
			attrInfo = AttrInfo( equip, value, effectID, "eq_extraEffect" )
			attributes[ effectID ] = attrInfo

		suitEffect = equip.query( "eq_suitEffect", {} )	# ��װ����
		for effectID, value in suitEffect.iteritems() :
			attrInfo = AttrInfo( equip, value, effectID, "eq_suitEffect" )
			attributes[ effectID ] = attrInfo

		createEffect = equip.getCreateEffect()			# ��ע����
		for effectID, value in createEffect :
			if effectID == 0 : continue
			attrInfo = AttrInfo( equip, value, effectID, "eq_createEffect" )
			attributes[ effectID ] = attrInfo

		return attributes

	# -------------------------------------------------
	def __lockItems( self, locked ) :
		"""
		��/�رս���ʱ�ı䱳���ж�Ӧ��Ʒ����ɫ
		"""
		equip = self.__pyEquip.itemInfo
		if equip is not None :
			self.__lockItem( equip, locked )

	def __lockItem( self, itemInfo, locked ) :
		"""
		֪ͨ��������/����ĳ����Ʒ
		"""
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )

	def __updateAttrs( self, attrs ) :
		"""�������Ը���"""
		for idx in xrange( self.__pyAttrPanel.itemCount ) :
			if idx < len( attrs ) :
				self.__pyAttrPanel.updateItem( idx, attrs[idx] )
			else :
				self.__pyAttrPanel.updateItem( idx, False )

	# -------------------------------------------------
	def __reset( self ) :
		pass

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
	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		�Ϸŵ�װ����
		"""
		itemInfo = pyDropped.itemInfo
		if not ( itemInfo.isEquip and itemInfo.level >= 30 \
			and itemInfo.quality >= ItemTypeEnum.CQT_GREEN ) :
				# "�����30�����ϵ���ɫװ����"
				msg = mbmsgs[0x0eb2] % ( 30, QAColorText[ ItemTypeEnum.CQT_GREEN ] )
				self.__showMessage( msg )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		attributes = self.__extractAttributes()
		self.__updateAttrs( attributes.values() )
		self.__pyAttrPanel.selIndex = -1
		self.__onAttrSelected( -1 )
		self.__lockItem( itemInfo, True )

	def onItemRemove__( self, pyItem ) :
		"""
		�һ��Ƴ���Ʒ
		"""
		if pyItem.itemInfo is None : return
		self.__lockItem( pyItem.itemInfo, False )
		pyItem.update( None )
		self.__updateAttrs( [] )
		self.__pyAttrPanel.selIndex = -1
		self.__onAttrSelected( -1 )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, trapEntityID ) :
		self.setTrappedEntID( trapEntityID )
		FixedTrapWindow.show( self )
		self.__lockItems( True )
		self.__pyAttrPanel.selIndex = -1

	def hide( self ) :
		FixedTrapWindow.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.__lockItems( False )
		self.dispose()
		self.__unregisterTriggers()
		self.__class__.releaseInst()

	def onLeaveWorld( self ) :
		FixedTrapWindow.onLeaveWorld( self )
		self.hide()

	def onAttrReBuildSuccess( self ):
		"""
		���������ɹ�
		"""
		left = self.left + 65.0
		top = self.top + 50.0
		self.__succeedAnimGui.playAnimation( ( left, top ), self )

	@classmethod
	def registerTriggers( SELF ) :
		SELF.__cc_triggers[ "EVT_ON_EQUIP_ATTR_REBUILD" ] = SELF.__triggerVisible
		SELF.__cc_triggers["EVT_ON_EQUIP_ATTR_REBUILD_SUCCESS"] = SELF.__onReBuildSuccess
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

	@classmethod
	def __onReBuildSuccess( SELF ):
		SELF.inst.onAttrReBuildSuccess( )


class AttrItem( ViewItem ) :

	__cc_prefix = {
		"eq_extraEffect"	: "",
		"eq_suitEffect"		: labelGather.getText( "EquipRemake:rebuild", "prefix1" ),
		"eq_createEffect"	: labelGather.getText( "EquipRemake:rebuild", "prefix2" ),
	}

	def __init__( self, pyPanel ) :
		gui = hfUILoader.load( "guis/general/equipremake/attritem.gui" )
		ViewItem.__init__( self, pyPanel, gui )
		self.__pyText = StaticText( gui.lbText )
		self.__fullText = ""

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __formatText( self, prefix, efName, efValue ) :
		"""
		��ʽ�������ı�
		"""
		fullText = cprsText = "%s%s%s" % ( prefix, efName, efValue )
		if len( fullText ) <= 20 : return fullText, cprsText
		cutLength = len( fullText ) - 20
		cutLength = cutLength / 2 + cutLength % 2 + 2					# ת��ΪҪ��ȥ�������ַ�������(+2��Ϊʡ�Ժ�Ԥ����)
		valueSRE = re.match( "[ \+\-\.%\d]+", efValue )
		if valueSRE and valueSRE.end() == len( efValue ) :
			cprsText = prefix + efName
			cprsText = csstring.toWideString( cprsText )				# ��ת��Ϊ���ַ������ٽ��н�ȡ�������Ͳ�
			cprsText = csstring.toString( cprsText[:-cutLength] )		# �ᵼ��ĳ�������ַ�����ȥһ��Ӷ���������
			cprsText = "%s%s%s" % ( cprsText, "...", efValue )
		else :
			cprsText = csstring.toWideString( cprsText )				# ��ת��Ϊ���ַ������ٽ��н�ȡ�������Ͳ�
			cprsText = csstring.toString( cprsText[:-cutLength] )		# �ᵼ��ĳ�������ַ�����ȥһ��Ӷ���������
			cprsText = "%s%s" % ( cprsText, "..." )
		return fullText, cprsText


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		ViewItem.onMouseEnter_( self )
		if self.__fullText != self.__pyText.text :
			toolbox.infoTip.showToolTips( self, self.__fullText )

	def onMouseLeave_( self ) :
		ViewItem.onMouseLeave_( self )
		toolbox.infoTip.hide()

	def onDisable_( self ) :
		ViewItem.onDisable_( self )
		self.materialFX = "BLEND"
		util.setGuiState( self.gui, UIState.MODE_R4C1, UIState.ST_R4C1 )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self ) :
		"""
		���ݴ���������Ϣ�ж���װ�������Ƿ�������
		"""
		attrInfo = self.listItem
		if not attrInfo :
			self.enable = False
			self.__pyText.text = ""
			self.__fullText = ""
		else :
			self.enable = True
			uiState = UIState.ST_R1C1
			if self.selected :
				uiState = UIState.ST_R2C1
			elif attrInfo.improvable :
				uiState = UIState.ST_R3C1
			util.setGuiState( self.gui, UIState.MODE_R4C1, uiState )
			prefix = self.__cc_prefix[ attrInfo.effectType ]
			effectInst = g_equipEffect.getEffect( attrInfo.effectID )
			efName, efValue = effectInst.descriptionList( attrInfo.value )
			self.__fullText, cprsText = self.__formatText( prefix, efName, efValue )
			self.__pyText.text = cprsText


EQAttrRebuild.registerTriggers()