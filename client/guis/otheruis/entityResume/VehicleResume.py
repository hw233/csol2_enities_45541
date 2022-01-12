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
		# �߻�Ҫ�������������ŵ�������ʱ��û�������ȫһ��
		#text = "���(%s)" % horseman.playerName
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