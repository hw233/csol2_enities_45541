# -*- coding: gb18030 -*-

# $Id: CPositionSpell.py

from CItemBase import CItemBase

class CPositionSpellItem( CItemBase ):
	"""
	位置施法物品
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )