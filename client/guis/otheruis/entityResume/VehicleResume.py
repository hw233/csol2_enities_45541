# -*- coding: gb18030 -*-

from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import csconst
from LabelGather import labelGather

class VehicleResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		text = ""
		horseman = entity.getHorseMan()
		if horseman is None: return text
		# 策划要求骑上骑宠后，鼠标放到其身上时与没有骑宠完全一样
		#text = "骑宠(%s)" % horseman.playerName
		#text += PL_NewLine.getSource()
		#return text

		if horseman.tongName != "":
			text =  horseman.tongName
			text += PL_NewLine.getSource()

		text += horseman.playerName
		text += PL_NewLine.getSource()

		pclass = csconst.g_chs_class[horseman.getClass()]
		level = horseman.level

		roleInfo = labelGather.getText( "EntityResume:vehicle", "LVAndRace", level, pclass )
		text += roleInfo

		return text


instance = VehicleResume()