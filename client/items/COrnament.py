# -*- coding: gb18030 -*-

# $Id: COrnament.py,v 1.1 2006-08-18 06:54:26 phw Exp $

"""
装备类基础模块
"""
from bwdebug import *
from CEquip import *

class COrnament( CEquip ):
	"""
	饰品，适用于戒指和项链
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

### end of class: COrnament ###


#
# $Log: not supported by cvs2svn $
#
