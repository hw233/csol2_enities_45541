# -*- coding: gb18030 -*-

#����Ч���ƶ��༼��
#��������������Ч����������һ�κ���ʧ�����������ã���
#�������ü����ͷŽǶȣ��Ե�ǰĿ��Ϊ��׼���������������ʹ�ã�
#edit by wuxo 2012-3-20

import math
import Math
import utils
import csdefine
import csstatus

import SkillTargetObjImpl
from SpellBase import *
from Spell_CastTotem import Spell_CastTotem



class Spell_MoveEffect( Spell ):
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self._target = None
		self._direction = None
		self._isOnce = None 	#�Ƿ���һ�����˺�����,������һ��Ŀ��ͱ��ƣ�Ȼ���ܽ���
		self._offsetYaw = 0
		self.skillID = 0
		self.lastPosition = (0,0,0)
		self.everyDis = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.skillID = int( dict[ "param1" ] )
		if dict[ "param2" ] != "":
			self._offsetYaw = float( dict[ "param2" ] )
		else:
			self._offsetYaw = 0.0
		self._isOnce = bool( int( dict[ "param3" ] ) )
		self.everyDis = dict["ReceiverCondition"]["value2"]
		
		
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
		
		#���¼��㳯��
		postion = target.getObjectPosition()
		if caster.position.flatDistTo( postion ) > 0.0:
			y = utils.yawFromPos( caster.position, postion )
			
		else:
			y = caster.yaw
			
		y += self._offsetYaw
		self._direction = Math.Vector3( math.sin(y), 0, math.cos(y) )
		self._direction.normalise()
		
		dPos = caster.position + self._direction * self._rangeMax
		
		self._target = SkillTargetObjImpl.createTargetObjPosition(dPos)
			
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
		Spell.use( self, caster, self._target )	
		
		
	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		target = self._target
		# �������ܼ��
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		
		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )
		
		self.lastPosition = caster.position + self._direction*self._rangeMax
		t0 = self.everyDis/self._speed
		n = self._rangeMax / self.everyDis
		n = int( math.ceil(n) )
		for i in range( 1, n + 1 ):
			delay = (i - 1) * t0
				
			dPos = caster.position + self._direction * delay * self._speed
			target0 = SkillTargetObjImpl.createTargetObjPosition(dPos)
			
			if delay <= 0.1:
				# ˲��
				caster.addCastQueue( self, target0, 0.1 )
			else:
				# �ӳ�
				caster.addCastQueue( self, target0, delay )
		caster.setTemp( "MOVE_EFFECT_DIS", self._rangeMax )
		
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		if (target.getObjectPosition() - self.lastPosition).length < 0.1:
			caster.removeTemp( "MOVE_EFFECT_DIS" )
		for e in receivers:
			caster.spellTarget( self.skillID , e.id )
			if self._isOnce:
				caster.cancelSpellMoveEffect( caster.id, self.getID() )
		
		
		