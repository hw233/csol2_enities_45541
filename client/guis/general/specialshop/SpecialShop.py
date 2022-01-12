# -*- coding: gb18030 -*-
#
# $Id: SpecialShop.py, fangpengjun Exp $

"""
implement SpecialShop class

"""
from bwdebug import *
from guis import *
import BigWorld
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.StaticText import StaticText
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from FittingPanel import FittingPanel
from SpecialCaster import SpecialCaster
from ExplainWnd import ExplainWnd
from GoodsPanel import GoodsPanel
from YBTradePanel import YBTradePanel
from LabelGather import labelGather
import Language
import csdefine
import math
import ItemTypeEnum
import reimpl_specialShop

from AbstractTemplates import MultiLngFuncDecorator

class deco_InitGoldSilver( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyGold, pySilver ) :
		"""
		����������µ���������������ĳߴ�
		"""
		pyGold.charSpace = -1.0
		pyGold.fontSize = 12
		
		pySilver.charSpace = -1
		pySilver.fontSize = 12

class SpecialShop( Window ):
	
	_cc_yb_type = 11

	def __init__( self ):
		wnd = GUI.load( "guis/general/specialshop/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
#		self.affirmBuy = True 								# ����ʱ�Ƿ񵯳�����ȷ��
		self.__triggers = {}
		self.__registerTriggers()
		self.__initCrystalUI( wnd )
		
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyBtnTry = HButtonEx( wnd.btnTry ) #�Դ���ť
		self.__pyBtnTry.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTry.enable = False
		self.__pyBtnTry.onLClick.bind( self.__onFitting )

		self.__pyBtnCharge = HButtonEx( wnd.btnCharge ) #��ֵ��ť
		self.__pyBtnCharge.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCharge.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnCharge.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyBtnCharge.onLMouseDown.bind( self.__onLMouseDown )
		self.__pyBtnCharge.enable = True
		self.__pyBtnCharge.onLClick.bind( self.__onCharge )

		self.__pyStGold = StaticText( wnd.stGold ) #��ҽ�Ԫ������
		self.__pyStGold.text = ""

		self.__pyStSilver = StaticText( wnd.stSilver ) #�����Ԫ����ʾ
		self.__pyStSilver.text = ""

		self.__pyBtnGuide = HButtonEx( wnd.btnGuide ) #����ָ��
		self.__pyBtnGuide.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnGuide.onLClick.bind( self.__onShowGuide )

		self.__pySpecialCaster = SpecialCaster( wnd.bdcaster.msgPanel )

		self.__pyRBGold = RadioButtonEx( wnd.goldChecker )
		self.__pyRBSilver = RadioButtonEx( wnd.silverChecker )
		self.__rbArray = CheckerGroup()
		self.__rbArray.addCheckers( self.__pyRBGold, self.__pyRBSilver )
		self.__rbArray.onCheckChanged.bind( self.__onMoneyTypeChanged )
		
		self.pyTabCtr = TabCtrl( wnd.tabCtrl )
		self.__pyGoodsPanel = GoodsPanel( wnd.tabCtrl.panel_0, self ) #�����Ʒ���
		self.__pyYBTradePanel = YBTradePanel( wnd.tabCtrl.panel_1, self ) #Ԫ���������
		
		self.__initGoldSilver( self.__pyStGold, self.__pyStSilver )
		
		pyPages = {}
		for name, item in wnd.tabCtrl.children: #��Ʒ���Ͱ�ť
			if not name.startswith( "typeBtn_" ):continue
			type = int( name.split( "_" )[1] )
			pyTypeBtn = TabButton( item )
			pyTypeBtn.setStatesMapping( UIState.MODE_R3C1 )
			pyTypeBtn.isOffsetText = True
			goodsType = int( math.pow( 2, type - 1 ) )
			labelGather.setPyBgLabel( pyTypeBtn, "SpecialShop:main", name ) # ���ñ�ǩ
			if type != self._cc_yb_type:
				pyPage = TabPage( pyTypeBtn, self.__pyGoodsPanel )
				pyPage.type = type
				pyPages[type] = pyPage
			else:
				YBPage = TabPage( pyTypeBtn, self.__pyYBTradePanel )
				YBPage.type = type
				pyPages[type] = YBPage
		for pyPage in pyPages.values():
			self.pyTabCtr.addPage( pyPage )
		self.pyTabCtr.onTabPageSelectedChanged.bind( self.__onPageChange )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnTry, "SpecialShop:main", "btnTry" )
		labelGather.setPyBgLabel( self.__pyBtnGuide, "SpecialShop:main", "btnGuide" )
		labelGather.setPyBgLabel( self.__pyBtnCharge, "SpecialShop:main", "btnCharge" )
		labelGather.setLabel( wnd.lbTitle, "SpecialShop:main", "lbTitle" )
		labelGather.setLabel( wnd.choiceIngot, "SpecialShop:main", "choiceIngot" )
	
	@deco_InitGoldSilver
	def __initGoldSilver( self, pyGold, pySilver ):
		pyGold.charSpace = 0.0
		pySilver.charSpace = 0.0
		fontSize = 13
		if pyGold.font == "MSYHBD.TTF":
			fontSize = 12
		pyGold.fontSize = fontSize
		pySilver.fontSize = fontSize

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_SPECIAL_SHOP"] = self.__onShopShow #��ʾ�̳ǽ���
		self.__triggers["EVT_ON_ROLE_GOLD_CHANGED"] = self.__onRoleGoldChange #���Ԫ���仯
		self.__triggers["EVT_ON_ROLE_SILVER_CHANGED"] = self.__onSilverChanged	# ��Ԫ�����������仯
		self.__triggers["EVT_ON_SPECIAL_GOODS_ADS_ADD"] = self.__onSpecialShopAd #��Ϸ�̳ǹ��
		self.__triggers["EVT_ON_SPECIALSHOP_CLOSED"] = self.__onShopClosed #�̳ǹر�
		self.__triggers["EVT_ON_QUERY_SHOP_ITEM"] = self.__onQueryItem	#��ѯ��Ʒ
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------
	@reimpl_specialShop.deco_guispecialShopStart
	def __initCrystalUI( self, wnd ):
		"""
		������Ƕˮ����ť����ʾ״̬
		"""
		wnd.tabCtrl.typeBtn_10.visible = False
		wnd.tabCtrl.typeBtn_11.visible = True
		wnd.tabCtrl.typeBtn_11.position = wnd.tabCtrl.typeBtn_10.position

	def __onShopShow( self ):
		self.__pyRBGold.checked = True							# Ĭ��ѡ���Ԫ��
		for pyPage in self.pyTabCtr.pyPages:
			type = pyPage.type
			goodsType = int( math.pow( 2, type - 1 ) )
			if goodsType == csdefine.SPECIALSHOP_RECOMMEND_GOODS :
				if self.pyTabCtr.pySelPage != pyPage :
					self.pyTabCtr.pySelPage = pyPage	# Ĭ����ʾ�Ƽ���Ʒ
				else :
					self.__onPageChange( self.pyTabCtr )
				break
		self.show()

	def __onShopClosed( self ):
		"""
		�̳ǹر�
		"""
		self.__pyGoodsPanel.onShopClose()
		if self.visible:
			def query( rs_id ):
				self.hide()
			# "��Ϸ�̳����ڸ��£��̳ǽ�����رա�"
			showMessage( 0x07e1, "", MB_OK, query )
			
	def __onQueryItem( self, itemID,pageIndex = 0 ):
		"""
		��ѯ��Ʒ
		"""
		self.show()
		self.pyTabCtr.pySelPage = self.pyTabCtr.pyPages[pageIndex]	#��ת��ȫ����Ʒҳ���ѯ
		pyPanel = self.pyTabCtr.pySelPage.pyPanel
		pyPanel.queryItem( itemID )

	def __onMoneyTypeChanged( self, pyRadio ):
		"""
		�������͸ı�
		"""
		if self.__pyRBGold.checked:
			BigWorld.player().setSpeMoneyType( csdefine.SPECIALSHOP_MONEY_TYPE_GOLD )
		else:
			BigWorld.player().setSpeMoneyType( csdefine.SPECIALSHOP_MONEY_TYPE_SILVER )

	def __onRoleGoldChange( self, oldGold, newGold ):
		"""
		��Ԫ���仯
		"""
		self.__pyStGold.text = str( newGold )

	def __onSilverChanged( self, oldSilver, newSilver ):
		"""
		��Ԫ���仯
		"""
		self.__pyStSilver.text = str( newSilver )

	def __onSpecialShopAd( self, adText ): #��ʾ�������
		pass

	def __onShowGuide( self ):
		ExplainWnd.instance().show( self )

	def __onPageChange( self, pyCtlr ):
		player = BigWorld.player()
		pySelPage = pyCtlr.pySelPage
		type = pySelPage.type
		if type != self._cc_yb_type: #��ΪԪ������
			self.__pyGoodsPanel.onGoodsTypeChange( type )
			self.__pyGoodsPanel.visible = True
		else:
			self.__pyYBTradePanel.onSelected()

	def __onCharge( self ):				# ��ת����ֵ��ҳ
		# Ŀǰ���󶨵ķ���������װ������ֻ�������� --pj
		self.__onChargeNormal()

	@reimpl_specialShop.deco_guispecialShopOnCharge
	def __onChargeNormal( self ):
		csol.openUrl( "http://www.gyyx.cn/pay/CardPay.aspx" )

	def __onFitting( self ):
		itemInfo = self.__pyGoodsPanel.getSelGoods()
		if itemInfo is None:return
		baseItem = itemInfo.baseInfo.baseItem
		if baseItem.isEquip() and baseItem.canWield( BigWorld.player() ):
			FittingPanel.instance().addNewModel( baseItem )
			if not FittingPanel.instance().rvisible:
				FittingPanel.instance().show( self )
		#�����
		elif baseItem.isType( ItemTypeEnum.ITEM_SYSTEM_VEHICLE ):
			FittingPanel.instance().addVehicleModel( baseItem )
			if not FittingPanel.instance().rvisible:
				FittingPanel.instance().show( self )

	def __onMouseEnter( self, pyBtn ):
		if pyBtn.pyText_:
			pyBtn.foreColor = 95, 255, 8, 255

	def __onMouseLeave( self, pyBtn ):
		if pyBtn.pyText_:
			pyBtn.foreColor = 255, 248, 158, 255

	def __onLMouseDown( self, pyBtn ):
		if pyBtn.pyText_:
			pyBtn.foreColor = 255, 248, 158, 255
	
	def _getAffirmBuy( self ):
		return self.__pyGoodsPanel.affirmBuy
	
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

	def show( self, pyOwner = None ):
		Window.show( self, pyOwner )

	def hide( self ):
		self.__pyYBTradePanel.onHide()
		Window.hide( self )

	def onLeaveWorld( self ):
		self.__pyGoodsPanel.clearGoods()
		self.__pyYBTradePanel.onLeaveWorld()
		self.hide()
	
	def setTryState( self, baseItem ):
		self.__pyBtnTry.enable = baseItem.isEquip() and baseItem.canWield( BigWorld.player() ) or baseItem.isType( 394497 )
