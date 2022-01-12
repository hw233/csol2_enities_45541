# -*- coding: gb18030 -*-
#
#
import csstatus
from SpellBase import Spell
from gbref import rds
from Function import Functor
import BigWorld
import Const

class Spell_FlyWater( Spell ):
	"""
	�貨΢���ͻ��˼���ģ��
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
		
		param2 = dict["param2"]
		if param2 == "":
			self.param2 = False
		else:
			self.param2 = True

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		player = BigWorld.player()
		target = targetObject.getObject()
		if target == player:
			player.changeAttackState( Const.ATTACK_STATE_NONE )
			rds.cameraEventMgr.triggerByClass( self.param1 )
			if self.param2:
				model = caster.getModel()
				model.visible = False
				rds.targetMgr.unbindTarget( None )
				

class Spell_FlyWaterAll( Spell_FlyWater ):
	"""
	�貨΢���ͻ��˼���ģ��(�����п��ĵ�����Ҷ��б���)
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )


	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		player = BigWorld.player()
		target = targetObject.getObject()
		player.changeAttackState( Const.ATTACK_STATE_NONE )
		rds.cameraEventMgr.triggerByClass( self.param1 )
		if self.param2:
			model = caster.getModel()
			model.visible = False
			rds.targetMgr.unbindTarget( None )