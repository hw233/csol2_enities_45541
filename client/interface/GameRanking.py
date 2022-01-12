# -*- coding: gb18030 -*-
#

import BigWorld
import Const
import csconst
import event.EventCenter as ECenter
from Function import Functor

class GameRanking:
	"""
	���а�����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		self.gr_upDateTime 	= 0							# ��¼�ϴλ�ȡ�����ݵĸ���ʱ�䣬�����ʱ��ͷ�������ǰ���ݵĸ���ʱ���Ǻϼ�Ϊ��������,
														# ��û�б�Ҫ������������������ʱ��Ϊ0��ʾ֮ǰû�л�ȡ������
		self.gr_datas 			= {}						# ���������
		self.gr_datasInfo		= {}						# �������ݵķ������ like {1:12, 2: 15} ��ʾ��һ�෢����12�� ������12��ʼ��������......
		self.__callback_id  = 0							# callback��ID
		self.gr_rType			= Const.LEVELRANKING	# ��ǰ��ȡ�����а����� Ĭ��Ϊ�ȼ�����
		self.queryCallID = 0							# �ͻ�����������callbackID

	def onQueryRankingData( self, rankingType, beginIndex, rankingDatas ):
		"""
		��ȡ������
		@param  rankingType  : ��ǰ��ȡ�����а�����ͣ�Ŀǰֻ�����¼���
								LEVELRANKING			=	1		# ��ҵȼ�����
								MONEYRANKING			=	2		# ��ҽ�Ǯ����
								TONGRANKING				=	3		# �������
								FAMILYRANKING			=	4		# ��������
								PFRANKING				=	5		# PK���а�
		@type   rankingType  : UINT8
		@param  beginIndex   : ��ǰ��ȡ�����ݵ���ʼ����
		@type   beginIndex   : UINT8
		@param  rankingDatas : ���������͹�������������
		@type   rankingDatas : LIST
		"""
		if not self.gr_datas.has_key( rankingType):
			self.gr_datas[rankingType] = []
		self.gr_datas[rankingType].extend( rankingDatas )
		self.gr_datasInfo[rankingType] += len(rankingDatas)							# ���Ӵ˴��������������
		self.__callback_id = BigWorld.callback( 0.2, self.queryRankingData )		# �����µ�����
		ECenter.fireEvent( "EVT_ON_RECEIVE_RANK_DATA", rankingType, beginIndex, rankingDatas )

	def onQueryRankingEnd( self, rankingType ):
		"""
		��ȡ�����͵����а��������
		"""
		self.gr_datasInfo[rankingType] = -1
		ECenter.fireEvent( "EVT_ON_SET_RANKBTNS_STATE", rankingType, True )
		if rankingType != self.gr_rType and self.gr_datasInfo[self.gr_rType] != -1:													# �����������ݲ��ǵ�ǰҪ��ȡ������ ��������
			self.__callback_id = BigWorld.callback( 0.2, self.queryRankingData )		# �����µ�����
		else:
			self.__callback_id = 0														# �������TIMER ID ����


	def queryRankingData( self ):
		"""
		���������������
		"""
		BigWorld.cancelCallback( self.__callback_id )
		self.base.queryRankingData( self.gr_rType, self.gr_datasInfo[self.gr_rType] )		# ���������������
		ECenter.fireEvent( "EVT_ON_SET_RANKBTNS_STATE", self.gr_rType, False )

	def onShowGameRanking( self, updateTime ):
		"""
		������֪ͨ�ͻ�����ʾ���а�,�����߿ͻ���������������
		@param  updateTime : ��ǰ���ݸ��µ�ʱ�䣬������ͻ��˵�ǰ���ݱȶԣ��Ƿ���Ҫ�������������������
		@type   updateTime : UINT32
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_RANK_WINDOW" )
		if self.gr_upDateTime != updateTime:							# ���û�л��߲������µ�����
			self.repairGameRankingData()										# �ָ�����
			self.gr_upDateTime		= updateTime						# ��¼�������ݷ��������µ�ʱ��
		self.beginQueryGameRanking( Const.LEVELRANKING )						# ��һ��Ĭ��ȥ��ȡ�ȼ����е����ݣ���Ϊ���Ľ��洦�ڵ�һλ

	def repairGameRankingData( self ):
		"""
		�ָ�����
		"""
		self.__callback_id  = 0						# callback��ID
		self.gr_datas 			= {}					# ���������
		self.gr_upDateTime 	= 0						# �������ݸ��µ�ʱ��
		self.gr_rType			= Const.LEVELRANKING	# ��ǰ��ȡ�����а�����
		self.gr_datasInfo		= {}

	def __setRanking( self, rType ):
		"""
		������ǰ��ȡ�����а�����
		@type  rType :	UINT8
		@param rType :	Ҫ��ȡ�����а�����ͣ�Ŀǰֻ�����¼���
						LEVELRANKING			=	1		# ��ҵȼ�����
						MONEYRANKING			=	2		# ��ҽ�Ǯ����
						TONGRANKING				=	3		# �������
						FAMILYRANKING			=	4		# ��������
						PFRANKING				=	5		# PK���а�
		"""
		self.gr_rType = rType

	def beginQueryGameRanking( self, rType ):
		"""
		��ʼ��ȡ�µ����а�����
		@type  rType :	UINT8
		@param rType :	Ҫ��ȡ�����а�����ͣ�Ŀǰֻ�����¼���
						LEVELRANKING			=	1		# ��ҵȼ�����
						MONEYRANKING			=	2		# ��ҽ�Ǯ����
						TONGRANKING				=	3		# �������
						FAMILYRANKING			=	4		# ��������
						PFRANKING				=	5		# PK���а�
		"""
		self.__setRanking(rType)
		if not self.gr_datasInfo.has_key(self.gr_rType):
			self.gr_datasInfo[self.gr_rType] = 0
		if self.gr_datasInfo[self.gr_rType] != -1:	# -1 ��ʾ�������
			if self.__callback_id == 0:
				self.__callback_id = BigWorld.callback( 0.2, self.queryRankingData )		# �����µ�����
		else: #�ڸ���ʱ���ڣ���ֱ��ȡ�ͻ�������
			self.queryLocalDatas( rType, 0 )
#			pass	#ֱ��ȡ��ȡ����,���������ȡ�Ķ�������ݲ����ڣ������ڷ�����û���ҵ��������ݣ��ͻ�ֱ�ӵ���
#					#onQueryRankingEnd �ӿ�.

	def queryLocalDatas( self, rType, startIndex ):
		"""
		��startIndexλ�ÿ�ʼ��һ������淢��5������
		"""
		endIndex = startIndex + 5
		rankDatas = self.getRankingDatas( rType )
		if rankDatas == []:return
		sectDatas = rankDatas[startIndex:endIndex]
		datasLen = len( rankDatas )
		if endIndex <= datasLen + 5:
			ECenter.fireEvent( "EVT_ON_RECEIVE_RANK_DATA", rType, startIndex, sectDatas )
			self.queryCallID = BigWorld.callback( 0.2, Functor( self.queryLocalDatas, rType, endIndex ) )
			ECenter.fireEvent( "EVT_ON_SET_RANKBTNS_STATE", rType, False )
		else:
			BigWorld.cancelCallback( self.queryCallID )
			ECenter.fireEvent( "EVT_ON_SET_RANKBTNS_STATE", rType, True )
			self.queryCallID = 0

	def getRankingDatas( self, rType ):
		"""
		��ʼ��ȡ�µ����а�����
		@type  rType :	UINT8
		@param rType :	Ҫ��ȡ�����а�����ͣ�Ŀǰֻ�����¼���
						LEVELRANKING			=	1		# ��ҵȼ�����
						MONEYRANKING			=	2		# ��ҽ�Ǯ����
						TONGRANKING				=	3		# �������
						FAMILYRANKING			=	4		# ��������
						PFRANKING				=	5		# PK���а�
		"""
		try:
			return self.gr_datas[rType]
		except:
			return []
