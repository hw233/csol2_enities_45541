# -*- coding: gb18030 -*-
#

import BigWorld
import Const
import csconst
import time
from bwdebug import *


class GameRankingManager( BigWorld.Base ):
	"""
	��Ϸ���а�ӿ�
	"""
	def __init__( self ):
		"""
		��ʼ�� ��ȡ���е�����
		"""
		self.registerGlobally( "GameRankingManager", self._onRegisterManager )		#ע���Լ���ȫ����
		self.rankings 		= {}													#����
		self.updateTime		= 0														#���ݸ��µ�ʱ��
		self.oldrankings	= {}													#������
		self.newflag = False
		self.oldflag = False		



	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register GameRankingManager Fail!" )
			self.registerGlobally( "GameRankingManager", self._onRegisterManager )
		else:
			BigWorld.baseAppData["GameRankingManager"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("GameRankingManager Create Complete!")
			self.LoadRankingDatas()									# ������� ȥ�������е���������

	def LoadRankingDatas( self ):
		"""
		�������е���������
		"""
		self.newflag = False
		self.oldflag = False
		def onGetDatas(results, rows, errstr):
			"""
			��ȡ����������
			"""
			if errstr:
				ERROR_MSG( "get player level ranking failed: %s" % errstr  )
				return
			if not results:
				return
			self.rankings = {}
			for result in results:
				if self.rankings.has_key( int(result[0]) ):
					self.rankings[ int(result[0]) ].append(result[1:])
				else:
					self.rankings[ int(result[0]) ] = [result[1:] ]
			self.updateTime = int(time.time())							# ��������ˢ�µ�ʱ��
			INFO_MSG("update Ranking List time is %s ,rankDatas = %s"%(str(self.updateTime), self.rankings))
			self.newflag = True
			if self.newflag and self.oldflag:
				calSort()
				
		def onGetOldDatas( results, rows, errstr ):
			if errstr:
				ERROR_MSG( "get player level ranking failed: %s" % errstr  )
				return
			if not results:
				return
			self.oldrankings = {}
			for result in results:
				if self.oldrankings.has_key( int(result[0]) ):
					self.oldrankings[ int(result[0]) ].append(result[1:])
				else:
					self.oldrankings[ int(result[0]) ] = [result[1:] ]	
			self.oldflag = True	
			if self.newflag and self.oldflag:
				calSort()

		def calSort():
			print "calSort()",self.newflag, self.oldflag
			for key, value in self.rankings.items():
				newindex = 1
				for item in value:
					playername = item[1]
					oldindex = getIndex(key, playername)
					if oldindex:
						self.rankings[key][newindex - 1][0] = oldindex - newindex
					else:
						self.rankings[key][newindex - 1][0] = len(self.rankings[key]) + 1 - newindex
					newindex += 1			
		
		def getIndex( type ,playername):
			playernamelist = [item[1] for item in self.oldrankings[type]]
			if type in self.oldrankings.keys() and self.oldrankings[type] is not None:
				playernamelist = [item[1] for item in self.oldrankings[type]]
				if playername in playernamelist:
					return playernamelist.index(playername) + 1
			elif type in self.oldrankings.keys():
				return len(self.oldrankings[type]) + 1
			else:
				return len(self.rankings[type]) + 1
		
		sqlnew = "select type,param1,param2,param3,param4,param5,param6 from custom_Ranking order by id ASC"
		BigWorld.executeRawDatabaseCommand( sqlnew, onGetDatas )
		sqlold = "select type,param1,param2,param3,param4,param5,param6 from custom_oldRanking order by id ASC"
		BigWorld.executeRawDatabaseCommand( sqlold, onGetOldDatas )


	def getRankingDatas( self, rtype ):
		"""
		��ȡ����������
		@type  rtype:UINT8
		@param rtype:���ݵ�����
		"""
		try:
			return self.rankings[rtype]
		except:
			return []

	def getRankingDatasEx( self, rtype, begin, num ):
		"""
		��ȡ���������� ����ָ����ʼ�����ݺ�����
		@type  rtype:int
		@param rtype:���ݵ�����
		@type  begin:int
		@param begin:��ʼ������
		@type    num:int
		@param   num:����
		"""
		try:
			return self.rankings[rtype][begin:begin+num]
		except:
			return []

	def showGameRanking( self, role ):
		"""
		@define method
		֪ͨ��ҿͻ��˽�������
		@type  role : mailbox
		@param role : ��ҵ�mailbox
		"""
		role.client.onShowGameRanking( self.updateTime )

	def queryRankingData( self, role, rankingType, beginIndex  ):
		"""
		@define method
		֪ͨ��ҿͻ��˽�������
		@type  role : mailbox
		@param role : ��ҵ�mailbox
		@type  rankingType: UINT8
		@param rankingType: ���ݵ����� �� �����������
		@type  beginIndex : UINT8
		@param beginIndex : ���ݷ��͵���ʼλ��
		"""
		datas = self.getRankingDatasEx(rankingType, beginIndex, csconst.GAMERANKING_SEND_DATANUM )
		if not datas:
			role.client.onQueryRankingEnd( rankingType )
		else:
			role.client.onQueryRankingData( rankingType,beginIndex,datas )
