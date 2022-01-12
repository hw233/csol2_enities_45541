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

UPDATE_DELAY_TIME = 1.5				# 更新延时

class RoleSpecialShop:
	"""
	道具商城
	"""
	def __init__( self ):
		"""
		"""
		self.spe_updateState = False	# 商城更新状态
		self.spe_reset()
		self.spe_moneyType = csdefine.SPECIALSHOP_MONEY_TYPE_GOLD	# 角色当前使用的货币类型

	def spe_reset( self ):
		"""
		重置商城数据
		"""
		self.specialItemData = { csdefine.SPECIALSHOP_MONEY_TYPE_GOLD: {},
								csdefine.SPECIALSHOP_MONEY_TYPE_SILVER: {},
							}
																				# ( 查询数据, 上次查询时间 )
		self.goodsTypeMap = { 	csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:{
									csdefine.SPECIALSHOP_RECOMMEND_GOODS : [ [], 0 ],	# 推荐商品
									csdefine.SPECIALSHOP_ESPECIAL_GOODS  : [ {csdefine.SPECIALSHOP_SUBTYPE_MOS_CRYSTAL:[], csdefine.SPECIALSHOP_SUBTYPE_VAL_GOODS:[]}, 0 ],	# 天材地宝
									csdefine.SPECIALSHOP_CURE_GOODS      : [ {csdefine.SPECIALSHOP_SUBTYPE_EXP_GOODS:[], csdefine.SPECIALSHOP_SUBTYPE_REST_GOODS:[]}, 0 ],	# 恢复类商品
									csdefine.SPECIALSHOP_REBUILD_GOODS   : [ [], 0 ],	# 打造材料
									csdefine.SPECIALSHOP_VEHICLE_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_LAND_VEHICLE:[],csdefine.SPECIALSHOP_SUBTYPE_SKY_VEHICLE:[], csdefine.SPECIALSHOP_SUBTYPE_VEHICLE_PROPS:[]}, 0 ],	# 坐骑类商品
									csdefine.SPECIALSHOP_PET_GOODS       : [ {csdefine.SPECIALSHOP_SUBTYPE_PET_BOOK:[], csdefine.SPECIALSHOP_SUBTYPE_PET_PROPS:[], csdefine.SPECIALSHOP_SUBTYPE_PET_EGG:[]}, 0 ],	# 宠物类商品
									csdefine.SPECIALSHOP_FASHION_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_MALE_FASHION:[], csdefine.SPECIALSHOP_SUBTYPE_FEMALE_FASHION:[]}, 0 ],	# 时装类商品
									csdefine.SPECIALSHOP_ENHANCE_GOODS 	 : [ [], 0 ],	# 强化材料
									csdefine.SPECIALSHOP_CRYSTAL_GOODS 	 : [ [], 0 ],	# 镶嵌水晶
									csdefine.SPECIALSHOP_TALISMAN_GOODS  : [ [], 0 ],	# 法宝神器
								},
								csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:{
									csdefine.SPECIALSHOP_RECOMMEND_GOODS : [ [], 0 ],	# 推荐商品
									csdefine.SPECIALSHOP_ESPECIAL_GOODS  : [ {csdefine.SPECIALSHOP_SUBTYPE_MOS_CRYSTAL:[], csdefine.SPECIALSHOP_SUBTYPE_VAL_GOODS:[]}, 0 ],	# 天材地宝
									csdefine.SPECIALSHOP_CURE_GOODS      : [ {csdefine.SPECIALSHOP_SUBTYPE_EXP_GOODS:[], csdefine.SPECIALSHOP_SUBTYPE_REST_GOODS:[]}, 0 ],	# 恢复类商品
									csdefine.SPECIALSHOP_REBUILD_GOODS   : [ [], 0 ],	# 打造材料
									csdefine.SPECIALSHOP_VEHICLE_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_LAND_VEHICLE:[],csdefine.SPECIALSHOP_SUBTYPE_SKY_VEHICLE:[], csdefine.SPECIALSHOP_SUBTYPE_VEHICLE_PROPS:[]}, 0 ],	# 坐骑类商品
									csdefine.SPECIALSHOP_PET_GOODS       : [ {csdefine.SPECIALSHOP_SUBTYPE_PET_BOOK:[], csdefine.SPECIALSHOP_SUBTYPE_PET_PROPS:[], csdefine.SPECIALSHOP_SUBTYPE_PET_EGG:[]}, 0 ],	# 宠物类商品
									csdefine.SPECIALSHOP_FASHION_GOODS   : [ {csdefine.SPECIALSHOP_SUBTYPE_MALE_FASHION:[], csdefine.SPECIALSHOP_SUBTYPE_FEMALE_FASHION:[]}, 0 ],	# 时装类商品
									csdefine.SPECIALSHOP_ENHANCE_GOODS 	 : [ [], 0 ],	# 强化材料
									csdefine.SPECIALSHOP_CRYSTAL_GOODS 	 : [ [], 0 ],	# 镶嵌水晶
									csdefine.SPECIALSHOP_TALISMAN_GOODS  : [ [], 0 ],	# 法宝神器
								}
							}

	def getSpeMoneyType( self ):
		"""
		获得当前的货币类型
		"""
		return self.spe_moneyType

	def setSpeMoneyType( self, moneyType ):
		"""
		设置当前的货币类型
		"""
		self.spe_moneyType = moneyType

	def spe_queryGoods( self, queryType, moneyType ):
		"""
		查询商城商品

		@param queryType : 查询类型
		@type queryType : UINT16
		"""
		if not self.spe_updateState or self.spe_moneyType != moneyType:
			self.spe_updateGoods( moneyType )
			self.spe_updateState = True
			
	def spe_updateGoods( self, moneyType ):
		"""
		向服务器请求更新商城物品数据
		"""
		interval = 0.0
		for goodsType in csconst.SPECIALSHOP_GOOS_LIST:
			BigWorld.callback( interval, Functor( self.base.spe_updateGoods, goodsType, moneyType ) )
			interval += UPDATE_DELAY_TIME
			
	def spe_receiveGoods( self, goodsData, queryType, moneyType ):
		"""
		Define method.
		接收商品数据
		
		@param goodsData : [ 物品id, 物品类型, 物品价, 物品描述 ]
		@type goodsData : [ ITEM_ID, INT, INT, STRING ]
		"""
		if moneyType not in self.goodsTypeMap:
			ERROR_MSG( "不存在(%i)类型的商城。" % moneyType )
			return
		if queryType not in self.goodsTypeMap[moneyType]:
			ERROR_MSG( "不存在(%i)类型的商品。" % queryType )
			return
		itemID = goodsData[0]
		subType = goodsData[-1]
		itemsDict = self.goodsTypeMap[moneyType][ queryType ][0]
		if subType in itemsDict: #有子分类
			itemsDict[subType].append( itemID )
		else:
			if isinstance( itemsDict,dict ) and subType < 0:
				ERROR_MSG( "商品配置有误，物品%d属于%d大类，请指定子类！"%( itemID, queryType ))
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
		商城关闭的通知
		"""
		self.spe_updateState = False
		self.spe_reset()
		ECenter.fireEvent( "EVT_ON_SPECIALSHOP_CLOSED" )
		
	def spe_shopping( self, itemID, amount, moneyType ):
		"""
		买一个物品
		"""
		itemsDict = self.specialItemData.get( csdefine.SPECIALSHOP_MONEY_TYPE_GOLD, {} )
		if Language.LANG == Language.LANG_BIG5:
			itemsDict = self.specialItemData.get( moneyType, {} )
		if itemID not in itemsDict:
			return
		# 判断玩家是否够钱买，在cell上并无物品价格数据，因此必须在这里先判断
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
		申请物品价格
		"""
		prices = {}
		for itemID in itemIDs :										# 首先搜索客户端，看是否又指定物品的
			if itemID in self.specialItemData :
				item = self.specialItemData[itemID]
				prices[itemID] = ( csdefine.SPECIALSHOP_REQ_SUCCESS, item[2] )
			else :
				self.base.spe_requestItemsPrices( itemIDs, self.spe_moneyType )			# 如果客户端缺少物品，则向服务器申请
				return
		ECenter.fireEvent( "EVT_ON_SPECIAL_GET_ITEMS_PRICES", prices )

	def spe_onReceiveItemsPrices( self, prices ) :
		"""
		收到物品价格
		hyw--2009.03.27
		"""
		ECenter.fireEvent( "EVT_ON_SPECIAL_GET_ITEMS_PRICES", prices )
