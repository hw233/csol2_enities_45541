# -*- coding: gb18030 -*-
from bwdebug import *
import csdefine
from SpawnPoint import SpawnPoint
import random

class RandomSpawnPoint( SpawnPoint ):
	"""
	�����ˢ�¹��ʵ������ķ�ʽȡ�ò߻��Ѿ����úõĶ��λ���е�һ��ˢ�����ֻ��������ͨ��ͼ��
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = SpawnPoint.getEntityArgs( self, selfEntity, params )
		positions = selfEntity.getEntityData( "positions" )
		if positions:
			args[ "position" ] = positions[ random.randint( 0, len( positions ) -1 ) ]			# ���ˢ�µ�
		return args