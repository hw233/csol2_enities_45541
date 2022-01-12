# -*- coding: gb18030 -*-

# ���۲˵� consignment sale menu

from guis import *
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.general.commissionsale.commissionviewer.CommissionViewer import CommissionViewer
from LabelGather import labelGather
import event.EventCenter as ECenter
import csdefine


class ConsignmentSaleMenu( object ) :

	__instance = None

	def __init__( self ) :
		assert ConsignmentSaleMenu.__instance is None, "ConsignmentSaleMenu instance has been created!"
		ConsignmentSaleMenu.__instance = self
		object.__init__( self )

		self.__triggers = {}
		self.__registerTriggers()
		self.__pyMenuItems = []

		self.__initialize()

	def __del__( self ) :
		if Debug.output_del_ContextMenu :
			INFO_MSG( "ConsignmentSaleMenu has been destroyed!" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		self.__pyMenu = ContextMenu()
		self.__pyMenu.onAfterClose.bind( self.hide )
		self.__pyMenu.onBeforePopup.bind( self.__onBeforMUPopup )
		self.__pyMenu.onItemClick.bind( self.__onMenuItemClick )
		self.__createMenuItem( self.__pyMenu, labelGather.getText( "minmap:cgMenu", "miShopView" ), self.__searchShops )
		self.__createMenuItem( self.__pyMenu, labelGather.getText( "minmap:cgMenu", "miFetchMoney"), self.__fetchMoney )
		self.__createMenuItem( self.__pyMenu, labelGather.getText( "minmap:cgMenu", "miFetchGoods" ), self.__fetchGoods )
		self.__createMenuItem( self.__pyMenu, labelGather.getText( "minmap:cgMenu", "miFetchPets" ), self.__fetchPets )
		self.__createMenuItem( self.__pyMenu, labelGather.getText( "minmap:cgMenu", "miFetchPGoods" ), self.__fetchPurchaseItems )
		self.__createMenuItem( self.__pyMenu, labelGather.getText( "minmap:cgMenu", "miFetchPDeposit" ), self.__fetchPurchaseDeposit )
		pyMI = self.__createMenuItem( self.__pyMenu, labelGather.getText( "minmap:cgMenu", "miSearchNPC" ), lambda i : True, False )
		self.__createMenuItem( pyMI.pySubItems, labelGather.getText( "minmap:cgMenu", "miFlyToNPC" ), self.__flyToNPC )
		self.__createMenuItem( pyMI.pySubItems, labelGather.getText( "minmap:cgMenu", "miRunToNPC" ), self.__runToNPC, False )

	def __registerTriggers( self ) :
		"""
		"""
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __createMenuItem( self, pyParent, text, handler, cloven = True ) :
		"""
		�����˵���
		@param	pyParent	: ���˵�
		@param	text		: �˵��ı�
		@param	handler		: �˵�����ص�����
		@param	cloven		: �Ƿ������´����ָ���
		"""
		pyMI = DefMenuItem( text )
		self.__pyMenuItems.append( pyMI )
		pyMI.handler = handler
		pyParent.add( pyMI )
		if cloven :
			pyST = DefMenuItem( style = MIStyle.SPLITTER )
			pyParent.add( pyST )
		return pyMI

	# -------------------------------------------------
	def __onMenuItemClick( self, pyItem ) :
		"""
		�����ĳ���˵���
		"""
		pyItem.handler( pyItem )

	def __onBeforMUPopup( self ) :
		return True

	def __searchShops( self, pyItem ) :
		"""
		���̲�ѯ
		"""
		CommissionViewer.instance().show()

	def __fetchMoney( self, pyItem ) :
		"""
		��ȡ���۽�Ǯ
		"""
		BigWorld.player().base.takeTSMoneyFromTiShouMgr()

	def __fetchGoods( self, pyItem ) :
		"""
		��ȡ������Ʒ
		"""
		player = BigWorld.player()
		player.base.takeTSItemFromTiShouMgr()

	def __fetchPets( self, pyItem ) :
		"""
		��ȡ���۳���
		"""
		player = BigWorld.player()
		player.base.takeTSPetFromTiShouMgr()

	def __fetchPurchaseItems( self, pyItem ) :
		"""
		��ȡ�չ���Ʒ
		"""
		player = BigWorld.player()
		player.cell.takeCollectedItems()

	def __fetchPurchaseDeposit( self, pyItem ) :
		"""
		��ȡ�չ�Ѻ��
		"""
		player = BigWorld.player()
		player.cell.takeCollectionDeposit()

	def __flyToNPC( self, pyItem ) :
		"""
		ʹ����·�䴫�͵�����NPC��
		"""	
		BigWorld.player().cell.cometoTSNPC( 0 )

	def __runToNPC( self, pyItem ) :
		"""
		�Զ�Ѱ·������NPC��
		"""
		BigWorld.player().cell.cometoTSNPC( 1 )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def instance() :
		if ConsignmentSaleMenu.__instance is None :
			ConsignmentSaleMenu.__instance = ConsignmentSaleMenu()
		return ConsignmentSaleMenu.__instance

	@staticmethod
	def isInstantial() :
		"""
		�Ƿ��ѱ�ʵ����
		"""
		return ConsignmentSaleMenu.__instance is not None

	def resetMenuItem( self, oldFlag ) :
		isTishouState = BigWorld.player().hasFlag( csdefine.ROLE_FLAG_TISHOU )
		self.__pyMenuItems[-3].enable = isTishouState

	def show( self ) :
		self.__pyMenu.show()
		self.__pyMenu.top = 69
		self.__pyMenu.right = BigWorld.screenWidth() - 186
		self.resetMenuItem( 0 )

	def hide( self ) :
		self.__pyMenu = None
		self.__triggers = {}
		self.__pyMenuItems = []
		ConsignmentSaleMenu.__instance = None

	def onEvent( self, evtMacro, *agrs ) :
		self.__triggers[evtMacro]( *agrs )
