# -*- coding: gb18030 -*-

# bigworld
import BigWorld
# python
import time
# common
import csdefine
from bwdebug import INFO_MSG, ERROR_MSG, WARNING_MSG
# local_default
import csstatus
# base
from BaseSpaceCopyFormulas import spaceCopyFormulas
from spacecopymatcher.CopyTeamMatcher import CopyTeamMatcher
from interface.CopyTeamMatchedQueuerInterface import CopyTeamMatchedQueuerInterface



class CopyTeamQueuerMgr( BigWorld.Base, CopyTeamMatchedQueuerInterface ) :
	"""
	副本组队管理器
	1.维护排队列表信息（增删改查）
	2.排队列表信息变动时，通知匹配实例管理器
	3.接收各种排队队列玩家（或队伍）的一些自身感兴趣的行为消息
	4.中转玩家（或队伍）在匹配过程中的操作
	"""

	def __init__( self ) :
		BigWorld.Base.__init__( self )
		CopyTeamMatchedQueuerInterface.__init__( self )
		self.__queuers = {}					# {queuerID:queuer}
		self.__matcher = CopyTeamMatcher( self )
		self.registerGlobally( "copyTeamQueuerMgr", self.__registerGlobalCB )

	def __registerGlobalCB( self, complete ) :
		"""
		"""
		if complete :
			INFO_MSG( "register copyTeamQueuerMgr Complete!" )
			BigWorld.globalData["copyTeamQueuerMgr"] = self				# 注册到所有的服务器中
		else :
			ERROR_MSG( "Register copyTeamQueuerMgr Fail!" )
			self.registerGlobally( "copyTeamQueuerMgr", self.__registerGlobalCB )

	def __addQueuer(self,queuer) :	
		"""
		"""
		if self.hasQueuer(queuer.id) :
			ERROR_MSG("[QueuerMgr]: %i is already exist." % queuer.id)
			self.removeQueuer(queuer.id)
		
		self.__queuers[queuer.id] = queuer
		self.__onAddQueuer(queuer)

	def __onAddQueuer(self, queuer) :
		queuer.mailbox.onJoinCopyMatcherQueue()
		self.__matcher.onQueuerEnterMatcher( queuer )
	
	

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	def onReceiveJoinRequest( self, queuerMB, level, members, copies, blacklist, camp, isRecruiter = False ) :
		"""
		<Define method>
		接收到加入请求后调用
		@type		requesterMB : MAILBOX
		@param		requesterMB : 请求者的mailbox（可能是玩家的，也可能是teamEntity的）
		@type		level : UINT8
		@param		level : 请求者的等级
		@type		members : PY_ARGS：((mailbox, name, duties, expectGuider),)
		@param		members : 请求者成员信息
		@type		copies : STRING_TUPLE
		@param		copies : 前往的副本
		@type		blacklist : STRING_TUPLE
		@param		blacklist : 黑名单列表
		@type		camp : UINT8
		@param		camp : 请求者的阵营
		@type		isRecruiter : BOOL
		@param		isRecruiter : 是否是招募者
		"""
		INFO_MSG( "%s,%s,%s,%s,%s,%s,%s," % (queuerMB, level, members, copies, blacklist, camp, isRecruiter) )
		queuer = Queuer( queuerMB,
						spaceCopyFormulas.formatCopyLevel( level ),
						members,
						copies,
						blacklist,
						camp,
						isRecruiter,				
						)
		self.__addQueuer(queuer)
	
	
	def removeQueuer( self, queuerID, reason = csstatus.CTM_LEAVE_QUEUE_SILENTLY ) :
		"""
		<Define method>
		@type		queuerID : OBJECT_ID
		@param		queuerID : 排队者的ID
		@type		reason : INT32
		@param		reason : 移除的原因（在csstatus中定义）
		"""
		queuer = self.getQueuerByID( queuerID)
		if queuer is None :
			WARNING_MSG( "[QueuerMgr]: queuer(ID %i) is not exist." % queuerID )
		else :
			self.__matcher.onQueuerLeaveMatcher( queuer )
			del self.__queuers[queuer.id]
			queuer.mailbox.onLeaveCopyMatcherQueue( reason )
	
	def hasQueuer( self, queuerID ) :
		"""
		"""
		return queuerID in self.__queuers
	
	def queuerRejoinMatcher( self, queuer ) :
		"""
		"""
		queuer.mailbox.onRejoinCopyMatcherQueue()
		self.__matcher.onQueuerRejoinMatcher( queuer )


	def querySameLevelQueuersNumber(self, playerMB, playerLevel ):
		"""
		查询与playerLevel同一等级段的queuer个数
		<Define Method>
		@type		playerMB : MAILBOX
		@param		playerMB : 玩家的mailbox
		@type		playerLevel : UINT8
		@param		playerLevel : 玩家的等级
		"""
		formatCopyLevel = spaceCopyFormulas.formatCopyLevel( playerLevel)
		levelQueuers = [queuer for queuer in self.__queuers.values() if queuer.copyLevel == formatCopyLevel]
		sameLevelQueuersNumber = len(levelQueuers)
		playerMB.onQuerySameLevelQueuersNumber(sameLevelQueuersNumber)
		
	def getQueuerByID( self, queuerID ) :
		"""
		"""
		return self.__queuers.get( queuerID )
		

	# ----------------------------------------------------------------
	# debug methods
	# ----------------------------------------------------------------
	@property
	def queuers( self ) :
		"""
		<For debug>
		"""
		return self.__queuers
	
	@property
	def matcher( self ) :
		"""
		<For debug>
		"""
		return self.__matcher
	

	# ----------------------------------------------------------------
	# operations after group formed
	# ----------------------------------------------------------------
	def onQueuersMatched( self, copyLabel, copyLevel, queuers, dutiesDistribution, recruiter ) :
		"""
		"""
		INFO_MSG( "[QueuerMgr]: A group has formed: copy %s, level %i, queuers %s, dstb %s, recruiter %s" %\
			( copyLabel, copyLevel, str( [ q.id for q in queuers ] ), str( dutiesDistribution ), getattr( recruiter, "id", "None" ) ) )
		for queuer in queuers :
			self.__matcher.onQueuerLeaveMatcher( queuer )
		self.onGroupFormed( copyLabel, copyLevel, queuers, dutiesDistribution, recruiter )
	


class Queuer( object ) :
	"""
	纯数据类，只保存参与排队玩家（或队伍）的信息
	"""
	
	def __init__( self, queuerMB, copyLevel, members, copies, blacklist,camp, isRecruiter  ) :
		self._id = queuerMB.id
		self._queuerMB = queuerMB
		self._copies = tuple( copies )
		self._copyLevel = copyLevel
		self._members = members								# ((mailbox, name, duties, expectGuider),)
		self._blacklist = tuple( blacklist )
		self._isRecruiter = isRecruiter						# 是否是招募者
		self._camp = camp
		self._prior = False								# 是否有优先匹配权
		self._queueTime = time.time()
		
	
	@property
	def id( self ) :
		return self._id
		
	
	@property
	def camp( self ) :
		return self._camp

	@property
	def len( self ) :
		return len( self._members )
	@property
	def mailbox( self ) :
		return self._queuerMB

	@property
	def memberMailboxes( self ) :
		return tuple( m[0] for m in self._members )

	@property
	def memberNames( self ) :
		return tuple( m[1] for m in self._members )

	@property
	def memberDuties( self ) :
		return dict( (m[0].id, m[2]) for m in self._members )

	@property
	def guiderCandidates( self ) :
		return tuple( (m[0], m[3]) for m in self._members )

	@property
	def copies( self ) :
		return self._copies[:]

	@property
	def copyLevel( self ) :
		return self._copyLevel

	@property
	def blacklist( self ) :
		return self._blacklist[:]

	@property
	def isRecruiter( self ) :
		return self._isRecruiter

	@property
	def prior( self ) :
		return self._prior
	
	@property
	def priorityValue( self ) :
		"""
		优先值，用来量化优先级的大小。
		如 isRecruiter 为 2，prior 为 1，isRecruiter and prior 为 3，什么都不是为 0。
		"""
		value = 0
		if self._isRecruiter :
			value += 2
		if self._prior :
			value += 1
		return value
	

	@property
	def queueTime( self ) :
		return self._queueTime

	def nameOfMember( self, memberID ) :
		for m in self._members :
			if m[0].id == memberID :
				return m[1]

	def setPrior( self, prior ) :
		self._prior = prior


