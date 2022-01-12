# -*- coding: gb18030 -*-

#Ŀ��λ�ü���
#���༼������ʱ����Ŀ������λ��Ϊ����Ч����������λ��
#edit by wuxo 2012-3-20

import math
import Math
import copy
import random
import csdefine
import csstatus
from SpellBase import *
import csarithmetic
import SkillTargetObjImpl
from Spell_CastTotem import Spell_CastTotem



class Spell_TargetPosition( Spell_CastTotem ):
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_CastTotem.__init__( self )
		self._target = None
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_CastTotem.init( self, dict )
		
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# ʩ��������
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ʩ���߼��
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		
		if not target:
			dstPos = caster.position
		else:
			dstPos = target.getObjectPosition()
		dstPos = csarithmetic.getCollidePoint( caster.spaceID, dstPos+(0,5,0), dstPos-( 0,5,0 ) )
		self._target = copy.deepcopy(SkillTargetObjImpl.createTargetObjPosition(dstPos))
		
		caster.setTemp( "TARGETPOSITION", self._target )
		return csstatus.SKILL_GO_ON
		
	def use( self, caster, target ):
		"""
		virtual method.
		����� target/position ʩչһ���������κη�����ʩ������ɴ˽���
		dstEntity��position�ǿ�ѡ�ģ����õĲ�����None���棬���忴���������Ƕ�Ŀ�껹��λ�ã�һ��˷���������client����ͳһ�ӿں���ת������
		Ĭ��ɶ��������ֱ�ӷ��ء�
		ע���˽ӿڼ�ԭ���ɰ��е�cast()�ӿ�
		@param   caster: ʩ����
		@type    caster: Entity

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_CastTotem.use( self, caster, caster.queryTemp( "TARGETPOSITION", None ) )	
		
	def cast( self, caster, target ):
		Spell_CastTotem.cast( self, caster, caster.queryTemp( "TARGETPOSITION", None ) )
		caster.removeTemp( "TARGETPOSITION" )
		

class Spell_TargetPosRandom( Spell_TargetPosition ):
	"""
	Ŀ������λ��ΪԲ�İ뾶ΪR�����һ������ΪĿ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_TargetPosition.__init__( self )
		self._target = None
		self.randomRange = 0.0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_TargetPosition.init( self, dict )
		param =  dict[ "param3" ].split(";")[-1]
		if param != "":
			self.randomRange = float( param )
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# ʩ��������
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ʩ���߼��
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		
		if not target:
			dstPos = caster.position
		else:
			dstPos = target.getObjectPosition()
		radius = random.uniform( 0.0, self.randomRange )
		yaw    = random.uniform( 0.0, 2*math.pi )
		direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
		pos = dstPos + radius*direction
		pos = csarithmetic.getCollidePoint( caster.spaceID, pos+(0,5,0), pos-( 0,5,0 ) )
		self._target = copy.deepcopy(SkillTargetObjImpl.createTargetObjPosition( pos ))
		
		caster.setTemp( "TARGETPOSITION", self._target )
		return csstatus.SKILL_GO_ON
		
	