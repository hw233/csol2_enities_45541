# -*- coding: gb18030 -*-

from bwdebug import *
from CItemBase import CItemBase

class CExpItem( CItemBase ):
	"""
	���鵤
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def setExp( self, exp, owner = None ):
		"""
		���þ��鵤�ľ���ֵ
		@param		exp		:	���鵤����ֵ
		@type		exp		:	INT64
		@param		owner	:	���鵤ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "exp_item", exp, owner )
	
	def getExp( self ):
		"""
		��ȡ���鵤��ǰ����ֵ
		"""
		return self.query( "exp_item", 0 )
		