# -*- coding: gb18030 -*-

"""
Ϊ40�����鸱������״̬�в��Ŷ����������ļ���
"""
import BigWorld
from SpellBase import *
from gbref import rds

class Spell_Action( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )
		self._actionName = ""
		self._playAniScale = None
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self._actionName = str(dict["param1"])
		if dict["param2"] != "":
			self._playAniScale = float(dict["param2"])
		
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		model = caster.model
		if model:
			model.action(self._actionName)()
		if self._playAniScale is not None:
			BigWorld.player().am.playAniScale = self._playAniScale
			