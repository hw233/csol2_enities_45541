
# -*- coding: gb18030 -*-
#
# $Id: TongNagual.py,v 1.1 2008-09-01 06:00:34 kebiao Exp $


import csdefine
import BigWorld
from Monster import Monster

class TongNagual( Monster ):
	"""
	怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )