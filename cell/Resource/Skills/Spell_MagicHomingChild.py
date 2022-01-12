# -*- coding:gb18030 -*-

from Spell_MagicImprove import Spell_MagicImprove
import csconst
import random
import csstatus
import Math
import math
import csarithmetic
import csdefine
import ECBExtend
from Function import newUID
from bwdebug import *
BE_HOMING_MAX_SPEED = 50.0

class Spell_MagicHomingChild( Spell_MagicImprove ):
	"""
	法术连击子技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_MagicImprove.__init__( self )

		# 施法者位移数据
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		self.casterMoveFace = False

		# 受术者位移数据
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0
		self.targetMoveFace = False
		
		#额外伤害配置
		self.extraTBuff = None #目标存在相关buff产生额外伤害
		self.extraSBuff = None #本身存在相关buff产生额外伤害
		self.extraSHP   = None #本身血量少于百分比产生额外伤害
		self.critSBuff  = [] #本身存在相关buff产生暴击伤害

	def init( self, data ):
		"""
		"""
		Spell_MagicImprove.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) >= 3:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
			self.casterMoveFace = bool( int( param2[2] ) )
		param3 = data["param3"].split(";")
		if len( param3 ) >= 3:
			self.targetMoveSpeed = float( param3[0] )
			self.targetMoveDistance = float( param3[1] )
			self.targetMoveFace = bool( int( param3[2] ) )
		if data["param5"] != "":
			params = data["param5"].split("|")
			for param5 in params:
				infos = param5.split(";")
				extra_type = int(infos[0])
				if extra_type == 1:
					self.extraTBuff = ( [ int( i ) for i in infos[1].split(",") ], int( infos[2] ) )
				elif extra_type == 2:
					self.extraSBuff = ( [ int( i ) for i in infos[1].split(",") ], int( infos[2] ) )
				elif extra_type == 3:
					self.extraSHP = ( float( infos[1] ), int( infos[2] ) )
				elif extra_type == 4:	
					self.critSBuff =  [ int( i ) for i in infos[1].split(",") ]
	
	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		# 施法者位移
		if self.casterMoveDistance and self.casterMoveSpeed:
			targetObject = target.getObject()
			direction = Math.Vector3( targetObject.position ) - Math.Vector3( caster.position )
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster.__class__.__name__ != "Role":
				caster.moveToPosFC( endDstPos, self.casterMoveSpeed, self.casterMoveFace )
			else:
				caster.move_speed = self.casterMoveSpeed
				caster.updateTopSpeed()
				timeData = ( endDstPos - caster.position ).length/self.casterMoveSpeed
				caster.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )

		Spell_MagicImprove.cast( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		if caster.isReal():
			Spell_MagicImprove.receive( self, caster, receiver )

		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 受术者位移
		#如果当前目标处于霸体状态，将不会差生位移
		if receiver.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX  ) > 0:
			return

		#如果是最先连击你的那个人，那么可以移动否则不移动
		targetID = receiver.queryTemp( "HOMING_TARGET", 0 )
		if targetID != 0 and targetID != caster.id:
			return

		if self.targetMoveDistance and self.targetMoveSpeed:
			direction = caster.queryTemp( "HOMING_DIRECT", None )
			if not direction:
				yaw = caster.yaw
				direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			sourcePos = caster.position
			dstPos = receiver.position + direction * self.targetMoveDistance
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, sourcePos, dstPos )
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+5.0,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-5.0,endDstPos[2]) )
			if receiver.__class__.__name__ != "Role" :
				receiver.moveToPosFC( endDstPos, self.targetMoveSpeed, self.targetMoveFace )
			else:
				perID = receiver.queryTemp( "HOMING_TIMMER", 0 )
				if perID:
					receiver.cancel( perID )

	def calcHitProbability( self, source, target ):
		"""
		计算命中率，策划要求连击子技能命中率100%
		"""
		return 1.0
	
	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		判断攻击者是否爆击
		return type:bool
		"""
		if self.critSBuff :
			for index, buff in enumerate( caster.attrBuffs ):
				spell = buff["skill"]
				if spell.getBuffID() in self.critSBuff:
					return  True
		return random.random() < ( caster.magic_double_hit_probability + ( receiver.be_magic_double_hit_probability - receiver.be_magic_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )	
	
	def calcSkillHitStrength( self, source, receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		方式1：技能攻击力（总公式中的基础值）=技能本身的攻击力+角色的物理攻击力
		带入总公式中就是：（技能本身的攻击力+角色物理攻击力）*（1+物理攻击力加成）+物理攻击力加值
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		base = random.randint( self._effect_min, self._effect_max )
		extra = self.calcTwoSecondRule( source, source.magic_damage * (1+self.magicPercent) )
		
		#计算目标身上buff额外伤害
		if self.extraTBuff and not receiver.isDestroyed :
			for index, buff in enumerate( receiver.attrBuffs ):
				spell = buff["skill"]
				if spell.getBuffID() in self.extraTBuff[0]:
					base += self.extraTBuff[1]
		#计算施法者身上buff额外伤害
		if self.extraSBuff:
			for index, buff in enumerate( source.attrBuffs ):
				spell = buff["skill"]
				if spell.getBuffID() in self.extraSBuff[0]:
					base += self.extraSBuff[1]
		#计算施法者血量低于百分比额外伤害
		if self.extraSHP:
			if float(source.HP)/source.HP_Max <= self.extraSHP[0]:
				base += self.extraSHP[1]
		#计算施法者隐身额外伤害
		extra_snake = source.queryTemp( "SNAKE_EXTRA", 0 )
		base += extra_snake
		
		skilldamage = self.calcProperty( base, extra * self._shareValPercent, dynPercent + source.magic_skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.magic_skill_extra_value / csconst.FLOAT_ZIP_PERCENT )
		return skilldamage
	

class Spell_FixTargetMagicHomingChild( Spell_MagicHomingChild ):
	"""
	固定目标法术连击子技能
	"""

	def __init__( self ):
		"""
		"""
		Spell_MagicHomingChild.__init__( self )
		self._receivers = []

	def onUse( self, caster, target, receivers ) :
		"""
		"""
		self._receivers = receivers
		data = self.addToDict()
		nSkill = self.createFromDict( data )
		nSkill.cast( caster, target )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		print self, self._receivers
		return self._receivers

	def valid( self, target ):
		"""
		检测目标是否已死亡
		"""
		spellTarget = target.getObject()
		try:
			if spellTarget.state == csdefine.ENTITY_STATE_DEAD:
				return csstatus.SKILL_CHANGE_TARGET
			return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# 只输出错误，但仍然有效，得到要求不符合的结果
			# 原因在于像掉落物品这一类的entity是不会有（最起码现在没有）isDead()方法的
			INFO_MSG( errstr )
		return csstatus.SKILL_CHANGE_TARGET

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : { "receivers" : self._receivers } }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )

		obj._receivers = data["param"]["receivers"]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
