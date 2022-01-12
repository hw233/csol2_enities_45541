# -*- coding: gb18030 -*-

from config.client.labels.items import lbs_EquipEffects
from CItemBase import CItemBase

class CItemGainPotential( CItemBase ):
	"""
	���Ǳ����Ʒ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def description( self, reference ):
		"""
		��������
		"""
		desPot = "%s:    %s"%( lbs_EquipEffects[66], self.query( "param1", 0 ) )
		self.desFrame.SetDescription( "bookPotential", desPot )
		return CItemBase.description( self, reference )