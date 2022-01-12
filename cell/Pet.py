# -*- coding: gb18030 -*-
#
# $Id: Pet.py,v 1.86 2008-09-04 07:44:14 kebiao Exp $

"""
This module implements the pet entity.

2007/07/16 : wirten by huangyongwei
2007/10/24 : base on new version documents, it is rewirten by huangyongwei
"""

import items
import time
import BigWorld
import csdefine
import csconst
import csstatus
import Const
import ECBExtend
import Language
import ShareTexts
from bwdebug import *
from PetFormulas import formulas
from LevelEXP import PetLevelEXP
from NPCObject import NPCObject
from interface.PetAI import PetAI
from interface.SkillBox import SkillBox
from interface.CombatUnit import CombatUnit
from interface.CombatUnit import calcProperty
from Love3 import g_skillTeachDatas
from Love3 import g_skills
from Love3 import g_equipEffect
from ObjectScripts.GameObjectFactory import g_objFactory

# --------------------------------------------------------------------
# 宠物所属角色包装
# --------------------------------------------------------------------
class _PetOwner( object ) :
	__slots__ = ( "etype", "entity" )
	def __init__( self, mbBase ) :
		entity = BigWorld.entities.get( mbBase.id )
		if entity is None :
			self.etype = "MAILBOX"
			self.entity = mbBase.cell
		elif entity.isReal() :
			self.etype = "REAL"
			self.entity = entity
		else :
			self.etype = "GHOST"
			self.entity = entity


# --------------------------------------------------------------------
# 宠物
# --------------------------------------------------------------------
class Pet( NPCObject, PetAI, SkillBox ) :
	__typesMaps = {}
	__typesMaps[ csdefine.PET_TYPE_STRENGTH ]	= ShareTexts.PET_TYPE_STRENGTH
	__typesMaps[ csdefine.PET_TYPE_SMART ]		= ShareTexts.PET_TYPE_SMART
	__typesMaps[ csdefine.PET_TYPE_INTELLECT ]	= ShareTexts.PET_TYPE_INTELLECT
	__typesMaps[ csdefine.PET_TYPE_BALANCED ]	= ShareTexts.PET_TYPE_BALANCED

	__attrNamesMaps = {}
	__attrNamesMaps[ "corporeity" ]	    = ShareTexts.PET_CORPOREITY_ENHANCE
	__attrNamesMaps[ "strength" ]		= ShareTexts.PET_STRENGTH_ENHANCE
	__attrNamesMaps[ "intellect" ] 		= ShareTexts.PET_INTELLECT_ENHANCE
	__attrNamesMaps[ "dexterity" ] 		= ShareTexts.PET_DEXTERITY_ENHANCE

	def __init__( self ) :
		NPCObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_PET )				# 设置宠物类别
		PetAI.__init__( self )
		SkillBox.__init__( self )

		self.initSkills()

		self.initialize()

		self.notifyDefOwner_( "onGetPetCell", self )
		self.isUseCombatCamp = True

	# ----------------------------------------------------------------
	# initialize methods
	# ----------------------------------------------------------------
	def initialize( self ) :
		self.changeState( csdefine.ENTITY_STATE_FREE )				# 初始状态
		self.tickCount = 0											# 心跳次数
		self.joyancyDecTime = time.time()							# 初始化快乐度递减时间
		self.__heartbeatTimerID = self.addTimer( 1.0, Const.PET_HEARTBEAT_INTERVAL, ECBExtend.PET_HEARTBEAT_CBID )
		self.__startRevert()										# 启动 HP 和 MP 回复
		self.__calcSndAttrsBase()
		self.setJoyancy( self.joyancy )
		if self.HP == 0 or self.isDeadWithdraw :					# 判断上次回收是否是因为死亡
			self.full()												# 如果是死亡回收的，则让宠物满血满魔
			self.isDeadWithdraw = False								# 将死亡回收标记设置为 False


	# ----------------------------------------------------------------
	# tussle formulas
	# ----------------------------------------------------------------
	def calcHPMax( self ):
		"""
		<virtual/>
		HP 最大值
		"""
		PetAI.calcHPMax( self )
		self.__startRevert()

	def calcHPMaxBase( self ):
		"""
		virtual method.
		HP 基础值
		"""
		self.HP_Max_base = int( formulas.getBaseHPMax( self.corporeity, self.ability, self.level ) )

	def calcMPMax( self ):
		"""
		<virtual/>
		MP 最大值
		"""
		PetAI.calcMPMax( self )
		self.__startRevert()

	def calcMPMaxBase( self ):
		"""
		virtual method.
		MP 基础值
		"""
		self.MP_Max_base = int( formulas.getBaseMPMax( self.intellect, self.ability, self.level ) )

	def calcHPCureSpeed( self ):
		"""
		<virtual/>
		计算生命恢复速度(每3秒可以恢复的生命数值。战斗时无效。数值读表。)
		"""
		self.HP_regen_base = 3.0 * self.corporeity * 0.03 + 11
		PetAI.calcHPCureSpeed( self )

	def calcMPCureSpeed( self ):
		"""
		<virtual/>
		计算法力回复速度(每3秒可以恢复的法力数值。战斗时无效。数值读表。)
		"""
		self.MP_regen_base = 3.0 * self.intellect * 0.03 + 15
		PetAI.calcMPCureSpeed( self )

	# ---------------------------------------
	def calcPhysicsDPSBase( self ):
		"""
		计算物理DPS_base值
		"""
		self.physics_dps_base = int( formulas.getBasePhysicsDPS( self.species, self.ability, self.strength, self.dexterity, self.level ) * csconst.FLOAT_ZIP_PERCENT )

	# ---------------------------------------
	def calcDoubleHitProbabilityBase( self ):
		"""
		物理爆击率
		"""
		self.double_hit_probability_base = int( formulas.getDoubleHitProbability( self.species, self.level, self.dexterity, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	def calcMagicDoubleHitProbabilityBase( self ):
		"""
		法术爆击率
		"""
		self.magic_double_hit_probability_base = int( formulas.getMagicDoubleHitProbability( self.species, self.level, self.intellect, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	def calcDodgeProbabilityBase( self ):
		"""
		闪避率 基础值
		角色闪躲对方攻击的几率。普通物理攻击可以被闪避。物理技能攻击和法术技能攻击不能被闪避。闪避成功后，被攻击方本次攻击不受任何伤害。
		"""
		self.dodge_probability_base = int( formulas.getDodgeProbability( self.species, self.level, self.dexterity, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	def calcResistHitProbabilityBase( self ):
		"""
		招架率
		招架率是指招架发生的几率，普通物理攻击，物理技能攻击，都能够被招架。但是法术攻击，不能被招架。招架成功后，角色受到的伤害降低50%
		"""
		self.resist_hit_probability_base = int( formulas.getResistProbability( self.species, self.level, self.strength, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	# ---------------------------------------
	def calcArmorBase( self ):
		"""
		virtual method
		物理防御值	表示当角色受到物理攻击时，能对此物理攻击力进行削减的能力。
		"""
		self.armor_base = formulas.getPhysicsArmorRadies( self.species, self.level, self.ability )

	def calcMagicArmorBase( self ):
		"""
		virtual method
		法术防御值	表示当角色受到法术攻击时，能对此法术攻击力进行削减的能力。
		"""
		self.magic_armor_base = formulas.getMagicArmorRadies( self.species, self.level, self.ability )

	# ---------------------------------------
	def calcHitSpeedBase( self ):
		"""
		攻击速度
		"""
		self.hit_speed_base = int( formulas.getHitSpeed( self.species ) * csconst.FLOAT_ZIP_PERCENT )

	# ---------------------------------------
	def calcDamageMinBase( self ):
		"""
		计算最小物理攻击力 基础值
		"""
		self.damage_min_base =  formulas.getMinDamage( self.species, self.physics_dps )

	def calcDamageMaxBase( self ):
		"""
		计算最大物理攻击力 基础值
		"""
		self.damage_max_base = formulas.getMaxDamage( self.species, self.physics_dps )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		法术攻击力
		"""
		self.magic_damage_base = formulas.getMagicDamage( self.ability, self.species, self.intellect, self.level )

	# ---------------------------------------
	def calcDamageMin( self ):
		"""
		计算最小物理攻击力
		"""
		PetAI.calcDamageMin( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDamageMin( self.damage_min )

	def calcDamageMax( self ):
		"""
		计算最大物理攻击力
		"""
		PetAI.calcDamageMax( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDamageMax( self.damage_max )

	# ---------------------------------------
	def calcMagicDamage( self ):
		"""
		virtual method
		法术攻击力
		"""
		PetAI.calcMagicDamage( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetMagicDamage( self.magic_damage )

	# ---------------------------------------
	def calcArmor( self ):
		"""
		virtual method
		物理防御值	表示当角色受到物理攻击时，能对此物理攻击力进行削减的能力。
		"""
		PetAI.calcArmor( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetArmor( self.armor )

	def calcMagicArmor( self ):
		"""
		virtual method
		法术防御值	表示当角色受到法术攻击时，能对此法术攻击力进行削减的能力。
		"""
		PetAI.calcMagicArmor( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetMagicArmor( self.magic_armor )

	# ---------------------------------------
	def calcDodgeProbability( self ):
		"""
		闪避率
		角色闪躲对方攻击的几率。普通物理攻击可以被闪避。物理技能攻击和法术技能攻击不能被闪避。闪避成功后，被攻击方本次攻击不受任何伤害。
		"""
		PetAI.calcDodgeProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDodgeProbability( self.dodge_probability )

	# ---------------------------------------
	def calcResistHitProbability( self ):
		"""
		招架率
		招架率是指招架发生的几率，普通物理攻击，物理技能攻击，都能够被招架。但是法术攻击，不能被招架。招架成功后，角色受到的伤害降低50%
		"""
		PetAI.calcResistHitProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistHitProbability( self.resist_hit_probability )

	# ---------------------------------------
	def calcDoubleHitProbability( self ):
		"""
		物理爆击率
		"""
		PetAI.calcDoubleHitProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDoubleHitProbability( self.double_hit_probability )

	def calcMagicDoubleHitProbability( self ):
		"""
		法术爆击率
		"""
		PetAI.calcMagicDoubleHitProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetMagicDoubleHitProbability( self.magic_double_hit_probability )

	# ---------------------------------------
	def calcResistGiddyProbability( self ):
		"""
		计算抵抗眩晕几率
		"""
		PetAI.calcResistGiddyProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistGiddyProbability( self.resist_giddy_probability )

	def calcResistFixProbability( self ):
		"""
		计算抵抗定身几率
		"""
		PetAI.calcResistFixProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistFixProbability( self.resist_fix_probability )

	def calcResistChenmoProbability( self ):
		"""
		计算抵抗沉默几率
		"""
		PetAI.calcResistChenmoProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistChenmoProbability( self.resist_chenmo_probability )

	def calcResistSleepProbability( self ):
		"""
		计算抵抗睡眠几率
		"""
		PetAI.calcResistSleepProbability( self )
		# 由于属性的改变， 我们应该通知客户端重新获取数据
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistSleepProbability( self.resist_sleep_probability )

	def calcElemHuoDerateRatio( self ):
		"""
		计算火元素抗性 规则上 宠物元素抗性最多到8成
		"""
		self.elem_huo_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_huo_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemXuanDerateRatio( self ):
		"""
		计算玄元素抗性 规则上 宠物元素抗性最多到8成
		"""
		self.elem_xuan_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_xuan_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemLeiDerateRatio( self ):
		"""
		计算雷元素抗性 规则上 宠物元素抗性最多到8成
		"""
		self.elem_lei_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_lei_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemBingDerateRatio( self ):
		"""
		计算冰元素抗性 规则上 宠物元素抗性最多到8成
		"""
		self.elem_bing_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_bing_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcRange( self ):
		"""
		virtual method.

		计算攻击距离
		"""
		ptype = self.getPType()
		if ptype == csdefine.PET_TYPE_SMART:		# 敏捷型宠物
			self.range_base = Const.PET_SMART_RANGE
		elif ptype == csdefine.PET_TYPE_INTELLECT:	# 智力型宠物
			self.range_base = Const.PET_INTELLECT_RANGE

		PetAI.calcRange( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __calcSndAttrsBase( self ) :
		"""
		重新计算宠物基础属性
		注意：当基础属性改变时，其战斗属性也跟着改变，因此这里还要重新计算战斗属性
		"""
		sndAttrValues = formulas.getSndProperties( self.species, self.level, self.nimbus )
		self.corporeity_base = self.e_corporeity + sndAttrValues["corporeity"]
		self.strength_base = self.e_strength + sndAttrValues["strength"]
		self.intellect_base = self.e_intellect + sndAttrValues["intellect"]
		self.dexterity_base = self.e_dexterity + sndAttrValues["dexterity"]
		self.move_speed_base = 90000					# 基础移动速度
		self.HP_regen_base = 10							# HP 回复速度
		self.calcDynamicProperties()

	# -------------------------------------------------
	def __lifeDetecting( self ) :
		"""
		寿命耗减侦测
		"""
		self.addLife( -formulas.getTickLifeDecreasement( self.getHierarchy() ) )

	def __joyancyDetecting( self ) :
		"""
		快乐度递减侦测
		"""
		self.addJoyancy( -formulas.getTickJoyancyDecreasement() )


	# -------------------------------------------------
	def __startRevert( self ):
		"""
		启动 HP / MP 恢复
		"""
		if self.__revertTimerID : return
		if self.isState( csdefine.ENTITY_STATE_FIGHT ) : return
		if self.isState( csdefine.ENTITY_STATE_DEAD ) : return
		if self.HP >= self.HP_Max and self.MP >= self.MP_Max : return
		self.__revertTimerID = self.addTimer( Const.PET_MP_REVER_INTERVAL, Const.PET_MP_REVER_INTERVAL, ECBExtend.REVERT_HPMP_TIMER_CBID )

	def __stopRevert( self ):
		"""
		结束 HP/MP 恢复
		"""
		if self.__revertTimerID:
			self.cancel( self.__revertTimerID )
			self.__revertTimerID = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def hackVerify_( self, srcEntityID ) :
		"""
		验证是否是欺骗性操作
		"""
		if srcEntityID != self.ownerID :
			hacker = BigWorld.entities.get( srcEntityID, None )
			if hacker :
				hacker.statusMessage( csstatus.GB_INVALID_CALLER )
			HACK_MSG( "unright srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return False
		elif self.state == csdefine.ENTITY_STATE_DEAD :
			return False
		return True

	# -------------------------------------------------
	def notifyOwner_( self, methodName, *args ) :
		"""
		调用所属玩家的非 def 方法
		"""
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner is None :
			self.baseOwner.remoteCall( methodName, args )
		elif owner.isReal() :
			getattr( owner, methodName )( *args )
		else :
			owner.remoteCall( methodName, args )

	def notifyDefOwner_( self, methodName, *args ) :
		"""
		调用所属玩家的 def 方法
		"""
		owner = self.getOwner()
		getattr( owner.entity, methodName )( *args )

	def notifyClient_( self, methodName, *args ) :
		"""
		调用所属角色的客户端方法
		"""
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner is None :
			getattr( self.baseOwner.client, methodName )( *args )
		else :
			getattr( owner.client, methodName )( *args )

	def notifyMyClient_( self, methodName, *args ):
		"""
		调用自己的客户端方法
		"""
		if self.baseOwner is None:
			return
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner is not None :
			client = owner.clientEntity( self.id )
			getattr( client, methodName )( *args )
		else :
			INFO_MSG("Pet(id %i) can't find owner(id %i) in current cellapp."%(self.id, self.baseOwner.id))

	# -------------------------------------------------
	def onAddBuff( self, buff ) :
		"""
		添加一个 buff
		"""
		self.notifyClient_( "pcg_onPetAddBuff", buff )
		PetAI.onAddBuff( self, buff )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.onPetAddBuff( buff )

	def onRemoveBuff( self, buff ) :
		"""
		删除一个 buff
		"""
		self.notifyClient_( "pcg_onPetRemoveBuff", buff[ "index" ] )
		PetAI.onRemoveBuff( self, buff )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.onPetRemoveBuff( buff )

	# ----------------------------------------------------------------
	# public methods called by owner
	# ----------------------------------------------------------------
	def withdraw( self, wmode ) :
		"""
		defined method.
		回收宠物
		"""
		if wmode == csdefine.PET_WITHDRAW_COMMON and \
			self.isState( csdefine.ENTITY_STATE_FIGHT ) :
			self.statusMessage( csstatus.PET_WITHDRAW_FAIL_IN_FIGHT )
		else :
			self.base.withdraw( wmode )

	def free( self ) :
		"""
		放生宠物
		"""
		if self.isState( csdefine.ENTITY_STATE_FIGHT ) :
			self.notifyDefOwner_( "pcg_onFreeResult", csstatus.PET_FREE_FAIL_FIGHTING )
		else :
			self.base.withdraw( csdefine.PET_WITHDRAW_FREE )

	# -------------------------------------------------
	def rejuvenesce( self, evolveType ) :
		"""
		define method.
		还童
		"""
		newHierarchy = formulas.getRejuvenesceHierarchy( self.getHierarchy() )
		ptype = self.getPType()
		self.species = ptype | newHierarchy
		self.name = formulas.getDisplayName( self.species, self.uname, "" )

		self.EXP = 0

		self.e_corporeity = 0
		self.e_strength = 0
		self.e_intellect = 0
		self.e_dexterity = 0

		self.ec_corporeity = 0
		self.ec_strength = 0
		self.ec_intellect = 0
		self.ec_dexterity = 0
		self.ec_free = 0

		for attrName in ["corporeity", "strength", "intellect", "dexterity", "free"]:
			self.notifyMyClient_( "onSetEC_" + attrName, getattr( self, "ec_" + attrName ) )

		self.ability = formulas.getAbility( self.takeLevel, newHierarchy, evolveType, self.stamp )
		self.setAbility( self.ability )
		self.setNimbus( 0 )
		self.setCalcaneus( 0 )

		self.character = formulas.getCharacter()
		self.setCharacter( self.character )
		self.life = csconst.PET_LIFE_UPPER_LIMIT
		self.setLife( self.life )
		self.joyancy = csconst.PET_JOYANCY_UPPER_LIMIT
		self.setJoyancy( self.joyancy )

		self.level = 1
		self.__calcSndAttrsBase()
		self.resetSkill()			# 还童后重置技能。10:47 2009-2-14，wsf
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )

		self.statusMessage( csstatus.PET_EVOLVE_SUCCESS )

	def combine( self, dbid ) :
		"""
		define method.
		合成宠物
		"""
		maxNimbus = formulas.getMaxNimbus( self.level )
		if self.nimbus >= maxNimbus :
			self.notifyDefOwner_( "pcg_onCombineResult", csstatus.PET_COMBINE_FAIL_NIMBUS_FULL,"" )
		else :
			self.baseOwner.pcg_combinePets( self.level, dbid )

	def enhance( self, etype, attrName, value ) :
		"""
		define method.
		强化
		"""
		if not hasattr( self, attrName ) :
			HACK_MSG( "the attribute '%s' is not exist! enhance fail" % attrName )
			self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_HACK )
			return

		def allownCommonEnhance() :
			"""
			普通强化
			"""
			maxCcount = formulas.getFixedEnhanceCount( self.species, attrName, self.level )
			count = getattr( self, "ec_" + attrName )
			if count >= maxCcount :
				self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_COM_FULL, self.__attrNamesMaps[attrName] )
				return False
			setattr( self, "ec_" + attrName, count + 1 )
			self.notifyMyClient_( "onSetEC_" + attrName, getattr( self, "ec_" + attrName ) )
			return True

		def allowFreeEnhance() :
			"""
			自由强化
			"""
			maxCcount = formulas.getFreeEnhanceCount( self.level )
			if self.ec_free >= maxCcount :
				self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_FREE_FULL )
				return False
			self.ec_free += 1
			self.notifyMyClient_( "onSetEC_free", self.ec_free )
			return True

		verifies = {}
		verifies[csdefine.PET_ENHANCE_COMMON]	= allownCommonEnhance
		verifies[csdefine.PET_ENHANCE_FREE]		= allowFreeEnhance
		if etype in verifies :
			if verifies[etype]() :
				getattr( self, "addE" + attrName )( value )
				self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_SUCCESS )
		else :
			self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_HACK )

	# -------------------------------------------------
	def lifeup( self, value ) :
		"""
		延寿
		"""
		if self.life >= csconst.PET_LIFE_UPPER_LIMIT :											# 无须延寿
			self.notifyDefOwner_( "pcg_onAddLifeResult", csstatus.PET_ADD_LIFE_FAIL_FULL )
		else :
			self.addLife( value )
			self.notifyDefOwner_( "pcg_onAddLifeResult", csstatus.PET_ADD_LIFE_SUCCESS )

	def domesticate( self, value ) :
		"""
		驯养
		"""
		if self.joyancy < csconst.PET_JOYANCY_UPPER_LIMIT :										# 无须驯养
			self.addJoyancy( value )
			self.notifyDefOwner_( "pcg_onAddJoyancyResult", csstatus.PET_ADD_JOYANCY_SUCCESS )

	# -------------------------------------------------
	def setEXP( self, value ) :
		"""
		define method
		设置 EXP
		"""
		expMax = PetLevelEXP.getEXPMax( self.level )
		self.EXP = min( max( value, 0 ), expMax )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def statusMessage( self, *args ) :
		"""
		将系统消息发送到所属玩家的客户端
		"""
		self.notifyOwner_( "statusMessage", *args )

	# -------------------------------------------------
	def getOwner( self ) :
		"""
		获取所属角色的 cell entity 或 cellmailbox
		@rtype					: _PetOwner
		@return					: 返回宠物所属角色的包装，请不要保存此返回实例以供长期使用
								: 注意：不会返回 None，因为宠物总会有主人
		"""
		return _PetOwner( self.baseOwner )

	def getName( self ) :
		"""
		获取宠物名字
		"""
		return formulas.getDisplayName( self.species, self.uname, "" )

	def getNameAndID( self ) :
		"""
		获取宠物名字
		"""
		return formulas.getDisplayName( self.species, self.uname, "" ) + "(%s)" % self.databaseID

	def getHierarchy( self ) :
		"""
		获取宠物辈分
		"""
		return self.species & csdefine.PET_HIERARCHY_MASK

	def getPType( self ) :
		"""
		获取宠物类别
		"""
		return self.species & csdefine.PET_TYPE_MASK

	def getClass( self ):
		"""
		获取宠物职业
		"""
		return self.getPType()

	def isRaceclass( self, rc, mask = csdefine.PET_TYPE_MASK ):
		"""
		是否为指定种族职业。
		"""
		return self.species & mask == rc

	def tlskillNum( self ):
		"""
		天赋技能的个数
		"""
		mapMonsterScript = g_objFactory.getObject( self.getOwner().entity.pcg_petDict.get( self.databaseID ).mapMonster )
		vpet = g_objFactory.getObject( mapMonsterScript.mapPetID )
		return vpet.getInbornSkillsCount()

	def getStamp( self ):
		"""
		获得宠物印记，手写或者系统
		"""
		return self.stamp

	# ----------------------------------------------------------------
	# defined methids called by base
	# ----------------------------------------------------------------
	def rename( self, newName ) :
		"""
		defined.
		重命名宠物
		"""
		self.name = newName
		self.notifyDefOwner_( "pcg_onRenameResult", csstatus.PET_RENAME_SUCCESS )

	def queryPetNimbus( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_PET_NIMBUS, str(( self.nimbus, )) )

	def queryPetLife( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_PET_LIFE, str(( self.life, )) )

	def queryPetJoyancy( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_PET_JOYANCY, str(( self.joyancy, )) )

	def queryPetPropagate( self, queryerMB, params ):
		"""
		define method
		"""
		if self.species & csdefine.PET_HIERARCHY_MASK == csdefine.PET_HIERARCHY_GROWNUP:
			queryerMB.client.onStatusMessage( csstatus.STRING_PET_HIERARCHY_GROWNUP, "" )
		if self.species & csdefine.PET_HIERARCHY_MASK == csdefine.PET_HIERARCHY_INFANCY1:
			queryerMB.client.onStatusMessage( csstatus.STRING_PET_HIERARCHY_INFANCY1, "" )
		if self.species & csdefine.PET_HIERARCHY_MASK == csdefine.PET_HIERARCHY_INFANCY2:
			queryerMB.client.onStatusMessage( csstatus.STRING_PET_HIERARCHY_INFANCY2, "" )


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def requestSkillBox( self, srcEntityID ) :
		"""
		<Exposed/>
		发送自身所有的skillID到请求者所在的client
		"""
		self.notifyClient_( "pcg_onInitPetSkillBox", self.getSkills() )

	def requestBuffs( self, srcEntityID ) :
		"""
		<Exposed/>
		请求发送所有 buff
		"""
		if srcEntityID == self.ownerID :					# 如果是所属玩家申请
			for buff in self.attrBuffs :
				self.onAddBuff( buff )
		else :												# 如果是别的玩家申请
			try : entity = BigWorld.entities[srcEntityID]
			except KeyError : return
			client = entity.clientEntity( self.id )
			for buff in self.attrBuffs :
				#检查是否需要客户端显示等其他操作
				if buff["sourceType"] != csdefine.BUFF_ORIGIN_SYSTEM:
					client.onReceiveBuff( buff )


	# ----------------------------------------------------------------
	# 更新属性方法
	# ----------------------------------------------------------------
	def setLevel( self, level ) :
		"""
		for real
		virtual method
		设置等级
		"""
		if level == self.level : return
		level = min( max( level, 1 ), PetLevelEXP.getMaxLevel() )
		if level > self.level :
			self.setJoyancy( csconst.PET_JOYANCY_UPPER_LIMIT )
			self.absorbableEXPLevelValue = 0
		oldLevel = self.level
		self.level = level
		self.__calcSndAttrsBase()
		self.setEXP( self.EXP )
		# 满血满魔
		self.full()
		self.onSkillUpgrade()
		self.statusMessage( csstatus.ACCOUNT_STATE_PET_UPDATE_GRADE, level )

	def setHP( self, value ):
		"""
		for real
		virtual method
		设置HP
		"""
		PetAI.setHP( self, value )
		self.__startRevert()

	def setMP( self, value ):
		"""
		for real
		virtual method
		设置MP
		"""
		PetAI.setMP( self, value )
		self.__startRevert()

	def calcStrength( self ):
		"""
		计算力量，并更新到客户端
		"""
		PetAI.calcStrength( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetStrength( self.strength )

	def calcIntellect( self ):
		"""
		计算智力，并更新到客户端
		"""
		PetAI.calcIntellect( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetIntellect( self.intellect )

	def calcDexterity( self ):
		"""
		计算敏捷，并更新到客户端
		"""
		PetAI.calcDexterity( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetDexterity( self.dexterity )

	def calcCorporeity( self ):
		"""
		计算体质，并更新到客户端
		"""
		PetAI.calcCorporeity( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetCorporeity( self.corporeity )

	# ---------------------------------------
	def setEcorporeity( self, value ) :
		"""
		for real
		设置强化的体质值
		"""
		value = max( value, 0 )
		self.e_corporeity = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_corporeity( self.e_corporeity )

	def setEstrength( self, value ) :
		"""
		for real
		设置强化的力量值
		"""
		value = max( value, 0 )
		self.e_strength = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_strength( self.e_strength )

	def setEintellect( self, value ) :
		"""
		for real
		设置强化的智力值
		"""
		value = max( value, 0 )
		self.e_intellect = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_intellect( self.e_intellect )

	def setEdexterity( self, value ) :
		"""
		for real
		设置强化的敏捷值
		"""
		value = max( value, 0 )
		self.e_dexterity = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_dexterity( self.e_dexterity )

	# ---------------------------------------
	def setNimbus( self, value ) :
		"""
		for real
		设置灵智
		"""
		maxNimbus = formulas.getMaxNimbus( self.level )
		self.nimbus = min( max( value, 0 ), maxNimbus )
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetNimbus( self.nimbus )

	# ---------------------------------------
	def setLife( self, value ) :
		"""
		for real
		设置寿命
		"""
		value = min( max( value, 0 ), csconst.PET_LIFE_UPPER_LIMIT )
		self.life = value
		if value == 0 :
			self.changeState( csdefine.ENTITY_STATE_DEAD )

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetLife( self.life )

	# ---------------------------------------
	def setCharacter( self, value ) :
		"""
		for real
		设置性格
		"""
		if value == 0 :
			self.changeState( csdefine.PET_CHARACTER_SUREFOOTED )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetCharacter( self.character )
	# -----------------------------------------
	def setJoyancy( self, value ) :
		"""
		for real
		设置快乐度
		"""
		value = min( max( value, 0 ), csconst.PET_JOYANCY_UPPER_LIMIT )
		self.joyancy = value

		oldPercent = self.queryTemp( "pet_effect_by_joyancy", 0.0 )
		newPercent = formulas.getJoyancyEffect( self.joyancy )
		percent = newPercent - oldPercent
		if percent != 0:
			self.setTemp( "pet_effect_by_joyancy", newPercent )
			value = percent * csconst.FLOAT_ZIP_PERCENT
			# 物理攻击
			self.damage_min_percent += value
			self.damage_max_percent += value
			self.calcDamageMin()
			self.calcDamageMax()
			# 法术攻击
			self.magic_damage_percent += value
			self.calcMagicDamage()
			# 物理防御
			self.armor_percent += value
			self.calcArmor()
			# 法术防御
			self.magic_armor_percent += value
			self.calcMagicArmor()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetJoyancy( self.joyancy )

	# -------------------------------------------------
	def setCalcaneus( self, value ):
		"""
		define method
		设置宠物根骨
		"""
		self.calcaneus = value
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetCalcaneus( self.calcaneus )
	# -------------------------------------------------
	def addEXP( self, value ) :
		"""
		defined method
		增加 EXP
		"""
		wowner = self.getOwner()
		earg, owner = wowner.etype, wowner.entity

		#--------- 以下为防沉迷系统的判断 --------#
		if earg == "REAL" and value >=0 :
			gameYield = owner.wallow_getLucreRate()
			value = value * gameYield							# 经验值取整 modify by gjx 2009-3-30
		#--------- 以上为防沉迷系统的判断 --------#

		if self.level >= csconst.PET_LEVEL_UPPER_LIMIT:			# 宠物等级上限暂时开放到110级。
			return
		if earg == "REAL":
			# 经验石经验加成
			gemExp = value * ( owner.gem_getComGemCount() + owner.ptn_getComGemCount() ) * csconst.GEM_PET_COMMON_EXP_PERCENT
			if gemExp > 0:
				owner.client.onStatusMessage( csstatus.PET_EXP_GET_FOR_STONE, str(( gemExp, )) )
				value += int( gemExp )

		maxExp = PetLevelEXP.getEXPMax( self.level )
		if self.EXP + value >= maxExp:
			if not getattr( owner,"level" ):
				return
			if self.level >= owner.level + Const.PET_EXP_LEVEL_LIMIT_GAP:	# 宠物和玩家等级差对升级的限制放到这里 by姜毅
				self.EXP = maxExp
				return
		newLevel, newEXP = formulas.getAddedEXP( self.level, self.EXP, value )
		self.EXP = newEXP
		value = int( value )
		if value > 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_GAIN_EXP, value )
		elif value < 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_LOST_EXP, -value )
		self.setLevel( newLevel )

	def addQuestEXP( self, value, questLevel ):
		"""
		define method
		增加任务经验
		衰减公式为：
		宠物等级小于任务等级5级（任务等级-宠物等级=5），完成该任务所得经验减少10%
		宠物等级小于任务等级6级（任务等级-宠物等级=6），完成该任务所得经验减少20%
		宠物等级小于任务等级7级（任务等级-宠物等级=7），完成该任务所得经验减少30%
		宠物等级小于任务等级8级（任务等级-宠物等级=8），完成该任务所得经验减少40%
		宠物等级小于任务等级9级（任务等级-宠物等级=9），完成该任务所得经验减少50%
		宠物等级小于任务等级10级（任务等级-宠物等级=10），完成该任务所得经验减少60%
		宠物等级小于任务等级11级（任务等级-宠物等级=11），完成该任务所得经验减少70%
		宠物等级小于任务等级12级以上（任务等级-宠物等级大于等于12），完成该任务获得20%经验（也就是减少80%）。
		"""
		levelMinus = questLevel - self.level
		if levelMinus > 12:
			newValue = value * 0.2
		elif levelMinus < 5:
			newValue = value
		else:
			newValue = value * ( 1 - ( levelMinus - 4 ) * 0.1 )

		self.addEXP( int( newValue ) )					# 经验值取整 modify by gjx 2009-3-30


	def absorbEXP( self, value ):
		"""
		Define method.
		从代练宝石里吸收经验

		@param value : 代练宝石的经验总值,INT32
		"""
		# 代练吸取的经验不能超过等级所需经验10% by 姜毅
		absorbLevelMax = PetLevelEXP.getEXPMax( self.level ) / 10
		oldLevel = self.level
		if self.absorbableEXPLevelValue >= absorbLevelMax:
			self.statusMessage( csstatus.PET_ABSORT_LEVEL_EXP_FULL )
			return
		limitValue = absorbLevelMax - self.absorbableEXPLevelValue
		if value > limitValue: value = limitValue

		date = time.localtime( self.absorbDate )[ 0:3 ]	# 获得年月日
		today = time.localtime()[ 0:3 ]					# 获得今天的日期
		if cmp( date, today ) != 0:						# 今天还没吸取过经验，那么设置今天的吸取上限
			expUpper = formulas.getAbsorbExpUpper( self.level )
			self.absorbableEXP = expUpper
			self.absorbDate = time.time()				# 设置吸取上限有效期
		else:
			expUpper = self.absorbableEXP
			if expUpper == 0:
				self.statusMessage( csstatus.PET_TRAIN_FEED_LIMIT ) #今天不能再吸取更多的经验值了。
				return
		tempValue = value
		if tempValue > expUpper:
			tempValue = expUpper
#		if not self.addEXP( tempValue ):
#			tempValue = 0
		self.absorbableEXP = expUpper - tempValue

		self.absorbableEXPLevelValue += value

		owner = self.getOwner().entity
		if owner.level + Const.PET_EXP_LEVEL_LIMIT_GAP > self.level:
			newLevel, newEXP = formulas.getAddedEXP( self.level, self.EXP, tempValue )
			self.EXP = newEXP
			self.setLevel( newLevel )
		else:
			self.EXP += value

		if value > 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_GAIN_EXP, tempValue )
		elif value < 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_LOST_EXP, -tempValue )

		owner.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_SUCCESS, tempValue )

	# ---------------------------------------
	def addCalcaneus( self, value ) :
		"""
		for real
		添加根骨
		"""
		value += self.calcaneus
		#hierarchy = self.species & csdefine.PET_HIERARCHY_MASK
		maxNimbus = formulas.getMaxNimbus( self.level )
		newNimbus, newCalcaneus = formulas.calcaneusToNimbus( maxNimbus, self.nimbus, value )
		upFlag = newNimbus - self.nimbus
		self.setNimbus( newNimbus )
		if self.nimbus == maxNimbus:
			self.calcaneus = 0
		else:
			self.calcaneus = newCalcaneus
		if upFlag:
			self.statusMessage( csstatus.PET_COMBINE_SUCCESS_UP_1,upFlag )
		self.setCalcaneus( self.calcaneus )
	# ---------------------------------------
	def addEcorporeity( self, value ) :
		"""
		for real
		添加体质
		"""
		self.setEcorporeity( value + self.e_corporeity )

	def addEstrength( self, value ) :
		"""
		for real
		添加力量
		"""
		self.setEstrength( value + self.e_strength )

	def addEintellect( self, value ) :
		"""
		for real
		添加智力
		"""
		self.setEintellect( value + self.e_intellect )

	def addEdexterity( self, value ) :
		"""
		for real
		添加敏捷
		"""
		self.setEdexterity( value + self.e_dexterity )

	# ---------------------------------------
	def addNimbus( self, value ) :
		"""
		for real
		添加灵值
		"""
		self.setNimbus( self.nimbus + value )

	# ---------------------------------------
	def addLife( self, value ) :
		"""
		for real
		添加寿命
		"""
		self.setLife( self.life + value )

	def addJoyancy( self, value ) :
		"""
		for real
		添加快乐度
		"""
		self.setJoyancy( self.joyancy + value )

	def setAbility( self, value ):
		"""
		define method
		设置宠物成长度
		"""
		self.ability = value
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetAbility( self.ability )

	# -------------------------------------------------
	def addSkill( self, skillID ):
		"""
		for real
		增加一个技能。
		@param skillID:	要增加的技能标识
		@type skillID:	int
		@return:		是否成功
		@rtype:			bool
		"""
		if SkillBox.addSkill( self, skillID ):
			cskill = g_skills[skillID]
			if cskill.getType() not in csconst.BASE_SKILL_TYPE_PASSIVE_SPELL_LIST:
				self.autoAddQBItem( skillID )		# 新学技能自动加到快捷栏中
			self.notifyClient_( "pcg_onPetAddSkill", skillID )
		else:
			return False
		return True

	def removeSkill( self, skillID ):
		"""
		for real
		去除一个技能。
		@param skillID:	要去除的技能标识
		@type skillID:	string
		@return:		是否成功
		@rtype:			bool
		"""
		if SkillBox.removeSkill( self, skillID ):
			PetAI.removeSkill( self, skillID )
			self.notifyClient_( "pcg_onPetRemoveSkill", skillID )
		else:
			return False
		return True

	def updateSkill( self, oldSkillID, newSkillID ):
		"""
		for real
		更新一个技能（从一个技能ID改为另一个技能ID）
		@type oldSkillID: SKILLID
		@type newSkillID: SKILLID
		"""
		if oldSkillID == newSkillID : return False
		if SkillBox.updateSkill( self, oldSkillID, newSkillID ):
			PetAI.onUpdateSkill( self, oldSkillID, newSkillID )
			self.notifyClient_( "pcg_onPetUpdateSkill", oldSkillID, newSkillID )
		else:
			return False
		return True

	def changeCooldown( self, typeID, lastTime, totalTime, endTimeVal ):
		"""
		virtual method.
		改变一个cooldown的类型
		@type  typeID: INT16
		@type timeVal: INT32
		"""
		PetAI.changeCooldown( self, typeID, lastTime, totalTime, endTimeVal )
		self.notifyClient_( "pcg_onPetCooldownChanged", typeID, lastTime, totalTime )

	# -------------------------------------------------
	def isInTeam( self ) :
		"""
		for real
		是否在队伍中
		"""
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return False
		return owner.entity.isInTeam()

	def getTeamMailbox( self ) :
		"""
		获取所属队伍
		"""
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return None
		return owner.entity.getTeamMailbox()

	# -------------------------------------------------
	def queryRelation( self, entity ) :
		"""
		virtual method.
		获取宠物与指定 entity 的关系
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT

		#if not isinstance( entity, CombatUnit ):
		#	return csdefine.RELATION_FRIEND
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		if entity.effect_state & csdefine.EFFECT_STATE_PROWL:	# 如果entity处于潜行效果状态
			return csdefine.RELATION_NOFIGHT

		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return csdefine.RELATION_NONE
		else :
			return owner.entity.queryRelation( entity )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onPetHeartbeatTimer( self, timerID, cbid ) :
		"""
		宠物心跳 timer
		"""
		if not self.isReal() : return
		self.tickCount += 1
		if self.tickCount % Const.PET_LIFE_WASTAGE_INTERVAL == Const.PET_LIFE_WASTAGE_INTERVAL - 1:
			self.__lifeDetecting()
		if self.tickCount % Const.PET_JOYANCY_WASTAGE_INTERVAL == Const.PET_JOYANCY_WASTAGE_INTERVAL -1:
			self.__joyancyDetecting()
		self.actionThinking_()


	def onPetDieWithdrawTimer( self, timerID, userData ) :
		"""
		宠物回收延时 timer
		"""
		wmode = self.queryTemp( "pet_death_status" )
		self.removeTemp( "pet_death_status" )
		if wmode :
			self.isDeadWithdraw = True
			self.base.withdraw( wmode )
		else :
			WARNING_MSG( "delay withdrawed twice!" )

	def onRevertTimer( self, timerID, cbid ):
		"""
		时间处发事件
		"""
		if self.HP < self.HP_Max :
			self.addHP( self.HP_regen )
		if self.MP < self.MP_Max :
			self.addMP( self.MP_regen )
		if self.HP_Max == self.HP and self.MP_Max == self.MP:
			self.__stopRevert()

	# -------------------------------------------------
	def onBeforeTeleport( self, newSpaceID, pos ) :
		"""
		宠物将要跳转时被调用（oldSpaceID : 当前spaceID, newSpaceID : 将要跳到的 spaceID, pos : 将要跳到的位置）
		"""
		#self.spellTarget( csconst.PENDING_SKILL_ID, self.id )		# 给宠物施加一个未决buff
		pass

	# -------------------------------------------------
	def onStateChanged( self, old, new ) :
		"""
		状态改变时被调用
		"""
		PetAI.onStateChanged( self, old, new )
		if self.isState( csdefine.ENTITY_STATE_DEAD ) and old != new :	# 如果宠物死亡
			wmode = csdefine.PET_WITHDRAW_HP_DEATH				# 默认回收方式为死亡回收
			if self.life <= 0 :													# 如果寿命为 0
				wmode = csdefine.PET_WITHDRAW_LIFE_DEATH			# 则回收方式改为寿命耗尽回收
			self.setTemp( "pet_death_status", wmode )						# 记录死亡方式
			self.addTimer( Const.PET_DIE_WITHDRAW_DELAY, 0, \
				ECBExtend.PET_DIE_WITHDRAW_DELAY_CBID )							# 死亡延时
			self.__stopRevert()													# 则，停止回复
		elif self.isState( csdefine.ENTITY_STATE_FREE ) or \
			self.isState( csdefine.ENTITY_STATE_REST ) :						# 如果进入休息或自由状态
				self.__startRevert()											# 恢复状态的改变
		elif self.isState( csdefine.ENTITY_STATE_FIGHT ) :						# 如果进入战斗状态
			self.__stopRevert()													# 则，停止回复

	def onDie( self, killerID ) :
		"""
		继承方法至CombatUnit
		@param		killerID : 杀人者的ID
		@type		killerID : OBJECT_ID
		"""
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.isSpaceCalcPkValue :							# 如果当前地图计算PK死亡惩罚
			reduceLife = int( formulas.getLostBellLifeDecreasement() * ( 1 - self.queryTemp( "pet_life_reduce_discount", 0.0 ) ) )
			self.addLife( -reduceLife )									# 则折减寿命
			reduceJoyancy = int( formulas.getLostBellJoyancyDecreasement() * ( 1 - self.queryTemp( "pet_joyancy_reduce_discount", 0.0 ) ) )
			self.addJoyancy( -reduceJoyancy )							# 折减快乐度

	# -------------------------------------------------
	def onSkillUpgrade( self ):
		"""
		技能升级
		"""
		for skillID in list( self.attrSkillBox ):
			cskill = g_skills[skillID]
			if cskill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:	# 天赋技能只能在帮会中升级
				continue
			if cskill.getLevel() < cskill.getMaxLevel():
				lv = cskill.getMaxLevel() - cskill.getLevel()
				if g_skillTeachDatas[ skillID + lv ]['ReqLevel'] <= self.level:
					self.updateSkill( skillID, skillID + lv )
				else:
					for v in xrange( lv ):
						if self.level < g_skillTeachDatas[ skillID + v + 1 ]['ReqLevel']:
							self.updateSkill( skillID, skillID + v )
							break

	def resetSkill( self ):
		"""
		根据自身当前的级别重置自身的技能数据

		wsf add,10:47 2009-2-14
		"""
		mapMonsterScript = g_objFactory.getObject( self.getOwner().entity.pcg_petDict.get( self.databaseID ).mapMonster )
		vpet = g_objFactory.getObject( mapMonsterScript.mapPetID )
		defaultSkillIDs = vpet.getDefSkillIDs( self.level )
		for skillID in list( self.attrSkillBox ):
			self.removeSkill( skillID )
			level1SkillID = skillID / 1000 * 1000 + 1
			if g_skills[level1SkillID].getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:	# 如果是天赋技能，重新获得最低阶的技能
				self.addSkill( level1SkillID )
		for defaultSkillID in defaultSkillIDs:
			self.addSkill( defaultSkillID )

	def onDestroy( self ) :
		"""
		当销毁的时候做点事情
		"""
		PetAI.onDestroy( self )
		SkillBox.onDestroy( self )
		self.cancel( self.__heartbeatTimerID )		# 停止心跳
		self.cancel( self.__revertTimerID )			# 停止回血/回蓝
		self.clearBuff( [0] ) 						# 清除身上所有的buff

		# 清除玩家对宠物的引用 BaseApp::setClient: Could not find base ***
		if not self.baseOwner:
			return
		
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.pcg_mbBaseActPet = None
			owner.pcg_actPetDBID = 0
		else:
			INFO_MSG( " My( %s, %i) owner has been destroyed!" % ( self.getName(), self.id ) )
		
		# in 1.8.6, 由于在base端，宠物所记录的owner会先于宠物destroyed，
		# 且由于宠物总是和它的主人（玩家）在同一个baseapp，
		# 如果不把此属性置为None，则base会由于无法找到主人的base而使服务器crash.
		self.baseOwner = None

	def removePetBuff( self, buffID, index ):
		"""
		defined method
		删除宠物身上一个BUFF
		"""
		buff = None
		try :
			buff = self.getBuff( index )
		except :
			ERROR_MSG( "pet %d required remove buff, but the given index %d is out of range!" % ( self.id, index ) )
			return

		if buff["skill"].getID() == buffID and g_skills[buffID].isBenign() :
			self.removeBuff( index, [csdefine.BUFF_INTERRUPT_REQUEST_CANCEL] )
		else :
			DEBUG_MSG( "pet: %d. the buff he required to remove is not mach or it is not a benign buff" % self.id )

	def requeryPetDatas( self, srcEntityID ):
		"""
		exposed method
		获取宠物数据
		"""
		petDatas = {}
		observer = BigWorld.entities.get( srcEntityID, None )
		if observer is None:
			return
		petDatas["databaseID"] = self.databaseID
		petDatas["uname"] = self.getName()
		petDatas["modelNumber"] = self.modelNumber
		petDatas["gender"] = self.gender
		petDatas["species"] = self.getHierarchy()
		petDatas["level"] = self.level
		petDatas["ptype"] = self.getPType()
		petDatas["EXP"] = self.EXP
		petDatas["HPMax"] = self.HP_Max
		petDatas["MPMax"] = self.MP_Max
		petDatas["HP"] = self.HP
		petDatas["MP"] = self.MP
		petDatas["strength"] = self.strength
		petDatas["intellect"] = self.intellect
		petDatas["dexterity"] = self.dexterity
		petDatas["corporeity"] = self.corporeity
		petDatas["ec_corporeity"] = self.ec_corporeity
		petDatas["ec_strength"] = self.ec_strength
		petDatas["ec_intellect"] = self.ec_intellect
		petDatas["ec_dexterity"] = self.ec_dexterity
		petDatas["ec_free"] = self.ec_free
		petDatas["ability"] = self.ability
		petDatas["nimbus"] = self.nimbus
		petDatas["calcaneus"] = self.calcaneus
		petDatas["character"] = self.character
		petDatas["procreated"] = self.procreated
		petDatas["life"] = self.life
		petDatas["joyancy"] = self.joyancy
		petDatas["attrSkillBox"] = self.attrSkillBox
		petDatas["takeLevel"] = self.takeLevel
		petDatas["damage_min"] = self.damage_min
		petDatas["damage_max"] = self.damage_max
		petDatas["armor"] = self.armor
		petDatas["dodge_probability"] = self.dodge_probability
		petDatas["double_hit_probability"] = self.double_hit_probability
		petDatas["resist_hit_probability"] = self.resist_hit_probability
		petDatas["magic_damage"] = self.magic_damage
		petDatas["magic_armor"] = self.magic_armor
		petDatas["dodge_probability"] = self.dodge_probability
		petDatas["magic_double_hit_probability"] = self.magic_double_hit_probability
		petDatas["resist_giddy_probability"] = self.resist_giddy_probability
		petDatas["resist_fix_probability"] = self.resist_fix_probability
		petDatas["resist_chenmo_probability"] = self.resist_chenmo_probability
		petDatas["resist_sleep_probability"] = self.resist_sleep_probability
		observer.clientEntity( self.id ).onRecievePetData( petDatas )


	# ----------------------------------------------------------------
	# 骑宠技能对宠物的影响
	# ----------------------------------------------------------------
	def onVehicleAddSkills( self, skillIDList, vehicleJoyancyEffect ):
		"""
		Define Method
		远程技能生效
		"""
		self.setTemp( "vehicleJoyancyEffect", vehicleJoyancyEffect )
		for skillID in skillIDList:
			if not g_skills.has( skillID ):
				WARNING_MSG( "Skills(%i) does not exist!" % skillID )
				continue
			skill = g_skills[skillID]
			skill.attach( self )

		self.__calcSndAttrsBase()

	def onVehicleRemoveSkills( self, skillIDList, vehicleJoyancyEffect ):
		"""
		Define Method
		远程技能卸载
		"""
		self.setTemp( "vehicleJoyancyEffect", vehicleJoyancyEffect )
		for skillID in skillIDList:
			if not g_skills.has( skillID ):
				WARNING_MSG( "Skills(%i) does not exist!" % skillID )
				continue
			skill = g_skills[skillID]
			skill.detach( self )

		self.__calcSndAttrsBase()

	# ----------------------------------------------------------------
	# 骑宠装备对宠物的影响（神经病）
	# ----------------------------------------------------------------
	def onVehicleAddEquips( self, equipIDList ):
		"""
		defined Method
		骑宠添加装备时被触发（神经病）
		@type			equipIDList : ARRAY of ITEM_ID
		@param			equipIDList : 添加的装备 ID 列表
		"""
		for itemID in equipIDList :
			if itemID == 0 : continue
			item = items.instance().createDynamicItem( itemID )
			if item is None : continue
			extraEffect = item.query( "eq_extraEffect", {} )
			for key, value in extraEffect.iteritems() :
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None : continue
				effectClass.attach( self, value, item )

	def onVehicleRemoveEquips( self, equipIDList ) :
		"""
		defined Method
		骑宠删除装备时被触发（神经病）
		@type			equipIDList : ARRAY of ITEM_ID
		@param			equipIDList : 删除的装备 ID 列表
		"""
		for itemID in equipIDList :
			if itemID == 0 : continue
			item = items.instance().createDynamicItem( itemID )
			if item is None : continue
			extraEffect = item.query( "eq_extraEffect", {} )
			for key, value in extraEffect.iteritems() :
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None : continue
				effectClass.detach( self, value, item )

	def calcPropertiesByVehicle( self ) :
		"""
		defined methid
		因为骑宠装备的更新，重新计算宠物属性
		"""
		self.__calcSndAttrsBase()

	def isDead( self ):
		"""
		virtual method.

		@return: BOOL，返回自己是否已经死亡的判断
		@rtype:  BOOL
		"""
		return self.state == csdefine.ENTITY_STATE_DEAD

	def getLevel( self ):
		"""
		级别
		"""
		return self.level

	def beforePostureChange( self, newPosture ):
		"""
		姿态改变之前

		@param newPosture : 改变后的姿态
		"""
		SkillBox.beforePostureChange( self, newPosture )

	def afterPostureChange( self, oldPosture ):
		"""
		姿态改变后

		@param oldPosture : 改变前的姿态
		"""
		SkillBox.afterPostureChange( self, oldPosture )
		
	def getRelationEntity( self ):
		"""
		获取关系判定的真实entity
		"""
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return None
		else:
			return owner.entity
			
	def queryCombatRelation( self, entity ):
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return csdefine.RELATION_NONE
		else:
			return owner.entity.queryCombatRelation( entity )
		