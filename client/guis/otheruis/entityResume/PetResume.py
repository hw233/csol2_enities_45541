# -*- coding: gb18030 -*-
#
# $Id: PetResume.py,v 1.5 2008-05-26 03:52:48 zhangyuxing Exp $

import BigWorld
import csconst
from PetFormulas import formulas
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from gbref import rds
from LabelGather import labelGather

class PetResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		text = ""
		name = entity.getName()
		name = rds.textFormatMgr.makeDestStr( name, rds.textFormatMgr.nameCode )

		text += name
		"""
		className = getattr( entity, "className", None )
		if className == 1:
			text = PL_Font.getSource( text, fc = ( 255, 255, 255 ) )
		elif className == 2:
			text = PL_Font.getSource( text, fc = ( 0, 128, 0 ) )
		elif className == 3:
			text = PL_Font.getSource( text, fc = ( 0, 255, 0 ) )
		elif className == 4:
			text = PL_Font.getSource( text, fc = ( 255, 255, 0 ) )
		"""
		text += PL_NewLine.getSource()
		owner = entity.getOwner()
		ownerName = owner.playerName
		if owner.onFengQi and owner.id != BigWorld.player().id:
			ownerName = labelGather.getText( "YezhanFengQi:main", "masked" )
		masterInfo = labelGather.getText( "EntityResume:pet", "petOwner", ownerName )
		text += masterInfo
		text += PL_NewLine.getSource()

		hi = formulas.getHierarchy( entity.species )
		hierarchie = csconst.pet_ch_hierarchies[hi]
		text += hierarchie
		text += PL_NewLine.getSource()

		petInfo = labelGather.getText( "EntityResume:pet", "petLVAndUname", entity.level, entity.uname )
		text += petInfo

		return text


instance = PetResume()