# -*- coding: gb18030 -*-
#
# $Id: Spell_112005.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *

class Spell_112005( Spell ):
	"""
	擒拿，将目标玩家传送至自己身边
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
		receiver.teleport( caster, caster.position, caster.direction )

#$Log: not supported by cvs2svn $
#
#