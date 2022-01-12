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
	复活术，复活选中的npc
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver.createObjectNearPlanes( receiver.className, receiver.position, receiver.direction, { "spawnPos" : tuple( receiver.position ) } )
		
#$Log: not supported by cvs2svn $
#
#