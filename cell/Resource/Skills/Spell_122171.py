# -*- coding: gb18030 -*-
"""
技能:血祭 
"""

from Spell_Magic import Spell_Magic
import csstatus

class Spell_122171(Spell_Magic):
	"""
	作用：恢复目标生命上限i%的生命值
	"""
	
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Magic.__init__( self )
		self._param = 0
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._param = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0.0 )  / 100	
	
	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		校验技能是否可以使用
		"""
		if receiver.getObject().HP == receiver.getObject().HP_Max:
			return csstatus.SKILL_NOT_NEED_USE
		return Spell_Magic.useableCheck( self, caster, receiver )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		value = receiver.HP_Max * self._param
		receiver.addHP( int( value ) )