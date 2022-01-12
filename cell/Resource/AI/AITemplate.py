# -*- coding: gb18030 -*-

# $Id: AITemplate.py,v 1.1 2008-04-22 04:15:58 kebiao Exp $

import BigWorld
import csstatus
import csdefine
from AIBase import *
from bwdebug import *

class AITemplate( AIBase ):
	"""
	����AIģ�� ������ͨAI��ʹ�ø�ģ��
	"""
	def __init__( self ):
		AIBase.__init__( self )
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIBase.init( self, section )

		if section.has_key( "SAIClass" ):
			if len( section[ "SAIClass" ].values() ) > 0:
				inst = AISAISet()
				inst.init( section[ "SAIClass" ] )
				self._actions.append( inst )
			
		if section.has_key( "EAIClass" ):
			if len( section[ "EAIClass" ].values() ) > 0:
				inst = AIEAISet()
				inst.init( section[ "EAIClass" ] )
				self._actions.append( inst )

		if section.has_key( "defaultCycle" ) and section[ "defaultCycle" ].asInt != -1:
			inst = AISetSystemDefLevel()
			inst.init( section[ "defaultCycle" ] )
			self._actions.append( inst )
			
		if section.has_key( "currentCycle" ) and section[ "currentCycle" ].asInt != -1:
			inst = AISetSystemTempLevel()
			inst.init( section[ "currentCycle" ] )
			self._actions.append( inst )

class AITemplate1( AIBase ):
	"""
	��ģ�岻���� eai, sai, �Լ�aiģ�����м��������
	��Ҫ����һЩ�磺 ��Ҵ���Ѳ�ߴ����� �Լ�û�м̳�aiinterface��entityʹ��
	"""
	def __init__( self ):
		AIBase.__init__( self )
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIBase.init( self, section )
			
#
# $Log: not supported by cvs2svn $
#