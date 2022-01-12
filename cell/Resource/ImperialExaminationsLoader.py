# -*- coding: gb18030 -*-
import random
import Language
from config.server.potentialMeleeConfig import Datas as g_config

ANSWERS_OPTIONS = ["a","b","c","d","e"]

class ImperialExaminationsLoader:
	# 副本信息
	_instance = None
	def __init__( self ):
		assert ImperialExaminationsLoader._instance is None
		self.data = {}
		
	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = ImperialExaminationsLoader()
		return self._instance

	def __getitem__( self, key ):
		"""
		取得Space数据部分
		"""
		if self.data.has_key( key ):
			return self.data[key]
		else:
			return None
	
	def load( self, filePath ):
		sec = Language.openConfigSection(filePath)
		if sec is None:
			raise SystemError, "Can not Load %s " % filePath
		
		for item in sec.values():
			dict = {}
			questionID = item[ "questionID" ].asInt
			dict[ "questionID" ] = questionID
			dict[ "questionDes" ] = item[ "questionDes" ].asString
			dict[ "answer" ] = item[ item[ "answer" ].asString ].asString
			questOptions = []
			for aKey in ANSWERS_OPTIONS:
				questOptions.append( item[ aKey ].asString )
			
			questOptions = filter(''.__ne__, questOptions)  #去掉里面空白的选项
			
			dict[ "questOptions" ] = questOptions
			
			self.data[ questionID ] = dict
	
	def randomGet( self ):
		return random.choice( self.data.values() )

g_imperialExaminationsLoader = ImperialExaminationsLoader.instance()