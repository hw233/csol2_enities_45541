# -*- coding: gb18030 -*-

# $Id: CItemBase.py,v 1.15 2008-07-02 03:41:19 wangshufeng Exp $

"""
自定义类型道具基础模块。

"""
import BigWorld
import cPickle
import copy
import ItemTypeEnum
from bwdebug import *
import ItemAttrClass
import ItemDataList
from Function import newUID

g_items = ItemDataList.ItemDataList.instance()

class CItemBase:
	"""
	自定义类型道具实例，主要用于保存和传输一些道具的易变属性
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: 物品的原始数据
		"""
		self.uid = newUID()						# 全局唯一性ID
		self.id = srcData["id"]					# 与自己对应的全局实例名称
		self.srcData = srcData					# 与自己对应的全局实例，该数据在初始化时产生，临时使用不需要保存
		self.kitbag = None						# 物品放置在哪个背包实例上,不一定存在
		self.order = -1							# 物品放置的位置
		self.amount = 1							# 当前数量，默认值为1
		self.extra = {}							# 额外的动态属性，所有的需要保存到数据库或迁移时需要保存的属性都保存在这里
		self.tmpExtra = {}						# 额外的动态属性，类似于extra,唯一区别是保存在此的属性不存盘，只在运行时有效


	def name( self ):
		"""
		获取物品名称
		"""
		return self.srcData["name"]

	def icon( self ):
		"""
		获取图标
		"""
		return self.srcData["icon"]

	def model( self ):
		"""
		获取模型
		"""
		try:
			return self.srcData["model"]
		except:
			return 0

	def credit( self ):
		"""
		获取物品需求的声望
		"""
		try:
			return self.srcData["credit"]
		except:
			return 0

	def query( self, attrName, default = None ):
		"""
		获取一个数据

		@param attrName: 想要获取的值的属性名称
		@type  attrName: String
		@param  default: 如果指定属性的值不存在，返回什么，默为返回None
		@type   default: any
		"""
		if attrName in self.extra:
			return self.extra[attrName]
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def queryTemp( self, attrName, default = None ):
		"""
		获取一个临时数据

		@param attrName: 想要获取的值的属性名称
		@type  attrName: String
		@param  default: 如果指定属性的值不存在，返回什么，默为返回None
		@type   default: any
		"""
		if attrName in self.tmpExtra:
			return self.tmpExtra[attrName]
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def queryInt( self, attrName ):
		return self.query( attrName, 0 )

	def queryTempInt( self, attrName ):
		return self.queryTemp( attrName, 0 )

	def queryStr( self, attrName ):
		return self.query( attrName, "" )

	def queryTempStr( self, attrName ):
		return self.queryTemp( attrName, "" )

	def set( self, attrName, value, owner = None ):
		"""
		设置动态数据

		@param owner: 如果值为None，则只设置数量；如果值(只能)为Role实例，则调用entity.client.onItemAttrUpdated()方法
		@return: None
		"""
		self.extra[attrName] = value
		if owner:
			if attrName not in ItemAttrClass.m_itemAttrMap:
				WARNING_MSG( "set undefine property. -->", attrName, value )
				return
			stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( value )
			owner.client.onItemAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

	def setTemp( self, attrName, value, owner = None ):
		"""
		设置动态的临时数据

		@param owner: 如果值为None，则只设置数量；如果值(只能)为Role实例，则调用entity.client.onItemAttrUpdated()方法
		@return: None
		"""
		self.tmpExtra[attrName] = value
		if owner:
			if attrName not in ItemAttrClass.m_itemAttrMap:
				WARNING_MSG( "set undefine property. -->", attrName, value )
				return
			stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( value )
			owner.client.onItemTempAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

	def addToDict( self ):
		"""
		转换成ITEM type format.

		@return: dict
		@rtype:  dict
		"""
		return { 	"uid"		: self.uid,
					"id" 		: self.id,
					"amount" 	: self.amount,
					"order"		: self.order,
					"extra" 	: cPickle.dumps( self.extra, 2 ),
					"tmpExtra" 	: cPickle.dumps( self.tmpExtra, 2 ),
				}

	def loadFromDict( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self.uid = valDict["uid"]
		self.amount = valDict["amount"]
		self.order = valDict["order"]
		if valDict.has_key( "extra" ):
			self.extra = cPickle.loads( valDict["extra"] )
		if valDict.has_key( "tmpExtra" ) and len( valDict["tmpExtra"] ):
			self.tmpExtra = cPickle.loads( valDict["tmpExtra"] )

	def setKitbag( self, kitbag ):
		"""
		@param kitbag: 放置该物品的背包实例
		@type  kitbag: KitbagBase
		@return:          无
		"""
		self.kitbag = kitbag

	def getKitbag( self ):
		"""
		获取该物品所在包裹实例
		"""
		return self.kitbag

	def setOrder( self, order ):
		"""
		@param  order: 该物品放在哪个位置
		@type   order: UINT8
		@return:          无
		"""
		self.order = order

	def getOrder( self ):
		"""
		获取orderID
		"""
		return self.order

	def getuid( self ):
		"""
		获取uid
		"""
		return self.uid

	def getType( self ):
		"""
		获取物品类型
		"""
		return self.query( "type" )

	def isType( self, type ):
		"""
		判断自己是否为某类型的道具；

		@param type: 欲判断的类型，值为该模块中“CIST_”开头的常量之一
		@type  type: UINT32
		@return:     True == 是指定的类型，False == 不是指定的类型
		@rtype:      BOOL
		"""
		return self.getType() == type

	def getAmount( self ):
		"""
		取得物品数量
		"""
		return self.amount

	def setAmount( self, amount, owner = None ):
		"""
		取得物品数量
		"""
		self.amount = amount
		if owner:
			if amount <= 0:
				owner.removeByOrder( self.order )
			else:
				attrName = "amount"
				stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( amount )
				owner.client.onItemAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

	def addFlag( self, flags, owner = None ):
		"""
		增加标志

		@param flags: 欲增加的标志；标志为所有“CFE_”开头的组合
		@type  flags: UINT16
		@return:      无
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		self.set( "flags", oldFlags | flags, owner )

	def removeFlag( self, flags, owner = None ):
		"""
		移除标志

		@param flags: 欲移除的标志；标志为所有“CFE_”开头的组合
		@type  flags: UINT16
		@return:      无
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		# 先确保里面有值再做异或取消掉
		self.set( "flags", (oldFlags | flags) ^ flags, owner )

	def hasFlag( self, flags ):
		"""
		判断标志

		@param flags: 欲判断的标志；标志为所有“CFE_”开头的组合
		@type  flags: UINT16
		@return:      True == 存在指定的标志(组合)；False == 不存在指定的标志(组合)
		@rtype:       BOOL
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		return flags & oldFlags == flags

	def getStackable( self ):
		"""
		获取该物品的叠加上限，默认为1
		"""
		return self.query( "stackable", 1 )

	def canStore( self ):
		"""
		判断一个物品是否能被存储

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_WAREHOUSE )

	def canSell( self ):
		"""
		判断一个物品是否能被出售

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_SELL )

	def canDestroy( self ):
		"""
		判断一个物品是否能被销毁

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_DESTROY )

	def canRepair( self ):
		"""
		判断一个物品是否能被修理

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_REPAIR )

	def canConsume( self ):
		"""
		判断一个物品是否能被消耗

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_WASTAGE )

	def canAbrasion( self ):
		"""
		判断一个物品是否能被磨损

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_ABRASION )

	def canIntensify( self ):
		"""
		判断一个物品是否能被强化

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_INTENSIFY )

	def canRebuid( self ):
		"""
		判断一个物品是否能被改造

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_REBUILD )

	def canStiletto( self ):
		"""
		判断一个物品是否能被打孔

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_STILETTO )

	def canGive( self ):
		"""
		判断是否能给(玩家与玩家之间的物品交换)
		当该物品为绑定状态时，该物品不能交易

		@return: bool
		@rtype:  bool
		"""
		return not self.isBinded() or self.hasFlag( ItemTypeEnum.CFE_NO_TRADE )

	def canUse( self ):
		"""
		判断自己是否可以被使用

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.query( "spell", 0 ) > 0

	def setBindType( self, type, owner ):	# 11:39 2008-7-2,wsf add
		"""
		设置绑定类型
		"""
		bit = 1 << type
		bindType = ( bit << 4 ) | bit
		self.set( "bindType", bindType, owner )

	def getBindType( self ):
		"""
		获取绑定类型
		"""
		return self.query( "bindType", 0 )

	def isBinded( self ):
		"""
		判断该物品是否绑定
		@return Bool
		"""
		return ( self.getBindType() >> 4 ) > 0

	def cancelBindType( self, owner = None ):
		"""
		取消该物品的绑定，恢复到绑定前状态
		"""
		bindType = self.query( "bindType", 0 )
		if bindType == ItemTypeEnum.CBT_NONE:
			return
		newBindType = bindType >> 4
		self.set( "bindType", newBindType, owner )

	def new( self ):
		"""
		使用当前物品的数据创建一个新的物品实例。

		@return: 继承于CItemBase的自定义类型道具实例
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		return obj

	def copy( self ):
		"""
		复制自己，uid与源物品一样。

		@return: 继承于CItemBase的自定义类型道具实例
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		obj.uid = self.uid
		return obj

	def updateMe( self, owner ):
		"""
		更新物品到拥有者的client端

		@return: 如果有拥有者则返回Treu, 没有则返回False
		"""
		raise "I can't support yet."

	def getAddedDescribe1( self ):
		"""
		取得附加的描述1
		"""
		try:
			return self.srcData["describe1"]
		except KeyError:
			return ""

	def getAddedDescribe2( self ):
		"""
		取得附加的描述2
		"""
		try:
			return self.srcData["describe2"]
		except KeyError:
			return ""

	def getAddedDescribe3( self ):
		"""
		取得附加的描述3
		"""
		try:
			return self.srcData["describe3"]
		except KeyError:
			return ""

	def getMaxSpace( self ):
		"""
		"""
		return self.query( "kb_maxSpace", 0 )

	def getPrice( self ):
		"""
		获取当前道具价值，有可能会需要根据某些特性计算
		"""
		return self.query( "price" )

	def setPrice( self, value, owner = None ):
		"""
		设置该物品的价格
		"""
		assert isinstance( value, int )
		self.set( "price", value, owner )

	def getQuestID( self ):
		"""
		获得该物品触发的任务ID
		"""
		return self.query( "questID", 0 )

	def getQuality( self ):
		"""
		获取物品的品质
		"""
		return self.query( "quality", 1 )

	def isFrozen( self ):
		"""
		判断自己是否被冻结
		@return: BOOL
		"""
		return self.queryTemp( "freeze" )

	def freeze( self, owner = None ):
		"""
		冻结自己
		@return: 如果能冻结则返回True, 如果已经被冻结则返回False
		@rtype:  bool
		"""
		if self.queryTemp( "freeze", 0 ):
			return False
		self.setTemp( "freeze", 1, owner )
		return True

	def unfreeze( self, owner = None ):
		"""
		解冻自己
		@return: 无
		"""
		self.setTemp( "freeze", 0, owner )

	def getReqLevel( self ):
		"""
		获取使用等级
		"""
		return self.query( "reqLevel", 0 )

	def getLifeTime( self ):
		"""
		获取物品存活时间
		"""
		return self.query( "lifeTime", 0 )

	def setLevel( self, level, owner = None ):
		"""
		设置物品的等级 by 姜毅
		@param    reqLevel: 使用等级
		@type     reqLevel: UINT8
		@param owner: 装备拥有者
		@type  owner: Entity
		@return None
		"""
		self.set( "level", level, owner )
		
	def getLevel( self ):
		"""
		获取等级
		"""
		return self.query( "level", 0 )
		
	def isEquip( self ):
		"""
		virtual method.
		判断是否是装备
		"""
		return False

# CItemBase.py
