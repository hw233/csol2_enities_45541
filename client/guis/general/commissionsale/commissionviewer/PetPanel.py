# -*- coding: gb18030 -*-

# commission sale pets search panel
# written by ganjinxing 2009-10-19

import csdefine
import csconst
from guis import *
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.TextBox import TextBox
#from guis.controls.ComboBox import ComboBox
#from guis.controls.ComboBox import ComboItem
from guis.controls.ODComboBox import ODComboBox
from guis.controls.StaticText import StaticText
from guis.controls.TabSwitcher import TabSwitcher
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.common.UIStatesTab import HStatesTabEx
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from guis.general.vendwindow.buywindow.EspialWindow import EspialWindow
from TaxisButton import TaxisButtonEx
from Function import Functor

from guis.common.PyGUI import PyGUI
from guis.UIFixer import hfUILoader
from GoodsPanel import ColItem, MoneyCol, ODTextBox
from NPCModelLoader import NPCModelLoader
g_npcModel = NPCModelLoader.instance()
from LabelGather import labelGather


class PetPanel( TabPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/commissionsale/shopsviewer/petPanel.gui" )
		uiFixer.firstLoadFix( panel )
		TabPanel.__init__( self, panel, pyBinder )

		self.__pyCBBoxs = {}										# ��������ComboBox
		self.__pyTaxisBtns = []
		self.__initialize( panel )

		self.__queryDict = {}										# ��¼���β�ѯ����
		self.__currPage = 0
		self.__pyMsgBox = None
		self.__dirCBID = 0
		self.__initCBID1 = 0
		self.__initCBID2 = 0

		self.__triggers = {}
		self.__registerTriggers()

	def __del__( self ) :
		if Debug.output_del_CSPetPanel :
			INFO_MSG( str( self ) )
		PetItem._PET_ITEM = None

	def __initialize( self, panel ) :
		for cName, cGui in panel.frame_inner.header.children :
			if "header_" in cName :
				index = int( cName.split("_")[-1] )
				pyTxBtn = TaxisButtonEx( cGui )
				pyTxBtn.setExStatesMapping( UIState.MODE_R3C1 )
				pyTxBtn.taxisIndex = index
				pyTxBtn.onLClick.bind( self.__onTaxis )
				self.__pyTaxisBtns.append( pyTxBtn )
				labelGather.setPyBgLabel( pyTxBtn, "commissionsale:PetPanel", cName )

		self.__pySearchBtn = HButtonEx( panel.searchBtn )
		self.__pySearchBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.isOffsetText = True
		self.__pySearchBtn.onLClick.bind( self.__onSearch )
		self.__pySearchBtn.enable = False

		self.__pyBuyBtn = HButtonEx( panel.buyBtn )
		self.__pyBuyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBuyBtn.isOffsetText = True
		self.__pyBuyBtn.onLClick.bind( self.__onBuy )
		self.__pyBuyBtn.enable = False

		self.__pyProBtn = HButtonEx( panel.propertyBtn )
		self.__pyProBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyProBtn.isOffsetText = True
		self.__pyProBtn.onLClick.bind( self.__onDetailsPro )
		self.__pyProBtn.enable = False

		self.__pyMoneyBox = MoneyBar( panel.box_money )
		self.__pyMoneyBox.readOnly = True
		self.__updateMoney( 879 )

		self.__pyUpperLimit = TextBox( panel.ibUL.box )			# �ȼ�����
		self.__pyUpperLimit.inputMode = InputMode.INTEGER			# ��������Ϊ��������
		self.__pyUpperLimit.maxLength = 3							# ���������λ��

		self.__pyLowerLimit = TextBox( panel.ibLL.box )			# �ȼ�����
		self.__pyLowerLimit.inputMode = InputMode.INTEGER
		self.__pyLowerLimit.maxLength = 3

		self.__pyDirText = StaticText( panel.dirText )				# ������ʾ����
		self.__pyDirText.text = labelGather.getText( "commissionsale:PetPanel", "stClewCondition" )

		self.__pyTabSwitcher = TabSwitcher( [self.__pyLowerLimit, self.__pyUpperLimit] )

		self.__pyPagesPanel = ODPagesPanel( panel.itemsPanel, panel.idxCtrl )
		self.__pyPagesPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyPagesPanel.onItemSelectChanged.bind( self.__onSelItem )
		self.__pyPagesPanel.pyBtnInc.onLClick.bind( self.__onShowNextPage, True )
		self.__pyPagesPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyPagesPanel.selectable = True
		self.__pyPagesPanel.viewSize = 8, 1							# 9��1��

		self.__initComboBoxs( panel )
		self.__initViewItems()

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySearchBtn, "commissionsale:PetPanel", "btnSearch" )
		labelGather.setPyBgLabel( self.__pyBuyBtn, "commissionsale:PetPanel", "btnBuy" )
		labelGather.setPyBgLabel( self.__pyProBtn, "commissionsale:PetPanel", "btnProperty" )
		labelGather.setLabel( panel.dObj, "commissionsale:PetPanel", "stLVRange" )
		labelGather.setLabel( panel.rObj, "commissionsale:PetPanel", "stSplit" )
		labelGather.setLabel( panel.stObj, "commissionsale:PetPanel", "stOwnMoney" )

	def __initComboBoxs( self, panel ) :
		"""
		��ʼ��ComboBox��ÿ��ComboBox�������ǹ̶��ģ�����ѡ����Ϊ
		��������
		"""
		tempDict = { "cbMR": (
						("cbMR_All", None ),
						("cbMR_Balanced", csdefine.PET_TYPE_BALANCED ),
						("cbMR_Nimble", csdefine.PET_TYPE_SMART ),
						("cbMR_Intellective", csdefine.PET_TYPE_INTELLECT ),
						("cbMR_Potent", csdefine.PET_TYPE_STRENGTH ),
						),
					"cbEra": (
						("cbEra_All", None ),
						("cbEra_Grown", csdefine.PET_HIERARCHY_GROWNUP ),
						("cbEra_Era1", csdefine.PET_HIERARCHY_INFANCY1 ),
						("cbEra_Era2", csdefine.PET_HIERARCHY_INFANCY2 ),
						),
					"cbGender" : (
						("cbGender_All", None ),
						("cbGender_Male", csdefine.GENDER_MALE ),
						("cbGender_Female", csdefine.GENDER_FEMALE ),
						),
					"cbBreed" : (
						("cbBreed_All", None ),
						("cbBreed_Progenitive", csdefine.PET_PROCREATE_STATUS_NONE ),
						("cbBreed_Irreproducible", csdefine.PET_PROCREATE_STATUS_PROCREATED ),
						),
					}
		self.__initCBID1 = BigWorld.callback( 0.2, Functor( self.__addCBGradual, tempDict ) )

	def __addCBGradual( self, tempDict ) :
		if len( tempDict ) == 0 : return
		panel = self.getGui()
		key, items = tempDict.popitem()
		cb = getattr( panel, key )
		pyCBBox = ODComboBox( cb, ODTextBox )
		pyCBBox.onViewItemInitialized.bind( self.__onInitCBXItem )
		pyCBBox.onDrawItem.bind( self.__onDrawCBXItem )
		pyCBBox.ownerDraw = True
		for name, content in items :
			label = labelGather.getText( "commissionsale:PetPanel", name )
			pyCBBox.addItem( ( label, content ) )
		pyCBBox.selIndex = 0
		self.__pyCBBoxs[key] = pyCBBox
		self.__initCBID1 = BigWorld.callback( 0.2, Functor( self.__addCBGradual, tempDict ) )

	def __initViewItems( self ) :
		"""
		���ٳ�ʼ��
		"""
		pyViewItems = self.__pyPagesPanel.pyViewItems
		self.__initCBID2 = BigWorld.callback( 0.05, Functor( self.__addVIGradual, pyViewItems ) )

	def __addVIGradual( self, pyViewItems ) :
		if len( pyViewItems ) == 0 :
			self.__pySearchBtn.enable = True
			self.pyTabPage.enable = True
			self.pyBinder.initGradual()
			return
		pyViewItem = pyViewItems.pop()
		pyItem = PetItem()
		pyViewItem.pyItem = pyItem
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0
		pyItem.refreshItem( pyViewItem )
		self.__initCBID2 = BigWorld.callback( 0.05, Functor( self.__addVIGradual, pyViewItems ) )

	def __registerTriggers( self ) :
		self.__triggers["ON_RECEIVE_COMMISSION_PET_INFO"] = self.__onReceivePetInfo
		self.__triggers["ON_REMOVE_COMMISSION_PET"] = self.__onRemovePet
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )

	def __onSearch( self ) :
		"""
		��ʼ����
		"""
		self.__queryDict = {}
		self.__pyPagesPanel.clearItems()
		lowerLevel = self.__pyLowerLimit.text.strip()
		lowerLevel = ( lowerLevel != "" and ( int( lowerLevel ), ) or ( 0,) )[-1]
		upperLevel = self.__pyUpperLimit.text.strip()
		upperLevel = ( upperLevel != "" and ( int( upperLevel ), ) or ( 0,) )[-1]
		if lowerLevel > upperLevel :
			# "�ȼ����޲��ܵ��ڵȼ����ޣ����������룡"
			self.__showMessage( 0x02c1 )
			return
		if lowerLevel > 0 :
			self.__queryDict[csconst.TISHOU_PET_LOWERLEVEL] = lowerLevel					# �ȼ�����
		if upperLevel > 0 :
			self.__queryDict[csconst.TISHOU_PET_UPPERLEVEL] = upperLevel					# �ȼ�����
		eraLimit = self.__pyCBBoxs["cbEra"].selItem[1]
		if eraLimit is not None :
			self.__queryDict[csconst.TISHOU_PET_ERALIMIT] = eraLimit						# �ڼ�������
		genderLimit = self.__pyCBBoxs["cbGender"].selItem[1]
		if genderLimit is not None :
			self.__queryDict[csconst.TISHOU_PET_GENDERLIMIT] = genderLimit					# �����Ա�����
		metierLimit = self.__pyCBBoxs["cbMR"].selItem[1]
		if metierLimit is not None :
			self.__queryDict[csconst.TISHOU_PET_METIERLIMIT] = metierLimit					# ����ְҵ��������
		breedLimit = self.__pyCBBoxs["cbBreed"].selItem[1]
		if breedLimit is not None :
			self.__queryDict[csconst.TISHOU_PET_BREEDLIMIT] = breedLimit					# ��ֳ״������
		self.__currPage = 0
		self.__notifySearchResult( "begin" )
		BigWorld.player().base.queryTishouPetInfo( self.__currPage, self.__queryDict )

	def __onShowNextPage( self ) :
		pageIndex = self.__pyPagesPanel.pageIndex
		itemCount = ( self.__currPage + 1 ) * csconst.TISHOU_PET_INFO_QUERY_PAGE_SIZE
		passPage = math.ceil( itemCount / float( self.__pyPagesPanel.viewCount ) )
		if pageIndex > passPage - 2 :
			self.__currPage += 1
			BigWorld.player().base.queryTishouPetInfo( self.__currPage, self.__queryDict )

	def __onTaxis( self, pyBtn ) :
		"""
		����
		"""
		taxisIndex = pyBtn.taxisIndex
		taxisReverse = pyBtn.taxisReverse
		self.__pyPagesPanel.separateSort( key = lambda item : item[taxisIndex], reverse = taxisReverse )

	def __onBuy( self ) :
		"""
		����ѡ�еĳ���
		"""
		selItem = self.__pyPagesPanel.selItem
		if selItem is None : return
		player = BigWorld.player()
		cost = selItem[-2][0]
		if cost > player.money :
			# "���Ľ�Ǯ�����Թ���ó��"
			self.__showMessage( 0x02c2 )
			return
		petDBID = selItem[-1].databaseID
		player.cell.buyTSPetFromTishouMgr( petDBID, selItem[7][0] )

	def __onDetailsPro( self ) :
		"""
		�鿴������ϸ����
		"""
		selPet = self.__pyPagesPanel.selItem
		if selPet is None : return
		petEpitome = selPet[-1]
		EspialWindow.instance().show( petEpitome, self.pyTopParent )

	def __updateMoney( self, money ) :
		self.__pyMoneyBox.money = money

	def __onInitItem( self, pyViewItem ) :
		pass

	def __onDrawItem( self, pyViewItem ) :
		pyItem = getattr( pyViewItem, "pyItem", None )
		if pyItem is not None :
			pyItem.refreshItem( pyViewItem )

	def __onInitCBXItem( self, pyViewItem ) :
		"""��ʼ��Combox���б���"""
		staticText = hfUILoader.load( "guis/controls/odlistpanel/itemtext.gui" )
		pyText = StaticText( staticText )
		pyViewItem.addPyChild( pyText )
		pyText.r_left = uiFixer.toFixedX( pyText.r_left )
		pyText.middle = pyViewItem.height / 2
		pyViewItem.pyText = pyText

	def __onDrawCBXItem( self, pyViewItem ) :
		"""�����б���"""
		pyText = pyViewItem.pyText
		listItem = pyViewItem.listItem
		pyText.text = listItem[0]
		pyPanel = pyViewItem.pyPanel
		pyViewItem.pyText.font = pyPanel.font
		if pyViewItem.selected :
			pyViewItem.pyText.color = pyPanel.itemSelectedForeColor			# ѡ��״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemSelectedBackColor				# ѡ��״̬�µı���ɫ
		elif pyViewItem.highlight :
			pyViewItem.pyText.color = pyPanel.itemHighlightForeColor		# ����״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemHighlightBackColor				# ����״̬�µı���ɫ
		else :
			pyViewItem.pyText.color = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor

	def __onSelItem( self, selIndex ) :
		self.__pyProBtn.enable = selIndex != -1
		self.__pyBuyBtn.enable = selIndex != -1

	def __onReceivePetInfo( self, merchantDBID, petDBID, epitome, price, merchantName, shopName ) :
		"""
		���յ������������ĳ�������
		"""
		self.__notifySearchResult( "found" )
		level = epitome.level
		player = BigWorld.player()
		playerLevel = player.level
		playerMoney = player.money
		levelColor = level > ( playerLevel + 5 ) and ( 255,0,0,255 ) or (255,225,255,255)
		priceColor = price > playerMoney and  ( 255,0,0,255 ) or (255,225,255,255)
		petInfo = ( ( epitome.name, (255,255,255,255) ),									# ��������
					EspialWindow._pet_hierarchy[epitome.hierarchy],							# ������
					( EspialWindow._pet_types[epitome.ptype][:-2], (255,255,255,255) ),		# ��������
					( EspialWindow._pet_genders[epitome.gender], (255,255,255,255) ),		# �����Ա�
					( EspialWindow._pet_breeds[epitome.procreated], (255,255,255,255) ),	# ��ֳ���
					( level, levelColor ),													# ����ȼ�
					( merchantName, (255,255,255,255) ),									# ������
					( price, priceColor ),													# �۸�
					epitome,																# �����������
			 	)
		for index, item in enumerate( self.__pyPagesPanel.items ) :							# ����Ƿ��ظ�
			if petDBID == item[-1].databaseID :
				self.__pyPagesPanel.updateItem( index, petInfo )
				print "------------>>> found repeat  pet data!"
				break
		else :
			self.__pyPagesPanel.addItem( petInfo )

	def __onRemovePet( self, petDBID ) :
		for index, item in enumerate( self.__pyPagesPanel.items ) :							# ɾ������
			if petDBID == item[-1].databaseID :
				self.__pyPagesPanel.removeItemOfIndex( index )
				break

	def __showMessage( self, msg ) :
		def query( result ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", MB_OK, query )

	def __notifySearchResult( self, step = "not found" ) :
		if step == "begin" :
			self.__pyDirText.visible = True
			self.__pyDirText.text = labelGather.getText( "commissionsale:PetPanel", "stClewSearching" )
			self.__dirCBID = BigWorld.callback( 2, self.__notifySearchResult )			# 2���δ�յ��κ�������Ĭ��û��ƥ������
		elif step == "found" :
			self.__pyDirText.visible = False
			if self.__dirCBID > 0 :
				BigWorld.cancelCallback( self.__dirCBID )
				self.__dirCBID = 0
		elif step == "not found" :
			self.__pyDirText.visible = True
			self.__pyDirText.text = labelGather.getText( "commissionsale:PetPanel", "stClewNotFound" )
		else :
			self.__pyDirText.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def searchByMerchantName( self, merchantName ) :
		"""
		����ĳ���������еļ��۳���
		"""
		self.__pyPagesPanel.clearItems()
		self.__currPage = 0
		self.__notifySearchResult( "begin" )
		self.__queryDict[csconst.TISHOU_OWNER_NAME] = merchantName
		BigWorld.player().base.queryTishouPetInfo( self.__currPage, self.__queryDict )

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# ��������˻س���
			if self.__pySearchBtn.enable :
				self.__onSearch()
				return True
		return False

	def isReady( self ) :
		return self.__pySearchBtn.enable

	def onEnterWorld( self ) :
		self.__updateMoney( BigWorld.player().money )

	def onRoleMoneyChanged( self, oldValue, newValue ) :
		self.__updateMoney( newValue )

	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def dispose( self ) :
		TabPanel.dispose( self )
		self.__triggers = {}
		BigWorld.cancelCallback( self.__dirCBID )
		BigWorld.cancelCallback( self.__initCBID1 )
		BigWorld.cancelCallback( self.__initCBID2 )


class PetItem( HStatesTabEx ) :

	_PET_ITEM = None

	def __init__( self ) :
		if PetItem._PET_ITEM is None :
			PetItem._PET_ITEM = GUI.load( "guis/general/commissionsale/shopsviewer/petitem.gui" )
			uiFixer.firstLoadFix( PetItem._PET_ITEM )
		gui = util.copyGuiTree( PetItem._PET_ITEM )
		HStatesTabEx.__init__( self, gui )
		self.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyColItems = []
		self.__initialize( gui )

	def __initialize( self, gui ) :
		for i in xrange( 1, 8 ) :
			colItem = getattr( gui, "col_" + str( i ) )
			pyCItem = ColItem( colItem )
			self.__pyColItems.append( pyCItem )
		colItem = getattr( gui, "col_8" )
		pyCItem = MoneyCol( colItem )
		self.__pyColItems.append( pyCItem )

		self.__pyIcon = PetIcon( gui.item )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refreshItem( self, pyViewItem ) :
		rowInfo = pyViewItem.pageItem
		if rowInfo is None :
			rowInfo = ( ( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( 0, (255,255,255,255) ),
						None,
						)
			pyViewItem.focus = False
		else :
			pyViewItem.focus = True
		for pyCItem, info in zip( self.__pyColItems, rowInfo ) :
			pyCItem.update( info )
		petEpitome = rowInfo[-1]
		self.__pyIcon.update( petEpitome )
		if petEpitome is None :
			self.setStateView_( UIState.COMMON )
		elif pyViewItem.selected :
			self.setStateView_( UIState.PRESSED )
		elif pyViewItem.highlight :
			self.setStateView_( UIState.HIGHLIGHT )
		else :
			self.setStateView_( UIState.COMMON )


class PetIcon( PyGUI ) :

	def __init__( self, item ) :
		PyGUI.__init__( self, item )
		self.__icon = item.icon


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, petEpitome ) :
		if petEpitome is None :
			self.materialFX = "COLOUR_EFF"
			self.__icon.textureName = ""
		else :
			self.materialFX = "BLEND"
			modelNumber = petEpitome.modelNumber
			self.__icon.textureName = g_npcModel.getHeadTexture( modelNumber )