# -*- coding: gb18030 -*-

# 辅助技能基础类
from bwdebug import *
from Spell import Spell
from Function import newUID
import csstatus
import csdefine
import time
import BigWorld
import Math
import random
import SkillTargetObjImpl
import math
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()


##连击次数达到一定值触发霸体
BATI_COUNT        = 10000
BATI_SKILL        = 122689001

BATI_CANCEL_TIME  = 2.0

#连击技能中断触发CD
INTERRUPT_CDS = { 1:1, 199:1 }

# 为偏度，可调节参数，取值与n有关
N_OFFSET = { 10:4.8, 9:4.8, 8:4.75, 7:4.75, 6:4.66, 5:4.66, 4:4 }
	
# --------------------------------------------------------------------
# 引导技能基础类
#    这个技能在吟唱过程中会有间隔的去释放另一个技能， 另一个技能可能是任何一个带有吟唱的技能
#	 但我们要求子技能的吟唱和冷却不生效
# --------------------------------------------------------------------
class HomingSpell( Spell ) :
	def __init__( self ) :
		Spell.__init__( self )
		self._childSpellIDs = []
		self._childSpellIDsCopy = []
		self._tickInterval = 0.0
		self._persistent = 0
		self._endTime = 0
		self._target = None
		self._actionMaxSpeed = 0.0
		self._extraSnake = 0

	def init( self, dictData ):
		"""
		读取技能配置
		@param dictData:	配置数据
		@type dictData:	python dictData
		"""
		Spell.init( self, dictData )
		self._persistent = float( dictData["param1"] )

		self._childSpellIDs = [int( k ) for k in dictData["param2"].split(",")]
		self._childSpellIDs.reverse()
		self._childSpellIDsCopy = list( self._childSpellIDs )
		if dictData["param4"] != "":
			param4 = dictData["param4"].split(";")
			if len( param4 ) > 0 :
				self._actionMaxSpeed = float( param4[0] )
			if len( param4 ) > 1 :
				self._extraSnake = int( param4[1] )
		self.initHomingSpellSelf( dictData )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP

		if self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		return Spell.useableCheck( self, caster, target )
	
	def initHomingSpellSelf( self, dictData ):
		"""
		初始化自身特有配置
		"""
		self._tickInterval = float( dictData[ "param3" ] )

	# ----------------------------------------------------------------
	# virtual methods
	# ----------------------------------------------------------------
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.onArrive( self, caster, target )
		self._target = target
		if self._persistent > 0:
			self._endTime = time.time() + self._persistent

		data = self.addToDict()
		nSkill = self.createFromDict( data )
		caster.addHomingSpell( nSkill )

	def onTick( self, caster ):
		"""
		virtual method.
		辅助技能的间隔响应tick
		@return type: 返回false则将提前结束这个技能
		"""
		spell = Spell.skillLoader[ self.getChildSpellID() ]
		if spell is None: return csstatus.SKILL_NOT_EXIST

		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_FIX > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_FIX

		if spell.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif spell.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		# 施法距离等条件
		state = spell.castValidityCheck( caster, self._target  )
		if state != csstatus.SKILL_GO_ON: return state

		# 检查施法者的消耗是否足够
		state = spell.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON: return state

		# 检查目标是否符合法术施展
		state = spell._castObject.valid( caster, self._target )
		if state != csstatus.SKILL_GO_ON: return state
		
		#加入转向
		caster.rotateToSpellTarget( self._target )	
		spell.cast( caster, self._target )
		return csstatus.SKILL_GO_ON

	def isTimeout( self ):
		"""
		0无持续时间，永不过期
		"""
		if self._endTime == 0:
			return False
		return time.time() >= self._endTime

	def getPersistent( self ):
		"""
		返回这个技能的作用的总时间
		"""
		return self._persistent

	def getEndTime( self ):
		"""
		virtual method.
		返回这个技能的作用的结束时间
		"""
		return self._endTime

	def getChildSpellIDs( self ):
		"""
		返回这个技能的所有子技能ID
		"""
		return self._childSpellIDs

	def getChildSpellID( self ):
		"""
		获取一个子技能ID
		"""
		if len( self._childSpellIDsCopy ) == 0:
			self._childSpellIDsCopy = list( self._childSpellIDs )

		return self._childSpellIDsCopy.pop()

	def getTickInterval( self ):
		"""
		virtual method.
		返回这个技能的触发间隔时间
		"""
		return self._tickInterval

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : { "endTime" : self._endTime, "target" : self._target, "childSpellIDs": list( self._childSpellIDs ) } }

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

		obj._endTime = data["param"][ "endTime" ]
		obj._target = data["param"][ "target" ]
		obj._childSpellIDsCopy = list( data["param"][ "childSpellIDs" ] )

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

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
		pass

	def onInterrupted( self, caster, reason ):
		"""
		引导技能被打断回调
		"""
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			notCDResons = [ csstatus.SKILL_INTERRUPTED_BY_SPELL_2, csstatus.SKILL_INTERRUPTED_BY_TIME_OVER, csstatus.SKILL_NO_MSG, csstatus.SKILL_CANT_CAST, csstatus.SKILL_NOT_READY ]
			if reason not in notCDResons: 
				#被打断触发CD
				for cd, time in INTERRUPT_CDS.items():
					try:
						endTime = g_cooldowns[ cd ].calculateTime( time )
					except:
						EXCEHOOK_MSG("skillID:%d" % self.getID())
					if caster.getCooldown( cd ) < endTime:
						caster.changeCooldown( cd, time, time, endTime )
		caster.updateTopSpeed( )
		caster.removeTemp( "SNAKE_EXTRA" )
		caster.removeTemp( "HOMING_DIRECT" )
		
	def canInterruptSpell( self, reason ):
		"""
		可否被该原因打断
		"""
		return reason != csstatus.SKILL_INTERRUPTED_BY_AI
	
	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		计算命中率
		命中率=(攻击方道行/受击方道行)^2+攻击方混乱穿透-受击方混乱抗性
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		return type:	Float
		"""
		hitRate = pow( source.daoheng / target.daoheng, 2 ) + source.chaos_penetrate - target.chaos_resist
		return hitRate
		
	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		Spell.cast( self, caster, target )
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self._actionMaxSpeed > 0.0: #为了防止玩家在播放动作时被拉回
				caster.setTemp( "TOP_SPEED", caster.topSpeed )
				caster.setTopSpeed( self._actionMaxSpeed )
		if caster.effect_state & csdefine.EFFECT_STATE_PROWL:	 #潜行装备额外伤害
			caster.setTemp("SNAKE_EXTRA", self._extraSnake )
		#记录当前施法者朝向 受击朝向需要用到
		direction = caster.queryTemp( "HOMING_DIRECT", None )
		if not direction:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			caster.setTemp( "HOMING_DIRECT", direction )

# --------------------------------------------------------------------
# 引导技能派生类
#   这个技能在吟唱过程中会有间隔的（这个时间间隔由策划定义的）去释放另一个技能，
#	另一个技能可能是任何一个带有吟唱的技能
#	但我们要求子技能的吟唱和冷却不生效
# --------------------------------------------------------------------
class ActiveHomingSpell( HomingSpell ):
	"""
	"""
	def __init__( self ):
		HomingSpell.__init__( self )
		self._tickInterval = []
		self._tickIntervalCopy = []
		self._receiverBuffs = []  #buff接受者
		self._comboData = []
		self._daoheng = True
		self._interruptRateList = []

	def initHomingSpellSelf( self, dictData ):
		"""
		初始化
		"""
		self._tickInterval = [float( k ) for k in dictData["param3"].split(",")]
		if dictData["param5"] != "":
			self._comboData = dictData["param5"].split(";")
			self._daoheng = bool( int( self._comboData[0] ) )
			if self._comboData[1] != "":
				self._interruptRateList = [float( k ) for k in self._comboData[1].split(",")]
		self._tickInterval.reverse()
		self._tickIntervalCopy = list( self._tickInterval )

	def getTickInterval( self ):
		"""
		返回这个技能的触发间隔时间
		"""
		if len( self._tickIntervalCopy ) == 0 :
			self._tickIntervalCopy = list( self._tickInterval )

		return self._tickIntervalCopy.pop()

	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		self._receiverBuffs = [] 
		HomingSpell.cast( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return
		self.receiveLinkBuff( caster, receiver )
		self._receiverBuffs.append( receiver.id )
	
	def onInterrupted( self, caster, reason ):
		"""
		引导技能被打断回调
		"""
		HomingSpell.onInterrupted( self, caster, reason )
		if reason == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER:
			self._receiverBuffs = []
			return 
		for entityID in self._receiverBuffs:
			entity = BigWorld.entities.get( entityID, None )
			if entity and not entity.isDestroyed:
				buffIndexList = []
				for buffData in self._buffLink:
					buffs = entity.findBuffsByBuffID( buffData.getBuff()._buffID )
					if len(buffs)>0:
						for buffIndex in buffs:			#从后往前删
							buff = entity.getBuff( buffIndex )
							if buff["caster"] == caster.id :
								buffIndexList.append( buff["index"] )
								#entity.removeBuffByID( buffData.getBuff()._id,  [csdefine.BUFF_INTERRUPT_NONE] )
								break
				for buffIndex in buffIndexList:
					entity.removeBuffByIndex( buffIndex, [ csdefine.BUFF_INTERRUPT_NONE ] )
		self._receiverBuffs = []
		
	def onTick( self, caster ):
		"""
		virtual method.
		辅助技能的间隔响应tick
		@return type: 返回false则将提前结束这个技能
		"""
		if self.onTickDo( caster ) == csstatus.SKILL_GO_ON:
			return csstatus.SKILL_GO_ON
		spell = Spell.skillLoader[ self.getChildSpellID() ]
		if spell is None: return csstatus.SKILL_NOT_EXIST

		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_FIX > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_FIX

		if spell.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif spell.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		# 施法距离等条件
		state = spell.castValidityCheck( caster, self._target  )
		if state != csstatus.SKILL_GO_ON: return state

		# 检查施法者的消耗是否足够
		state = spell.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON: return state

		# 检查目标是否符合法术施展
		state = spell._castObject.valid( caster, self._target )
		if state != csstatus.SKILL_GO_ON: return state
		
		#加入转向
		caster.rotateToSpellTarget( self._target )	
		spell.cast( caster, self._target )
		
		if self.onTickDo( caster ) == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER:
			return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
		return csstatus.SKILL_GO_ON

	def onTickDo( self, caster ):
		if len( self._tickIntervalCopy ) == 0 and self._persistent <= 0:
			if self._persistent == -1.0:
				return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
			caster.planesAllClients( "castSpell", ( self.getID(), self._target ) )
			return csstatus.SKILL_GO_ON
		return None

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : {	"endTime" : self._endTime,
								"tickInterval" : self._tickInterval,
								"target" : self._target,
								"childSpellIDs" : list( self._childSpellIDs ),
								"receiverBuffs" : list( self._receiverBuffs ), }}


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

		obj._endTime = data["param"][ "endTime" ]
		obj._tickIntervalCopy = list( data["param"][ "tickInterval" ] )
		obj._target = data["param"][ "target" ]
		obj._childSpellIDsCopy = list( data["param"][ "childSpellIDs" ] )
		obj._receiverBuffs = list( data["param"][ "receiverBuffs" ] )

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj


# --------------------------------------------------------------------
# 引导技能派生类
#   这个引导技能在释放过程中维持着一个对目标的BUFF，当这个引导技能还在
#	释放的时候，BUFF会一直存在，当引导技能结束，则BUFF也结束。 当前只对单体作用对象有效
# --------------------------------------------------------------------
class HomingSpellBuff( ActiveHomingSpell ):
	"""
	"""

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		ActiveHomingSpell.receive( self, caster, receiver )
		caster.setTemp( "HomingSpellReceiverID", receiver.id )
		self.receiveLinkBuff( caster, receiver )


	def onInterrupted( self, caster, reason ):
		"""
		引导技能被打断回调
		"""
		ActiveHomingSpell.onInterrupted( self, caster, reason )
		if self._target.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY:
			entity = self._target.getObject()
			if entity is not None:
				buffIndexList = []
				for buffData in self._buffLink:
					buffs = entity.findBuffsByBuffID( buffData.getBuff()._buffID )
					if len(buffs)>0:
						for buffIndex in buffs:			#从后往前删
							buff = entity.getBuff( buffIndex )
							if buff["caster"] == caster.id :
								buffIndexList.append( buff["index"] )
								#entity.removeBuffByID( buffData.getBuff()._id,  [csdefine.BUFF_INTERRUPT_NONE] )
								break
				for buffIndex in buffIndexList:
					entity.removeBuffByIndex( buffIndex,  [csdefine.BUFF_INTERRUPT_NONE] )


	def onTick( self, caster ):
		"""
		virtual method.
		辅助技能的间隔响应tick
		@return type: 返回false则将提前结束这个技能
		"""
		if BigWorld.entities.get( caster.queryTemp( "HomingSpellReceiverID", 0 ) ) is None:
			return csstatus.SKILL_TARGET_NOT_EXIST
		return ActiveHomingSpell.onTick( self, caster )

	def onTickDo( self, caster ):
		if len( self._tickIntervalCopy ) == 0 and self._persistent <= 0:
			if self._persistent == -1.0:
				return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
			caster.planesAllClients( "castSpell", ( self.getID(), self._target ) )
			return csstatus.SKILL_GO_ON
		return None


# --------------------------------------------------------------------
# 引导技能派生类
#   这个类将会打包母技能的生效目标给予子技能
# --------------------------------------------------------------------
class FixTargetActiveHomingSpell( ActiveHomingSpell ):
	"""
	"""
	def __init__( self ):
		ActiveHomingSpell.__init__( self )
		self._receivers = []
		self._comboInter = [] #连击抵抗索引 目标
		
	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		HomingSpell.cast( self, caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 获取所有受术者
		Spell.onArrive( self, caster, target )
		self._receivers = self.getReceivers( caster, target )
		
		self._target = target
		if self._persistent > 0:
			self._endTime = time.time() + self._persistent

		data = self.addToDict()
		nSkill = self.createFromDict( data )
		caster.addHomingSpell( nSkill )
		

	def onTick( self, caster ):
		"""
		virtual method.
		辅助技能的间隔响应tick
		@return type: 返回false则将提前结束这个技能
		"""
		if self.onTickDo( caster ) == csstatus.SKILL_GO_ON:
			return csstatus.SKILL_GO_ON

		spell = Spell.skillLoader[ self.getChildSpellID() ]
		if spell is None: return csstatus.SKILL_NOT_EXIST


		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_FIX > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_FIX

		if spell.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif spell.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		# 施法距离等条件
		state = spell.castValidityCheck( caster, self._target  )
		if state != csstatus.SKILL_GO_ON: return state

		# 检查施法者的消耗是否足够
		state = spell.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON: return state

		# 检查目标是否已死亡
		if hasattr( spell, "valid" ):
			state = spell.valid( self._target )
		if state == csstatus.SKILL_CHANGE_TARGET:
			self._target = self.__chooseTarget( spell, caster )

		# 检查目标是否符合法术施展
		state = spell._castObject.valid( caster, self._target )
		if state != csstatus.SKILL_GO_ON: return state
		
		#FixTarget连击技能在每个子技能释放成功的时候需要重新检查receivers（死亡检查）
		for enti in self._receivers[:]:
			if enti.isDestroyed:
				self._receivers.remove( enti )
		#加入抵抗判断
		skillL = self.getChildSpellIDs()
		n = len( skillL ) 
		k = n - len( self._childSpellIDsCopy )
		if k == 1:
			self._comboInter=[]
			for receiver in self._receivers:
				en = receiver
				if en.isDestroyed: continue
				if self._daoheng:
					da = float(caster.daoheng)
					dd = float(en.daoheng)
					if n in N_OFFSET.keys():
						offset = 1 - N_OFFSET[n]/5.0
					else:
						offset = 1 - 4/5.0
					
					if  da + dd != 0:
						p = ( da / ( da + dd ) ) ** offset
					else:
						p = 0
					nJ = reduce(lambda x,y: x*y, range(1,n+1))
					glL = []
					for i in range( 0, n+1 ):
						if i > 0:
							iJ = reduce(lambda x,y: x*y, range(1,i+1))
						else:
							iJ = 1
						if n-i > 0:
							niJ = reduce(lambda x,y: x*y, range(1,n-i+1))
						else:
							niJ = 1
						pnk = (nJ/(iJ*niJ))*(p**i)*((1-p)**(n-i))
						glL.append( pnk )
					#算到哪一个子技能中断
					interR = random.random()
					ls = 0
					for idx in range(len(glL)):
						v2 = ls 
						ls += glL[idx]
						if v2 <= interR < ls:
							self._comboInter.append(( idx + 1 + 1, en ))
							break
				else:
					#不通过道行计算哪个子技能中断，通过读技能配置实现子技能中断
					self.__unDaohengRate( en )
		self._comboInter.sort() #排序
		for co in self._comboInter:
			if k == co[0]:
				en = co[1]
				if en and not en.isDestroyed:
					if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						caster.homingSpellResist( en.id )
					if en.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						en.homingSpellResist( en.id )
				if en in self._receivers:
					self._receivers.remove( en )
				#移除身上的控制buff
				for entityID in self._receiverBuffs:
					entity = BigWorld.entities.get( entityID, None )
					if entityID != en.id: break
					if entity and not entity.isDestroyed:
						buffIndexList = []
						for buffData in self._buffLink:
							buffs = entity.findBuffsByBuffID( buffData.getBuff()._buffID )
							if len(buffs)>0:
								for buffIndex in buffs:			#从后往前删
									buff = entity.getBuff( buffIndex )
									if buff["caster"] == caster.id :
										buffIndexList.append( buff["index"] )
										#entity.removeBuffByID( buffData.getBuff()._id,  [csdefine.BUFF_INTERRUPT_NONE] )
										break
						for buffIndex in buffIndexList:
							entity.removeBuffByIndex( buffIndex,  [csdefine.BUFF_INTERRUPT_NONE] )
				if en.id == self._target.getObject().id:
					if len(self._receivers)>0:
						self._target = self.__chooseTarget( spell, caster )
					else:
						return csstatus.SKILL_MISS_TARGET
				self._comboInter.remove(co)
				break
		
		#判断是否使用了主动闪避
		if k != 1:
			avoidanceEntities = []
			for e in self._receivers:
				try :
					flag = e.popTemp( "AVOIDANCE_FLAG",False )
				except:
					flag = False
				if flag:
					avoidanceEntities.append(e)
			for e in avoidanceEntities:
				self._receivers.remove( e )
			if self._target.getObject() in avoidanceEntities :
				if len(self._receivers)>0:
					self._target = self.__chooseTarget( spell, caster )
				else:
					return csstatus.SKILL_MISS_TARGET

			loseEnemys = []
			for re in self._receivers:
				if re.isDestroyed: continue
				if not re.hasEnemy( caster.id ):	# 不在敌人列表则从受术者列表移除
					loseEnemys.append( re )
			for en in loseEnemys:
				self._receivers.remove( en )
			if self._target.getObject() in loseEnemys:
				if len( self._receivers ) > 0:
					self._target = self.__chooseTarget( spell, caster )
				else:
					return csstatus.SKILL_MISS_TARGET

		if hasattr( spell, "onUse" ):
			spell.onUse( caster, self._target, self._receivers )
		
		for receiver in self._receivers:
			en = receiver
			if en.isDestroyed:continue
			if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				#检测是否触发霸体
				bati = en.queryTemp( "HOMINGSPELL_BATI", None )
				if bati:
					if bati[1] < BATI_COUNT:
						if ( time.time() - bati[0] ) < BATI_CANCEL_TIME :
							newBati = ( time.time(), bati[1] + 1 )
						else:
							newBati = ( time.time(), 1 )
					else:
						en.spellTarget( BATI_SKILL, en.id )
						newBati = ( time.time(), 0 )
				else:
					newBati = ( time.time(), 1 )
				en.setTemp( "HOMINGSPELL_BATI", newBati )
		
		state = self.onTickDo( caster )
		if state == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER:
			return state
		#加入转向
		caster.rotateToSpellTarget( self._target )
		return csstatus.SKILL_GO_ON

	def __unDaohengRate( self, en ):
		"""
		不通过道行计算哪个子技能中断
		"""
		if self._interruptRateList == []: return
		rateList = self._interruptRateList
		if len( rateList ) != len( self.getChildSpellIDs() ):
			self._comboInter = []
			ERROR_MSG( "%s's childSpell interrupt rate config is wrong!" % self.getID() )
			return
		for index in range( len( rateList ) ):
			inter = random.random()
			if inter <= rateList[index]:
				self._comboInter.append( (index + 1,en) )
				break

	def __chooseTarget( self, spell, caster ):
		"""
		选择新的目标
		"""
		for receiver in self._receivers:
			target = SkillTargetObjImpl.createTargetObjEntity( receiver )
			state = spell._castObject.valid( caster, target )
			if state == csstatus.SKILL_GO_ON:
				return target
		return self._target

	def onTickDo( self, caster ):
		if len( self._tickIntervalCopy ) == 0 and self._persistent <= 0:
			if self._persistent == -1.0:
				return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
			caster.planesAllClients( "castSpell", ( self.getID(), self._target ) )
			return csstatus.SKILL_GO_ON
		return None

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : {	"endTime" : self._endTime,
								"tickInterval" : self._tickInterval,
								"target" : self._target,
								"receiver" : self._receivers,
								"childSpellIDs" : list( self._childSpellIDs ), }}


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

		obj._endTime = data["param"][ "endTime" ]
		obj._tickIntervalCopy = list( data["param"][ "tickInterval" ] )
		obj._target = data["param"][ "target" ]
		obj._receivers = data["param"][ "receiver" ]
		obj._childSpellIDsCopy = list( data["param"][ "childSpellIDs" ] )

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
	

class FTAHomingSpell_SelfBuff( FixTargetActiveHomingSpell ):
	"""
	buff2给自己加的连击母技能脚本
	"""
	def __init__( self ):
		FixTargetActiveHomingSpell.__init__( self )
		
	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID != 108007:
				buff.receive( caster, caster )
		FixTargetActiveHomingSpell.cast( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == 108007:
				buff.receive( caster, receiver )
		self._receiverBuffs.append( receiver.id )
		caster.setTemp( "HomingSpellReceiverID", receiver.id )
		
class FTAHomingSpell_TeamBuff( FixTargetActiveHomingSpell ):
	"""
	buff2给自己和队友加的连击母技能脚本
	"""
	def __init__( self ):
		FixTargetActiveHomingSpell.__init__( self )
		
	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID != 108007:
				elist = caster.getAllMemberInRange( 15.0 )
				if len( elist ) <= 0:
					elist = [ caster ]
				for e in elist:
					buff.receive( caster, e )
		FixTargetActiveHomingSpell.cast( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == 108007:
				buff.receive( caster, receiver )
		self._receiverBuffs.append( receiver.id )
		caster.setTemp( "HomingSpellReceiverID", receiver.id )