# -*- coding: gb18030 -*-


"""
implement SpecialShop class

繁体版商城
"""
from guis import *
import BigWorld
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.CheckerGroup import CheckerGroup
from FittingPanel import FittingPanel
from SpecialCaster import SpecialCaster
from GoodsPanel_Big5 import GoodsPanel
from LabelGather import labelGather
import csdefine
import Language

class SpecialShop( Window ):
	
	_cc_yb_type = 11
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/specialshop/window_big5.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__pyItems = {}
		self.__pagesNum = -1
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__pySpecialCaster = SpecialCaster( wnd.msgPanel )
		self.__pyGoodsCtrl = TabCtrl( wnd.mainCtrl )
		self.__pyGoldGoodsPanel = GoodsPanel( wnd.mainCtrl.panel_0, csdefine.SPECIALSHOP_MONEY_TYPE_GOLD )
		self.__pyGoldTabBtn = TabButton( wnd.mainCtrl.btn_0 )
		labelGather.setPyBgLabel( self.__pyGoldTabBtn, "SpecialShop:main", "tab_0" )
		self.__pyGoldGoodsPage = TabPage( self.__pyGoldTabBtn, self.__pyGoldGoodsPanel )
		self.__pyGoodsCtrl.addPage( self.__pyGoldGoodsPage )
		
		self.__pySilverGoodsPanel = GoodsPanel( wnd.mainCtrl.panel_1, csdefine.SPECIALSHOP_MONEY_TYPE_SILVER )
		self.__pySilverTabBtn = TabButton( wnd.mainCtrl.btn_1 )
		labelGather.setPyBgLabel( self.__pySilverTabBtn, "SpecialShop:main", "tab_1" )
		self.__pySilverGoodsPage = TabPage( self.__pySilverTabBtn, self.__pySilverGoodsPanel )
		self.__pyGoodsCtrl.addPage( self.__pySilverGoodsPage )
		
		self.__pyGoodsCtrl.onTabPageSelectedChanged.bind( self.__onPageChange )

		labelGather.setLabel( wnd.lbTitle, "SpecialShop:main", "lbTitle" )
		labelGather.setLabel( wnd.stTips, "SpecialShop:main", "stTips" )
		labelGather.setLabel( wnd.converatio, "SpecialShop:main", "converatio" )
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_SPECIAL_SHOP"] = self.__onShopShow #显示商城界面
		self.__triggers["EVT_ON_ROLE_GOLD_CHANGED"] = self.__onRoleGoldChange #玩家元宝变化
		self.__triggers["EVT_ON_ROLE_SILVER_CHANGED"] = self.__onSilverChanged	# 银元宝数量发生变化
		self.__triggers["EVT_ON_SPECIAL_GOODS_ADS_ADD"] = self.__onSpecialShopAd #游戏商城广告
		self.__triggers["EVT_ON_SPECIALSHOP_CLOSED"] = self.__onShopClosed #商城关闭
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------
	def __onShopShow( self ):
		self.__pyGoodsCtrl.pySelPage = self.__pyGoldGoodsPage
		pySelPage = self.__pyGoodsCtrl.pySelPage
		if pySelPage is None:return
		pyPanel = pySelPage.pyPanel
		if pyPanel is None:return
		pyPanel.onSelected()
		self.show()
	
	def __onPageChange( self, tabCtrl ):
		"""
		货币类型改变
		"""
		pySelPage = tabCtrl.pySelPage
		if pySelPage is None:return
		pyPanel = pySelPage.pyPanel
		moneyType = pyPanel.moneyType
		pyPanel.onSelected()
		for pyPage in tabCtrl.pyPages:
			if pyPage.index != pySelPage.index:
				pyPanel = pyPage.pyPanel
				pyPanel.resetTypeBtns()

	def __onRoleGoldChange( self, oldGold, newGold ):
		"""
		金元宝变化
		"""
		self.__pyGoldGoodsPanel.onGoldChange( oldGold, newGold )

	def __onSilverChanged( self, oldSilver, newSilver ):
		"""
		银元宝变化
		"""
		self.__pySilverGoodsPanel.onGoldChange( oldSilver, newSilver )

	def __onSpecialShopAd( self, adText ): #显示滚动广告
		pass
	
	def __onShopClosed( self ):
		"""
		商城关闭
		"""
		self.__pyGoodsPanel.onShopClose()
		if self.visible:
			def query( rs_id ):
				self.hide()
			# "游戏商城正在更新，商城界面需关闭。"
			showMessage( 0x07e1, "", MB_OK, query )

	def _getAffirmBuy( self ):
		pySelPage = self.__pyGoodsCtrl.pySelPage
		if pySelPage is None:
			return True
		else:
			selPyPanel = pySelPage.pyPanel
			return selPyPanel.affirmBuy
	
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	affirmBuy = property( _getAffirmBuy, )

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )
	
	def show( self ):
		Window.show( self )

	def hide( self ):
		for pyPage in self.__pyGoodsCtrl.pyPages:
			pyPanel = pyPage.pyPanel
			if pyPanel is None:continue
			pyPanel.resetTypeBtns()
			pyPanel.clearGoods()
		Window.hide( self )

	def onLeaveWorld( self ):
		self.hide()
		