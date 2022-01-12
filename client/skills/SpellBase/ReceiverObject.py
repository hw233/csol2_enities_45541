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
		spell��ĳ��condition�����ļ�python dict
		"""
		pass

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
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
		spell��ĳ��condition�����ļ�python dict
		"""
		if dict[ "Dead" ] == 1:
			self._stateFunc = self.isDead

	def validEntityType( self, target ):
		"""
		virtual method.
		entity�������Ƿ�Ϸ�
		"""
		return csstatus.SKILL_GO_ON

	@staticmethod
	def isLive( caster, receiver ):
		"""
		�������Ƿ����
		"""
		try:
			if not receiver.isDead():
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# ֻ������󣬵���Ȼ��Ч���õ�Ҫ�󲻷��ϵĽ��
			# ԭ�������������Ʒ��һ���entity�ǲ����У�����������û�У�isDead()������
			INFO_MSG( errstr )
		return csstatus.SKILL_TARGET_DEAD

	@staticmethod
	def isDead( caster, receiver ):
		"""
		�������Ƿ��Ѿ�����
		"""
		try:
			if receiver.isDead():
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# ֻ������󣬵���Ȼ��Ч���õ�Ҫ�󲻷��ϵĽ��
			# ԭ�������������Ʒ��һ���entity�ǲ����У�����������û�У�isDead()������
			INFO_MSG( errstr )
		return csstatus.SKILL_TARGET_NOT_DEAD

class ReceiverObjectSelf( ReceiverObjectEntity ):
	"""
	���ö������Լ�(��������Բ�Σ���������...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if caster.id != target.getObject().id:
				# �㲻�ܶԸ�Ŀ��ʹ�ô˼���
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		return self._stateFunc( caster, caster )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return caster

class ReceiverObjectTeam( ReceiverObjectEntity ):
	"""
	���ö����Ƕ����Ա(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if caster.utype == target.getObject().utype and \
				caster.isInTeam() and \
				caster.isTeamMember( target.getObject().id ):
				# �����ж�
				lvMin = self.parent.getCastTargetLevelMin()
				lvMax = self.parent.getCastTargetLevelMax()
				targetLv = target.getObject().getLevel()
				if lvMin > 0 and targetLv < lvMin :
					# ʩչĿ�꼶��̫����
					skillID = self.parent.getID()
					fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
					if fitSkillID == -1:
						return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
				if lvMax > 0 and targetLv > lvMax :
					# ʩչĿ�꼶��̫����
					return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
				return self._stateFunc( caster, target.getObject() )
			else:
				# �㲻�ܶԸ�Ŀ��ʹ�ô˼���
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		if targetEntity:
			return targetEntity
		return caster

class ReceiverObjectMonster( ReceiverObjectEntity ):
	"""
	���ö����ǹ���(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_MONSTER:
				return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectRole( ReceiverObjectEntity ):
	"""
	���ö��������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_ROLE and target.getObject().utype != csdefine.ENTITY_TYPE_PET:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		if targetEntity is None: return caster
		if not targetEntity.inWorld: return caster

		if caster.queryRelation( targetEntity ) == csdefine.RELATION_ANTAGONIZE:
			return caster
		return targetEntity

class ReceiverObjectRoleOnly( ReceiverObjectRole ):
	"""
	���ö��������(���壬Բ�Σ�����...)����������
	"""
	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
			
		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_ROLE:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectRoleEnemyOnly( ReceiverObjectRoleOnly ):
	"""
	ֻ�Եж������Ч
	"""
	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
			
		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_ROLE:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW
			
		if caster.queryRelation( target.getObject() ) != csdefine.RELATION_ANTAGONIZE:
			return csstatus.SKILL_NOT_ENEMY_ENTITY
			
		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )
		
class ReceiverObjectEnemy( ReceiverObjectEntity ):
	"""
	���ö����ǿɹ�������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not self.isEnemy( caster, target.getObject() ):
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def isEnemy( self, caster, receiver ):
		"""
		�Ƿ����
		"""
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE

class ReceiverObjectEnemyRandom( ReceiverObjectEnemy ):
	"""
	�����ǿɹ�������������������������ɹ�������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEnemy.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEnemy.init( self, dict )

class ReceiverObjectNotAttack( ReceiverObjectEntity ):
	"""
	���ö����ǲ��ɹ���entity(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not self.isNotFight( caster, target.getObject() ):
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def isNotFight( self, caster, receiver ):
		"""
		�ɷ񹥻�
		"""
		return ( not hasattr(receiver,"canFight") and not receiver.canFight() ) or caster.id == receiver.id

class ReceiverObjectNotEnemyRole( ReceiverObjectEntity ):
	"""
	���ö����ǷǵжԵ����(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not target.getObject().isEntityType( csdefine.ENTITY_TYPE_ROLE ) or self.isEnemy( caster, target.getObject() ):
				return csstatus.SKILL_TARGET_IS_ENEMY_ROLE
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

	def isEnemy( self, caster, receiver ):
		"""
		�Ƿ����
		"""
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE

class ReceiverObjectItem( ReceiverObjectBase ):
	"""
	���ö�������Ʒ����������
	"""
	def __init__( self, parent ):
		"""
		"""
		pass

	def init( self, dict ):
		"""
		��ʼ���ܴ������Ʒ����
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
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ITEM:
			# ֻ�ܶ���Ʒʩչ
			return csstatus.SKILL_CANT_ITEM_ONLY

		item = target.getObject()
		if item == None:
			# �Ҳ������ܷ�������Ʒ
			return csstatus.SKILL_ITEM_NOT_EXIST

		try:
			# ����һ����Ʒ
			if not isinstance( target.getObject(), items.CItemBase.CItemBase ):
				# �㲻�ܶԸ�Ŀ��ʹ�ô˼���
				return csstatus.SKILL_CAST_OBJECT_INVALID
			# ������ұ�������Ʒ
			if target.getObject().getUid() == -1:
				return csstatus.SKILL_CAST_OBJECT_INVALID
			if target.getObject().getType() in self._itemTypes:
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW
		# �㲻�ܶԸ�Ŀ��ʹ�ô˼���
		return csstatus.SKILL_CAST_OBJECT_INVALID

class ReceiverObjectSelfPet( ReceiverObjectEntity ):
	"""
	���ö������Լ��ĳ��� �൱������ ����ѡ��һ��Ŀ��(��������Բ�Σ���������...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return caster.pcg_getActPet()

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		target = caster.pcg_getActPet()
		# Ŀ��Ϸ����ж�
		if target is None:
			# �����ٻ�һ����������ʹ��
			return csstatus.SKILL_PET_NO_CONJURED

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
			#ȡ�����沿�֣� �Ͳ߻�������������Լ������Լ��ĳ���Ϊʩչ����ļ��ܲ���ȥ��Ӧ�Ե��ͷ�
			#skillID = self.parent.getID()
			#fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			#if fitSkillID == -1:
			#	return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target )

class ReceiverObjectPet( ReceiverObjectEntity ):
	"""
	���ö������κ�һ������ ��ѡ��һ��Ŀ��(��������Բ�Σ���������...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().getEntityType() != csdefine.ENTITY_TYPE_PET:
				return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectNPC( ReceiverObjectEntity ):
	"""
	���ö����ǹ���(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_NPC:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )


class ReceiverObjectNPCObject( ReceiverObjectEntity ):
	"""
	���ö�����NPCObject(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		try:
			if target.getObject().utype not in [csdefine.ENTITY_TYPE_NPC_OBJECT, csdefine.ENTITY_TYPE_QUEST_BOX, csdefine.ENTITY_TYPE_FRUITTREE]:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		return self._stateFunc( caster, target.getObject() )

	@staticmethod
	def isLive( caster, receiver ):
		"""
		�������Ƿ����
		"""
		return csstatus.SKILL_GO_ON

class ReceiverObjectVehicleDart( ReceiverObjectEntity ):
	"""
	���ö������ڳ�
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		if targetEntity:
			return targetEntity
		return caster

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None or target.getObject() is None:
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_VEHICLE_DART:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectSelfSlaveMonster( ReceiverObjectEntity ):
	"""
	���ö������Լ��Ĵ�������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		if targetEntity:
			return targetEntity
		return caster

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None or target.getObject() is None:
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if target.getObject().utype != csdefine.ENTITY_TYPE_SLAVE_MONSTER:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target.getObject() )

class ReceiverObjectOtherRole( ReceiverObjectEntity ):
	"""
	���ö��������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, targetWrap ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param targetWrap: ʩչ����
		@type  targetWrap: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if targetWrap is None or targetWrap.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		target = targetWrap.getObject()
		if targetWrap.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if ( target.utype != csdefine.ENTITY_TYPE_ROLE and target.utype != csdefine.ENTITY_TYPE_PET ) or \
				( caster.utype == csdefine.ENTITY_TYPE_ROLE and caster.pcg_getActPet() == target ) or \
				( caster.utype == csdefine.ENTITY_TYPE_PET and caster.getOwner() == target ) or \
				target == caster :
					return csstatus.SKILL_CAST_OBJECT_INVALID
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, target )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return targetEntity



class ReceiverObjectNPCOrMonster( ReceiverObjectEntity ):
	"""
	���ö����ǹ���(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition�����ļ�python dict
		"""
		ReceiverObjectEntity.init( self, dict )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		# Ŀ��Ϸ����ж�
		if target is None or target.getObject() is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if not target.getObject().utype in [ csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_YAYU ]:
				return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = target.getObject().getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = skills.binarySearchSKillID( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
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
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ONLY	: ReceiverObjectRoleOnly,	# ���������Ч�ļ��ܣ���������RECEIVER_CONDITION_ENTITY_ROLE
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ENEMY_ONLY	: ReceiverObjectRoleEnemyOnly,	# ���Եж������Ч
}

def newInstance( condition, parent ):
	"""
	������������
		@param objectType:	��������
		@type objectType:	INT32
	"""
	return g_reveiverCondition[condition]( parent )


