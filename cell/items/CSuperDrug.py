# -*- coding: gb18030 -*-

# $Id: CSuperDrug.py,v 1.1 2008-08-30 02:39:19 yangkai Exp $

from CItemBase import CItemBase
import csdefine

class CSuperDrug( CItemBase ):
	"""
	���д����ֵ��ʹ�ö�εĲ�ҩ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getMaxPoint( self ):
		"""
		��ȡ��ҩ����ָܻ�����
		"""
		return self.query( "sd_maxPoint", 0 )

	def getCurrPoint( self ):
		"""
		��ȡ��ҩ��ǰ�ָܻ��ĵ���
		"""
		return self.query( "sd_currPoint", 0 )

	def onSpellOver( self, owner ):
		"""
		����ʹ�ý���
		@param owner	: ӵ����
		@type  owner	: Entity
		@return 		: None
		"""
		usePoint = self.queryTemp( "sd_usePoint", 0 )
		remainPoint = self.getCurrPoint() - usePoint
		if remainPoint <= 0:
			owner.removeItem_( self.order, reason = csdefine.DELETE_ITEM_USE )
		else:
			self.set( "sd_currPoint", remainPoint, owner )

		self.setTemp( "sd_usePoint", 0 )

# $Log: not supported by cvs2svn $
