# -*- coding: gb18030 -*-
#

from gbref import rds
from bwdebug import *
from LabelGather import labelGather

class SpaceDoorResume:
	"""
	����������
	"""
	def __init__( self ):
		"""
		"""
		pass

	def doMsg_( self, entity, window ):
		"""
		"""
		return labelGather.getText( "EntityResume:spaceDoor", "destination", rds.mapMgr.getArea( entity.getDstSpaceLabel(), entity.getDstPosition() ).fullName )


instance = SpaceDoorResume()