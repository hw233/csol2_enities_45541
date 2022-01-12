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
	�������ƥ����
	1.�洢�����ӹ�����ʵ��
	2.�洢���еĸ���ƥ�䵥Ԫ
	3.����ƥ�䴦�����Ҷ�Ӧ�ĸ���ƥ�䵥Ԫ�����û���򴴽���
	"""
	def __init__( self, queuerMgr ) :
		self.__queuerMgr = queuerMgr
		self.__matchUnits = {}              # { "copyLabel_camp_copyLevel" : CopySpaceNormalMatchUnit() }
	

	def onQueuerEnterMatcher( self, queuer) :
		"""
		�Ŷ��߽���ƥ����ʱ��������
		"""
		for copyLabel in queuer.copies :
			matchUnit = self.getMatchUnit( copyLabel, queuer.camp, queuer.copyLevel, True )
			matchUnit.addQueuer( queuer )


	def onQueuerLeaveMatcher( self, queuer ) :
		"""
		�Ŷ����뿪ƥ����ʱ��������
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
		�Ŷ����ٴν���ƥ����
		"""
		queuer.setPrior( True )
		self.onQueuerEnterMatcher( queuer )

	
	def getMatchUnit( self, copyLabel, camp, copyLevel, createIfNotExist=False ) :
		"""
		���Ҷ�Ӧ�ĸ���ƥ�䵥Ԫ�����û�����´���
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
		��ȡ�����ӹ�����
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
	����ƥ�䵥Ԫ ��
	ά��ĳ��������һ��ƥ��ʵ������
	"""
	def __init__( self, matcher, copyLabel ) :
		self.__matcher = matcher
		self.__copyLabel = copyLabel
		self.__queuers = {}                     # {queuerID:queuer}
		# �������ȼ�������ƥ��ʵ������Ϊ 4 ��
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
		#������ӵ�ʱ���ǰ�queuer��ÿ��group�ϼӣ����ɾ����ʱ��Ҫ�����к���queuer��groupȫ��ɾ��
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
		��ȡ���뵽ƥ�������Ŷ���
		"""
		return self.__queuers

	def queuingGroups( self ) :
		"""
		��ȡ�Ŷ���
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
		�����µ��Ŷ��߼��븱��ƥ�䴦�����������Ĵ���
		"""
		group = QueuerGroup( self.__copyLabel, (queuer,) )
		if  group.isMatchSuccessful() : 
			self.__onMatched( group )    #ƥ����ˣ�׼�����븱��	
		else :
			# �������ȼ�
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
		����� queuer ���� queuer ���ȼ��Ĳ�ͬ���¶�Ӧ�� 4 �� queuingGroups �б�
		�Ŷ������ȼ�˳��R&P > R > P > not(R or P) ( R Ϊ��ļ�ߣ�P Ϊ������Ȩ���Ŷ���)
		����ƥ��ʵ�����ȼ�˳��������������ȼ���ߵ��Ŷ��߾�����
		"""
		group = QueuerGroup( self.__copyLabel, (queuer,) )
		
		# �ֱ��4����ͬ���ȼ��� groups ���� queuer���õ�4����Ӧ���¸���ƥ��ʵ���б�
		newList_1 = self.__groupsAbsorbQueuer( self.__firstQueuingGroups, queuer )
		newList_2 = self.__groupsAbsorbQueuer( self.__secondQueuingGroups, queuer )
		newList_3 = self.__groupsAbsorbQueuer( self.__thirdQueuingGroups, queuer )
		newList_4 = self.__groupsAbsorbQueuer( self.__forthQueuingGroups, queuer )
		
		if (newList_1 is None) or (newList_2 is None) or (newList_3 is None) or (newList_4 is None) :
			return
		
		# ���� queuer �����ȼ����� 4 ���б�ֱ���뵽��ͬ�����ȼ� queuingGroups �б��С�
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
		һ�鸱��ƥ��ʵ�� groups ���������Ŷ��� queuer���������պ�õ����¸���ƥ��ʵ���б�
		������չ������п���ƥ��ɹ��ģ��򷵻� None��
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
		���и���ƥ��ʵ��ƥ��ɹ�����������
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
	����ƥ��ʵ�� : �Ŷ��߼�
	1���洢ĳ������ƥ��ʵ���е��Ŷ������ݣ�
	2����֤�Ƿ������Ŷ��ߣ�
	3����֤�Ƿ�������븱��Ҫ��
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
		����һ���Ŷ��ߡ�
		�������� : ����һ���µ��Ŷ��߼������������յ��Ŷ��ߡ�
		�������� : ���� None ��
		"""
		
		#��������,������queuer
		if self.__absorbQueuerHandle.canAccept( queuer ) :
			queuerslist = []
			for q in self.__queuers.values() :
				queuerslist.append( q )
			queuerslist.append( queuer )
			queuers = tuple( queuerslist )
			newGroup = QueuerGroup( self.__copyLabel, queuers )
			return newGroup
		#����������
		else :
			return None

	def isMatchSuccessful( self ) :
		"""
		��֤�Ƿ�������븱��Ҫ��.
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
		����ƥ��ʵ��������������Ҹ���
		"""
		len = 0
		for queuer in self.__queuers.values() :
			len += queuer.len
		return len
	
	@property
	def copyLabel( self ) :
		"""
		������ǩ
		"""
		return self.__copyLabel
	


class GroupAbsorbQueuerHandle :
	"""
	����ƥ��ʵ�������Ŷ����ж� ��
	1. self.canAccept(queuer) Ϊ�棬�����ա�
	2. self.canAccept(queuer) Ϊ�٣��������ա� 
	"""
	def __init__( self, group ) :
		self.__group = group
	
	def canAccept( self, queuer ) :
		"""
		�������գ����� True
		���򣬷��� False
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
		�ж��������������Ƿ����㣺�����������ļ�ߡ������� �� ְ��
		"""
		if self.__playersNumberSatisfied(queuer) and self.__recruiterSatisfied(queuer) and self.__blacklistSatisfied(queuer) and self.__dutiesSatisfied(queuer) :
			return True
		else :
			return False
	
	def __playersNumberSatisfied( self, queuer ) :
		"""
		�����������
		"""
		if ( self.__group.len + queuer.len > COPIES_NUMBER[self.__group.copyLabel] ) :
			return False
		else :
			return True
	
	def __recruiterSatisfied( self, queuer ) :
		"""
		��ļ������
		"""
		if ( self.__group.recruiter() and queuer.isRecruiter) :
			return False
		else :
			return True
	
	def __blacklistSatisfied( self, queuer ) :
		"""
		����������
		"""
		blacklistHandle = BlacklistHandle()
		return blacklistHandle.groupAcceptQueuer( self.__group, queuer )
	
	def __dutiesSatisfied( self, queuer ) :
		"""
		ְ������,��������û�ж�ְ������󣬷��� True
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
	

