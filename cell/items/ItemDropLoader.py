# -*- coding: gb18030 -*-

#$Id: ItemDropLoader.py,v 1.16 2008-08-09 09:31:10 wangshufeng Exp $

from bwdebug import *
from MsgLogger import g_logger
import Language
import random
import items
import Const
import ItemTypeEnum
import time
import sys
from SmartImport import smartImport

g_items = items.instance()

from config.server.droppedItem import	eq_wieldType
from config.server.droppedItem import	equip_quality
from config.server.droppedItem import	LuckyBoxItemDropZhaocai
from config.server.droppedItem import	LuckyBoxItemDropJinbao
from config.server.droppedItem import	EquipMakeDropAmend
from config.server.droppedItem import	SpecialDropAmend
from config.server.droppedItem import	lotteryDropAmend
from config.server.droppedItem import	TreasureBoxDrops
from config.server.droppedItem import	HonorItemZhaocai
from config.server.droppedItem import	HonorItemJinbao


# ----------------------------------------------------------------------------------------------------
# 物品世界掉落加载
# ----------------------------------------------------------------------------------------------------
class ItemDropInWorldLoader:
	"""
	物品世界掉落加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert ItemDropInWorldLoader._instance is None, "instance already exist in"
		self.tidyDatas = equip_quality.Datas # 根据不同的品质分开存储 like { quality:{ npcLevel : { "items" : [ ( itemID, quality, prefix, dropOdds ),...],"totalDropOdds" : alDropOdds } } ,{ quality: .........} }
		self.specialDatas = eq_wieldType.Datas # 根据不同的品质等级和部位分开存储

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = ItemDropInWorldLoader()
		return self._instance

	def getDropItems( self, npcLevel ):
		"""
		根据怪物等级获取怪物掉落信息
		@type  npcLevel: INT
		@param npcLevel: 怪物等级
		@return [ ( itemID, quality, prefix, dropOdds )... ]
		"""
		try:
			datas = []
			for tidyDatas in self.tidyDatas.itervalues():
				datas.append( ( tidyDatas[npcLevel]["items"], tidyDatas[npcLevel]["totalDropOdds"] ) )		#like ( [物品信息], 总掉率  )
			return datas
		except KeyError:
			return []

	def getDropOdds( self, npcLevel ):
		"""
		获取指定等级的装备掉率
		"""
		odds = 0.0
		for tidyDatas in self.tidyDatas.itervalues():
			odds += tidyDatas[npcLevel]["totalDropOdds"]
		return odds

	def randomValue( self, quality, npcLevel ):
		"""
		随机一个该等级总掉率以内的值
		"""
		try:
			return random.random() * self.tidyDatas[ quality ][ npcLevel ][ "totalDropOdds" ]
		except:
			try:
				g_logger.itemDropExceptLog( "in ItemDropInWorldLoader Drop a not exist Item, Info: quality %s, npcLevel %s" % ( quality, npcLevel ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return -1.0


	def getItem( self, quality, npcLevel ):
		"""
		根据掉率值获取掉落的物品
		"""
		odds = self.randomValue( quality, npcLevel )
		if odds == -1.0:
			return None
		for item in self.tidyDatas[ quality ][ npcLevel ][ "items" ]:
			if odds <= item[3]:
				return item
		try:
			g_logger.itemDropExceptLog( "in ItemDropInWorldLoader, can not drop this item : odds(%s), quality(%s), npcLevel(%s)" %( odds,quality,npcLevel ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return None

	def specialRandomValue( self, quality, npcLevel, eq_wieldType ):
		"""
		随机一个该等级总掉率以内的值（特殊怪）
		"""
		try:
			return random.random() * self.specialDatas[ quality ][ npcLevel ][ eq_wieldType ][ "totalDropOdds" ]
		except:
			try:
				g_logger.itemDropExceptLog( "in ItemDropInWorldLoader Drop a not exist Item, Info: quality %s, npcLevel %s, eq_wieldType %s" % ( quality, npcLevel, eq_wieldType )  )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return -1.0

	def getSpecialItem( self, quality, npcLevel, eq_wieldType ):
		"""
		根据掉率值获取掉落的物品（特殊怪）
		"""
		odds = self.specialRandomValue( quality, npcLevel, eq_wieldType )
		if odds == -1.0:
			return None
		for item in self.specialDatas[ quality ][ npcLevel ][ eq_wieldType ][ "items" ]:
			if odds <= item[3]:
				return item
		try:
			g_logger.itemDropExceptLog( "in ItemDropInWorldLoader, can not drop this item : odds(%s), quality(%s), npcLevel(%s), eq_wieldType(%s)" %( odds,quality,npcLevel,eq_wieldType ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return None

	def getSpecialwieldTypeList( self, quality, npcLevel ):
		"""
		根据品质和等级获取掉落的装备部位列表（特殊怪）
		"""
		try:
			return self.specialDatas[ quality ][ npcLevel ].keys()
		except:
			try:
				g_logger.itemDropExceptLog( "in ItemDropInWorldLoader, can not drop a level items : quality(%s), npcLevel(%s)" % ( quality, npcLevel ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return []

	def getDropItemsEx( self, quality, npcLevel):
		"""
		根据怪物等级获取怪物掉落信息中的指定品质的物品的掉落信息
		"""
		try:
			return self.tidyDatas[quality][npcLevel]["items"]
		except KeyError:
			return []

	def getItemsTotalOddsEx( self, quality, npcLevel ):
		"""
		根据怪物等级获取怪物掉落信息中的指定品质的物品的该级别的掉落概率总和
		@type  npcLevel: INT
		@param npcLevel: 怪物等级
		@return [ ( itemID, quality, prefix, dropOdds )... ]
		"""
		try:
			return self.tidyDatas[quality][npcLevel]["totalDropOdds"]
		except KeyError:
			return 0.0

	def getItemByClass( self, quality, npcLevel, playerClass ):
		"""
		抽取相应品质、等级、职业的装备
		"""
		itemList = []
		for item in self.tidyDatas[ quality ][ npcLevel ][ "items" ]:
			itemID = item[0]
			if g_items[itemID]['reqClasses'] == [ playerClass ] and not itemID in itemList:
				itemList.append( itemID )
		return itemList

# ----------------------------------------------------------------------------------------------------
# 普通怪物杂物掉落加载
# ----------------------------------------------------------------------------------------------------
class ItemDropSundriesLoader:
	"""
	杂物掉落加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	def __init__( self, pyconfig ):
		self._datas = pyconfig.Datas # like as { npcID : { itemID : { "odds" : odds, "amount" : amount, "multiOdds" : multiOdds }, ... } }

	def getDropItemInfo( self, monsterID ):
		"""
		获取怪物掉落信息
		@type  monsterID: String
		@param monsterID: 怪物类型
		"""
		try:
			return self._datas[monsterID]["items"]
		except:
			WARNING_MSG( "Can't Find SunbriesItemDrop config By %s" % monsterID )
			return []

	def getMaxOdds( self, monsterID ):
		"""
		获取怪物所有掉落物品暴率总和，用于权重计算
		@type  monsterID: String
		@param monsterID: 怪物类型
		@return Float
		"""
		try:
			return self._datas[monsterID]["maxOdds"]
		except:
			WARNING_MSG( "Can't Find MaxOdds config By %s" % monsterID )
			return 0

	def getMultiOdds( self, monsterID, itemID ):
		"""
		获取掉落多个物品的掉落率修正
		@type  monsterID: String
		@param monsterID: 怪物类型
		@type  itemID: ITEM_ID
		@param itemID: 物品ID
		"""
		try:
			return self._datas[monsterID]["multiOdds"][itemID]
		except:
			WARNING_MSG( "Can't Find modifyOdds config By %s" % monsterID )
			return 0

	def getModifyDropAmount( self, monsterID, amount, itemID ):
		"""
		当怪物掉落的杂物大于1个时候，有一个参数用于控制掉落数量
		例如：某怪物会掉落一种杂物2个以上，那么它有一个参数用于控制
		该怪物的杂物掉落。这个参数是一个概率值，比如为 70% ，那么
		这个怪物掉落这种杂物一个时是100%出的，掉2个是70%出，掉
		3个是49%出....以此类推
		@type  monsterID: String
		@param monsterID: 怪物类型
		@type  amount: Int
		@param amount: 物品数量
		"""
		if amount == 1: return amount
		dropAmount = 0
		multiOdds = self.getMultiOdds( monsterID, itemID )
		r = random.random()
		for index in xrange( 1, amount ):
			if r <= ( multiOdds ** index ):
				dropAmount = index
		return dropAmount + 1

	def getDropItem( self, monster):
		"""
		获取掉落的物品
		"""
		monsterID = monster.className
		sundriesDropInfo = self.getDropItemInfo( monsterID )
		maxOdds = self.getMaxOdds( monsterID )
		r = random.random() * maxOdds
		for itemID, amount, odds in sundriesDropInfo:
			if r <= odds:
				dropAmount = self.getModifyDropAmount( monsterID, amount, itemID )
				tempItem =  g_items.createDynamicItem( int( itemID ) , dropAmount )
				if tempItem is None:
					continue
				return tempItem
		return None


# ----------------------------------------------------------------------------------------------------
# 宝箱掉落收费道具物品加载
# ----------------------------------------------------------------------------------------------------
class ItemDropTreasureBoxLoader:
	"""
	宝箱掉落收费道具物品加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert ItemDropTreasureBoxLoader._instance is None, "instance already exist in"
		self._datas = TreasureBoxDrops.Datas	# like as { npcID : { "items" : [ ( itemID, quality, prefix ),...], "amendOdds" : amendOdds } ,..... }


	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = ItemDropTreasureBoxLoader()
		return self._instance


	def getDropItems( self, boxLevel ):
		"""
		根据怪物等级获取怪物掉落信息
		@type  boxLevel: INT
		@param boxLevel: 宝箱等级
		@return [ ( itemID, quality, prefix, dropRate )... ]
		"""
		try:
			return self._datas[boxLevel]
		except KeyError:
			ERROR_MSG("has no item boxLevel = %s" % boxLevel )
			return []

	def randomValue( self, boxLevel ):
		"""
		随机一个该等级总掉率以内的值
		"""
		try:
			return random.random() * self._datas[ boxLevel][-1][1]		# format [(id,odds,amount)] -1表示最后一列，1代表掉落，最后一列的第二个索引值为总掉率
		except:
			ERROR_MSG( "can not find  item  boxLevel(%s)" % boxLevel )
			return -1.0

	def getEquipDropInfo( self , level, quality ):
		"""
		获取最有可能的装备掉落
		"""
		worldDrop =  ItemDropInWorldLoader.instance()
		data = worldDrop.getItem( quality, level )
		return data

	def getDropItem( self, boxLevel):
		"""
		获取掉落的物品
		"""
		dropDatas = self.getDropItems( boxLevel )
		if len( dropDatas ) == 0:
			return None
		dropRate  = self.randomValue( boxLevel )
		if dropRate < 0.0:
			return None
		for itemID, dropOdds, dropAmount in dropDatas:
			if dropRate <= dropOdds:
				if itemID.startswith( "equip_quality" ): #如果是装备
					quality = int( itemID[-1] )
					itemInfo = self.getEquipDropInfo( boxLevel, quality ) #itemInfo 格式 ( itemID, quality, prefix, odds )
					if not itemInfo:
						ERROR_MSG( "can not get equip level = %s, quality = %s " % (boxLevel, quality) )
						return None
					itemInst = g_items.createDynamicItem( int( itemInfo[0] ) , 1 )		# 装备固定只出一个 不读取配置，避免配置错误。
					if itemInst is None:
						ERR0R_MSG( "Create Equip Error, item id = %s " % itemInfo[0]  )
						return None
					if itemInfo[1] !=0 and itemInfo[2] != 0:
						itemInst.setQuality( itemInfo[1] )
						itemInst.setPrefix( itemInfo[2] )
						if not itemInst.createRandomEffect():
							DEBUG_MSG( "getDropItem createRandomEffect failed, item %s, quality %s, prefix %s " % ( itemInfo[0], itemInfo[1], itemInfo[2] ) )
					return itemInst
				else:
					itemInst = g_items.createDynamicItem( int( itemID ) , dropAmount )
					if itemInst is None:
						ERR0R_MSG( "Create Equip Error, item id = %s " % itemInfo[0]  )
						return None
					return itemInst
		return  None

# --------------------------------------------------------------------------------------------
# 天降宝盒掉落.15:59 2009-1-12,wsf
# --------------------------------------------------------------------------------------------
class LuckyBoxDrop:
	"""
	天降宝盒掉落数据基类
	"""
	def __init__( self, dictDat ):
		"""
		@param		dictDat: 配置数据
		@type		dictDat: python dictDat
		"""
		self.dtype = dictDat[ "drop_type" ]	# 掉落类型
		self.level = dictDat[ "level" ]		# 对应的天降宝盒级别
		self.rate = dictDat[ "rate" ]		# 掉落概率
		self.rateNode = 0.0							# 掉率所在节点

	def getDropData( self ):
		"""
		Virtual method.
		获得掉落数据，子类必须重写此方法
		"""
		try:
			g_logger.itemDropExceptLog( "this is virtual method.-->>>" )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setRateNode( self, rateNode ):
		"""
		决定掉落哪个物品的规则是 在级别对应的总掉率范围随机一个数值，而每一个掉落实例都有自己所在的掉率范围
		如果此随机数在某个掉落实例的掉率范围内则表明掉落的将是此实例。

		仅存储掉落范围的最大值，因为判断的实现从最小值开始判断，直到找到合适的掉落实例。

		@type rateNode : FLOAT
		"""
		self.rateNode = rateNode

	def getRateNode( self ):
		"""
		@type rateNode : FLOAT
		"""
		return self.rateNode


class LuckyBoxDropItem( LuckyBoxDrop ):
	"""
	天降宝盒掉落物品
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		self.itemID = int( dictDat[ "param" ] )


	def getDropData( self ):
		"""
		"""
		tempItem = items.instance().createDynamicItem( self.itemID )
		return ( self.dtype, tempItem )


class LuckyBoxDropAmount( LuckyBoxDrop ):
	"""
	天降宝盒掉落数值，适用于经验、潜能、金钱。由于根据dtype可以区分此3种掉落，因此3种都使用此类。
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		self.amount = int( dictDat[ "param" ] )	# 经验/潜能/金钱


	def getDropData( self ):
		"""
		"""
		return ( self.dtype, self.amount )


class LuckyBoxDropEquip( LuckyBoxDrop ):
	"""
	天降宝盒掉落：a-b级c品质的武器。例如：1-3级的蓝装
	10级箱子掉落的品质2级以上武器同10级怪物的掉落，10:21 2009-1-14，wsf
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		tempList = dictDat["param"].split( "|" )
		self.quality = int( tempList[0] )
		self.lowLevel = int( tempList[1] )
		self.highLevel = int( tempList[2] )


	def getDropData( self ):
		"""
		10级箱子掉落的品质2级以上武器同10级怪物的掉落10:21 2009-1-14，wsf
		世界掉落的总表已提供此接口，获得武器的方式。
		"""
		#level = random.randint( self.lowLevel, self.highLevel )
		itemData = ItemDropInWorldLoader.instance().getItem( self.quality, self.level )	# ( itemID, quality, prefix, dropOdds )
		item = items.instance().createDynamicItem( int( itemData[ 0 ] ) )
		item.set( "quality", itemData[ 1 ] )
		item.set( "prefix", itemData[2] )
		if not item.createRandomEffect():
			DEBUG_MSG( "getDropData createRandomEffect failed, item %s, quality %s, prefix %s " % ( itemData[0], itemData[1], itemData[2] ) )
		return ( self.dtype, item )


class HonorItem( LuckyBoxDrop ):
	"""
	荣誉度兑换物品
	"""
	def __init__( self, dictDat ):
		"""
		"""
		LuckyBoxDrop.__init__( self, dictDat )
		self.itemID = int( dictDat[ "param" ] )
		self.count	= int( dictDat[ "count" ] )


	def getDropData( self ):
		"""
		"""
		tempItem = items.instance().createDynamicItem( self.itemID, max( self.count, 1 ) )
		return ( self.dtype, tempItem )

# 建立一个掉落类型的类映射
LUCKY_DROP_ITEM_MAP = {	Const.LUCKY_BOX_DROP_NORMAL_ITEM : LuckyBoxDropItem,
						Const.LUCKY_BOX_DROP_EQUIP : LuckyBoxDropEquip,
						Const.LUCKY_BOX_DROP_MONEY : LuckyBoxDropAmount,
						Const.LUCKY_BOX_DROP_POTENTIAL : LuckyBoxDropAmount,
						Const.LUCKY_BOX_DROP_EXP : LuckyBoxDropAmount,
						Const.HONOR_ITEM	: HonorItem,
						}


class ItemDropLuckyBoxZhaocai:
	"""
	天降宝盒:招财，掉落配置加载
	"""
	_instance = None
	#从config.server.droppedItem.LuckyBoxItemDropZhaocai.Datas 数据源初始化该实例
	_datas		= LuckyBoxItemDropZhaocai.Datas

	def __init__( self ):
		"""
		"""
		assert ItemDropLuckyBoxZhaocai._instance is None,"Just allow only one instance exist!!"

		self._levelMapRate = {}	# 级别对应的总掉率，用于限制获得随机数的范围{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# 存放掉落物品的配置数据{ 级别1:{ 概率段最大值1:掉落实例1,概率段最大值2:掉落实例2,...}, ... }

		ItemDropLuckyBoxZhaocai._instance = self
		self.init( )


	@classmethod
	def instance( self ):
		"""
		"""
		if ItemDropLuckyBoxZhaocai._instance is None:
			ItemDropLuckyBoxZhaocai._instance = ItemDropLuckyBoxZhaocai()
		return ItemDropLuckyBoxZhaocai._instance

	def init( self ):
		"""
		"""
		for i in xrange( len( self._datas ) ):
			node = self._datas[ i ]
			dtype = node["drop_type"]
			level = node["level"]
			rate = node["rate"]
			if not self._data.has_key( level ):
				self._data[ level ] = []
			if not self._levelMapRate.has_key( level ):
				self._levelMapRate[ level ] = 0.0
			levelDropTable = self._data[ level ]
			self._levelMapRate[ level ] += rate
			dropInstance = LUCKY_DROP_ITEM_MAP[ dtype ]( node )
			dropInstance.setRateNode( self._levelMapRate[ level ] )
			levelDropTable.append( dropInstance )


	def getDropData( self, level ):
		"""
		根据宝盒的等级获得掉落数据

		@param level : 宝盒级别
		@type level : UINT16
		@return ( 宝盒掉落类型, 掉落数据 )
		"""
		totalRate = self._levelMapRate[ level ]	# 级别对应的总掉率，会在此掉率范围随机确定会掉落何种物品
		dropRate = random.random() * totalRate
		for dropInstace in self._data[ level ]:
			if dropRate < dropInstace.getRateNode():
				return dropInstace.getDropData()


class ItemDropLuckyBoxJinbao:
	"""
	天降宝盒:进宝，掉落配置加载
	"""
	_instance 	= None
	#从config.server.droppedItem.LuckyBoxItemDropJinbao.Datas 数据源初始化该实例
	_datas 		= LuckyBoxItemDropJinbao.Datas

	def __init__( self ):
		"""
		"""
		assert ItemDropLuckyBoxJinbao._instance is None,"Just allow only one instace exist!!"
		ItemDropLuckyBoxJinbao._instance = self

		self._levelMapRate = {}	# 级别对应的总掉率，用于限制获得随机数的范围{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# 存放掉落物品的配置数据{ 级别1:{ 概率段最大值1:掉落实例1,概率段最大值2:掉落实例2,...}, ... }
		self.init( )

	@classmethod
	def instance( self ):
		"""
		"""
		if ItemDropLuckyBoxJinbao._instance is None:
			ItemDropLuckyBoxJinbao._instance = ItemDropLuckyBoxJinbao()
		return ItemDropLuckyBoxJinbao._instance

	def init( self ):
		"""
		"""
		for i in xrange( len( self._datas ) ):
			node = self._datas[ i ]
			dtype = node["drop_type"]
			level = node["level"]
			rate = node["rate"]
			if not self._data.has_key( level ):
				self._data[ level ] = []
			if not self._levelMapRate.has_key( level ):
				self._levelMapRate[ level ] = 0.0
			levelDropTable = self._data[ level ]
			self._levelMapRate[ level ] += rate
			dropInstance = LUCKY_DROP_ITEM_MAP[ dtype ]( node )
			dropInstance.setRateNode( self._levelMapRate[ level ] )
			levelDropTable.append( dropInstance )


	def getDropData( self, level ):
		"""
		根据宝盒的等级获得掉落数据

		@param level : 宝盒级别
		@type level : UINT16
		@return ( 宝盒掉落类型, 掉落数据 )
		"""
		totalRate = self._levelMapRate[ level ]	# 级别对应的总掉率，会在此掉率范围随机确定会掉落何种物品
		dropRate = random.random() * totalRate
		for dropInstace in self._data[ level ]:
			if dropRate < dropInstace.getRateNode():
				return dropInstace.getDropData()

# ----------------------------------------------------------------------------------------------------
# 锦囊的物品掉落配置加载
# ----------------------------------------------------------------------------------------------------
class ItemDropLotteryLoader:

	"""
	锦囊的物品掉落配置加载
	"""

	_instance = None

	def __init__( self ):
		"""
		初始化，加载掉落数据
		@type  xmlConfig : STRING
		@param xmlConfig : 配置的路径
		"""
		assert ItemDropLotteryLoader._instance is None, "instance already exist in"
		self.__datas   = lotteryDropAmend.Datas #存储掉率数据
		self.totalodds = lotteryDropAmend.Totalodds #记录总的掉落率

	def getDropDatas( self ):
		"""
		获取存储的掉落数据
		"""
		return self.__datas

	def gettotalodds( self, fact ):
		"""
		获取真实掉率或者显示掉率的总掉率
		"""
		odds = "fact_odds"
		if not fact:
			odds = "falsity_odds"
		return self.totalodds[ odds ]

	def getItemLevel( self, itemID ):
		"""
		根据物品的ID，获取该物品在锦囊掉落中的等级。该物品必须锦囊掉落出的物品，不然没有意义
		"""
		for item in self.__datas:
			if item["id"] == str(itemID):
				return item["itemLevel"]
		return 6		#如果没有找到这个ID 说明它是装备(因为该物品本身就是从锦囊掉落出随机出来的)

	def randomValue( self, fact, valueLimit = 0 ):
		"""
		按照掉率的类型随机一个数据
		"""
		odds = "fact_odds"
		if not fact:
			odds = "falsity_odds"
		if valueLimit == 0:
			limit = self.totalodds[ odds ]
		else:
			limit = valueLimit

		randomValue = random.random()
		randomValue = randomValue * limit

		return randomValue

	def getEquipDropInfo( self , level ):
		"""
		获取最可能的粉色装备的掉落的信息
		"""
		worldDrop =  ItemDropInWorldLoader.instance()
		data = worldDrop.getItem( 4, level )
		return data

	@classmethod
	def instance( self ):
		"""
		返回程序的实例
		"""
		if self._instance is None:
			self._instance = ItemDropLotteryLoader()
		return self._instance

# ----------------------------------------------------------------------------------------------------
# 制作卷的掉落加载
# ----------------------------------------------------------------------------------------------------
class EquipMakeDropLoader:
	"""
	制作卷的掉落加载
	"""
	_instance = None

	def __init__( self ):
		"""
		初始化，加载掉落数据
		@type  xmlConfig : STRING
		@param xmlConfig : 配置的路径
		"""
		assert EquipMakeDropLoader._instance is None, "instance already exist in"
		self.__datas   = EquipMakeDropAmend.Datas #存储掉率数据

	def randomValue( self, quality, itemlevel ):
		"""
		随机一个该等级总掉率以内的值
		"""
		try:
			return random.random() * self.__datas[ quality ][ itemlevel ][ "totalDropOdds" ]
		except:
			ERROR_MSG( "can not find  item quality(%s) itemlevel(%s)" % (quality, itemlevel) )
			return -1.0

	def getItem( self, quality, itemlevel ):
		"""
		根据掉率值获取掉落的物品
		@type  quality   : int
		@param quality   : 该制作卷的品质
		@type  itemlevel : int
		@param itemlevel : 该制作卷的等级
		"""
		odds = self.randomValue( quality, itemlevel )
		if odds == -1.0:
			return 0
		for item in self.__datas[ quality ][ itemlevel ][ "items" ]:
			if odds <= item["DROP_ODDS"]:
				return item["ITEM_ID"]

	@classmethod
	def instance( self ):
		"""
		返回程序的实例
		"""
		if self._instance is None:
			self._instance = EquipMakeDropLoader()
		return self._instance


# ----------------------------------------------------------------------------------------------------
# 掉落配置加载
# ----------------------------------------------------------------------------------------------------
class SpecialDropLoader:
	"""
	特殊怪物的掉落总掉率配置加载
	"""
	_instance = None

	def __init__( self, xmlConfig = None ):
		"""
		初始化，加载掉落数据
		@type  xmlConfig : STRING
		@param xmlConfig : 配置的路径
		"""
		assert SpecialDropLoader._instance is None, "instance already exist in"
		self.__datas   = {}
		for key,value in SpecialDropAmend.Datas.iteritems():
			obj = eval(value['drop_script'])
			config = smartImport( "config.server.droppedItem." + value["drop_config_name"] )
			self.__datas[key] = obj( config )

	def getDropDatas( self ):
		"""
		获取存储的掉落数据
		"""
		return self.__datas

	@classmethod
	def instance( self ):
		"""
		返回程序的实例
		"""
		if self._instance is None:
			self._instance = SpecialDropLoader()
		return self._instance


# ----------------------------------------------------------------------------------------------------
# 怪物物品掉落加载
# ----------------------------------------------------------------------------------------------------
class SpecialMonsterDropLoader:
	"""
	特殊怪物物品掉落加载的基类
	"""
	def __init__( self, pyconfig ):
		"""
		@param dictDat: 配置数据
		@type  dictDat: python dict
		"""
		self.__datas   = pyconfig.Datas

	def getClassName( self ):
		"""
		获取自己的类名，打印信息用
		"""
		return self.__class__.__name__

	def getDropDatas( self ):
		"""
		获取存储的掉落数据
		"""
		return self.__datas

	def getDropDatasEx( self, level ):
		"""
		获取指定等级的物品掉落数据
		"""
		try:
			return self.__datas[ level ][ "item" ]
		except KeyError:
			return []

	def gettotalodds( self, level ):
		"""
		获取该等级怪物的总掉率
		"""
		try:
			return self.__datas[ level ][ "totalodds" ]
		except KeyError:
			return 0.0

	def randomValue( self, level ):
		"""
		按照怪物的等级获取一个随机数
		"""
		limit = self.gettotalodds( level )
		randomValue = random.random()
		randomValue = randomValue * limit
		return randomValue

	def getDropItem( self, monster):
		"""
		获取掉落的物品
		"""
		level = monster.level
		dropRate  = self.randomValue( level )
		dropDatas = self.getDropDatasEx( level )
		for item in dropDatas:
			if dropRate <= item[ "drop_odds" ]:
				if item[ "item_id" ] == "nothing":							#如果是没有 就返回none
					return None
				elif item[ "item_id" ].startswith( "equip_quality" ): #如果是装备
					info = item[ "item_id" ].split("_")
					if len( info ) < 4:		#判断书写格式为equip_quality_2
						quality = int( info[2] )
						# 获取掉落部位列表
						specialDrop = ItemDropInWorldLoader.instance()
						wieldTypeList = specialDrop.getSpecialwieldTypeList( quality, level )
						if not wieldTypeList: return None
						eq_wieldType = random.choice( wieldTypeList )	#随机一个掉落部位
						itemInfo = self.getEquipDropInfo( quality, level, eq_wieldType )	#itemInfo 格式 ( itemID, quality, prefix, odds )
						if not itemInfo:
							return None
						itemInst = g_items.createDynamicItem( int( itemInfo[0] ) , 1 )
						if itemInst is None:
							continue
					elif len( info ) >= 4:		#判断书写格式为equip_quality_2_2
						quality = int( info[2] )
						eq_wieldType = int( info[3] ) 		#增加装备指定掉落部位
						itemInfo = self.getEquipDropInfo( quality, level, eq_wieldType )	#itemInfo 格式 ( itemID, quality, prefix, odds,eq_wieldType )
						if not itemInfo:
							return None
						itemInst = g_items.createDynamicItem( int( itemInfo[0] ) , 1 )
						if itemInst is None:
							continue
					if itemInfo[1] !=0 and itemInfo[2] != 0:
						itemInst.setQuality( itemInfo[1] )
						itemInst.setPrefix( itemInfo[2] )
						if not itemInst.createRandomEffect():
							DEBUG_MSG( "getDropItem createRandomEffect failed, item %s, quality %s, prefix %s " % ( itemInfo[0], itemInfo[1], itemInfo[2] ) )
					return itemInst
				elif item[ "item_id" ].startswith( "equip_make" ): #如果是制作卷
					itemLevel = level + random.randint(0,2)
					quality = int( item[ "item_id" ][-1] )
					itemid = self.getEquipMakeDropInfo( itemLevel, quality )	#itemid 就为制作卷的ID
					if not itemid:
						return None
					itemInst = g_items.createDynamicItem( int( itemid ) , 1 )
					if itemInst is None:
						continue
					return itemInst
				else:
					itemInst = g_items.createDynamicItem( int( item[ "item_id" ] ) , 1 )
					if itemInst is None:
						continue
					return itemInst
		return  None

	def getEquipDropInfo( self, quality, level, eq_wieldType ):
		"""
		按照怪物的等级获取最可能的 装备的掉落的信息
		"""
		specialDrop = ItemDropInWorldLoader.instance()
		data = specialDrop.getSpecialItem( quality, level, eq_wieldType )
		return data

	def getEquipMakeDropInfo( self , level, quality ):
		"""
		按照怪物的等级获取最可能的 装备的掉落的信息
		"""
		EquipMakeDrop =  EquipMakeDropLoader.instance()
		data = EquipMakeDrop.getItem( quality, level )
		return data

# ----------------------------------------------------------------------------------------------------
# 特殊怪物的杂物掉落配置加载
# ----------------------------------------------------------------------------------------------------
class SpecialSundriesLoader:
	"""
	特殊怪物的杂物掉落配置加载
	"""

	def __init__( self, pyconfig ):
		"""
		初始化，加载掉落数据
		@type  xmlConfig : STRING
		@param xmlConfig : 配置的路径
		"""
		self.__datas   = pyconfig.Datas #存储掉率数据

	def getClassName( self ):
		"""
		获取自己的类名，打印信息用
		"""
		return self.__class__.__name__

	def getDropItem( self, monster):
		"""
		获取掉落的物品
		"""
		level = monster.level
		for item in self.__datas:
			if level <= item["item_level"]:
				itemInst = g_items.createDynamicItem( int( item[ "item_id" ] ) , 1 )
				if itemInst is None:
					continue
				return itemInst
		return None

#----------------------------------------------------------
#特殊怪物公共的物品掉落(如藏宝图)
#----------------------------------------------------------
class CommonItemsLoader:
	"""
	特殊怪物公共的物品掉落
	"""

	def __init__( self, pyconfig ):
		"""
		初始化
		"""
		self.__datas   = pyconfig.Datas #存储掉率数据

	def getClassName( self ):
		"""
		获取自己的类名，打印信息用
		"""
		return self.__class__.__name__

	def getDropItem( self, monster ):
		"""
		获取掉落的物品
		"""
		if len( self.__datas ) == 0:
			try:
				L_logger.itemDropExceptLog( "%s has no Item" % self.getClassName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		odds = random.random() * self.__datas[-1]["drop_odds"]	#最后一个物品的掉落就是该表的总掉率
		for item in self.__datas:
			if odds <= item["drop_odds"]:
				if item[ "item_id" ] == "nothing":							#如果是没有 就返回none
					return None
				else:
					dropped_item = g_items.createDynamicItem( int( item[ "item_id" ] ) , 1 )
					if dropped_item is None:
						continue
					item_creat = item["item_creat"]
					if item_creat:
						for key,value in item_creat.iteritems():
							if key == "level":
								if value == "monster":
									dropped_item.set( "level", monster.level )
							else:
								dropped_item.set( key, eval(value) )
						dropped_item.generateLocation( None, monster.level )
					return dropped_item
		return None


#----------------------------------------------------------
#带产出时间的公共的物品掉落(如天降宝盒)
#----------------------------------------------------------
class CommonItemsTimeLoader:
	"""
	特殊怪物公共的物品掉落
	"""

	def __init__( self, pyconfig ):
		"""
		初始化
		"""
		self.__datas   = pyconfig.Datas #存储掉率数据

	def getClassName( self ):
		"""
		获取自己的类名，打印信息用
		"""
		return self.__class__.__name__

	def getDropItem( self, monster ):
		"""
		获取掉落的物品
		"""
		if len( self.__datas ) == 0:
			try:
				g_logger.itemDropExceptLog( "%s has no Item" % self.getClassName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		hour = int(time.strftime("%H",time.localtime()))
		dropDatas = self.__datas.get(hour, None)
		if not dropDatas:
			return None
		for item in dropDatas:
			odds = random.random()
			if odds <= item["drop_odds"]:
				dropped_item = g_items.createDynamicItem( int( item[ "item_id" ] ), 1 )
				if dropped_item is None:
					continue
				item_creat = item["item_creat"]
				if item_creat:
					for key,value in item_creat.iteritems():
						if key == "level":
							if value == "monster":
								dropped_item.set( "level", monster.level )
						else:
							dropped_item.set( key, eval(value) )
				return dropped_item
		return None


class HonorItemZhaocai( ItemDropLuckyBoxZhaocai ):
	_datas = HonorItemZhaocai.Datas
	_hinstance = None


	@classmethod
	def instance( self ):
		"""
		"""
		if HonorItemZhaocai._hinstance is None:
			HonorItemZhaocai._hinstance = HonorItemZhaocai()
		return HonorItemZhaocai._hinstance

	def __init__( self ):
		"""
		"""
		assert HonorItemZhaocai._hinstance is None,"Just allow only one instance exist!!"

		self._levelMapRate = {}	# 级别对应的总掉率，用于限制获得随机数的范围{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# 存放掉落物品的配置数据{ 级别1:{ 概率段最大值1:掉落实例1,概率段最大值2:掉落实例2,...}, ... }

		HonorItemZhaocai._hinstance = self
		self.init( )


class HonorItemJinbao( ItemDropLuckyBoxJinbao ):
	_datas = HonorItemJinbao.Datas
	_hinstance = None

	@classmethod
	def instance( self ):
		"""
		"""
		if HonorItemJinbao._hinstance is None:
			HonorItemJinbao._hinstance = HonorItemJinbao()
		return HonorItemJinbao._hinstance

	def __init__( self ):
		"""
		"""
		assert HonorItemJinbao._hinstance is None,"Just allow only one instance exist!!"

		self._levelMapRate = {}	# 级别对应的总掉率，用于限制获得随机数的范围{ level1:totalRate1, level2:totalRate2, ... }
		self._data = {}			# 存放掉落物品的配置数据{ 级别1:{ 概率段最大值1:掉落实例1,概率段最大值2:掉落实例2,...}, ... }

		HonorItemJinbao._hinstance = self
		self.init( )