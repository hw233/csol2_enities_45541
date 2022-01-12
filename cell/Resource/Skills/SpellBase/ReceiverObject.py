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
		spell��ĳ��condition����dictDat
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

	def validReceiver( self, caster, receiver ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		return csstatus.SKILL_GO_ON

	def getReceivers( self, caster, target ):
		"""
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: �ܻ���
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		return []

	def convertCastObject( self, caster, target ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: �ܻ���
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		return target

class ReceiverObjectEntity( ReceiverObjectBase ):
	"""
	���ö�����entity
	"""
	def __init__( self, parent ):
		ReceiverObjectBase.__init__( self, parent )
		# ������������ �������������� ��ͼ�����߼����֧��.
		self._receiveCountMax = 1
		self._stateFunc = self.isLive
		self._area = AreaDefine.newInstance( csdefine.SKILL_SPELL_AREA_SINGLE, self.parent )	# see also AreaDefine; Ĭ��Ϊ���壬���Բ���Ҫload()

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����dictDat
		"""
		if dictDat[ "Dead" ] == 1:
			self._stateFunc = self.isDead

		if dictDat.has_key( "Area" ):
			self._area = AreaDefine.newInstance( dictDat[ "Area" ], self.parent )								# �������򣺵���(0)��Բ(1)��ֱ��(2)
			self._area.load( dictDat )
		try:
			self._receiveCountMax = dictDat[ "ReceiveCountMax" ]
		except:
			self._receiveCountMax  = 0

	def getReceiveObjCountMax( self ):
		"""
		virtual method.
		��ȡ����entity��������
		"""
		return self._receiveCountMax

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
			if not receiver.state == csdefine.ENTITY_STATE_DEAD:
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
			if receiver.state == csdefine.ENTITY_STATE_DEAD:
				return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# ֻ������󣬵���Ȼ��Ч���õ�Ҫ�󲻷��ϵĽ��
			# ԭ�������������Ʒ��һ���entity�ǲ����У�����������û�У�isDead()������
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
		�ж�Ŀ���Ƿ���Ч
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if receiver.getEntityType() in RULE_OUT_TARGET:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		return self._validReceiver( caster, receiver )

	def filterReceiver( self, caster, receivers ):
		"""
		ɸѡ�����кϷ���
		@param   caster: ʩ����
		@type    caster: Entity
		@param receivers: �ܻ���
		@type  receivers: list of Entity
		"""
		wrapReceivers = []

		for e in receivers:
			if self.validReceiver( caster, e ) == csstatus.SKILL_GO_ON:
				#�������߰�װ
				wrapReceivers.append( e )
				if self._receiveCountMax > 0 and len( wrapReceivers ) >= self.getReceiveObjCountMax():
					break # ���������������򲻼���Ѱ��
		return wrapReceivers

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: �ܻ���
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py

		@rtype: list of Entity
		"""
		receivers = self._area.getObjectList( caster, target )
		return self.filterReceiver( caster, receivers )

	def convertCastObject( self, caster, target ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: �ܻ���
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		return target

class ReceiverObjectInfection( ReceiverObjectEntity ):
	"""
	���ö�����ʩչ������������η�Χ�ڹ�����һ������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )
		self._rate = 0  														#���� ʩչ����35%�������η�Χ�������һ���ɹ�������
		self._extraInfectionCount = 0   										#�˼���rate���ʻ�����Ⱦָ����Χ��N��Entity  ������һ��Ӧ���ڵ��幥������

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat )
		#���ʩչ����35%�������η�Χ�������һ���ɹ�������
		self._rate = dictDat["Area"]["rate"]  #float   #!!!notice��ò��������Ѿ����ã�skill.def ��key:"rate" ������
		self._extraInfectionCount = dictDat["Area"]["infectionCount"]  #Int
		self._randomArea = AreaDefine.newInstance( dictDat["Area"][ "Area" ], self.parent )				# �������򣺵���(0)��Բ(1)��ֱ��(2)
		self._randomArea.load( dictDat["Area"] )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: �ܻ���
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py

		@rtype: list of Entity
		"""

		#ȡʩչ����x%�������η�Χ�������N���ɹ�������
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
	���ö������Լ�(��������Բ�Σ���������...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat)

	def getReceiveObjCountMax( self ):
		"""
		virtual method.
		��ȡ����entity��������
		"""
		return 1

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		if ( not caster.inHomingSpell() ) and caster.id != receiver.id:
			return csstatus.SKILL_NOT_SELF_ENTITY

		""" ���Լ�ΪĿ��ļ��ܲ�Ӧ���м����ж�
		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
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
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

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

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		�жϸ�entity�Ƿ���Խ��ܸ÷���
		@param caster:ʩ����
		@param receiver:������ Ҫ���caster��һ������
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		if ( caster.utype == receiver.utype and \
			caster.isInTeam() and \
			receiver.isInTeam() and \
			receiver.spaceID == caster.spaceID and \
			caster.teamMailbox.id == receiver.teamMailbox.id ) or caster.id == receiver.id:

			#�����ж�
			lvMin = self.parent.getCastTargetLevelMin()
			lvMax = self.parent.getCastTargetLevelMax()
			targetLv = receiver.getLevel()

			if lvMin > 0 and targetLv < lvMin :
				# ʩչĿ�꼶��̫����
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
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET


		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

class ReceiverObjectMonster( ReceiverObjectEntity ):
	"""
	���ö����ǹ���(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����dictDat
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		if receiver.utype != csdefine.ENTITY_TYPE_MONSTER or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_MONSTER_ENTITY

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""

		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		if tObject.utype != csdefine.ENTITY_TYPE_MONSTER:
			return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER
		return self._validReceiver( caster, tObject )

class ReceiverObjectRole( ReceiverObjectEntity ):
	"""
	���ö��������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_NOT_ENEMY_ENTITY
		#�����ʹ�õļ��ܾͿɶԳ���ʹ��,Ҳ�ɶ��̹��ػ�ʹ��
		if ( receiver.utype != csdefine.ENTITY_TYPE_ROLE and receiver.utype != csdefine.ENTITY_TYPE_PET and receiver.utype != csdefine.ENTITY_TYPE_PANGU_NAGUAL ):
			return csstatus.SKILL_NOT_ROLE_ENTITY

		if receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NO_RECEIVER

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

class ReceiverObjectRoleOnly( ReceiverObjectRole ):
	"""
	���ö��������(���壬Բ�Σ�����...)����������

	֮ǰ���ڹ������ж������Ч�ļ��ܶԳ���Ҳ��Ч��
	������Ҫ�н��������Ч�ļ��ܣ�����ReceiverObjectRole�Ѿ����������ã�����޸Ŀ��ܻ���ɴ�������
	�����Ӵ�������Ϊ���������Ч��������������
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

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

class ReceiverObjectRoleEnemyOnly( ReceiverObjectRoleOnly ):
	"""
	ֻ�Եж������Ч
	"""
	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if caster.queryRelation( receiver ) != csdefine.RELATION_ANTAGONIZE:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		return ReceiverObjectRoleOnly._validReceiver( self, caster, receiver )

class ReceiverObjectEnemy( ReceiverObjectEntity ):
	"""
	���ö����ǿɹ�������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or ( not self.isEnemy( caster, receiver ) ) or receiver.spaceID != caster.spaceID :
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		�Ƿ����
		"""
		#ERROR_MSG( "--> Here must change.�ǵ����Ѳ�����ô�жϵġ�" )
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		#return receiver.utype in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_ROLE ] and ( hasattr(receiver,"canFight") and receiver.canFight() )

class ReceiverObjectEnemyRandom( ReceiverObjectInfection ):
	"""
	�����ǿɹ�������������������������ɹ�������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectInfection.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectInfection.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or not self.isEnemy( caster, receiver ) or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_ENEMY_ENTITY

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		�Ƿ����
		"""
		#ERROR_MSG( "--> Here must change.�ǵ����Ѳ�����ô�жϵġ�" )
		#print "isEnemy--->>>",caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		#return ( receiver.utype == csdefine.ENTITY_TYPE_MONSTER or receiver.utype == csdefine.ENTITY_TYPE_NPC ) and ( hasattr(receiver,"canFight") and receiver.canFight() )

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

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or ( not receiver.getObject().isEntityType( csdefine.ENTITY_TYPE_ROLE ) ) or \
			self.isEnemy( caster, receiver ) or receiver.spaceID != caster.spaceID :
			return csstatus.SKILL_TARGET_IS_ENEMY_ROLE

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		�Ƿ����
		"""
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE

class ReceiverObjectNotAttack( ReceiverObjectEntity ):
	"""
	���ö����ǲ��ɹ���entity(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed or self.isEnemy( caster, receiver ) or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_IS_ENEMY_ENTITY

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()

		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN

		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX

		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

	def isEnemy( self, caster, receiver ):
		"""
		�Ƿ����
		"""
		#ERROR_MSG( "--> Here must change.�ǵ����Ѳ�����ô�жϵġ�" )
		#print "isEnemy--->>>",caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		return caster.queryRelation( receiver ) == csdefine.RELATION_ANTAGONIZE
		#return ( receiver.utype == csdefine.ENTITY_TYPE_MONSTER or receiver.utype == csdefine.ENTITY_TYPE_NPC ) and ( hasattr(receiver,"canFight") and receiver.canFight() )

class ReceiverObjectItem( ReceiverObjectBase ):
	"""
	���ö�������Ʒ����������
	"""
	def __init__( self, parent ):
		"""
		"""
		pass

	def init( self, dictDat ):
		"""
		��ʼ���ܴ������Ʒ����
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
		�жϸ���Ʒ�Ƿ���Խ��ܷ���
		�����receiverʵ������һ�� Item ֮��������������Ϊ�˲��ƻ���������������еĽ�������
		����һ��entity����Ʒ����һ��entity��������������Ʒ�������յĽ�����
		@param caster:ʩ����
		@param receiver:���ս��ܷ�������ұ����е���Ʒʵ��
		"""
		# ����һ����Ʒ
		if not isinstance( item, items.CItemBase.CItemBase ):
			return csstatus.SKILL_CANT_ITEM_ONLY
		# ������ұ�������Ʒ
		if item.getUid() == -1:
			return csstatus.SKILL_ITEM_NOT_IN_BAG
		if item.getType() in self._itemTypes:
			return csstatus.SKILL_GO_ON
		# ���ܶԸ���Ʒʹ��
		return csstatus.SKILL_CANT_CAST_ITEM

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET
		if target.type != csdefine.SKILL_TARGET_OBJECT_ITEM:
			# ֻ�ܶ���Ʒʩչ
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
		�ж�Ŀ���Ƿ���Ч
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		#�뿴 Spell_SpellToItem.py  receive
		uid = receiver.queryTemp( "spellItem_uid", -1 )

		item = receiver.getItemByUid_( uid )
		if item is None:
			return csstatus.SKILL_ITEM_NOT_IN_BAG

		return self._validReceiver( caster, item )

	def getReceivers( self, caster, target ):
		"""
		��ȡ���е��ڷ�Χ�ڵ�entity�б�
		@param target: �ܻ���
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: list of entity
		"""
		#��Ϊtarget���Ǳ���װ��һ��item��������ֱ�ӷ���
		if target.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = target.getOwner()
			if owner.etype == "MAILBOX" :
				return []
			return [owner.entity]
		return  []

class ReceiverObjectSelfPet( ReceiverObjectEntity ):
	"""
	���ö������Լ��ĳ��� �൱������ ����ѡ��һ��Ŀ��(��������Բ�Σ���������...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
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

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
			#ȡ�����沿�֣� �Ͳ߻�������������Լ������Լ��ĳ���Ϊʩչ����ļ��ܲ���ȥ��Ӧ�Ե��ͷ�
			#skillID = self.parent.getID()
			#fitSkillID = binarySearch( targetLv, skillID )
			#if fitSkillID == -1:
			#	return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		actPet = caster.pcg_getActPet()
		# Ŀ��Ϸ����ж� �����ٻ�һ����������ʹ��
		if actPet is None or actPet.etype == "MAILBOX" or actPet.entity is None or actPet.entity.isDestroyed:
			return csstatus.SKILL_PET_NO_CONJURED
		return self._validReceiver( caster, actPet.entity )

	def validReceiver( self, caster, receiver ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		return self._validReceiver( caster, receiver )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: �ܻ���
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py

		@rtype: list of Entity
		"""
		actPet = caster.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX":
			return [ actPet.entity ]
		return []

class ReceiverObjectPet( ReceiverObjectEntity ):
	"""
	���ö������κ�һ������ ��ѡ��һ��Ŀ��(��������Բ�Σ���������...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY
		if receiver.getEntityType() != csdefine.ENTITY_TYPE_PET:
			return csstatus.SKILL_MISSING_NOT_PET
		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX

		return self._stateFunc( caster, receiver )

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

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

class ReceiverObjectNPC( ReceiverObjectEntity ):
	"""
	���ö����ǹ���(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY

		if receiver.utype != csdefine.ENTITY_TYPE_NPC or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_MONSTER_ENTITY

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

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

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )


class ReceiverObjectNPCObject( ReceiverObjectEntity ):
	"""
	���ö����ǳ���NPC(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
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

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )

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

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

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
		# Ŀ��Ϸ����ж�
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if tObject.utype != csdefine.ENTITY_TYPE_VEHICLE_DART:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = tObject.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, tObject )

class ReceiverObjectSelfSlaveMonster( ReceiverObjectEntity ):
	"""
	���ö������Լ��Ĵ�������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

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
		# Ŀ��Ϸ����ж�
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET


		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY

		try:
			if tObject.utype != csdefine.ENTITY_TYPE_SLAVE_MONSTER or tObject.utype != csdefine.ENTITY_TYPE_PANGU_NAGUAL:
				return csstatus.SKILL_CAST_OBJECT_NOT_ENEMY
		except AttributeError, errstr:
			# �����������һ���ǿͻ���δ��ʼ����һ��entity, ׼ȷ˵��δ�յ������������԰���
			# �����´˿�û���������
			ERROR_MSG( errstr )
			return csstatus.SKILL_UNKNOW

		# �����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = tObject.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			# ʩչĿ�꼶��̫����
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, tObject )

class ReceiverObjectOtherRole( ReceiverObjectEntity ):
	"""
	���ö��������(���壬Բ�Σ�����...)����������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:								# ����������
			return csstatus.SKILL_IS_ENEMY_ENTITY
		if receiver == caster :									# ���Լ�ʩ��
			return csstatus.SKILL_CAST_OBJECT_INVALID
		if receiver.utype != csdefine.ENTITY_TYPE_ROLE and \
			receiver.utype != csdefine.ENTITY_TYPE_PET :		# ����Ŀ��
				return csstatus.SKILL_CAST_OBJECT_INVALID
		if caster.utype == csdefine.ENTITY_TYPE_ROLE :
			actPet = caster.pcg_getActPet()
			if actPet and actPet.entity.id == receiver.id :		# ���Լ�����ʩ��
				return csstatus.SKILL_CAST_OBJECT_INVALID
		if caster.utype == csdefine.ENTITY_TYPE_PET and \
			caster.getOwner().entity.id == receiver.id :		# ������Լ�����ʩ��
				return csstatus.SKILL_CAST_OBJECT_INVALID

		if receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NO_RECEIVER

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

	def validCastObject( self, caster, target ):
		"""
		�ж�Ŀ���Ƿ���Ч
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		if target is None:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
			return csstatus.SKILL_CAST_ENTITY_ONLY
		return self._validReceiver( caster, tObject )


class ReceiverObjectNPCOrMonster( ReceiverObjectEntity ):
	"""
	���ö�����NPC���߹������������
	"""
	def __init__( self, parent ):
		"""
		"""
		ReceiverObjectEntity.__init__( self, parent )

	def init( self, dictDat ):
		"""
		virtual method.
		spell��ĳ��condition����
		"""
		ReceiverObjectEntity.init( self, dictDat )

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		if receiver.isDestroyed:
			return csstatus.SKILL_IS_ENEMY_ENTITY

		if not receiver.utype in [ csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_YAYU ] or receiver.spaceID != caster.spaceID:
			return csstatus.SKILL_NOT_MONSTER_ENTITY

		#�����ж�
		lvMin = self.parent.getCastTargetLevelMin()
		lvMax = self.parent.getCastTargetLevelMax()
		targetLv = receiver.getLevel()
		if lvMin > 0 and targetLv < lvMin :
			# ʩչĿ�꼶��̫����
			skillID = self.parent.getID()
			fitSkillID = binarySearch( targetLv, skillID )
			if fitSkillID == -1:
				return csstatus.SKILL_CAST_ENTITY_LEVE_MIN
		if lvMax > 0 and targetLv > lvMax :
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return self._stateFunc( caster, receiver )

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

		tObject = target.getObject()

		if tObject is None or tObject.isDestroyed:
			# ��ѡ��һ��Ŀ��
			return csstatus.SKILL_NO_TARGET

		if target.type != csdefine.SKILL_TARGET_OBJECT_ENTITY:
			# ��Ч��Ŀ��2
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
		self.quests = [int(qid) for qid in dictDat["value1"].split()]  	#�����б�

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		state = ReceiverObjectRoleOnly._validReceiver(self, caster, receiver)
		if state != csstatus.SKILL_GO_ON:
			return state

		# �������Ҫ�󣬱�����ָ��������������
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
		self.quests = [int(qid) for qid in dictDat["value1"].split()]  	#�����б�

	def _validReceiver( self, caster, receiver ):
		"""
		"""
		state = ReceiverObjectRoleOnly._validReceiver(self, caster, receiver)
		if state != csstatus.SKILL_GO_ON:
			return state

		# �������Ҫ�󣬱�����ָ��������������
		for questID in self.quests:
			if receiver.has_quest(questID) and not receiver.questIsCompleted(questID):
				return csstatus.SKILL_GO_ON

		return csstatus.SKILL_CAST_OBJECT_INVALID


g_reveiverCondition = {
	csdefine.RECEIVER_CONDITION_ENTITY_NONE			:	ReceiverObjectBase,
	csdefine.RECEIVER_CONDITION_ENTITY_SELF			:	ReceiverObjectSelf,
	csdefine.RECEIVER_CONDITION_ENTITY_TEAMMEMBER	:	ReceiverObjectTeam,
	csdefine.RECEIVER_CONDITION_ENTITY_MONSTER		:	ReceiverObjectMonster,
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE			:	ReceiverObjectRole,	# �������Ч�ļ���Ҳ�ܶԳ�����Ч
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
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ONLY	: ReceiverObjectRoleOnly,	# ���������Ч�ļ��ܣ���������RECEIVER_CONDITION_ENTITY_ROLE
	csdefine.RECEIVER_CONDITION_ENTITY_ROLE_ENEMY_ONLY	: ReceiverObjectRoleEnemyOnly,	# ���Եж������Ч
	csdefine.RECEIVER_CONDITION_ROLE_WITH_COMPLETED_QUESTS	: ReceiverObjectRoleWithCompletedQuests, # Ŀ���������ָ����������
	csdefine.RECEIVER_CONDITION_ROLE_HAS_UNCOMPLETED_QUESTS	: ReceiverObjectRoleHasUnCompletedQuests, # Ŀ���������ָ����������
}

def newInstance( condition, parent ):
	"""
	������������
		@param objectType:	��������
		@type objectType:	INT32
	"""
	return g_reveiverCondition[condition]( parent )


def binarySearch( playerLv, skillID ):	# 15:00 2008-11-24,wsf
	"""
	2�ֲ����ʺ�playerLv�ļ���id

	@param playerLv : ��Ҽ���
	@type playerLv : UINT8
	@param skillID : �ߵȼ�����
	@type skillID : INT64
	"""
	from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA
	headString = str( skillID )[:-3]		# ��ü���id�ĵ�һ��
	tailInt = int( str( skillID )[-3:] )	# ��ü��ܵļ���
	min = 001
	max = tailInt
	fitSkillID = -1
	while min <= max:
		mid = ( min + max ) / 2
		midStr = str( mid )
		while len( midStr ) < 3:	# ����3λ�Ͳ�0
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


