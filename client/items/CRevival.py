# -*- coding: gb18030 -*-

# $Id: CArmor.py,v 1.7 2008-05-17 11:42:42 huangyongwei Exp $

"""

"""
import ItemAttrClass
import csdefine
import csstatus
import BigWorld
from CItemBase import CItemBase
import csconst
import ItemTypeEnum

class CRevival( CItemBase ):
	"""
	��������Ʒ������ by���� 2009-7-28
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )

	def use( self, owner, target ):
		"""
		ʹ����Ʒ
		@param    owner: ����ӵ����
		@type     owner: Entity
		@param   target: ʹ��Ŀ��
		@type    target: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult
		return CItemBase.use( self, owner, target )

	def checkUse( self, owner ):
		"""
		��鸴������Ʒ�Ƿ����
		@param owner: ����ӵ����
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		if not owner.isDead():
			return csstatus.CIB_REVIVAL_ITEM_USE
		return CItemBase.checkUse( self, owner )

	def description( self, reference ):
		return CItemBase.description( self, reference )

#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/03/24 02:30:55  yangkai
# �����װ�����������
#
# Revision 1.5  2008/02/22 01:40:25  yangkai
# ��ӷ��߸�����������
#
# Revision 1.4  2008/01/29 02:37:26  yangkai
# ������Ʒ������Ϣ
#
# Revision 1.3  2008/01/24 10:10:41  yangkai
# �����Ʒ�������
#
# Revision 1.2  2006/08/11 02:47:12  phw
# ɾ���˽ӿ�wield()��unwield()������cellApp�ķϴ���
#
# Revision 1.1  2006/08/09 08:21:30  phw
# no message
#
