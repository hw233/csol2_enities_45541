# -*- coding: gb18030 -*-
#
# $Id: Spell_112009.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Spell_Magic import Spell_Magic
from ObjectScripts.GameObjectFactory import g_objFactory


class Spell_112009( Spell_Magic ):
	"""
	分身术，复制出几个分身参与战斗
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self._p1 = 0
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		for i in xrange( self._p1 ):
			caster.createEntityNearPlanes( caster.className, caster.position, caster.direction, { "spawnPos" : tuple( caster.position ) } )

#$Log: not supported by cvs2svn $
#
#