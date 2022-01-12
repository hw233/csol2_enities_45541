# -*- coding:gb18030 -*-

from SpellBase.Spell import Spell
from Spell_HomingChild import Spell_HomingChild,Spell_TargetChangeHomingChild,Spell_HomingChild_Distance
import csconst
import csdefine
import random
import Math
import csstatus
from Function import newUID
import SkillTargetObjImpl
from bwdebug import *

class Spell_FirstHomingChild( Spell_HomingChild ):
	"""
	物理连击第一个子技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_HomingChild.__init__( self )

	def onMiss( self, damageType, caster, receiver ):
		"""
		技能未命中
		"""
		Spell_HomingChild.onMiss( self, damageType, caster, receiver )

class Spell_FixTargetFirstHomingChild( Spell_FirstHomingChild ):
	"""
	固定目标物理连击第一个子技能
	"""

	def __init__( self ):
		"""
		"""
		Spell_FirstHomingChild.__init__( self )
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

class Spell_FirstTargetChangeHomingChild( Spell_TargetChangeHomingChild ):
	"""
	连击第一个子技能-目标是自己
	"""
	def __init__( self ):
		"""
		"""
		Spell_TargetChangeHomingChild.__init__( self )

	def onMiss( self, damageType, caster, receiver ):
		"""
		技能未命中
		"""
		# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
		receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
		caster.doAttackerOnDodge( receiver, damageType )
		receiver.doVictimOnDodge( caster, damageType )


class Spell_FirstHomingChild2( Spell ):
	"""
	快速移动到指定位置
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# 施法者位移数据
		self.moveTime = 0.0

	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		self.moveTime = float( data["param2"] )

	def cast( self, caster, target ) :
		Spell.cast( self, caster, target )
		dist = caster.position.distTo( target.getObjectPosition() )
		moveSpeed = dist / self.moveTime
		caster.moveToPosFC( Math.Vector3( target.getObjectPosition() ), moveSpeed, True )

class Spell_FirstHomingChild3( Spell ):
	"""
	直接位移到某位置
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# 施法者位移数据
		self.maxDist = 0.0

	def init( self, data ):
		"""
		"""
		Spell.init( self, data )

	def cast( self, caster, target ) :
		Spell.cast( self, caster, target )
		caster.position = target.getObjectPosition()

class Spell_FirstHomingChild4( Spell_HomingChild_Distance ):
	"""
	怪物冲到玩家的位置
	"""
	def __init__( self ):
		"""
		"""
		Spell_HomingChild_Distance.__init__( self )

	def onMiss( self, damageType, caster, receiver ):
		"""
		技能未命中
		"""
		Spell_HomingChild_Distance.onMiss( self, damageType, caster, receiver )
