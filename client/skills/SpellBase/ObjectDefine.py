# -*- coding: gb18030 -*-
#
# $Id: ObjectDefine.py,v 1.11 2008-08-29 03:56:22 qilan Exp $

"""
对象选择
"""

from bwdebug import *
from csdefine import *
import csdefine
import csconst
import csstatus
import weakref
import utils
import ReceiverObject
import gbref
import Math

class ObjectNone:
	"""
	无施法位置和对象
	"""
	def __init__( self, parent ):
		"""
		"""
		self.parent = weakref.proxy( parent )

	def init( self, dict ):
		"""
		virtual method.
		spell配置文件python dict
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
		
	def valid( self, caster, target ):
		"""
		virtual method.
		检查施展开始时要求 (法术还未释放出时的检查)
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
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distance > range:		# 必须加上偏移
			# 距离目标太远
			return csstatus.SKILL_TOO_FAR
			
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distance < range:		# 必须加上偏移
			# 距离目标太近
			return csstatus.SKILL_TOO_NEAR
			
		return csstatus.SKILL_GO_ON

class ObjectEntity( ObjectNone ):
	"""
	施法目标为Entity
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell配置文件python dict
		"""
		self._receiverObject = ReceiverObject.newInstance(  eval( dict[ "conditions" ] ), self.parent )
		self._receiverObject.init( dict )
	
	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return self._receiverObject.convertCastObject( caster, targetEntity )

	def valid( self, caster, target ):
		"""
		virtual method.
		检查施展开始时要求 (法术还未释放出时的检查)
		校验目标是否符合选择要求。
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		state = self._receiverObject.validCastObject( caster, target )
		if csstatus.SKILL_GO_ON != state:
			return state
		
		# 距离判断
		distanceBB = caster.distanceBB( target.getObject() )
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distanceBB > range:		# 必须加上偏移
			# 距离目标太远
			return csstatus.SKILL_TOO_FAR
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distanceBB < range:		# 必须加上偏移
			# 距离目标太近
			return csstatus.SKILL_TOO_NEAR
		return csstatus.SKILL_GO_ON

class ObjectEntitys( ObjectEntity ):
	"""
	施法目标为Entitys
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectEntity.__init__( self, parent )

	def valid( self, caster, target ):
		"""
		virtual method.
		检查施展开始时要求 (法术还未释放出时的检查)
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		校验目标是否符合选择要求。
		"""
		state = self._receiverObject.validCastObject( caster, target )
		if csstatus.SKILL_GO_ON != state:
			return state
		
		# 距离判断
		distanceBB = caster.distanceBB( target.getObject() )
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distanceBB > range:		# 必须加上偏移
			# 距离目标太远
			return csstatus.SKILL_TOO_FAR
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distanceBB < range:		# 必须加上偏移
			# 距离目标太近
			return csstatus.SKILL_TOO_NEAR
		return csstatus.SKILL_GO_ON
		
class ObjectItem( ObjectNone ):
	"""
	施法目标为物品
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell配置文件python dict
		"""
		self._receiverObject = ReceiverObject.newInstance( eval( dict[ "conditions" ] ), self.parent)
		self._receiverObject.init( dict )

	def convertCastObject( self, caster, targetEntity ):
		"""
		各类型根据需要转换施展对象
		@param   caster: 施法者
		@type    caster: Entity
		@param targetEntity: 受击者
		@type  targetEntity: Entity
		"""
		return self._receiverObject.convertCastObject( caster, targetEntity )

	def valid( self, caster, target ):
		"""
		virtual method.
		检查施展开始时要求 (法术还未释放出时的检查)
		校验目标是否符合选择要求。
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 判断是否为有效的目标
		return self._receiverObject.validCastObject( caster, target )
	
class ObjectCursorPosition( ObjectNone ):
	def __init__( self, parent ):
		ObjectNone.__init__( self, parent )
	
	def convertCastObject( self, caster, targetEntity ):
		cursorPos = gbref.cursorToDropPoint()
		return cursorPos
	
	def valid( self, caster, target ):
		"""
		virtual method.
		检查施展开始时要求 (法术还未释放出时的检查)
		校验目标是否符合选择要求。
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		distance = caster.position.flatDistTo( target.getObjectPosition() )
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distance > range:		# 必须加上偏移
			# 距离目标太远
			return csstatus.SKILL_TOO_FAR
			
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distance < range:		# 必须加上偏移
			# 距离目标太近
			return csstatus.SKILL_TOO_NEAR
			
		return csstatus.SKILL_GO_ON

g_objects = {
	csdefine.SKILL_CAST_OBJECT_TYPE_NONE		:	ObjectNone,			# 无位置无目标
	csdefine.SKILL_CAST_OBJECT_TYPE_POSITION	:	ObjectPosition,		# 位置
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITY		:	ObjectEntity,		# entity
	csdefine.SKILL_CAST_OBJECT_TYPE_ITEM		:	ObjectItem,			# 物品
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITYS		:	ObjectEntitys,		# entitys
}

def newInstance( objectType, spellInstance ):
	"""
	获取对象选择实例。
	@type objectType:	string
	"""
	return g_objects[objectType]( spellInstance )


#
# $Log: not supported by cvs2svn $
# Revision 1.10  2008/08/29 02:35:27  qilan
# 调整技能条件判断顺序
#
# Revision 1.9  2008/07/15 04:08:01  kebiao
# 将技能配置修改到datatool相关初始化需要修改
#
# Revision 1.8  2008/04/16 07:19:48  zhangyuxing
# no message
#
# Revision 1.7  2008/04/15 06:52:43  zhangyuxing
# 处理场景物件等无等级属性，在判断中提示BUG
#
# Revision 1.6  2008/03/29 08:58:15  phw
# 调整distanceBB()的调用方式，原来从utils模块中调用，改为直接在 entity 身上调用
#
# Revision 1.5  2008/03/29 07:39:08  kebiao
# 去掉技能计算距离的偏移
#
# Revision 1.4  2008/03/03 06:36:33  kebiao
# 增加最小距离的判断
#
# Revision 1.3  2008/03/01 08:35:21  kebiao
# 增加validTarget接口 仅仅对施展目标类型的相关判断 忽略其他条件 如距离
#
# Revision 1.2  2008/01/24 05:45:58  kebiao
# 增加对施法目标级别要求的功能
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# 调整技能结构，目录结构
#
#
