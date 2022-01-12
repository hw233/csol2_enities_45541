# -*- coding: gb18030 -*-
#

from SpaceDomainCopyTeam import SpaceDomainCopyTeam


class SpaceDomainGumigong(SpaceDomainCopyTeam):
	"""
	创天关
	"""
	def __init__( self ):
		SpaceDomainCopyTeam.__init__(self)


	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""

		baseMailbox.logonSpaceInSpaceCopy()


