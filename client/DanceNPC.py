# -*- coding: gb18030 -*-
#

"""

"""

import BigWorld
from bwdebug import *
import GUIFacade
from NPC import NPC
import csdefine
import event.EventCenter as ECenter
from gbref import rds
import Define
import Const
from Function import Functor 
import csconst

skillIDToAction = {csconst.DanceSkill1:"dance1_1", csconst.DanceSkill2:"dance2_1", csconst.DanceSkill3:"dance3_1", csconst.DanceSkill4:"dance4_1", csconst.DanceSkill5:"dance5_1" }
class DanceNPC( NPC ):
	"""
	"""
	def __init__( self ):
		NPC.__init__(self)

		
	def playDanceAction(self, actionNameList, countdown):
		#Define method
		rds.actionMgr.playActions( self.getModel(), actionNameList, callbacks = [ Functor( self.finishPlayAction,countdown), ] )
		
		
	def finishPlayAction(self, countdown):
		self.cell.finishPlayAction()
		#更新跳舞倒计时,countdown参数在挑战斗舞的时候是有倒计时显示，如果这个参数是0 ，表示是练习斗舞，倒计时一直显示为0
		ECenter.fireEvent( "EVT_DANCE_TIME_LIMIT", countdown )
		
	def refreshDanceComobo(self, danceComoboPoint):
		#define method
		ECenter.fireEvent( "EVT_DANCE_COMOBO_POINT", danceComoboPoint )
		
	def playAction(self, skillID):
		#define method
		rds.actionMgr.playAction(self.getModel(), skillIDToAction[skillID])
		