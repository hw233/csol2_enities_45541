# -*- coding: gb18030 -*-
#
# $Id: PotentialObject.py,v 1.2 2008-03-28 07:30:44 kebiao Exp $

"""
怪物NPC的类
"""

from NPC import NPC
from bwdebug import *

class PotentialObject(NPC):
	"""
	怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPC.__init__( self )

# Monster.py
