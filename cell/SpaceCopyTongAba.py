# -*- coding: gb18030 -*-
#
#$Id:$

"""
14:23 2008-9-11,by wangshufeng
"""
"""
2010.11
家族擂台移植为帮会擂台 by cxm
"""
import BigWorld
from bwdebug import *
import time

import csdefine
import csconst
import csstatus

from SpaceCopy import SpaceCopy



class SpaceCopyTongAba( SpaceCopy ):
	"""
	帮会擂台赛副本空间
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		
		
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'tongDBID' : entity.tong_dbID }
		
		
	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		return csstatus.SPACE_OK
		
	def receiveAbaData( self, round, startTime ):
		"""
		Define method.
		接收擂台赛数据
		
		@param round : 帮会擂台赛的轮次
		@param startTime : 本轮开始时间
		"""
		DEBUG_MSG( "--------->>>round, startTime", round, startTime )
		self.abaRound = round
		self.abaStartTime = startTime
		if self.abaRound == csdefine.ABATTOIR_EIGHTHFINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 15 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		elif self.abaRound == csdefine.ABATTOIR_QUARTERFINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 15 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		elif self.abaRound == csdefine.ABATTOIR_SEMIFINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 15 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		elif self.abaRound == csdefine.ABATTOIR_FINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 20 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		
	def getAbaTimeInfo( self ):
		"""
		return 比赛已经开始了多长时间
		"""
		return BigWorld.time() - self.abaStartTime
	
	def getAbaRound( self ):
		return self.abaRound
		