# -*- coding: gb18030 -*-
#
# $Id: QuestBoxResume.py,v 1.3 2008-05-26 03:52:48 zhangyuxing Exp $


import csconst
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine

class QuestBoxResume:
	def __init__( self ) :
		pass


	def doMsg_( self, entity, window ):

		text = entity.uname
		text += PL_NewLine.getSource()
		
		return text


instance = QuestBoxResume()