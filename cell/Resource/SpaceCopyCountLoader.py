# -*- coding: gb18030 -*-
import copy
import Math

import Language
import csdefine
from config.server.SpaceCopyCount import Datas as datas_config

class SpaceCopyCountLoader:
	# 副本怪物死亡计数
	_instance = None
	def __init__( self ):
		assert SpaceCopyCountLoader._instance is None
		self._datas = {}
		
	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = SpaceCopyCountLoader()
		return self._instance

	def __getitem__( self, key ):
		"""
		"""
		if self._datas.has_key( key ):
			return self._datas[key]
		else:
			return None
	
	def initCnfData( self ):
		"""
		初始化数据
		"""
		for cnf in datas_config:
			spaceType = eval( "csdefine.SPACE_TYPE_%s"%cnf["spaceType"] )	#副本类型，唯一标识
			contentKey = cnf["contentKey"]								#副本关卡，非空则为有2个以上关卡，不同关卡用|隔开，为空则没有多个关卡
			bossCnfs = cnf["bossClassName"]							#boss的className
			speCnfs = cnf["specialClassName"]						#需要计数的特殊小怪
			doorCnfs = cnf["doorClassName"]							#关卡门entity的className
			nCalCnfs = cnf["noCalClassName"]							#不需要计数entity
			if len( contentKey ):											#有多个关卡,不同关卡className使用|分割，同1个关卡用;隔开
				contents = {}
				keys = contentKey.split( "|" )
				for index, key in enumerate( keys ):
					bossCls = speCls = []
					doorCls = nCalCls = []
					if len( bossCnfs ):
						bossCls = bossCnfs.split( "|" )[index].split(";")
					if len( speCnfs ):
						speCls = speCnfs.split( "|" )[index].split(";")
					if len( doorCnfs ):
						doorCls = doorCnfs.split( "|" )[index].split(";")
					if len( nCalCnfs ):
						nCalCls = nCalCnfs.split( "|" )[index].split(";")
					contents[key] = {"bossCls":bossCls, "speCls":speCls, "doorCls":doorCls, "noCalCls":nCalCls}
				self._datas[spaceType] = contents
			else:
				self._datas[spaceType] = {"bossCls":bossCnfs.split(";"), "speCls":speCnfs.split(";"),"doorCls":doorCnfs.split(";"),"noCalCls":nCalCnfs.split(";")}
	
	def getSpaceAssignCls( self, spaceType, clsType, content = "" ):
		"""
		获取副本指定类型entity的className
		@param clsType : 查询entity的类型，如bossCls，speCls等
		@type clsType : STRING
		"""
		if content != "":
			if spaceType in self._datas:
				if content in self._datas[spaceType]:
					return self._datas[spaceType][content][clsType]
		else:
			if spaceType in self._datas:
				return self._datas[spaceType][clsType]