# -*- coding: gb18030 -*-

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomain import SpaceDomain
from interface.ImpPlanesSpaceDomain import ImpPlanesSpaceDomain
import csdefine

class SpaceDomainPlanes( SpaceDomain, ImpPlanesSpaceDomain ):
	"""
	位面地图domain
	"""
	def __init__( self ):
		super( SpaceDomainPlanes, self ).__init__()
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_PLANES
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		副本是由一定规则开放的， 因此不允许登陆后能够呆在一个
		不是自己开启的副本中， 遇到此情况应该返回到上一次登陆的地方
		"""
		baseMailbox.logonSpaceInSpaceCopy()