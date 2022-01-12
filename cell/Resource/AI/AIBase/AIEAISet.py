# -*- coding: gb18030 -*-

# $Id: AIEAISet.py,v 1.1 2008-04-22 04:16:47 kebiao Exp $

import csstatus
import csdefine
import BigWorld
from bwdebug import *
from AIAction import AIAction

class AIEAISet( AIAction ):
	"""
	设置EAI
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._eaiData = []
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		#AIAction.init( self, section )
		for s in section.values():
			self._eaiData.append( s.asInt )
				
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		for aiID in self._eaiData:
			entity.addEAI( aiID )

#
# $Log: not supported by cvs2svn $
#