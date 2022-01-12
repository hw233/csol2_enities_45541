# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCopyTemp.py,v 1.1 2007-10-07 07:13:39 phw Exp $

"""
"""

import Language
import BigWorld
from SpaceItem import SpaceItem
from bwdebug import *
from SpaceDomain import SpaceDomain
import csdefine

# 领域类
class SpaceDomainCopyTemp(SpaceDomain):
	"""
	临时副本，用于让cell的NPC等entity主动通过requestCreateSpace()接口来获取新副本实例；
	即此副本不提供通过标准的接口进入的方式；
	使用此领域时，副本的"waitingCycle"参数应该设置少于1秒的时间，以减少冗余副本实例数量；
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COPY_TEMP
		

	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		raise RuntimeError, "I can't implement the functional."
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		raise RuntimeError, "I can't implement the functional."

#
# $Log: not supported by cvs2svn $
#