# -*- coding: gb18030 -*-
# $Id: Founder.py,v 1.2 2007-10-29 04:13:54 yangkai Exp $

import BigWorld
import NPC
from bwdebug import *

class Founder( NPC.NPC ):
	"""An Founder class for cell.
	����ʦNPC
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


# Founder.py
