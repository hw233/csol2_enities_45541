# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import random
import items
import csdefine
import cschannel_msgs
g_items = items.instance()
import cPickle





class SpaceCopyRoleCompetition( SpaceCopy ):
	
	def __init__(self):
		"""
		���캯����
		"""
		self.setTemp( "rolesScore", {} )
		SpaceCopy.__init__( self )
		self.gradeList = []
		self.champion = {}
	
	def addRoleKillerCount( self, playerID ,playerDBID):
		"""
		define method
		������ҵ�ɱ�˴���
		"""
		rolesScore = self.queryTemp( "rolesScore" )
		if playerID not in rolesScore:
			rolesScore[ playerID ] = [ 0, playerDBID ]
		rolesScore[ playerID ][0] = rolesScore[ playerID ][0] + 1
		self.setTemp( "rolesScore", rolesScore )
	
	def noticeGrade( self ):
		if self.gradeList == []:
			gradeListCopy = []
		else:
			gradeListCopy = self.gradeList
		self.gradeList = []
		for e in self._players:
			entity = BigWorld.entities[e.id]
			entityName = entity.playerName
			entityScore = entity.queryTemp( "killPersonalCount", 0 )
			entityCompetitionTime = entity.queryTemp( "killPersonalTime", 0 )
			self.gradeList.append((entityName,entityScore,entityCompetitionTime))
		def judgeList( a, b):			#���������ж��ã�����ڶ���Ԫ�ز��Ȱ��մ�С�������������Ȱ��յ�����Ԫ�شӴ�С����
			if a[1] != b[1]:
				return cmp( b[1], a[1])
			else:
				return cmp( a[2], b[2])
		self.gradeList.sort( cmp = judgeList )
		if len(gradeListCopy) <= 5 and gradeListCopy == self.gradeList:
			return
		if len(gradeListCopy) > 5 and gradeListCopy[0:5] == self.gradeList[0:5]:
			return
		if len(self.gradeList) >= 5:
			gradeListCopy = self.gradeList[0:5]
		else:
			gradeListCopy = self.gradeList
		scoreList = []
		for iInfo in gradeListCopy:
			scoreList.append( ( iInfo[0], iInfo[1] ) )
		for e in self._players:
			e.client.receiveRoleCompetitionScore(scoreList)
