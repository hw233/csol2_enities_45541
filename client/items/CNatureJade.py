# -*- coding: gb18030 -*-

# common
from bwdebug import *
# cell
from CItemBase import CItemBase

class CNatureJade( CItemBase ):
	"""
	�컯��뺻�����
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		
	def getYDRealm( self ):
		"""
		��ȡ����
		"""
		return self.query( "ydRealm", 1 )
		

#
# $Log: not supported by cvs2svn $
#
