# -*- coding: gb18030 -*-

# $Id: AITemplate.py,v 1.1 2008-04-22 04:15:58 kebiao Exp $

import BigWorld
import csstatus
import csdefine
from AIBase import *
from bwdebug import *

class AITemplate( AIBase ):
	"""
	常规AI模板 所有普通AI都使用该模板
	"""
	def __init__( self ):
		AIBase.__init__( self )
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
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
	该模板不进行 eai, sai, 以及ai模板运行级别的设置
	主要用于一些如： 玩家传送巡逻触发， 以及没有继承aiinterface的entity使用
	"""
	def __init__( self ):
		AIBase.__init__( self )
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIBase.init( self, section )
			
#
# $Log: not supported by cvs2svn $
#