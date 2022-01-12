# -*- coding: gb18030 -*-

# common
from bwdebug import *
# cell
from CItemBase import CItemBase

class CNatureJade( CItemBase ):
	"""
	造化玉牒基础类
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		
	def getYDRealm( self ):
		"""
		获取境界
		"""
		return self.query( "ydRealm", 1 )
		

#
# $Log: not supported by cvs2svn $
#
