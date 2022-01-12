# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCopyTeam.py,v 1.2 2008-01-28 06:02:10 kebiao Exp $

"""
即允许单人进又允许队伍组队进的副本（类似于wow的普通副本）

a1, a2 表示副本领域A中的两个副本实例；
p1, p2, p3表示三个独立的玩家；

进入副本时，如果有队伍ID相关联的副本，直接进入；
p1, p2, p3未组队，
	·p1进入a1, p2进入a2，这时p1和p2组队，队长为p1，此时
		·队伍立即解散，什么事情也没发生
		·p2离开a2，重进A，由于队伍没有副本记录，这时应该进入a1（即以队长的副本为队伍副本），且设置队伍副本记录
		·p1离开a1，重进A，由于队伍没有副本记录，这时应该进入a1（即以队长的副本为队伍副本），且设置队伍副本记录
			·以上两个情况发生后，如果p3加入队伍，进入副本A时，不论p3是否为队长，均应该进入队伍记录的副本（即a1）
		·p3加入队伍，是队长，进入A，由于队伍没有副本记录，这时应该进入最早创建的副本实例，且设置队伍副本记录
		·p3加入队伍，不是队长，进入A，由于队伍没有副本记录，这时应该进入a1（即以队长的副本为队伍副本），且设置队伍副本记录
			·以上三个情况发生后，此时
				·队伍解散，p1,p2重新组成队伍，进入A（p1原来是队长，有副本记录），发现p1有副本，但此副本是归属于一个队伍的，因此应该新建副本，设置队伍副本记录，设置副本创建人为队长
				·队长从p1改为p2，p1离开队伍，且离开当前副本，重进A，由于原副本是归属队伍的，所以，必须重建新副本，设置创建者为p1
					·问：原来副本a1的创建者谁？如果队伍解散，以后该副本归属谁？
					·答：原副本a1创建者丢失，如果此时队伍解散，出去后将不可能再找回此副本；
					·问：如果在副本中解散队伍后再次重新组建队伍，此副本是否还有效？
					·答：由于每个队伍id在短时间内都是唯一的，即使在副本内解散队伍后重组，也无法获取原来的副本，当玩家离开副本后重进时，必然是新建副本（没有队伍记录的副本，且当前队长所在的副本已属于另一个队伍，只能新建）；
				·队长人选改变，如果队伍解散，以后该副本归属谁？
					·根据上一条规则，那么副本将无法再找回，经过一定时间后自动消失；

p1,p2都没有进入A，p1,p2组队，进入A，此时
	·由于队伍没有副本记录，且两人都没有副本记录，因此创建新副本，且设置队伍为副本记录，设置副本创建人为队长

综合以上规则，副本地图进入判断先后顺序如下：
p1进入副本地图
	p1已组队
		根据队伍ID，找到了相应的space实例a1，直接进入a1，over。
		根据队伍ID，没找到相应的space实例
			根据队长dbid，找到了相应的space实例a1，且a1没有与队伍ID相关联，使a1与队伍ID相关联，进入a1，over。
			根据队长dbid，找不到相关的space实例，或找到的是已经与队伍ID相关联的
				根据剩余队员的dbid查找没有与队伍ID相关联的space实例，
					找到了，取最早创建的space实例a1，使a1与队伍ID相关联，进入a1，over。
					找不到，进入下一条
				上一条为否(没有找到)，创建新副本a1，使a1的创建者为队长DBID，使a1与队伍ID相关联，进入a1，over。
	p1未组队，以自己的dbid查找相关的space实例
		找到，直接进入，over。
		找不到，创建新副本a1，使a1的创建者为自己的dbid，进入a1，over。
"""

import Language
import BigWorld
import csconst
import csstatus
from bwdebug import *
import Function
from SpaceDomainCopy import SpaceDomainCopy
import csdefine

# 领域类
class SpaceDomainCopyTeam(SpaceDomainCopy):
	"""
	即允许单人进又允许队伍组队进的副本（类似于wow的普通副本）
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__(self)

		# 以下两个属性用于映射队伍entityID与spaceNumber之间的关系，
		# 用于当玩家进入某个space时，确定该已存在的space是否有队伍归属权；
		# 这两个属性中存在的值是两两关系，即某个属性存在某个key/value时，另一个也会有一个与之对应的value/key
		self.__spaceNumber2teamID = {}		# key = space number,	value = team entity id
#		self.teamID2spaceNumber = {}		# key = team entity id,	value = space number
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS

	def createSpaceItem( self, param ):
		"""
		virtual method.
		模板方法；使用param参数创建新的spaceItem
		"""
		# 由于当前的规则是创建者不会（也不可能）随着队长的改变而改变，
		# 如果当前副本的创建者离开了队伍，然后自己另外创建副本时，
		# 新的副本就会覆盖旧的副本，由于旧的副本保存的创建者还是现在的玩家，
		# 当旧的副本比该玩家新创建的副本先关闭时，必然会导致新的副本映射被删除，
		# 因此，为了避免这种bug，在创建新的副本时，我们必须先查找当前玩家是否已创建了副本，
		# 如果有则需要先把旧副本的创建者置0（即没有创建者或创建者丢失），才可以创建新的副本。
		spaceItem = self.getSpaceItemByDBID( param.get( "dbID" ) )
		if spaceItem:
			spaceItem.params["dbID"] = 0

		spaceItem = SpaceDomainCopy.createSpaceItem( self, param )
		if spaceItem and param.get( "teamID" ):	# 创建了新的spaceItem，且组队了（没组队值应该是0或None），则设置该副本为队伍副本
			self.setTeamRelation( param.get( "teamID" ), spaceItem.spaceNumber )
		return spaceItem

	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		模板方法；删除spaceItem
		"""
		SpaceDomainCopy.removeSpaceItem( self, spaceNumber )
		self.removeTeamRelation( spaceNumber )

	def setTeamRelation( self, teamEntityID, spaceNumber ):
		"""
		设置某个space与队伍的关系
		"""
		self.keyToSpaceNumber[teamEntityID] = spaceNumber
		self.__spaceNumber2teamID[spaceNumber] = teamEntityID
		SpaceDomainCopy.setTeamRelation( self, teamEntityID, spaceNumber )

	def removeTeamRelation( self, spaceNumber ):
		"""
		移除某个space与队伍的关系
		@param value: INT, spaceNumber
		"""
		if spaceNumber in self.__spaceNumber2teamID:
			v = self.__spaceNumber2teamID.pop( spaceNumber )
			self.keyToSpaceNumber.pop( v )
			SpaceDomainCopy.removeTeamRelation( self, v )

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		空间关闭，space entity销毁通知。
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		self.notifyTeamSpaceClosed( spaceNumber )		# 通知绑定的队伍副本关闭了
		self.removeTeamRelation( spaceNumber )	# 先移除队伍与spaceItem的关系
		SpaceDomainCopy.onSpaceCloseNotify( self, spaceNumber )

	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		副本是由一定规则开放的， 因此不允许登陆后能够呆在一个
		不是自己开启的副本中， 遇到此情况应该返回到上一次登陆的地方
		"""
		spaceItem = self.findSpaceItem( params, False )
		dbid = params[ "dbID" ]
		if spaceItem:
			if not self.isKickNotOnlineMember( spaceItem.spaceNumber, dbid ):
				spaceItem.logon( baseMailbox )
				self.clearKickNotOnlineMember( dbid )
				return
		
		self.clearKickNotOnlineMember( dbid )	
		baseMailbox.logonSpaceInSpaceCopy()

	def getSpaceNumberByTeamID( self, teamID ):
		"""
		"""
		if not self.keyToSpaceNumber.has_key( teamID ):
			return 0
		return self.keyToSpaceNumber[teamID]

	def queryBossesKilledByTeamID( self, querist, teamID ) :
		"""
		<Define method>
		@type	querist : MAILBOX
		@param	querist : 查询者，必须带有定义方法onQueryBossesKilledCallback
		@type	teamID : OBJECT_ID
		@param	teamID : 队伍ID
		"""
		spaceItem = self.getSpaceItem( self.getSpaceNumberByTeamID( teamID ) )
		if spaceItem is None :
			ERROR_MSG( "Can't find map space copy by teamID %i." % teamID )
			querist.onQueryBossesKilledCallback( teamID, -1 )						# 回调一个负数，表示出错了
		elif spaceItem.baseMailbox is None :
			ERROR_MSG( "SpaceCopy(%s) of team(ID:%i) base mailbox is None ." %\
				( self.__class__.__name__, teamID, ) )
			querist.onQueryBossesKilledCallback( teamID, -1 )						# 回调一个负数，表示出错了
		else :
			spaceItem.baseMailbox.queryBossesKilled( querist, teamID )

	def notifyTeamSpaceClosed( self, spaceNumber ) :
		"""
		通知和副本绑定的队伍，副本关闭了
		"""
		if spaceNumber in self.__spaceNumber2teamID :
			teamID = self.__spaceNumber2teamID[spaceNumber]
			BigWorld.globalBases["TeamManager"].teamRemoteCall( teamID, "onMatchedCopyClosed", () )
		else :
			# 走到这步可能的原因之一是，在之前匹配的副本关闭之前，队伍又重新匹配到了新的副本
			WARNING_MSG("Can't find map team to space(spaceNumber:%i)." % spaceNumber)

	def notifyTeamRaidFinished( self, spaceNumber ) :
		"""
		<Define method>
		通知和副本绑定的队伍，本次Raid已经完成
		@type		spaceNumber : SPACE_NUMBER
		@param		spaceNumber : 副本实例的唯一编号
		"""
		if spaceNumber in self.__spaceNumber2teamID :
			teamID = self.__spaceNumber2teamID[spaceNumber]
			BigWorld.globalBases["TeamManager"].teamRemoteCall( teamID, "onMatchedRaidFinished", () )
		else :
			# 走到这步可能的原因之一是，在之前匹配的副本关闭之前，队伍又重新匹配到了新的副本
			WARNING_MSG("Can't find map team to space(spaceNumber:%i)." % spaceNumber)


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/10/07 07:13:39  phw
# no message
#
#