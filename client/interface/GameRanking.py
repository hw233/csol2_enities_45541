# -*- coding: gb18030 -*-
#

import BigWorld
import Const
import csconst
import event.EventCenter as ECenter
from Function import Functor

class GameRanking:
	"""
	排行榜数据
	"""
	def __init__( self ):
		"""
		初始化
		"""
		self.gr_upDateTime 	= 0							# 记录上次获取的数据的更新时间，如果该时间和服务器当前数据的更新时间吻合即为最新数据,
														# 就没有必要再向服务器请求，如果该时间为0表示之前没有获取过数据
		self.gr_datas 			= {}						# 保存的数据
		self.gr_datasInfo		= {}						# 保存数据的发送情况 like {1:12, 2: 15} 表示第一类发送了12条 从索引12开始继续请求......
		self.__callback_id  = 0							# callback的ID
		self.gr_rType			= Const.LEVELRANKING	# 当前获取的排行榜类型 默认为等级排行
		self.queryCallID = 0							# 客户端数据请求callbackID

	def onQueryRankingData( self, rankingType, beginIndex, rankingDatas ):
		"""
		获取了数据
		@param  rankingType  : 当前获取的排行榜的类型，目前只有如下几个
								LEVELRANKING			=	1		# 玩家等级排行
								MONEYRANKING			=	2		# 玩家金钱排行
								TONGRANKING				=	3		# 帮会排行
								FAMILYRANKING			=	4		# 家族排行
								PFRANKING				=	5		# PK排行榜
		@type   rankingType  : UINT8
		@param  beginIndex   : 当前获取的数据的起始索引
		@type   beginIndex   : UINT8
		@param  rankingDatas : 服务器发送过来的排行数据
		@type   rankingDatas : LIST
		"""
		if not self.gr_datas.has_key( rankingType):
			self.gr_datas[rankingType] = []
		self.gr_datas[rankingType].extend( rankingDatas )
		self.gr_datasInfo[rankingType] += len(rankingDatas)							# 增加此次请求的数据索引
		self.__callback_id = BigWorld.callback( 0.2, self.queryRankingData )		# 请求新的数据
		ECenter.fireEvent( "EVT_ON_RECEIVE_RANK_DATA", rankingType, beginIndex, rankingDatas )

	def onQueryRankingEnd( self, rankingType ):
		"""
		获取该类型的排行榜数据完毕
		"""
		self.gr_datasInfo[rankingType] = -1
		ECenter.fireEvent( "EVT_ON_SET_RANKBTNS_STATE", rankingType, True )
		if rankingType != self.gr_rType and self.gr_datasInfo[self.gr_rType] != -1:													# 如果发完的数据并非当前要获取的数据 继续请求
			self.__callback_id = BigWorld.callback( 0.2, self.queryRankingData )		# 请求新的数据
		else:
			self.__callback_id = 0														# 发送完毕TIMER ID 清零


	def queryRankingData( self ):
		"""
		向服务器请求数据
		"""
		BigWorld.cancelCallback( self.__callback_id )
		self.base.queryRankingData( self.gr_rType, self.gr_datasInfo[self.gr_rType] )		# 向服务器请求数据
		ECenter.fireEvent( "EVT_ON_SET_RANKBTNS_STATE", self.gr_rType, False )

	def onShowGameRanking( self, updateTime ):
		"""
		服务器通知客户端显示排行榜,并告诉客户端请求排行数据
		@param  updateTime : 当前数据更新的时间，用以与客户端当前数据比对，是否需要重新向服务器申请数据
		@type   updateTime : UINT32
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_RANK_WINDOW" )
		if self.gr_upDateTime != updateTime:							# 如果没有或者不是最新的数据
			self.repairGameRankingData()										# 恢复数据
			self.gr_upDateTime		= updateTime						# 记录本次数据服务器更新的时间
		self.beginQueryGameRanking( Const.LEVELRANKING )						# 第一次默认去获取等级排行的数据，因为它的界面处于第一位

	def repairGameRankingData( self ):
		"""
		恢复数据
		"""
		self.__callback_id  = 0						# callback的ID
		self.gr_datas 			= {}					# 保存的数据
		self.gr_upDateTime 	= 0						# 本次数据更新的时间
		self.gr_rType			= Const.LEVELRANKING	# 当前获取的排行榜类型
		self.gr_datasInfo		= {}

	def __setRanking( self, rType ):
		"""
		更换当前获取的排行榜类型
		@type  rType :	UINT8
		@param rType :	要获取的排行榜的类型，目前只有如下几个
						LEVELRANKING			=	1		# 玩家等级排行
						MONEYRANKING			=	2		# 玩家金钱排行
						TONGRANKING				=	3		# 帮会排行
						FAMILYRANKING			=	4		# 家族排行
						PFRANKING				=	5		# PK排行榜
		"""
		self.gr_rType = rType

	def beginQueryGameRanking( self, rType ):
		"""
		开始获取新的排行榜数据
		@type  rType :	UINT8
		@param rType :	要获取的排行榜的类型，目前只有如下几个
						LEVELRANKING			=	1		# 玩家等级排行
						MONEYRANKING			=	2		# 玩家金钱排行
						TONGRANKING				=	3		# 帮会排行
						FAMILYRANKING			=	4		# 家族排行
						PFRANKING				=	5		# PK排行榜
		"""
		self.__setRanking(rType)
		if not self.gr_datasInfo.has_key(self.gr_rType):
			self.gr_datasInfo[self.gr_rType] = 0
		if self.gr_datasInfo[self.gr_rType] != -1:	# -1 表示发送完毕
			if self.__callback_id == 0:
				self.__callback_id = BigWorld.callback( 0.2, self.queryRankingData )		# 请求新的数据
		else: #在更新时间内，则直接取客户端数据
			self.queryLocalDatas( rType, 0 )
#			pass	#直接取获取数据,在这里可能取的对象的数据不存在，比如在服务器没有找到该类数据，就会直接调用
#					#onQueryRankingEnd 接口.

	def queryLocalDatas( self, rType, startIndex ):
		"""
		从startIndex位置开始，一次向界面发送5个数据
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
		开始获取新的排行榜数据
		@type  rType :	UINT8
		@param rType :	要获取的排行榜的类型，目前只有如下几个
						LEVELRANKING			=	1		# 玩家等级排行
						MONEYRANKING			=	2		# 玩家金钱排行
						TONGRANKING				=	3		# 帮会排行
						FAMILYRANKING			=	4		# 家族排行
						PFRANKING				=	5		# PK排行榜
		"""
		try:
			return self.gr_datas[rType]
		except:
			return []
