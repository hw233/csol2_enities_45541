# -*- coding: gb18030 -*-
from SpaceNormal import SpaceNormal
from interface.ImpPlanesSpace import ImpPlanesSpace

class SpacePlanes( SpaceNormal, ImpPlanesSpace ):
	"""
	λ�渱��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		super( SpacePlanes, self ).__init__()