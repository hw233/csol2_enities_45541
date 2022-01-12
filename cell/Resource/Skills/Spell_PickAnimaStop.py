# -*- coding: gb18030 -*-
from SpellBase import *

class Spell_PickAnimaStop( Spell ):
	"""
	结束拾取灵气玩法
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver.pickAnima_onEnd() #通知玩家，玩法结束