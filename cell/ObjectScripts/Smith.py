# -*- coding: gb18030 -*-
# $Id: Smith.py,v 1.3 2007-10-29 04:15:22 yangkai Exp $

import BigWorld
import NPC
from bwdebug import *

class Smith( NPC.NPC ):
	"""
	Smith
	"""

	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		NPC.NPC.load( self, section )

	def initEntity( self, selfEntity ):
		"""
		virtual method.
		��ʼ���Լ���entity������
		"""
		NPC.NPC.initEntity( self, selfEntity )


# Smith.py
