# -*- coding: gb18030 -*-
#

"""
��ʩ���ߴ�Ŀ��������б��˺��б�ս���б��������б���ɾ��
"""


from SpellBase.Spell import Spell
import random
import csdefine
from Domain_Fight import g_fightMgr

class Spell_312618( Spell ):
	"""	
	��ʩ���ߴ�Ŀ��������б��˺��б�ս���б��������б���ɾ��
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
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		g_fightMgr.breakEnemyRelation( receiver, caster )

		
