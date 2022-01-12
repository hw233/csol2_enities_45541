# -*- coding: gb18030 -*-

# $Id: CArmor.py,v 1.3 2007-11-24 02:57:12 yangkai Exp $

"""

"""
from CEquip import *

class CArmor( CEquip ):
	"""
	护甲基础类

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		获取防具效果类型自定义数据格式
		用于发送到客户端
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
# 防具增加属性
# "reliable" // 可靠度
# "maxReliableLimit" // 最大可靠度上限
#
# Revision 1.1  2006/08/09 08:24:17  phw
# no message
#
#
