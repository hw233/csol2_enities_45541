# -*- coding: gb18030 -*-

# implement the TiShouSellPanel class
# written by ganjinxing 2009-10-29

from guis.controls.TabCtrl import TabCtrl
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.general.commissionsale.CommissionSale import commiss_models
from guis.general.vendwindow.sellwindow.SellPanel import BaseSellPanel
from PetsPanel import PetsPanel
from GoodsPanel import GoodsPanel
from PurchasePanel import TSPurchasePanel
from LabelGather import labelGather
from Time import Time
import BigWorld
import event.EventCenter as ECenter


class TiShouSellPanel( BaseSellPanel ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_TSNPC_FLAGS_CHANGED"] = self.__onFlagsChanged
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def initialize_( self, tabPanel ) :
		BaseSellPanel.initialize_( self, tabPanel )
		tabPanel.endVendBtn.visible = False
		tabPanel.changeNameBtn.visible = False
		tabPanel.startVendBtn.position = tabPanel.endVendBtn.position
		tabPanel.pauseVendBtn.position = tabPanel.endVendBtn.position

		self.__destroyTime = 0														# 保存NPC销毁时间
		self.__cdCBID = 0

		self.__pyRemainTime = StaticText( tabPanel.remainTime )
		self.__initComboBox( tabPanel.cb_stallModel )

	def initTabCtrl_( self, subTab ) :
		self.pySubCtrl_ = TabCtrl( subTab )
		self.pySubCtrl_.onTabPageSelectedChanged.bind( self.onTabSelectChanged_ )
		panelCls = [ GoodsPanel, PetsPanel, TSPurchasePanel ]
		self.pySubCtrl_.autoSearchPages( panelCls )
		for pyTabPanel in self.pySubCtrl_.pyPanels :
			pyTabPanel.subclass( pyTabPanel.gui, self )
		BaseSellPanel.initTabCtrl_( self, subTab )

	def onStartvend_( self ) :
		"""
		通知服务器开始寄售
		"""
		tishouNPC = self.pyBinder.tishouNPC
		if tishouNPC is not None :
			tishouNPC.cell.startTS()

	def onPauseVend_( self ) :
		"""
		需要修改寄售商品时，先通知服务器暂停寄售
		"""
		tishouNPC = self.pyBinder.tishouNPC
		if tishouNPC is not None :
			tishouNPC.cell.stopTS()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initComboBox( self, box ) :
		tempMap = [
					( 0, "colouredGlazeFox" ),
					( 1, "blueTiger" ),
					( 2, "yellowTiger" ),
					( 3, "lightningDog" ),
					( 4, "bigHeadRacoon" ),
					( 5, "blueMandarinDuck" ),
					( 6, "fortunatePig" ),
					]
		self.__pyCBStallModel = ODComboBox( box )
		self.__pyCBStallModel.onItemLClick.bind( self.__onModelChanged )
		self.__pyCBStallModel.pyBox.text = labelGather.getText( "commissionsale:TiShouSellPanel", "stallModel" )
		for index, modelNumber in tempMap :
			self.__pyCBStallModel.addItem( labelGather.getText( "commissionsale:TiShouSellPanel", modelNumber ) )

	def __onModelChanged( self, index ) :
		if commiss_models.has_key( index + 1 ) :
			tishouNPC = self.pyBinder.tishouNPC
			if tishouNPC is None : return
			tishouNPC.cell.updateTSNPCModel( index + 1 )

	def __onFlagsChanged( self, oldFlags ) :
		"""
		flags 标记发生变化
		"""
		self.onEnableButtons()
		self.__enableCBBox()
		for pyTabPanel in self.pySubCtrl_.pyPanels :
			pyTabPanel.onTSNPCFlagChaned( oldFlags )

	def __enableCBBox( self ) :
		"""
		设定是否能选择寄售形象
		"""
		tishouNPC = self.pyBinder.tishouNPC
		if tishouNPC is None : return
		isTishouState = tishouNPC.tsState
		self.__pyCBStallModel.enable = not isTishouState

	def __countdown( self ) :
		remainTime = int( self.__destroyTime - Time.time() )
		if remainTime < 0 :
			self.__pyRemainTime.text = labelGather.getText( "commissionsale:TiShouSellPanel", "stRemainTime" )+\
			labelGather.getText( "commissionsale:TiShouSellPanel", "stSecond", 0 )
			self.__stopCountdown()
			return
		hour = remainTime / 3600
		minute = remainTime % 3600 / 60
		second = remainTime % 60
		remainStr = labelGather.getText( "commissionsale:TiShouSellPanel", "stRemainTime" )
		if hour or minute :
			if second :
				minute += 1
				second = 0
			if minute == 60 :
				hour += 1
				minute = 0
		if hour :
			remainStr += labelGather.getText( "commissionsale:TiShouSellPanel", "stHour" ) % hour
		if minute :
			remainStr += labelGather.getText( "commissionsale:TiShouSellPanel", "stMinute" ) % minute
		if second :
			remainStr += labelGather.getText( "commissionsale:TiShouSellPanel", "stSecond" ) % second
		self.__pyRemainTime.text = remainStr
		self.__cdCBID = BigWorld.callback( 1, self.__countdown )

	def __stopCountdown( self ) :
		if self.__cdCBID :
			BigWorld.cancelCallback( self.__cdCBID )
			self.__cdCBID = 0


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enableChangePriceBtn( self ) :
		selTabPage = self.pySubCtrl_.pySelPage
		if selTabPage is None : return
		tishouNPC = self.pyBinder.tishouNPC
		selPanel = selTabPage.pyPanel
		enable = tishouNPC is not None and not tishouNPC.tsState
		enable &= selPanel.canChangePrice()
		self.pyChangePriceBtn_.enable = enable

	def refreshRemainTime( self, destroyTime ) :
		"""
		"""
		self.__destroyTime = destroyTime
		self.__stopCountdown()
		self.__countdown()

	def onEnableButtons( self ) :
		"""
		根据flags标记的寄售状态使能按钮
		"""
		tishouNPC = self.pyBinder.tishouNPC
		if tishouNPC is None : return
		isTishouState = tishouNPC.tsState
		self.pyStartVendBtn_.visible = not isTishouState
		self.pyPauseVendBtn_.visible = isTishouState
		self.enableChangePriceBtn()

	def onParentShow( self ) :
		self.onEnableButtons()
		self.__enableCBBox()
		playerName = BigWorld.player().getName()
		self.pyStOwnerName_.text = labelGather.getText( "commissionsale:TiShouSellPanel", "stOwnerName" ) + playerName
		tishouNPC = self.pyBinder.tishouNPC
		if tishouNPC is None : return
		for key, modelNumber in commiss_models.iteritems() :
			if tishouNPC.modelNumber == modelNumber :
				self.__pyCBStallModel.selIndex = key - 1
		for pyTabPanel in self.pySubCtrl_.pyPanels :
			pyTabPanel.onParentShow()

	def onParentHide( self ) :
		self.__stopCountdown()
		self.__pyRemainTime.text = ""
		for pyTabPanel in self.pySubCtrl_.pyPanels :
			pyTabPanel.onParentHide()

	def dispose( self ) :
		self.triggers_ = {}
		BaseSellPanel.dispose( self )
		for pyTabPanel in self.pySubCtrl_.pyPanels :
			pyTabPanel.dispose()

