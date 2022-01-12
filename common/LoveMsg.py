# -*- coding: gb18030 -*-
#

import BigWorld
import csdefine
import time
import cPickle

Subjects = {
			csdefine.FCWR_VOTE_KAN_HAO : "vote_1",
			csdefine.FCWR_VOTE_QING_DI : "vote_2",
			csdefine.FCWR_VOTE_SHI_LIAN : "vote_3",
			csdefine.FCWR_VOTE_KAN_QI : "vote_4",	
			csdefine.FCWR_VOTE_FAN_DUI : "vote_5",
			csdefine.FCWR_VOTE_LU_GUO : "vote_6",	
			}



class LoveMsg:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.index 			= 0
		self.roleDBID 		= 0
		self.receiveTime	= 0
		self.senderName		= ""
		self.receiverName	= ""
		self.msg			= ""
		self.isAnonymity	= False
		self.vote_1			= 0
		self.vote_2			= 0
		self.vote_3			= 0
		self.vote_4			= 0
		self.vote_5			= 0
		self.vote_6			= 0
		self.lastVoteTime	= 0
		self.senderRaceclass		= 0
		self.receiverRaceclass		= 0


	def init( self, index, roleDBID, receiveTime, senderName, receiverName, msg, isAnonymity, vote_1 = 0, vote_2 = 0, vote_3 = 0, vote_4 = 0, vote_5 = 0, vote_6 = 0, lastVoteTime = 0, senderRaceclass = 0, receiverRaceclass = 0  ):
		"""
		"""
		self.index 			= index
		self.roleDBID 		= roleDBID
		self.receiveTime	= receiveTime
		self.senderName		= senderName
		self.receiverName	= receiverName
		self.msg			= msg
		self.isAnonymity	= isAnonymity
		self.vote_1			= vote_1
		self.vote_2			= vote_2
		self.vote_3			= vote_3
		self.vote_4			= vote_4
		self.vote_5			= vote_5
		self.vote_6			= vote_6
		self.lastVoteTime	= lastVoteTime
		self.senderRaceclass		= senderRaceclass
		self.receiverRaceclass		= receiverRaceclass
	
	def vote( self, chooseSubject ):
		"""
		"""
		if chooseSubject in Subjects:
			count = getattr( self, Subjects[chooseSubject] )
			setattr( self, Subjects[chooseSubject], count + 1 )
			self.lastVoteTime = int( time.time() )
			return True
		return False

	def getVoteCount( self ):
		"""
		"""
		return self.vote_1 + self.vote_2 + self.vote_3 + self.vote_4 + self.vote_5 + self.vote_6

	def setRaceClass( self, senderRaceclass, receiverRaceclass ):
		"""
		"""
		self.senderRaceclass 	= senderRaceclass
		self.receiverRaceclass	= receiverRaceclass


	def printMsgInfo( self ):
		"""
		"""
		print self.index
		print self.roleDBID
		print self.receiveTime
		print self.senderName
		print self.receiverName
		print self.msg
		print self.isAnonymity
		print self.vote_1
		print self.vote_2
		print self.vote_3
		print self.vote_4
		print self.vote_5
		print self.vote_6
		print self.lastVoteTime
		print self.senderRaceclass
		print self.receiverRaceclass

	##################################################################
	# BigWorld 的接口												#
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "index" 			: obj.index,
		         "roleDBID" 		: obj.roleDBID,
		         "receiveTime"		: obj.receiveTime,
		         "senderName"		: obj.senderName,
		         "receiverName"		: obj.receiverName,
		         "msg"				: obj.msg,
		         "isAnonymity"		: obj.isAnonymity,
		         "vote_1"			: obj.vote_1,
		         "vote_2"			: obj.vote_2,
		         "vote_3"			: obj.vote_3,
		         "vote_4"			: obj.vote_4,
		         "vote_5"			: obj.vote_5,
		         "vote_6"			: obj.vote_6,
		         "lastVoteTime"		: obj.lastVoteTime,
		         "senderRaceclass"	: obj.senderRaceclass,
		         "receiverRaceclass": obj.receiverRaceclass,
			}                         

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = LoveMsg()
		obj.index 			= dict["index"]
		obj.roleDBID 		= dict["roleDBID"]
		obj.receiveTime		= dict["receiveTime"]
		obj.senderName		= dict["senderName"]
		obj.receiverName	= dict["receiverName"]
		obj.msg				= dict["msg"]
		obj.isAnonymity		= dict["isAnonymity"]
		obj.vote_1			= dict["vote_1"]
		obj.vote_2			= dict["vote_2"]
		obj.vote_3			= dict["vote_3"]
		obj.vote_4			= dict["vote_4"]
		obj.vote_5			= dict["vote_5"]
		obj.vote_6			= dict["vote_6"]
		obj.lastVoteTime	= dict["lastVoteTime"]
		obj.senderRaceclass = dict["senderRaceclass"]
		obj.receiverRaceclass = dict["receiverRaceclass"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, LoveMsg )



class FcwrResult:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.key 			= ""				
		self.rewardReason	= -1
		self.takenTime		= 0
		self.hasTaken		= 0
		self.param01		= ""
		self.param02		= ""
	
	def init( self, key, rewardReason, takenTime = 0, hasTaken = False, param01 = "", param02 = "" ):
		"""
		"""
		self.key 			= key
		self.rewardReason	= rewardReason
		self.takenTime		= takenTime
		self.hasTaken		= hasTaken
		self.param01		= param01
		self.param02		= param02


class VoteInstance:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.roleDBID		= 0
		self.roleName		= ""
		self.voteTime		= 0
		self.voteList		= []

	def init( self, roleDBID, roleName, voteTime, voteStr = cPickle.dumps( [], 2 ) ):
		"""
		"""
		self.roleDBID = roleDBID
		self.roleName = roleName
		self.voteTime = voteTime
		self.voteList = cPickle.loads( voteStr )

	def makeVoteStr( self ):
		"""
		"""
		return cPickle.dumps( self.voteList, 2 )
	
	def getVoteCount( self ):
		"""
		"""
		return len( self.voteList )


instance = LoveMsg()

