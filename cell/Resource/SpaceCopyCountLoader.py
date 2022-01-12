# -*- coding: gb18030 -*-
import copy
import Math

import Language
import csdefine
from config.server.SpaceCopyCount import Datas as datas_config

class SpaceCopyCountLoader:
	# ����������������
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
		��ʼ������
		"""
		for cnf in datas_config:
			spaceType = eval( "csdefine.SPACE_TYPE_%s"%cnf["spaceType"] )	#�������ͣ�Ψһ��ʶ
			contentKey = cnf["contentKey"]								#�����ؿ����ǿ���Ϊ��2�����Ϲؿ�����ͬ�ؿ���|������Ϊ����û�ж���ؿ�
			bossCnfs = cnf["bossClassName"]							#boss��className
			speCnfs = cnf["specialClassName"]						#��Ҫ����������С��
			doorCnfs = cnf["doorClassName"]							#�ؿ���entity��className
			nCalCnfs = cnf["noCalClassName"]							#����Ҫ����entity
			if len( contentKey ):											#�ж���ؿ�,��ͬ�ؿ�classNameʹ��|�ָͬ1���ؿ���;����
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
		��ȡ����ָ������entity��className
		@param clsType : ��ѯentity�����ͣ���bossCls��speCls��
		@type clsType : STRING
		"""
		if content != "":
			if spaceType in self._datas:
				if content in self._datas[spaceType]:
					return self._datas[spaceType][content][clsType]
		else:
			if spaceType in self._datas:
				return self._datas[spaceType][clsType]