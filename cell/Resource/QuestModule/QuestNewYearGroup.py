# -*- coding: gb18030 -*-
#
# $Id $


from QuestRandomGroup import *
import Love3

NEW_YEAR_GROUP_SPELL = 122152006

class QuestNewYearGroup( QuestRandomGroup ):
	def __init__( self ):
		QuestRandomGroup.__init__( self )


	def abandoned( self, player, flags ):
		"""
		放弃任务增加反省buff
		"""	
		Love3.g_skills[NEW_YEAR_GROUP_SPELL].receiveLinkBuff( player, player )		
		return QuestRandomGroup.abandoned( self, player, flags )
