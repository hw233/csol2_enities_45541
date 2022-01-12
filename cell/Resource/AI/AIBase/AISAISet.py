# -*- coding: gb18030 -*-

# $Id: AISAISet.py,v 1.1 2008-04-22 04:16:47 kebiao Exp $

import csstatus
import csdefine
import BigWorld
from bwdebug import *
from AIAction import AIAction

class AISAISet( AIAction ):
	"""
	设置SAI
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._saiData = []			# saiID 可以不在当前怪物身上

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		#AIAction.init( self, section )
		for s in section.values():
			aiID = s[ "AIID" ].asInt
			self._saiData.append( aiID )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if ai.getID() in entity.saiArray:	# 如果当前AIData已经在怪物的SAI列表里面，则不再加SAI
			return
		for aiID in self._saiData:
			entity.addSAI( aiID )

#
# $Log: not supported by cvs2svn $
#