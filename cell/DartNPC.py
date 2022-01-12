# -*- coding: gb18030 -*-
#
# $Id: DartNPC.py,v 1.2 2008-09-05 03:50:52 zhangyuxing Exp $


from bwdebug import *
import csdefine
from NPC import NPC
import ECBExtend



timerBegin = 7200 											#����Сʱ

class DartNPC( NPC ):
	"""
	NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		self.addTimer( timerBegin, 0, ECBExtend.QUERY_DART_MESSAGE_CBID )			#ÿ������Сʱ��ѯ�ھ���Ϣһ��
		
		
	
	def refreshDartMessage( self, key, dartMessages ):
		"""
		define method
		�����ھ�����
		"""
		self.setTemp( key, dartMessages )
	
	
	def getDartMessage( self, key ):
		"""
		"""
		return self.queryTemp( key, [] )
	
	
	def onQueryDartMessage( self ):
		"""
		�����ݿ��ѯ��������
		"""
		self.base.queryDartMessage()
		self.addTimer( timerBegin, 0, ECBExtend.QUERY_DART_MESSAGE_CBID )			#ÿ������Сʱ��ѯ�ھ���Ϣһ��
