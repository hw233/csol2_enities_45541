# -*- coding: gb18030 -*-
#
# $Id: Spell_322377.py,v 1.2 2008-02-26 07:53:57 kebiao Exp $

"""
"""

from SpellBase import *
import csstatus
import Const
from Spell_Item import Spell_Item
from bwdebug import *

class Spell_322377( Spell_Item ):
	"""
	使用：驾御神典
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		self.param1 = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.param1 = int( dict[ "param1" ] )
		
	def useableCheck( self, caster, target ) :
		if target.getObject().pcg_reinBible >= Const.PET_KEEP_REINBIBLE_MAX :
			return csstatus.PET_OVERSTEP_REINBIBLE_MAX
		if target.getObject().pcg_reinBible + 1 > self.param1:
			return csstatus.REIN_BOOK_TOO_LOWER
		if target.getObject().pcg_reinBible + 1 < self.param1:
			return csstatus.REIN_BOOK_TOO_HIGHER
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		if receiver.pcg_reinBible < Const.PET_KEEP_REINBIBLE_MAX :
			receiver.pcg_reinBible += 1
		
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/02/26 06:17:53  kebiao
# no message
#
#