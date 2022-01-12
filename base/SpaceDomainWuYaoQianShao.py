# -*- coding: gb18030 -*-
#
# SpaceDomainWuYaoQianShao.py

"""
巫妖前哨副本domain
"""

import Language
import BigWorld
import csconst
import csstatus
from bwdebug import *
import Function
from SpaceDomainCopyTeam import SpaceDomainCopyTeam

# 领域类
class SpaceDomainWuYaoQianShao(SpaceDomainCopyTeam):
	"""
	巫妖前哨副本，允许单人进又允许队伍组队进的副本，只有队长才能创建副本
	"""

	def findSpaceItem( self, params, createIfNotExisted = False ):
		"""
		virtual method.
		模板方法，通过给定的params来查找space，不同类型的space有不同的处理方式。
		重载此方法时必须严格按照参数中的说明进行实现。
		
		@param params: dict; 来自于space脚本中的packedDomainData()函数
		@param createIfNotExisted: bool; 当找不到时是否创建
		@return: instance of SpaceItem or None
		"""
		dbid = params.get( "dbID" )				# dbid参数来自与之相关的ObjectScripts/SpaceCopy.py的相关接口
		assert dbid is not None, "the key dbID is necessary."
		
		teamID = params.get( "teamID", 0 )		# get team entity's id
		spaceItem = None
		
		if teamID:
			# 必须组队才能进入副本
			captainDBID = params.get( "captainDBID", 0 )
			mailbox = params.get( "mailbox", 0 )
			membersMailboxs = params.get( "membersMailboxs", [] )
			isCallTeamMember = params.get( "isCallTeamMember", False )
			spaceNumber = self.getSpaceNumberByTeamID( teamID )
			if spaceNumber:
				# 找到与队伍相关联的space
				spaceItem = self.getSpaceItem( spaceNumber )
			else:
				if dbid == captainDBID  and createIfNotExisted:		# 必须队长才能创建新副本
					spaceItem = self.createSpaceItem( params )
					if isCallTeamMember:	# 如果需要传送队员进入
						for membersMailbox in membersMailboxs:
							if membersMailbox.id != mailbox.id:
								membersMailbox.cell.gotoSpace( self.name, ( 131.505, 1.91, -96.102 ), ( 0, 0, 0 ) )	# 把所有队员也传送到副本中
		
		return spaceItem
