# -*- coding: gb18030 -*-

# $Id: kitCasket.py,v 1.4 2008-10-28	huangdong Exp $

"""
���������ģ��
"""

from CItemBase import *

class kitCasket( CItemBase ):
	"""
	���ϻ

	@ivar maxSpace: Ĭ�����ռ�
	@type maxSpace: INT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
