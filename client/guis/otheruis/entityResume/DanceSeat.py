# -*- coding: gb18030 -*-
#
# $Id: NpcResume.py,v 1.7 2008-08-30 10:14:15 wangshufeng Exp $


import csdefine
import csconst
from gbref import rds
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from FactionMgr import factionMgr
from LabelGather import labelGather
import cschannel_msgs

class DanceSeat:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		text = None
		for i in entity.entitiesInRange(5):
			if i.__class__.__name__ == "DanceKing" and i.locationIndex == entity.locationIndex:
				return text
		text = cschannel_msgs.DANCESEATTIPS
		return text
		
instance =  DanceSeat()