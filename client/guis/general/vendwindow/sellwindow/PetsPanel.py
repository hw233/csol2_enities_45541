# -*- coding: gb18030 -*-
#
# $Id: PetsPanel.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $
# rewritten by ganjinxing 2010-01-21

from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StatusItem import StatusItem
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ODListPanel import ViewItem
from guis.controls.ODListPanel import ODListPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from config.client.msgboxtexts import Datas as mbmsgs
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()
from LabelGather import labelGather
import csdefine
import csconst
import csstatus


class BasePetPanel( TabPanel ) :

	def __init__( self, panel, pyBinder ) :
		TabPanel.__init__( self, panel, pyBinder )

		self.triggers_ = {}
		self.registerTriggers_()
		self.initialize_( panel )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_PCG_ADD_PET"]		= self.onRoleGainPet_ 		# 角色得到宠物
		self.triggers_["EVT_ON_PCG_REMOVE_PET"] 	= self.onRoleLosePet_ 		# 角色失去宠物
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )

	def initialize_( self, panel ) :
		self.pyUpBtn_ = HButtonEx( panel.upBtn ) 									# 宠物上架按钮
		self.pyUpBtn_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyUpBtn_.enable = False
		self.pyUpBtn_.onLClick.bind( self.onPetUp_ )

		self.pyDownBtn_ = HButtonEx( panel.downBtn ) 								# 宠物下架按钮
		self.pyDownBtn_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyDownBtn_.enable = False
		self.pyDownBtn_.onLClick.bind( self.onPetDown_ )

		self.pyMyPanel_ = ODListPanel( panel.myPanel.clipPanel, panel.myPanel.sbar )
		self.pyMyPanel_.onItemSelectChanged.bind( self.onMyPetSelected_ )
		self.pyMyPanel_.onViewItemInitialized.bind( self.onInitMyPetItem_ )
		self.pyMyPanel_.onDrawItem.bind( self.onMyPetDraw_ )
		self.pyMyPanel_.autoSelect = False
		self.pyMyPanel_.itemHeight = 46
		self.pyMyPanel_.ownerDraw = True										# 开启自定义绘制

		self.pySellPanel_ = ODListPanel( panel.sellPanel.clipPanel, panel.sellPanel.sbar )
		self.pySellPanel_.onItemSelectChanged.bind( self.onSellPetSelected_ )
		self.pySellPanel_.onViewItemInitialized.bind( self.onInitSellPetItem_ )
		self.pySellPanel_.onItemMouseEnter.bind( self.onSellPetMouseEnter_ )
		self.pySellPanel_.onItemMouseLeave.bind( self.onSellPetMouseLeave_ )
		self.pySellPanel_.onDrawItem.bind( self.onSellPetDraw_ )
		self.pySellPanel_.autoSelect = False
		self.pySellPanel_.itemHeight = 46
		self.pySellPanel_.ownerDraw = True										# 开启自定义绘制

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.sellPanel.lbTitle, "vendwindow:BasePetPanel", "stSelling" )
		labelGather.setLabel( panel.myPanel.lbTitle, "vendwindow:BasePetPanel", "stRemain" )
		labelGather.setPyBgLabel( self.pyUpBtn_, "vendwindow:BasePetPanel", "btnUp" )
		labelGather.setPyBgLabel( self.pyDownBtn_, "vendwindow:BasePetPanel", "btnDown" )

	def onPetUp_( self ) :
		pass

	def onPetDown_( self ) :
		pass

	def getMyPetItem_( self ) :
		return MyPetItem()

	def getSellPetItem_( self ) :
		return SellPetItem()

	def onInitSellPetItem_( self, pyViewItem ) :
		pySellPet = self.getSellPetItem_()
		pyViewItem.pyPetItem = pySellPet
		pyViewItem.addPyChild( pySellPet )
		pySellPet.pos = 0, 1

	def onInitMyPetItem_( self, pyViewItem ) :
		pyMyPet = self.getMyPetItem_()
		pyViewItem.pyPetItem = pyMyPet
		pyViewItem.addPyChild( pyMyPet )
		pyMyPet.pos = 0, 0

	def onMyPetSelected_( self, index ) :
		self.pyUpBtn_.enable = index > -1

	def onSellPetSelected_( slef, index ) :
		isSelected = index > -1
		self.pyDownBtn_.enable = isSelected
		self.pyBinder.enableChangePriceBtn()

	def onMyPetDraw_( self, pyViewItem ) :
		pyMyPet = pyViewItem.pyPetItem
		pyMyPet.update( pyViewItem )

	def onSellPetDraw_( self, pyViewItem ) :
		pySellPet = pyViewItem.pyPetItem
		pySellPet.update( pyViewItem )

	def onSellPetMouseEnter_( self, pyViewItem ) :
		sellPet = pyViewItem.listItem
		costStr = utils.currencyToViewText( sellPet.rolePrice )
		hierText = ""
		hierarchy = sellPet.hierarchy
		if hierarchy == csdefine.PET_HIERARCHY_GROWNUP : 							# 成年宠物
			hierText = labelGather.getText( "vendwindow:BasePetPanel", "grownPet" )
		elif hierarchy == csdefine.PET_HIERARCHY_INFANCY1 :							# 一代宝宝
			hierText = PL_Font.getSource( labelGather.getText( "vendwindow:BasePetPanel", "generation1" ),
										fc = ( 5, 193, 255, 255 ) )
		else: 																		# 二代宝宝
			hierText = PL_Font.getSource( labelGather.getText( "vendwindow:BasePetPanel", "generation2" ),
										fc = ( 254, 163, 8, 255 ) )
		dsp = sellPet.name + "@B" + hierText + \
		"@B%s@A{M}"%labelGather.getText( "vendwindow:BasePetPanel", "price" ) + \
		costStr + "@A{L}"
		toolbox.infoTip.showItemTips( self, dsp )

	def onSellPetMouseLeave_( self, pyViewItem ) :
		toolbox.infoTip.hide()

	def onRoleGainPet_( self, epitome ) :
		self.pyMyPanel_.addItem( epitome )

	def onRoleLosePet_( self, petDBID ) :
		for index, epitome in enumerate( self.pyMyPanel_.items ) :
			if epitome.databaseID == petDBID :
				self.pyMyPanel_.removeItemOfIndex( index )
				break


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def canChangePrice( self ) :
		return self.pySellPanel_.selItem is not None

	def changeItemPrice( self ) :
		pass

	def getTotalPrice( self ) :
		totalPrice = 0
		for epitome in self.pySellPanel_.items :
			totalPrice += epitome.rolePrice
		return totalPrice

	def onEvent( self, evtMacro, *args ) :
		self.triggers_[evtMacro]( *args )

	def onParentShow( self ) :
		pass

	def onParentHide( self ) :
		pass

	def reset( self ) :
		self.pySellPanel_.clearItems()
		self.pyMyPanel_.clearItems()


class VendPetPanel( BasePetPanel ) :

	def __init__( self, panel, pyBinder ) :
		BasePetPanel.__init__( self, panel, pyBinder )
		self.__pyMsgBox = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __showMessage( self, msg ) :
		def query( result ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", MB_OK, query, None, Define.GST_IN_WORLD )

	def __checkOperation( self ) :
		isVendState = BigWorld.player().state == csdefine.ENTITY_STATE_VEND
		if isVendState :
			# "请先停止摆摊再进行该操作！"
			self.__showMessage( 0x0aa1 )
			return False
		return True


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_VEND_PET_SELLED"] 	= self.onRoleLosePet_ 		# 角色失去宠物
		BasePetPanel.registerTriggers_( self )

	def onPetUp_( self ) :
		if not self.__checkOperation() : return
		selPet = self.pyMyPanel_.selItem
		if selPet is None : return
		if selPet.isBinded :
			BigWorld.player().statusMessage( csstatus.PET_HAD_BEEN_BIND )
			return
		isVended = getattr( selPet, "isVended", False )
		if isVended :
			# "该宠物已是待售宠物！"
			showAutoHideMessage( 3.0, 0x0de1, mbmsgs[0x0c22], pyOwner = self )
		else :
			def addSellPet( result, price ):
				if result == DialogResult.OK :
					if price <= 0:
						# "该宠物还没有定价!"
						showAutoHideMessage( 3.0, 0x0de2, mbmsgs[0x0c22], pyOwner = self )
					else :
						if not self.__checkOperation() : return
						if BigWorld.player().testAddMoney( price ) > 0 :				# 超过系统规定的金钱上限
							# "价格超出了上限！"
							self.__showMessage( 0x0aa6 )
							return
						selPet.isVended = True
						selPet.rolePrice = price
						selIndex = self.pyMyPanel_.selIndex
						self.onMyPetSelected_( selIndex )
						self.pyMyPanel_.updateItem( selIndex, selPet )
						self.pySellPanel_.addItem( selPet )
						self.pyBinder.onCalcuExpense_()
			MoneyInputBox().show( addSellPet, labelGather.getText( "vendwindow:VendPetPanel", "ipBoxPrice" ), self )

	def onPetDown_( self ) :
		selPet = self.pySellPanel_.selItem
		if selPet is None : return
		self.pySellPanel_.removeItem( selPet )
		selPet.isVended = False
		for index, epitome in enumerate( self.pyMyPanel_.items ) :
			if epitome.databaseID == selPet.databaseID :
				self.pyMyPanel_.updateItem( index, selPet )
				break
		mySelIndex = self.pyMyPanel_.selIndex
		self.onMyPetSelected_( mySelIndex )
		self.pyBinder.onCalcuExpense_()

	def onRoleLosePet_( self, petDBID ) :
		BasePetPanel.onRoleLosePet_( self, petDBID )
		for index, epitome in enumerate( self.pySellPanel_.items ) :
			if epitome.databaseID == petDBID :
				self.pySellPanel_.removeItemOfIndex( index )
				break
		self.pyBinder.onCalcuExpense_()

	def onMyPetSelected_( self, index ) :
		"""
		玩家身上的宠物选择发生改变
		"""
		selPet = self.pyMyPanel_.selItem
		btnEnable = selPet is not None
		btnEnable &= not getattr( selPet, "isVended", False )
		roleState = BigWorld.player().state
		btnEnable &= roleState != csdefine.ENTITY_STATE_VEND					# 摆摊状态下不能操作
		self.pyUpBtn_.enable = btnEnable

	def onSellPetSelected_( self, index ) :
		"""
		正在摆摊的宠物选择发生改变
		"""
		roleState = BigWorld.player().state
		btnEnable = index > -1 and roleState != csdefine.ENTITY_STATE_VEND		# 摆摊状态下不能操作
		self.pyDownBtn_.enable = btnEnable
		self.pyBinder.enableChangePriceBtn()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def changeItemPrice( self ) :
		if not self.__checkOperation() : return
		selPet = self.pySellPanel_.selItem
		if selPet is None : return
		def changePrice( result, price ):
			if result == DialogResult.OK :
				if price <= 0:
					# "该宠物还没有定价!", "提示"
					showAutoHideMessage( 3.0, 0x0de2, mbmsgs[0x0c22], pyOwner = self )
				else :
					if not self.__checkOperation() : return
					if BigWorld.player().testAddMoney( price ) > 0 :					# 超过系统规定的金钱上限
						# "价格超出了上限！"
						self.__showMessage( 0x0aa6 )
						return
					selPet.rolePrice = price
					self.pyBinder.onCalcuExpense_()
		MoneyInputBox().show( changePrice, labelGather.getText( "vendwindow:VendPetPanel", "ipBoxNewPrice" ), self )

	def getVendPets( self ) :
		"""
		获取全部上架宠物
		"""
		return self.pySellPanel_.items

	def onRoleTradeStateChanged( self, state ) :
		mySelIndex = self.pyMyPanel_.selIndex
		self.onMyPetSelected_( mySelIndex )
		sellSelIndex = self.pySellPanel_.selIndex
		self.onSellPetSelected_( sellSelIndex )



class MyPetItem( StatusItem ) :

	__ITEM = None

	def __init__( self ) :
		if MyPetItem.__ITEM is None :
			MyPetItem.__ITEM = GUI.load( "guis/general/vendwindow/sellwindow/mypetitem.gui" )
			uiFixer.firstLoadFix( MyPetItem.__ITEM )
		item = util.copyGuiTree( MyPetItem.__ITEM )
		StatusItem.__init__( self, item )
		self.focus = False
		self.crossFocus = False
		self.commonColor = ( 255,255,255,0 )
		self.disableColor = ( 137,137,137,200 )

		self.__initialize( item )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ) :
		self.pyItem.onMouseEnter.bind( self.__onDescriptionShow )
		self.pyItem.onMouseLeave.bind( self.__onDescriptionHide )
		self.__pyResume = CSRichText( item.clipPanel )

	def __onDescriptionShow( self ) :
		#dsp = "如有需要，可在此添加说明。如：@B该宠物正在/不再摆摊中"
		#toolbox.infoTip.showItemTips( self, dsp )
		pass

	def __onDescriptionHide( self ) :
		toolbox.infoTip.hide()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setDisableView_( self ) :
		self.pyItem_.materialFX = "COLOUR_EFF"


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, pyViewItem ) :
		myPet = pyViewItem.listItem
		modelNumber = myPet.modelNumber
		self.pyItem.icon = g_npcmodel.getHeadTexture( modelNumber )
		if getattr( myPet, "isVended", False ) :
			self.state = UIState.DISABLE
		else :
			self.selected = pyViewItem.selected
		hierarchy = myPet.hierarchy
		if hierarchy == csdefine.PET_HIERARCHY_GROWNUP : 						# 成年宠物
			if len(myPet.name) > 8:
				self.__pyResume.text = myPet.name[0:8] + "..." + "@B(%s)" % labelGather.getText( "vendwindow:MyPetItem", "grownPet")
			else:
				self.__pyResume.text = myPet.name + "@B(%s)" % labelGather.getText( "vendwindow:MyPetItem", "grownPet")
			self.__pyResume.foreColor = ( 255, 255, 255, 255 )
		elif hierarchy == csdefine.PET_HIERARCHY_INFANCY1 : 					# 一代宝宝
			if len(myPet.name) > 8:
				self.__pyResume.text = myPet.name[0:8] + "..." + "@B(%s)" % labelGather.getText( "vendwindow:MyPetItem", "generation1" )
			else:
				self.__pyResume.text = myPet.name + "@B(%s)" % labelGather.getText( "vendwindow:MyPetItem", "generation1" )
			self.__pyResume.foreColor = ( 5, 193, 255, 255 )
		else: 																	# 二代宝宝
			if len(myPet.name) > 8:
				self.__pyResume.text = myPet.name[0:8] + "..." + "@B(%s)" % labelGather.getText( "vendwindow:MyPetItem", "generation2" )
			else:
				self.__pyResume.text = myPet.name + "@B(%s)" % labelGather.getText( "vendwindow:MyPetItem", "generation2" )
			self.__pyResume.foreColor = ( 254, 163, 8, 255 )



class SellPetItem( PyGUI ) :

	__PY_SELECTED_FLAG = None
	__ITEM = None

	def __init__( self ) :
		if SellPetItem.__ITEM is None :
			selctedFlag = GUI.load( "guis/general/vendwindow/sellwindow/selected_cover.gui" )
			SellPetItem.__PY_SELECTED_FLAG = PyGUI( selctedFlag )
			SellPetItem.__ITEM = GUI.load( "guis/general/vendwindow/sellwindow/sellpetitem.gui" )
			uiFixer.firstLoadFix( SellPetItem.__ITEM )
		item = util.copyGuiTree( SellPetItem.__ITEM )
		PyGUI.__init__( self, item )
		self.__pyHeader = PyGUI( item.item )
		self.__pyHeader.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, pyViewItem ) :
		sellPet = pyViewItem.listItem
		modelNumber = sellPet.modelNumber
		self.__pyHeader.texture = g_npcmodel.getHeadTexture( modelNumber )
		if pyViewItem.selected :
			self.addPyChild( SellPetItem.__PY_SELECTED_FLAG, "sel_cover" )
			SellPetItem.__PY_SELECTED_FLAG.pos = self.__pyHeader.pos
		else :
			self.gui.delChild( "sel_cover" )
