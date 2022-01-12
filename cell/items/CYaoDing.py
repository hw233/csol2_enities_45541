# -*- coding: gb18030 -*-

# $Id: CYaoDing.py

from CItemBase import CItemBase
import csdefine
import SkillTargetObjImpl
import BigWorld

class CYaoDing(CItemBase):
	"""
	��ҩ�������ģ��
	"""
	def __init__( self, srcData ):
		"""
		��ʼ��
		"""
		CItemBase.__init__( self, srcData )

	def onUseOver( self, owner ):
		"""
		����ʹ�ý���
		"""
		useDegree = self.getUseDegree()
		if useDegree == -1:
			pass
		elif useDegree > 1:
			self.set( "useDegree", useDegree - 1, owner )
		else:
			self.setAmount( self.getAmount() - 1, owner, csdefine.DELETE_ITEM_USEYAODING )
		owner.questIncreaseItemUsed( self.id )

	def checkItem( self, item ):
		"""
		�鿴����Ʒ�Ƿ��������ʹ�÷�Χ����,�ýӿڱ��뱻����
		"""
		pass

	def onUse( self, srcEntityID, item, owner, targetID ):
		"""
		��ҩ��ʹ����Ʒ
		"""
		if self.checkItem( item ):
			target = BigWorld.entities.get( targetID )
			if target is None:return
			targetObj = SkillTargetObjImpl.createTargetObjEntity( target )
			if owner.useItem( srcEntityID, item.uid, targetObj ):
				self.onUseOver( owner )
