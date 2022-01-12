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
	����
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
		���Ƿ���ȷ
		"""
		return answer == self.answer
		
	def getDescription( self ):
		"""
		�����������
		"""
		return self.description
		
	def getOption( self ):
		"""
		�������ѡ��
		"""
		return self.optionList
		
class QuizGameLoader:
	"""
	ȫ���ʴ����ù���
	"""
	_instance = None
	
	def __init__( self ):
		"""
		"""
		assert QuizGameLoader._instance is None, "instance has already exist!"
		QuizGameLoader._instance = self
		self.questionDict = {}		# ���{ questionID:QuestionItem, ... }
		self.secondMapScore = {}	# ����ʣ��ʱ���Ӧ�Ļ��֣�{ ʣ��ʱ��( int ):����( int ), ... }
		
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
		�����ʴ�÷�����
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
		�������
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
		�����Ŀ�Ĵ�
		"""
		return self.questionDict.get( questionID ).getAnswer()
		
	def getQuestionList( self ):
		"""
		��ÿ�����Ŀ
		"""
		if len( self.questionDict ) <= csconst.QUIZ_QUESTION_COUNT:
			return self.questionDict.keys()
		return random.sample( self.questionDict, csconst.QUIZ_QUESTION_COUNT )
		
	def getScore( self, restTime ):
		"""
		���ݴ����ʣ��ʱ���÷���
		
		@param restTime : ������Ŀ��ʣ��ʱ��
		@param restTime : FLOAT
		"""
		try:
			return self.secondMapScore[int( restTime )]
		except:
			ERROR_MSG( "restTime( %f ):cannot find relevant score." % restTime )
			return 0
		
	def getDescription( self, questionID ):
		"""
		�����������
		"""
		return self.questionDict.get( questionID ).getDescription()
		
	def getOption( self, questionID ):
		"""
		�����������
		"""
		return self.questionDict.get( questionID ).getOption()
		
quizGameLoader = QuizGameLoader.instance()
