# -*- coding: gb18030 -*-
#

import csconst
import BigWorld


class GameRanking:
	"""
	��Ϸ�������ݷ������ͻ��˽����ӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		pass

	def queryRankingData( self, rankingType, beginIndex ):
		"""
		@define method
		�ͻ�����������������ݵĽӿ�
		@type  rankingType: UINT8
		@param rankingType: ���ݵ����� �� �����������
		@type  beginIndex : UINT8
		@param beginIndex : ���ݷ��͵���ʼλ��
		"""
		BigWorld.baseAppData["GameRankingManager"].queryRankingData( self, rankingType, beginIndex )


	def showGameRanking( self ):
		"""
		@define method
		֪ͨ�ͻ��˿�ʼ��������
		"""
		BigWorld.baseAppData["GameRankingManager"].showGameRanking( self )
