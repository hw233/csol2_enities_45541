# -*- coding: gb18030 -*-
#
# ���ֽ𵰻�Ի�function

from Function import Function
from KuaiLeJinDan import KuaiLeJinDan
g_KuaiLeJinDan = KuaiLeJinDan.instance()

class FuncKuaiLeJinDan( Function ):
	"""
	���ֽ𵰻
	"""
	def do( self, player, talkEntity = None ):
		"""
		ִ�п��ֽ𵰻
		"""
		g_KuaiLeJinDan.startKLJDActivity( player )
		
class FuncSuperKuaiLeJinDan( Function ):
	"""
	���ֽ𵰻--������
	"""
	def do( self, player, talkEntity = None ):
		"""
		ִ�п��ֽ𵰻--������
		"""
		g_KuaiLeJinDan.startSuperKLJDActivity( player )
		
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		"""
		return g_KuaiLeJinDan.validStartSuperKLJDActivity( player )

class FuncKuaiLeJinDanExpReward( Function ):
	"""
	���ֽ𵰣���ȡ���齱��
	"""
	def do( self, player, talkEntity = None ):
		"""
		���ֽ𵰣���ȡ���齱��
		"""
		g_KuaiLeJinDan.doKLJDExpReward( player )
		
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		"""
		return g_KuaiLeJinDan.validDoKLJDExpReward( player )

class FuncKuaiLeJinDanZuoQi( Function ):
	"""
	���ֽ𵰣���ȡ���ｱ��
	"""
	def do( self, player, talkEntity = None ):
		"""
		���ֽ𵰣���ȡ���ｱ��
		"""
		g_KuaiLeJinDan.doKLJDZuoQiReward( player )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		"""
		return g_KuaiLeJinDan.validDoKLJDZuoQiReward( player )
