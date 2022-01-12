# -*- coding: gb18030 -*-

# bigWorld
import BigWorld
# common
import csdefine
from bwdebug import INFO_MSG, ERROR_MSG
# base
#from CopyTeamFormulas import copyTeamFormulas
from BaseSpaceCopyFormulas import spaceCopyFormulas

#spaceCopyFormulas.loadCopiesData( "config/matchablecopies.xml" )
COPIES_NUMBER ={}
for copyLabel,summary in spaceCopyFormulas.getCopiesSummary().items():
	COPIES_NUMBER[copyLabel] = summary["mode"]


class CopyTeamMatcher :
	"""
	副本组队匹配器
	1.存储随机组队管理器实例
	2.存储所有的副本匹配单元
	3.进行匹配处理（查找对应的副本匹配单元，如果没有则创建）
	"""
	def __init__( self, queuerMgr ) :
		self.__queuerMgr = queuerMgr
		self.__matchUnits = {}              # { "copyLabel_camp_copyLevel" : CopySpaceNormalMatchUnit() }
	

	def onQueuerEnterMatcher( self, queuer) :
		"""
		排队者进入匹配器时所做处理
		"""
		for copyLabel in queuer.copies :
			matchUnit = self.getMatchUnit( copyLabel, queuer.camp, queuer.copyLevel, True )
			matchUnit.addQueuer( queuer )


	def onQueuerLeaveMatcher( self, queuer ) :
		"""
		排队者离开匹配器时所做处理
		"""
		for copyLabel in queuer.copies :
			matchUnit = self.getMatchUnit( copyLabel, queuer.camp, queuer.copyLevel )
			if matchUnit is None :
				INFO_MSG( "[CopyTeamMatcher]: matchUnit(%s,%s) missing but queuer(%i) still exist." %\
					( copyLabel, queuer.copyLevel, queuer.id ) )
			else :
				matchUnit.removeQueuer( queuer )

	
	def onQueuerRejoinMatcher( self, queuer ) :
		"""
		排队者再次进入匹配器
		"""
		queuer.setPrior( True )
		self.onQueuerEnterMatcher( queuer )

	
	def getMatchUnit( self, copyLabel, camp, copyLevel, createIfNotExist=False ) :
		"""
		查找对应的副本匹配单元，如果没有则新创建
		"""
		key = self.__getKey( copyLabel, camp, copyLevel )
		matchUnit = self.__matchUnits.get( key )
		if matchUnit is None :
			if createIfNotExist :
				matchUnit = CopySpaceNormalMatchUnit( self, copyLabel )
				self.__matchUnits[key] = matchUnit
				INFO_MSG( "[CopyTeamMatcher]: create matchUnit of copyLabel:%s." %( copyLabel ) )
			else :
				return None
		return matchUnit


	@property
	def queuerMgr( self ) :
		"""
		获取随机组队管理器
		"""
		return self.__queuerMgr

	# ----------------------------------------------------------------
	# debug
	# ----------------------------------------------------------------
	
	def clear( self ) :
		"""
		For debug
		"""
		for matchUnit in self.__matchUnits.values() :
			matchUnit.clear()
		self.__matchUnits.clear()
	
	@property
	def matchUnits( self ) :
		"""
		For debug
		"""
		return self.__matchUnits
		
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	
	def __getKey( self, copyLabel, camp, copyLevel ) :
		key = repr( copyLabel) + '_' + repr( camp) + '_' + repr( copyLevel)
		return key
	

class CopySpaceNormalMatchUnit :
	"""
	副本匹配单元 ：
	维护某个副本的一组匹配实例数据
	"""
	def __init__( self, matcher, copyLabel ) :
		self.__matcher = matcher
		self.__copyLabel = copyLabel
		self.__queuers = {}                     # {queuerID:queuer}
		# 根据优先级将副本匹配实例划分为 4 组
		self.__firstQueuingGroups  = []
		self.__secondQueuingGroups = []
		self.__thirdQueuingGroups = []
		self.__forthQueuingGroups = []

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	def hasQueuer( self, queuer ) :
		return queuer.id in self.__queuers


	def addQueuer( self, queuer ) :
		"""
		add queuer to matchUnit.
		"""
		
		if self.hasQueuer( queuer ) :
			ERROR_MSG( "[CopySpaceNormalMatchUnit]: queuer(ID %i) already in my queue." % queuer.id )
			self.removeQueuer( queuer )
		
		self.__queuers[queuer.id] = queuer 
		self.__onAddQueuer( queuer )

	
	def removeQueuer( self, queuer ) :
		"""
		remove queuer from matchUnit.
		"""
		if not self.hasQueuer( queuer ) :
			INFO_MSG( "[CopySpaceNormalMatchUnit]: queuer(ID %i) is not in my queue." % queuer.id )
			return
		#由于添加的时候是把queuer往每个group上加，因此删除的时间要把所有含有queuer的group全部删除
		self.__removeQueuerInGroups( self.__firstQueuingGroups , queuer )
		self.__removeQueuerInGroups( self.__secondQueuingGroups , queuer )
		self.__removeQueuerInGroups( self.__thirdQueuingGroups , queuer )
		self.__removeQueuerInGroups( self.__forthQueuingGroups , queuer )
		del self.__queuers[queuer.id]
	

	# ----------------------------------------------------------------
	# debug
	# ----------------------------------------------------------------
	
	def queuers( self ) :
		"""
		获取加入到匹配器的排队者
		"""
		return self.__queuers

	def queuingGroups( self ) :
		"""
		获取排队组
		"""
		queuingGroups = self.__firstQueuingGroups + self.__secondQueuingGroups \
		                + self.__thirdQueuingGroups + self.__forthQueuingGroups
		return queuingGroups

	
	def clear( self ) :
		for q in self.__queuers.values() :
			self.removeQueuer( q )
	

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------

	def __onAddQueuer( self, queuer ) :
		"""
		当有新的排队者加入副本匹配处理器后，所做的处理
		"""
		group = QueuerGroup( self.__copyLabel, (queuer,) )
		if  group.isMatchSuccessful() : 
			self.__onMatched( group )    #匹配好了，准备进入副本	
		else :
			# 更新优先级
			self.__updateQueuingGroupsOnAddQueuer( queuer )
		
	
	def __removeQueuerInGroups( self, groups, queuer ) :
		"""
		"""
		removeIndexlist = [] 
		index = 0
		for g in groups :
			if g.contain( queuer ) :
				removeIndexlist.append( index )
			index += 1
		removeIndexlist.reverse()
		for index in removeIndexlist :
			del groups[index]
	
	
	def __updateQueuingGroupsOnAddQueuer( self, queuer ) :
		"""
		在添加 queuer 根据 queuer 优先级的不同更新对应的 4 个 queuingGroups 列表。
		排队者优先级顺序：R&P > R > P > not(R or P) ( R 为招募者，P 为有优先权的排队者)
		副本匹配实例优先级顺序由其包含的优先级最高的排队者决定。
		"""
		group = QueuerGroup( self.__copyLabel, (queuer,) )
		
		# 分别对4个不同优先级的 groups 吸收 queuer，得到4个对应的新副本匹配实例列表。
		newList_1 = self.__groupsAbsorbQueuer( self.__firstQueuingGroups, queuer )
		newList_2 = self.__groupsAbsorbQueuer( self.__secondQueuingGroups, queuer )
		newList_3 = self.__groupsAbsorbQueuer( self.__thirdQueuingGroups, queuer )
		newList_4 = self.__groupsAbsorbQueuer( self.__forthQueuingGroups, queuer )
		
		if (newList_1 is None) or (newList_2 is None) or (newList_3 is None) or (newList_4 is None) :
			return
		
		# 根据 queuer 的优先级将这 4 个列表分别加入到不同的优先级 queuingGroups 列表中。
		if queuer.isRecruiter and queuer.prior :
			newList_1.append( group )
			self.__firstQueuingGroups += newList_1 + newList_2 + newList_3 + newList_4
		elif queuer.isRecruiter :
			newList_2.append( group )
			self.__firstQueuingGroups  += newList_1
			self.__secondQueuingGroups += newList_2 + newList_3 + newList_4
		elif queuer.prior :
			newList_3.append( group )
			self.__firstQueuingGroups  += newList_1
			self.__secondQueuingGroups += newList_2
			self.__thirdQueuingGroups  += newList_3 + newList_4
		else :
			newList_4.append( group )
			self.__firstQueuingGroups  += newList_1
			self.__secondQueuingGroups += newList_2
			self.__thirdQueuingGroups  += newList_3
			self.__forthQueuingGroups  += newList_4

	
	def __groupsAbsorbQueuer( self, groups, queuer ) :
		"""
		一组副本匹配实例 groups 依次吸收排队者 queuer，返回吸收后得到的新副本匹配实例列表。
		如果吸收过程中有可以匹配成功的，则返回 None。
		"""
		
		newList = []
		for iGroup in groups: 
			newGroup = iGroup.absorb( queuer )
			if newGroup and newGroup.isMatchSuccessful() :
				self.__onMatched( newGroup )
				return None
			elif newGroup :
				newList.append( newGroup )
		
		return newList


	def __onMatched( self, group ) :
		"""
		当有副本匹配实例匹配成功后，所做处理
		"""
		INFO_MSG( "[CopySpaceNormalMatchUnit]: %s has matched successfully." % str( group.dutiesDistribution() ))
		queuers = group.getQueuers()
		copyLevel = queuers[0].copyLevel
		self.__matcher.queuerMgr.onQueuersMatched( self.__copyLabel, copyLevel, queuers, group.dutiesDistribution(), group.recruiter() )


	# ----------------------------------------------------------------
	# pass
	# ----------------------------------------------------------------


class QueuerGroup :
	"""
	副本匹配实例 : 排队者集
	1、存储某个副本匹配实例中的排队者数据；
	2、验证是否吸收排队者；
	3、验证是否满足进入副本要求。
	"""
	def __init__( self, copyLabel, queuers ) :
		self.__queuers = {}                          # {queuerID:queuer}
		for q in queuers :
			self.__queuers[q.id] = q
		
		self.__copyLabel = copyLabel
		self.__dutiesDistribution = {}
		self.__absorbQueuerHandle = GroupAbsorbQueuerHandle( self )
	
	
	def getQueuers( self ):
		return self.__queuers.values()
	
	def absorb( self, queuer ) :
		"""
		吸收一个排队者。
		可以吸收 : 返回一个新的排队者集，包含新吸收的排队者。
		不可吸收 : 返回 None 。
		"""
		
		#满足条件,就吸收queuer
		if self.__absorbQueuerHandle.canAccept( queuer ) :
			queuerslist = []
			for q in self.__queuers.values() :
				queuerslist.append( q )
			queuerslist.append( queuer )
			queuers = tuple( queuerslist )
			newGroup = QueuerGroup( self.__copyLabel, queuers )
			return newGroup
		#不满足条件
		else :
			return None

	def isMatchSuccessful( self ) :
		"""
		验证是否满足进入副本要求.
		"""
		if self.len == COPIES_NUMBER[self.__copyLabel] :
			return True
		else :
			return False

	def contain( self, queuer ) :
		"""
		check if contains queuer.
		"""
		return queuer.id in self.__queuers


	def memberNames( self ) :
		"""
		names of group members
		"""
		names = []
		for queuer in self.__queuers.values() :
			names.extend( queuer.memberNames )
		return names


	def dutiesDistribution( self ) :
		"""
		"""
		return self.__dutiesDistribution.copy()

	def recruiter( self ) :
		"""
		get the queuer who is recruiter.
		"""
		for queuer in self.__queuers.values() :
			if queuer.isRecruiter :
				return queuer
		return None


	# ----------------------------------------------------------------
	# @property
	# ----------------------------------------------------------------
	
	@property
	def len( self ) :
		"""
		副本匹配实例中所包含的玩家个数
		"""
		len = 0
		for queuer in self.__queuers.values() :
			len += queuer.len
		return len
	
	@property
	def copyLabel( self ) :
		"""
		副本标签
		"""
		return self.__copyLabel
	


class GroupAbsorbQueuerHandle :
	"""
	副本匹配实例吸收排队者判断 ：
	1. self.canAccept(queuer) 为真，可吸收。
	2. self.canAccept(queuer) 为假，不可吸收。 
	"""
	def __init__( self, group ) :
		self.__group = group
	
	def canAccept( self, queuer ) :
		"""
		若可吸收，返回 True
		否则，返回 False
		"""
		if self.__allConditionsSatisfied( queuer ) :
			return True
		else :
			return False

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	
	def __allConditionsSatisfied( self, queuer ) :
		"""
		判断所有吸收条件是否都满足：玩家人数、招募者、黑名单 和 职务。
		"""
		if self.__playersNumberSatisfied(queuer) and self.__recruiterSatisfied(queuer) and self.__blacklistSatisfied(queuer) and self.__dutiesSatisfied(queuer) :
			return True
		else :
			return False
	
	def __playersNumberSatisfied( self, queuer ) :
		"""
		玩家人数限制
		"""
		if ( self.__group.len + queuer.len > COPIES_NUMBER[self.__group.copyLabel] ) :
			return False
		else :
			return True
	
	def __recruiterSatisfied( self, queuer ) :
		"""
		招募者限制
		"""
		if ( self.__group.recruiter() and queuer.isRecruiter) :
			return False
		else :
			return True
	
	def __blacklistSatisfied( self, queuer ) :
		"""
		黑名单限制
		"""
		blacklistHandle = BlacklistHandle()
		return blacklistHandle.groupAcceptQueuer( self.__group, queuer )
	
	def __dutiesSatisfied( self, queuer ) :
		"""
		职务限制,由于现在没有对职务的需求，返回 True
		"""
		return True
	

class BlacklistHandle :
	"""
	
	"""
	def __init__( self ) :
		pass
	
	def groupAcceptQueuer( self, group, queuer ) :
		"""
		"""
		for member in group.getQueuers() :
			if not self.__queuerAcceptQueuer( member, queuer ) :
				return False
		return True
	
	def __queuerAcceptQueuer( self, queuerA, queuerB ) :
		"""
		"""
		for name in queuerA.memberNames :
			if name in queuerB.blacklist :
				return False
		for name in queuerB.memberNames :
			if name in queuerA.blacklist :
				return False
		return True
	

