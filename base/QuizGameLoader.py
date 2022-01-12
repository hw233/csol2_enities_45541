# -*- coding: gb18030 -*-

"""
10:55 2009-4-25, by wsf
"""

import Language
import csconst
import random
from bwdebug import *

class QuestionItem:
	"""
	考题
	"""
	def __init__( self, section ):
		self.id = section.readInt( "questionID" )
		self.description = section.readString( "questionDes" )
		self.answer = section.readString( "answer" )
		self.optionList = []
		optionList = [ "a", "b", "c", "d", "e" ]
		for key in optionList:
			option = section.readString( key )
			if option == "":
				break
			self.optionList.append( option )
			
	def getAnswer( self ):
		"""
		"""
		return self.answer
		
	def isCurrent( self, answer ):
		"""
		答案是否正确
		"""
		return answer == self.answer
		
	def getDescription( self ):
		"""
		获得问题描述
		"""
		return self.description
		
	def getOption( self ):
		"""
		获得问题选项
		"""
		return self.optionList
		
class QuizGameLoader:
	"""
	全民问答配置管理
	"""
	_instance = None
	
	def __init__( self ):
		"""
		"""
		assert QuizGameLoader._instance is None, "instance has already exist!"
		QuizGameLoader._instance = self
		self.questionDict = {}		# 题库{ questionID:QuestionItem, ... }
		self.secondMapScore = {}	# 答题剩余时间对应的积分，{ 剩余时间( int ):分数( int ), ... }
		
	@classmethod
	def instance( self ):
		if self._instance is  None:
			self._instance = QuizGameLoader()
		return self._instance
		
	def load( self ):
		"""
		"""
		self.loadQuestion( xmlConfig = "config/server/QuizGameQuestion.xml" )
		self.loadSecondMapScore( xmlConfig = "config/server/QuizGameScore.xml" )
		
	def loadSecondMapScore( self, xmlConfig ):
		"""
		加载问答得分配置
		"""
		section = Language.openConfigSection( xmlConfig )
		if section is None:
			raise SystemError,"cannot load %s." % xmlConfig
		loadCount = 0
		for subSection in section.values():
			self.secondMapScore[subSection.readInt( "second" )] = subSection.readInt( "score" )
			loadCount += 1
		INFO_MSG( "--->>>load success count:%i." % loadCount )
		
	def loadQuestion( self, xmlConfig ):
		"""
		加载题库
		"""
		section = Language.openConfigSection( xmlConfig )
		if section is None:
			raise SystemError, "cannot load:%s." % xmlConfig
		count = 0
		for subSection in section.values():
			self.questionDict[subSection.readInt( "questionID" )] = QuestionItem( subSection )
			count += 1
		INFO_MSG( "--->>>load count:%i." % count )
		
	def getAnswer( self, questionID ):
		"""
		获得题目的答案
		"""
		return self.questionDict.get( questionID ).getAnswer()
		
	def getQuestionList( self ):
		"""
		获得考试题目
		"""
		if len( self.questionDict ) <= csconst.QUIZ_QUESTION_COUNT:
			return self.questionDict.keys()
		return random.sample( self.questionDict, csconst.QUIZ_QUESTION_COUNT )
		
	def getScore( self, restTime ):
		"""
		根据答题的剩余时间获得分数
		
		@param restTime : 答完题目的剩余时间
		@param restTime : FLOAT
		"""
		try:
			return self.secondMapScore[int( restTime )]
		except:
			ERROR_MSG( "restTime( %f ):cannot find relevant score." % restTime )
			return 0
		
	def getDescription( self, questionID ):
		"""
		获得问题描述
		"""
		return self.questionDict.get( questionID ).getDescription()
		
	def getOption( self, questionID ):
		"""
		获得问题描述
		"""
		return self.questionDict.get( questionID ).getOption()
		
quizGameLoader = QuizGameLoader.instance()
