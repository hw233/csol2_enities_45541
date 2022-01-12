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
import csarithmetic
import Math
import math
from Function import Functor 
from gbref import rds

class Spell_Dance( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.danceAction = None



	def init( self, dict ):
		"""
		"""
		Spell.init( self, dict )
		self.danceAction = dict["param1"]  


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
		"""
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
		"""
		# �������Ƿ��ھ��������������GM�۲���״̬
		player = BigWorld.player()
		if caster == player:
			if caster.isDeadWatcher() or caster.isGMWatcher():
				return csstatus.SKILL_NOT_IN_POSTURE

		# ��鼼��cooldown ���ݿ������ɫ��������������������ж�˳�� ���ֻ�ܷ����
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		"""
		if caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		"""
		return csstatus.SKILL_GO_ON

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		pass
		

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		print "Spell_Dance caster is ",caster, "targetObject is ", targetObject
		if caster.__class__.__name__ == "PlayerRole":
			rds.actionMgr.playActions( caster.getModel(), [self.danceAction,], callbacks = [ caster.finishSkillPlayAction ])
		elif caster.__class__.__name__ == "DanceNPC": #ʩ������NPC
			rds.actionMgr.playActions( caster.getModel(), [self.danceAction,], callbacks = [ caster.cell.finishPlayAction ])
	




