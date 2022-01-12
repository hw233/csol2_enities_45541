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
		self.ivfAnswer = 0				# UINT8����ǰ������ȷ�����ĸ�
		self.ivfAnswerType = 0			# INT8��-1 δ�ش�, 0 �ش����, 1 �ش���ȷ
		self.ivfPlayerPause = 0			# UINT8��1 Ϊ��ͣ��0 Ϊ����
		self.ivfAnswerTimerID = 0		# UINT32�����ʺ�����ڶ೤ʱ���ڻش�
		self.ivfQuestTimerID = None		# UINT32�����ʼ������timer
		self.ivfQuestTime = 0.0			# FLOAT����ǰ��ȥ�೤ʱ�����
		self.ivfAnswerTime = 0.0		# FLOAT, �����ʵ��ش����⣬�����೤ʱ��
		self.ivfFailCount = 0			# �ش�������

	def firstVerifyCount( self ):
		"""
		�˷��������ڴ���base Entity��ʱ��(����ʼ��ʱ)�����ã�
		��Ϊ�ܶ�ʱ�����ǿ��ܽ���ֻ����base��Entity����һЩ���飬��û��client��
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
		@param result: �ش�����player ѡ���˵ڼ�����
		@type  result: UINT8
		@return: ��
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
		@return: ��
		"""
		if state:
			if self.ivfQuestTimerID is not None:
				self.stopVerifyCount()
		else:
			self.continueVerifyCount()

	def onTimer_imageVerify( self, timerID, userData ):
		"""
		for ECBExtend
		��������ʱ�䣬��ʼ����
		"""
		self.ivfQuestTime += imageVerify.ACTIVE_DELAY
		# ��������ʱ�䣬��ʼ����
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
# Ƶ���Ķ����� L3Common �аᵽ csdefine ��
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
# ͼƬ��֤��ش���
#
#
