# -*-coding: gb18030 -*-
#
#

import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus

from SpaceCopy import SpaceCopy


class SpaceCopyTeamChallenge( SpaceCopy ):
	"""
	组队擂台副本空间全局实例脚本
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		
		
	def load( self, section ):
		"""
		从配置中加载数据
		
		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		