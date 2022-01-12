# -*- coding: gb18030 -*-
#
# $Id: Spell_HP.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

import Const
from SpellBase import *


class Spell_HPMP( Spell ):
	"""	
	�ָ��ٷֱȵ�HP��MP
	ֻ������ҹս����ս��
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self._p1 = 0.0
		self._p2 = 0.0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) / 100.0
		self._p2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) / 100.0
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		cureHP = int( receiver.HP_Max * self._p1 )
		cureMP = int( receiver.MP_Max * self._p2 )
		
		receiver.addHP( cureHP )
		receiver.addMP( cureMP )