# -*- coding: gb18030 -*-

# $Id: CItemBase.py,v 1.52 2008-08-29 07:22:49 yangkai Exp $

"""
自定义类型道具基础模块。

"""
import BigWorld
import cPickle
import copy
import ItemTypeEnum
import ItemAttrClass
from bwdebug import *
from MsgLogger import g_logger
import csstatus
import csdefine
import csconst
import ItemDataList
import SkillTargetObjImpl
import SkillTypeImpl
import CooldownFlyweight
from Resource.SkillLoader import g_skills
from Function import newUID
import math
import sys
from ItemSystemExp import EquipQualityExp


g_items = ItemDataList.ItemDataList.instance()
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

CANNOT_USE_DRUG_HP_SPACE = [
	csdefine.SPACE_TYPE_TONG_TURN_WAR,
	csdefine.SPACE_TYPE_CAMP_TURN_WAR,
	csdefine.SPACE_TYPE_JUE_DI_FAN_JI,
	csdefine.SPACE_TYPE_AO_ZHAN_QUN_XIONG,
]

class CItemBase:
	"""
	自定义类型道具实例，主要用于保存和传输一些道具的易变属性

	@ivar        id: 与自己对应的全局实例名称
	@type        id: str
	@ivar    amount: 当前数量
	@type    amount: INT
	@ivar   srcData: 与自己对应的全局数据，该数据在初始化时产生，临时使用不需要保存
	@type   srcData: instance
	@ivar    kitbag: 物品放置在哪个背包实例上,不一定存在
	@type    kitbag: KitbagBase
	@ivar     order: 物品放置的位置,不一定存在
	@type     order: UINT8
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
		return self.query("name")

	def fullName( self ):
		"""
		获取物品的全名 如 雄鹰的逆天的霸王弓
		"""
		nameDes = self.name()
		proName = self.query( "propertyPrefix")
		if proName: nameDes = proName + nameDes
		instan = EquipQualityExp.instance()
		prefix = self.query( "prefix" )
		excName = instan.getName( prefix )
		if excName != "": nameDes = excName + nameDes

		return nameDes

	def icon( self ):
		"""
		获取图标路径
		"""
		return self.srcData["icon"]

	def model( self ):
		"""
		获取模型编号
		"""
		try:
			return int( self.srcData["model"] )
		except:
			return 0

	def getParticle( self ):
		"""
		获取原始光效ID
		"""
		return self.query( "particle", "" )

	def credit( self ):
		"""
		获取物品需求的声望
		"""
		try:
			return self.srcData["reqCredit"]
		except:
			return {}

	def queryReqClasses( self ):
		"""
		获取物品需求的职业列表
		"""
		return self.query( "reqClasses", [] )

	def getReqGender( self ):
		"""
		获取物品需求性别列表
		"""
		return self.query( "reqGender", [] )

	def queryBaseData( self, attrName, default = None ):
		"""
		获取一个从配置表里读取的数据

		@param attrName: 想要获取的值的属性名称；具体可用的属性名取值请查看common/ItemAttrClass.py
		@type  attrName: String
		@param  default: 如果指定属性的值不存在，返回什么，默为返回None
		@type   default: any
		"""
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def query( self, attrName, default = None ):
		"""
		获取一个数据

		@param attrName: 想要获取的值的属性名称；具体可用的属性名取值请查看common/ItemAttrClass.py
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

		@param attrName: 想要获取的值的属性名称；具体可用的属性名取值请查看common/ItemAttrClass.py
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
		
	def pop( self, attrName, default = None ):
		return self.extra.pop( attrName, default )

	def popTemp( self, attrName, default = None ):
		return self.tmpExtra.pop( attrName, default )

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
			# 参数 attrName --> ItemAttrClass.m_itemAttrSendMap.index( attrName )
			# 目的是为了减少通信消耗 16:26 2008-3-21 yk
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
			# 参数 attrName --> ItemAttrClass.m_itemAttrSendMap.index( attrName )
			# 目的是为了减少通信消耗 16:26 2008-3-21 yk
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

	def getLifeType( self ):
		"""
		获取物品存活类型
		"""
		return self.query( "lifeType", ItemTypeEnum.CLTT_NONE )

	def getLifeTime( self ):
		"""
		获取物品存活时间
		"""
		return self.query( "lifeTime", 0 )

	def setLifeTime( self, lifeTime, owner = None ):
		"""
		获取物品存活时间
		"""
		return self.set( "lifeTime", int( lifeTime ), owner )

	def getDeadTime( self ):
		"""
		获取物品死亡时间
		"""
		return self.query( "deadTime", 0 )

	def setDeadTime( self, deadTime, owner = None ):
		"""
		设置物品死亡时间
		"""
		self.set( "deadTime", int( deadTime ), owner )

	def isActiveLifeTime( self ):
		"""
		判断是否激活使用时间
		"""
		return self.query( "deadTime" ) is not None

	def activaLifeTime( self, owner = None ):
		"""
		激活一个物品的使用时间
		如果存活类型是下线计时，那么owner必须为None
		因为它不应该通知addLifeItemsToManage
		"""
		if self.getLifeType() == 0: return
		if self.isActiveLifeTime(): return
		lifeTime = self.getLifeTime()
		if lifeTime == 0: return
		deadTime = time.time() + lifeTime
		self.setDeadTime( deadTime, owner )
		if owner is None: return
		owner.addLifeItemsToManage( [self.uid], [deadTime] )

	def isOverdue( self ):
		"""
		判断当前是否过期
		"""
		if not self.isActiveLifeTime(): return False
		return time.time() > self.getDeadTime()

	def onAdd( self, owner ):
		"""
		玩家获取物品
		"""
		if owner is None: return
		# 存活时间类型处理
		lifeType = self.getLifeType()
		if lifeType in [ItemTypeEnum.CLTT_ON_GET, ItemTypeEnum.CLTT_ON_GET_EVER]:
			self.activaLifeTime( owner )
		# 绑定类物品的处理
		bindType = self.getBindType()
		isBinded = self.isBinded()
		if not isBinded:
			# 拾取邦定
			if bindType == ItemTypeEnum.CBT_PICKUP:
				self.setBindType( ItemTypeEnum.CBT_PICKUP, owner )
			# 任务邦定
			elif bindType == ItemTypeEnum.CBT_QUEST:
				self.setBindType( ItemTypeEnum.CBT_QUEST, owner )

	def onDelete( self, owner ):
		"""
		玩家删除物品
		"""
		if owner is None: return
		# 清除一个激活使用时间物品
		deadTime = self.getDeadTime()
		if deadTime <= 0: return
		owner.removeLifeItemsFromManage( [self.uid], [deadTime] )

	def onWield( self, owner ):
		"""
		vitural method
		"""
		pass

	def setKitbag( self, kitbag ):
		"""
		@param kitbag: 放置该物品的背包实例
		@type  kitbag: KitbagBase
		@return:          无
		"""
		self.kitbag = kitbag

	def getKitID( self ):
		"""
		获取该物品所在包裹ID
		"""
		return self.order/csdefine.KB_MAX_SPACE

	def setOrder( self, order ):
		"""
		@param  order: 该物品放在哪个位置
		@type   order: UINT8
		@return:          无
		"""
		self.order = order

	def getOrder( self ):
		"""
		获取该物品orderID
		"""
		return self.order

	def getUid( self ):
		"""
		获取该物品uid
		"""
		return self.uid

	def getType( self ):
		"""
		获取该物品类型
		"""
		return self.query( "type" )

	def isType( self, type ):
		"""
		判断自己是否为某类型的道具；

		@param type: 欲判断的类型
		@type  type: UINT32
		@return:     True == 是指定的类型，False == 不是指定的类型
		@rtype:      BOOL
		"""
		return self.getType() == type

	def getLevel( self ):
		"""
		获取等级
		"""
		return self.query( "level", 0 )

	def getReqLevel( self ):
		"""
		获取使用等级
		"""
		return self.query( "reqLevel", 0 )

	def getUseDegree( self ):
		"""
		取得使用次数
		"""
		return self.query( "useDegree", 0 )

	def getAmount( self ):
		"""
		取得物品数量
		"""
		return self.amount

	def setAmount( self, amount, owner = None, reason = csdefine.ITEM_NORMAL ):
		"""
		设置物品数量
		这里还涉及一个
		"""
		old = self.amount
		self.amount = amount
		if owner:
			if amount <= 0:
				order = self.order
				owner.itemsBag.removeByOrder( order )
				owner.client.removeItemCB( order )
				if reason == csdefine.ITEM_NORMAL:	# 由于有非常多的非玩家物品进行了setAmount操作,而我们只需要记录玩家身上的物品的setAmount操作,
					return							# 所以如果是ITEM_NORMAL原来,就不做记录，当然我们会尽量保证玩家身上的每一个setAmount操作都会拥有一个 reason.
					
			else:
				attrName = "amount"
				stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( amount )
				owner.client.onItemAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )
				if reason == csdefine.ITEM_NORMAL:
					return
		
			try:
				g_logger.itemSetAmountLog( owner.databaseID, owner.getName(), owner.grade, reason, self.uid, self.name(), old, amount )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def onSpellOver( self, owner ):
		"""
		技能使用结束
		"""
		useDegree = self.getUseDegree()
		if useDegree == -1:
			pass
		elif useDegree > 1:
			self.set( "useDegree", useDegree - 1, owner )
		else:
			# self.setAmount( self.getAmount() - 1, owner )
			owner.removeItem_( self.order, 1, csdefine.DELETE_ITEM_USE )	# 2009-07-06 SPF

		owner.questIncreaseItemUsed( self.id )


	def setUseDegree( self, useDegree, owner = None ):
		"""
		设置使用次数
		"""
		self.set( "useDegree", useDegree, owner )

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

	def getOnlyLimit( self ):
		"""
		获取该物品的最大拥有数量
		"""
		return self.query( "onlyLimit", 0 )

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
		if self.isBinded(): return False
		if self.hasFlag( ItemTypeEnum.CFE_NO_TRADE ): return False
		return True

	def canExchange( self ):
		"""
		绕开绑定判定物品的可交换属性 by姜毅
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_TRADE )

	def getSpellID( self ):
		"""
		"""
		return self.query( "spell", 0 )

	def use( self, owner, target ):
		"""
		使用物品

		@param    owner: 背包拥有者
		@type     owner: Entity
		@param   target: 使用目标
		@type    target: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		# 检测物品是否可用
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult

		spell = self.query( "spell" )
		target = SkillTargetObjImpl.createTargetObjEntity( target )
		# 在这里因为我们要保存当前要使用的物品信息
		# 所以我们要在确定物品可以正常使用的情况下才记录物品信息
		# 否则会出Bug
		try:
			spell = g_skills[spell]
		except:
			return  csstatus.SKILL_NOT_EXIST

		value = self.getUid()
		# 这个temp一定要在useableCheck之前设置，因为useableCheck的一些
		# 继承接口需要知道正在使用的物品，这个物品得从这个temp中查询
		if owner.intonating():
			return csstatus.SKILL_INTONATING
		# 策划要求在连击状态下可以使用药品csol-2229
		if owner.inHomingSpell() and ( not self.getType() in ItemTypeEnum.ROLE_DRUG_LIST ):
			return csstatus.SKILL_CANT_CAST
		if owner.getCurrentSpaceType() in CANNOT_USE_DRUG_HP_SPACE and ( self.getType() in ItemTypeEnum.ROLE_DRUG_HP_LIST ):
			return csstatus.SKILL_CAN_NOT_CAST_IN_CURRENT_SPACE
		owner.setTemp( "item_using", value )
		state = spell.useableCheck( owner, target )
		if state != csstatus.SKILL_GO_ON:
			owner.removeTemp( "item_using" )
			return csconst.SKILL_STATE_TO_ITEM_STATE.get( state,state )

		spell.use( owner, target )
		return csstatus.SKILL_GO_ON

	def onSetCooldownInUsed( self, caster ):
		"""
		物品物品使用后触发
		@param    caster: 物品使用者
		@type     caster: Entity
		"""
		self.freeze()
		springUsedCD = self.query( "springUsedCD", {} )
		for cd, time in springUsedCD.iteritems():
			endTime = g_cooldowns[ cd ].calculateTime( time )
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def onSetCooldownInIntonateOver( self, caster ):
		"""
		技能物品吟唱结束后触发
		@param    owner: 物品使用者
		@type     owner: Entity
		"""
		self.unfreeze()
		springIntonateOverCD = self.query( "springIntonateOverCD", {} )
		for cd, time in springIntonateOverCD.iteritems():
			endTime = g_cooldowns[ cd ].calculateTime( time )
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def checkUse( self, owner ):
		"""
		检测使用者是否能使用该物品

		@param owner: 背包拥有者
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		# 判断是否正在使用其它物品，因为理论上物品使用不允许并行进行
		if not owner.queryTemp( "item_using" ) is None:
			return csstatus.CIB_MSG_ITEM_MULT_USE
		# 判断物品受影响的CD有没有过
		if owner.level < self.getReqLevel():
			return csstatus.CIB_MSG_ITEM_NOT_USED

		isLifeType = self.getLifeType()
		hasLifeTime = self.getLifeTime()
		if isLifeType and not hasLifeTime:
			return csstatus.CIB_MSG_ITEM_NO_USE_TIME

		if not self.query( "spell", 0 ):
			return csstatus.CIB_MSG_ITEM_NOT_USED

		limitCD = self.query( "limitCD", [] )
		for cd in limitCD:
			timeVal = owner.getCooldown( cd )
			if not g_cooldowns[ cd ].isTimeout( timeVal ):
				return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON

	def new( self ):
		"""
		使用当前物品的数据创建一个新的物品。

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

	def createEntity( self, spaceID, position, direction ):
		"""
		调用与自己关联的全局实例，创建一个包含自己的Entity扔到地图上

		@param   spaceID: 地图ID号
		@type    spaceID: INT32
		@param  position: 道具产生后放在哪个位置
		@type   position: VECTOR3
		@param direction: 道具产生后放的方向
		@type  direction: VECTOR3
		@param   srcItem: 继承于CItemBase的自定义道具类型实例。
		                  该参数默认值为None，表示使用全局实例的默认参数初始化它，否则将使用提供的参数进行初始化
		@type    srcItem: CItemBase
		@return:          一个新的道具entity
		@rtype:           Entity
		"""
		return g_items.createEntity( self.id, spaceID, position, direction, { "itemProp" : self } )

	def getPrice( self ):
		"""
		获取当前道具价值，有可能会需要根据某些特性计算
		"""
		basePrice = self.getRecodePrice()
		baseUseDegree = self.queryBaseData( "useDegree", 0 )
		if baseUseDegree <= 1: return basePrice
		useDegree = self.getUseDegree()
		newPrice = int( useDegree * 1.0 / baseUseDegree * basePrice )
		return newPrice

	def getRecodePrice( self ):
		"""
		获取物品当前记录的价格，此数据和服务器的数据是一样的
		和上面的getPrice()接口计算的价格不一样
		"""
		return self.query( "price", 0 )

	def updatePrice( self, owner = None ):
		"""
		Virtual Method
		刷新物品的价格
		由于一些计算物品价格的参数改变，价格也做相应改变了
		"""
		basePrice = self.queryBaseData( "price", 0 )
		self.setPrice( basePrice, owner )

	def getWarIntegral( self ):
		"""
		获取道具的战场积分价值
		"""
		return self.query( "warIntegral",  0)

	def setPrice( self, value, owner = None ):
		"""
		设置该物品的价格
		"""
		self.set( "price", int( value ), owner )

	def getMaxSpace( self ):
		"""
		"""
		return self.query( "kb_maxSpace", 0 )

	def setPrefix( self, prefix, owner = None ):
		"""
		设置该物品的前缀
		"""
		self.set( "prefix", prefix, owner )

	def setQuality( self, quality, owner = None ):
		"""
		设置该物品的品质
		@param    quality: 物品品质
		@type     quality: INT8
		@param owner: 装备拥有者
		@type  owner: Entity
		@return None
		"""
		self.set( "quality", quality, owner )

	def getQuestID( self ):
		"""
		获取该物品触发的任务ID
		"""
		return self.query( "questID", 0 )

	def getVehicleMoveSpeed( self ):
		"""
		获取该物品的移动速度数据(骑宠)
		"""
		return self.query( "vehicle_move_speed", 0.0 )

	def getVehicleMaxMount( self ):
		"""
		获取该物品的额外装载人数(骑宠)
		"""
		return self.query( "vehicle_max_mount", 0 )

	def getVehicleCanFight( self ):
		"""
		获取该骑宠是否能战斗(骑宠)
		"""
		return self.query( "vehicle_canFight", 0 )

	def getLastBjExtraEffectID( self ):
		"""
		获取最后一个宝石镶嵌附加属性
		"""
		bjEffect = self.getBjExtraEffect()
		if len( bjEffect ) == 0:
			effectID = 0
		else:
			effectID = bjEffect[-1][0]
		return effectID

	def getBjExtraEffectCount( self ):
		"""
		获取宝石镶嵌数量
		"""
		return len( self.getBjExtraEffect() )

	def getBjExtraEffect( self ):
		"""
		获取宝石附加属性
		"""
		return self.query( "bj_extraEffect", [] )

	def setBjExtraEffect( self, effect, owner = None ):
		"""
		设置装备/宝石附加属性
		增加装备/宝石的镶嵌属性
		@param    effect: 镶嵌属性
		@type     effect: dic
		@param owner: 装备拥有者
		@type  owner: Entity
		@return None
		"""
		self.set("bj_extraEffect", effect, owner )

	def addBjExtraEffect( self, effect, owner = None ):
		"""
		增加装备/宝石的镶嵌属性
		@param    effect: 镶嵌属性
		@type     effect: ( key, value )
		@param owner: 装备拥有者
		@type  owner: Entity
		@return None
		"""
		oldEffect = self.getBjExtraEffect()
		oldEffect.extend( effect )
		self.setBjExtraEffect( oldEffect, owner )

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

	def setReqLevel( self, reqLevel, owner = None ):
		"""
		设置物品的使用等级
		@param    reqLevel: 使用等级
		@type     reqLevel: UINT8
		@param owner: 装备拥有者
		@type  owner: Entity
		@return None
		"""
		self.set( "reqLevel", reqLevel, owner )

	def setBaseRate( self, baseRate, owner = None ):
		"""
		设置物品的基础属性品质比率
		@param baseRate: 基础属性品质比率
		@type  baseRate: Float
		@param    owner: 装备拥有者
		@type     owner: Entity
		@return:    无
		"""
		self.set( "baseQualityRate", baseRate, owner )

	def getBaseRate( self ):
		"""
		获取物品的基础附加属性品质比率
		"""
		return self.query( "baseQualityRate", 0.0 )

	def setExcRate( self, baseRate, owner = None ):
		"""
		设置物品的附加属性品质比率
		@param baseRate: 基础属性品质比率
		@type  baseRate: Float
		@param    owner: 装备拥有者
		@type     owner: Entity
		@return:    无
		"""
		self.set( "excQualityRate", baseRate, owner )

	def getExcRate( self ):
		"""
		获取物品的附加属性品质比率
		"""
		return self.query( "excQualityRate", 0.0 )

	def getPrefix( self ):
		"""
		获取物品的前缀
		"""
		return self.query( "prefix", 0 )

	def getQuality( self ):
		"""
		获取物品的品质
		"""
		return self.query( "quality", 1 )

	def setBindType( self, type, owner = None ):
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

	def getSrcBindType( self ):
		"""
		返回原型绑定类型
		"""
		return self.queryBaseData( "bindType", 0 )

	def isBinded( self ):
		"""
		判断该物品是否绑定
		@return Bool
		"""
		return self.getBindType() != self.getSrcBindType()

	def cancelBindType( self, owner = None ):
		"""
		取消该物品的绑定，恢复到绑定前状态
		"""
		srcBindType = self.getSrcBindType()
		self.set( "bindType", srcBindType, owner )

	def isEquip( self ):
		"""
		virtual method.
		判断是否是装备
		"""
		return False

	def isWhite( self ):
		"""
		virtual method.
		判断是否是白色物品
		"""
		return self.getQuality() == ItemTypeEnum.CQT_WHITE

	def isBlue( self ):
		"""
		virtual method.
		判断是否是蓝色物品
		"""
		return self.getQuality() == ItemTypeEnum.CQT_BLUE

	def isGold( self ):
		"""
		virtual method.
		判断是否是金色物品
		"""
		return self.getQuality() == ItemTypeEnum.CQT_GOLD

	def isPink( self ):
		"""
		virtual method.
		判断是否是粉色物品
		"""
		return self.getQuality() == ItemTypeEnum.CQT_PINK

	def isGreen( self ):
		"""
		virtual method.
		判断是否是绿色物品
		"""
		return self.getQuality() == ItemTypeEnum.CQT_GREEN

	def isFrozen( self ):
		"""
		判断自己是否被冻结
		@return: BOOL
		"""
		return self.queryTemp( "freeze", 0 )

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


	def yinpiao( self ):
		"""
		获取银票物品的银两数
		"""
		return self.query( "yinpiao", 0 )


	def reqYinpiao( self ):
		"""
		获取物品需求的银票
		"""
		return self.query( "reqYinpiao", 0 )

	def setObey( self, type, owner = None ):
		"""
		设置认主 by姜毅
		"""
		self.set( "eq_obey", type, owner )

	def getObey( self ):
		"""
		获取认主状态 by姜毅
		"""
		return self.query( "eq_obey", 0 )

	def isObey( self ):
		"""
		判断是否认主装备 by姜毅
		"""
		if self.getObey():
			return True
		return False

	def onDieDrop( self ):
		"""
		"""
		pass

	def isAlreadyWield( self ):
		"""
		判断是否已经装备上效果了
		@return: BOOL
		@rtype:  BOOL
		"""
		# 增加了物品基类是否装备上效果的接口
		# 默认返回 False
		# 增加原因，代码中多处需要判断某个物品是否处于被装备上的效果，但有时候，如果该物品不是一个CEquip就会出错
		# 2009-07-16 SPF
		return False

	def getTsItemType( self ):
		"""
		获得物品的替售分类类型
		"""
		itemType = self.getType()

		if itemType in ItemTypeEnum.WEAPON_LIST:
			return csconst.TI_SHOU_WEAPON
		elif itemType in ItemTypeEnum.ARMOR_LIST:
			return csconst.TI_SHOU_ARMOR
		elif itemType == ItemTypeEnum.ITEM_PRODUCE_STUFF:
			return csconst.TI_SHOU_PRODUCE_STUFF
		else:
			return csconst.TI_SHOU_TYPE_NONE
# CItemBase.py
