# -*- coding: gb18030 -*-
from SpaceNormal import SpaceNormal
from interface.ImpPlanesSpace import ImpPlanesSpace

class SpacePlanes( SpaceNormal, ImpPlanesSpace ):
	"""
	位面副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		super( SpacePlanes, self ).__init__()