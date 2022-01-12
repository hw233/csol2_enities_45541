# -*- coding: gb18030 -*-

import csdefine
from bwdebug import INFO_MSG
from CopyTeamQueuerMgr import Queuer
import spacecopymatcher.CopyTeamMatcher as test


class RoleSimulation :
	"""
	���ģ��
	"""
	def __init__( self, id, name, level, copies, blacklist, camp ) :
		self.id = id
		self.name = name
		self.level = level
		self.blacklist = blacklist
		self.copies = copies
		self.camp = camp
	
	def members( self ) :
		"""
		(self, name, duties, expectGuider)
		"""
		return (self, self.name, (csdefine.COPY_DUTY_DPS,), False)


class TeamEntitySimulation :
	"""
	����ģ��
	"""
	def __init__( self, id, captain, roles, isRecruiter ) :
		self.id = id
		self.captain = captain
		self.roles = roles
		self.isRecruiter = isRecruiter
		
		self.level = captain.level
		self.copies = captain.copies
		self.camp = captain.camp
		
		self.blacklist = []
		for r in roles :
			self.blacklist.extend( r.blacklist )	
		self.blacklist = tuple( self.blacklist )

	def members( self ) :
		members = []
		for r in self.roles :
			members.append( r.members() )
		return tuple(members) 


class CopyTeamQueuerMgrSimulation :
	"""
	������ģ��
	"""
	def __init__( self ) :
		self.__matchedInfo = None
		self.__matcher = None
	
	def popMatchedInfo( self ) :
		"""
		�ɹ�ƥ�����Ϣ
		"""
		info =  self.__matchedInfo
		self.__matchedInfo = None
		return info
	
	def setMatcher( self, matcher ) :
		self.__matcher = matcher

	
	def onQueuersMatched( self, copyLabel, copyLevel, queuers, dutiesDistribution, recruiter ) :
		"""
		"""
		INFO_MSG( "[QueuerMgr]: A group has formed: copy %s, level %i, queuers %s, dstb %s, recruiter %s" %\
			( copyLabel, copyLevel, str( [ q.id for q in queuers ] ), str( dutiesDistribution ), getattr( recruiter, "id", "None" ) ) )
		for queuer in queuers :
			self.__matcher.onQueuerLeaveMatcher( queuer )
		self.__matchedInfo = { "copyLabel" : copyLabel,  "queuers" : queuers }

class Check :
	"""
	ƥ��������
	"""
	def __init__( self, matcher ) :
		self.__matcher = matcher
	
	def checkMatchingInfo( self, copyLabel, camp, copyLevel, expectMatchingInfo ) :
		"""
		���黹����ƥ�����Ϣ����ʽΪ { ��n1,n2,n3,n4��: numbers },
		���� ni ������i����ҵ��Ŷ��߸�������n1,n2,n3,n4������һ������ƥ��ʵ����numbers�Ǹ�ƥ��ʵ��������
		���磺expectMatchingInfo = { (2,1,0,0) : 2 }
		��ʾ�� 2 �������ĸ���ƥ��ʵ����2��1����Ŷ��ߺ�1��2����Ŷ��߹��ɵĸ���ƥ��ʵ����
		"""
		info = {}
		matchUnit = self.__matcher.getMatchUnit( copyLabel, camp, copyLevel )
		if matchUnit is None :
			return False
		queuingGroups = matchUnit.queuingGroups()
		for iGroup in queuingGroups :
			key = [0,0,0,0]
			for q in iGroup.getQueuers() :
				key[ q.len -1 ] += 1
			key = tuple( key )
			if info.has_key( key ):
				info[ key ] += 1
			else :
				info[ key ] = 1
		INFO_MSG("%s" % info)
		INFO_MSG("%s" % expectMatchingInfo)
		return self.__equalDict( info, expectMatchingInfo )
	
	def checkMatchedInfo( self, expectMatchedInfo ) :
		"""
		�����ѳɹ�ƥ�����Ϣ, ��ʽΪ { "copyLabel" : copyLabel,  "queuers" : queuers }
		���磺expectMatchedInfo = { "copyLabel" : 'fu_ben_tian_guan_02', "queuers" : (q1,q2,q3) }
		��ʾ�Ŷ��� q1,q2,q3 �ɹ����� 'fu_ben_tian_guan_02'��
		"""
		info = self.__matcher.queuerMgr.popMatchedInfo()
		if info is None :
			return False
		if not info["copyLabel"] == expectMatchedInfo["copyLabel"] :
			return False
		
		return self.__equalList( info["queuers"], expectMatchedInfo["queuers"] )
	
	
	def __equalDict( self, dict1, dict2 ) :
		if not len( dict1 ) == len( dict2 ) :
			return False
		for k in dict1 :
			if not dict2.has_key( k ) :
				return False
			if not dict2[k] == dict1[k] :
				return False
		
		return True
	
	
	def __equalList( self, queuers1, queuers2 ) :
		list1 = [ q.id for q in queuers1 ]
		list2 = [ q.id for q in queuers2 ]
		for id in list1 :
			if not id in list2 :
				return False
		for id in list2 :
			if not id in list1 :
				return False
		
		return True


#*********************************************************************************
# ��ʼ����������ƥ������ƥ��������ʵ��
#*********************************************************************************
queuerMgr = CopyTeamQueuerMgrSimulation()
matcher = test.CopyTeamMatcher( queuerMgr )
queuerMgr.setMatcher( matcher )
check = Check( matcher )

#*********************************************************************************
# ����Ϊģ��Ĳ������ݣ����У�
#     r1 �������1��               team2_1 �������˶���1��
#   q_r1 �������1���ɵ��Ŷ��ߣ� q_team2_1 �������˶���1 ���ɵ��Ŷ��ߡ�
# �ر�� r0_otherCopy ����ͬ��������ң�team2_3_r �������˶���3����ļ�߶��顣   
#*********************************************************************************

# Role( id, name, level, copies, blacklist, camp )
r0_otherCopy = RoleSimulation( 10000, 'r0', 90, ('fu_ben_tian_guan_02',), (), csdefine.ENTITY_CAMP_DEMON )
r1 = RoleSimulation( 10001, 'r1', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
r2 = RoleSimulation( 10002, 'r2', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
r3 = RoleSimulation( 10003, 'r3', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
r4 = RoleSimulation( 10004, 'r4', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
r5 = RoleSimulation( 10005, 'r5', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
r6_otherCamp = RoleSimulation( 10006, 'r6', 90, ('fu_ben_tian_guan_02',), (), csdefine.ENTITY_CAMP_TAOISM )
r7_otherLevel = RoleSimulation( 10007, 'r7', 60, ('fu_ben_tian_guan_02',), (), csdefine.ENTITY_CAMP_DEMON )


# �������ɶ�������
m1  = RoleSimulation( 20001, 'm1',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m2  = RoleSimulation( 20002, 'm2',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m3  = RoleSimulation( 20003, 'm3',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m4  = RoleSimulation( 20004, 'm4',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m5  = RoleSimulation( 20005, 'm5',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m6  = RoleSimulation( 20006, 'm6',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m7  = RoleSimulation( 20007, 'm7',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m8  = RoleSimulation( 20008, 'm8',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m9  = RoleSimulation( 20009, 'm9',  90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m10 = RoleSimulation( 20010, 'm10', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m11 = RoleSimulation( 20011, 'm11', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m12 = RoleSimulation( 20012, 'm12', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m13 = RoleSimulation( 20013, 'm13', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m14 = RoleSimulation( 20014, 'm14', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m15 = RoleSimulation( 20015, 'm15', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m16 = RoleSimulation( 20016, 'm16', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m17 = RoleSimulation( 20017, 'm17', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m18 = RoleSimulation( 20018, 'm18', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m19 = RoleSimulation( 20019, 'm19', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m20 = RoleSimulation( 20020, 'm20', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m21 = RoleSimulation( 20021, 'm21', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m22 = RoleSimulation( 20022, 'm22', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m23 = RoleSimulation( 20023, 'm23', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m24 = RoleSimulation( 20024, 'm24', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )
m25 = RoleSimulation( 20025, 'm25', 90, ('fu_ben_feng_jian_shen_gong',), ( 'm26', ), csdefine.ENTITY_CAMP_DEMON )
m26 = RoleSimulation( 20026, 'm26', 90, ('fu_ben_feng_jian_shen_gong',), ( 'm25', ), csdefine.ENTITY_CAMP_DEMON )
m27 = RoleSimulation( 20027, 'm27', 90, ('fu_ben_feng_jian_shen_gong',), ( 'm25', ), csdefine.ENTITY_CAMP_DEMON )
m28 = RoleSimulation( 20028, 'm28', 90, ('fu_ben_feng_jian_shen_gong',), (), csdefine.ENTITY_CAMP_DEMON )

# TeamEntity( id, captain, roles, isRecruiter )
team2_1   = TeamEntitySimulation( 30001, m1, [ m1, m2 ], False )
team2_2   = TeamEntitySimulation( 30002, m3, [ m3, m4 ], False )
team2_3_r = TeamEntitySimulation( 30003, m5, [ m5, m6 ], True )
team2_4_r = TeamEntitySimulation( 30004, m7, [ m7, m8 ], True )
team3_1   = TeamEntitySimulation( 30005, m9, [ m9, m10, m11 ], False )
team3_2_r = TeamEntitySimulation( 30006, m12, [ m12, m13, m14 ], True )
team1_1_r = TeamEntitySimulation( 30007, m15, [ m15,], True )
team4_1_r = TeamEntitySimulation( 30008, m16, [ m16, m17, m18, m19], True )
team5_1   = TeamEntitySimulation( 30009, m20, [ m20, m21, m22, m23, m24], False )
team2_5   = TeamEntitySimulation( 30010, m25, [ m25, m26 ], False )
team1_2_r = TeamEntitySimulation( 30011, m28, [ m28,], True )


# Queuer( queuerMB, level, members, copies, blacklist, camp, isRecruiter = False )
q_r0_otherCopy = Queuer( r0_otherCopy, r0_otherCopy.level, ( r0_otherCopy.members(), ), \
                         r0_otherCopy.copies, r0_otherCopy.blacklist, r0_otherCopy.camp, False )
q_r6_otherCamp = Queuer( r6_otherCamp, r6_otherCamp.level, ( r6_otherCamp.members(), ), \
                         r6_otherCamp.copies, r6_otherCamp.blacklist, r6_otherCamp.camp, False )
q_r7_otherLevel = Queuer( r7_otherLevel, r7_otherLevel.level, ( r7_otherLevel.members(), ), \
                         r7_otherLevel.copies, r7_otherLevel.blacklist, r7_otherLevel.camp, False )

q_r1 = Queuer( r1, r1.level, ( r1.members(), ), r1.copies, r1.blacklist, r1.camp, False )
q_r2 = Queuer( r2, r2.level, ( r2.members(), ), r2.copies, r2.blacklist, r2.camp, False )
q_r3 = Queuer( r3, r3.level, ( r3.members(), ), r3.copies, r3.blacklist, r3.camp, False )
q_r4 = Queuer( r4, r4.level, ( r4.members(), ), r4.copies, r4.blacklist, r4.camp, False )
q_r5 = Queuer( r5, r5.level, ( r5.members(), ), r5.copies, r5.blacklist, r5.camp, False )
q_m25 = Queuer( m25, m25.level, ( m25.members(), ), m25.copies, m25.blacklist, m25.camp, False )
q_m26 = Queuer( m26, m26.level, ( m26.members(), ), m26.copies, m26.blacklist, m26.camp, False )
q_m27 = Queuer( m27, m27.level, ( m27.members(), ), m27.copies, m27.blacklist, m27.camp, False )

q_team2_1 = Queuer( team2_1.captain, team2_1.level, team2_1.members(), team2_1.copies, team2_1.blacklist, team2_1.camp, team2_1.isRecruiter )
q_team2_2 = Queuer( team2_2.captain, team2_2.level, team2_2.members(), team2_2.copies, team2_2.blacklist, team2_2.camp, team2_2.isRecruiter )
q_team2_3_r = Queuer( team2_3_r.captain, team2_3_r.level, team2_3_r.members(), team2_3_r.copies, team2_3_r.blacklist, team2_3_r.camp, team2_3_r.isRecruiter )
q_team2_4_r = Queuer( team2_4_r.captain, team2_4_r.level, team2_4_r.members(), team2_4_r.copies, team2_4_r.blacklist, team2_4_r.camp, team2_4_r.isRecruiter )
q_team3_1 = Queuer( team3_1.captain, team3_1.level, team3_1.members(), team3_1.copies, team3_1.blacklist, team3_1.camp, team3_1.isRecruiter )
q_team3_2_r = Queuer( team3_2_r.captain, team3_2_r.level, team3_2_r.members(), team3_2_r.copies, team3_2_r.blacklist, team3_2_r.camp, team3_2_r.isRecruiter )
q_team1_1_r = Queuer( team1_1_r.captain, team1_1_r.level, team1_1_r.members(), team1_1_r.copies, team1_1_r.blacklist, team1_1_r.camp, team1_1_r.isRecruiter )
q_team4_1_r = Queuer( team4_1_r.captain, team4_1_r.level, team4_1_r.members(), team4_1_r.copies, team4_1_r.blacklist, team4_1_r.camp, team4_1_r.isRecruiter )
q_team5_1 = Queuer( team5_1.captain, team5_1.level, team5_1.members(), team5_1.copies, team5_1.blacklist, team5_1.camp, team5_1.isRecruiter )
q_team2_5 = Queuer( team2_5.captain, team2_5.level, team2_5.members(), team2_5.copies, team2_5.blacklist, team2_5.camp, team2_5.isRecruiter )
q_team1_2_r = Queuer( team1_2_r.captain, team1_2_r.level, team1_2_r.members(), team1_2_r.copies, team1_2_r.blacklist, team1_2_r.camp, team1_2_r.isRecruiter )

#*********************************************************************************
#  ��ͬ����
#*********************************************************************************
matcher.clear()
matcher.onQueuerEnterMatcher( q_r0_otherCopy )
matcher.onQueuerEnterMatcher( q_r1 )

expectMatchingInfo1 = { (1,0,0,0) : 1 }
expectMatchingInfo2 = { (1,0,0,0) : 1 }
assert check.checkMatchingInfo( 'fu_ben_tian_guan_02', q_r0_otherCopy.camp, q_r0_otherCopy.copyLevel, expectMatchingInfo1)
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo2)


#*********************************************************************************
#  ��ͬ��Ӫ
#*********************************************************************************
matcher.clear()
matcher.onQueuerEnterMatcher( q_r6_otherCamp )
matcher.onQueuerEnterMatcher( q_r1 )

expectMatchingInfo1 = { (1,0,0,0) : 1 }
expectMatchingInfo2 = { (1,0,0,0) : 1 }
assert check.checkMatchingInfo( 'fu_ben_tian_guan_02', q_r6_otherCamp.camp, q_r6_otherCamp.copyLevel, expectMatchingInfo1)
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo2)


#*********************************************************************************
#  ��ͬ�ȼ��ε���ң� Ŀǰ10��Ϊһ�Σ��磺90-99 ��
#*********************************************************************************
matcher.clear()
matcher.onQueuerEnterMatcher( q_r7_otherLevel )
matcher.onQueuerEnterMatcher( q_r1 )

expectMatchingInfo1 = { (1,0,0,0) : 1 }
expectMatchingInfo2 = { (1,0,0,0) : 1 }
assert check.checkMatchingInfo( 'fu_ben_tian_guan_02', q_r7_otherLevel.camp, q_r7_otherLevel.copyLevel, expectMatchingInfo1)
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo2)


#*********************************************************************************
#  ͬһ����, �������
#*********************************************************************************

# ��� 1 ���������
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
expectMatchingInfo = { (1,0,0,0) : 1 }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

# ��� 2 ���������
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_r2 )
expectMatchingInfo = { (1,0,0,0) : 2,\
                       (2,0,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

# ��� 3 ���������
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_r3 )
expectMatchingInfo = { (1,0,0,0) : 3,\
                       (2,0,0,0) : 3,\
                       (3,0,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

# ��� 4 ���������,���������뿪����Ƿ���ȷ��
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_r3 )
matcher.onQueuerEnterMatcher( q_r4 )
expectMatchingInfo = { (1,0,0,0) : 4,\
                       (2,0,0,0) : 6,\
                       (3,0,0,0) : 4,\
                       (4,0,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)
matcher.onQueuerLeaveMatcher( q_r1 )
expectMatchingInfo = { (1,0,0,0) : 3,\
                       (2,0,0,0) : 3,\
                       (3,0,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)
matcher.onQueuerLeaveMatcher( q_r3 )
expectMatchingInfo = { (1,0,0,0) : 2,\
                       (2,0,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)
matcher.onQueuerLeaveMatcher( q_r2 )
expectMatchingInfo = { (1,0,0,0) : 1 }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)
matcher.onQueuerLeaveMatcher( q_r4 )
expectMatchingInfo = {}
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)


#*********************************************************************************
#  ͬһ����, ������� �� ���� ���
#*********************************************************************************

# ��� 1�� ������� �� 1�� 2�˷���ļ�߶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team2_1 )

expectMatchingInfo = { (1,0,0,0) : 1,\
                       (1,1,0,0) : 1,\
                       (0,1,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

# ��� 1�� ������� �� 1�� 2����ļ�߶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team2_3_r )

expectMatchingInfo = { (1,0,0,0) : 1,\
                       (1,1,0,0) : 1,\
                       (0,1,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

# ��� 1�� ������� �� 1�� rejoin �� 2�˷���ļ�߶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerRejoinMatcher( q_team2_1 )
q_team2_1.setPrior( False )

expectMatchingInfo = { (1,0,0,0) : 1,\
                       (1,1,0,0) : 1,\
                       (0,1,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

# ��� 1�� ������� �� 1�� rejoin �� 2����ļ�߶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerRejoinMatcher( q_team2_3_r )
q_team2_3_r.setPrior( False )

expectMatchingInfo = { (1,0,0,0) : 1,\
                       (1,1,0,0) : 1,\
                       (0,1,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

# ��� 2�� ������� �� 1�� 2�˷���ļ�߶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_team2_1 )

expectMatchingInfo = { (1,0,0,0) : 2,\
                       (2,0,0,0) : 1,\
                       (1,1,0,0) : 2,\
                       (2,1,0,0) : 1,\
                       (0,1,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_r1.camp, q_r1.copyLevel, expectMatchingInfo)

#*********************************************************************************
#  ͬһ����, ���� 
#*********************************************************************************

# ��� 2�� 2�˷���ļ�߶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_team2_2 )

expectMatchingInfo = { (0,1,0,0) : 2,\
                       (0,2,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team2_1.camp, q_team2_1.copyLevel, expectMatchingInfo)


# ��� 1�� 2����ļ�߶��� �� 1�� 2�˷���ļ�߶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_team2_3_r )

expectMatchingInfo = { (0,1,0,0) : 2,\
                       (0,2,0,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team2_1.camp, q_team2_1.copyLevel, expectMatchingInfo)


#*********************************************************************************
#  ������������������ƥ��ɹ�������� 
#  ע ���ڲ�����ļ�ߵ�����£�������Һ�1�˶������ɵ�Queuerû���κ����𣬹ʲ������֡�
#*********************************************************************************

# 5�� �������
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_r3 )
matcher.onQueuerEnterMatcher( q_r4 )
matcher.onQueuerEnterMatcher( q_r5 )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_r1, q_r2, q_r3, q_r4, q_r5) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s,%s,%s] Matched '%s' Successful !" % ( q_r1.memberNames , q_r2.memberNames ,\
q_r3.memberNames , q_r4.memberNames , q_r5.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# 3�� ������� 1�� 2�˶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_r3 )
matcher.onQueuerEnterMatcher( q_team2_1 )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_r1, q_r2, q_r3, q_team2_1) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s,%s] Matched '%s' Successful !" % ( q_r1.memberNames , q_r2.memberNames ,\
q_r3.memberNames , q_team2_1.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# 2�� ������� 1�� 3�˶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_team3_1 )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_r1, q_r2, q_team3_1) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_r1.memberNames , q_r2.memberNames ,\
q_team3_1.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# 1�� ������� 2�� 2�˶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_team2_2 )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_r1, q_team2_1, q_team2_2) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_r1.memberNames , q_team2_1.memberNames ,\
q_team2_2.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# 1�� ������� 1�� 4�˶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team4_1_r )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_r1, q_team4_1_r) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s] Matched '%s' Successful !" % ( q_r1.memberNames , q_team4_1_r.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# 1�� 2�˶��� 1�� 3�˶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_team3_1 )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team2_1, q_team3_1) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s] Matched '%s' Successful !" % ( q_team2_1.memberNames , q_team2_1.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# 1�� 5�˶���
matcher.clear()
matcher.onQueuerEnterMatcher( q_team5_1 )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team5_1 ,) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,] Matched '%s' Successful !" % ( q_team5_1.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

#*********************************************************************************
#  ����������������ļ�߳�ͻ�� �޷�ƥ��ɹ��� 
#*********************************************************************************

# 2�� 2����ļ�߶���( 2 �� 2 )
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team2_3_r )
matcher.onQueuerEnterMatcher( q_team2_4_r )
expectMatchingInfo = { (1,0,0,0) : 1,\
                       (0,1,0,0) : 2,\
                       (1,1,0,0) : 2, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team2_3_r.camp, q_team2_3_r.copyLevel, expectMatchingInfo)

# 1�� 2����ļ�߶��� �� 1�� 3����ļ�߶���( 2 �� 3 )
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_3_r )
matcher.onQueuerEnterMatcher( q_team3_2_r )
expectMatchingInfo = { (0,1,0,0) : 1,\
                       (0,0,1,0) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team2_3_r.camp, q_team2_3_r.copyLevel, expectMatchingInfo)

# 1�� 2����ļ�߶��� �� 1�� 1����ļ�߶���( 2 �� 1 )
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_team2_3_r )
matcher.onQueuerEnterMatcher( q_team1_1_r )
expectMatchingInfo = { (1,0,0,0) : 1,\
                       (0,1,0,0) : 2,\
                       (1,1,0,0) : 1,\
                       (0,2,0,0) : 1 }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team2_3_r.camp, q_team2_3_r.copyLevel, expectMatchingInfo)

# 1�� 3����ļ�߶��� �� 1�� 1����ļ�߶���( 3 �� 1 )
matcher.clear()
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team3_2_r )
matcher.onQueuerEnterMatcher( q_team1_1_r )
expectMatchingInfo = { (1,0,0,0) : 2,\
                       (0,0,1,0) : 1,\
                       (1,0,1,0) : 1,\
                       (2,0,0,0) : 1 }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team3_2_r.camp, q_team3_2_r.copyLevel, expectMatchingInfo)

# 1�� 4����ļ�߶��� �� 1�� 1����ļ�߶���( 4 �� 1 )
matcher.clear()
matcher.onQueuerEnterMatcher( q_team4_1_r )
matcher.onQueuerEnterMatcher( q_team1_1_r )
expectMatchingInfo = { (1,0,0,0) : 1,\
                       (0,0,0,1) : 1, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team4_1_r.camp, q_team4_1_r.copyLevel, expectMatchingInfo)


#*********************************************************************************
#  ����������������������ͻ�� �޷�ƥ��ɹ���
#  ����� 'm25' �� 'm26' ��Ϊ�������� ��� 'm27' �� 'm25' Ϊ�����������
#*********************************************************************************

# ��Ϊ������
matcher.clear()
matcher.onQueuerEnterMatcher( q_team3_1 )
matcher.onQueuerEnterMatcher( q_m25 )
matcher.onQueuerEnterMatcher( q_m26 )
expectMatchingInfo = { (1,0,0,0) : 2,\
                       (0,0,1,0) : 1,\
                       (1,0,1,0) : 2, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team3_1.camp, q_team3_1.copyLevel, expectMatchingInfo)

# ���������
matcher.clear()
matcher.onQueuerEnterMatcher( q_team3_1 )
matcher.onQueuerEnterMatcher( q_m25 )
matcher.onQueuerEnterMatcher( q_m27 )
expectMatchingInfo = { (1,0,0,0) : 2,\
                       (0,0,1,0) : 1,\
                       (1,0,1,0) : 2, }
assert check.checkMatchingInfo( 'fu_ben_feng_jian_shen_gong', q_team3_1.camp, q_team3_1.copyLevel, expectMatchingInfo)

# һ�����Ӧע�⣬��������ͻ��ָ����Queuer֮��ģ�����������ͻ�����������˶������ƥ�䣬���ܳɹ���
matcher.clear()
matcher.onQueuerEnterMatcher( q_team3_1 )
matcher.onQueuerEnterMatcher( q_team2_5 )
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team3_1, q_team2_5) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s] Matched '%s' Successful !" % ( q_team3_1.memberNames , q_team2_5.memberNames , 'fu_ben_feng_jian_shen_gong' ) )


#*********************************************************************************
# ���ȼ����ܵĲ�������:
# �Ŷ������ȼ�˳��R&P > R > P > not (R or P) ,����R����Ϊ��ļ�ߣ�P����������Ȩ��
# ���ȼ����ܵ����ԭ���Ǿ����ܵ������ȼ����ߵ��Ŷ��߸����ƥ�䵽������
#*********************************************************************************


#********************************************************
#���� ��R&P�Ŷ��ߡ� �Ƿ������� ��R�Ŷ��ߡ� 
#********************************************************
# ����ƥ�������������Ϊ�� q_team2_1 �� q_team1_1_r �� q_team1_2_r (Rejoin)�� q_team2_2
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_team1_1_r )
matcher.onQueuerRejoinMatcher( q_team1_2_r )
matcher.onQueuerEnterMatcher( q_team2_2 )
q_team1_2_r.setPrior( False )
# ����ƥ���Ƿ����Ԥ��
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team2_1, q_team1_2_r, q_team2_2) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_team2_1.memberNames , q_team1_2_r.memberNames ,\
q_team2_2.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# ��� ��R&P�Ŷ��ߡ� �뿪�ٽ������ȼ��ܷ��������ʹ��
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_team1_1_r )
matcher.onQueuerRejoinMatcher( q_team1_2_r )
matcher.onQueuerLeaveMatcher( q_team1_2_r )
matcher.onQueuerRejoinMatcher( q_team1_2_r )
matcher.onQueuerEnterMatcher( q_team2_2 )
q_team1_2_r.setPrior( False )
# ����ƥ���Ƿ����Ԥ��
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team2_1, q_team1_2_r, q_team2_2) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_team2_1.memberNames , q_team1_2_r.memberNames ,\
q_team2_2.memberNames , 'fu_ben_feng_jian_shen_gong' ) )


#********************************************************
#���� ��R�Ŷ��ߡ� �Ƿ������� ��P�Ŷ��ߡ� 
#********************************************************
# ����ƥ�������������Ϊ�� q_team2_1 �� q_r1 (Rejoin) �� q_team1_1_r �� q_team2_2
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerRejoinMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team1_1_r )
matcher.onQueuerEnterMatcher( q_team2_2 )
q_r1.setPrior( False )
# ����ƥ���Ƿ����Ԥ��
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team2_1, q_team1_1_r, q_team2_2) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_team2_1.memberNames , q_team1_1_r.memberNames ,\
q_team2_2.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# ��� ��R�Ŷ��ߡ� �뿪�ٽ������ȼ��ܷ��������ʹ��
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerRejoinMatcher( q_r1 )
matcher.onQueuerEnterMatcher( q_team1_1_r )
matcher.onQueuerLeaveMatcher( q_team1_1_r )
matcher.onQueuerEnterMatcher( q_team1_1_r )
matcher.onQueuerEnterMatcher( q_team2_2 )
q_r1.setPrior( False )
# ����ƥ���Ƿ����Ԥ��
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team2_1, q_team1_1_r, q_team2_2) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_team2_1.memberNames , q_team1_1_r.memberNames ,\
q_team2_2.memberNames , 'fu_ben_feng_jian_shen_gong' ) )


#********************************************************
#���� ��P�Ŷ��ߡ� �Ƿ������� ��not (R or P)�Ŷ��ߡ� 
#********************************************************
# ����ƥ�������������Ϊ�� q_team2_1 �� q_r1 �� q_r2 (Rejoin) �� q_team2_2
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerRejoinMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_team2_2 )
q_r2.setPrior( False )
# ����ƥ���Ƿ����Ԥ��
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team2_1, q_r2, q_team2_2) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_team2_1.memberNames , q_r2.memberNames ,\
q_team2_2.memberNames , 'fu_ben_feng_jian_shen_gong' ) )

# ��� ��P�Ŷ��ߡ� �뿪�ٽ������ȼ��ܷ��������ʹ��
matcher.clear()
matcher.onQueuerEnterMatcher( q_team2_1 )
matcher.onQueuerEnterMatcher( q_r1 )
matcher.onQueuerRejoinMatcher( q_r2 )
matcher.onQueuerLeaveMatcher( q_r2 )
matcher.onQueuerRejoinMatcher( q_r2 )
matcher.onQueuerEnterMatcher( q_team2_2 )
q_r2.setPrior( False )

# ����ƥ���Ƿ����Ԥ��
expectMatchedInfo = { "copyLabel" : 'fu_ben_feng_jian_shen_gong', "queuers" : (q_team2_1, q_r2, q_team2_2) }
assert check.checkMatchedInfo( expectMatchedInfo )
INFO_MSG( "[%s,%s,%s] Matched '%s' Successful !" % ( q_team2_1.memberNames , q_r2.memberNames ,\
q_team2_2.memberNames , 'fu_ben_feng_jian_shen_gong' ) )



INFO_MSG("Test Successful !")