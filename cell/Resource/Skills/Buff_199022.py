# -*- coding: gb18030 -*-

"""
"""
from Buff_ChangeFace import Buff_ChangeFace

class Buff_199022( Buff_ChangeFace ):
	"""
	变脸
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_ChangeFace.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_ChangeFace.init( self, dict )