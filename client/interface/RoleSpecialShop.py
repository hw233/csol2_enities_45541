# -*- coding: gb18030 -*-
#
# $Id: RoleSpecialShop.py,v 1.1 2008-08-15 09:14:10 wangshufeng Exp $


import BigWorld
from bwdebug import *
import event.EventCenter as ECenter
import time
import csdefine
import csconst
import csstatus
import items
from Function import Functor
import Language

g_items = items.instance()

UPDATE_DELAY_TIME = 1.5				# ������ʱ

class RoleSpecialShop:
	"""
	�����̳�
	"""
	def __init__( self ):
		"""
		"""
		self.spe_updateState = False	# �̳Ǹ���״̬
		self.spe_reset()
		self.spe_moneyType = csdefine.SPECIALSHOP_MONEY_TYPE_GOLD	# ��ɫ��ǰʹ�õĻ�������

	def spe_reset( self ):
		"""
		�����̳�����
		"""
		self.specialItemData = { csdefine.SPECIALSHOP_MONEY_TYPE_GOLD: {},
								csdefine.SPECIALSHOP_MONEY_TYPE_SILVER: {},
							}
																				# ( ��ѯ����, �ϴβ�ѯʱ�� )
		self.goodsTypeMap = { 	csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:{
									csdefine.SPECIALSHOP_RECOMMEND_GOODS : [ [], 0 ],	# �Ƽ���Ʒ
									csdefine.SPECIALSHOP_ESPECIAL_GOODS  : [ {csdefine.SPECIALSHOP_SUBTYPE_MOS_CRYSTAL:[], csdefine.SPECIALSHOP_SUBTYPE_VAL_GOODS:[]}, 0 ],	# ��ĵر�
									csdefine.SPECIALSHOP_CURE_GOODS      : [ {csdefine.SPECIALSHOP_SUBTYPE_EXP_GOODS:[], csdefine.SPECIALSHOP_SUBTYPE_REST_GOODS:[]}, 0 ],	# �ָ�����Ʒ
									csdefine.SPECIALSHOP_REBUILD_GOODS   : [ [], 0 ],	# �������
									csdefine.SPECIALSHOP_VEHICLE_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_LAND_VEHICLE:[],csdefine.SPECIALSHOP_SUBTYPE_SKY_VEHICLE:[], csdefine.SPECIALSHOP_SUBTYPE_VEHICLE_PROPS:[]}, 0 ],	# ��������Ʒ
									csdefine.SPECIALSHOP_PET_GOODS       : [ {csdefine.SPECIALSHOP_SUBTYPE_PET_BOOK:[], csdefine.SPECIALSHOP_SUBTYPE_PET_PROPS:[], csdefine.SPECIALSHOP_SUBTYPE_PET_EGG:[]}, 0 ],	# ��������Ʒ
									csdefine.SPECIALSHOP_FASHION_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_MALE_FASHION:[], csdefine.SPECIALSHOP_SUBTYPE_FEMALE_FASHION:[]}, 0 ],	# ʱװ����Ʒ
									csdefine.SPECIALSHOP_ENHANCE_GOODS 	 : [ [], 0 ],	# ǿ������
									csdefine.SPECIALSHOP_CRYSTAL_GOODS 	 : [ [], 0 ],	# ��Ƕˮ��
									csdefine.SPECIALSHOP_TALISMAN_GOODS  : [ [], 0 ],	# ��������
								},
								csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:{
									csdefine.SPECIALSHOP_RECOMMEND_GOODS : [ [], 0 ],	# �Ƽ���Ʒ
									csdefine.SPECIALSHOP_ESPECIAL_GOODS  : [ {csdefine.SPECIALSHOP_SUBTYPE_MOS_CRYSTAL:[], csdefine.SPECIALSHOP_SUBTYPE_VAL_GOODS:[]}, 0 ],	# ��ĵر�
									csdefine.SPECIALSHOP_CURE_GOODS      : [ {csdefine.SPECIALSHOP_SUBTYPE_EXP_GOODS:[], csdefine.SPECIALSHOP_SUBTYPE_REST_GOODS:[]}, 0 ],	# �ָ�����Ʒ
									csdefine.SPECIALSHOP_REBUILD_GOODS   : [ [], 0 ],	# �������
									csdefine.SPECIALSHOP_VEHICLE_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_LAND_VEHICLE:[],csdefine.SPECIALSHOP_SUBTYPE_SKY_VEHICLE:[], csdefine.SPECIALSHOP_SUBTYPE_VEHICLE_PROPS:[]}, 0 ],	# ��������Ʒ
									csdefine.SPECIALSHOP_PET_GOODS       : [ {csdefine.SPECIALSHOP_SUBTYPE_PET_BOOK:[], csdefine.SPECIALSHOP_SUBTYPE_PET_PROPS:[], csdefine.SPECIALSHOP_SUBTYPE_PET_EGG:[]}, 0 ],	# ��������Ʒ
									csdefine.SPECIALSHOP_FASHION_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_MALE_FASHION:[], csdefine.SPECIALSHOP_SUBTYPE_FEMALE_FASHION:[]}, 0 ],	# ʱװ����Ʒ
									csdefine.SPECIALSHOP_ENHANCE_GOODS 	 : [ [], 0 ],	# ǿ������
									csdefine.SPECIALSHOP_CRYSTAL_GOODS 	 : [ [], 0 ],	# ��Ƕˮ��
									csdefine.SPECIALSHOP_TALISMAN_GOODS  : [ [], 0 ],	# ��������
								}
							}

	def getSpeMoneyType( self ):
		"""
		��õ�ǰ�Ļ�������
		"""
		return self.spe_moneyType

	def setSpeMoneyType( self, moneyType ):
		"""
		���õ�ǰ�Ļ�������
		"""
		self.spe_moneyType = moneyType

	def spe_queryGoods( self, queryType, moneyType ):
		"""
		��ѯ�̳���Ʒ

		@param queryType : ��ѯ����
		@type queryType : UINT16
		"""
		if not self.spe_updateState or self.spe_moneyType != moneyType:
			self.spe_updateGoods( moneyType )
			self.spe_updateState = True
			
	def spe_updateGoods( self, moneyType ):
		"""
		���������������̳���Ʒ����
		"""
		interval = 0.0
		for goodsType in csconst.SPECIALSHOP_GOOS_LIST:
			BigWorld.callback( interval, Functor( self.base.spe_updateGoods, goodsType, moneyType ) )
			interval += UPDATE_DELAY_TIME
			
	def spe_receiveGoods( self, goodsData, queryType, moneyType ):
		"""
		Define method.
		������Ʒ����
		
		@param goodsData : [ ��Ʒid, ��Ʒ����, ��Ʒ��, ��Ʒ���� ]
		@type goodsData : [ ITEM_ID, INT, INT, STRING ]
		"""
		if moneyType not in self.goodsTypeMap:
			ERROR_MSG( "������(%i)���͵��̳ǡ�" % moneyType )
			return
		if queryType not in self.goodsTypeMap[moneyType]:
			ERROR_MSG( "������(%i)���͵���Ʒ��" % queryType )
			return
		itemID = goodsData[0]
		subType = goodsData[-1]
		itemsDict = self.goodsTypeMap[moneyType][ queryType ][0]
		if subType in itemsDict: #���ӷ���
			itemsDict[subType].append( itemID )
		else:
			if isinstance( itemsDict,dict ) and subType < 0:
				ERROR_MSG( "��Ʒ����������Ʒ%d����%d���࣬��ָ�����࣡"%( itemID, queryType ))
			else:
				itemsDict.append( itemID )
		specialItemData = self.specialItemData.get( moneyType, None )
		if specialItemData is None: return
		specialItemData[itemID] = goodsData
		if self.spe_moneyType != moneyType and \
		Language.LANG == Language.LANG_BIG5:
			self.spe_moneyType = moneyType
		ECenter.fireEvent( "EVT_ON_SPECIAL_GOODS_RECIEVE", queryType, goodsData, moneyType )
		
	def spe_onShopClosed( self ):
		"""
		Define method.
		�̳ǹرյ�֪ͨ
		"""
		self.spe_updateState = False
		self.spe_reset()
		ECenter.fireEvent( "EVT_ON_SPECIALSHOP_CLOSED" )
		
	def spe_shopping( self, itemID, amount, moneyType ):
		"""
		��һ����Ʒ
		"""
		itemsDict = self.specialItemData.get( csdefine.SPECIALSHOP_MONEY_TYPE_GOLD, {} )
		if Language.LANG == Language.LANG_BIG5:
			itemsDict = self.specialItemData.get( moneyType, {} )
		if itemID not in itemsDict:
			return
		# �ж�����Ƿ�Ǯ����cell�ϲ�����Ʒ�۸����ݣ���˱������������ж�
		if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:
			moneyAmount = self.gold
			statusMessageID = csstatus.SPECIALSHOP_GOLD_NOT_ENOUGH
		else:
			moneyAmount = self.silver
			statusMessageID = csstatus.SPECIALSHOP_SILVER_NOT_ENOUGH
		if moneyAmount < itemsDict[ itemID ][ 2 ] * amount:
			self.statusMessage( statusMessageID )
			return
		self.base.spe_shopping( itemID, amount, moneyType )

	# -------------------------------------------------
	def spe_requestItemsPrices( self, itemIDs ) :
		"""
		������Ʒ�۸�
		"""
		prices = {}
		for itemID in itemIDs :										# ���������ͻ��ˣ����Ƿ���ָ����Ʒ��
			if itemID in self.specialItemData :
				item = self.specialItemData[itemID]
				prices[itemID] = ( csdefine.SPECIALSHOP_REQ_SUCCESS, item[2] )
			else :
				self.base.spe_requestItemsPrices( itemIDs, self.spe_moneyType )			# ����ͻ���ȱ����Ʒ���������������
				return
		ECenter.fireEvent( "EVT_ON_SPECIAL_GET_ITEMS_PRICES", prices )

	def spe_onReceiveItemsPrices( self, prices ) :
		"""
		�յ���Ʒ�۸�
		hyw--2009.03.27
		"""
		ECenter.fireEvent( "EVT_ON_SPECIAL_GET_ITEMS_PRICES", prices )
