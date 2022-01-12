# -*- coding: gb18030 -*-

# $Id: ProximityTransducer.py,v 1.4 2008-07-08 09:39:49 yangkai Exp $
"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from gbref import rds
import csdefine
import Define

class ProximityTransducer( NPCObject ):
	"""
	"""
	def __init__( self ):
		NPCObject.__init__( self )
		self.setSelectable( True )

	def enterWorld( self ):
		"""
		This method is called when the entity enter the world
		"""
		self.filter = BigWorld.AvatarDropFilter()	# 代替AvatarFilter

		if len( self.modelNumber ):
			rds.npcModel.createDynamicModelBG( self.modelNumber,  self.__onModelLoad )
	
	def __onModelLoad( self, model ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.model = model
		self.am = self.model.motors[0]
		self.am.matchCaps = [Define.CAPS_DEFAULT]
		self.setVisibility( self.visible )

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		pass	# do nothing


# end of ProximityTransducer.py
