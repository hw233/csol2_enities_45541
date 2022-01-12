# -*- coding: gb18030 -*-

from CEquip import CEquip
import ItemTypeEnum
import random

from ItemSystemExp import TalismanExp
g_talisman = TalismanExp.instance()
from TalismanEffectLoader import TalismanEffectLoader
g_tmEffect = TalismanEffectLoader.instance()
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()
from config.item.TalismanAmend import Datas as TalismanAmentData

class CTalisman( CEquip ):
	"""
	法宝-继承装备
	"""
	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )
		self.__initExtraEffect()

	def getFDict( self ):
		"""
		Virtual Method
		获取法宝效果类型自定义数据格式
		用于发送到客户端
		return INT32
		"""
		return self.model()

	def icon( self ):
		"""
		获取图标路径
		"""
		grade = self.getGrade()
		if grade == ItemTypeEnum.TALISMAN_COMMON:
			return CEquip.icon( self )
		else:
			try:
				return TalismanAmentData[self.id][grade][1]
			except:
				return CEquip.icon( self )

	def model( self ):
		"""
		获取模型
		"""
		grade = self.getGrade()
		if grade == ItemTypeEnum.TALISMAN_COMMON:
			return CEquip.model( self )
		else:
			try:
				return TalismanAmentData[self.id][grade][0]
			except:
				return CEquip.model( self )

	def __initExtraEffect( self, owner = None ):
		"""
		根据法宝的品级初始化附加属性
		"""
		# 法宝初始化属性会生成6条属性。凡品2条，仙品2条，神品2条。
		# 默认情况下法宝品级激活后会激活品级对应的属性中第一条属性。
		grade = self.getGrade()
		# 生成凡品属性，默认第一个属性是激活的
		if len( self.getCommonEffect() ) == 0:
			isLive = grade >= ItemTypeEnum.TALISMAN_COMMON
			commonEffectID1 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_COMMON )
			commonEffectID2 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_COMMON )
			commonEffect = [ ( commonEffectID1, isLive ), ( commonEffectID2, False ) ]
			self.setCommonEffect( commonEffect, owner )
		# 生成仙品属性，默认第一个属性是激活的
		if len( self.getImmortalEffect() ) == 0:
			isLive = grade >= ItemTypeEnum.TALISMAN_IMMORTAL
			immortalEffectID1 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_IMMORTAL )
			immortalEffectID2 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_IMMORTAL )
			immortalEffect = [ ( immortalEffectID1, isLive ), ( immortalEffectID2, False ) ]
			self.setImmortalEffect( immortalEffect, owner )
		# 生成神品属性，默认第一个属性是激活的
		if len( self.getDeityEffect() ) == 0:
			isLive = grade >= ItemTypeEnum.TALISMAN_DEITY
			deityEffectID1 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_DEITY )
			deityEffectID2 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_DEITY )
			deityEffect = [ ( deityEffectID1, isLive ), ( deityEffectID2, False ) ]
			self.setDeityEffect( deityEffect, owner )
		# 生成破绽属性
		flawEffect = g_tmEffect.getFlawEffect()
		if len( flawEffect ):
			self.setFlawEffect( flawEffect, owner )

	def getExp( self ):
		"""
		获取法宝当前经验值
		"""
		return self.query( "tm_exp", 0 )

	def getMaxExp( self ):
		"""
		获得法宝所需最大经验值
		"""
		return g_tmEffect.getMaxExp( self.getLevel() )

	def addExp( self, exp, owner = None ):
		"""
		法宝增加经验值
		@param		exp		:	法宝经验值
		@type		exp		:	INT64
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		#--------- 以下为防沉迷系统的判断 --------#
		if owner != None and exp >=0:
			gameYield = owner.wallow_getLucreRate()
			exp = exp * gameYield
		#--------- 以上为防沉迷系统的判断 --------#
		self.setExp( self.getExp() + exp, owner )

	def setExp( self, exp, owner = None ):
		"""
		设置法宝的经验值
		@param		exp		:	法宝经验值
		@type		exp		:	INT64
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_exp", exp, owner )

	def setLevel( self, lv, owner = None ):
		"""
		设定法宝的等级
		@param		lv		:	法宝等级
		@type		lv		:	INT64
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		oldLevel = self.getLevel()
		if oldLevel == lv: return

		# 设置等级
		self.set( "level", lv, owner )

		# 如果该装备没有装备或者不允许装备直接返回
		if not self.isAlreadyWield(): return False
		if not self.canWield( owner ): return False

		# 升级随机选择技能
		skillList = g_tmEffect.getSkillListByID(self.id)
		if 0 != len(skillList) and 0 == self.query( "spell", 0 ):
			odd = g_tmEffect.getOdds(self.getLevel())
			if random.randint(1, 10000) <= odd * 10000:
				skillID = random.choice(skillList) * 1000 + 1
				self.setSKillID( skillID, owner )
				if owner: owner.addSkill( skillID )

		# 升级基本附加属性增加
		# 卸载基本属性
		extraEffect = self.getExtraEffect()
		newExtraEffect = dict( extraEffect )
		baseExtraEffect = self.queryBaseData( "eq_extraEffect", {} )
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			# 计算新属性
			beginValue = baseExtraEffect.get( key )
			if beginValue is None: continue
			param = g_tmEffect.getBaseUpParam()
			newValue = beginValue + lv * param
			# 卸载旧属性
			effectClass.detach( owner, value, self )
			# 附加新属性
			effectClass.attach( owner, newValue, self )
			# 存储新属性
			newExtraEffect[key] = newValue
		# 设置新基本附加属性
		self.set( "eq_extraEffect", newExtraEffect, owner )

		if owner is None: return
		totalEffect = []
		# 凡品属性
		commonEffect = self.getCommonEffect()
		totalEffect.extend( commonEffect )
		# 仙品属性
		immortalEffect = self.getImmortalEffect()
		totalEffect.extend( immortalEffect )
		# 神品属性
		deityEffect = self.getDeityEffect()
		totalEffect.extend( deityEffect )

		for key, state in totalEffect:
			# 过滤未激活的属性
			if not state: continue
			# 获取属性脚本
			effectKey =  g_tmEffect.getEffectID( key )
			effectClass = g_equipEffect.getEffect( effectKey )
			if effectClass is None: continue
			# 计算属性差值
			param = g_tmEffect.getUpParam( key )
			value = ( lv - oldLevel ) * param
			# 附加属性差值
			effectClass.attach( owner, value, self )

		# 刷新玩家属性
		owner.calcDynamicProperties()

	def getPotential( self ):
		"""
		获取法宝当前潜能值
		"""
		return self.query( "tm_potential", 0 )

	def getMaxPotential( self ):
		"""
		获得法宝所需最大潜能值
		"""
		if 0 == self.getSkillLevel():
			return 0
		return g_tmEffect.getPotential(self.getSkillLevel())

	def addPotential( self, exp, owner = None ):
		"""
		法宝增加潜能值
		@param		exp		:	法宝潜能值
		@type		exp		:	INT64
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.setPotential( self.getPotential() + exp, owner )

	def setPotential( self, exp, owner = None ):
		"""
		设置法宝的潜能
		@param		exp		:	法宝经验值
		@type		exp		:	INT64
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_potential", exp, owner )

	def getSkillLevel( self ):
		"""
		获得法宝技能的等级
		"""
		return self.query( "spell", 0 ) % 1000

	def setSkillLevel( self, lv, owner = None ):
		"""
		设定法宝技能的等级
		@param		lv		:	法宝技能等级
		@type		lv		:	INT64
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		skillID = self.query( "spell", 0 )
		if 0 == skillID:return
		newSkillID = skillID - self.getSkillLevel() + lv
		self.setSKillID( newSkillID, owner )

	def getGrade( self ):
		"""
		获取法宝的品级
		"""
		return self.query( "tm_grade", ItemTypeEnum.TALISMAN_COMMON )

	def setGrade( self, grade, owner = None ):
		"""
		设置法宝的品级
		@param		grade	:	法宝品级
		@type		grade	:	INT8
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		if grade == self.getGrade(): return
		if grade < ItemTypeEnum.TALISMAN_COMMON: return
		if grade > ItemTypeEnum.TALISMAN_DEITY: return
		self.set( "tm_grade", grade, owner  )
		# 激活品级对应的第一条属性
		if grade == ItemTypeEnum.TALISMAN_IMMORTAL:
			effect = list( self.getImmortalEffect() )
			fuc = self.setImmortalEffect
		elif grade == ItemTypeEnum.TALISMAN_DEITY:
			effect = list( self.getDeityEffect() )
			fuc = self.setDeityEffect
		else:
			return

		if len( effect ) == 0: return
		key, state = effect.pop(0)
		# 已是激活状态，直接返回
		if state: return
		effectKey =  g_tmEffect.getEffectID( key )
		effectClass = g_equipEffect.getEffect( effectKey )
		if effectClass is None: return
		# 计算附加属性
		initEffectValue = g_tmEffect.getInitValue( key )
		param = g_tmEffect.getUpParam( key )
		value = initEffectValue + self.getLevel() * param
		# 附加属性
		effectClass.attach( owner, value, self )
		# 更改本身属性
		effect.insert( 0, ( key, True ) )
		fuc( effect, owner )
		# 给玩家计算属性
		if owner is None: return

		owner.calcDynamicProperties()

	def getSkillID( self ):
		"""
		获取技能ID
		"""
		return self.query( "spell", 0 )

	def setSKillID( self, skillID, owner = None ):
		"""
		设置法宝的技能ID
		@param		skillID	:	技能ID
		@type		skillID	:	INT64
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		if owner is not None:
			oldID = self.getSkillID()
			if oldID != 0:
				owner.updateSkill( oldID, skillID )
			else:
				owner.addSkill( skillID )
			self.set( "spell", skillID, owner )

	def getCommonEffect( self ):
		"""
		获取法宝的凡品属性
		"""
		return self.query( "tm_commonEffect", [] )

	def getImmortalEffect( self ):
		"""
		获取法宝的仙品属性
		"""
		return self.query( "tm_immortalEffect", [] )

	def getDeityEffect( self ):
		"""
		获取法宝的神品属性
		"""
		return self.query( "tm_deityEffect", [] )

	def getFlawEffect( self ):
		"""
		获取法宝的破绽属性
		"""
		return self.query( "tm_flawEffect", {} )

	def setCommonEffect( self, effect, owner = None ):
		"""
		设置法宝的凡品附加属性
		@param		effect	:	附加属性
		@type		effect	:	dict
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_commonEffect", effect, owner )

	def setImmortalEffect( self, effect, owner = None ):
		"""
		设置法宝的仙品附加属性
		@param		effect	:	附加属性
		@type		effect	:	dict
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_immortalEffect", effect, owner )

	def setDeityEffect( self, effect, owner = None ):
		"""
		设置法宝的神品附加属性
		@param		effect	:	附加属性
		@type		effect	:	dict
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_deityEffect", effect, owner )

	def setFlawEffect( self, effect, owner = None ):
		"""
		设置法宝的破绽属性
		@param		effect	:	附加属性
		@type		effect	:	dict
		@param		owner	:	法宝拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_flawEffect", effect, owner )

	def wield( self, owner, update = True ):
		"""
		装备道具

		@param  owner: 法宝拥有者
		@type   owner: Entity
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		if owner is None: return
		if not CEquip.wield( self, owner, update ):
			return False

		# 装备技能
		skillID = self.getSkillID()
		if 0 != skillID and not owner.hasSkill( skillID ):
			#玩家装备道具可以发生在装上装备 和 上线重新装备两个行为上。如果是上线重新装上装备，那么法宝对应的技能，玩家已经拥有了的。
			#再调用addSkill 会引起警告，既然我们都知道这个情况，那就把这种情况排除，避免警告发生。
			owner.addSkill(skillID)

		intensifyLevel = self.getIntensifyLevel()
		grade = self.getGrade()
		# 附加属性
		totalEffect = []
		# 凡品属性
		commonEffect = self.getCommonEffect()
		totalEffect.extend( commonEffect )
		# 仙品属性
		immortalEffect = self.getImmortalEffect()
		totalEffect.extend( immortalEffect )
		# 神品属性
		deityEffect = self.getDeityEffect()
		totalEffect.extend( deityEffect )

		for key, state in totalEffect:	# 附加属性
			# 过滤未激活的属性
			if not state: continue
			# 获取属性脚本
			effectKey =  g_tmEffect.getEffectID( key )
			effectClass = g_equipEffect.getEffect( effectKey )
			if effectClass is None: continue
			# 计算附加属性
			initEffectValue = g_tmEffect.getInitValue( key )
			param = g_tmEffect.getUpParam( key )
			value = initEffectValue + self.getLevel() * param
			if intensifyLevel != 0:
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# 强化附加比率
				value = (1.0 + iRate) * value
			# 附加属性
			effectClass.attach( owner, value, self )

		if intensifyLevel != 0:
			baseExtraEffect = self.getExtraEffect()
			for key, value in baseExtraEffect.iteritems():
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None: continue
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# 强化附加比率
				value *= iRate
				effectClass.attach( owner, value, self  )

		# 破绽属性
		flawEffect = self.getFlawEffect()
		for key, value in flawEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self )

		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param  owner: 法宝拥有者
		@type   owner: Entity
		@return:    无
		"""
		if owner is None: return
		# 如果没有装备效果则不用unwield
		if not self.isAlreadyWield(): return

		# 卸下
		skillID = self.getSkillID()
		if 0 != skillID:owner.removeSkill(skillID)

		intensifyLevel = self.getIntensifyLevel()
		grade = self.getGrade()
		# 附加属性
		totalEffect = []
		# 凡品属性
		commonEffect = self.getCommonEffect()
		totalEffect.extend( commonEffect )
		# 仙品属性
		immortalEffect = self.getImmortalEffect()
		totalEffect.extend( immortalEffect )
		# 神品属性
		deityEffect = self.getDeityEffect()
		totalEffect.extend( deityEffect )

		if intensifyLevel != 0:
			baseExtraEffect = self.getExtraEffect()
			for key, value in baseExtraEffect.iteritems():
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None: continue
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# 强化附加比率
				value *= iRate
				effectClass.detach( owner, value, self  )

		for key, state in totalEffect:
			# 过滤未激活的属性
			if not state: continue
			# 获取属性脚本
			effectKey =  g_tmEffect.getEffectID( key )
			effectClass = g_equipEffect.getEffect( effectKey )
			if effectClass is None: continue
			# 计算附加属性
			initEffectValue = g_tmEffect.getInitValue( key )
			param = g_tmEffect.getUpParam( key )
			value = initEffectValue + self.getLevel() * param
			if intensifyLevel != 0:
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# 强化附加比率
				value = (1.0 + iRate) * value
			# 附加属性
			effectClass.detach( owner, value, self )

		# 破绽属性
		flawEffect = self.getFlawEffect()
		for key, value in flawEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

		CEquip.unWield( self, owner, update )
		return True