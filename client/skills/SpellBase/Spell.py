# -*- coding: gb18030 -*-
#
# $Id: Spell.py,v 1.48 2008-08-26 08:00:56 yangkai Exp $

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from Function import Functor
import csdefine
import csstatus
import csconst
import GUIFacade
from event.EventCenter import *
from csdefine import *
from SkillBase import SkillBase
from Buff import Buff
from SmartImport import smartImport
import ObjectDefine
import AreaDefine
import RequireDefine
from CasterCondition import CasterCondition
import ReceiverObject
import skills
import event.EventCenter as ECenter
from gbref import rds
from Time import Time
import time
import Const
from interface.CombatUnit import CombatUnit
from config.client.NpcSkillName import Datas as npcSkillName

class Spell( SkillBase ):
	"""
	��������ģ��
	"""
	def __init__( self ):
		"""
		����SkillBase
		"""
		SkillBase.__init__( self )
		self._casterCondition = CasterCondition()					# ʩ���߿���ʩ����Ҫ��(�ж�һ��ʩ�����Ƿ���ʩչ�������)
		self._receiverObject = ReceiverObject.newInstance( 0, self )# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._require = RequireDefine.newInstance( None )			# see also RequireDefine; ʩ�ŷ������ĵĶ���; Ĭ��Ϊ"None"��������
		self._buffLink	= []										# ���ܲ�����BUFF [buffInstance...]
		self._effectState = 0										# Ŀǰ���弼���ƺ����Ƕ��Ե� ��˵�ǰ��ôд��
		self.isNotRotate = False									# ʩ���Ƿ���Ҫת��
		self.target = None

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type  dict:			python dict
		"""
		SkillBase.init( self, dict )
		# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self.getCastObjectType(), self )
		self._castObject.init( dict[ "CastObjectType" ] )
		self.isNotRotate = dict.get( "isNotRotate", 0 )

		# ʩ������
 		if len( dict[ "Require" ] ) > 0: #list
			self._require = RequireDefine.newInstance( dict["Require"] )		# ʩ�ŷ������ĵĶ���

		if len( dict[ "CasterCondition" ] ) > 0: #dict
			self._casterCondition.init( dict["CasterCondition"] )

		if len( dict[ "ReceiverCondition" ] ) > 0: #dict
			conditions = dict["ReceiverCondition"][ "conditions" ]
			if len( conditions ) > 0:
				self._receiverObject = ReceiverObject.newInstance( eval( dict["ReceiverCondition"][ "conditions" ] ), self )
				self._receiverObject.init( dict["ReceiverCondition"] )

		if dict.has_key( "buff" ): #list
			index = 0
			for datI in xrange( len( dict[ "buff" ] ) ):
				dat = dict[ "buff" ][datI]
				inst = None
				if len( dat[ "ClientClass" ] ) > 0:
					buffclass = "skills." + dat[ "ClientClass" ]
					inst = smartImport( buffclass )()
				else:
					inst = Buff()
				inst.init( dat )
				inst.setSource( self.getID(), index )
				self._buffLink.append( inst )
				skills.register( inst.getID(), inst )
				index += 1

	def isMalignant( self ):
		"""
		virtual method.
		�жϷ���Ч���Ƿ�Ϊ����
		����ӿڽ������������⣬  ��Ϊ��ǰ���弼�ܶ��Ƕ��Եģ� ����Ĭ���Ƕ��Եģ� ���
		��������������� BUFFȫ�������Ե� ��ô�����ı�Ϊ���ԣ� ���BUFF����һ���Ƕ��Ե� ��ô��������Ƕ��Եġ�
		"""
		effectState = self._datas[ "EffectState" ]
		return effectState in [ csdefine.SKILL_EFFECT_STATE_MALIGNANT, csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ]

	def isNeutral( self ):
		"""
		�Ƿ������Լ���
		"""
		return self._datas[ "EffectState" ] == csdefine.SKILL_EFFECT_STATE_NONE

	def getIntonateTime( self ):
		"""
		��øü��ܵĻ�������ʱ�䣨������������Ӱ�� ������Ҫ�ṩ������ʹ��
		@return:		�ͷ�ʱ��
		@rtype:			float
		"""
		return self._datas[ "IntonateTime" ]			# ����ʱ��
	
	def getReceiveDelayTime( self ):
		"""
		���Ƽ���ǰҡʱ��
		"""
		return self._datas.get( "receiveDelayTime", 0.0 )

	def getSpringOnUsedCD( self ):
		"""
		����ͷŸü�������CoolDown ʱ��
		"""
		return  self._datas[ "SpringUsedCD" ]

	def getSpringOnIntonateOverCD( self ):
		"""
		���_springOnIntonateOverCD
		"""
		return self._datas[ "SpringIntonateOverCD" ]

	def getLimitCooldown( self ):
		"""
		����ͷŸü�����������޼���
		"""
		return self._datas[ "LimitCD" ]

	def getRequire( self ):
		"""
		����ͷŸü�����������
		"""
		return self._require

	def getType( self ):
		"""
		@return: ��������
		"""
		if self._datas.has_key( "Type" ):
			return eval( 'csdefine.' + self._datas[ "Type" ] )
		return csdefine.BASE_SKILL_TYPE_NONE					# �������

	def getFlySpeed( self ):
		"""
		@return: �����ķ����ٶ�
		"""
		return self._datas[ "Speed" ]

	def getCastRange( self, role ):
		"""
		@return: �������ͷž���
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = role.magicSkillRangeVal_value
			val2 = role.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = role.phySkillRangeVal_value
				val2 = role.phySkillRangeVal_percent
			return ( self._datas[ "CastRange" ] + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return self._datas[ "CastRange" ]

	def getBuffLink( self ):
		"""
		@return: ���ܲ�����BUFF [buffInstance,...]
		"""
		return self._buffLink

	def getRangeMax( self, role ):
		"""
		�����̡�
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = role.magicSkillRangeVal_value
			val2 = role.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = role.phySkillRangeVal_value
				val2 = role.phySkillRangeVal_percent
			return ( self._datas[ "RangeMax" ] + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return self._datas[ "RangeMax" ]

	def getPosture( self ) :
		"""
		��ȡ����������̬
		"""
		for condition in self._casterCondition :
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_POSTURE :
				return condition.posture
		return SkillBase.getPosture( self )

	def calcExtraRequire( self, role ):
		"""
		virtual method.
		���㼼�����ĵĶ���ֵ�� ������װ�����߼���BUFFӰ�쵽���ܵ�����
		return : (�������ĸ���ֵ���������ļӳ�)
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = role.magicManaVal_value
			val2 = role.magicManaVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = role.phyManaVal_value
				val2 = role.phyManaVal_percent
			return ( val1, val2 / csconst.FLOAT_ZIP_PERCENT )
		return ( 0, 0.0 )

	def getRangeMin( self, caster ):
		"""
		virtual method.
		@param caster: ʩ���ߣ�ͨ��ĳЩ��Ҫ���������Ϊ����ķ����ͻ��õ���
		@return: ʩ����С����
		"""
		return self._datas[ "RangeMin" ]

	def isCooldownType( self, cooldownType ):
		"""
		�ж������Ƿ���ĳһ���͵�cooldown��ͬ

		@param cooldownType: cooldown����
		@type  cooldownType: INT
		@return: bool
		"""
		return cooldownType in self.getLimitCooldown()

	def isCooldown( self, caster ):
		"""
		�жϷ�����cooldown�Ƿ��ѹ�

		@return: BOOL
		"""
		for cd in self.getLimitCooldown():
			endTime = caster.getCooldown( cd )[3]
			if endTime > Time.time():	# getCooldown modified by hyw( 08.01.31 )
				return False
		return True

	def isHomingSkill( self ):
		"""
		�ж��Ƿ��������� 	by ����
		@return: BOOL
		"""
		return False
		
	def isMoveSpell( self ):
		"""
		�ж��Ƿ������������� by wuxo 2012-4-28
		@return: BOOL
		"""
		return False
	
	def isTriggerSkill( self ):
		"""
		�ж��Ƿ񴥷���������  add by wuxo 2012-2-20
		@return: BOOL
		"""
		return False
	
	def isNormalHomingSkill( self ):
		"""
		�ж��Ƿ�������ͨ�������� by wuxo
		@return: BOOL
		"""
		return False

	def isTargetPositionSkill( self ):
		"""
		�ж��Ƿ���λ�ù�Ч����
		@return: BOOL
		"""
		return False

	def getCooldownData( self, caster ):
		"""
		��ȡ�ü�������cooldown���������
		@return type: ( �������� cooldown ��ʼʱ��, �������� cooldown ����ʱ�� )
		modified by hyw( 08.01.31 )
		"""
		totalTime, endTime = 0, 0
		for cdID in self.getLimitCooldown() :
			cdData = caster.getCooldown( cdID )
			t = cdData[1]
			e = cdData[3]
			if e > Time.time() and e > endTime :
				totalTime, endTime = t, e
		return totalTime, endTime

	def getCastObjectType( self ):
		"""
		virtual method.
		ȡ�÷�����ʩ����Ŀ��������͡�

		@return: CAST_OBJECT_TYPE_*
		@rtype:  INT8
		"""
		return self._datas["CastObjectType"][ "type" ]

	def getCastObject( self ):
		"""
		virtual method.
		ȡ�÷�����ʩ����Ŀ������塣
		@rtype:  ObjectDefine Instance
		"""
		return self._castObject

	def getCastTargetLevelMin( self ):
		"""
		virtual method = 0.
		���ܿ�ʩչ������׼�
		"""
		return self._datas[ "CastObjLevelMin" ]

	def getCastTargetLevelMax( self ):
		"""
		virtual method = 0.
		���ܿ�ʩչ������߼�
		"""
		return self._datas[ "CastObjLevelMax" ]

	def _checkRequire( self, caster ):
		"""
		virtual method.
		��������Ƿ�

		@return: INT��see also csdefine.SKILL_*
		"""
		return self._require.validObject( caster, self )

	def validCaster( self, caster ):
		"""
		virtual method.
		�ж�ʩ�����Ƿ����ʩ��Ҫ��

		@return: INT��see also csdefine.SKILL_*
		"""
		if hasattr( caster, "state" ):
			if caster.state == csdefine.ENTITY_STATE_DEAD:	# ��ʩ�����Ƿ��������ж�д�ڽű������Ҫ���á�
				return csstatus.SKILL_IN_DEAD

		return self._casterCondition.valid( caster )

	def validTarget( self, caster, target ):
		"""
		virtual method.
		�ж�ʩ��Ŀ���Ƿ����ʩ��Ҫ��

		@return: INT��see also csdefine.SKILL_*
		"""
		return self._castObject.valid( caster, target )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		# ����Ƿ����ʩ��
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ) or caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_CANT_CAST
		elif self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ) or caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				 return csstatus.SKILL_CANT_CAST

		# ���ʩ���������Ƿ�����
		state = self.validCaster( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ����
		state = self.validTarget( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���ʩ���ߵ������Ƿ��㹻
		state = self._checkRequire( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		if caster.intonating():
			return csstatus.SKILL_INTONATING

		# �������Ƿ��ھ��������������GM�۲���״̬
		player = BigWorld.player()
		if caster == player:
			if caster.isDeadWatcher() or caster.isGMWatcher():
				return csstatus.SKILL_NOT_IN_POSTURE
				
		if hasattr( caster, "isInHomingSpell" ) and caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		if caster.effect_state & csdefine.EFFECT_STATE_BE_HOMING:
			return csstatus.SKILL_CANT_CAST

		# ��鼼��cooldown ���ݿ������ɫ��������������������ж�˳�� ���ֻ�ܷ����
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		
		return csstatus.SKILL_GO_ON

	def spell( self, caster, target ):
		"""
		�����������Spell����

		@param caster:		ʩ����Entity
		@type  caster:		Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		skillID = self.getID()
		sk_id = str( skillID )[:-3]	 # ȡǰ��λ�ж�
		if not sk_id: sk_id = "0"
		orgSkillID = int( sk_id )
		if BigWorld.player().id == caster.id and ( not orgSkillID in Const.JUMP_SPELL_SKILLS ) :	# ���⼼����Ծ�п�������ʩ�����������ƿյ�
			if caster.isJumping():		# ��Ծ�в���������ʩ��
				caster.statusMessage( csstatus.SKILL_ROLE_IS_JUMPING )
				return

		if hasattr( target.getObject(), "level" ) and self.getCastTargetLevelMin() > target.getObject().level:
			# ʩչĿ�꼶��̫����
			skillID = skills.binarySearchSKillID( target.getObject().level, self.getID() )
			if skillID != -1:
				tempSkill = skills.getSkill( skillID )
				caster.statusMessage( csstatus.SKILL_TARGET_ENTITY_LEVE_MIN_USE, tempSkill.getLevel(), tempSkill.getName() )

		caster.useSpell( skillID, target )
		if hasattr( caster, "showSpellingItemCover" ) :
			caster.showSpellingItemCover( self.getID() )

		if not self.isNotRotate:
			castObjectType = self.getCastObjectType()
			if castObjectType == 0:
				# ��Ŀ���λ��
				pass
			elif castObjectType == 1:
				# λ��
				self.rotate( caster, target.getObject() )
			elif castObjectType == 2:
				# Ŀ��Entity
				self.rotate( caster, target.getObject() )
			elif castObjectType == 3:
				# ����Ʒ
				self.rotate( caster, target.getOwner() )
			elif castObjectType == 4:
				# �Զ�Ŀ��Entity
				self.rotate( caster, target.getObject() )

	def rotate( self, caster, receiver ):
		"""
		ת������
		"""
		if caster.id == receiver.id:
			return
		#���˻�˯��ѣ�Ρ������Ч��ʱ�����Զ�ת��
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP |csdefine.EFFECT_STATE_BE_HOMING
		if caster.effect_state & EffectState_list != 0: return
		new_yaw = (receiver.position - caster.position).yaw
		# yaw������10��ʱ��ת��
		if abs( caster.yaw - new_yaw ) > 0.0:
			caster.turnaround( receiver.matrix, None )

	def interrupt( self, caster, reason ):
		"""
		��ֹʩ�ż��ܡ�
		@param caster:			ʩ����Entity
		@type caster:			Entity
		"""
		if reason not in [ csstatus.SKILL_INTONATING, csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY,csstatus.SKILL_CANT_CAST,csstatus.SKILL_INTERRUPTED_BY_TIME_OVER]  :
			if hasattr( caster, "hideSpellingItemCover" ) :
				caster.hideSpellingItemCover()
			caster.isInterrupt = True
			self.pose.interrupt( caster )
			rds.skillEffect.interrupt( caster )
			if caster.effect.has_key( self.getID() ):
				caster.effect.pop( self.getID() )
		if BigWorld.player().id == caster.id :
			caster.flushAction()

	def intonate( self, caster, intonateTime, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		"""
		caster.isInterrupt = False
		caster.hasCast = False
		skillID = self.getID()
		# ��������
		result = self.pose.intonate( caster, skillID, Functor( self.onStartActionEnd, caster, caster ) )
		if not result:
			self.onStartActionEnd( caster, caster )
		# ��Ч����
		rds.skillEffect.playBeginEffects( caster, targetObject, skillID )
		# ����������
		if BigWorld.player().id == caster.id :
			self.target = rds.targetMgr.getTarget()
			if self.getReceiveDelayTime() <= 0.1:
				lastTime = intonateTime
				GUIFacade.onSkillIntonate( lastTime )
			self.onCheckTarget()

	def onCheckTarget( self ):
		"""
		�������������߼��
		"""
		player = BigWorld.player()
		if player is None:
			self.target = None
			return
		if player.hasCast:
			self.target = None
			return
		if player.isInterrupt:
			self.target = None
			return
		if self.target is None:
			return
		# �����߲�����
		if not self.target.inWorld:
			self.target = None
			player.interruptAttack( csstatus.SKILL_TARGET_NOT_EXIST )
			return
		# ����������ЧĿ��
		if ( not self.target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.target.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ) ) or \
			self.target.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
				self.target = None
				player.interruptAttack( csstatus.SKILL_NO_TARGET )
				return
		# ������������
		if isinstance( self.target, CombatUnit ):
			if self.target.isDead():
				self.target = None
				player.interruptAttack( csstatus.SKILL_TARGET_DEAD )
				return
		BigWorld.callback( 0.1, self.onCheckTarget )

	def onStartActionEnd( self, caster, target ):
		"""
		�����������������Բ���ѭ�������Ĺ�Ч�ȡ�
		"""
		#DEBUG_MSG( "Spell", self.getName(), caster.id  )
		# ��Ϊ�첽�Ĺ�ϵ���п����ڲ���loopЧ����ʱ���յ����ж���Ϣ��
		# ��ʱ��ֱ���жϲ���loopЧ������
		if not caster.inWorld: return
		if caster.isInterrupt: return
		# ��Ϊ�첽�Ĺ�ϵ���п����ڲ���LoopЧ����ʱ��CastЧ���Ѿ�������
		# ��ʱ��ֱ���жϲ���loopЧ������
		if caster.hasCast: return
		self.pose.onStartActionEnd( caster )	# ֪ͨpose���ֶ����������
		
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		caster.hasCast = True
		skillID = self.getID()

		# �Զ������ԣ���ֻ�Ქ��һ��
		self.pose.cast( caster, skillID, targetObject )
		if hasattr( caster,"isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( rds.skillEffect.playCastEffects, caster, targetObject, skillID ) )
		else:
			rds.skillEffect.playCastEffects( caster, targetObject, skillID )

		# ����������ʾ
		speller = caster  #���¸�ֵ����ֹ������û���
		if hasattr( speller, 'getOwner' ):
			speller = speller.getOwner()

		player = BigWorld.player()
		if player is None: return
		if speller is None: return

		if player.position.distTo( speller.position ) > 20: return
		if hasattr( caster, "className" ):
			sk_id = str( skillID )[:-3]
			if not sk_id: return		# ���Ϊ�գ�ֱ�ӷ���
			orgSkillID = int( sk_id )	# ֧�����ñ�ɱ�ȼ�NPC������д
			skillIDs = npcSkillName.get( caster.className, [] )
			if orgSkillID in skillIDs or skillID in skillIDs:
		 		caster.showSkillName( skillID )
				return
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			caster.showSkillName( skillID )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		���ܲ����˺�ʱ�Ķ���Ч���ȴ���
		@param player:			����Լ�
		@type player:			Entity
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		@param caster:			Buffʩ���� ����ΪNone
		@type castaer:			Entity
		@param damageType:		�˺�����
		@type damageType:		Integer
		@param damage:			�˺���ֵ
		@type damage:			Integer
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return
		id = self.getID()
		if caster and damage != 0:
			self.pose.hit( id, target )
			rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )
