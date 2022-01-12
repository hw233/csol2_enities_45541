# -*- coding: gb18030 -*-
#
# $Id: Spell_112006.py,v 1.2 2008-09-02 03:21:13 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *

class Spell_112006( Spell ):
	"""
	˲����ǰ��������
	"""
	def __init__( self ):
		Spell.__init__( self )
		self._p1 = 0
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  * 1.8		# ˲���ľ��룬��Ҫ��ȷ
		
		
	def receiver( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		x = caster.position[ 0 ] + self._p1
		y = caster.position[ 1 ]
		z = caster.position[ 2 ] + self._p1
		receiver.teleport( receiver, tuple( x, y, z ), receiver.direction )

#$Log: not supported by cvs2svn $
#Revision 1.1  2008/08/30 10:01:12  wangshufeng
#npc��ؼ��ܡ�buff
#
#
#