# -*- coding: gb18030 -*-

# The commission sale window includs the merchant search,
# normal goods search, pet goods search.
# written by ganjinxing 2009-10-19

import sys
from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabButton
from MerchantPanel import MerchantPanel
from GoodsPanel import GoodsPanel
from PetPanel import PetPanel
from LabelGather import labelGather


class CommissionViewer( Window ) :

	__instance = None

	def __init__( self ) :
		assert CommissionViewer.__instance is None, "CommissionViewer instance had been created!"
		wnd = GUI.load( "guis/general/commissionsale/shopsviewer/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__triggers = {}
		self.__initialize( wnd )
		self.__registerTriggers()
		self.addToMgr()

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )			# 添加到MutexGroup.TRADE1互斥组

	def __del__( self ) :
		print "CommissionViewer is destroyed!"

	def __initialize( self, wnd ) :
		self.__pyTabCtrl = TabCtrl( wnd.tc )
		tempPanelMap = { "0" : ( "merchant", EmptyPanel, MerchantPanel ),
						 "1" : ( "goods", GoodsPanel, GoodsPanel ),
						 "2" : ( "pet", EmptyPanel, PetPanel ),
						}
		for cName, child in wnd.tc.children :
			if "btn_" in cName :
				panelIdx = cName.split( "_" )[-1]
				panelName, commitScript, panelScript = tempPanelMap.get( panelIdx, ( None, None, None ) )
				if commitScript is None : continue
				pyTabBtn = TabButton( child )
				pyTabBtn.selectedForeColor = 142,216,217,255
				pyTabBtn.text = labelGather.getText( "commissionsale:CommissionViewer", "tb_" + panelName )
				pyTabPanel = commitScript( self )
				pyTabPanel.onEnterWorld()
				self.__pyTabCtrl.addPyChild( pyTabPanel )
				pyTabPanel.pos = 0, 0
				pyTabPanel.panelScript = panelScript
				pyTabPage = TabPage( pyTabBtn, pyTabPanel )
				self.__pyTabCtrl.addPage( pyTabPage )
				pyTabPage.enable = False

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "commissionsale:CommissionViewer", "lbTitle")

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_MONEY_CHANGED"] = self.__onMoneyChanged
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )

	def __onMoneyChanged( self, oldValue, newValue ) :
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onRoleMoneyChanged( oldValue, newValue )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		"""
		keyEventHandler = getattr( self.__pyTabCtrl.pySelPage.pyPanel, "keyEventHandler", None )
		if callable( keyEventHandler ) :
			return keyEventHandler( key, mods )
		return Window.onKeyDown_( self, key, mods )

	def searchByMerchantName( self, merchantName ) :
		"""
		查找某个玩家的所有寄售商品
		"""
		for pyPanel in self.__pyTabCtrl.pyPanels :
			if hasattr( pyPanel, "searchByMerchantName" ) :
				pyPanel.searchByMerchantName( merchantName )
			if isinstance( pyPanel, GoodsPanel ) :
				pyPanel.pyTabPage.selected = True

	def initGradual( self ) :
		"""
		逐个初始化界面，由已初始化好的界面通知初始化下一个
		"""
		for pyPage in self.__pyTabCtrl.pyPages :
			if not isinstance( pyPage.pyPanel, EmptyPanel ) : continue			# 如果已经创建了该实例，则不再创建
			pyBtn = pyPage.pyBtn
			panelScript = pyPage.pyPanel.panelScript
			pyTabPanel = panelScript( self )
			pyTabPanel.onEnterWorld()
			self.__pyTabCtrl.addPyChild( pyTabPanel )
			pyTabPanel.pos = 0, 0
			pyPage.setPage( pyBtn, pyTabPanel )
			break

	def onEnterWorld( self ) :
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onEnterWorld()

	def onLeaveWorld( self ) :
		self.hide()

	def onEvent( self, evtMacro, *agrs ) :
		self.__triggers[evtMacro]( *agrs )

	def hide( self ) :
		Window.hide( self )
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.dispose()
		self.__triggers = {}
		self.dispose()
		CommissionViewer.__instance = None

	@staticmethod
	def instance() :
		if CommissionViewer.__instance is None :
			CommissionViewer.__instance = CommissionViewer()
		return CommissionViewer.__instance


class EmptyPanel( TabPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.Simple("")
		TabPanel.__init__( self, panel, pyBinder )

	def onRoleMoneyChanged( self, oldValue, newValue ) :
		pass

	def onEnterWorld( self ) :
		pass

