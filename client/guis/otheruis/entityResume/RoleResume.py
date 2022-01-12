# -*- coding: gb18030 -*-
#
# $Id: RoleResume.py,v 1.4 2008-06-21 01:35:37 kebiao Exp $


import csconst
from gbref import rds
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from LabelGather import labelGather

class RoleResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):

		text = ""

		if entity.tongName != "":
			text =  entity.tongName
			text += PL_NewLine.getSource()
			
		name = entity.playerName
		name = rds.textFormatMgr.makeDestStr( name, rds.textFormatMgr.nameCode )
		text += name
		text += PL_NewLine.getSource()

		pclass = csconst.g_chs_class[entity.getClass()]
		level = entity.level

		roleInfo = labelGather.getText( "EntityResume:role", "LVAndRace", level, pclass )
		text += roleInfo

		if hasattr( entity, "onFengQi" ) and entity.onFengQi:
			text = labelGather.getText( "EntityResume:role", "fengQiName" )

		return text


instance = RoleResume()