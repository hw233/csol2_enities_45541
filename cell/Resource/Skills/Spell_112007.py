# -*- coding: gb18030 -*-
#
# $Id: Spell_112007.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *

class Spell_112007( Spell ):
	"""
	��Ӱ���Σ����Լ�������Ŀ������
	"""
	def __init__( self ):
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
		caster.teleport( receiver, receiver.position, receiver.direction )

#$Log: not supported by cvs2svn $
#
#