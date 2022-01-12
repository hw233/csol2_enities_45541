# -*- coding: gb18030 -*-
#
# $Id: RoleImageVerify.py,v 1.9 2007-11-22 02:06:54 phw Exp $

"""
"""

from bwdebug import *
import imageVerify
import imageVerifySql
import BigWorld
import time
import ECBExtend

C_ANSWER_ERROR = 0
C_ANSWER_RIGHT = 1
C_NO_ANSWER    = -1

class RoleImageVerify:
	"""
	"""
	def __init__( self ):
		self.ivfAnswer = 0				# UINT8，当前问题正确答案是哪个
		self.ivfAnswerType = 0			# INT8，-1 未回答, 0 回答错误, 1 回答正确
		self.ivfPlayerPause = 0			# UINT8，1 为暂停，0 为继续
		self.ivfAnswerTimerID = 0		# UINT32，提问后必须在多长时间内回答
		self.ivfQuestTimerID = None		# UINT32，提问间隔计算timer
		self.ivfQuestTime = 0.0			# FLOAT，当前过去多长时间计数
		self.ivfAnswerTime = 0.0		# FLOAT, 从提问到回答问题，经历多长时间
		self.ivfFailCount = 0			# 回答错误次数

	def firstVerifyCount( self ):
		"""
		此方法不能在创建base Entity的时候(即初始化时)被调用，
		因为很多时候我们可能仅仅只创建base的Entity处理一些事情，被没有client。
		"""
		if imageVerify.ACTIVE_DELAY > 0:
			self.ivfQuestTimerID = self.addTimer( imageVerify.FIRST_QUEST_TIME, 0, ECBExtend.IMAGE_VERIFY_FIRST_TIMER_CBID )
			self.ivfQuestTime = 0

	def startVerifyCount( self ):
		if imageVerify.ACTIVE_DELAY > 0:
			self.ivfQuestTimerID = self.addTimer( imageVerify.ACTIVE_DELAY, 0, ECBExtend.IMAGE_VERIFY_TIMER_CBID )
			self.ivfQuestTime = 0

	def continueVerifyCount( self ):
		if imageVerify.ACTIVE_DELAY > 0:
			self.ivfQuestTimerID = self.addTimer( imageVerify.ACTIVE_DELAY, 0, ECBExtend.IMAGE_VERIFY_TIMER_CBID )

	def stopVerifyCount( self ):
		if self.ivfQuestTimerID is not None:
			self.delTimer( self.ivfQuestTimerID )
			self.ivfQuestTimerID = None

	def onReplyImageVerify( self, result ):
		"""
		@param result: 回答结果，player 选择了第几个答案
		@type  result: UINT8
		@return: 无
		"""
		self.ivfAnswerTime = BigWorld.time() - self.ivfAnswerTime
		if result == self.ivfAnswer:
			self.ivfAnswerType = C_ANSWER_RIGHT
			self.ivfFailCount = 0
		else:
			self.ivfAnswerType = C_ANSWER_ERROR
			self.ivfAddFail()
		self.delTimer( self.ivfAnswerTimerID )
		#DEBUG_MSG( self.playerName, self.ivfAnswerTime, self.ivfAnswerType, self.ivfFailCount, self.ivfAnswer, result )
		imageVerifySql.write( self )
		self.startVerifyCount()

	def playerPause( self, state ):
		"""
		@param state: bt 0 if player is not active, eq 0 if player is active again
		@type  state: UINT8
		@return: 无
		"""
		if state:
			if self.ivfQuestTimerID is not None:
				self.stopVerifyCount()
		else:
			self.continueVerifyCount()

	def onTimer_imageVerify( self, timerID, userData ):
		"""
		for ECBExtend
		到达提问时间，开始提问
		"""
		self.ivfQuestTime += imageVerify.ACTIVE_DELAY
		# 到达提问时间，开始提问
		if self.ivfQuestTime >= imageVerify.QUEST_TIME:
			self.onImageVerifyTimer()
			
	def onTimer_imageVerifyFirst( self, timerID, userData ):
		"""
		"""
		self.onImageVerifyTimer()
	
	def onTimer_imageVerifyAnswer( self, timerID, userData ):
		"""
		"""
		self.ivfAnswerType = C_NO_ANSWER
		self.ivfAnswerTime = BigWorld.time() - self.ivfAnswerTime
		imageVerifySql.write( self )
		#DEBUG_MSG( self.playerName, self.ivfAnswerTime, self.ivfAnswerType, self.ivfFailCount, self.ivfAnswer )
		self.startVerifyCount()
		self.ivfAddFail()
	
	def ivfAddFail( self ):
		self.ivfFailCount += 1
		if self.ivfFailCount >= imageVerify.FAIL_COUNT:
			ERROR_MSG( "%s(%i): fail count %i, kick out." % (self.playerName, self.databaseID, self.ivfFailCount) )
			self.loginLockTime = time.time() + imageVerify.LOGIN_LOCK_TIME
			self.destroyCellEntity()

	def onImageVerifyTimer( self ):
		self.ivfAnswer, imgStr = imageVerify.createRandomVerify()
		#self.client.onImageVerify( imgStr )
		self.sendImgPacket( imgStr )
		self.ivfAnswerTimerID = self.addTimer( imageVerify.ANSWER_TIME, 0, ECBExtend.IMAGE_VERIFY_ANSWER_TIMER_CBID )
		self.ivfAnswerTime = BigWorld.time()
		self.stopVerifyCount()


	def sendImgPacket( self, imgStr ):
		maxLen = 1024
		if len( imgStr ) <= maxLen:
			self.client.onImageVerify( 1, 1, imgStr )
			return
		iPacket = len(imgStr) / maxLen
		if len(imgStr) % maxLen != 0:
			maxPacket = iPacket + 1
		else:
			maxPacket = iPacket
		for e in xrange( iPacket ):
			self.client.onImageVerify( maxPacket, e + 1, imgStr[e * maxLen:(e+1) * maxLen] )
		if maxPacket != iPacket:
			self.client.onImageVerify( maxPacket, maxPacket, imgStr[iPacket * maxLen:] )


#
# $Log: not supported by cvs2svn $
# Revision 1.8  2007/06/14 09:21:23  huangyongwei
# 频道的定义由 L3Common 中搬到 csdefine 中
#
# Revision 1.7  2005/12/08 02:03:26  phw
# no message
#
# Revision 1.6  2005/11/25 09:38:42  phw
# no message
#
# Revision 1.5  2005/11/25 09:27:27  phw
# no message
#
# Revision 1.4  2005/11/25 08:55:17  phw
# no message
#
# Revision 1.3  2005/11/25 04:42:08  phw
# no message
#
# Revision 1.2  2005/11/24 08:58:43  phw
# no message
#
# Revision 1.1  2005/11/23 09:28:46  phw
# 图片认证相关代码
#
#
