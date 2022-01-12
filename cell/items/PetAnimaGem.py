# -*- coding: gb18030 -*-

# $Id: PetAnimaGem.py,v 1.1 2007-11-26 00:45:20 huangyongwei Exp $

"""
equip by role and used by pet to enhance
"""

from PetFormulas import formulas
from CItemBase import CItemBase


class PetAnimaGem( CItemBase ) :
	def __init__( self ) :
		CItemBase.__init__( self, { "id" : 10 } )

	def isFull( self ) :
		return True

	def getValue( self, isCurse ) :
		return formulas.getEnhanceEffect( isCurse )
