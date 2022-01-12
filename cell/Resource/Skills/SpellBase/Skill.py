# -*- coding: gb18030 -*-
#
# $Id: Skill.py,v 1.25 2008-02-29 09:26:00 kebiao Exp $

"""
攻击技能类。
"""
import csdefine
from bwdebug import *
import csstatus
import new
import random
import copy

from Function import newUID

class Skill:
	"""
	所有技能效果的基础类，所有的技能、法术、buff等效果加载的时候都应该存在于一个全局的基本列表中。
	我们认为，所有的技能效果都可使用，且使用过程是“施展（use）”->“接收（receive）”，因此基础类只有“施展”和“接收”的接口，以及检查“可施展情况（useableCheck）”的接口。
	另由于很多技能效果都可能会需要先附在entity身上，在特定的情况才会进行“施展”或“接收”，因此我们增加了attach()和detach()接口提供粘附功能。
	所有"Skill"类均由"Skill_"开头
	define SKILLID INT32
	"""
	# 全局数据集合; key is Skill::_id and value is instance of Skill or derive from it.
	skillLoader = None
	def __init__( self ):
		"""
		构造函数。
		"""
		self._id = 0										# 技能ID
		self._uid = 0										# 技能的uid
		self._name = ""										# 技能名称
		self._description = ""								# 技能描述
		
	@staticmethod
	def instance( id ):
		"""
		通过 skill id 获取skill实例
		"""
		return Skill.skillLoader[id]

	@staticmethod
	def setInstance( skillLoader ):
		"""
		设置全局的数据集合，此通过由skill loader调用

		@param datas: dict
		"""
		Skill.skillLoader = skillLoader

	@staticmethod
	def register( id, instance ):
		"""
		注册一个skill实例
		"""
		Skill.skillLoader.register( id, instance )
		
	def init( self, dictDat ):
		"""
		virtual method;
		读取技能配置
		@param dictDat: 配置数据
		@type  dictDat: python dict
		"""
		self._id = long( dictDat["ID"] )
		self._description = dictDat[ "Description" ]
		self._name = dictDat["Name"]
			
	def getID( self ):
		"""
		"""
		return self._id
	
	def getUID( self ):
		"""
		"""
		return self._uid
	
	def setUID( self, uid ):
		"""
		uid禁止被手动设置， 
		只是技能在打包传输的过程后，在另一个cell上应该
		恢复他的原先一直拥有的uid, 这个时候是允许被设置的
		"""
		self._uid = uid
		
	def getName( self ):
		"""
		virtual method;
		取得该技能的名称 实现由派生类实现
		"""
		return self._name
		
	def getDescription( self ):
		"""
		virtual method;
		取得该技能的描述 实现由派生类实现
		"""
		return self._description

	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		pass

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		pass

	def use( self, caster, target ):
		"""
		virtual method = 0.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity
		
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		pass

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_UNKNOW
		
	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。
		通常情况下此接口是由onArrive()调用，但它亦有可能由SpellUnit::receiveOnreal()方法调用，
		用于处理一些需要在受术者的real entity身上作的事情。但对于是否需要在real entity身上接收，
		由技能设计者在receive()中自行关断，并不提供相关机制。
		
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		pass

	def springOnDamage( self, caster, receiver, skill, damage ):
		"""
		virtual method.
		在伤害计算后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在受到伤害以后再触发的效果；

		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   skill: 技能实例
		@type    skill: Entity
		@param   damage: 施法者造成的伤害
		@type    damage: int32
		"""
		pass
	
	def springOnHit( self, caster, receiver, damageType ):
		"""
		技能命中时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   damageType: 伤害类别
		@type    damageType: uint32
		"""
		pass

	def springOnDodge( self, caster, receiver, damageType ):
		"""
		技能被闪避时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   damageType: 伤害类别
		@type    damageType: uint32
		"""
		pass
		
	def springOnDoubleHit( self, caster, receiver, damageType ):
		"""
		技能暴击时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   damageType: 伤害类别
		@type    damageType: uint32
		"""
		pass
		
	def springOnResistHit( self, caster, receiver, damageType ):
		"""
		技能被招架时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   damageType: 伤害类别
		@type    damageType: uint32
		"""
		pass
	
	def getNewObj( self ):
		"""
		virtual method.
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		obj.setUID( newUID() )
		return obj
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return {  "param" : None }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		return self

# Skill.py
