# -*- coding: gb18030 -*-
#
# $Id: ObjectDefine.py,v 1.22 2008-09-01 09:39:08 qilan Exp $

"""
����ѡ��
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
			#���������CastObjectType == 2 ���߱�����<CastObjectType>�����ó�����Ϊentity����ص�����
			#���<ReceiverCondition>����ΪRECEIVER_CONDITION_ENTITY_SELF ��ôCastObjectType����Ϊ2����������ΪRECEIVER_CONDITION_ENTITY_SELF
			#��Ϊ<ReceiverCondition>����ΪRECEIVER_CONDITION_ENTITY_SELF��ʵ����˵�����������Ӱ����ǵ���entity
"""

#ʩ��Ŀ��ķ�װ

class ObjectNone:
	"""
	��ʩ��λ�úͶ���
	"""
	def __init__( self, parent ):
		"""
		"""
		self.parent = weakref.proxy( parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell����dict
		"""
		pass
		
	def valid( self, caster, target ):
		"""
		virtual method.
		У��Ŀ���Ƿ����ѡ��Ҫ��
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		return csstatus.SKILL_GO_ON

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return None
		
class ObjectPosition( ObjectNone ):
	"""
	ʩ��Ŀ��Ϊλ��
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell����dictDat
		"""
		pass
		
	def valid( self, caster, target ):
		"""
		virtual method.
		У��Ŀ���Ƿ����ѡ��Ҫ��
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if not target or target.getObject() is None :
			# ��ѡ��һ��ʩ��λ��
			return csstatus.SKILL_MISS_POSITION
			
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_POSITION:
			return csstatus.SKILL_CAST_POSITION_ONLY
		
		# �����Ǳ����жϵ�
		distance = caster.position.flatDistTo( target.getObjectPosition() )

		minRange = self.parent.getRangeMin(caster)
		if minRange > 0.0 and distance < minRange:
			# ����Ŀ��̫��
			return csstatus.SKILL_TOO_NEAR

		# �����Ǳ����жϵ�
		castRange = self.parent.getCastRange(caster)
		if castRange > 0.0 and distance > castRange + csconst.ATTACK_RANGE_BIAS:		# �������ƫ��
			return csstatus.SKILL_TOO_FAR
			
		return csstatus.SKILL_GO_ON
		
class ObjectEntity( ObjectNone ):
	"""
	ʩ��Ŀ��ΪEntity
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell����dictDat
		"""
		
		self._receiverCondition = ReceiverObject.newInstance(  eval( dictDat[ "conditions" ] ), self.parent )
		self._receiverCondition.init( dictDat )
		
	def valid( self, caster, target ):
		"""
		virtual method.
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		У��Ŀ���Ƿ����ѡ��Ҫ��
		"""
		tObject = target.getObject()
		
		if not ( target or tObject or tObject.isDestroyed ):
			return csstatus.SKILL_MISS_TARGET
		
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			return csstatus.SKILL_CAST_ENTITY_ONLY
		
		state = self._receiverCondition.validCastObject( caster, target )
		if csstatus.SKILL_GO_ON != state:
			return state
		
		# �����Ǳ����жϵ�
		distanceBB = caster.distanceBB( tObject )
		maxRange = self.parent.getRangeMax(caster) 
		if maxRange > 0.0 and distanceBB > maxRange + caster.getRangeBias():		# ����ƫ��
			return csstatus.SKILL_TOO_FAR
		minRange = self.parent.getRangeMin(caster)
		if minRange > 0.0 and distanceBB < minRange:
			return csstatus.SKILL_TOO_NEAR

		return csstatus.SKILL_GO_ON
		
	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return self._receiverCondition.convertCastObject( caster, targetEntity )
		
class ObjectEntitys( ObjectEntity ):
	"""
	ʩ��Ŀ��ΪEntitys
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell����dictDat
		"""
		
		ObjectEntity.init( self, dictDat )
		
	def valid( self, caster, target ):
		"""
		virtual method.
		���ʩչ��ʼʱҪ�� (������δ�ͷų�ʱ�ļ��)
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		У��Ŀ���Ƿ����ѡ��Ҫ��
		"""
		tObject = target.getObject()
		
		if target is None or tObject is None:
			return csstatus.SKILL_MISS_TARGET
		
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITYS:
			return csstatus.SKILL_CAST_ENTITY_ONLY
		
		# �����ж�
		distanceBB = caster.distanceBB( tObject )
		maxRange = self.parent.getRangeMax(caster)
		if maxRange > 0.0 and distanceBB > maxRange + csconst.ATTACK_RANGE_BIAS:		# �������ƫ��
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
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return self._receiverCondition.convertCastObject( caster, targetEntity )
		
class ObjectItem( ObjectNone ):
	"""
	ʩ��Ŀ��Ϊ��Ʒ
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell����dictDat
		"""
		self._receiverCondition = ReceiverObject.newInstance( eval( dictDat[ "conditions" ] ), self.parent)
		self._receiverCondition.init( dictDat )
		
	def valid( self, caster, target ):
		"""
		virtual method.
		���ʩչ��ʼʱҪ�� (������δ�ͷų�ʱ�ļ��)
		У��Ŀ���Ƿ����ѡ��Ҫ��
		"""
		return self._receiverCondition.validCastObject( caster, target )
		
	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return self._receiverCondition.convertCastObject( caster, targetEntity )


g_objects = {
	csdefine.SKILL_CAST_OBJECT_TYPE_NONE		:	ObjectNone,			# ��λ����Ŀ��
	csdefine.SKILL_CAST_OBJECT_TYPE_POSITION	:	ObjectPosition,		# λ��
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITY		:	ObjectEntity,		# entity
	csdefine.SKILL_CAST_OBJECT_TYPE_ITEM		:	ObjectItem,			# ��Ʒ
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITYS		:	ObjectEntitys,		# ��entity
}

def newInstance( objectType, spellInstance ):
	"""
	��ȡ����ѡ��ʵ����
	@type objectType:	string
	"""
	return g_objects[objectType]( spellInstance )


#
# $Log: not supported by cvs2svn $
