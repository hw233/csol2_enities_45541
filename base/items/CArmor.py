# -*- coding: gb18030 -*-

# $Id: CArmor.py,v 1.3 2007-11-24 02:57:12 yangkai Exp $

"""

"""
from CEquip import *

class CArmor( CEquip ):
	"""
	���׻�����

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return ARMOR_EFFECT FDict, Define in alias.xml
		"""
		data = { 	"modelNum"		:	self.model(),
					"iLevel"		:	self.getIntensifyLevel(),
					}

		return data

### end of class: CArmor ###


#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/08/15 07:12:03  yangkai
# ������������
# "reliable" // �ɿ���
# "maxReliableLimit" // ���ɿ�������
#
# Revision 1.1  2006/08/09 08:24:17  phw
# no message
#
#
