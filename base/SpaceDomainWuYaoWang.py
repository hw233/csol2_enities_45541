# -*- coding: gb18030 -*-
#
# SpaceDomainShenGuiMiJing.py

"""
巫妖王宝藏副本domain
"""

import Language
import BigWorld
import csconst
import csstatus
from bwdebug import *
import Function
from SpaceDomainCopyTeam import SpaceDomainCopyTeam
import csdefine

# 领域类
class SpaceDomainWuYaoWang(SpaceDomainCopyTeam):
	"""
	巫妖王宝藏副本，允许单人进又允许队伍组队进的副本，只有队长才能创建副本
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomainCopyTeam.__init__( self )
		
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
		SpaceDomainCopyTeam.teleportEntity( self, position, direction, baseMailbox, params )
		self.teleportTeamMembers( position, direction, baseMailbox, params )
	
	def teleportTeamMembers( self, position, direction, baseMailbox, params ):
		"""
		把队友传入副本
		"""				
		isCallTeamMember = params.get( "isCallTeamMember", False )
		membersMailboxs = params.get( "membersMailboxs", [] )
		mailbox = params.get( "mailbox", 0 )
		if isCallTeamMember:	# 如果需要传送队员进入
			for membersMailbox in membersMailboxs:
				if membersMailbox.id != mailbox.id:
						membersMailbox.cell.gotoSpace( spaceDomain.name, ( 131.505, 1.91, -96.102 ), ( 0, 0, 0 ) )
