# -*- coding: gb18030 -*-
#
# $Id: Functions.py,v 1.3 2008-01-15 06:06:34 phw Exp $

"""
"""

from bwdebug import *
from Resource.FuncsModule import m_functions

__FAILED_MSG_KEY__ = "faultMsgKey"   #配置中失败标记

class Functions:
	"""
	对话抽像层
	"""
	def __init__( self, section = None ):
		"""
		"""
		self._functions = []		# ARRAY of Function
		if section:
			self.init( section )
		
	def init( self, section ):
		"""
		@param section: xml data section
		@type  section: pyDataSection
		"""
			
		for sec in section.values():
			try:
				func = m_functions[sec.readString( "key" )]( sec )
			except KeyError, errstr:
				ERROR_MSG( "no such function. key: %s" % sec.readString( "key" ), errstr )
				continue
			info = { "func":func, __FAILED_MSG_KEY__:-1 }
			if sec.has_key( __FAILED_MSG_KEY__ ):
				info[ __FAILED_MSG_KEY__ ] = sec[ __FAILED_MSG_KEY__ ].asString
			self._functions.append( info )
	
	def do( self, player, talkEntity = None ):
		"""
		执行所有条件要求的操作
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		for func in self._functions:
			func[ "func" ].do( player, talkEntity )
		
	def valid( self, player, talkEntity = None ):
		"""
		查询所有条件，决定玩家是否能与自己对话。
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: (None)==True or (funcCall or -1) == False
		@rtype:  None or (funcCall or -1)
		"""
		for func in self._functions:
			if not func[ "func" ].valid( player, talkEntity ):
				return func[ __FAILED_MSG_KEY__ ]
		return None

	def buildDepend( self, manager ):
		"""
		@param manager: 类的管理者
		@type  manager: DialogManager
		"""
		if len( self._functions ) <= 0:
			return

		for i, func in enumerate( self._functions ):
			faultKey = func[ __FAILED_MSG_KEY__ ]
			self._functions[i][ __FAILED_MSG_KEY__ ] = -1
			if faultKey == "":
				continue
			func = manager.getDialog( faultKey )
			if func != None:
				self._functions[i][ __FAILED_MSG_KEY__ ] = func

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/05/18 08:41:34  kebiao
# 修改所有param 为targetEntity
# 加入某个功能失败 则调用失败功能
#
# Revision 1.1  2005/12/08 01:08:03  phw
# no message
#
#
