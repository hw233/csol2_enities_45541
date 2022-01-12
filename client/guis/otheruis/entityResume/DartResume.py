# -*- coding: gb18030 -*-
#
# $Id: PetResume.py,v 1.5 2008-05-26 03:52:48 zhangyuxing Exp $


import csconst
from PetFormulas import formulas
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from gbref import rds
from LabelGather import labelGather

class DartResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):
		text = ""
		name = entity.getName()
		name = rds.textFormatMgr.makeDestStr( name, rds.textFormatMgr.nameCode )

		text += name
		text += PL_NewLine.getSource()

		ownerInfo = labelGather.getText( "EntityResume:dart", "dartOwner" ) % (entity.ownerName)
		text += ownerInfo
		text += PL_NewLine.getSource()

		levelInfo = labelGather.getText( "EntityResume:dart", "dartLevel" ) % entity.level
		text += levelInfo

		return text


instance = DartResume()