# -*- coding: gb18030 -*-
#
# $Id: MonsterResume.py,v 1.9 2008-08-30 10:13:42 wangshufeng Exp $


import BigWorld
import csconst
from gbref import rds
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import csdefine
from FactionMgr import factionMgr
from LabelGather import labelGather

RACEDICT = { 1: labelGather.getText( "EntityResume:monster", "type_person" ),
				2: labelGather.getText( "EntityResume:monster", "type_machine" ),
				3: labelGather.getText( "EntityResume:monster", "type_animal" ),
				4: labelGather.getText( "EntityResume:monster", "type_plant" ),
				5: labelGather.getText( "EntityResume:monster", "type_apparition" ),
				6: labelGather.getText( "EntityResume:monster", "type_immortal" ),
				7: labelGather.getText( "EntityResume:monster", "type_monster" ),
			}

class MonsterResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		text = ""
		name = entity.getName()
		name = rds.textFormatMgr.makeDestStr( name, rds.textFormatMgr.nameCode )

		if entity.isEntityType( csdefine.ENTITY_TYPE_CONVOY_MONSTER ):
			ownerName =  entity.ownerName
			if ownerName:
				name = ownerName + labelGather.getText( "EntityResume:monster", "de" ) + name
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
		text += factionMgr.getName( ( entity.raceclass & csdefine.RCMASK_FACTION ) >> 12 )
		text += PL_NewLine.getSource()
		if entity.level != 0:
			try:
				petInfo = labelGather.getText( "EntityResume:monster", "LVAndUname", entity.level, RACEDICT[( entity.raceclass & csdefine.RCMASK_RACE ) >> 8] )
			except:
				petInfo = ""
			text += petInfo
			text += PL_NewLine.getSource()

		if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_CATCH ):
			takeLevelDescript = labelGather.getText( "EntityResume:monster", "takeLevel", entity.getTakeLevel() )
			takeLevelDescript = PL_Font.getSource( takeLevelDescript, fc = ( 0, 255, 0, 255 ) )
			text += takeLevelDescript
		#else:
		#	takeLevelDescript = labelGather.getText( "EntityResume:monster", "cantCatch" )
		#	takeLevelDescript = PL_Font.getSource( takeLevelDescript, fc = ( 255, 0, 0, 255 ) )
		return text


instance = MonsterResume()