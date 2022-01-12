# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
import NPC
import csstatus
import GUIFacade
import skills

class LivingTrainer( NPC.NPC ):
	"""
	�����NPC
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )
		
	def train( self, player, skillID ):
		"""
		@type skillID: INT16
		"""
		self.cell.trainPlayer( skillID )
		
	def oblive( self, player, skillID ):
		"""
		����һ������
		"""
		self.cell.oblive( skillID )
		
	def skillLevelUp( self, player, skillID ):
		"""
		����һ������
		"""
		self.cell.skillLevelUp( skillID )
		