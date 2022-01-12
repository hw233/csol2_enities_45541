# -*- coding: gb18030 -*-
#
# 牛魔王活动
#

from NormalActivityManager import NormalActivityManager
import cschannel_msgs
import ShareTexts as ST
import random
import BigWorld
from datetime import date
from bwdebug import *


LINE_NUMBER = 1
ORIGINAL_TIME = date( 1970, 1, 1 )
BASE_NUM = 2

class BovineDevilMgr( BigWorld.Base, NormalActivityManager ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_JTNM_BEGIN_NOTIFY_0
		self.startMsg 			= cschannel_msgs.BCT_JTNM_BEGIN_NOTIFY
		self.endMgs 			= cschannel_msgs.BCT_JTNM_BEGIN_NOTIFY_1
		self.errorStartLog 		= cschannel_msgs.NIU_MO_WANG_NOTICE_01
		self.errorEndLog 		= cschannel_msgs.NIU_MO_WANG_NOTICE_02
		self.globalFlagKey		= "BovineDevilStart"
		#self.spawnMonsterCount  = 40
		self.managerName 		= "BovineDevilMgr"
		self.crondNoticeKey		= "BovineDevilMgr_start_notice"
		self.crondStartKey		= "BovineDevilMgr_start"
		self.crondEndKey		= "BovineDevilMgr_end"
		self.gmSpaceName = ""
		NormalActivityManager.__init__( self )
		
	def spawnMonster( self ):
		"""
		"""
		spaceName = random.choice( self.monsterSpawnPoints.keys() )
		if self.gmSpaceName:
			spaceName = self.gmSpaceName
		if self.monsterSpawnPoints.has_key( spaceName ) and self.monsterSpawnPoints[ spaceName ].has_key( LINE_NUMBER ):
			spawnPoint = random.choice( self.monsterSpawnPoints[ spaceName ][ LINE_NUMBER ] )
			if not self.currMonsterSpawns.has_key( spaceName ):
				self.currMonsterSpawns[spaceName] = []
			self.currMonsterSpawns[spaceName].append( spawnPoint )
			now = date.today()
			days = ( now - ORIGINAL_TIME ).days				#今天跟1970年1月1日相隔的天数，如果是双数，刷第一个BOSS，如果是单数，刷第二个BOSS。
			if days % BASE_NUM == 0:
				spawnPoint.cell.createEntity( { "type":0 } )
			else:
				spawnPoint.cell.createEntity( { "type":1 } )
			INFO_MSG( "spaceName is %s,lineNumber is %s"%( spaceName, LINE_NUMBER ))

	def setGMSpaceName( self, spaceName ):
		"""
		GM设置刷怪的spaceName
		"""
		self.gmSpaceName = spaceName
