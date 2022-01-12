# -*- coding:gb18030 -*-

#edit by wuxo 2013-2-1

import Math
import math
import csdefine
import csarithmetic
import ECBExtend
import csstatus
from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import time

class Spell_Avoidance( Spell_BuffNormal ):
	"""
	�������ܼ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		#ʩ����λ������
		self.casterMoveDistance = 0.0	#��̾���
		self.casterMoveSpeed    = 0.0	#����ٶ�
		self._triggerBuffInterruptCode = []
		self.forbidUseBuffs = []  #���ϴ�����Щbuff������ֹʹ�ô˼���
		self.buffTimeBefore = -1
		self.buffTimeAfter  = -1
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		param1 = data["param1"].split(";")
		self.forbidUseBuffs = [ int( i ) for i in param1 ]	
		param2 = data["param2"].split(";")
		if len( param2 ) >= 2:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
		for val in data[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		if data["param3"] != "" :
			self.buffTimeBefore = int(data["param3"])
		if data["param4"] != "" :
			self.buffTimeAfter  = int(data["param4"])
		
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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		#����Ϊ�����ж� ��ӵ������buffʱ �޷��ͷ�
		for index, buff in enumerate( caster.attrBuffs ):
			if int(buff["skill"].getBuffID()) in self.forbidUseBuffs:
				return csstatus.SKILL_CANT_CAST
			#if int(buff["skill"].getBuffID()) == 108007:
				#leaveTime = buff["persistent"] - time.time()
				#disTime = buff["skill"]._persistent - leaveTime
				#if self.buffTimeBefore > 0 and self.buffTimeBefore >= disTime:
					#return csstatus.SKILL_CANT_CAST
				#if self.buffTimeAfter > 0 and self.buffTimeAfter <= disTime:
					#return csstatus.SKILL_CANT_CAST
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
		caster.interruptSpell( csstatus.SKILL_INTERRUPTED_BY_AVOIDANCE )	
		return csstatus.SKILL_GO_ON	
		
	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		caster.setTemp( "AVOIDANCE_FLAG", True ) #�����������ܱ�ʶ
		Spell_BuffNormal.cast( self, caster, target )
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.isDestroyed:
			return
		caster.clearBuff( self._triggerBuffInterruptCode ) #�ж�buff
		self.receiveLinkBuff( caster, receiver )	
		