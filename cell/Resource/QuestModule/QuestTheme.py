# -*- coding: gb18030 -*-
#
# $Id: QuestTheme.py,v 1.3 2007-11-02 03:56:27 phw Exp $

"""
"""
from Quest import *
from bwdebug import *
import csdefine
import csstatus
from QuestDataType import QuestDataType
import random
from QTTask import QTTaskDeliver
from QTTask import QTTaskKill
from QTRequirement import QTRLevel
import items

from ECBExtend import *
import Love3
import random
import Math

class QuestTheme( Quest ):
	def __init__( self ):
		Quest.__init__( self )

	def _hangNPC( self, npc, hangTime ):
		npc.changeState( csdefine.ENTITY_STATE_HANG )
		npc.addTimer( hangTime, 0, UNHANG_TIMER_CBID )

	def _hangAndKillNPC( self, npc, afterTime ):
		npc.addTimer( afterTime, 0, HANG_AND_KILL_TIMER_CBID )

	def _randGenNPC( self, key, spaceID, position, range, showTime ):
		npc = Love3.g_NPCList[ key ]
		pos = Math.Vector3( random.random(), random.random(), random.random() )
		pos.normalise()
		pos = position + pos.scale( range / 6 + random.random() * (range / 6 * 5) )
		face = Math.Vector3( 0, 0, random.random() * 3.14 )
		npc = npc.createEntity( spaceID, pos, face )
		self._hangAndKillNPC( npc, showTime )

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/06/14 09:59:20  huangyongwei
# 重新整理了宏定义
#
# Revision 1.1  2006/09/18 01:48:45  chenzheming
# no message
#
#
#