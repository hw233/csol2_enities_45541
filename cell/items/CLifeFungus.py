# -*- coding: gb18030 -*-

# implement the life fungus item
# written by ganjinxing 2009-12-4


from CItemBase import CItemBase
import csdefine

class CLifeFungus( CItemBase ) :

	def onAdd( self, owner ):
		"""
		��һ�������Ʒʱͷ��Ҫ��ʾĢ�����
		"""
		CItemBase.onAdd( self, owner )
		owner.tong_showFungusFlag()

	def onDelete( self, owner ):
		"""
		���ɾ����Ʒ
		"""
		CItemBase.onDelete( self, owner )
		for item in owner.getAllItems() :		# ����������û��������Ģ�������Ʒ�����Ƴ�ͷ��Ģ�����
			if self.id == item.id :
				return
			owner.tong_removeFungusFlag()