# -*- coding: gb18030 -*-

from bwdebug import *
from CItemBase import CItemBase

class CExpItem( CItemBase ):
	"""
	经验丹
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def setExp( self, exp, owner = None ):
		"""
		设置经验丹的经验值
		@param		exp		:	经验丹经验值
		@type		exp		:	INT64
		@param		owner	:	经验丹拥有者
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "exp_item", exp, owner )
	
	def getExp( self ):
		"""
		获取经验丹当前经验值
		"""
		return self.query( "exp_item", 0 )
		