# -*- coding: gb18030 -*-
#
# $Id: Spell_112025.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Spell_Magic import Spell_Magic


class Spell_112025( Spell_Magic ):
	"""
	������������ѡ�е�npc
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		receiver.createObjectNearPlanes( receiver.className, receiver.position, receiver.direction, { "spawnPos" : tuple( receiver.position ) } )
		
#$Log: not supported by cvs2svn $
#
#