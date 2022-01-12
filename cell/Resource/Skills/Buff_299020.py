# -*- coding: gb18030 -*-

"""
变身buff，buff结束后改变为自由状态
"""
import csdefine
from SpellBase import *
from Buff_299018 import Buff_299018

class Buff_299020( Buff_299018 ):
	"""
	变身buff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_299018.__init__( self )
