# -*- coding: gb18030 -*-

# $Id: CKitbag.py,v 1.4 2008-05-30 03:03:14 yangkai Exp $

"""
背包类基础模块
"""

from CItemBase import CItemBase
import ItemTypeEnum

class CKitbag( CItemBase ):
	"""
	背包基础

	@ivar maxSpace: 默认最大空间
	@type maxSpace: INT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		#self.maxSpace = 0

	def onWield( self, owner ):
		"""
		vitural method
		"""
		# 激活背包后计时的使用时间
		lifeType = self.getLifeType()
		if lifeType == ItemTypeEnum.CLTT_ON_WIELD:
			self.activaLifeTime( owner )

		# 背包绑定类型
		bindType = self.getBindType()
		isBinded = self.isBinded()
		if bindType == ItemTypeEnum.CBT_EQUIP and not isBinded:
			self.setBindType( ItemTypeEnum.CBT_EQUIP, owner )

### end of class: CKitbag ###


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/11/24 03:07:18  yangkai
# 物品系统调整，属性更名
# 背包实例"kitbagClass" -- > "kb_kitbagClass"
#
# Revision 1.2  2006/08/11 02:57:00  phw
# 属性更名：修改所有itemInstance.keyName或itemInstance.id()为itemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
