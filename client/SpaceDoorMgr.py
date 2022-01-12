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
			if spaceFolder in self.__FolderToLabelData:	# 已经有了~~
				spaceLabel = self.__FolderToLabelData[spaceFolder] + "|" + spaceLabel
			self.__FolderToLabelData[spaceFolder] = spaceLabel
			self.__LabelToFolderData[spaceLabel] = spaceFolder

	def __getPathCost( self, vertex, neighbor ):
		"""
		返回顶点vertex到neighbor的路径权值
		@type		vertex  :  string
		@param		vertex  :  顶点的键值
		@type		neighbor： int
		@param		neighbor:  顶点vertex的第几号邻居
		"""
		return 1 #暂定为1

	def getSpaceFolder( self, spaceLabel ):
		"""
		通过spaceLabel获取Space Folder
		@type		spaceLabel  :  string
		@param		spaceLabel  :  空间的标签，和文件夹的名字一样
		"""
		try:
			return self.__LabelToFolderData[spaceLabel]
		except:
			#DEBUG_MSG( "spaceLabel: %s is not in self.__LabelToFolderData " % spaceLabel )
			return spaceLabel

	def getSpaceLabel( self, spaceFolder ):
		"""
		通过spaceFolder获取spaceLabel
		@type		spaceFolder : string
		"""
		try:
			return self.__FolderToLabelData[spaceFolder]
		except:
			#DEBUG_MSG( "spaceFolder: %s is not in self.__FolderToLabelData " % spaceFolder )
			return spaceFolder

	def getSpaceDoorInf( self, spaceLabel ):
		"""
		通过spaceLabel来获取相应传送门的信息,引用数据源，不能直接做修改
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
		以字典数据形式返回从源点到目标点的路径, 格式：{(spaceLabel, position), ...}
		注意: 没有路径时,返回{}
		@type		srcSpaceLabel :  string
		@param		srcSpaceLabel :  源点space Label
		@type		srcPos    :  Vector3
		@param		srcPos    :  源点坐标值
		@type		dstSpaceLabel  :  string
		@param		dstSpaceLabel  :  目标点space Label
		@type		dstPos    :  Vector3
		@param		dstPos    :  目标点坐标值
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
				pathInf[label]=[[],INFINITE,False] #[路径，距离值，是否确定]
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
		返回SpaceDoorMgr单件的实例
		"""
		if SpaceDoorMgr._instance is None:
			SpaceDoorMgr._instance = SpaceDoorMgr( SpaceDoor.Datas )
		return SpaceDoorMgr._instance