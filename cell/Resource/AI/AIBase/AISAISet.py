# -*- coding: gb18030 -*-

# $Id: AISAISet.py,v 1.1 2008-04-22 04:16:47 kebiao Exp $

import csstatus
import csdefine
import BigWorld
from bwdebug import *
from AIAction import AIAction

class AISAISet( AIAction ):
	"""
	����SAI
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._saiData = []			# saiID ���Բ��ڵ�ǰ��������

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		#AIAction.init( self, section )
		for s in section.values():
			aiID = s[ "AIID" ].asInt
			self._saiData.append( aiID )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if ai.getID() in entity.saiArray:	# �����ǰAIData�Ѿ��ڹ����SAI�б����棬���ټ�SAI
			return
		for aiID in self._saiData:
			entity.addSAI( aiID )

#
# $Log: not supported by cvs2svn $
#