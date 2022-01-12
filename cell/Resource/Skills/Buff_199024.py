# -*- coding: gb18030 -*-

"""
"""
from Buff_VehicleTrans import Buff_VehicleTrans

class Buff_199024( Buff_VehicleTrans ):
	"""
	变身buff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_VehicleTrans.__init__( self )
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_VehicleTrans.init( self, dict )