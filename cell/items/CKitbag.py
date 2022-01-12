# -*- coding: gb18030 -*-

# $Id: CKitbag.py,v 1.4 2008-05-30 03:03:14 yangkai Exp $

"""
���������ģ��
"""

from CItemBase import CItemBase
import ItemTypeEnum

class CKitbag( CItemBase ):
	"""
	��������

	@ivar maxSpace: Ĭ�����ռ�
	@type maxSpace: INT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		#self.maxSpace = 0

	def onWield( self, owner ):
		"""
		vitural method
		"""
		# ��������ʱ��ʹ��ʱ��
		lifeType = self.getLifeType()
		if lifeType == ItemTypeEnum.CLTT_ON_WIELD:
			self.activaLifeTime( owner )

		# ����������
		bindType = self.getBindType()
		isBinded = self.isBinded()
		if bindType == ItemTypeEnum.CBT_EQUIP and not isBinded:
			self.setBindType( ItemTypeEnum.CBT_EQUIP, owner )

### end of class: CKitbag ###


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/11/24 03:07:18  yangkai
# ��Ʒϵͳ���������Ը���
# ����ʵ��"kitbagClass" -- > "kb_kitbagClass"
#
# Revision 1.2  2006/08/11 02:57:00  phw
# ���Ը������޸�����itemInstance.keyName��itemInstance.id()ΪitemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
