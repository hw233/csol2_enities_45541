# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.5 2008-04-16 05:50:45 kebiao Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from SpaceCopy import SpaceCopy

class SpaceCopyFirstMap( SpaceCopy ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, selfEntity, baseMailBox, params ):
		"""
		virtual method.
		玩家进入了空间
		@param baseMailbox: cell mailbox
		@type baseMailbox: mailbox
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "SpaceDomain_FirstMap" ].incPlayerAmount( selfEntity.spaceNumber )

	def onLeave( self, selfEntity, baseMailBox, params  ):
		"""
		virtual method.
		玩家离开空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "SpaceDomain_FirstMap" ].decPlayerAmount( selfEntity.spaceNumber )
		
# SpaceNormal.py
