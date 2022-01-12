# -*- coding: gb18030 -*-
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
from bwdebug import *
import BigWorld
import Love3

class SpaceCopyTowerDefense( SpaceCopy, SpaceCopyYeWaiInterface, SpaceCopyRaidRecordInterface ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )

	def checkNeedSpawn( self, sec ):
		# virtual method.
		# �ж��Ƿ���Ҫ������ˢ�µ�
		return SpaceCopyYeWaiInterface.checkNeedSpawn( self, sec ) and SpaceCopy.checkNeedSpawn( self, sec )

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		SpaceCopyYeWaiInterface.onSpawnPointLoadedOver( self, retCode )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ䣬��Ҫ���ݸ���boss�Ļ�ɱ����������
		��Ӧ����ʾ���������ѡ���Ǽ������������뿪������
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )