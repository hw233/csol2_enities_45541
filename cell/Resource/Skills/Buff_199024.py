# -*- coding: gb18030 -*-

"""
"""
from Buff_VehicleTrans import Buff_VehicleTrans

class Buff_199024( Buff_VehicleTrans ):
	"""
	����buff
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_VehicleTrans.__init__( self )
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_VehicleTrans.init( self, dict )