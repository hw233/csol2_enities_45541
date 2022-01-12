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

class NpcResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		text = ""
		name = entity.getName()
		name = rds.textFormatMgr.makeDestStr( name, rds.textFormatMgr.nameCode )

		text += name
		"""
		className = getattr( entity, "className", None )
		if entity.className[4] == '1':
			text = PL_Font.getSource( text, fc = ( 255, 255, 255 ) )
		elif entity.className[4] == '2':
			text = PL_Font.getSource( text, fc = ( 0, 128, 0 ) )
		elif entity.className[4] == '3':
			text = PL_Font.getSource( text, fc = ( 0, 255, 0 ) )
		elif entity.className[4] == '4':
			text = PL_Font.getSource( text, fc = ( 255, 255, 0 ) )
		"""
		text += PL_NewLine.getSource()

		if entity.title != "":
			text += entity.title
			text += PL_NewLine.getSource()

		text += factionMgr.getName( ( entity.raceclass & csdefine.RCMASK_FACTION ) >> 12 )
		text += PL_NewLine.getSource()

		petInfo = labelGather.getText( "EntityResume:npc", "level", entity.level )
		text += petInfo

		return text



instance = NpcResume()