# -*- coding: gb18030 -*-
#
#edit by wuxo 2012-8-20


"""
�ͻ������봫�ͣ����ڿͻ��˾�ͷ���ű�
"""

from SpellBase import Spell
import BigWorld

class Spell_RequestTeleport( Spell ):
	"""
	���ͼ��ܻ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
	
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		player = BigWorld.player()
		player.cell.requestTeleport( )
	
