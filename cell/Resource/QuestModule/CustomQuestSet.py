# -*- coding: gb18030 -*-
#
# $Id: CustomQuestSet.py,v 1.28 2008-02-18 02:59:53 kebiao Exp $

"""
"""
from bwdebug import *

__all__ = [ ]
__quests__ = [

	# 材料收集任务
	#"Q40100",
]

def importAllQuests():
	for q in __quests__:
		mod = __import__( "Resource.QuestModule.%s" % q, None, None, [ q ] )
		__all__.append( getattr( mod, q )() )
	return
	
importAllQuests()

