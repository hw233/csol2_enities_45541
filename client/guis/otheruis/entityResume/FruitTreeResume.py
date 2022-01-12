# -*- coding: gb18030 -*-
#

import csconst
from PetFormulas import formulas
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from gbref import rds
from LabelGather import labelGather
import time

class FruitTreeResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		text = ""
		text += labelGather.getText( "EntityResume:FruitTree", "PlanterName", entity.planterName )
		text += PL_NewLine.getSource()
		isRipe = entity.isRipe
		if isRipe:
			text += labelGather.getText( "EntityResume:FruitTree", "Ripe" )
			text += PL_NewLine.getSource()


			#planterName
		else:
			currTime = time.time()
			lessTime = entity.endTime - currTime
			if lessTime <= 0:
				per = 0
				sec = 0
			else:
				per = int( lessTime/60.0 )
				sec = int( lessTime%60 )
			text += labelGather.getText( "EntityResume:FruitTree", "noRipe", "%d:%d"%( per, sec ) )
			text += PL_NewLine.getSource()
		return text


instance = FruitTreeResume()