# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from NPCObject import NPCObject
import csdefine
import items
import ECBExtend
from QuestBox import QuestBox

class YiJieZhanChangFactionFlag( QuestBox ):
	"""
	异界战场阵营柱
	"""
	
	def __init__( self ):
		QuestBox.__init__( self )

