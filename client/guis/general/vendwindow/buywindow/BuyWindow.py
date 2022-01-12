# -*- coding: gb18030 -*-
#
# $Id: BuyWindow.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $
from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from guis.controls.StaticText import StaticText
from PetsPanel import BuyPetsPanel
from ItemsPanel import BuyItemsPanel
from PurchasePanel import PurchasePanel
from LabelGather import labelGather
from gbref import rds
import csdefine
import csconst


# --------------------------------------------------------------------
# BaseBuyWindow can't be instantiated
# --------------------------------------------------------------------
class BaseBuyWindow( Window ) :

	def __init__( self ):
		wnd = GUI.load( "guis/general/vendwindow/buywindow/vendbuywindow.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.trapEntityID_ = -1
		self.triggers_ = {}
		self.registerTriggers_()
		self.trapID_ = None
		self.__initialize( wnd )

	#	rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# 添加到MutexGroup.TRADE1互斥组


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ):
		self.pyStOwnerName_ = StaticText( wnd.stOwnerName ) 					# 摊主名称
		self.pyStOwnerName_.text = ""

		self.__pyMoneyBox = MoneyBar( wnd.box_money ) 							# 买家拥有金钱
		self.__pyMoneyBox.readOnly = True
		self.__pyMoneyBox.money = 0

		self.initTabCtrl_( wnd )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "vendwindow:BaseBuyWindow", "lbTitle" )
		labelGather.setLabel( wnd.st_money, "vendwindow:BaseBuyWindow", "rtOwnMoney" )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )

	def __onRoleMoneyChanged( self, oldMoney, newMoney ) :
		"""
		玩家金钱改变
		"""
		self.__pyMoneyBox.money = newMoney


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initTabCtrl_( self, wnd ) :
		for index, pyBtn in enumerate( self.pyTabCtrl_.pyBtns ) :
			labelGather.setPyBgLabel( pyBtn, "vendwindow:BaseBuyWindow", "tabBtn_%i" % index )

	def resetTabPanel_( self ) :
		for pyPanel in self.pyTabCtrl_.pyPanels :
			pyPanel.reset()

	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_ROLE_MONEY_CHANGED"] = self.__onRoleMoneyChanged #金钱数量发生变化
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def addTrap_( self ) :
		"""
		添加对话陷阱
		"""
		self.delTrap_()
		distance = csconst.COMMUNICATE_DISTANCE
		self.trapID_ = BigWorld.addPot(self.trapEntity.matrix, distance, self.onEntitiesTrapThrough_ )	#打开窗口后为玩家添加对话陷阱

	def delTrap_( self ) :
		if self.trapID_ is not None:
			BigWorld.delPot( self.trapID_ )							# 删除玩家的对话陷阱
			self.trapID_ = None

	def onEntitiesTrapThrough_( self, isEnter,handle ) :
		if  not isEnter :											# 如果NPC离开玩家对话陷阱
			self.hide()


	# -------------------------------------------------------------------
	# public
	# -------------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.triggers_[eventMacro]( *args )

	def hide( self ) :
		self.resetTabPanel_()
		self.delTrap_()
		self.trapEntityID_ = -1
		Window.hide( self )

	def show( self ) :
		Window.show( self )
		self.addTrap_()

	def onLeaveWorld( self) :
		self.hide()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTrapNPC( self ) :
		return BigWorld.entities.get( self.trapEntityID_, None )

	trapEntity = property( _getTrapNPC )


class VendBuyWindow( BaseBuyWindow ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initTabCtrl_( self, wnd ) :
		self.pyTabCtrl_ = TabCtrl( wnd.tc )
		panelCls = [ BuyItemsPanel, BuyPetsPanel, PurchasePanel ]
		self.pyTabCtrl_.autoSearchPages( panelCls )
		for pyTabPanel in self.pyTabCtrl_.pyPanels :
			pyTabPanel.subclass( pyTabPanel.gui, self )
		BaseBuyWindow.initTabCtrl_( self, wnd )

	def registerTriggers_( self ):
		self.triggers_["EVT_ON_VEND_STATE_CHANGE"] = self.__onVenderStateChange #卖家状态改变
		self.triggers_["EVT_ON_VEND_UI_NAME_CHANGE"] = self.__onSignboardChange #摆摊招牌改变
		BaseBuyWindow.registerTriggers_( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onVenderStateChange( self, tradeState ) :
		if tradeState == csdefine.ENTITY_STATE_VEND :
			self.show()
		else :
			self.hide()

	def __onSignboardChange( self, playerID, signboard ) :
		if playerID == self.trapEntityID_ :
			self.pyStOwnerName_.text = signboard


	# -------------------------------------------------------------------
	# public
	# -------------------------------------------------------------------
	def show( self ) :
		shopman = BigWorld.player().targetEntity
		if shopman is None:return
		self.trapEntityID_ = shopman.id
		if shopman.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and \
		shopman.state == csdefine.ENTITY_STATE_VEND :
			vendSignboard = shopman.vendSignboard
			if vendSignboard == "":
				self.pyStOwnerName_.text = labelGather.getText( "vendwindow:VendBuyWindow", "stSignBoard", shopman.getName() )
			else:
				self.pyStOwnerName_.text = vendSignboard
			BaseBuyWindow.show( self )
