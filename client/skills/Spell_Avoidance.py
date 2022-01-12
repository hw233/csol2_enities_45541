# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
from gbref import rds
from Time import Time

class Spell_Avoidance( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.casterMoveDistance = 0.0	#��̾���
		self.casterMoveSpeed    = 0.0	#����ٶ�
		self.forbidUseBuffs = []
		self.buffTimeBefore = -1
		self.buffTimeAfter  = -1
		
	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) >= 2:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
		param1 = data["param1"].split(";")
		self.forbidUseBuffs = [ int( i ) for i in param1 ]
		if data["param3"] != "" :
			self.buffTimeBefore = int(data["param3"])
		if data["param4"] != "" :
			self.buffTimeAfter  = int(data["param4"])
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if hasattr( caster, "state" ):
			if caster.state == csdefine.ENTITY_STATE_DEAD:	# ��ʩ�����Ƿ��������ж�
				return csstatus.SKILL_IN_DEAD
		
		#����Ϊ�����ж� ��ӵ������buffʱ �޷��ͷ�
		for index, buff in enumerate( caster.attrBuffs ):
			if int(buff["skill"].getBuffID()) in self.forbidUseBuffs:
				return csstatus.SKILL_CANT_CAST
			#if int(buff["skill"].getBuffID()) == 108007:
				#leaveTime = buff["persistent"] - Time.time()
				#disTime = buff["skill"].getPersistent() - leaveTime
				#if self.buffTimeBefore > 0 and self.buffTimeBefore >= disTime:
					#return csstatus.SKILL_CANT_CAST
				#if self.buffTimeAfter > 0 and self.buffTimeAfter <= disTime:
					#return csstatus.SKILL_CANT_CAST
			
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

		# ��鼼��cooldown ���ݿ������ɫ��������������������ж�˳�� ���ֻ�ܷ����
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		#if caster.isInHomingSpell:
		#	return csstatus.SKILL_CANT_CAST
		
		
		return csstatus.SKILL_GO_ON
	
	def cast( self, caster, targetObject ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		if caster.id == BigWorld.player().id:
			caster.stopMove()
		Spell.cast( self, caster, targetObject )
		