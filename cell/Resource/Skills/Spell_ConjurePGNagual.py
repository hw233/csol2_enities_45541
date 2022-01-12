# -*- coding: gb18030 -*-

# common and global
import BigWorld
import random
import Math
from bwdebug import *
import csconst
import csdefine
# cell
import Const
from SpellBase import Spell

# config
import csstatus

class Spell_Conjure( Spell ):
	"""
	玩家召唤盘古守护技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.className = ""				# 盘古守护className
		self.attackType = 1				# 攻击类型

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.className = dict[ "param1" ] if dict["param1"] else ""
		self.attackType = int( dict["param3"] ) if dict["param3"] else 1 

	def receive( self, caster, receiver ):
		"""
		virtual method = 0
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		pos = Math.Vector3( receiver.position )
		dir = receiver.direction
		dic = [ -5, -4, -3, 3, 4, 5 ]
		randomVal = dic[ random.randint( 0, 5 ) ]
		
		pos.x = receiver.position.x + randomVal
		pos.z = receiver.position.z + randomVal
		
		# 召唤怪物的时候对地面进行碰撞检测避免怪物陷入地下
		collide = BigWorld.collide( receiver.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y
				
		dict ={}
		dict[ "spawnPos" ] = tuple( pos )
		dict["attackType"] = self.attackType
		dict["level"] = self.getLevel()

		newEntity = receiver.createObjectNearPlanes( self.className, pos, dir, dict )
		newEntity.setOwner( caster.base )

class Spell_ConjurePGNagual( Spell_Conjure ):
	"""
	玩家召唤盘古守护技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Conjure.__init__( self )
		self.reqAccum = 0				# 消耗气运

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Conjure.init( self, dict )
		self.reqAccum = int( dict["param2"] ) if dict["param2"] else 0 

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
		targetEntity = target.getObject()
		if not targetEntity:
			ERROR_MSG( "Can't find target entity!" )
			return
			
		spaceScript = targetEntity.getCurrentSpaceScript()
		if not spaceScript.canGetAccum:														# 指定地图
			return csstatus.SKILL_SPELL_NOT_SPECIAL_SPACE
			
		callPGDict = caster.queryTemp( "callPGDict", {} )
		npcIDs = []
		for id in callPGDict.values():
			npcIDs.extend( id )
		if len( npcIDs ) >= caster.queryTemp( "ROLE_CALL_PGNAGUAL_LIMIT", csconst.ROLE_CALL_PGNAGUAL_LIMIT ):	# 可召唤数量判断
			return csstatus.SKILL_SPELL_CALL_PGNAGUAL_ENOUGH
		
		if caster.getAccum() < self.reqAccum:												# 气运值判断
			return csstatus.SKILL_SPELL_NOT_ENOUGH_ACCUM 
		
		return Spell_Conjure.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		Spell_Conjure.receive( self, caster, receiver )
		caster.addAccumPoint( - self.reqAccum )