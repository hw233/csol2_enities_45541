# -*- coding: gb18030 -*-

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyMaps( SpaceCopy ):
	"""
	���ͼ���˸����ű�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		self._spaceMapsClassNames = []
		self._spaceMapsNo = 0
		self.bossID = []

	def load( self, section ):
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		for idx, item in enumerate( section[ "Space" ][ "spaceMapsInfos" ].values() ):
			className = item[ "className" ].asString
			self._spaceMapsClassNames.append( className )
			if className == self.getClassName():
				self._spaceMapsNo = idx
		self.bossID = section[ "Space" ][ "bossID" ].asString.split(";")
		
		SpaceCopy.load( self, section )
	
	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'dbID' : entity.databaseID, "enterCopyNo" : self._spaceMapsNo }
	
	def getCopyNo( self ):
		"""
		��ȡ��ǰ�ĵ�ͼ�ı��
		"""
		return self._spaceMapsNo
	
	def getSpaceClassName( self, copyNo ):
		"""
		��ȡ��Ӧ��ͼ��ClassName
		"""
		return self._spaceMapsClassNames[ copyNo ]