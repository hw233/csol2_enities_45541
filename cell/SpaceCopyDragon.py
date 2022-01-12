# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst


class SpaceCopyDragon( SpaceCopy ):
	
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		if "TJQS_%i"%self.params["teamID"] in BigWorld.cellAppData.keys():
			del BigWorld.cellAppData["TJQS_%i"%self.params["teamID"]]

	
	def onEnter( self, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
	
