# -*- coding: gb18030 -*-
import BigWorld
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import csconst
from LabelGather import labelGather

class EidolonResume:
	def __init__( self ):
		pass
	
	def doMsg_( self, entity, window ):
		text = ""
		ownerName = entity.ownerName
		owner = BigWorld.entities.get( entity.ownerID, None )
		if ownerName != "":
			text += labelGather.getText( "EntityResume:eidolon", "ownerName", ownerName )
		if owner:
			text += PL_NewLine.getSource()
			text += labelGather.getText( "EntityResume:eidolon", "ownerVip", owner.vip )			
		return text
instance = EidolonResume()