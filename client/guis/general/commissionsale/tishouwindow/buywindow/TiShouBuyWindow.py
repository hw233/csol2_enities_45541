# -*- coding: gb18030 -*-

from guis import *
from guis.controls.TabCtrl import TabCtrl
from guis.general.vendwindow.buywindow.BuyWindow import BaseBuyWindow
from PetsPanel import PetsPanel
from ItemsPanel import ItemsPanel
from PurchasePanel import PurchasePanel
from gbref import rds


class TiShouBuyWindow( BaseBuyWindow ):

	def __init__( self ) :
		BaseBuyWindow.__init__( self )
		self.__lastOpenTime = 0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initTabCtrl_( self, wnd ):
		self.pyTabCtrl_ = TabCtrl( wnd.tc )
		panelCls = [ ItemsPanel, PetsPanel, PurchasePanel ]
		self.pyTabCtrl_.autoSearchPages( panelCls )
		for pyTabPanel in self.pyTabCtrl_.pyPanels :
			pyTabPanel.subclass( pyTabPanel.gui, self )
		BaseBuyWindow.initTabCtrl_( self, wnd )

	def registerTriggers_( self ):
		self.triggers_["EVT_ON_TRIGGER_TISHOU_BUY_WINDOW"] = self.__onTriggerVisible # 打开/关闭替售购买界面
		BaseBuyWindow.registerTriggers_( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onTriggerVisible( self, shopName, ownerName, trapEntity ) :
		now = time.time()
		if self.trapEntityID_ == trapEntity.id and \
			self.__lastOpenTime + 0.5 > now :
				return
		self.__lastOpenTime = now
		self.pyStOwnerName_.text = shopName
		self.trapEntityID_ = trapEntity.id
		self.show()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		pass

	def show( self ) :
		BaseBuyWindow.show( self )
		for pyPage in self.pyTabCtrl_.pyPages :
			pyPage.pyPanel.onParentShow()

	def hide( self ) :
		BaseBuyWindow.hide( self )
		self.__lastOpenTime = 0
