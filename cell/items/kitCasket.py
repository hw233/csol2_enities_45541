# -*- coding: gb18030 -*-

# $Id: kitCasket.py,v 1.4 2008-10-28	huangdong Exp $

"""
背包类基础模块
"""

from CItemBase import *

class kitCasket( CItemBase ):
	"""
	神机匣

	@ivar maxSpace: 默认最大空间
	@type maxSpace: INT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
