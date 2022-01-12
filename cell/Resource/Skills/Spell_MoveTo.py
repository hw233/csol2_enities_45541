# -*- coding: gb18030 -*-
#

import Math
import math
import BigWorld
import ECBExtend
import random
from SpellBase import *
import csstatus
import csdefine


class Spell_MoveTo( Spell ):
	"""
	# �ƶ���Ŀ����Χһ����Χ��
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.param1 = float( dict[ "param1" ] )  # param1,��Ŀ��ľ���
		if dict[ "param2" ]:
			self.param2 = float( dict[ "param2" ] )	 # param2,�ƶ��ٶ�
			
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
		#����ѣ�Ρ�������˯��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )
	
	def cast( self, caster, target ):
		"""
		"""
			
		count = 10
		pos = None
		if hasattr( self, "param2" ):
			caster.move_speed = self.param2
			caster.updateTopSpeed()
		targetEntity = target.getObject()
		for tryNum in xrange( count ):
			a = self.param1 + ( caster.getBoundingBox().z + targetEntity.getBoundingBox().z ) / 3.0
			# ѡȡ��Բ���ϵĵ�
			targetPos =  target.getObjectPosition()
			yaw = ( caster.position - targetPos ).yaw
			angle = random.uniform( yaw - math.pi/2, yaw + math.pi / 2 )
			direction = Math.Vector3( math.sin( angle ), 0.0, math.cos( angle ) )
			direction.normalise()					# ��������λ��
			pos = Math.Vector3( targetPos ) + a * direction

			posList = BigWorld.collide( caster.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
			if not posList:
				continue
			caster.gotoPosition( pos )
			if hasattr( self, "param2" ):
				pos_temp = ( pos - caster.position ).length
				delayTime = pos_temp / caster.move_speed
				caster.addTimer( delayTime, 0, ECBExtend.CHARGE_SPELL_CBID )
			break
		Spell.cast( self, caster, target )
		