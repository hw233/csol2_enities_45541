# -*- coding: gb18030 -*-

# $Id: CKitbag.py,v 1.4 2008-05-30 03:03:54 yangkai Exp $

"""
���������ģ��
"""

from CItemBase import *

class CKitbag( CItemBase ):
	"""
	��������

	@ivar maxSpace: Ĭ�����ռ�
	@type maxSpace: INT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		#self.maxSpace = 0

### end of class: CKitbag ###


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/11/24 03:01:14  yangkai
# ��Ʒϵͳ���������Ը���
# ����ʵ��"kitbagClass" -- > "kb_kitbagClass"
#
# Revision 1.2  2006/08/11 02:58:48  phw
# no message
#
# Revision 1.1  2006/08/09 08:24:17  phw
# no message
#
#
