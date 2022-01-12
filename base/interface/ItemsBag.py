# -*- coding: gb18030 -*-
#
# $Id: ItemsBag.py,v 1.5 2008-03-19 02:50:46 wangshufeng Exp $


import csdefine
from bwdebug import *
from RoleSwapItem import RoleSwapItem
from RoleVend import RoleVend

class ItemsBag( RoleSwapItem, RoleVend ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		RoleSwapItem.__init__( self )
		RoleVend.__init__( self )
