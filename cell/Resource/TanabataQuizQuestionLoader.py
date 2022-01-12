# -*- coding:gb18030 -*-

from bwdebug import *
import Language
import time


class TanabataQuizQuestionLoader:
	"""
	"""
	_instance = None
	def __init__( self ):
		assert TanabataQuizQuestionLoader._instance is None
		self._data = {}
		
	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = TanabataQuizQuestionLoader()
		return self._instance
		
	def load( self, xmlPath ):
		"""
		加载七夕问答数据
		"""
		section = Language.openConfigSection( xmlPath )
		if section is None:
			raise SystemError, "cannot load:%s." % xmlPath
		for subSection in section.values():
			quizTime = eval( subSection.readString( "quizTime" ) )
			questionData = { "questionDes":subSection.readString( "questionDes" ) }
			options = []
			for i in xrange(5):	# 最多只有5个选项
				option = subSection.readString( "option" + str(i+1) )
				if option != "":
					options.append( option )
			questionData["options"] = options
			if not self._data.has_key( quizTime ):
				self._data[quizTime] = {}
			self._data[quizTime][subSection.readInt( "questionID" )] = questionData
			
	def getQuestion( self, questionID ):
		"""
		获得问答题目（描述、选项）
		rType : { "questionDes":questionDes, "options":[a,b,c,...] }
		"""
		key = time.localtime()[0:3]
		return self._data[key][questionID]
		