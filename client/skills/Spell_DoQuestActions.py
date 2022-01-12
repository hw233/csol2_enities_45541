# -*- coding: gb18030 -*-
#
#
import csstatus
from SpellBase import Spell
from gbref import rds
from Function import Functor
import BigWorld
import Const

class Spell_DoQuestActions( Spell ):
	"""
	�������ָ�����񣬲�ִ����ض���
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"] != "":
			self.param1 = [ int(i) for i in dict["param1"].split("|")]
		else:
			self.param1 = []

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		target = targetObject.getObject()
		player = BigWorld.player()
		if target.id !=  player.id:
			return
		
		player.changeAttackState( Const.ATTACK_STATE_NONE )
		rds.cameraEventMgr.triggerByClass( self.param1 )
		model = caster.getModel()
		if model:
			model.visible = False
		rds.targetMgr.unbindTarget( None )
		