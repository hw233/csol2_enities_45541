# -*- coding: gb18030 -*-
#
# $Id: Spell_ChangeEnmity.py,v 1.1 2007-11-24 08:22:58 kebiao Exp $

"""
��ʩ���ߴ�Ŀ��������б��˺��б�ս���б��������б���ɾ��
"""

from SpellBase import *
import random
import csdefine
import csstatus
from Spell_Magic import Spell_Magic
from Domain_Fight import g_fightMgr

class Spell_ChangeEnmity( Spell_Magic ):
	"""
	��ʩ���ߴ�Ŀ��������б��˺��б�ս���б��������б���ɾ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )

	def useableCheck( self, caster, target ):
		
		if target.getObject().level > self.getCastTargetLevelMax():
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return Spell_Magic.useableCheck( self, caster, target )
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		g_fightMgr.breakEnemyRelation( receiver, caster )
		
# $Log: not supported by cvs2svn $
