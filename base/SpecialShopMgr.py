# -*- coding: gb18030 -*-
#


from bwdebug import *
import Language
import csdefine
import Language

SUBTYPE_MAPS = { csdefine.SPECIALSHOP_ESPECIAL_GOODS: [
																	csdefine.SPECIALSHOP_SUBTYPE_MOS_CRYSTAL,
																	csdefine.SPECIALSHOP_SUBTYPE_VAL_GOODS
																	],
					csdefine.SPECIALSHOP_CURE_GOODS:			[
																	csdefine.SPECIALSHOP_SUBTYPE_EXP_GOODS,
																	csdefine.SPECIALSHOP_SUBTYPE_REST_GOODS
																	],
					csdefine.SPECIALSHOP_VEHICLE_GOODS:		[
																	csdefine.SPECIALSHOP_SUBTYPE_LAND_VEHICLE,
																	csdefine.SPECIALSHOP_SUBTYPE_SKY_VEHICLE,
																	csdefine.SPECIALSHOP_SUBTYPE_VEHICLE_PROPS
																	],
					csdefine.SPECIALSHOP_PET_GOODS:			[
																	csdefine.SPECIALSHOP_SUBTYPE_PET_BOOK,
																	csdefine.SPECIALSHOP_SUBTYPE_PET_PROPS,
																	csdefine.SPECIALSHOP_SUBTYPE_PET_EGG
																	],
					csdefine.SPECIALSHOP_FASHION_GOODS:		[
																	csdefine.SPECIALSHOP_SUBTYPE_MALE_FASHION,
																	csdefine.SPECIALSHOP_SUBTYPE_FEMALE_FASHION
																	]
				}


class SpecialItem:
	"""
	道具商城商品
	"""
	def __init__( self, itemID, itemType, goldPrice, silverPrice, description, subType ):
		"""
		itemID : 物品id
		type : 商品分类
		price : 价格
		"""
		self.itemID = itemID
		self.type = itemType
		self.goldPrice = goldPrice
		self.silverPrice = silverPrice
		self.description = description
		self.subType = subType
		
		
	def getDataList( self, moneyType ):
		"""
		获得物品数据
		@return [ self.itemID, self.type, self.price ]
		"""
		dataList = []
		if Language.LANG == Language.LANG_BIG5:
			if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_GOLD and self.goldPrice >= 0:
				dataList = [ self.itemID, self.type, self.goldPrice, self.description, moneyType, self.subType ]
			if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER and self.silverPrice >= 0:
				dataList = [ self.itemID, self.type, self.silverPrice, self.description, moneyType, self.subType ]
		else:
			dataList = [ self.itemID, self.type, self.goldPrice, self.description, self.subType ]
		return dataList
	def getPrice( self, moneyType ):
		"""
		"""
		if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:
			return self.goldPrice
		elif moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:
			return self.silverPrice
		
		
class SpecialShopMgr:
	"""
	道具商城配置管理
	"""
	_instance = None
	
	def __init__( self ):
		"""
		"""
		assert SpecialShopMgr._instance is None, "there's aready a instance exist!"
		self.data = {}
		self.reconmmentHotGoods = []# 官方推荐热销商品
		self.recommentGoods = []	# 推荐商品
		self.especialGoods = []		# 天才地宝
		self.cureGoods = []			# 灵丹妙药
		self.rebuildGoods = []		# 打造材料
		self.vehicleGoods = []		# 坐骑商城
		self.petGoods = []			# 仙宠商城
		self.fashionGoods = []		# 时装类商品
		self.enhanceGoods = []		# 强化材料
		self.talismanGoods = []		# 法宝神器
		self.crystalGoods = []		# 镶嵌水晶
		
		self.goodsTypeMap = { csdefine.SPECIALSHOP_RECOMMEND_GOODS : self.recommentGoods,
							csdefine.SPECIALSHOP_ESPECIAL_GOODS  : self.especialGoods,
							csdefine.SPECIALSHOP_CURE_GOODS      : self.cureGoods,
							csdefine.SPECIALSHOP_REBUILD_GOODS   : self.rebuildGoods,
							csdefine.SPECIALSHOP_VEHICLE_GOODS   : self.vehicleGoods,
							csdefine.SPECIALSHOP_PET_GOODS       : self.petGoods,
							csdefine.SPECIALSHOP_FASHION_GOODS   : self.fashionGoods,
							csdefine.SPECIALSHOP_ENHANCE_GOODS   : self.enhanceGoods,
							csdefine.SPECIALSHOP_TALISMAN_GOODS  : self.talismanGoods,
							csdefine.SPECIALSHOP_CRYSTAL_GOODS   : self.crystalGoods,
							}
							
	@classmethod
	def instance( self ):
		if SpecialShopMgr._instance is None:
			SpecialShopMgr._instance = SpecialShopMgr()
		return SpecialShopMgr._instance
		
	def load( self, xmlConfig ):
		"""
		加载配置
		"""
		section = Language.openConfigSection( xmlConfig )
		if section is None:
			raise SystemError,"cannot load %s." % xmlConfig
			
		for item in section.values():
			itemID = item.readInt( "itemID" )
			tempType = item.readInt( "type" )
			subType = item.readInt( "subType" )
			activate = bool( item.readInt( "activate" ) )
			if not activate: continue
			if itemID in self.data:
				ERROR_MSG( "itemID(%i) has already in data."%( itemID ) )
				continue
			if tempType&csdefine.SPECIALSHOP_GOODS_TYPES != tempType:				#商品类型不在大类中
				ERROR_MSG( "not exit goods(%i) width type(%i)."%( itemID, tempType) )
				continue
			else: 																	#商品类型在大类
				if tempType in SUBTYPE_MAPS and \
				not subType in SUBTYPE_MAPS[tempType]:						#但子类不属于大类的子类范围
					ERROR_MSG( "goods(%i) subtype(%i) not exit in type(%i)."%( itemID, subType, tempType) )
					continue
			tempItem = SpecialItem( itemID, tempType, item.readInt( "goldPrice" ), item.readInt( "silverPrice" ), item.readString( "description" ), subType )
			self.data[itemID] = tempItem
			
			if tempType & csdefine.SPECIALSHOP_RECOMMEND_GOODS:	# 推荐商品
				self.recommentGoods.append( tempItem )
			if tempType & csdefine.SPECIALSHOP_ESPECIAL_GOODS:	# 天财地宝
				self.especialGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_CURE_GOODS:	# 恢复类商品
				self.cureGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_REBUILD_GOODS:	# 打造材料
				self.rebuildGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_VEHICLE_GOODS:	# 骑宠类商品
				self.vehicleGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_PET_GOODS:		# 宠物类商品
				self.petGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_FASHION_GOODS:	# 时装类商品
				self.fashionGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_ENHANCE_GOODS:	# 强化材料
				self.enhanceGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_TALISMAN_GOODS:# 法宝神器
				self.talismanGoods.append( tempItem )
			elif tempType & csdefine.SPECIALSHOP_CRYSTAL_GOODS:	# 镶嵌水晶
				self.crystalGoods.append( tempItem )
				
	def getItemPrice( self, itemID, amount, moneyType ):
		"""
		玩家询价，根据itemID返回物品价格，如果不存在物品则返回-1
		
		@param itemID : 物品id
		@type itemID : ITEM_ID
		@param amount : 欲购买的数量
		@type amount : INT32
		"""
		try:
			price = self.data[itemID].getPrice( moneyType )
		except KeyError:
			return -1
		else:
			return price * amount if price >= 0 else -1
			
	def requestItemsPrices( self, player, itemIDs, moneyType ) :
		"""
		请求发送物品价格
		"""
		prices = {}
		for itemID in itemIDs :
			state = csdefine.SPECIALSHOP_REQ_FAIL_NOT_EXIST
			prices[itemID] = ( state, 0 )
			if itemID in self.data :
				state = csdefine.SPECIALSHOP_REQ_SUCCESS
				item = self.data[itemID]
				prices[itemID] = ( state, item.getPrice( moneyType ) )
		player.client.spe_onReceiveItemsPrices( prices )
		
	def updateGoods( self, player, queryType, moneyType ):
		"""
		玩家请求更新商城物品信息
		
		@param player : 查询玩家
		@type player : ENTITY
		@param queryType : 按哪种类型查询商城道具
		@type queryType : UINT32
		"""
		if not self.isOpen():
			player.statusMessage( csstatus.SPECIALSHOP_IS_NOT_OPEN )
			return
		for item in self.goodsTypeMap[ queryType ]:
			goodsData = item.getDataList( moneyType )
			if len( goodsData ) > 0:
				player.client.spe_receiveGoods( goodsData, queryType, moneyType )
			
	def isOpen( self ):
		return True
		
specialShop = SpecialShopMgr.instance()
