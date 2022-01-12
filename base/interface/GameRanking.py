# -*- coding: gb18030 -*-
#

import csconst
import BigWorld


class GameRanking:
	"""
	游戏排行数据服务器客户端交互接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		pass

	def queryRankingData( self, rankingType, beginIndex ):
		"""
		@define method
		客户端向服务器请求数据的接口
		@type  rankingType: UINT8
		@param rankingType: 数据的类型 如 帮会排行数据
		@type  beginIndex : UINT8
		@param beginIndex : 数据发送的起始位置
		"""
		BigWorld.baseAppData["GameRankingManager"].queryRankingData( self, rankingType, beginIndex )


	def showGameRanking( self ):
		"""
		@define method
		通知客户端开始请求数据
		"""
		BigWorld.baseAppData["GameRankingManager"].showGameRanking( self )
