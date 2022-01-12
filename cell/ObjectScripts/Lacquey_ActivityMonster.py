# -*- coding: gb18030 -*-
#
# $Id: Lacquey_NPC108Star.py,v 1.5 2008-04-15 06:19:17 kebiao Exp $

"""
攻城小怪
"""
import BigWorld
from Monster import Monster

class Lacquey_ActivityMonster(Monster):
	"""
	攻城小怪
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
