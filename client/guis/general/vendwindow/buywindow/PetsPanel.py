# -*- coding: gb18030 -*-
#
# $Id: VendWindow.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $

from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.UIStatesTab import HStatesTabEx
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from LabelGather import labelGather
from EspialWindow import EspialWindow
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()
SPACE = PL_Space.getSource
import csdefine


class BasePetsPanel( TabPanel ) :

	def __init__( self, tabPanel, pyBinder = None ):
		TabPanel.__init__( self, tabPanel, pyBinder )

		self.pyMsgBox_ = None
		self.sortHandlerMap_ = {}
		self.triggers_ = {}
		self.registerTriggers_()
		self.initialize_( tabPanel )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, tabPanel ) :
		self.pyPagesPanel_ = ODPagesPanel( tabPanel.clipPanel, tabPanel.ctrlBar )
		self.pyPagesPanel_.onViewItemInitialized.bind( self.initItem_ )
		self.pyPagesPanel_.onItemSelectChanged.bind( self.onItemSelected_ )
		self.pyPagesPanel_.onItemRClick.bind( self.onItemRClick_ )
		self.pyPagesPanel_.onDrawItem.bind( self.drawItem_ )
		self.pyPagesPanel_.viewSize = ( 6, 1 )
		self.pyPagesPanel_.selectable = True

		self.pyExamineBtn_ = HButtonEx( tabPanel.attrBtn ) 						# 宠物属性查看
		self.pyExamineBtn_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyExamineBtn_.enable = False
		self.pyExamineBtn_.onLClick.bind( self.checkDetail_ )

		self.pyBuyBtn_ = HButtonEx( tabPanel.buyBtn ) 							# 购买按钮
		self.pyBuyBtn_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBuyBtn_.enable = False
		self.pyBuyBtn_.onLClick.bind( self.buyPet_ )

		self.pyStNumber_ = StaticText( tabPanel.stNumber )
		self.pyStNumber_.text = "0"

		self.initSortBox_( tabPanel.sortComBox )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( tabPanel.sortText, "vendwindow:BasePetsPanel", "stSortText" )
		labelGather.setLabel( tabPanel.numberText, "vendwindow:BasePetsPanel", "stNumberText" )
		labelGather.setPyBgLabel( self.pyExamineBtn_, "vendwindow:BasePetsPanel", "btnAttr" )
		labelGather.setPyBgLabel( self.pyBuyBtn_, "vendwindow:BasePetsPanel", "btnBuy" )

	def initSortBox_( self, comboBox ) :
		"""
		初始化排序控件
		"""
		tempMap = (
					( 0, "price", self.sortByPrice_ ),
					( 1, "level", self.sortByLevel_ ),
					( 2, "type", self.sortByType_ ),
					)
		self.sortBox_ = ODComboBox( comboBox )
		self.sortBox_.onItemLClick.bind( self.onSort_ )
		self.sortBox_.pyBox.text = labelGather.getText( "vendwindow:BasePetsPanel", "option" )
		for index, sortText, handler in tempMap :
			self.sortBox_.addItem( labelGather.getText( "vendwindow:BasePetsPanel", sortText ) )
			self.sortHandlerMap_[index] = handler

	def registerTriggers_( self ) :
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def initItem_( self, pyViewItem ) :
		"""
		"""
		pyPetItem = BuyPetItem()
		pyViewItem.pyPetItem = pyPetItem
		pyViewItem.addPyChild( pyPetItem )
		pyPetItem.left = 4
		pyPetItem.top = 0

	def drawItem_( self, pyViewItem ) :
		"""
		"""
		pyPetItem = pyViewItem.pyPetItem
		pyPetItem.update( pyViewItem )

	def onItemRClick_( self, pyViewItem ) :
		pass

	def onItemSelected_( self, index ) :
		itemSelected = self.pyPagesPanel_.selItem is not None
		self.pyExamineBtn_.enable = itemSelected
		self.pyBuyBtn_.enable = itemSelected

	def checkDetail_( self ) :
		selPet = self.pyPagesPanel_.selItem
		if selPet is None : return
		EspialWindow.instance().show( selPet, self.pyTopParent )

	def buyPet_( self ) :
		pass

	def showMsg_( self, msg, style = MB_OK, callback = lambda res : True ) :
		def query( result ) :
			self.pyMsgBox_ = None
			callback( result )
		if self.pyMsgBox_ is not None :
			self.pyMsgBox_.hide()
		self.pyMsgBox_ = showMessage( msg, "", style, query, self, Define.GST_IN_WORLD )


	# -------------------------------------------------
	# sort function
	# -------------------------------------------------
	def onSort_( self, index ) :
		handler = self.sortHandlerMap_[ index ]
		self.pyPagesPanel_.sort( key = handler )

	def sortByPrice_( self, epitome ) :
		"""
		按价格排序
		"""
		return epitome.vendSellPrice

	def sortByLevel_( self, epitome ) :
		"""
		按照等级排序
		"""
		return epitome.level

	def sortByMetier_( self, epitome ) :
		"""
		按照职业排序
		"""
		return epitome.ptype

	def sortByType_( self, epitome ):
		"""
		按类型排序；同价格按等级从高到低排序；同价格、等级，按id排序。
		"""
		return epitome.character

	# -------------------------------------------------
	# pet operation
	# -------------------------------------------------
	def onRemovePet_( self, petDBID ) :
		for index, epitome in enumerate( self.pyPagesPanel_.items ) :
			if epitome.databaseID == petDBID :
				self.pyPagesPanel_.removeItemOfIndex( index )
				break
		self.pyStNumber_.text = str( self.pyPagesPanel_.itemCount )

	def onUpdatePetPrice_( self, petDBID, price ) :
		"""
		宠物价格更新
		"""
		for index, epitome in enumerate( self.pyPagesPanel_.items ) :
			if epitome.databaseID == petDBID :
				epitome.vendSellPrice = price
				self.pyPagesPanel_.updateItem( index, epitome )
				break
		else :
			print "-------->>> Can't find pet by databaseID", petDBID


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		"""
		self.triggers_[eventMacro]( *args )

	def reset( self ) :
		self.pyPagesPanel_.clearItems()
		self.pyStNumber_.text = "0"



class BuyPetsPanel( BasePetsPanel ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ):
		self.triggers_["EVT_ON_VEND_RECEIVE_VEND_PETEPITOMES"] = self.__onReceivePets
		self.triggers_["EVT_ON_VEND_PET_SELLED"] = self.onRemovePet_ 			# 卖出宠物回调
		BasePetsPanel.registerTriggers_( self )

	def buyPet_( self ) :
		selPet = self.pyPagesPanel_.selItem
		if selPet is None : return
		shopman = self.pyBinder.trapEntity
		if shopman is not None :
			BigWorld.player().vend_buyPet( selPet.databaseID, shopman.id )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onReceivePets( self, epitomes ) :
		"""
		接收到多个宠物数据
		"""
		self.pyPagesPanel_.clearItems()
		self.pyPagesPanel_.addItems( epitomes )
		self.pyStNumber_.text = str( self.pyPagesPanel_.itemCount )



class BuyPetItem( HStatesTabEx ) :

	_PET_TYPE = {
					csdefine.PET_CHARACTER_SUREFOOTED	: labelGather.getText( "vendwindow:BuyPetItem", "surefooted" ),
					csdefine.PET_CHARACTER_CLOVER		: labelGather.getText( "vendwindow:BuyPetItem", "intelligent" ),
					csdefine.PET_CHARACTER_CANNILY		: labelGather.getText( "vendwindow:BuyPetItem", "cannily" ),
					csdefine.PET_CHARACTER_BRAVE		: labelGather.getText( "vendwindow:BuyPetItem", "brave" ),
					csdefine.PET_CHARACTER_LIVELY		: labelGather.getText( "vendwindow:BuyPetItem", "vivacious" )
				}
	_PET_GENDER = {
					csdefine.GENDER_MALE	: labelGather.getText( "vendwindow:BuyPetItem", "male" ),
					csdefine.GENDER_FEMALE	: labelGather.getText( "vendwindow:BuyPetItem", "female" )
				  }
	_PET_BREED = {
					csdefine.PET_PROCREATE_STATUS_NONE			: labelGather.getText( "vendwindow:BuyPetItem", "progenitive" ),
					csdefine.PET_PROCREATE_STATUS_PROCREATING	: labelGather.getText( "vendwindow:BuyPetItem", "procreating" ),
					csdefine.PET_PROCREATE_STATUS_PROCREATED	: labelGather.getText( "vendwindow:BuyPetItem", "irreproducible" )
				 }
	__ITEM = None

	def __init__( self ) :
		if BuyPetItem.__ITEM is None :
			BuyPetItem.__ITEM = GUI.load( "guis/general/vendwindow/buywindow/buypetitem.gui" )
			uiFixer.firstLoadFix( BuyPetItem.__ITEM )
		item = util.copyGuiTree( BuyPetItem.__ITEM )
		HStatesTabEx.__init__( self, item )
		self.setExStatesMapping( UIState.MODE_R2C1 )

		self.__pyPetHead = PyGUI( item.petHead ) 				# 宠物头像
		self.__pyPetHead.texture = ""
		
		self.__headColor = item.headColor
		self.__headColor.visible = 0

		self.__pyStLevel = StaticText( item.stLevel ) 			# 宠物等级
		self.__pyStLevel.text = ""

		self.__pyRtBaseAttr = CSRichText( item.rtBase ) 			# 基本属性
		self.__pyRtBaseAttr.align = "L"
		self.__pyRtBaseAttr.text = ""

		self.__pyRtExpense = CSRichText( item.rtExpense ) 		# 价钱
		self.__pyRtExpense.foreColor = ( 16, 197, 165, 255 )
		self.__pyRtExpense.align = "R"
		self.__pyRtExpense.text = ""


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, pyViewItem ) :
		epitome = pyViewItem.pageItem
		if epitome is None :
			pyViewItem.focus = False
			self.__pyStLevel.text = ""
			self.__pyRtExpense.text = ""
			self.__pyRtBaseAttr.text = ""
			self.__pyPetHead.texture = ""
			self.__headColor.visible = 0
			self.gui.headBg.materialFX = "COLOUR_EFF"
			self.gui.levelBg.materialFX = "COLOUR_EFF"
		else :
			pyViewItem.focus = True
			self.__pyStLevel.text = str( epitome.level )
			petName = PL_Font.getSource( epitome.name.ljust( 15 ), \
												fc = ( 236, 218, 157, 255 ) )					# 宠物名字
			baseAttrStr = self._PET_GENDER[ epitome.gender ].ljust( 5 )
			hierarchy = epitome.hierarchy
			baseColor = ( 255, 255, 255, 255 )
			if hierarchy == csdefine.PET_HIERARCHY_GROWNUP :
				baseAttrStr += labelGather.getText("vendwindow:BuyPetItem", "grownPet" ).ljust( 9 )
			elif hierarchy == csdefine.PET_HIERARCHY_INFANCY1 :
				baseAttrStr += labelGather.getText( "vendwindow:BuyPetItem", "generation1" ).ljust( 9 )
				baseColor = ( 0, 128, 255, 255 )
			else :
				baseAttrStr += labelGather.getText( "vendwindow:BuyPetItem", "generation2" ).ljust( 9 )
				baseColor = ( 254, 163, 8, 255 )
			baseAttrStr += self._PET_BREED[ epitome.procreated ]								# 繁殖状况
			baseAttrStr = PL_Font.getSource( baseAttrStr, fc = baseColor )
			self.__pyRtBaseAttr.text = petName + baseAttrStr									# 设置基础信息
			priceColor = epitome.vendSellPrice > BigWorld.player().money and ( 255,0,0,255 ) or ( 16, 197, 165, 255 )
			priceStr = utils.currencyToViewText( epitome.vendSellPrice )
			self.__pyRtExpense.text = PL_Align.getSource( lineFlat = "M" ) + PL_Font.getSource( priceStr, fc = priceColor ) 	# 售价
			self.__pyPetHead.texture = g_npcmodel.getHeadTexture( epitome.modelNumber )			# 头像
			self.gui.headBg.materialFX = "BLEND"
			self.gui.levelBg.materialFX = "BLEND"
			player = BigWorld.player()
			if epitome.takeLevel> player.level:
				self.__headColor.visible = 1
			else:
				self.__headColor.visible = 0
		if pyViewItem.selected or pyViewItem.highlight :
			self.setStateView_( UIState.HIGHLIGHT )
		else :
			self.setStateView_( UIState.COMMON )
