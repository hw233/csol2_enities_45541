# -*- coding: gb18030 -*-

"""
Ϊ40�����鸱������״̬�������ض������ļ���
"""

import csdefine
import BigWorld
from gbref import rds
from SpellBase import *

class Spell_322506( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )
		self._paths = []
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self._paths = str( dict[ "param1" ] ).split(";")
		
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		if len(self._paths) > 0 and BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
			rds.roleFlyMgr.doCheckFly( self._paths, self.onEndFly )
			
	def onEndFly(self):
		"""
		�������лص�
		"""
		rds.roleFlyMgr.stopFly(False)
		BigWorld.player().physics.fall = True
		BigWorld.player().cell.requestClearBuffer()			#֪ͨ�������������贫��buffer
		