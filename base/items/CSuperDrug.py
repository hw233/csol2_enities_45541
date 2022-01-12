# -*- coding: gb18030 -*-

# $Id: CSuperDrug.py,v 1.1 2008-08-30 02:39:05 yangkai Exp $

from CItemBase import CItemBase


class CSuperDrug( CItemBase ):
	"""
	具有大额数值能使用多次的补药
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

# $Log: not supported by cvs2svn $
