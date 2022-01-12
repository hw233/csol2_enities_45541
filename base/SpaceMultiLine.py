# -*- coding: gb18030 -*-
#
# $Id: SpaceMultiLine.py,v 1.43 2008-08-09 06:02:41 kebiao Exp $

"""
"""

import BigWorld

import Language
from bwdebug import *
import time
import Love3
import Const
from SpaceNormal import SpaceNormal
from ObjectScripts.GameObjectFactory import GameObjectFactory

g_objFactory = GameObjectFactory.instance()

class SpaceMultiLine( SpaceNormal ):
	"""
	多线场景。
	@ivar domainMB:			一个声明的属性，记录了它的领域空间mailbox，用于某些需要通知其领域空间的操作，此接口如果为None则表示当前不可使用
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceNormal.__init__( self )
		self.lineNumber	= self.params[ "lineNumber" ]	# 空间的线号码

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceNormal.onEnter( self, baseMailbox, params )
		self.domainMB.incPlayerAmount( self.lineNumber )
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		玩家离开空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onLeave时的一些额外参数
		@type params: py_dict
		"""
		SpaceNormal.onLeave( self, baseMailbox, params )
		self.domainMB.decPlayerAmount( self.lineNumber )
	