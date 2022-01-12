# -*- coding: gb18030 -*-

import Math
from bwdebug import *
from config import SpaceDoor
from MapMgr import mapMgr

class SpaceDoorMgr:
	_instance = None
	def __init__( self, data ):
		assert SpaceDoorMgr._instance is None, "instance already exist in"
		self.__data = data
		self.__FolderToLabelData = {}
		self.__LabelToFolderData = {}
		for area in mapMgr.getWholeAreas() :
			spaceLabel = area.spaceLabel
			spaceFolder = area.spaceFolder
			if spaceFolder in self.__FolderToLabelData:	# �Ѿ�����~~
				spaceLabel = self.__FolderToLabelData[spaceFolder] + "|" + spaceLabel
			self.__FolderToLabelData[spaceFolder] = spaceLabel
			self.__LabelToFolderData[spaceLabel] = spaceFolder

	def __getPathCost( self, vertex, neighbor ):
		"""
		���ض���vertex��neighbor��·��Ȩֵ
		@type		vertex  :  string
		@param		vertex  :  ����ļ�ֵ
		@type		neighbor�� int
		@param		neighbor:  ����vertex�ĵڼ����ھ�
		"""
		return 1 #�ݶ�Ϊ1

	def getSpaceFolder( self, spaceLabel ):
		"""
		ͨ��spaceLabel��ȡSpace Folder
		@type		spaceLabel  :  string
		@param		spaceLabel  :  �ռ�ı�ǩ�����ļ��е�����һ��
		"""
		try:
			return self.__LabelToFolderData[spaceLabel]
		except:
			#DEBUG_MSG( "spaceLabel: %s is not in self.__LabelToFolderData " % spaceLabel )
			return spaceLabel

	def getSpaceLabel( self, spaceFolder ):
		"""
		ͨ��spaceFolder��ȡspaceLabel
		@type		spaceFolder : string
		"""
		try:
			return self.__FolderToLabelData[spaceFolder]
		except:
			#DEBUG_MSG( "spaceFolder: %s is not in self.__FolderToLabelData " % spaceFolder )
			return spaceFolder

	def getSpaceDoorInf( self, spaceLabel ):
		"""
		ͨ��spaceLabel����ȡ��Ӧ�����ŵ���Ϣ,��������Դ������ֱ�����޸�
		@type		RETURN:
		@type		spaceLabel: string
		"""
		spaceFolder = self.getSpaceFolder( spaceLabel )
		try:
			return self.__data[spaceFolder]
		except:
			return ()

	def getPath( self, srcSpaceLabel, srcPos, dstSpaceLabel, dstPos ):
		"""
		���ֵ�������ʽ���ش�Դ�㵽Ŀ����·��, ��ʽ��{(spaceLabel, position), ...}
		ע��: û��·��ʱ,����{}
		@type		srcSpaceLabel :  string
		@param		srcSpaceLabel :  Դ��space Label
		@type		srcPos    :  Vector3
		@param		srcPos    :  Դ������ֵ
		@type		dstSpaceLabel  :  string
		@param		dstSpaceLabel  :  Ŀ���space Label
		@type		dstPos    :  Vector3
		@param		dstPos    :  Ŀ�������ֵ
		"""
		INFINITE = 1073741824
		srcSpaceFolder = self.getSpaceFolder( srcSpaceLabel )
		dstSpaceFolder = self.getSpaceFolder( dstSpaceLabel )
		if not self.__data.has_key( srcSpaceFolder ):
			DEBUG_MSG( "Can not find src space: \"%s\" in SpaceDoor.Datas!" %srcSpaceFolder )
			return {}

		if not self.__data.has_key( dstSpaceFolder ):
			DEBUG_MSG( "Can not find dst space: \"%s\" in SpaceDoor.Datas!" %dstSpaceFolder )
			return {}

		srcEdgeNum = len( self.__data[ srcSpaceFolder ] )
		if srcEdgeNum == 0:
			return {}

		pathInf ={}
		for i in self.__data:
			Label = self.getSpaceLabel( i )
			for label in Label.split( "|" ):
				pathInf[label]=[[],INFINITE,False] #[·��������ֵ���Ƿ�ȷ��]
		nowFolder = srcSpaceFolder
		nowLabel = srcSpaceLabel
		pathInf[nowLabel]=[[],0,False]

		for sp in xrange( len( self.__data ) ):
			dat = self.__data[nowFolder]
			for nIndex in xrange( len( dat ) ):
				curCost = pathInf[nowLabel][1] + self.__getPathCost( nowFolder, nIndex )
				neighbor = pathInf[dat[nIndex]["destSpace"]]
				if not neighbor[2] and neighbor[1] > curCost:
					neighbor[1] = curCost
					neighbor[0] = pathInf[nowLabel][0] + [( nowLabel, dat[nIndex]["position"] )]
			min = INFINITE
			findLb = nowLabel
			for lb in pathInf:
				if not pathInf[lb][2]:
					if pathInf[lb][1] < min: findLb, min = lb, pathInf[lb][1]
			nowLabel = findLb
			nowFolder = self.getSpaceFolder( nowLabel )
			pathInf[nowLabel][2] = True

		if len( pathInf[dstSpaceLabel][0] ) == 0:
			return {}
		else:
			return pathInf[dstSpaceLabel][0] + [(dstSpaceLabel, Math.Vector3( dstPos ) )]

	@staticmethod
	def instance():
		"""
		����SpaceDoorMgr������ʵ��
		"""
		if SpaceDoorMgr._instance is None:
			SpaceDoorMgr._instance = SpaceDoorMgr( SpaceDoor.Datas )
		return SpaceDoorMgr._instance