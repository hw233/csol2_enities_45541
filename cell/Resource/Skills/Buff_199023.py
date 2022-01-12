# -*- coding: gb18030 -*-

"""
"""
from Buff_ChangeHair import Buff_ChangeHair

class Buff_199023( Buff_ChangeHair ):
	"""
	变身发型
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_ChangeHair.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_ChangeHair.init( self, dict )