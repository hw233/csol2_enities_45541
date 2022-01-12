# -*- coding: gb18030 -*-

# $Id: CSuperDrug.py,v 1.1 2008-08-30 02:39:19 yangkai Exp $

from CItemBase import CItemBase
import csdefine

class CSuperDrug( CItemBase ):
	"""
	具有大额数值能使用多次的补药
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getMaxPoint( self ):
		"""
		获取该药最大能恢复点数
		"""
		return self.query( "sd_maxPoint", 0 )

	def getCurrPoint( self ):
		"""
		获取该药当前能恢复的点数
		"""
		return self.query( "sd_currPoint", 0 )

	def onSpellOver( self, owner ):
		"""
		技能使用结束
		@param owner	: 拥有者
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
