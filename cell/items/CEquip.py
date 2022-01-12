# -*- coding: gb18030 -*-

# $Id: CEquip.py,v 1.33 2008-09-04 07:44:43 kebiao Exp $

"""
装备类基础模块
"""
from CItemBase import CItemBase
import funcEquip
from bwdebug import *
import csdefine
import Const
import random
import csconst
import SkillTypeImpl
import ItemTypeEnum
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()
from EquipSuitLoader import EquipSuitLoader
g_equipSuit = EquipSuitLoader.instance()
from ItemSystemExp import EquipIntensifyExp
g_equipIntensify = EquipIntensifyExp.instance()
from ItemSystemExp import ItemTypeAmendExp
g_typeAmend = ItemTypeAmendExp.instance()
from ItemSystemExp import EquipQualityExp
g_itemQualityExp = EquipQualityExp.instance()
from ItemSystemExp import PropertyPrefixExp
g_itemPropPrefixExp = PropertyPrefixExp.instance()
from ItemSystemExp import EquipAttrExp
g_itemPropAttrExp = EquipAttrExp.instance()

from config.server.EquipIntensifyAttr import Datas as EIA_DATA

import random
import math

from config.item.EquipAttrRebuildProb import Datas as attrRebuildProb

class CEquip( CItemBase ):
	"""
	装备基础类

	@ivar wieldStatus: 装备状态；0或该属性不存在则表示没有装备效果，1表示装备了效果；
	                   这个值可能会保存，但不读取，每次玩家登录的时候都会重新更新这个值
	                     - 0 表示该装备没有装备上效果
	                     - 1 表示正常装备,对于武器来说表示它装备的伤害是单手伤害
	                     - 2 对于武器来说表示它装备的伤害是双手伤害
	@type wieldStatus: UINT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )

	def fullName( self ):
		"""
		获取物品的全名 如 雄鹰的逆天的霸王弓
		"""
		#if len( self.getCreateEffect() ):
		#	return self.name()
		return CItemBase.fullName( self )

	def getFDict( self ):
		"""
		Virtual Method
		获取法宝效果类型自定义数据格式
		用于发送到客户端
		return INT32
		"""
		raise AssertionError, "I can't do this!"

	def isAlreadyWield( self ):
		"""
		判断是否已经装备上效果了

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_wieldStatus", 0 ) > 0

	def isSuitEffectWield( self ):
		"""
		判断是否已经装备上套装属性了

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_suitEffectStatus", 0 ) > 0

	def getWieldOrders( self ):
		"""
		取得当前物品的可装备位置列表，即该物品可以放在装备栏的哪些位置上；CEL_*

		@return: tuple of int
		@rtype:  tuple of int
		"""
		return funcEquip.m_cwt2cel[self.query( "eq_wieldType" )]

	def getUnwieldOrders( self, equipKitbag, equipOrder ):
		"""
		用于当要装备某种类型的装备时检查装备栏需要卸下哪些位置的装备

		@param equipKitbag: 装备栏
		@type  equipKitbag: KitbagType
		@param  equipOrder: 想要装备的位置
		@type   equipOrder: INT8
		@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
		                    如果指定的装备位置与当前函数默认的类型对应的位置不符则返回None
		@rtype:             tuple of UINT8/None
		"""
		return funcEquip.m_unwieldCheck[self.query( "eq_wieldType" )]( equipKitbag, equipOrder )

	def wieldExtraEffect( self, owner ):
		"""
		装备附加属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self  )

	def unWieldExtraEffect( self, owner ):
		"""
		卸载附加属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

	def wieldCreateEffect( self, owner ):
		"""
		装备灌注属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		createEffect = self.getCreateEffect()
		for key, value in createEffect:
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self  )

	def unWieldCreateEffect( self, owner ):
		"""
		卸载灌注属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		createEffect = self.getCreateEffect()
		for key, value in createEffect:
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

	def wieldSuitEffect( self, owner ):
		"""
		装备套装属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		suitEffect = self.query( "eq_suitEffect", {} )
		for suitKey, suitValue in suitEffect.iteritems():
			effectClass = g_equipEffect.getEffect( suitKey )
			if effectClass is None: continue
			effectClass.attach( owner, suitValue, self  )

	def unWieldSuitEffect( self, owner ):
		"""
		卸载套装属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		suitEffect = self.query( "eq_suitEffect", {} )
		for suitKey, suitValue in suitEffect.iteritems():
			effectClass = g_equipEffect.getEffect( suitKey )
			if effectClass is None: continue
			effectClass.detach( owner, suitValue, self  )

	def wieldBjEffect( self, owner ):
		"""
		装备镶嵌属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		bjEffect = self.getBjExtraEffect()
		for data in bjEffect:
			effectClass = g_equipEffect.getEffect( data[0] )
			if effectClass is None: continue
			effectClass.attach( owner, data[1], self  )

	def unWieldBjEffect( self, owner ):
		"""
		卸载镶嵌属性
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return:    None
		"""
		bjEffect = self.getBjExtraEffect()
		for data in bjEffect:
			effectClass = g_equipEffect.getEffect( data[0] )
			if effectClass is None: continue
			effectClass.detach( owner, data[1], self  )

	def wield( self, owner, update = True ):
		"""
		装备道具

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		# 已装备不可能再次装备，这个是效果是否产生问题，和装备要求扯不上，因此不放在canWield里
		if self.isAlreadyWield(): return False
		if not self.canWield( owner ): return False

		# 装备附加属性
		self.wieldExtraEffect( owner )

		# 装备灌注属性
		self.wieldCreateEffect( owner )

		# 装备镶嵌属性
		self.wieldBjEffect( owner )

		# 当前装备为绿色装备才有可能触发套装是否激活
		# 身上穿的是一套绿色套装，激活所有绿色装备的套装属性
		isSuitEqu = False
		if self.isGreen():
			suitEquipIDs = owner.getSuitEquipIDs()
			if g_equipSuit.isSuit( suitEquipIDs ):
				isSuitEqu = True
				for equip in owner.getAllGreenEquips():
					if equip.isSuitEffectWield(): continue
					equip.wieldSuitEffect( owner )
					equip.setTemp( "eq_suitEffectStatus", 1, owner )

		# 判断强化套效果
		# 玩家身上有至少7件装备（可以是防具、武器、首饰中任7件）的强化等级为9时，玩家会获得强化套装效果1：
		# 角色物理攻击力提高3％，角色法术攻击力提高3%；物理防御值提高3%，法术防御值提高3%，全身获得一个光效。
		# 玩家全身装备的强化等级为9时，玩家会获得强化套装效果2：
		# 角色物理攻击力提高6％，角色法术攻击力提高6%；物理防御值提高6%，法术防御值提高6%，获得一个更华丽的光效。

		# 标识已装备上效果
		self.setTemp( "eq_wieldStatus", 1, owner )

		# 处理装备后的效果，如装备计时，装备绑定
		self.onWield( owner )
		owner.questItemAmountChanged( self, -1 )	# 装备成功，影响任务目标。
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		if not self.isAlreadyWield(): return
		self.setTemp( "eq_wieldStatus", 0, owner )		# 标识没有装备上效果
		# 卸下附加属性
		self.unWieldExtraEffect( owner )

		# 写下灌注属性
		self.unWieldCreateEffect( owner )

		# 卸下镶嵌属性
		self.unWieldBjEffect( owner )

		# 卸下一个装备的时候，如果剩下的装备还是套装则只卸下自己的套装属性
		# 如果不是则卸下所有的套装属性
		if self.isGreen():
			greenEquipIDs = owner.getSuitEquipIDs()
			if not g_equipSuit.isSuit( greenEquipIDs ):
				for equip in owner.getAllGreenEquips():
					if not equip.isSuitEffectWield(): continue
					equip.unWieldSuitEffect( owner )
					equip.setTemp( "eq_suitEffectStatus", 0, owner )

		if self.isSuitEffectWield():
			self.unWieldSuitEffect( owner )
			self.setTemp( "eq_suitEffectStatus", 0, owner )

		if update: owner.calcDynamicProperties()
		owner.questItemAmountChanged( self, 1 )		# 卸下装备，影响任务目标。
		return

	def onWield( self, owner ):
		"""
		vitural method
		"""
		# 激活装备后计时的使用时间
		lifeType = self.getLifeType()
		if lifeType in [ItemTypeEnum.CLTT_ON_WIELD, ItemTypeEnum.CLTT_ON_WIELD_EVER]:
			self.activaLifeTime( owner )

		# 装备绑定类型
		bindType = self.getBindType()
		isBinded = self.isBinded()
		if bindType == ItemTypeEnum.CBT_EQUIP and not isBinded:
			self.setBindType( ItemTypeEnum.CBT_EQUIP, owner )

	def canWield( self, owner ):
		"""
		检查是否能装备物品效果

		@param owner: 道具的使用者（即拥有者）
		@type  owner: Entity
		@return:    True 允许装备，False 不允许装备
		@return:    BOOL
		"""
		if not self._checkReqlevel( owner ): return False
		if not self._checkReqGender( owner ): return False
		if not self._checkClasses( owner ): return False
		if not self._checkHardiness(): return False
		if not self._checkLifeTime(): return False
		return True

	def isSystemEquip( self ):
		"""
		判断是否为系统装备

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.query( "isSystemItem" ) == 1

	def _checkLifeTime( self ):
		"""
		检查使用时间
		"""
		lifeType = self.getLifeType()
		lifeTime = self.getLifeTime()
		if lifeType and not lifeTime: return False
		return True

	def _checkHardiness( self ):
		"""
		检查当前耐久度
		对于一个装备而言，如果当前耐久度为None，即该装备总是可以装备的
		@return: 大于0或不存在这个属性则返回True，否则返回False
		@rtype:  BOOL
		"""
		hMax = self.query( "eq_hardinessMax" )
		if hMax is None or hMax <= 0: return True
		return self.query( "eq_hardiness" ) > 0

	def _checkClasses( self, owner ):
		"""
		检查可装备职业

		@return: 匹配则返回True, 否则返回False
		@rtype:  BOOL
		"""
		return self.isMetier( owner.getClass() )

	def _checkReqlevel( self, owner ):
		"""
		检查装备等级

		@param owner: 背包拥有者
		@type  owner: Entity
		@return: 匹配则返回True, 否则返回False
		@rtype:  BOOL
		"""
		return owner.level >= self.query( "reqLevel", 0 )

	def _checkReqGender( self, owner ):
		"""
		检查装备需求性别

		@param owner: 物品拥有者
		@type  owner: Entity
		@return: 匹配则返回True, 否则返回False
		@rtype:  BOOL
		"""
		reqGender = self.getReqGender()
		if len( reqGender ) == 0: return True
		return owner.getGender() in reqGender

	def isMetier( self, metierType ):
		"""
		判断是否可以装备在某个职业上

		@parma metierType: 职业类型; CEM_*; 可以使用“或(|)”来连接多个，表示能同时支持这么多个职业装备。
		@type  metierType: UINT16
		@return: 如果可以在某职业上装备则返回True，否则返回False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		# 没有classes则表示没有此需求
		if reqClasses is None: return True
		return metierType in reqClasses

	def isMetierOnly( self, metierType ):
		"""
		判断是否只能装备在某个职业上

		@parma metierType: 职业类型; CEM_*
		@type  metierType: UINT16
		@return: 如果只能在指定的职业上装备则返回True，否则返回False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		# 没有classes则表示没有此需求
		if reqClasses is None: return True
		return reqClasses  == [ metierType ]

	def getHardinessMax( self ):
		"""
		获得最大耐久度上限(此值不变)
		@return: 最大耐久度上限,如果没有耐久度上限则为0
		@rtype: int
		"""
		return self.query( "eq_hardinessMax", 0 )

	def getHardinessLimit( self ):
		"""
		获得当前耐久度上限(此值能更改)

		@return: 最大耐久度,如果没有耐久度则为0
		@rtype: int
		"""
		return self.query( "eq_hardinessLimit", 0 )

	def getHardiness( self ):
		"""
		获得当前耐久度
		@return: 当前耐久度,如果没有耐久度则为0
		@rtype: int
		"""
		return self.query( "eq_hardiness", 0 )

	def addHardiness( self, hardiness, owner = None ):
		"""
		增加当前装备的耐久度

		@param hardiness: 耐久值
		@type  hardiness: UINT16
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return: 无
		"""
		self.setHardiness( self.getHardiness() + hardiness, owner )

	def setHardiness( self, hardiness, owner = None ):
		"""
		设置当前装备的耐久度
		如果参数“owner”为None，则不会更新数据

		@param hardiness: 耐久值
		@type  hardiness: UINT16
		@param  owner: 装备拥有者
		@type   owner: Entity
		@return: 无
		"""
		# 如果旧的耐久和新的耐久度相等，直接返回
		oldHardiness = self.getHardiness()
		if hardiness < 0: hardiness = 0
		if oldHardiness == hardiness: return

		# 限定新的耐久度不能超过当前耐久度上限也不能小于0
		hardinessLimit = self.getHardinessLimit()
		if hardiness > hardinessLimit:
			hardiness = hardinessLimit

		self.set( "eq_hardiness", int( hardiness ), owner )
		# phw 20091226: 这个日志量比战斗的日志量还要恐怖，因此，在没有什么问题的情况下，不再输出。
		#if owner is None:
		#	DEBUG_MSG( "None Owner set %s [%i] eq_hardiness from %i to %i" % ( self.name(), self.uid, oldHardiness, int( hardiness ) ) )
		#else:
		#	DEBUG_MSG( "%s [%i] set %s [%i] eq_hardiness from %i to %i" % ( owner.getName(), owner.id, self.name(), self.uid, oldHardiness, int( hardiness ) ) )

		# 如果装备在装备栏上，并且玩家存在
		if owner and self.getKitID() == csdefine.KB_EQUIP_ID:
			# 如果旧的耐久度为0，那么就重新装上该装备
			if oldHardiness <= 0:
				self.wield( owner )
				owner.resetEquipModel( self.order, self )
			# 如果新的耐久度为0，那么就卸下该装备
			if hardiness == 0:
				self.unWield( owner )
				owner.resetEquipModel( self.order, None )

	def addHardinessLimit( self, hardiness, owner = None ):
		"""
		增加当前装备的最大耐久度

		@param hardiness: 耐久值
		@type  hardiness: UINT16
		@return: 无
		"""
		self.setHardinessLimit( self.getHardinessLimit() + hardiness, owner )

	def setHardinessLimit( self, hardiness, owner = None ):
		"""
		设置当前装备的耐久度上限
		如果参数“owner”为None，则不会更新数据

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param hardiness: 耐久值
		@type  hardiness: UINT16
		@return: 无
		"""
		hardinessMax = self.getHardinessMax()
		oldHardinessLimint = self.getHardinessLimit()
		if hardiness > hardinessMax:
			hardiness = hardinessMax
		if hardiness < 0:
			hardiness = 0
		self.set( "eq_hardinessLimit", int( hardiness ), owner )

		if owner is None:
			DEBUG_MSG( "None Owner set %s [%i] eq_hardinessLimit from %i to %i" % ( self.name(), self.uid, oldHardinessLimint, int( hardiness ) ) )
		else:
			DEBUG_MSG( "%s [%i] set %s [%i] eq_hardinessLimit from %i to %i" % ( owner.getName(), owner.id, self.name(), self.uid, oldHardinessLimint, int( hardiness ) ) )

		# 如果当前耐久度大于当前耐久度上限
		# 强制其等于当前耐久度上限
		if self.getHardiness() > hardiness:
			self.setHardiness( hardiness, owner )

	def getIntensifyLevel( self ):
		"""
		获取装备强化等级
		"""
		return self.query( "eq_intensifyLevel", 0 )
	
	def model( self ):
		"""
		获取模型编号
		"""
		try:
			modelList = self.srcData["model"].split(";")
			model = modelList[0]
			if self.getIntensifyLevel() >= 5 and len( modelList ) > 1:
				model = modelList[1] if modelList[1] else model
			if self.getIntensifyLevel() >= 8 and len( modelList ) > 2 :
				model = modelList[2] if modelList[2] else model
			return int ( model )
		except:
			return 0

	def addIntensifyLevel( self, intensifyLevel, owner = None ):
		"""
		增加当前装备的耐久度
		@param hardiness: 耐久值
		@type  hardiness: UINT16
		@param    owner: 装备拥有者
		@type     owner: Entity
		@return: 无
		"""
		self.setIntensifyLevel( self.getIntensifyLevel() + intensifyLevel,  owner )

	def setIntensifyLevel( self, intensifyLevel, owner = None ):
		"""
		设置装备强化等级
		virtual method
		@param intensifyLevel: 强化等级
		@type  intensifyLevel: bool
		@param    owner: 装备拥有者
		@type     owner: Entity
		@return:    无
		"""
		# 强化影响基础属性品质比率
		oldLevel = self.getIntensifyLevel()
		if oldLevel == intensifyLevel: return
		# 设置强化等级
		self.set( "eq_intensifyLevel", intensifyLevel, owner )
		#检测御敌、破敌属性增加
		wieldType = self.query( "eq_wieldType" )
		if EIA_DATA.has_key( intensifyLevel ) and EIA_DATA[intensifyLevel].has_key( wieldType ): #开始附加属性
			attrInfo = EIA_DATA[intensifyLevel][wieldType]
			level = self.getLevel()
			if attrInfo[0] > 0:
				self.set( "eq_ReduceRoleD", attrInfo[0], owner )
			if attrInfo[1] > 0:
				self.set( "eq_AddRoleD", attrInfo[1], owner )
		else:
			self.set( "eq_ReduceRoleD", 0.0, owner )
			self.set( "eq_AddRoleD",    0.0, owner )

	def setQuality( self, quality, owner = None ):
		"""
		设置该物品的品质
		物品的品质改变直接导致
		基础属性品质比率和附加属性品质比率的改变
		@param    quality: 物品品质
		@type     quality: INT8
		@param owner: 装备拥有者
		@type  owner: Entity
		@return None
		"""
		# 计算基础属性品质比率
		oldQuality = self.getQuality()
		if oldQuality == quality: return

		prefix = self.getPrefix()
		

		# 计算基础属性品质比率
		newQBaseRate = g_itemQualityExp.getBaseRateByQuality( quality, prefix )
		self.setBaseRate( newQBaseRate, owner )

		# 计算附加属性品质比率
		newExcRate = g_itemQualityExp.getexcRateByQandP( quality, prefix )
		self.setExcRate( newExcRate, owner )

		# 设置品质
		CItemBase.setQuality( self, quality, owner )

		# 重新计算耐久度
		self.CalculateHardiness( owner )

		# 刷新价格
		self.updatePrice( owner )

	def setPrefix( self, prefix, owner = None ):
		"""
		设置该物品的前缀
		物品的前缀改变直接导致附加属性品质比率的改变
		最新规则显示前缀的改变会影响绿色装备的基础属性品质比率
		@param    prefix: 物品前缀
		@type     prefix: INT8
		@param owner: 装备拥有者
		@type  owner: Entity
		@return None
		"""
		# 重新计算耐久度
		self.CalculateHardiness( owner )

		# 刷新价格
		self.updatePrice( owner )

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

	def getMagicPower( self ):
		"""
		获取魔法攻击力
		"""
		return self.query( "eq_magicPower", 0 )

	def getSlot( self ):
		"""
		获取装备已使用孔数
		"""
		return self.query( "eq_slot", 0 )

	def getLimitSlot( self ):
		"""
		获取装备当前拥有孔数
		"""
		return self.query( "eq_limitSlot", 0 )

	def getMaxSlot( self ):
		"""
		获取此装备最大能拥有的孔数
		"""
		return self.query( "eq_maxSlot", 0 )

	def setLimitSlot( self, slotAmount, owner = None ):
		"""
		设置当前装备拥有孔数
		@param    slotAmount: 装备孔数
		@type     slotAmount: UINT8
		@param owner: 装备拥有者
		@type  owner: Entity
		@return:    无
		"""
		self.set( "eq_limitSlot", slotAmount, owner )

	def setSlot( self, slotAmount, owner = None ):
		"""
		设置当前装备已镶嵌孔数
		@param    slotAmount: 装备孔数
		@type     slotAmount: UINT8
		@param owner: 装备拥有者
		@type  owner: Entity
		@return:    无
		"""
		self.set( "eq_slot", slotAmount, owner )

	def updataHardiness( self, value, owner = None ):
		"""
		设置耐久度的值
		"""
		self.set( "eq_hardinessMax",   int( value ), owner )
		self.set( "eq_hardinessLimit", int( value ), owner )
		self.set( "eq_hardiness",      int( value ), owner )

	def CalculateHardiness( self , owner ):
		"""
		计算耐久度(品质改变时要重新计算耐久度)
		"""
		pass

	def getExtraEffect( self ):
		"""
		获取装备附加属性
		@return:    dict
		"""
		return self.query( "eq_extraEffect", {} )

	def getCreateEffect( self ):
		"""
		获取装备灌注属性
		@return:    dict
		"""
		return self.query( "eq_createEffect", [] )
		
	# 获取装备上已灌注的属性 by mushuang
	# @return type:[] （包含所有已经灌注属性的列表）
	def getPouredCreateEffect( self ):
		res = []
		for effect in self.query( "eq_createEffect", [] ):
			if effect != ( 0, 0 ):
				res.append( effect )
		return res

	def addCreateEffect( self, effect, owner = None ):
		"""
		添加灌注属性
		"""
		oldEffect = self.getCreateEffect()
		oldEffect.extend( effect )
		self.setCreateEffect( oldEffect, owner )

	def setCreateEffect( self, effect, owner = None ):
		"""
		设置灌注属性
		"""
		self.set( "eq_createEffect", effect, owner )

	def createRandomEffect( self, owner = None ):
		"""
		生成装备的随机属性
		@param owner: 装备拥有者
		@type  owner: Entity
		@return Bool
		"""
		itemKey = self.id
		quality = self.getQuality()
		level = self.getLevel()
		type = self.getType()
		datas = {}
		if quality != ItemTypeEnum.CQT_WHITE:
			if not self.getExtraEffect():
				datas = g_itemPropAttrExp.getEquipRandomEffect( itemKey, level, type, quality )
		# 获取随机属性失败
		if not datas: return False
		randomEffect = datas["dic"]
		
		self.set( "eq_extraEffect", randomEffect, owner )
		return True

	def fixedCreateRandomEffect( self, quality, owner = None, suitEffect = False ):
		"""
		根据固定的前缀 品质 属性前缀 创建物品的随机属性
		@param quality: 品质
		@type  quality: INT
		@param prefix: 前缀
		@type  prefix: INT
		@param proPrefixID: 属性前缀
		@type  proPrefixID: INT
		@param owner: 装备拥有者
		@type  owner: Entity
		@param suitEffect: 是否随机套装属性
		@type  suitEffect: BOOL
		@return Bool
		"""
		datas = {}
		if not self.getExtraEffect():
			datas = g_itemPropAttrExp.getEquipRandomEffect( self.id, self.getLevel(), self.getType(), quality )
		# 获取随机属性失败
		if not datas: return False
		randomEffect = datas["dic"]
		
		self.set( "eq_extraEffect", randomEffect, owner )
		return True

	def isEquip( self ):
		"""
		virtual method.
		判断是否是装备
		"""
		return True

	def canRepair( self ):	# wsf add,15:30 2008-7-2
		"""
		virtual method.
		判断一个物品是否能被修理
		@return: BOOL
		@rtype:  BOOL
		"""
		if not CItemBase.canRepair( self ): return False
		hMax = self.query( "eq_hardinessMax" )
		if hMax is None or hMax <= 0: return False
		return self.query("eq_hardinessLimit") > 0

	def setIntensifyValue( self, value, owner = None ):
		"""
		设置装备的强化附加值属性
		"""
		self.set( "intensifyValue", value, owner )

	def getIntensifyValue( self ):
		"""
		获取装备的强化附加值属性

		@rtype : [ [ 强化的物理攻击力, 强化的魔法攻击力 ], [ 强化的物理防御值, 强化的魔法防御值 ] ]
		"""
		return self.query( "intensifyValue", [ [ 0, 0 ], [ 0, 0 ] ] )

	def updatePrice( self, owner = None ):
		"""
		刷新物品的价格
		由于一些计算物品价格的参数改变，价格也做相应改变了
		由于装备的基础属性品质比率不是固定的，那么价格也会随着相应的变动
		装备分手写装备和系统装备，其中系统装备品质，前缀，强化等级改变会影响基础属性品质比率和附加属性品质比率
			1、系统装备( 受品质，前缀，强化等级影响)会改变价格
			2、手写装备(只受强化等级影响)会改变价格

		计算公式为:
		价值因子 = 物品类型修正率 * 1.82*（7.5*（2*等级*附加属性品质比率）^1.54+（等级^1.5*2.5+60）*附加属性品质比率）
		价格 = 物品类型修正率*（道具等级^2*基础属性品质比率+价值因子/3）
		"""
		# 获取物品的类型修正率
		typeAmend = g_typeAmend.getGeneAmend( self.getType() )
		# 获取物品的等级
		level = self.getLevel()
		# 获取物品的基础属性品质比率( 装备强化后会影响该值 )
		baseQualityRate = self.getBaseRate()
		# 获取物品的附加属性品质比率( 跟品质和前缀有关)
		excQualityRate = self.getExcRate()
		# 计算物品的价值因子
		priceGene = typeAmend * 1.82 * ( 7.5 * ( 2 * level * excQualityRate ) ** 1.54 + ( level ** 1.5 * 2.5 + 60 ) * excQualityRate )
		# 计算物品的价格
		price = typeAmend * ( level**2*baseQualityRate ) + priceGene/3
		self.setPrice( price, owner )

	def getPrice( self ):
		"""
		获取装备的价格
		跟耐久度有关
		"""
		# 装备的价格 = 当前耐久度/原始最大耐久度*装备原始卖店价格
		basePrice = self.getRecodePrice()
		hardinessMax = self.getHardinessMax()
		if hardinessMax == 0: return basePrice
		newPrice = int( self.getHardiness() * 1.0 / self.getHardinessMax() * basePrice )
		if newPrice <= 0: return 1
		return newPrice
	
	# ----------------------------------------------------------------
	# 设置装备飞升者的名字
	# ----------------------------------------------------------------
	def setQualityUpper( self, name, owner ) :
		"""
		@name(string): 装备飞升者的名字
		@owner: 装备的持有人
		"""
		self.set( "eq_upper", name, owner )
		
	# ----------------------------------------------------------------
	# 装备属性重铸 by mushuang
	# ----------------------------------------------------------------
	def attrRebuild( self, attrType, effectId, owner = None):		
		
		# 获取装备的“价值因子”
		priceGeneMin = g_itemPropAttrExp.getItemPriceGene( self.id, self.getLevel(), self.getType(), self.getQuality(), ItemTypeEnum.CPT_FABULOUS ) # 传说绿装
		priceGeneMax = g_itemPropAttrExp.getItemPriceGene( self.id, self.getLevel(), self.getType(), self.getQuality(), ItemTypeEnum.CPT_MYGOD ) # 逆天绿装
		
		# 算出每条属性的价值因子
		attrGeneMin = priceGeneMin * csconst.EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR
		attrGeneMax = priceGeneMax * csconst.EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR
		
		
		genePerPoint = g_equipEffect.getPerGene( effectId )
		if genePerPoint == 0 : return False# 属性id无效时会返回0
		
		# 算出属性初始值
		minValue = attrGeneMin / genePerPoint
		
		# 算出属性最大值
		maxValue = attrGeneMax / genePerPoint

		# 计算步进
		step = ( maxValue - minValue ) / csconst.EQUIP_ATTR_REBUILD_STAGES
		
		# 产生概率并根据概率得到阶次
		chance = random.random()
		for i in xrange( csconst.EQUIP_ATTR_REBUILD_STAGES -1 , -1, -1):
			if chance > attrRebuildProb[ i ]: 
				n = i + 1
				break
		
		# 根据阶次，步进，初始值计算新的属性值
		newValue = minValue + n * step
		
		# if 新的属性值 > 最大值
		if newValue > maxValue:
			# 新的属性值 = 最大值
			newValue = maxValue
		
		#添加属性类型区分，加值向下取整，加成不变 by cxm 2010.10.13
		type = g_equipEffect.getType( effectId )
		if type == ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD:
			maxValue = int( maxValue )
			newValue = int( newValue )
		
		# 保存新的属性值
		if attrType == "eq_extraEffect": # 附加属性
			extraEffect = self.query( "eq_extraEffect" ) # {k:v}
			if not effectId in extraEffect : return False
			
			# if 该属性已经到达最大值 : return
			if extraEffect[effectId] >= maxValue : return False
			
			extraEffect[effectId] = newValue
			self.set( "eq_extraEffect", extraEffect, owner )
			return True
			
		elif attrType == "eq_createEffect": # 灌注属性
			createEffect = self.query( "eq_createEffect" ) # [(k,v)]
			# 判断该灌注属性是否存在
			idx = -1
			for ( k, v ) in createEffect:
				if k == effectId :
					idx = 	createEffect.index( ( k ,v ) )
					break
			
			
			# if 该属性不存在 : return
			if idx == -1 : return False
			
			# if 该属性已经到达最大值 : return
			if createEffect[idx][1] >= maxValue : return False
			
			# 存入新的值
			createEffect[idx] = ( effectId, newValue )
			self.set( "eq_createEffect", createEffect, owner )
			return True
			
		elif attrType == "eq_suitEffect": # 套装属性
			suitEffect = self.query( "eq_suitEffect" ) # { k:v }
			if not effectId in suitEffect : return False
			
			# if 该属性已经到达最大值 : return
			if suitEffect[effectId] >= maxValue : return False
				
			suitEffect[effectId] = newValue
			self.set( "eq_suitEffect", suitEffect, owner )
			return True
		
		return False
		
	
	def removeAllPrefix( self, player = None ):
		"""
		移除装备的各种前缀（目前而言为：装备前缀、属性前缀）
		@player: 如果player不是None，那么此次状态更新将传到客户端
		"""	
		CItemBase.setPrefix( self, ItemTypeEnum.CPT_NONE, player )
		self.set( "propertyPrefix", "", player )
#
# $Log: not supported by cvs2svn $
# Revision 1.32  2008/08/13 08:55:17  qilan
# 镶嵌改为最多有两个相同属性水晶，相应调整
#
# Revision 1.31  2008/07/17 02:33:18  yangkai
# 调整判断一个装备是否能装备和是否能修理的判断
#
# Revision 1.30  2008/07/02 07:36:18  wangshufeng
# add method:canRepair,判断一个物品是否能被修理
#
# Revision 1.29  2008/05/30 03:03:14  yangkai
# 装备栏调整引起的部分修改
#
# Revision 1.28  2008/04/22 10:46:13  yangkai
# no message
#
# Revision 1.27  2008/04/10 07:44:44  yangkai
# 方法 createRandomEffect 添加默认参数 owner
#
# Revision 1.26  2008/04/03 08:57:49  yangkai
# 添加镶嵌属性的处理
#
# Revision 1.25  2008/04/03 08:26:27  yangkai
# 添加接口createRandomEffect
#
# Revision 1.24  2008/04/03 02:07:53  yangkai
# 完善装备镶嵌等相关接口
#
# Revision 1.23  2008/04/01 00:44:36  yangkai
# 添加装备打孔相关接口
#
# Revision 1.22  2008/03/29 08:37:28  yangkai
# 装备强化完善
#
# Revision 1.21  2008/03/24 02:29:09  yangkai
# 1，添加接口 isGreen（）
# 2，添加套装属性
#
# Revision 1.20  2008/03/18 07:39:55  yangkai
# reqlevel rename to reqLevel
#
# Revision 1.19  2008/03/15 08:17:53  yangkai
# no message
#
# Revision 1.18  2008/02/28 02:30:35  yangkai
# 修改处理特效时参数
#
# Revision 1.17  2008/02/22 08:16:31  yangkai
# no message
#
# Revision 1.16  2008/02/22 01:36:25  yangkai
# 添加对装备附加属性的支持
#
# Revision 1.15  2008/02/19 08:32:34  yangkai
# 去除无用的初始化set信息
#
# Revision 1.14  2007/12/28 01:14:20  yangkai
# 初始化设强化等级为0
#
# Revision 1.13  2007/12/14 09:13:14  yangkai
# 修正装备职业判断
#
# Revision 1.12  2007/11/24 03:06:44  yangkai
# 物品系统调整，属性更名
# 当前耐久度"endure" -- > "eq_hadriness"
# 最大耐久度"currEndureLimit" --> "eq_hardinessLimit"
# 最大耐久度上限"maxEndureLimit" --> "eq_hardinessMax"
#
# Revision 1.11  2007/11/08 06:20:57  yangkai
# 增加接口：
# - intensify()
#
# Revision 1.10  2007/08/23 01:30:36  kebiao
# 随机装备修改
#
# Revision 1.9  2007/08/15 07:52:28  yangkai
# 修改:
#     - 武器属性修改
#     - 武器装备/卸下函数处理
#
# Revision 1.8  2007/08/15 04:01:07  kebiao
# 随机装备
#
# Revision 1.7  2007/06/14 09:55:52  huangyongwei
# 搬动了宏定义
#
# Revision 1.6  2007/05/17 09:12:50  huangyongwei
# 原来在 ItemBagRole 中的类变量
# KB_COUNT
# KB_EQUIP_ID
# KB_COMMON_ID
# 被移动到
# L3Define 中
#
#
# ItemBagRole.ItemBagRole.KB_EQUIP_ID
# --->
# csdefine.KB_EQUIP_ID
#
# Revision 1.5  2006/12/29 07:31:15  panguankong
# 添加判断装备接口
#
# Revision 1.4  2006/10/16 10:00:55  phw
# method modified:
#     wield()
#     unwield()
#     在装上和卸下装备时加入了对是否有被动的和装备有关的技能判断。
#
# Revision 1.3  2006/08/18 07:00:18  phw
# 删除接口：
#     description(); 为了避免以后不必要的猜测，删除不需要的接口
#
# Revision 1.2  2006/08/11 02:57:34  phw
# 属性更名：修改所有itemInstance.keyName或itemInstance.id()为itemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
