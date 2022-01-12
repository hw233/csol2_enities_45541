# -*- coding: gb18030 -*-
import BigWorld
import csdefine
from bwdebug import *
from gbref import rds
import event.EventCenter as ECenter
from SpaceDoor import SpaceDoor

class SpaceDoorChallenge( SpaceDoor ):
	def __init__( self ):
		SpaceDoor.__init__( self )
	
	# Becoming a target
	def onTargetFocus( self ):
		self.canShowDescript = True
		if rds.ruisMgr.isMouseHitScreen() :
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
			rds.ccursor.set( "transport" )

	# Quitting as target
	def onTargetBlur( self ):
		self.canShowDescript = False
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		rds.ccursor.set( "normal" )