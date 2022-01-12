# -*- coding: gb18030 -*-
#
# $Id: ObjectDefine.py,v 1.22 2008-09-01 09:39:08 qilan Exp $

"""
对象选择
"""

from bwdebug import *
import weakref
import utils
import csdefine
import csconst
import csstatus
import ReceiverObject
from csdefine import *		# only for "eval" expediently

"""
			#如果配置上CastObjectType == 2 或者必须在<CastObjectType>中配置出条件为entity与相关的条件
			#如果<ReceiverCondition>条件为RECEIVER_CONDITION_ENTITY_SELF 那么CastObjectType必须为2且条件必须为RECEIVER_CONDITION_ENTITY_SELF
			#因为<ReceiverCondition>条件为RECEIVER_CONDITION_ENTITY_SELF其实隐含说明了这个技能影响的是单个entity
"""

#施法目标的封装

class ObjectNone:
	"""
	无施法位置和对象
	"""
	def __init__( self, parent ):
		"""
		"""
		self.parent = weakref.proxy( parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell配置dict
		"""
		pass
		
	def valid( self, caster, target ):
		"""
		virtual method.
		校验目标是否符合选择要求。
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
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
		return None
		
class ObjectPosition( ObjectNone ):
	"""
	施法目标为位置
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell配置dictDat
		"""
		pass
		
	def valid( self, caster, target ):
		"""
		virtual method.
		校验目标是否符合选择要求。
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if not target or target.getObject() is None :
			# 请选择一个施法位置
			return csstatus.SKILL_MISS_POSITION
			
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_POSITION:
			return csstatus.SKILL_CAST_POSITION_ONLY
		
		# 距离是必须判断的
		distance = caster.position.flatDistTo( target.getObjectPosition() )

		minRange = self.parent.getRangeMin(caster)
		if minRange > 0.0 and distance < minRange:
			# 距离目标太近
			return csstatus.SKILL_TOO_NEAR

		# 距离是必须判断的
		castRange = self.parent.getCastRange(caster)
		if castRange > 0.0 and distance > castRange + csconst.ATTACK_RANGE_BIAS:		# 必须加上偏移
			return csstatus.SKILL_TOO_FAR
			
		return csstatus.SKILL_GO_ON
		
class ObjectEntity( ObjectNone ):
	"""
	施法目标为Entity
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell配置dictDat
		"""
		
		self._receiverCondition = ReceiverObject.newInstance(  eval( dictDat[ "conditions" ] ), self.parent )
		self._receiverCondition.init( dictDat )
		
	def valid( self, caster, target ):
		"""
		virtual method.
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		校验目标是否符合选择要求。
		"""
		tObject = target.getObject()
		
		if not ( target or tObject or tObject.isDestroyed ):
			return csstatus.SKILL_MISS_TARGET
		
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			return csstatus.SKILL_CAST_ENTITY_ONLY
		
		state = self._receiverCondition.validCastObject( caster, target )
		if csstatus.SKILL_GO_ON != state:
			return state
		
		# 距离是必须判断的
		distanceBB = caster.distanceBB( tObject )
		maxRange = self.parent.getRangeMax(caster) 
		if maxRange > 0.0 and distanceBB > maxRange + caster.getRangeBias():		# 加上偏移
			return csstatus.SKILL_TOO_FAR
		minRange = self.parent.getRangeMin(caster)
		if minRange > 0.0 and distanceBB < minRange:
			return csstatus.SKILL_TOO_NEAR

		return csstatus.SKILL_GO_ON
		
	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return self._receiverCondition.convertCastObject( caster, targetEntity )
		
class ObjectEntitys( ObjectEntity ):
	"""
	施法目标为Entitys
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell配置dictDat
		"""
		
		ObjectEntity.init( self, dictDat )
		
	def valid( self, caster, target ):
		"""
		virtual method.
		检查施展开始时要求 (法术还未释放出时的检查)
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		校验目标是否符合选择要求。
		"""
		tObject = target.getObject()
		
		if target is None or tObject is None:
			return csstatus.SKILL_MISS_TARGET
		
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITYS:
			return csstatus.SKILL_CAST_ENTITY_ONLY
		
		# 距离判断
		distanceBB = caster.distanceBB( tObject )
		maxRange = self.parent.getRangeMax(caster)
		if maxRange > 0.0 and distanceBB > maxRange + csconst.ATTACK_RANGE_BIAS:		# 必须加上偏移
			return csstatus.SKILL_TOO_FAR
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distanceBB < range:
			return csstatus.SKILL_TOO_NEAR

		state = self._receiverCondition.validCastObject( caster, target )
		if csstatus.SKILL_GO_ON != state:
			return state

		return csstatus.SKILL_GO_ON
		
	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return self._receiverCondition.convertCastObject( caster, targetEntity )
		
class ObjectItem( ObjectNone ):
	"""
	施法目标为物品
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell配置dictDat
		"""
		self._receiverCondition = ReceiverObject.newInstance( eval( dictDat[ "conditions" ] ), self.parent)
		self._receiverCondition.init( dictDat )
		
	def valid( self, caster, target ):
		"""
		virtual method.
		检查施展开始时要求 (法术还未释放出时的检查)
		校验目标是否符合选择要求。
		"""
		return self._receiverCondition.validCastObject( caster, target )
		
	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return self._receiverCondition.convertCastObject( caster, targetEntity )


g_objects = {
	csdefine.SKILL_CAST_OBJECT_TYPE_NONE		:	ObjectNone,			# 无位置无目标
	csdefine.SKILL_CAST_OBJECT_TYPE_POSITION	:	ObjectPosition,		# 位置
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITY		:	ObjectEntity,		# entity
	csdefine.SKILL_CAST_OBJECT_TYPE_ITEM		:	ObjectItem,			# 物品
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITYS		:	ObjectEntitys,		# 多entity
}

def newInstance( objectType, spellInstance ):
	"""
	获取对象选择实例。
	@type objectType:	string
	"""
	return g_objects[objectType]( spellInstance )


#
# $Log: not supported by cvs2svn $
