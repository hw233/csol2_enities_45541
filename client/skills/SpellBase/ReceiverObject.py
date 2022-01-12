# -*- coding: gb18030 -*-
#
# $Id: ReceiverObject.py,v 1.14 2008-09-05 01:45:30 zhangyuxing Exp $

"""
"""

import csdefine
import csstatus
from csdefine import *		# for eval expediently
from bwdebug import *
from interface.CombatUnit import CombatUnit
import items
import weakref
import skills

class ReceiverObjectBase:
	"""
	"""
	def __init__( self, parent ):
		self.parent = parent

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition配置文件python dict
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

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return targetEntity

class ReceiverObjectEntity( ReceiverObjectBase ):
	"""
	"""
	def __init__( self, parent ):
		ReceiverObjectBase.__init__( self, parent )
		self._stateFunc = self.isLive

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition配置文件python dict
		"""
		if dict[ "Dead" ] == 1:
			self._stateFunc = self.isDead

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
			if not receiver.isDead():
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
			if receiver.isDead():
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# 只输出错误，但仍然有效，得到要求不符合的结果
			# 原因在于像掉落物品这一类的entity是不会有（最起码现在没有）isDead()方法的
			INFO_MSG( errstr )
		return csstatus.SKILL_TARGET_NOT_DEAD

class ReceiverObjectSelf( ReceiverObjectEntity ):
	"""
	作用对象是自己(自身，自身圆形，自身扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if caster.id != target.getObject().id:
				# 你不能对该目标使用此技能
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		return self._stateFunc( caster, caster )

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

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition配置文件python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if caster.utype == target.getObject().utype and \
				caster.isInTeam() and \
				caster.isTeamMember( target.getObject().id ):
				# 级别判断
				lvMin = self.parent.getCastTargetLevelMin()
				lvMax = self.parent.getCastTargetLevelMax()
				targetLv = target.getObject().getLevel()
				if lvMin > 0 and targetLv < lvMin :
					# 施展目标级别太低了
					skillID = self.parent.getID()
					fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
					if fitSkillID == -1:
						return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
				if lvMax > 0 and targetLv > lvMax :
					# 施展目标级别太高了
					return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
				return self._stateFunc( caster, target.getObject() )
			else:
				# 你不能对该目标使用此技能
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

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

class ReceiverObjectMonster( ReceiverObjectEntity ):
	"""
	作用对象是怪物(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_MONSTER:
				return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectRole( ReceiverObjectEntity ):
	"""
	作用对象是玩家(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_ROLE and target.getObject().utype != csdefine.ENTITY_TYPE_PET:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		if targetEntity is None: return caster
		if not targetEntity.inWorld: return caster

		if caster.queryRelation( targetEntity ) == csdefine.RELATION_ANTAGONIZE:
			return caster
		return targetEntity

class ReceiverObjectRoleOnly( ReceiverObjectRole ):
	"""
	作用对象是玩家(单体，圆形，扇形...)的受术条件
	"""
	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
			
		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_ROLE:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectRoleEnemyOnly( ReceiverObjectRoleOnly ):
	"""
	只对敌对玩家有效
	"""
	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
			
		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_ROLE:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW
			
		if caster.queryRelation( target.getObject() ) != csdefine.RELATION_ANTAGONIZE:
			return csstatus.SKILL_NOT_ENEMY_ENTITY
			
		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )
		
class ReceiverObjectEnemy( ReceiverObjectEntity ):
	"""
	作用对象是可攻击敌人(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not self.isEnemy( caster, target.getObject() ):
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def isEnemy( self, caster, receiver ):
		"""
		是否敌人
		"""
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE

class ReceiverObjectEnemyRandom( ReceiverObjectEnemy ):
	"""
	对象是可攻击敌人随机攻击区域类其他可攻击对象(单体，圆形，扇形...)的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEnemy.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition配置文件python dict
		"""
		ReceiverObjectEnemy.init( self, dict )

class ReceiverObjectNotAttack( ReceiverObjectEntity ):
	"""
	作用对象是不可攻击entity(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not self.isNotFight( caster, target.getObject() ):
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def isNotFight( self, caster, receiver ):
		"""
		可否攻击
		"""
		return ( not hasattr(receiver,"canFight") and not receiver.canFight() ) or caster.id == receiver.id

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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not target.getObject().isEntityType( csdefine.ENTITY_TYPE_ROLE ) or self.isEnemy( caster, target.getObject() ):
				return csstatus.SKILL_TARGET_IS_ENEMY_ROLE
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def isEnemy( self, caster, receiver ):
		"""
		是否敌人
		"""
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE

class ReceiverObjectItem( ReceiverObjectBase ):
	"""
	作用对象是物品的受术条件
	"""
	def __init__( self, parent ):
		"""
		"""
		pass

	def init( self, dict ):
		"""
		初始化能处理的物品类型
		"""
		self._itemTypes = set([])

		val = dict[ "value1" ]
		for v in val.split(";"):
			d = eval( v )
			if type( d ) == list:
				self._itemTypes.update( set( d ) )
			else:
				self._itemTypes.add( d )

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
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ITEM:
			# 只能对物品施展
			return csstatus.SKILL_CANT_ITEM_ONLY

		item = target.getObject()
		if item == None:
			# 找不到接受法术的物品
			return csstatus.SKILL_ITEM_NOT_EXIST

		try:
			# 不是一个物品
			if not isinstance( target.getObject(), items.CItemBase.CItemBase ):
				# 你不能对该目标使用此技能
				return csstatus.SKILL_CAST_OBJECT_INVALID
			# 不是玩家背包的物品
			if target.getObject().getUid() == -1:
				return csstatus.SKILL_CAST_OBJECT_INVALID
			if target.getObject().getType() in self._itemTypes:
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW
		# 你不能对该目标使用此技能
		return csstatus.SKILL_CAST_OBJECT_INVALID

class ReceiverObjectSelfPet( ReceiverObjectEntity ):
	"""
	作用对象是自己的宠物 相当与自身 无需选择一个目标(自身，自身圆形，自身扇形...)的受术条件
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

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return caster.pcg_getActPet()

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		target = caster.pcg_getActPet()
		# 目标合法性判断
		if target is None:
			# 必须召唤一个宠物后才能使用
			return csstatus.SKILL_PET_NO_CONJURED

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
			#取消下面部分， 和策划商量后决定对自己或者自己的宠物为施展对象的技能不再去适应性的释放
			#skillID = self.parent.getID()
			#fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			#if fitSkillID == -1:
			#	return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target )

class ReceiverObjectPet( ReceiverObjectEntity ):
	"""
	作用对象是任何一个宠物 需选择一个目标(自身，自身圆形，自身扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().getEntityType() != csdefine.ENTITY_TYPE_PET:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectNPC( ReceiverObjectEntity ):
	"""
	作用对象是怪物(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_NPC:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )


class ReceiverObjectNPCObject( ReceiverObjectEntity ):
	"""
	作用对象是NPCObject(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		try:
			if target.getObject().utype not in [csdefine.ENTITY_TYPE_NPC_OBJECT, csdefine.ENTITY_TYPE_QUEST_BOX, csdefine.ENTITY_TYPE_FRUITTREE]:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		return self._stateFunc( caster, target.getObject() )

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

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition配置文件python dict
		"""
		ReceiverObjectEntity.init( self, dict )

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
		if target is None or target.getObject() is None:
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_VEHICLE_DART:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectSelfSlaveMonster( ReceiverObjectEntity ):
	"""
	作用对象是自己的从属怪物
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
		if target is None or target.getObject() is None:
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_SLAVE_MONSTER:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectOtherRole( ReceiverObjectEntity ):
	"""
	作用对象是玩家(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, targetWrap ):
		"""
		判断目标是否有效
		@param targetWrap: 施展对象
		@type  targetWrap: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if targetWrap is None or targetWrap.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		target = targetWrap.getObject()
		if targetWrap.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if ( target.utype != csdefine.ENTITY_TYPE_ROLE and target.utype != csdefine.ENTITY_TYPE_PET ) or \
				( caster.utype == csdefine.ENTITY_TYPE_ROLE and caster.pcg_getActPet() == target ) or \
				( caster.utype == csdefine.ENTITY_TYPE_PET and caster.getOwner() == target ) or \
				target == caster :
					return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target )

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return targetEntity



class ReceiverObjectNPCOrMonster( ReceiverObjectEntity ):
	"""
	作用对象是怪物(单体，圆形，扇形...)的受术条件
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

	def validCastObject( self, caster, target ):
		"""
		判断目标是否有效
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# 目标合法性判断
		if target is None or target.getObject() is None:
			# 请选择一个目标
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# 无效的目标2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not target.getObject().utype in [ csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_YAYU ]:
				return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER
		except AttributeError, errstr:
			# 出现这个错误一般是客户端未初始化完一个entity, 准确说是未收到服务器的属性包，
			# 而导致此刻没有这个属性
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# 级别判断
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# 施展目标级别太低了
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# 施展目标级别太高了
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

g_reveiverCondition = {
	csdefine.RECEIVER_CONDITION_ENTITY_NONE			:	ReceiverObjectBase,
	csdefine.RECEIVER_CONDITION_ENTITY_SELF			:	ReceiverObjectSelf,
	csdefine.RECEIVER_CONDITION_ENTITY_TEAMMEMBER	:	ReceiverObjectTeam,
	csdefine.RECEIVER_CONDITION_ENTITY_MONSTER		:	ReceiverObjectMonster,
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE			:	ReceiverObjectRole,
	csdefine.RECEIVER_CONDITION_ENTITY_ENEMY		:	ReceiverObjectEnemy,
	csdefine.RECEIVER_CONDITION_ENTITY_NOTATTACK	:	ReceiverObjectNotAttack,
	csdefine.RECEIVER_CONDITION_KIGBAG_ITEM			:	ReceiverObjectItem,
	csdefine.RECEIVER_CONDITION_ENTITY_RANDOMENEMY	:	ReceiverObjectEnemyRandom,
	csdefine.RECEIVER_CONDITION_ENTITY_SELF_PET		:	ReceiverObjectSelfPet,
	csdefine.RECEIVER_CONDITION_ENTITY_PET			:	ReceiverObjectPet,
	csdefine.RECEIVER_CONDITION_ENTITY_NPC			:	ReceiverObjectNPC,
	csdefine.RECEIVER_CONDITION_ENTITY_SELF_SLAVE_MONSTER	:	ReceiverObjectSelfSlaveMonster,
	csdefine.RECEIVER_CONDITION_ENTITY_OTHER_ROLE	:	ReceiverObjectOtherRole,
	csdefine.RECEIVER_CONDITION_ENTITY_NPC_OR_MONSTER:	ReceiverObjectNPCOrMonster,
	csdefine.RECEIVER_CONDITION_ENTITY_NPCOBJECT	:	ReceiverObjectNPCObject,
	csdefine.RECEIVER_CONDITION_ENTITY_NOT_ENEMY_ROLE: ReceiverObjectNotEnemyRole,
	csdefine.RECEIVER_CONDITION_ENTITY_VEHICLE_DART	:	ReceiverObjectVehicleDart,
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ONLY	: ReceiverObjectRoleOnly,	# 仅对玩家有效的技能，以区别于RECEIVER_CONDITION_ENTITY_ROLE
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ENEMY_ONLY	: ReceiverObjectRoleEnemyOnly,	# 仅对敌对玩家有效
}

def newInstance( condition, parent ):
	"""
	产生技能条件
		@param objectType:	条件类型
		@type objectType:	INT32
	"""
	return g_reveiverCondition[condition]( parent )


