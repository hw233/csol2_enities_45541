# -*- coding: gb18030 -*-
#
# $Id: ReceiverObject.py,v 1.21 2008-09-05 01:43:14 zhangyuxing Exp $

"""
"""

from bwdebug import *
from csdefine import *		# only for "eval" expediently
import csdefine
import csstatus
import AreaDefine
import SkillTargetObjImpl
import items
import random
from Skill import Skill

RULE_OUT_TARGET = [ csdefine.ENTITY_TYPE_DROPPED_BOX, csdefine.ENTITY_TYPE_SPAWN_POINT ]

class ReceiverObjectBase:
	"""
	"""
	def __init__( self, parent ):
		self.parent = parent

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置dictDat
		"""
		pass

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		return csstatus.SKILL_GO_ON

	def validReceiver( self, caster, receiver ):
		"""
		判断目标是否有效
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		return csstatus.SKILL_GO_ON

	def getReceivers( self, caster, target ):
		"""
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 受击者
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		return []

	def convertCastObject( self, caster, target ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 受击者
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		return target

class ReceiverObjectEntity( ReceiverObjectBase ):
	"""
	作用对象是entity
	"""
	def __init__( self, parent ):
		ReceiverObjectBase.__init__( self, parent )
		# 所有条件都有 受术者最大个数， 最低级别，最高级别的支持.
		self._receiveCountMax = 1
		self._stateFunc = self.isLive
		self._area = AreaDefine.newInstance( csdefine.SKILL_SPELL_AREA_SINGLE, self.parent )	# see also AreaDefine; 默认为单体，可以不需要load()

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置dictDat
		"""
		if dictDat[ "Dead" ] == 1:
			self._stateFunc = self.isDead

		if dictDat.has_key( "Area" ):
			self._area = AreaDefine.newInstance( dictDat[ "Area" ], self.parent )								# 作用区域：单体(0)、圆(1)、直线(2)
			self._area.load( dictDat )
		try:
			self._receiveCountMax = dictDat[ "ReceiveCountMax" ]
		except:
			self._receiveCountMax  = 0

	def getReceiveObjCountMax( self ):
		"""
		virtual method.
		获取接受entity的最大个数
		"""
		return self._receiveCountMax

	def validEntityType( self, target ):
		"""
		virtual method.
		entity的类型是否合法
		"""
		return csstatus.SKILL_GO_ON

	@staticmethod
	def isLive( caster, receiver ):
		"""
		受术者是否活着
		"""
		try:
			if not receiver.state == csdefine.ENTITY_STATE_DEAD:
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# 只输出错误，但仍然有效，得到要求不符合的结果
			# 原因在于像掉落物品这一类的entity是不会有（最起码现在没有）isDead()方法的
			INFO_MSG( errstr )
		return csstatus.SKILL_TARGET_DEAD

	@staticmethod
	def isDead( caster, receiver ):
		"""
		受术者是否已经死亡
		"""
		try:
			if receiver.state == csdefine.ENTITY_STATE_DEAD:
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# 只输出错误，但仍然有效，得到要求不符合的结果
			# 原因在于像掉落物品这一类的entity是不会有（最起码现在没有）isDead()方法的
			INFO_MSG( errstr )
		return csstatus.SKILL_TARGET_NOT_DEAD

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY
		return csstatus.SKILL_GO_ON

	def validReceiver( self, caster, receiver ):
		"""
		判断目标是否有效
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if receiver.getEntityType() in RULE_OUT_TARGET:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		return self._validReceiver( caster, receiver )

	def filterReceiver( self, caster, receivers ):
		"""
		筛选出所有合法者
		@param   caster: 施法者
		@type    caster: Entity
		@param receivers: 受击者
		@type  receivers: list of Entity
		"""
		wrapReceivers = []

		for e in receivers:
			if self.validReceiver( caster, e ) == csstatus.SKILL_GO_ON:
				#将受术者包装
				wrapReceivers.append( e )
				if self._receiveCountMax > 0 and len( wrapReceivers ) >= self.getReceiveObjCountMax():
					break # 超出受术最大个数则不继续寻找
		return wrapReceivers

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 受击者
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py

		@rtype: list of Entity
		"""
		receivers = self._area.getObjectList( caster, target )
		return self.filterReceiver( caster, receivers )

	def convertCastObject( self, caster, target ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 受击者
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		return target

class ReceiverObjectInfection( ReceiverObjectEntity ):
	"""
	作用对象是施展对象，随机在扇形范围内攻击另一个对象
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )
		self._rate = 0  														#几率 施展对象，35%几率扇形范围内随机另一个可攻击对象
		self._extraInfectionCount = 0   										#此技能rate几率会额外感染指定范围内N个Entity  此属性一般应用于单体攻击技能

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat )
		#随机施展对象，35%几率扇形范围内随机另一个可攻击对象
		self._rate = dictDat["Area"]["rate"]  #float   #!!!notice：貌似这个类已经不用，skill.def 中key:"rate" 不存在
		self._extraInfectionCount = dictDat["Area"]["infectionCount"]  #Int
		self._randomArea = AreaDefine.newInstance( dictDat["Area"][ "Area" ], self.parent )				# 作用区域：单体(0)、圆(1)、直线(2)
		self._randomArea.load( dictDat["Area"] )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 受击者
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py

		@rtype: list of Entity
		"""

		#取施展对象，x%几率扇形范围内随机另N个可攻击对象
		receivers = self._area.getObjectList( caster, target )
		if random.random() <= self._rate:
			tmp = self.filterReceiver( caster, self._randomArea.getObjectList( caster, target ) )
			ocount = 0
			while ocount < self._extraInfectionCount and len( tmp ) > 0:
				index = random.randint( 0, len( tmp ) - 1 )
				e = tmp[ index ]
				tmp.pop( index )
				if e.id == target.getObject().id:
					continue
				ocount += 1
				receivers.append( e )
		return receivers

class ReceiverObjectSelf( ReceiverObjectEntity ):
	"""
	作用对象是自己(自身，自身圆形，自身扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat)

	def getReceiveObjCountMax( self ):
		"""
		virtual method.
		获取接受entity的最大个数
		"""
		return 1

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		if ( not caster.inHomingSpell() ) and caster.id != receiver.id:
			return csstatus.SKILL_NOT_SELF_ENTITY

		""" 对自己为目标的技能不应该有级别判断
		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		"""
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return caster

class ReceiverObjectTeam( ReceiverObjectEntity ):
	"""
	作用对象是队伍成员(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		判断该entity是否可以接受该法术
		@param caster:施法者
		@param receiver:受术者 要求和caster在一个队伍
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		if ( caster.utype == receiver.utype and \
			caster.isInTeam() and \
			receiver.isInTeam() and \
			receiver.spaceID == caster.spaceID and \
			caster.teamMailbox.id == receiver.teamMailbox.id ) or caster.id == receiver.id:

			#级别判断
			lvMin = self.parent.getCastTargetLevelMin()
			lvMax = self.parent.getCastTargetLevelMax()
			targetLv = receiver.getLevel()

			if lvMin > 0 and targetLv < lvMin :
				# 施展目标级别太低了
				skillID = self.parent.getID()
				fitSkillID = binarySearch( targetLv, skillID )
				if fitSkillID == -1:
					return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
			if lvMax > 0 and targetLv > lvMax :
				return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
			return csstatus.SKILL_GO_ON
		else:
			return csstatus.SKILL_NOT_TEAM_MEMBER

		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET


		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

class ReceiverObjectMonster( ReceiverObjectEntity ):
	"""
	作用对象是怪物(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		if receiver.utype != csdefine.ENTITY_TYPE_MONSTER or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_MONSTER_ENTITY

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""

		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		if tObject.utype != csdefine.ENTITY_TYPE_MONSTER:
			return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER
		return self._validReceiver( caster, tObject )

class ReceiverObjectRole( ReceiverObjectEntity ):
	"""
	作用对象是玩家(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY
		#对玩家使用的技能就可对宠物使用,也可对盘古守护使用
		if ( receiver.utype != csdefine.ENTITY_TYPE_ROLE and receiver.utype != csdefine.ENTITY_TYPE_PET and receiver.utype != csdefine.ENTITY_TYPE_PANGU_NAGUAL ):
			return csstatus.SKILL_NOT_ROLE_ENTITY

		if receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NO_RECEIVER

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

class ReceiverObjectRoleOnly( ReceiverObjectRole ):
	"""
	作用对象是玩家(单体，圆形，扇形...)的受术条件

	之前存在规则，所有对玩家有效的技能对宠物也有效。
	现在需要有仅对玩家有效的技能，由于ReceiverObjectRole已经被大量配置，如果修改可能会造成大量错误，
	因此添加此类来作为仅对玩家有效的受术者条件。
	"""
	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY
		if receiver.utype != csdefine.ENTITY_TYPE_ROLE:
			return csstatus.SKILL_NOT_ROLE_ENTITY

		if receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NO_RECEIVER

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

class ReceiverObjectRoleEnemyOnly( ReceiverObjectRoleOnly ):
	"""
	只对敌对玩家有效
	"""
	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if caster.queryRelation( receiver ) != csdefine.RELATION_ANTAGONIZE:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		return ReceiverObjectRoleOnly._validReceiver( self, caster, receiver )

class ReceiverObjectEnemy( ReceiverObjectEntity ):
	"""
	作用对象是可攻击敌人(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or ( not self.isEnemy( caster, receiver ) ) or receiver.spaceID != caster.spaceID :
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		是否敌人
		"""
		#ERROR_MSG( "--> Here must change.是敌是友不是这么判断的。" )
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		#return receiver.utype in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_ROLE ] and ( hasattr(receiver,"canFight") and receiver.canFight() )

class ReceiverObjectEnemyRandom( ReceiverObjectInfection ):
	"""
	对象是可攻击敌人随机攻击区域类其他可攻击对象(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectInfection.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectInfection.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or not self.isEnemy( caster, receiver ) or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		是否敌人
		"""
		#ERROR_MSG( "--> Here must change.是敌是友不是这么判断的。" )
		#print "isEnemy--->>>",caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		#return ( receiver.utype == csdefine.ENTITY_TYPE_MONSTER or receiver.utype == csdefine.ENTITY_TYPE_NPC ) and ( hasattr(receiver,"canFight") and receiver.canFight() )

class ReceiverObjectNotEnemyRole( ReceiverObjectEntity ):
	"""
	作用对象是非敌对的玩家(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition配置文件python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or ( not receiver.getObject().isEntityType( csdefine.ENTITY_TYPE_ROLE ) ) or \
			self.isEnemy( caster, receiver ) or receiver.spaceID != caster.spaceID :
			return csstatus.SKILL_TARGET_IS_ENEMY_ROLE

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		是否敌人
		"""
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE

class ReceiverObjectNotAttack( ReceiverObjectEntity ):
	"""
	作用对象是不可攻击entity(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or self.isEnemy( caster, receiver ) or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_IS_ENEMY_ENTITY

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX

		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		是否敌人
		"""
		#ERROR_MSG( "--> Here must change.是敌是友不是这么判断的。" )
		#print "isEnemy--->>>",caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		#return ( receiver.utype == csdefine.ENTITY_TYPE_MONSTER or receiver.utype == csdefine.ENTITY_TYPE_NPC ) and ( hasattr(receiver,"canFight") and receiver.canFight() )

class ReceiverObjectItem( ReceiverObjectBase ):
	"""
	作用对象是物品的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		pass

	def init( self, dictDat ):
		"""
		初始化能处理的物品类型
		"""
		self._itemTypes = set([])

		val = str( dictDat[ "value1" ] )
		for v in val.split(";"):
			d = eval( v )
			if type( d ) == list:
				self._itemTypes.update( set( d ) )
			else:
				self._itemTypes.add( d )

	def _validReceiver( self, caster, item ):
		"""
		判断该物品是否可以接受法术
		这里的receiver实际上是一个 Item 之所以这样命名是为了不破坏整体规则，其他所有的接受条件
		都是一个entity而物品不是一个entity，但在这里，这个物品就是最终的接收者
		@param caster:施法者
		@param receiver:最终接受法术的玩家背包中的物品实例
		"""
		# 不是一个物品
		if not isinstance( item, items.CItemBase.CItemBase ):
			return csstatus.SKILL_CANT_ITEM_ONLY
		# 不是玩家背包的物品
		if item.getUid() == -1:
			return csstatus.SKILL_ITEM_NOT_IN_BAG
		if item.getType() in self._itemTypes:
			return csstatus.SKILL_GO_ON
		# 不能对该物品使用
		return csstatus.SKILL_CANT_CAST_ITEM

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ITEM:
			# 只能对物品施展
			return csstatus.SKILL_CANT_ITEM_ONLY
		if target.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = target.getOwner()
			if owner.etype == "MAILBOX" :
				return csstatus.SKILL_NO_TARGET
			target = owner.entity
		if target.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_ROLE_ENTITY
		return self._validReceiver( caster, target.getObject() )

	def validReceiver( self, caster, receiver ):
		"""
		判断目标是否有效
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		#请看 Spell_SpellToItem.py  receive
		uid = receiver.queryTemp( "spellItem_uid", -1 )

		item = receiver.getItemByUid_( uid )
		if item is None:
			return csstatus.SKILL_ITEM_NOT_IN_BAG

		return self._validReceiver( caster, item )

	def getReceivers( self, caster, target ):
		"""
		获取所有的在范围内的entity列表
		@param target: 受击者
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: list of entity
		"""
		#因为target就是被包装的一个item所以这里直接返回
		if target.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = target.getOwner()
			if owner.etype == "MAILBOX" :
				return []
			return [owner.entity]
		return  []

class ReceiverObjectSelfPet( ReceiverObjectEntity ):
	"""
	作用对象是自己的宠物 相当与自身 无需选择一个目标(自身，自身圆形，自身扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		actPet = caster.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX" :
			return actPet.entity
		return None

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver == None :
			return csstatus.SKILL_PET_NO_CONJURED

		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY

		if caster.spaceID != receiver.spaceID:
			return csstatus.SKILL_PET_NO_FIND

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
			#取消下面部分， 和策划商量后决定对自己或者自己的宠物为施展对象的技能不再去适应性的释放
			#skillID = self.parent.getID()
			#fitSkillID = binarySearch( targetLv, skillID )
			#if fitSkillID == -1:
			#	return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		actPet = caster.pcg_getActPet()
		# 目标合法性判断 必须召唤一个宠物后才能使用
		if actPet is None or actPet.etype == "MAILBOX" or actPet.entity is None or actPet.entity.isDestroyed:
			return csstatus.SKILL_PET_NO_CONJURED
		return self._validReceiver( caster, actPet.entity )

	def validReceiver( self, caster, receiver ):
		"""
		判断目标是否有效
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		return self._validReceiver( caster, receiver )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 受击者
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py

		@rtype: list of Entity
		"""
		actPet = caster.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX":
			return [ actPet.entity ]
		return []

class ReceiverObjectPet( ReceiverObjectEntity ):
	"""
	作用对象是任何一个宠物 需选择一个目标(自身，自身圆形，自身扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY
		if receiver.getEntityType() != csdefine.ENTITY_TYPE_PET:
			return csstatus.SKILL_MISSING_NOT_PET
		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX

		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

class ReceiverObjectNPC( ReceiverObjectEntity ):
	"""
	作用对象是怪物(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY

		if receiver.utype != csdefine.ENTITY_TYPE_NPC or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_MONSTER_ENTITY

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )


class ReceiverObjectNPCObject( ReceiverObjectEntity ):
	"""
	作用对象是场景NPC(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY
		if receiver.utype not in [csdefine.ENTITY_TYPE_QUEST_BOX, csdefine.ENTITY_TYPE_NPC_OBJECT, csdefine.ENTITY_TYPE_FRUITTREE] or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_MONSTER_ENTITY
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	@staticmethod
	def isLive( caster, receiver ):
		"""
		受术者是否活着
		"""
		return csstatus.SKILL_GO_ON

class ReceiverObjectVehicleDart( ReceiverObjectEntity ):
	"""
	作用对象是镖车
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		if targetEntity:
			return targetEntity
		return caster

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if tObject.utype != csdefine.ENTITY_TYPE_VEHICLE_DART:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = tObject.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, tObject )

class ReceiverObjectSelfSlaveMonster( ReceiverObjectEntity ):
	"""
	作用对象是自己的从属怪物
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		if targetEntity:
			return targetEntity
		return caster

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET


		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if tObject.utype != csdefine.ENTITY_TYPE_SLAVE_MONSTER or tObject.utype != csdefine.ENTITY_TYPE_PANGU_NAGUAL:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = tObject.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, tObject )

class ReceiverObjectOtherRole( ReceiverObjectEntity ):
	"""
	作用对象是玩家(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:								# 手术者死亡
			return csstatus.SKILL_IS_ENEMY_ENTITY
		if receiver == caster :									# 对自己施法
			return csstatus.SKILL_CAST_OBJECT_INVALID
		if receiver.utype != csdefine.ENTITY_TYPE_ROLE and \
			receiver.utype != csdefine.ENTITY_TYPE_PET :		# 不明目标
				return csstatus.SKILL_CAST_OBJECT_INVALID
		if caster.utype == csdefine.ENTITY_TYPE_ROLE :
			actPet = caster.pcg_getActPet()
			if actPet and actPet.entity.id == receiver.id :		# 对自己宠物施法
				return csstatus.SKILL_CAST_OBJECT_INVALID
		if caster.utype == csdefine.ENTITY_TYPE_PET and \
			caster.getOwner().entity.id == receiver.id :		# 宠物对自己主人施法
				return csstatus.SKILL_CAST_OBJECT_INVALID

		if receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NO_RECEIVER

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )


class ReceiverObjectNPCOrMonster( ReceiverObjectEntity ):
	"""
	作用对象是NPC或者怪物的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY

		if not receiver.utype in [ csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_YAYU ] or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_MONSTER_ENTITY

		#级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )


class ReceiverObjectRoleWithCompletedQuests(ReceiverObjectRoleOnly):

	def __init__( self, parent ):
		ReceiverObjectRoleOnly.__init__(self, parent)
		self.quests = []

	def init( self, dictDat ):
		"""
		"""
		ReceiverObjectRoleOnly.init(self, dictDat)
		self.quests = [int(qid) for qid in dictDat["value1"].split()]  	#任务列表

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		state = ReceiverObjectRoleOnly._validReceiver(self, caster, receiver)
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查任务要求，必须是指定的任务均已完成
		for questID in self.quests:
			if not receiver.questIsCompleted(questID):
				return csstatus.SKILL_CAST_OBJECT_INVALID

		return csstatus.SKILL_GO_ON


class ReceiverObjectRoleHasUnCompletedQuests(ReceiverObjectRoleOnly):

	def __init__( self, parent ):
		ReceiverObjectRoleOnly.__init__(self, parent)
		self.quests = []

	def init( self, dictDat ):
		"""
		"""
		ReceiverObjectRoleOnly.init(self, dictDat)
		self.quests = [int(qid) for qid in dictDat["value1"].split()]  	#任务列表

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		state = ReceiverObjectRoleOnly._validReceiver(self, caster, receiver)
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查任务要求，必须是指定的任务均已完成
		for questID in self.quests:
			if receiver.has_quest(questID) and not receiver.questIsCompleted(questID):
				return csstatus.SKILL_GO_ON

		return csstatus.SKILL_CAST_OBJECT_INVALID


g_reveiverCondition = {
	csdefine.RECEIVER_CONDITION_ENTITY_NONE			:	ReceiverObjectBase,
	csdefine.RECEIVER_CONDITION_ENTITY_SELF			:	ReceiverObjectSelf,
	csdefine.RECEIVER_CONDITION_ENTITY_TEAMMEMBER	:	ReceiverObjectTeam,
	csdefine.RECEIVER_CONDITION_ENTITY_MONSTER		:	ReceiverObjectMonster,
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE			:	ReceiverObjectRole,	# 对玩家有效的技能也能对宠物有效
	csdefine.RECEIVER_CONDITION_ENTITY_ENEMY		:	ReceiverObjectEnemy,
	csdefine.RECEIVER_CONDITION_ENTITY_NOTATTACK	:	ReceiverObjectNotAttack,
	csdefine.RECEIVER_CONDITION_KIGBAG_ITEM			:	ReceiverObjectItem,
	csdefine.RECEIVER_CONDITION_ENTITY_RANDOMENEMY	:	ReceiverObjectEnemyRandom,
	csdefine.RECEIVER_CONDITION_ENTITY_SELF_PET		:	ReceiverObjectSelfPet,
	csdefine.RECEIVER_CONDITION_ENTITY_PET			:	ReceiverObjectPet,
	csdefine.RECEIVER_CONDITION_ENTITY_NPC			:	ReceiverObjectNPC,
	csdefine.RECEIVER_CONDITION_ENTITY_SELF_SLAVE_MONSTER			:	ReceiverObjectSelfSlaveMonster,
	csdefine.RECEIVER_CONDITION_ENTITY_OTHER_ROLE	:	ReceiverObjectOtherRole,
	csdefine.RECEIVER_CONDITION_ENTITY_NPC_OR_MONSTER:	ReceiverObjectNPCOrMonster,
	csdefine.RECEIVER_CONDITION_ENTITY_NPCOBJECT	:	ReceiverObjectNPCObject,
	csdefine.RECEIVER_CONDITION_ENTITY_NOT_ENEMY_ROLE: ReceiverObjectNotEnemyRole,
	csdefine.RECEIVER_CONDITION_ENTITY_VEHICLE_DART	:	ReceiverObjectVehicleDart,
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ONLY	: ReceiverObjectRoleOnly,	# 仅对玩家有效的技能，以区别于RECEIVER_CONDITION_ENTITY_ROLE
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ENEMY_ONLY	: ReceiverObjectRoleEnemyOnly,	# 仅对敌对玩家有效
	csdefine.RECEIVER_CONDITION_ROLE_WITH_COMPLETED_QUESTS	: ReceiverObjectRoleWithCompletedQuests, # 目标是完成了指定任务的玩家
	csdefine.RECEIVER_CONDITION_ROLE_HAS_UNCOMPLETED_QUESTS	: ReceiverObjectRoleHasUnCompletedQuests, # 目标是完成了指定任务的玩家
}

def newInstance( condition, parent ):
	"""
	产生技能条件
		@param objectType:	条件类型
		@type objectType:	INT32
	"""
	return g_reveiverCondition[condition]( parent )


def binarySearch( playerLv, skillID ):	# 15:00 2008-11-24,wsf
	"""
	2分查找适合playerLv的技能id

	@param playerLv : 玩家级别
	@type playerLv : UINT8
	@param skillID : 高等级技能
	@type skillID : INT64
	"""
	from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA
	headString = str( skillID )[:-3]		# 获得技能id的第一段
	tailInt = int( str( skillID )[-3:] )	# 获得技能的级别
	min = 001
	max = tailInt
	fitSkillID = -1
	while min <= max:
		mid = ( min + max ) / 2
		midStr = str( mid )
		while len( midStr ) < 3:	# 不够3位就补0
			midStr = "0" + midStr
		tempSkillID = int( headString + midStr )
		if not SKILL_DATA.has_key( tempSkillID ):
			return fitSkillID

		castObjLevelMin = SKILL_DATA[ tempSkillID ]["CastObjLevelMin"]
		if castObjLevelMin == playerLv:
			return tempSkillID
		if castObjLevelMin < playerLv:
			min = mid + 1
			fitSkillID = tempSkillID
		else:
			max = mid - 1
	return fitSkillID


