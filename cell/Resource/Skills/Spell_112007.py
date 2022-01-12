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
	如影随形，将自己传送至目标区域
	"""
	def __init__( self ):
		Spell.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		caster.teleport( receiver, receiver.position, receiver.direction )

#$Log: not supported by cvs2svn $
#
#