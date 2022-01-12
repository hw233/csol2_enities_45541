# -*- coding: gb18030 -*-

# $Id: AISetSystemDefLevel.py,v 1.1 2008-04-22 04:16:47 kebiao Exp $

import csstatus
import csdefine
import BigWorld
from bwdebug import *
from AIAction import AIAction

class AISetSystemDefLevel( AIAction ):
	"""
	����ϵͳĬ�����м���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._level = 0
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		#AIAction.init( self, section )
		self._level	 = section.asInt
				
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if not entity.isDestroyed:
			entity.setDefaultAILevel( self._level )

#
# $Log: not supported by cvs2svn $
#