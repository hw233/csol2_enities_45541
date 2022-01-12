# -*- coding: gb18030 -*-

# $Id: CItemBase.py,v 1.61 2008-08-13 08:57:12 qilan Exp $

"""
自定义类型道具基础模块。
"""

# clommon
import copy
import cPickle
import BigWorld
import csdefine
import csconst
import csstatus
import ItemTypeEnum
import ItemAttrClass

# client
import Const
import Define
import ItemDataList
import skills
import SkillTargetObjImpl
import CItemDescription
import TextFormatMgr

# common
from bwdebug import *
from ItemSystemExp import EquipQualityExp

# client
from Time import Time
from gbref import rds
from EquipEffectLoader import EquipEffectLoader
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CItemBase

# global instances
g_items = ItemDataList.ItemDataList.instance()
equ_items_type = ItemTypeEnum.EQUIP_TYPE_SET
g_equipQualityExp = EquipQualityExp.instance()
g_equipEffect = EquipEffectLoader.instance()


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
		self.id = srcData["id"]					# 与自己对应的全局实例名称
		self.srcData = srcData					# 与自己对应的全局实例，该数据在初始化时产生，临时使用不需要保存
		self.kitbag = None						# 物品放置在哪个背包实例上,不一定存在
		self.order = -1							# 物品放置的位置
		self.amount = 1							# 当前数量，默认值为1
		self.extra = {}							# 额外的动态属性，所有的需要保存到数据库或迁移时需要保存的属性都保存在这里
		self.tmpExtra = {}						# 额外的动态属性，类似于extra,唯一区别是保存在此的属性不存盘，只在运行时有效
		self.defaultColor = ( 255, 255, 255 ) 	# 物品描述的默认颜色
		self.desFrame = CItemDescription.CItemDescription()# 物品的描述信息(用于生成相应的描述信息浮动框模板) - -add by hd

	def name( self ):
		"""
		获取物品名称
		"""
		return self.query("name","")

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
		iconName = self.query( "icon", Const.ITEM_DEFAULT_ICON )
		return "icons/%s.dds" % iconName

	def model( self ):
		"""
		获取模型路径
		"""
		return int( self.query( "model", 0 ) )

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

	def set( self, attrName, value, owner = None ):
		"""
		设置动态数据

		@param owner: 如果值为None，则只设置数量；如果值(只能)为Role实例，则调用entity.client.onItemAttrUpdated()方法
		@return: None
		"""
		self.extra[attrName] = value

	def setTemp( self, attrName, value, owner = None ):
		"""
		设置动态的临时数据

		@param owner: 如果值为None，则只设置数量；如果值(只能)为Role实例，则调用entity.client.onItemAttrUpdated()方法
		@return: None
		"""
		self.tmpExtra[attrName] = value

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
		if valDict.has_key( "tmpExtra" ):
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

	def getDeadTime( self ):
		"""
		获取物品死亡时间
		"""
		return self.query( "deadTime", 0 )

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
		获取该物品的order位置
		"""
		return self.order

	def getUid( self ):
		"""
		获取该物品的uid位置
		"""
		return self.uid

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

	def getBaseRate( self ):
		"""
		获取物品的基础附加属性品质比率
		"""
		return self.query( "baseQualityRate", 0.0 )
	
	def getExcRate( self ):
		"""
		获取物品的附加属性品质比率
		"""
		return self.query( "excQualityRate", 0.0 )

	def getType( self ):
		"""
		获取该物品的类型
		"""
		return self.query( "type" )

	def getPickUpType( self ):
		"""
		获取该物品的拾取类型
		"""
		put = self.query( "pickUpType" )
		return put if not (put is None or put == 0) else ItemTypeEnum.PICK_UP_TYPE_DEFAULT

	def isType( self, type ):
		"""
		判断自己是否为某类型的道具；

		@param type: 欲判断的类型，
		@type  type: UINT32
		@return:     True == 是指定的类型，False == 不是指定的类型
		@rtype:      BOOL
		"""
		return self.getType() == type

	def isCooldownType( self, cooldownType ):
		"""
		判断自身是否与某一类型的cooldown相同

		@param cooldownType: cooldown类型
		@type  cooldownType: INT
		@return: bool
		"""
		return cooldownType in self.query( "limitCD", [] )

	def isActiveLifeTime( self ):
		"""
		判断是否激活使用时间
		"""
		return self.query( "deadTime" ) is not None

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
		return not ( self.isBinded() or self.hasFlag( ItemTypeEnum.CFE_NO_TRADE ) )

	def getSpell( self ):
		"""
		获取物品关联的技能
		@return: SkillBase instance or None
		"""
		spellID = self.query( "spell", 0 )
		if not spellID:
			return None
		try:
			return skills.getSkill( spellID )
		except KeyError:
			return None

	def use( self, owner, target, position = (0.0, 0.0, 0.0) ):
		"""
		使用物品

		@param    owner: 背包拥有者
		@type     owner: Entity
		@param   target: 使用目标
		@type    target: Entity
		@param position: 目标位置,无则为None
		@type  position: tuple or VECTOR3
		@return: STATE CODE
		@rtype:  UINT16
		"""
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult

		sk = skills.getSkill( self.query( "spell" ) )
		state = sk.useableCheck( owner, SkillTargetObjImpl.createTargetObjEntity(target) )
		return csconst.SKILL_STATE_TO_ITEM_STATE.get( state,state )

	def checkUse( self, owner ):
		"""
		检测使用者是否能使用该物品

		@param owner: 背包拥有者
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		if owner.level < self.getReqLevel():
			return csstatus.CIB_MSG_ITEM_NOT_USED

		isLifeType = self.getLifeType()
		hasLifeTime = self.getLifeTime()
		if isLifeType and not hasLifeTime:
			return csstatus.CIB_MSG_ITEM_NO_USE_TIME

		if not self.query( "spell", 0 ):
			return csstatus.CIB_MSG_ITEM_NOT_USED

		springUsedCD = self.query( "springUsedCD", {} )
		player = BigWorld.player()
		for cd in springUsedCD:
			endTime = player.getCooldown( cd )[3]
			if endTime > Time.time():
				return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON

	def copy( self ):
		"""
		复制自己

		@return: 继承于CItemBase的自定义类型道具实例
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		return obj

	def getProDescription( self, reference ):
		"""
		virtual method
		获取物品专有描述信息
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		

		# 显示物品分类，等级需求
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if reference.level < self.getReqLevel():
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		if desReqlevel != "":
			self.desFrame.SetDescription("itemreqLevel" , desReqlevel)
		useDegreeDes = attrMap["useDegree"].description( self, reference )
		if useDegreeDes != "":
			self.desFrame.SetDescription( "useDegree", useDegreeDes )
	
		# 物品本身等级(策划暂时划掉这属性，但以防他们反悔，暂时只是注释掉，方便加起来)
	#	desLevel = attrMap["level"].description( self, reference )
	#	if desLevel != "":
	#		self.desFrame.SetDescription( "itemLevel" , desLevel )
		# 传送点记录信息
		teleportRes = attrMap["ch_teleportRecord"].description( self, reference )
		if teleportRes != "":
			teleportRes = PL_Font.getSource( teleportRes, fc = ( 0, 255, 0 ) )
			self.desFrame.SetDescription( "ch_teleportRecord", teleportRes )
		# 战场积分
		warIntegralDes = attrMap["warIntegral"].description( self, reference )
		if warIntegralDes != "":
			self.desFrame.SetDescription( "warIntegral", warIntegralDes )
		# 宝石的附加属性
		desStuList = attrMap["bj_extraEffect"].descriptionList( self, reference )
		if len( desStuList ):
			desStuListTemp = [ PL_Font.getSource( des[0] ,fc = "c27" ) + " " + PL_Font.getSource( des[1] ,fc = "c27" ) for des in desStuList ]
			self.desFrame.SetDesSeveral( "bj_extraEffect", desStuListTemp )
		# 宝石镶嵌位置
		deswWieldType = attrMap["bj_slotLocation"].description( self, reference )
		if deswWieldType != "":
			deswWieldType = PL_Font.getSource( deswWieldType, fc = "c27" )
			self.desFrame.SetDescription( "bj_slotLocation", deswWieldType )

	def description( self, reference ):
		"""
		产生描述

		@param reference: 玩家entity,表示以谁来做为生成描述的参照物
		@type  reference: Entity
		@return:          物品的字符串描述
		@rtype:           ARRAY of str
		"""
		# 显示物品相关信息
		self.getProDescription( reference )	#显示物品本身的信息

		attrMap = ItemAttrClass.m_itemAttrMap
		# 显示物品名字，根据物品的品质决定物品名字的颜色
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = self.getQualityColor() )
		self.desFrame.SetDescription("name" , nameDes)
		# 物品类型
		desType = attrMap["type"].description( self, reference )
		self.desFrame.SetDescription( "type", desType )
		# 需求声望
		reqCredits = attrMap["reqCredit"].descriptionDict( self, reference )
		if reqCredits:
			reqCreditsDes = reqCredits.keys()
			for index in xrange( len( reqCreditsDes) ):
				if not reqCredits[ reqCreditsDes[index] ]:
					reqCreditsDes[ index ] = PL_Font.getSource( reqCreditsDes[ index ] , fc = "c3" )
			self.desFrame.SetDesSeveral( "reqCredit", reqCreditsDes )
	
		#是否绑定
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			desBind = PL_Font.getSource( desBind , fc = "c1" )
			self.desFrame.SetDescription( "bindType", desBind )
		#是否已认主 by姜毅
		type = self.getType()
		if not type in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
			print self.isWhite()
			canEqu = False
			if type in equ_items_type:
				canEqu = True
			if canEqu and not self.isWhite():
				desObey = attrMap["eq_obey"].description( self, reference )
				if desObey != "":
					desObey = PL_Font.getSource( desObey, fc = "c7" )
					self.desFrame.SetDescription( "eq_obey", desObey )
		#是否唯一
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CItemBase[1] )
		# 是否可出售
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CItemBase[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )
		# 取得额外的描述1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 )
		# 取得额外的描述2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
		#	if des1 != "": des2 = g_newLine + des2
			self.desFrame.SetDescription( "describe2", des2 )
		# 取得额外的描述3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
		#	if des1 != "" or des2 != "": des3 = g_newLine + des3
			self.desFrame.SetDescription( "describe3", des3 )

		# 剩余使用时间
		lifeType = self.getLifeType()
		if lifeType:
			lifeTime = self.getLifeTime()
			if lifeTime:
				deadTime = self.getDeadTime()
				if deadTime:
					sTime = int( Time.time() )
					rTime = deadTime - sTime
					if rTime > lifeTime: rTime = lifeTime
					des = lbs_CItemBase[3]
					if rTime <= 0:
						des += lbs_CItemBase[4]
					else:
						hour = rTime/3600
						min = ( rTime - hour * 3600 )/60
						sec = rTime%60

						# 修改时间的描述显示 by姜毅
						day = int( hour / 24 )

						if day:
							des += lbs_CItemBase[5] % day
						elif int( hour ):
							des += lbs_CItemBase[6] % hour
						elif int( min ):
							des += lbs_CItemBase[7] % min
						else:
							des += lbs_CItemBase[8] % sec
					des = PL_Font.getSource( des, fc = "c3" )
					self.desFrame.SetDescription( "lifeType", des )
			else:
				des = PL_Font.getSource( lbs_CItemBase[9], fc = "c3" )
				self.desFrame.SetDescription( "lifeType", des )

		return self.desFrame.GetDescription()

	def getPrice( self ):
		"""
		获取当前道具价值，有可能会需要根据某些特性计算
		"""
		# 物品的价格跟使用次数有关
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

	def getQuestID( self ):
		"""
		获取该物品触发的任务ID
		"""
		return self.query( "questID", 0 )

	def getBjExtraEffect( self ):
		"""
		获取宝石附加属性
		"""
		return self.query( "bj_extraEffect", [] )

	def getPrefix( self ):
		"""
		获取物品的前缀
		"""
		return self.query( "prefix", 0 )

	def getMaxSpace( self ):
		"""
		"""
		return self.query( "kb_maxSpace", 0 )

	def getQuality( self ):
		"""
		获取物品的品质
		"""
		return self.query( "quality", 1 )

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

	def getUseDegree( self ):
		"""
		取得使用次数
		"""
		return self.query( "useDegree", 0 )

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

	def isOverdue( self ):
		"""
		virtual method.
		判断是否
		"""
		if not self.isActiveLifeTime(): return False
		return Time.time() > self.getDeadTime()


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

	def getVehicleMoveSpeed( self ):
		"""
		获取该物品的移动速度数据(骑宠)
		"""
		return self.query( "vehicle_move_speed", 0.0 )

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

	def getQualityColor( self ) :
		"""
		获取品质颜色
		hyw--2010.01.28
		"""
		return g_equipQualityExp.getColorByQuality( self.getQuality() )

	def getGodWeaponSkillID( self ):
		"""
		获取神器属性技能ID
		"""
		return 0

	def checkUseStatus( self, owner ) :
		"""
		检查物品的使用情况
		"""
		if owner.level < self.getReqLevel() :
			return Define.ITEM_STATUS_USELESSNESS
		return Define.ITEM_STATUS_NATURAL
