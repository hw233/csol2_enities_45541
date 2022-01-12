# -*- coding: gb18030 -*-
import BigWorld
from SpaceCopy import SpaceCopy
import Love3

class SpaceCopyYiJieZhanChang( SpaceCopy ):
	# ���ս��
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.minLevel = 0
		self.maxLevel = 0
		self.intervalLevel = 0
		self.minPlayer = 0
		self.maxPlayer = 0
		self.enterInfos = []
	
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		self.minLevel = section[ "Space" ][ "minLevel" ].asInt
		self.maxLevel = section[ "Space" ][ "maxLevel" ].asInt
		self.intervalLevel = section[ "Space" ][ "intervalLevel" ].asInt
		self.minPlayer = section[ "Space" ][ "minPlayer" ].asInt
		self.maxPlayer = section[ "Space" ][ "maxPlayer" ].asInt
		self.maxOfflineTime = section[ "Space" ][ "maxOfflineTime" ].asInt
		
		for idx, item in enumerate( section[ "Space" ][ "enterInfos" ].values() ):
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self.enterInfos.append( ( pos, direction ) )
		

	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		pickDict = {}
		pickDict["dbID"] 		= entity.databaseID
		pickDict["lastOffline"]	= entity.role_last_offline
		return pickDict