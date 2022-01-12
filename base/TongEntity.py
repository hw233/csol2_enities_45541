# -*- coding: gb18030 -*-
#
# $Id: TongEntity.py,v 1.22 2008-08-25 09:30:09 kebiao Exp $
"""
帮会和家族的框架和部分特性相同，但没有整合到一起，2个系统牵连性越小越好
帮会，家族系统支持动态加载，数据异步传输模式，编辑或者修改该功能的时候
必须考虑上面2种模式的发生性导致的一些问题.
written by kebiao, in 2008/06/23
"""

import time
import cschannel_msgs
import ShareTexts as ST
import items
import sys
import copy
import BigWorld
import csdefine
import csstatus
import csconst
import Love3
import time
import Define
import Const
import Function
import SkillLoader
import random
import math
import cPickle
from bwdebug import *
from MsgLogger import g_logger
from Message_logger import *
from Function import Functor
from interface.TongStorage import TongStorage
from interface.TongCampaign import TongCampaign
from interface.TongTerritory import TongTerritory
from interface.TongCityWarInterface import TongCityWarInterface
from interface.TongRobWarInterface import TongRobWarInterface
from csdefine import NONE_STATUS,LUNARHALO,SUNSHINE,STARLIGHT

from Love3 import g_tongItems
from Love3 import g_tongSpecItems
from TongCityWarFightInfos import MasterChiefData
from LevelEXP import TongLevelEXP as TLevelEXP

TIME_CBID_CHECK_REQUEST_JOIN			= 1			# timeID检测邀请加入tong的数据， 判断有没有过时的邀请 清理垃圾
CONST_REQUEST_JOIN_TIMEOUT				= 60		# 邀请加入tong请求超时的时间
CONST_CHIEF_CONJURE_TIMEOUT				= 30		# 队长集结令应答超时时间
CONST_CONTRIBUTE_INIT_VAL				= 100		# 每个帮会成员刚进入帮会时的初始化帮贡
TEMP_DATA_OVERTIME_INTERVAL				= 2			# 临时数据过期时间
COMPETITION_LEVEL_LIMIT					= 60		# 参加帮会竞技的成员等级限制
COMPETITION_MEMBER_LIMIT				= 1			# 参加帮会竞技的帮会人数最低限制

# 异步数据处理定义
TASK_KEY_MEMBER_DATA					= 1			# 处理成员数据
TASK_KEY_PERSTIGE_DATA					= 2			# 处理声望数据
TASK_KEY_AFFICHE_DATA					= 3			# 处理公告数据
TASK_KEY_MONEY_DATA						= 4			# 处理金钱数据
TASK_KEY_LEVEL_DATA						= 5			# 处理级别数据
TASK_KEY_LEAGUES_DATA					= 8			# 处理帮会同盟数据
TASK_KEY_DUTY_NAMES_DATA				= 9			# 处理帮会职位名称数据
TASK_KEY_HOLD_CITY_DATA					= 11		# 处理帮会所控制的城市数据
TASK_KEY_TONG_SIGN_MD5					= 17		# 帮会会标MD5信息
TASK_KEY_TONG_EXP						= 18		# 帮会经验
TASK_KEY_TONG_SKILL						= 19		# 帮会技能
TASK_KEY_BATTLE_LEAGUES_DATA			= 20		# 处理帮会战争同盟数据

TONG_NORMAL_QUEST_MAX_MAP = { 1:60, 2:120, 3:180, 4:240, 5:300, 6:360, 7:420, 8:480, 9:540, 10: 600 }		# 不同等级的帮会允许完成的日常任务次数
TONG_MERCHANT_QUEST_MAX_MAP = { 1:3, 2:4, 3:5, 4:5, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10 }        		# 跑商任务中帮会等级中对个人任务次数的限制

OLD_GRADE_MAPPING = { 0x00000001:1, 0x00000010: 2, 0x00000040:3, 0x00000080: 4 ,}

class MemberInfos:
	"""
	家族中成员的一些信息结构
	"""
	def __init__( self ):
		"""
		初始化成员信息
		"""
		self._isOnline = False					# 该成员是否在线
		self._name = ""							# 该成员的名称
		self._grade = 0							# 该成员的帮会权限
		self._class = 0							# 该成员的职业
		self._level = 0							# 该成员的级别
		self._spaceID = 0						# 该成员所在space位置
		self._lastPosition = ( 0, 0, 0 )		# 该成员最后一次查询所在位置
		self._reinstateGrade = 0				# 被重新任职
		self._entityBaseMailbox = None			# 该成员的baseMailbox
		self._scholium = ''						# 该成员的批注
		self._contribute = 0					# 该成员帮会贡献度
		self._totalContribute = 0				# 该成员帮会累积贡献度
		
		self._lastWeekTotalContribute = 0		# 该成员上周帮会累计帮贡值
		self._lastWeekSalaryReceived = 0		# 该成员上周领取俸禄值
		self._weekTongContribute = 0 			# 该成员本周获取帮贡值
		self._weekSalaryReceived = 0			# 该成员本周领取俸禄值

	def init( self, name, grade, eclass, level ):
		"""
		正式的初始填充各项属性
		"""
		self._name = name
		self._grade = grade
		self._class = eclass
		self._level = level

	def setReinstateGrade( self, grade ):
		self._reinstateGrade = grade

	def isOnline( self ):
		return self._isOnline

	def getName( self ):
		return self._name

	def getGrade( self ):
		return self._grade

	def getClass( self ):
		return self._class

	def getLevel( self ):
		return self._level

	def getBaseMailbox( self ):
		return self._entityBaseMailbox

	def getSpaceID( self ):
		return self._spaceID

	def getPosition( self ):
		return self._lastPosition

	def getScholium( self ):
		return self._scholium

	def getContribute( self ):
		return self._contribute

	def getTotalContribute( self ):
		return self._totalContribute

	def updateTotalContribute( self, val ):
		self._totalContribute = val

	def addTotalContribute( self, val ):
		self._totalContribute += val

	def setOnlineState( self, online ):
		"""
		设置在线状态
		@param online: bool, 在线或者不在线
		"""
		self._isOnline = online

	def setBaseMailbox( self, e ):
		"""
		设置该成员的baseMailbox
		@param e: entity or None
		"""
		if e == None and self.isOnline():
			ERROR_MSG( "member is online, entityMB set to None..." )
		self._entityBaseMailbox = e
		if self._entityBaseMailbox and self.isOnline():
			if self._reinstateGrade != 0 and self._grade != self._reinstateGrade:
				self._entityBaseMailbox.tong_setGrade( self._reinstateGrade )
				self._reinstateGrade = 0

	def setGrade( self, grade ):
		self._grade = grade

	def setLevel( self, level ):
		self._level = level

	def setPosition( self, pos ):
		self._lastPosition = pos

	def setSpaceID( self, spaceID ):
		self._spaceID = spaceID

	def setScholium( self, scholium ):
		self._scholium = scholium

	def setContribute( self, contribute ):
		self._contribute = contribute

	def setName( self, name ):
		self._name = name
	
	def setLastWeekTotalContribute( self, lastWeekTotalContribute ):
		self._lastWeekTotalContribute = lastWeekTotalContribute
		
	def getLastWeekTotalContribute( self ):
		return self._lastWeekTotalContribute
		
	def setLastWeekSalaryReceived( self, lastWeekSalaryReceived ):
		self._lastWeekSalaryReceived = lastWeekSalaryReceived
		
	def getLastWeekSalaryReceived( self ):
		return self._lastWeekSalaryReceived
		
	def updateWeekTongContribute( self, weekTongContribute ):
		self._weekTongContribute = weekTongContribute
		
	def addWeekTongContribute( self, val ):
		self._weekTongContribute += val
		
	def getWeekTongContribute( self ):
		return self._weekTongContribute
		
	def setWeekSalaryReceived( self, weekSalaryReceived ):
		self._weekSalaryReceived = weekSalaryReceived
		
	def getWeekSalaryReceived( self ):
		return self._weekSalaryReceived

class TongEntity(	BigWorld.Base,
					TongTerritory,
					TongCampaign,
					TongStorage,
					TongRobWarInterface,
					TongCityWarInterface
):
	"""
	帮会entity 帮会数据处理中心，维护一切帮会核心.
	"""
	def __init__( self ):
		"""
		初始化
		"""
		TongTerritory.__init__( self )
		TongCampaign.__init__( self )
		TongStorage.__init__( self )
		TongCityWarInterface.__init__( self )
		TongRobWarInterface.__init__( self )
		
		self._onlineMemberDBID = set([])
		self._requestJoinEntityList = {} 					# {邀请者dbid:被邀请者DBID:被邀请者basemailbox}
		self._check_RequestJoinTimerID = 0					# 检测邀请加入tong的数据， 判断有没有过时的邀请 清理垃圾
		self._requestLeagueRecord = {} 						# {被邀请者tongDBID}
		self._check_RequestLeagueTimerID = 0				# 检测邀请加入同盟tong的数据， 判断有没有过时的邀请 清理垃圾
		self._memberInfos = {}								# 成员的可用信息
		self._delayDataTasks = {}							# {memberDBID:[oterMemberDBID,...]}由于玩家客户端初始化信息一次性发送数据量过大，造成阻塞，所以需要异步数据发送，那么信息就需要放到一个队列去慢慢的给客户端
		self._chiefCommandInfo = {}							# 帮主令相关信息
		self._check_conjureTimerID	=	0					# 检测帮主令数据
		self._check_payChiefMoney_timerID = 0				# 帮主工资发放检测时间timer
		self._startupTimerID = 0							# startup过程改为由一个timer来触发， 避免在tongentity初始化过程调用，一些解散类似的操作会出问题。
		self._afterFeteTimerID = 0							# 用于取消帮会祭祀结束后获得的状态
		self.basePrestige = 0								# 帮会保底声望
		self.destroyTimerID = 0								# 帮会销毁timer

		self.chiefDBID = 0						# 帮主dbid
		self.chiefName = ""						# 帮主名字

		# 开除玩家，如果玩家不在线，那么直接操作数据库，清除玩家帮会数据；如果玩家在线，需要从玩家cell开始处理数据，但给玩家cell发送清除帮会
		# 数据指令后，有可能玩家cell entity已经销毁，此timer就是一个清理是否成功的检测，如果到期后玩家的数据没有被清除，那么表明玩家可能已经销毁，或者服务器通信出了问题。
		# 这里不考虑服务器通信或硬件问题，假设这个可靠性是100%的，如果到期玩家数据没有清除成功，那么当作玩家entity已经销毁处理，直接清理玩家数据库中的帮会数据。11:34 2010-11-6，wsf
		# 此机制同样应用于玩家加入帮会的临时数据清理。
		self.tempDataCheckTimer = 0
		self.kickMemberTempInfo = {}	# 离帮处理中的玩家数据
		self.joinMemberTempInfo = {}	# 入帮处理中的玩家数据
		self.gradeChangeTempData = {}	# 帮会权限改变处理中的玩家数据

		## 添加帮会多种指标的增益速度的控制措施，提供灵活更改这些指标增长速度的能力 ##
		# 以下这些量在相应的由定时器控制增加的各种相应指标中，作为百分比参与计算
		# by mushuang
		# 参见：CSOL-9750
		#self._afterFeteStatus = NONE_STATUS # 帮会祭祀完成之后获得的状态, persistent 属性
		
		self.tongAbaGatherFlag = None
		self.tongAbaRound = 0

		self.tongCompetitionGatherFlag = None

		# 广播一些帮会数据
		self.onBroadcastData()
		
		# 战争结盟
		self._inviteBattleLeagueRecord = {} 						# {被邀请者tongDBID}
		self._check_inviteBattleLeagueTimerID = 0					# 检测邀请加入同盟tong的数据， 判断有没有过时的邀请 清理垃圾
		
		# 加载所有成员的信息 第一次创建的时候会设置isCreate标记
		if not self.queryTemp( "isCreate", False ):
			BigWorld.globalData[ "tong.%i" % self.databaseID ] = self
			self.loadMemberInfoFromDB()
		else:
			self.writeToDB( self.onCreatedTongCallBack )


	def onCreatedTongCallBack( self, success, tongEntity ):
		"""
		帮会实体写入数据库回调
		"""
		if not success:
			ERROR_MSG( "creator %s TongEntity %s writeToDB is failed!" % ( self.chiefName, self.playerName ) )
		else:
			self._startupTimerID = self.addTimer( 0.01, 0, 0 )
			self.creatorInfo["baseMailbox"].cell.tong_createSuccess( self.databaseID, self )

	def createSuccess( self ):
		"""
		Define method.
		帮会创建成功

		self.creatorInfo 为创建帮会entity时传入的一个临时属性
		like as:
		creatorInfo = { "databaseID":creatorDBID, \
						"playerName":creatorName, \
						"level":creatorLevel, \
						"raceclass":creatorRaceclass, \
						"baseMailbox":creator, \
						}
		"""
		creatorName = self.creatorInfo["playerName"]
		creatorDBID = self.creatorInfo["databaseID"]
		creatorRaceclass = self.creatorInfo["raceclass"]
		creatorLevel = self.creatorInfo["level"]
		creatorBase = self.creatorInfo["baseMailbox"]
		
		self.camp = ( creatorRaceclass & csdefine.RCMASK_CAMP ) >> 20
		self.chiefDBID = creatorDBID
		self.chiefName = creatorName
		self.dutyNames = copy.deepcopy( Const.TONG_DUTY_NAME )
		self.saveChiefdate = int( time.time() )
		self.initTongItems()
		self.initTongSpecialItems()

		INFO_MSG( "creator %s TongEntity %s writeToDB is successfully! " % ( creatorName, self.playerName ) )
		BigWorld.globalData[ "tong.%i" % self.databaseID ] = self
		BigWorld.globalBases["TongManager"].onRegisterTongOnCreated( creatorDBID, self, self.playerName, self.databaseID, self.chiefName, self.camp )
		# 把创建者数据加入帮会
		creatorBase.tong_onJoin( self.databaseID, csdefine.TONG_DUTY_CHIEF, self )

		# 玩家数据加入帮会需要在onRegisterTongOnCreated注册到帮会管理器之后，因为加入玩家后需更新帮会数据到管理器，此时必须保证帮会在管理器中已经注册
		self.onJoin( creatorDBID, creatorName, creatorLevel, creatorRaceclass, creatorBase, csdefine.TONG_DUTY_CHIEF, csconst.JOIN_TONG_CHIEF_INIT_CONTRIBUTE )
		self.calBasePrestige()
		creatorBase.client.tong_onCreateSuccessfully( self.databaseID, self.playerName )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_TONG_ESTABLISH_NOTIFY % ( creatorName, self.playerName ), [] )

	def getTongManager( self ):
		return BigWorld.globalBases["TongManager"]

	def getMailMgr( self ):
		return BigWorld.globalData[ "MailMgr" ]

	def getMemberInfos( self, memberDBID ):
		return self._memberInfos[ memberDBID ]

	def getNameAndID( self ):
		"""
		获取帮会的名称和DBID
		"""
		return self.playerName + "(%s)" % self.databaseID

	def getName( self ):
		return self.playerName
	
	def getCamp( self ):
		return self.camp

	#------------------------------------------------------------------------------------------
	def onBroadcastData( self ):
		"""
		广播数据被改变 主要是提供给角色登陆后， 一些重要数据需要立即给到cellData中
		"""
		key = "tong.%i" % self.databaseID
		if not BigWorld.baseAppData.has_key( key ):
			BigWorld.baseAppData[ key ] = {}

		baseAppData = BigWorld.baseAppData[ key ]
		baseAppData[ "level" ] = self.level
		BigWorld.baseAppData[ key ] = baseAppData

	#------------------------------------------------------------------------------------------
	def queryTemp( self, key, default = None ):
		"""
		根据关键字查询临时mapping中与之对应的值

		@return: 如果关键字不存在则返回default值
		"""
		try:
			return self.tempMapping[key]
		except KeyError:
			return default

	def setTemp( self, key, value ):
		"""
		define method.
		往一个key里写一个值

		@param   key: 任何PYTHON原类型(建议使用字符串)
		@param value: 任何PYTHON原类型(建议使用数字或字符串)
		"""
		self.tempMapping[key] = value

	def popTemp( self, key, default = None ):
		"""
		移除并返回一个与key相对应的值
		"""
		return self.tempMapping.pop( key, default )

	def removeTemp( self, key ):
		"""
		define method.
		移除一个与key相对应的值
		@param   key: 任何PYTHON原类型(建议使用字符串)
		"""
		self.tempMapping.pop( key, None )

	#------------------------------------------------------------------------------------------
	def addMemberInfos( self, memberDBID, memberInfo ):
		"""
		向信息表添加该成员的可用信息
		"""
		self._memberInfos[ memberDBID ] = memberInfo
		self.addMemberTotalContributeRecord( memberDBID, memberInfo.getContribute() )

	def createMemberInfo( self, mDBID, mName, mLevel, mClass, \
						mBaseMailbox, mgrade, scholium, contribute ):
		"""
		创建帮会成员信息实例
		"""
		infos = MemberInfos()
		infos.init( mName, mgrade, mClass, mLevel )
		infos.setOnlineState( mBaseMailbox is not None )
		infos.setBaseMailbox( mBaseMailbox )
		infos.setScholium( scholium )
		infos.setContribute( contribute )
		return infos

	def addMember( self, memberDBID, memberInfo ):
		"""
		加入新帮会成员
		"""
		self._memberInfos[ memberDBID ] = memberInfo
		self.addMemberTotalContributeRecord( memberDBID, memberInfo.getContribute() )
		self.onMemberCountChanged()
		try:
			g_logger.tongMemberAddLog( self.databaseID, self.getName(), memberDBID, memberInfo.getName(), len(self._memberInfos) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def removeMember( self, playerDIBD ):
		"""
		移除一个成员
		"""
		try:
			playerName = self._memberInfos.pop( playerDIBD )
		except KeyError:
			ERROR_MSG( "cannot find tong memeber( %i )" % playerDBID )
		if self.inDestroy():
			DEBUG_MSG( "tongEntity( %i ) is destroying..." % self.databaseID )
			return
		self.onMemberCountChanged()
		try:
			g_logger.tongMemberRemoveLog( self.databaseID, self.getName(), playerDIBD, playerName,len(self._memberInfos) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
	def hasMember( self, playerDIBD ):
		return playerDIBD in self._memberInfos

	def onMemberCountChanged( self ):
		"""
		成员数量有改变
		"""
		self.memberCount = len( self._memberInfos )
		self.calPrestige()			# 帮会成员数量变化引起保底声望变化
		# 将数据更新到管理器
		self.getTongManager().updateTongMemberCount( self.databaseID, self.memberCount )

	#------------------------------------------------------------------------------------------
	def updateTotalContributeToMemberInfos( self ):
		"""
		同步个人帮会累积贡献度到成员信息结构中(一般只需要在重启之后帮会加载后进行一次操作)
		"""
		for memberDBID, memberInfo in self._memberInfos.iteritems():
			for item in self.memberTotalContributes:
				if item[ "dbID" ] == memberDBID:
					memberInfo.updateTotalContribute( item[ "totalContribute" ] )
					memberInfo.setLastWeekTotalContribute( item[ "lastWeekTotalContribute" ])
					memberInfo.setLastWeekSalaryReceived( item[ "lastWeekSalaryReceived" ])
					memberInfo.updateWeekTongContribute( item[ "weekTongContribute" ])
					memberInfo.setWeekSalaryReceived( item[ "weekSalaryReceived" ])
					continue 

	def addMemberTotalContributeRecord( self, memberDBID, val ):
		"""
		记录个人累积帮贡， 降低帮贡我们不进行记录， 只记录增加帮贡
		"""
		info = self.getMemberInfos( memberDBID )
		if val <= 0:
			return info.getTotalContribute()

		# 同步到成员信息结构中
		info.addTotalContribute( val )
		info.addWeekTongContribute( val )			# 个人本周帮贡累计
		self.weekTongTotalContribute += val			# 帮会本周帮贡累计
		
		for item in self.memberTotalContributes:
			if item[ "dbID" ] == memberDBID:
				item[ "totalContribute" ] += val
				item[ "weekTongContribute"] += val
				return item[ "totalContribute" ]
				
		# 如果还没记录则新增一条
		self.memberTotalContributes.append( { "dbID" : memberDBID, "totalContribute" : val, "weekTongContribute": val, "weekSalaryReceived": 0, "lastWeekTotalContribute": 0, "lastWeekSalaryReceived": 0 } )
		return val

	def removeMemberTotalContributeRecord( self, memberDBID ):
		"""
		删除成员的累积帮贡记录
		"""
		for item in self.memberTotalContributes:
			if item[ "dbID" ] == memberDBID:
				self.memberTotalContributes.remove( item )
				return

	#------------------------------------------------------------------------------------------
	def onDestroy( self ):
		"""
		当销毁的时候做点事情
		"""
		self.save()

	#------------------------------------------------------------------------------------------
	def save( self ):
		"""
		服务器将要重启
		"""
		self.writeToDB()

	#------------------------------------------------------------------------------------------
	def loadMemberInfoFromDB( self ):
		"""
		从数据库加载成员信息
		"""
		cmd = "select id, sm_tong_grade, sm_tong_scholium, sm_playerName, sm_level, sm_raceclass, tbl_Role.sm_tong_contribute from tbl_Role where %i = tbl_Role.sm_tong_dbID;" % self.databaseID
		BigWorld.executeRawDatabaseCommand( cmd, self.loadMemberInfoFromDB_Callback )

	def loadMemberInfoFromDB_Callback( self, results, dummy, error ):
		"""
		加载成员信息 数据库回调
		"""
		if (error):
			ERROR_MSG( error )
			return

		if len( results ) <= 0:
			# 出现这个原因可能是某人删除了帐号
			DEBUG_MSG( "tong %s:%i can't found all member!" % ( self.playerName, self.databaseID ) )
		else:
			for result in results:
				entityDBID				= int( result[0] )
				tongGrade				= int( result[1] )
				tongScholium 			= result[2]
				mName					= result[3]
				mLevel					= int( result[4] )
				mClass					= int( result[5] )
				tongContribute			= int( result[6] )
				if tongGrade not in csdefine.TONG_DUTYS:
					if tongGrade in OLD_GRADE_MAPPING.keys():
						tongGrade = OLD_GRADE_MAPPING[ tongGrade ]
					else:
						tongGrade = csdefine.TONG_DUTY_MEMBER
				memberInfo = self.createMemberInfo( entityDBID, mName, mLevel, mClass, None, tongGrade, tongScholium, tongContribute )
				self.addMemberInfos( entityDBID, memberInfo )

				if tongGrade == csdefine.TONG_DUTY_CHIEF:
					self.chiefDBID = entityDBID
					self.chiefName = mName

		# 通知manager加载完毕 做一些事情.
		self.getTongManager().onTongEntityLoadMemberInfoComplete( self.databaseID, self, self.chiefName )
		# 更新一下帮会成员数量
		self.memberCount = len( self._memberInfos )
		# 开启帮会启动程序
		self._startupTimerID = self.addTimer( 0.01, 0, 0 )

	def removeMemberFromDB( self, memberDBID ):
		"""
		从数据库中删除某成员的帮会信息
		"""
		cmd = "update tbl_Role set sm_tong_dbID=0, sm_tong_grade=0, tbl_Role.sm_tong_scholium=\'\', tbl_Role.sm_tong_contribute=0 where %i = tbl_Role.id;" % memberDBID
		BigWorld.executeRawDatabaseCommand( cmd, self.removeMemberFromDB_Callback )

	def removeMemberFromDB_Callback( self, result, dummy, error ):
		"""
		删除成员信息 数据库回调
		"""
		if (error):
			ERROR_MSG( error )
			return

	#------------------------------------------------------------------------------------------
	def onTongStartup( self ):
		"""
		帮会系统启动(通常是系统重启后建立了帮会entity,加载完所有数据后)
		"""
		# 每整点检查一次 帮主工资发放情况
		self._check_payChiefMoney_timerID = self.addTimer( ( 60 - time.localtime()[4] ) * 60, 60 * 60, 0 )
		# 同步个人帮会累积贡献度到成员信息结构中
		self.updateTotalContributeToMemberInfos()
		# 初始化帮会祭祀完成后所获得的状态
		self.__initAfterFeteStatus()

	#---------------------------------------------------------------------------------------------------------
	def setTID( self, tid ):
		"""
		define method.
		设置帮会ID
		"""
		self.tid = tid
		self.save()

	def getTID( self ):
		"""
		获取帮会ID
		"""
		return self.tid

	def setAD( self, ad ):
		"""
		define method.
		设置帮会ID
		"""
		self.ad = ad
		self.save()
		chiefMailBox = self.getMemberInfos( self.chiefDBID ).getBaseMailbox() #帮主的mailbox
		self.statusMessage( chiefMailBox, csstatus.TONG_AD_FINISHED )


	def initTongIDAndAD( self, tid, ad ):
		"""
		define method.
		过渡性接口，  把tid和广告信息由tongmanager转移到这里来， 新版本
		tongmanager不再保存这些信息， 由数据库中tong_entity表初始化。
		"""
		self.setTID( tid )
		self.ad = ad

	#---------------------------------------------------------------------------------------------------------
	def clearMemberInfo( self, memberDBID ):
		"""
		清理帮会成员的数据
		"""
		# 删除他的累积帮贡记录
		self.removeMemberTotalContributeRecord( memberDBID )
		# 删除购买帮会物品记录
		self.removeBuyTongItemRecord( memberDBID )
		# 更新所有在线成员的客户端的成员列表中删除该成员
		for dbid in self._onlineMemberDBID:
			if dbid != memberDBID:
				otherMember = self.getMemberInfos( dbid ).getBaseMailbox()

				# 如果我还在对方的数据更新列表中那么 将他清除避免再更新到客户端 否则清除对方的客户端上的我
				if self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
					self.delMemberFromDelayTaskMember( dbid, memberDBID )
				else:
					if hasattr( otherMember, "client" ):
						otherMember.client.tong_onDeleteMemberInfo( memberDBID )

				if memberDBID in self._onlineMemberDBID:
					if hasattr( otherMember, "cell" ):
						otherMember.cell.tong_onMemberRemoveOL( memberDBID )

		memberMailbox = self.getMemberInfos( memberDBID ).getBaseMailbox()
		if memberMailbox:	# 如果成员在线，那么处理缓存数据和在线数据
			if self.isInDelayTaskList( memberDBID ):
				self.delDelayTaskMember( memberDBID )
			self._onlineMemberDBID.remove( memberDBID )

		self.removeMember( memberDBID )

	def memberLeave( self, memberDBID ):
		"""
		Define method.
		玩家在线时离开帮会的处理

		@param memberDBID : 离开的成员databaseID
		"""
		try:
			memberMailbox = self.getMemberInfos( memberDBID ).getBaseMailbox()
		except:
			return
		DEBUG_MSG( "member( %i ) leave tong " % ( memberDBID ) )
		if self.isJoinTongCityWar: # 城战期间不给退帮会CSOL-11589
			self.statusMessage( memberMailbox, csstatus.TONG_CITY_WAR_CANNOT_QUIT )
			return
			
		memberMailbox.client.tong_onSetTongSignMD5( "tcbh" )
		memberMailbox.cell.tong_leave()
		memberMailbox.client.tong_meQuit()

		# 清理帮会擂台数据
		if self.tongAbaGatherFlag:
			memberMailbox.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
		if self.tongAbaRound:
			memberMailbox.client.receiveAbaRound( 0 )
		
		if self.tongCompetitionGatherFlag:
			memberMailbox.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )
		
		# 清理帮会数据
		self.clearMemberInfo( memberDBID )
		self.save()
		self.memberLeaveSuccess( memberDBID )

	def startTempDataCheck( self ):
		"""
		"""
		if not self.tempDataCheckTimer:	# 启动临时数据检测机制
			self.tempDataCheckTimer = self.addTimer( TEMP_DATA_OVERTIME_INTERVAL, TEMP_DATA_OVERTIME_INTERVAL, 0 )

	def endTempDataCheck( self ):
		"""
		"""
		if not self.tempDataCheckTimer or len( self.kickMemberTempInfo ) or len( self.joinMemberTempInfo ):
			return
		self.delTimer( self.tempDataCheckTimer )
		self.tempDataCheckTimer = 0

	def addMemberLeaveCheck( self, memberDBID ):
		"""
		帮会成员离开帮会处理流程
		"""
		self.kickMemberTempInfo[memberDBID] = time.time()
		self.startTempDataCheck()

	def memberLeaveSuccess( self, memberDBID ):
		"""
		玩家离开帮会成功
		"""
		try:
			del self.kickMemberTempInfo[memberDBID]
		except KeyError:
			return
		self.endTempDataCheck()

	def onTempDataCheckTimerCheck( self ):
		"""
		"""
		try:		# 捕捉这种无限循环timer中的异常，避免中断处理无法停止timer
			nowTime = time.time()
			for memberDBID, leaveTime in self.kickMemberTempInfo.items():
				if nowTime - leaveTime > TEMP_DATA_OVERTIME_INTERVAL:	# 到期没清理成功
					del self.kickMemberTempInfo[memberDBID]
					self.clearMemberInfo( memberDBID )
					#self.removeMemberFromDB( memberDBID )				# 直接从数据库中移除
			for memberDBID, joinTime in self.joinMemberTempInfo.items():
				if nowTime - joinTime > TEMP_DATA_OVERTIME_INTERVAL:	# 到期没入帮成功
					del self.joinMemberTempInfo[memberDBID]
			for memberDBID, info in self.gradeChangeTempData.items():
				if nowTime - info[1] > TEMP_DATA_OVERTIME_INTERVAL:		# 到期设置不成功
					del self.gradeChangeTempData[memberDBID]
					self.updateGrade2DB( memberDBID, info[0] )			# 直接设置数据库
		except:
			EXCEHOOK_MSG( "捕捉这种无限循环timer中的异常，避免中断处理无法停止timer。" )
		if len( self.kickMemberTempInfo ) or len( self.joinMemberTempInfo ) or len( self.gradeChangeTempData ):
			return
		self.delTimer( self.tempDataCheckTimer )
		self.tempDataCheckTimer = 0

	def addChangeGradeChek( self, memberDBID, grade ):
		"""
		给设置临时数据监测加入数据
		"""
		self.gradeChangeTempData[memberDBID] = ( grade, time.time )
		self.startTempDataCheck()

	def changeGradeSuccess( self, memberDBID ):
		"""
		Define method.
		改变玩家的帮会职位成功
		"""
		try:
			del self.gradeChangeTempData[memberDBID]
		except KeyError:
			return
		self.endTempDataCheck()

	def addMemberJoinCheck( self, memberDBID ):
		"""
		"""
		self.joinMemberTempInfo[memberDBID] = time.time()
		self.startTempDataCheck()

	def memberJoinSuccess( self, memberDBID ):
		"""
		"""
		try:
			del self.joinMemberTempInfo[memberDBID]
		except KeyError:
			return
		self.endTempDataCheck()

	#---------------------------------------------------------------------------------------------------------
	def canDismiss( self ):
		"""
		是否可以解散帮会
		"""
		if len( self.joinMemberTempInfo ):	# 如果正在处理玩家入帮数据，则不能解散帮会
			return False
		return True

	def onDismissTong( self, memberDBID, reason ):
		"""
		define method
		解散帮会
		"""
		DEBUG_MSG( "chief dismiss of tong. %i, %s" % ( self.databaseID, self.playerName ) )
		if memberDBID > 0:
			info = self.getMemberInfos( memberDBID )
			if not self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_DISMISS_TONG ):
				return
			
			if self.isJoinTongCityWar:
				self.statusMessage( info.getBaseMailbox(), csstatus.TONG_CITY_WAR_CANNOT_DISMISS )
				return
				
		if not self.canDismiss():	# 就算是帮会资金不足自动解散也不允许，否则会造成玩家帮会数据异常，不妨等下一次资金不足的检查
			DEBUG_MSG( "( %i )i am in member joining progress..." % self.databaseID )
			return
		if self.inDestroy():
			return
		self.setTongSignMD5( "" )
		self.resetMemberDelayTaskData()

		# 清理帮会成员身上的帮会信息， 并给予遣散费
		for memberDBID, info in self._memberInfos.items():
			emb = self.getMemberInfos( memberDBID ).getBaseMailbox()
			if emb is None:	# 玩家不在线
				# 清理帮会数据
				self.clearMemberInfo( memberDBID )
				#self.removeMemberFromDB( memberDBID )
			else:
				if hasattr( emb, "cell" ):
					emb.cell.tong_leave()
				if hasattr( emb, "client" ):
					emb.client.tong_onDismissTong()
				self.addMemberLeaveCheck( memberDBID )

		self.getTongManager().onTongDismiss( self.databaseID, reason )
		# 通知同盟帮会 解除同盟.
		for league in self.leagues:
			self.getTongManager().leagueDispose( league[ "dbID" ], self.databaseID )
		
		# 解散战争同盟
		for battleLeague in self.battleLeagues:
			self.getTongManager().battleLeagueAutoDispose( battleLeague[ "dbID" ], self.databaseID )

		self.destroyTimerID = self.addTimer( TEMP_DATA_OVERTIME_INTERVAL + 3 )	# 延时销毁，帮会解散清除帮会成员帮会数据时他刚好下线，那么需要帮会entity从数据库中清除。

	def inDestroy( self ):
		"""
		"""
		return self.destroyTimerID != 0

	#---------------------------------------------------------------------------------------------------------
	def kickMember( self, kickerDBID, targetDBID ):
		"""
		Define method.
		开除玩家出帮会

		@param kickerDBID : 请求执行开除行为的玩家dbid
		@param targetDBID : 被请求开除的玩家dbid
		"""
		if not self.hasMember( targetDBID ):
			HACK_MSG( "kicker(%i) request target(%i):there is no target info." % ( kickerDBID, targetDBID ) )
			return
		DEBUG_MSG( "kickerDBID=%i, targetDBID=%i" % ( kickerDBID, targetDBID ) )
		kickerInfo = self.getMemberInfos( kickerDBID )
		kickerGrade = kickerInfo.getGrade()
		if not self.checkMemberDutyRights( kickerGrade, csdefine.TONG_RIGHT_MEMBER_MANAGE ): # 没有开除权限
			DEBUG_MSG( "(%i) dont have kick Permissions." % ( kickerDBID ) )
			self.statusMessage( kickerInfo.getBaseMailbox(), csstatus.TONG_CANT_KICK_NO_GRADE )
			return
		targetInfo = self.getMemberInfos( targetDBID )
		if targetInfo.getGrade() >= kickerGrade:				# 您只能开除帮会中职务比自己低的玩家。
			DEBUG_MSG( "(%i) cant kick tong chief(%i)." % ( kickerDBID, targetDBID ) )
			self.statusMessage( kickerInfo.getBaseMailbox(), csstatus.TONG_CANT_KICK_LOW_GRADE )
			return
		
		#if targetInfo.getGrade() == csdefine.TONG_GRADE_DEALER:	# 不能开除商人 没有商人这个角色
		#	self.statusMessage( kickerInfo.getBaseMailbox(), csstatus.TONG_CANT_KICK_CHAPMAN )
		#	return

		# 进入删除帮会成员流程
		targetMailbox = targetInfo.getBaseMailbox()
		if targetMailbox is None:	# 玩家不在线
			# 清理帮会数据
			self.clearMemberInfo( targetDBID )
			#self.removeMemberFromDB( targetDBID )
		else:
			targetMailbox.cell.tong_leave()
			self.addMemberLeaveCheck( targetDBID )
			self.statusMessage( targetMailbox, csstatus.TONG_BE_KICKED, kickerInfo.getName() )
		for dbid in self._onlineMemberDBID:
			if dbid == targetDBID:
				continue
			self.statusMessage( self.getMemberInfos( dbid ).getBaseMailbox(), csstatus.TONG_KICK_MEMBER, targetInfo.getName(), kickerInfo.getName() )

	#---------------------------------------------------------------------------------------------------------
	def onPrestigeChanged( self ):
		"""
		帮会声望改变了
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_PERSTIGE_DATA ):
				emb.client.tong_onSetTongPrestige( self.prestige )
				emb.client.tong_onSetVariablePrestige( self.prestige - self.basePrestige )

		# 将数据更新到管理器
		self.getTongManager().updateTongPrestige( self.databaseID, self.prestige )

	def addPrestige( self, prestige, reason ):
		"""
		define method.
		添加声望
		"""
		if prestige < 0:
			self.payPrestige( abs(prestige), reason )
		else:
			oldPrestige = self.prestige
			self.prestige += prestige
			try:
				g_logger.tongPrestigeChangeLog( self.databaseID, self.getName(), oldPrestige, self.prestige, reason )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			
		self.onPrestigeChanged()
		
	def payPrestige( self, val,reason ):
		"""
		支付声望
		"""
		val = int( val )
		if val <= 0:
			return
		variablePrestige = self.prestige - self.basePrestige
		if variablePrestige < val:	# 帮会声望最小值为保底声望
			val = variablePrestige
		oldPrestige = self.prestige
		self.prestige -= val
		self.onPrestigeChanged()
		
		try:
			g_logger.tongPrestigeChangeLog( self.databaseID, self.getName(), oldPrestige, self.prestige, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def calBasePrestige( self ):
		"""
		计算保底声望
		"""
		memberCount = len( self._memberInfos )
		if memberCount == 0:	# 没有帮会成员
			self.basePrestige = 0
			return
		totalLevel = 0
		for info in self._memberInfos.itervalues():
			totalLevel += info.getLevel()
		self.basePrestige = int( totalLevel / memberCount )

	def calPrestige( self ):
		"""
		计算声望值
		"""
		variablePrestige = self.prestige - self.basePrestige	# 获得当前的可变声望
		self.calBasePrestige()									# 重新计算保底声望
		self.prestige = variablePrestige + self.basePrestige
		self.onPrestigeChanged()

	def addBasePrestige( self, prestige ):
		"""
		define method
		增加帮会基础声望
		"""
		self.basePrestige += prestige
		self.onPrestigeChanged()

	#------------------------------------------------------------------------------------------
	def addExp( self, value, reason = None ):
		"""
		define method
		经验增加
		@type	value : int32
		@param	value : 经验值
		"""
		if self.spendMoney > 0:			# CSOL- 2118 欠维护费不让加经验
			INFO_MSG( "Tong[%i : %s] own money( spendMoney: %s ), can't add exp!" % ( self.databaseID, self.playerName, self.spendMoney ) )
			return
		level = self.level
		oldValue = self.EXP
		if level > TLevelEXP.getMaxLevel():
			return
		
		DEBUG_MSG( "TONG: %s has gained %i exp, reason is %s" % ( self.getNameAndID(), value, reason ) )
		
		exp = value + self.EXP
		expMax = TLevelEXP.getEXPMax( self.level )		# 当前等级的 exp 最大值

		while exp >= expMax :
			exp -= expMax								# 减去将要升级的 exp 最大值
			level += 1
			self.addLevel( 1, csdefine.TONG_LEVEL_CHANGE_REASON_ADD_EXP )
			expMax = TLevelEXP.getEXPMax( level )
			if expMax <= 0 :
				ERROR_MSG( "Error exp max: %d" % expMax )
				break
		
		if level > TLevelEXP.getMaxLevel() :			# 将等级限制在限制等级以内
			level = TLevelEXP.getMaxLevel()
			exp = TLevelEXP.getEXPMax( level )

		self.EXP = max( 0, exp )						# 设置剩下的 exp
		try:
			g_logger.tongExpChangeLog( self.databaseID, self.getName(), oldValue, self.EXP, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onExpChanged( self, value, exp, reason ):
		"""
		帮会经验改变
		"""
		# 通知客户端进行更新
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_TONG_EXP ):
				emb.client.tong_onSetTongExp( exp )

#------------------------------------------------------------------------------------------
	def onLevelChanged( self ):
		"""
		帮会级别改变了
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_LEVEL_DATA ):
				emb.cell.tong_onSetTongLevel( self.level )

		# 将数据更新到管理器
		self.getTongManager().updateTongLevel( self.databaseID, self.level )
		self.upgradeBuildingLevel()		# 更新帮会建筑及其相应的功能
		self.onBroadcastData()
		self.initTongSpecialItems( 1 )

	def degrade( self, level, reason ):
		"""
		define method.
		帮会降级
		"""
		if self.level <= 1:
			return

		oldLevel = self.level
		self.level -= level
		self.onLevelChanged()
		self.statusMessageToOnlineMember( csstatus.TONG_DEGRADE )
		try:
			g_logger.tongDemotionLog( self.databaseID, self.getName(), self.level, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setLevel( self, level, reason ):
		"""
		define method
		设置帮会等级,GM指令用到
		"""
		if level > TLevelEXP.getMaxLevel():
			self.statusMessageToOnlineMember( csstatus.TONG_LEVEL_CAN_NOT_GAIN_EXP )
			return
		
		self.level = level
		self.onLevelChanged()
		self.statusMessageToOnlineMember( csstatus.TONG_STATE_SET_LEVEL, level )

	def addLevel( self, level, reason ):
		"""
		define method.
		添加级别
		"""
		INFO_MSG( "TONG: %s add %i level, old level is %i, new level is %i , reason is %s" % ( self.getNameAndID(), level, self.level, self.level + level, reason ) )
		oldLevel = self.level
		self.level += level
		self.onLevelChanged()
		self.statusMessageToOnlineMember( csstatus.TONG_UPGRADE )
		
		try:
			g_logger.tongUpgradeLog( self.databaseID, self.getName(), self.level, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	#------------------------------------------------------------------------------------------
	def onMoneyChanged( self ):
		"""
		帮会金钱改变了
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_MONEY_DATA ):
				emb.client.tong_onSetTongMoney( self.money )

		# 回调给领地模块， 自动补交建筑维护费
		TongTerritory.onMoneyChanged( self )

	def isMoneyLessKeepMoney( self, offset = 0 ):
		"""
		帮会资金是否小于保底资金
		@param offset: 通过这个偏移量来测试不同的情况
		"""
		return ( self.money + offset ) < self.getKeepMoney()

	def addMoney( self, money, reason ):
		"""
		define method.
		添加金钱
		"""
		money = int( money )
		if money <= 0:
			EXCEHOOK_MSG("add tongMoney[%i]<=0, reason:%i" % (money, reason))
			return

		oldValue = self.money
		currentValue = oldValue + money
		if currentValue > Const.TONG_MONEY_LIMIT[ self.jk_level ][ 1 ]:	# 检查帮会资金上限
			self.money = Const.TONG_MONEY_LIMIT[ self.jk_level ][ 1 ]
			self.statusMessageToOnlineMember( csstatus.TONG_MONEY_MAX )
		elif currentValue < 0:
			self.money = 0
		else:
			self.money = currentValue
			self.weekTongMoney += money 			# 统计帮会一周的资金输入

		self.onMoneyChanged()
		try:
			g_logger.tongMoneyChangeLog( self.databaseID, self.getName(), oldValue, self.money, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def getValidMoney( self ):
		"""
		获取帮会可用资金（除去保底资金）
		"""
		if self.isMoneyLessKeepMoney():
			return 0
		return self.money - self.getKeepMoney()

	def getKeepMoney( self ):
		"""
		获取帮会的保底资金数额
		"""
		return Const.TONG_MONEY_LIMIT[ self.jk_level ][ 0 ]

	def payMoney( self, val, islimit = True, reason = csdefine.TONG_CHANGE_MONEY_NORMAL ):
		"""
		支付帮会资金
		"""
		val = int( val )
		if val <= 0:
			return True

		if self.money <= 0:
			return False

		if islimit:	# 检查帮会资金下限
			if self.isMoneyLessKeepMoney( -val ):
				return False

		oldValue = self.money
		self.money -= val
		if self.money < 0:
			self.money = 0
			self.weekTotalCost += oldValue			# 周帮会资金支出
		else:
			self.weekTotalCost += val
		self.onMoneyChanged()

		try:
			g_logger.tongMoneyChangeLog( self.databaseID, self.getName(), oldValue, self.money, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def getDiscountMoney( self, money ):
		"""
		计算出占领城市打折优惠后的帮会资金，目前是八折
		"""
		if self.holdCity:
			money *= 0.8
		return int( math.ceil( money ) )

	#------------------------------------------职务权限-------------------------------------------------------
	
	def checkMemberDutyRights( self, duty, right ):
		"""
		检测某位置的权限
		"""
		dutyMapping = csdefine.TONG_DUTY_RIGHTS_MAPPING
		if duty not in dutyMapping.keys():
			return False
		
		if right not in dutyMapping[ duty ]:
			return False
		
		return True
	#------------------------------------------------------------------------------------------
	def setMemberGrade( self, userDBID, targetDBID, grade ):
		"""
		define method.
		user设置target权限(职务)
		@param userDBID   : 使用该接口的用户DBID
		@param targetDBID : 被设置者DBID
		@param grade  	  : 最终要设置的权限
		"""
		DEBUG_MSG( "%i:set to target(%i) the grade=%i" % ( userDBID, targetDBID, grade ) )
		if grade not in csdefine.TONG_DUTYS:
			return
		# 检查userDBID的权限 是否可以设置 targetDBID的权限
		userGrade = self.getMemberInfos( userDBID ).getGrade()
		targetGrade = self.getMemberInfos( targetDBID ).getGrade()
		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_CHANGE_DUTY ): # 没有开除权限
			return
		if targetGrade == grade or userGrade <= targetGrade or userGrade <= grade:
			return

		if grade == csdefine.TONG_DUTY_DEPUTY_CHIEF:		# 副帮主
			xcount = self.getCountByGrade( grade )
			# 副帮主数量达到最大
			if xcount >= csdefine.TONG_DUTY_CHIEF_SUBALTERN_COUNT:
				mb = self.getMemberInfos( userDBID ).getBaseMailbox()
				if mb:
					self.statusMessage( mb, csstatus.TONG_CHIEF_SUBALTERN_MAX )
				return
			self.saveAdjutantChiefdate.append( { "dbID": targetDBID, "time": int( time.time() ) } )		# 保存新副帮主就职时间, 主要是提供给工资发放使用

		elif grade == csdefine.TONG_DUTY_TONG:					# 堂主
			xcount = self.getCountByGrade( grade )
			if xcount >= csdefine.TONG_DUTY_TONG_COUNT:
				# 堂主数量达到最大
				mb = self.getMemberInfos( userDBID ).getBaseMailbox()
				if mb:
					self.statusMessage( mb, csstatus.TONG_GRADE_TONG_MAX )
				return

		if targetGrade == csdefine.TONG_DUTY_DEPUTY_CHIEF:	# 移除原来的副帮主就职时间
			for recordTime in self.saveAdjutantChiefdate:
				if recordTime[ "dbID" ] == targetDBID:
					self.saveAdjutantChiefdate.remove( recordTime )

		targetBaseMailbox = self.getMemberInfos( targetDBID ).getBaseMailbox()
		if targetBaseMailbox:
			targetBaseMailbox.tong_setGrade( grade )
			self.addChangeGradeChek( targetDBID, csdefine.TONG_DUTY_MEMBER )
		else:
			cmd = "update tbl_Role set sm_tong_grade=%i where id=%i;" % ( grade, targetDBID )
			BigWorld.executeRawDatabaseCommand( cmd )

		self.onMemberGradeChanged( userDBID, targetDBID, grade )
		try:
			g_logger.tongSetGradeLog( self.databaseID, self.getName(), userDBID, self._memberInfos[ userDBID ].getName(), targetDBID, self._memberInfos[ targetDBID ].getName(), targetGrade, grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		
	def getCountByGrade( self, grade ):
		"""
		获取某一种职位人数
		"""
		xcount = 0
		for info in self._memberInfos.itervalues():
			if info.getGrade() == grade:
				xcount += 1
		return xcount

	def onMemberGradeChanged( self, userDBID, memberDBID, grade ):
		"""
		define method.
		某成员的权限改变了
		"""
		ograde = self.getMemberInfos( memberDBID ).getGrade()
		if grade == ograde:
			return

		self.getMemberInfos( memberDBID ).setGrade( grade )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberGradeChanged( userDBID, memberDBID, grade )    # 更新其他成员的客户端

	#------------------------------------------------------------------------------------------
	def setMemberScholium( self, userDBID, targetDBID, scholium ):
		"""
		define method.
		user设置target备注
		@param userDBID   : 使用该接口的用户DBID
		@param targetDBID : 被设置者DBID
		@param grade  	  : 最终要设置的权限
		"""
		DEBUG_MSG( "%i:set to target(%i) the scholium=%s" % ( userDBID, targetDBID, scholium ) )
		if len( scholium ) > csdefine.TONG_MEMBER_SCHOLIUM_LENGTH_MAX:
			return

		# 检查userDBID的权限 是否可以设置 targetDBID的权限
		userGrade = self.getMemberInfos( userDBID ).getGrade()
		tscholium = self.getMemberInfos( targetDBID ).getScholium()

		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_MEMBER_SCHOLIUM ):
			return
		elif tscholium == scholium:
			return

		targetBaseMailbox = self.getMemberInfos( targetDBID ).getBaseMailbox()
		if targetBaseMailbox:
			targetBaseMailbox.tong_setScholium( scholium )
		else:
			cmd = "update tbl_Role set sm_tong_scholium=%s where id=%i;" % ( BigWorld.escape_string( scholium ), targetDBID )
			BigWorld.executeRawDatabaseCommand( cmd )

		self.onMemberScholiumChanged( targetDBID, scholium )

	def onMemberScholiumChanged( self, memberDBID, scholium ):
		"""
		某成员的批注改变了
		"""
		oscholium = self.getMemberInfos( memberDBID ).getScholium()
		if scholium == oscholium:
			return

		self.getMemberInfos( memberDBID ).setScholium( scholium )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberScholiumChanged( memberDBID, scholium )    # 更新其他成员的客户端

	#------------------------------------------------------------------------------------------
	def onMemberOnlineStateChanged( self, memberBaseMailbox, memberDBID, onlineState, updataClient = True ):
		"""
		某成员的在线状态改变了
		@param memberBaseMailbox: 如果onlineState为ture 那么就为BaseMailbox否则为none
		@param onlineState		: bool 在线或不在线
		"""
		currentMemberInfo = self.getMemberInfos( memberDBID )
		currentMemberInfo.setOnlineState( onlineState )
		currentMemberInfo.setBaseMailbox( memberBaseMailbox )

		if onlineState:
			try:
				for dbid in self._onlineMemberDBID:
					otherMember = self.getMemberInfos( dbid ).getBaseMailbox()
					memberBaseMailbox.cell.tong_addMemberOL( dbid, otherMember )		 	 		  # 向自己的cell在线成员列表添加所有在线成员
					otherMember.cell.tong_addMemberOL( memberDBID, memberBaseMailbox )	  			  # 向其他成员的cell在线成员列表里添加我
					if updataClient and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
						otherMember.client.tong_onMemberOnlineStateChanged( memberDBID, True ) 	  	  # 更新其他成员的客户端 我的状态为在线
			except:
				pass

			self._onlineMemberDBID.add( memberDBID )
			self.createSendDataTask( memberDBID )
			memberBaseMailbox.cell.tong_onSetTongName( self.playerName )
			TongCampaign.initTongQuestState( self, memberBaseMailbox )
		else:
			self._onlineMemberDBID.remove( memberDBID )
			for dbid in self._onlineMemberDBID:
				otherMember = self.getMemberInfos( dbid ).getBaseMailbox()
				otherMember.cell.tong_onMemberRemoveOL( memberDBID )			 	 	 		   # 告诉其他在线成员我下线了 并从其他人的在线成员列表里删除我
				if updataClient and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
					otherMember.client.tong_onMemberOnlineStateChanged( memberDBID, False )    	   # 更新其他成员的客户端 我的状态为不在线

			# 从异步数据处理中删除
			if self.isInDelayTaskList( memberDBID ):
				self.delDelayTaskMember( memberDBID )

	#------------------------------------------------------------------------------------------
	def onMemberLevelChanged( self, memberDBID, level ):
		"""
		define method.
		某成员的级别改变了
		"""
		olevel = self.getMemberInfos( memberDBID ).getLevel()
		if level == olevel:
			return

		self.getMemberInfos( memberDBID ).setLevel( level )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberLevelChanged( memberDBID, level )   						 # 更新其他成员的客户端
		self.calPrestige()			# 保底声望变化

	#------------------------------------------------------------------------------------------
	def onMemberNameChanged( self, memberDBID, name ):
		"""
		define method.
		某成员的名字改变了
		"""
		oname = self.getMemberInfos( memberDBID ).getName()
		if name == oname:
			return

		self.getMemberInfos( memberDBID ).setName( name )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberNameChanged( memberDBID, name )   						 # 更新其他成员的客户端

	#------------------------------------------------------------------------------------------
	def setAffiche( self, userDBID, affiche ):
		"""
		define method.
		user设置公告, 需权限
		"""
		userInfo = self.getMemberInfos( userDBID )
		userGrade = userInfo.getGrade()

		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_AFFICHE ): # 没有权限
			return
		elif len( affiche ) > csdefine.TONG_AFFICHE_LENGTH_MAX or affiche == self.affiche:			# 字数过长这里直接返回不做报告，应该由客户端那边检测后报告给用户.
			return

		self.affiche = affiche
		self.onTongAfficheChanged()

	def onTongAfficheChanged( self ):
		"""
		define method.
		帮会公告改变了
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_AFFICHE_DATA ):
				self.statusMessage( emb, csstatus.TONG_AFFICHE_CHANGED )
				self.statusMessage( emb, csstatus.TONG_AFFICHE_CHANGED_SHOW, self.affiche )
				emb.client.tong_onSetAffiche( self.affiche )    # 更新其他成员的客户端

	#------------------------------------------------------------------------------------------
	def onMemberContributeChanged( self, memberDBID, contribute ):
		"""
		define method.
		某成员的帮会贡献度改变了
		"""
		ocontribute = self.getMemberInfos( memberDBID ).getContribute()
		if contribute == ocontribute:
			return

		# 记录个人累积帮贡， 降低帮贡我们不进行记录， 只记录增加帮贡
		totalContribute = self.addMemberTotalContributeRecord( memberDBID, contribute - ocontribute )
		self.getMemberInfos( memberDBID ).setContribute( ocontribute + ( contribute - ocontribute ) )
		contribute = self.getMemberInfos( memberDBID ).getContribute()
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberContributeChanged( memberDBID, contribute, totalContribute )    # 更新其他成员的客户端

	#---------------------------------------------------------------------------------------------------------
	def onMemberLogin( self, memberBaseMailbox, memberDBID ):
		"""
		define method.
		成员登陆通知
		"""
		DEBUG_MSG( "playerDBID %i login to tong(%s)." % ( memberDBID, self.playerName ) )
		if not self.hasMember( memberDBID ):		# 该玩家已经不在本帮会
			DEBUG_MSG( "%i is not in tong %i"  % ( memberBaseMailbox.id, self.tid ) )
			memberBaseMailbox.tong_reset()
			return
		
		self.onMemberOnlineStateChanged( memberBaseMailbox, memberDBID, True )
		memberBaseMailbox.tong_onLoginCB( self )

		#帮会公告//
		if self.affiche:
			self.statusMessage( memberBaseMailbox, csstatus.TONG_AFFICHE_SHOW, self.affiche )
		memberBaseMailbox.cell.sendTongFaction( self.factionCount )
		
		if self.tongAbaGatherFlag:
			memberBaseMailbox.client.tongAbaGather( self.tongAbaGatherFlag )
			memberBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
		
		if self.tongAbaRound:
			memberBaseMailbox.client.receiveAbaRound( self.tongAbaRound )

		if self.tongCompetitionGatherFlag:
			memberBaseMailbox.client.tongCompetitionGather()
			memberBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )

		if memberDBID == self.chiefDBID:
			if not self.holdCity: return
			cityName = csconst.g_maps_info.get( self.holdCity )
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_TONG_CHIEFONLINE_NOTIFY % ( self.playerName, cityName, self.chiefName ), [] )

	def onMemberLogout( self, memberDBID ):
		"""
		define method.
		成员下线通知
		"""
		DEBUG_MSG( "playerDBID %i logout of tong(%s)." % ( memberDBID, self.playerName ) )
		self.onMemberOnlineStateChanged( None, memberDBID, False )

	#-----------------------------------------------------------------------------------------------------------
	def hasRequestJoin( self, targetDBID ):
		"""
		该ENTITY是否有被邀请
		"""
		return self._requestJoinEntityList.has_key( targetDBID )

	def getRequestJoinInfo( self, targetDBID ):
		"""
		获取被邀请对象的一些记录
		"""
		return self._requestJoinEntityList[ targetDBID ]

	def removeRequestJoinInfo( self, targetDBID ):
		"""
		删除这个被邀请对象的记录
		"""
		if self.hasRequestJoin( targetDBID ):
			self._requestJoinEntityList.pop( targetDBID )

	def checkRequestJoinTimeOut( self, time ):
		"""
		检查time是否超过最大邀请时间
		"""
		return BigWorld.time() - time > CONST_REQUEST_JOIN_TIMEOUT

	def onAddRequestJoinInfo( self, userDBID, targetBaseMailbox, targetDBID ):
		"""
		添加被邀请人的信息
		@param userDBID			: 本次邀请功能的使用者databaseID
		@param targetBaseMailbox: 本次的被邀请目标baseMailbox
		@param targetDBID		: 本次的被邀请目标的databaseID
		"""
		d = {}
		d["targetBaseMailbox"] 	= targetBaseMailbox
		d["userDBID"]			= userDBID
		d["time"]				= BigWorld.time()
		self._requestJoinEntityList[ targetDBID ] = d

		# 如果没有时钟检测了 那么开启检测过时请求
		if self._check_RequestJoinTimerID <= 0:
			self._check_RequestJoinTimerID = self.addTimer( CONST_REQUEST_JOIN_TIMEOUT, CONST_REQUEST_JOIN_TIMEOUT, TIME_CBID_CHECK_REQUEST_JOIN )

	def onCheckRequestJoinTimer( self ):
		"""
		删除过时的邀请请求
		"""
		rme = []
		for key, info in self._requestJoinEntityList.iteritems():
			if self.checkRequestJoinTimeOut( info[ "time" ] ):
				rme.append( key )

		for key in rme:
			self._requestJoinEntityList.pop( key )

		if len( self._requestJoinEntityList ) <= 0:
			self.delTimer( self._check_RequestJoinTimerID )
			self._check_RequestJoinTimerID = 0

	def getMemberLimit( self ):
		"""
		获得帮会成员人数上限
		"""
		return csconst.TONG_MEMBER_LIMIT_DICT[self.level]

	def checkJoinTongConditions( self, userDBID, targetBaseMailbox, targetDBID ):
		"""
		检查加入这个玩家是否符合条件
		@param userDBID			: 本次邀请功能的使用者databaseID
		@param targetBaseMailbox: 本次的被邀请目标baseMailbox
		@param targetDBID		: 本次的被邀请目标的databaseID
		@param targetLevel		: 本次的被邀请目标的级别
		"""
		userInfo = self.getMemberInfos( userDBID )
		userBaseMailbox = userInfo.getBaseMailbox()
		userGrade = userInfo.getGrade()

		# 检查邀请者的权限
		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_MEMBER_MANAGE ): 
			return csstatus.TONG_GRADE_INVALID 					# 你的权限不够
		elif self.isTongMemberFull():
			return csstatus.TONG_MEMBER_FULL 					# 帮会人数达到上限,在入帮处理列表中也计算帮会成员
		elif userDBID == targetDBID:
			return csstatus.TONG_TARGET_SELF 					# 你不能邀请自己
		elif self.hasRequestJoin( targetDBID ):
			return csstatus.TONG_WAITING_RESPONSE 				# 是否正在被邀请中？请等待对方回应.

		return csstatus.TONG_NORMAL

	def onRequestJoin( self, userDBID, targetBaseMailbox, targetDBID ):
		"""
		define method.
		帮会中有权人士邀请某人加入本帮会
		@param userDBID			: 本次邀请功能的使用者databaseID
		@param targetBaseMailbox: 本次的被邀请目标baseMailbox
		@param targetDBID		: 本次的被邀请目标的databaseID
		@param targetLevel		: 本次的被邀请目标的级别
		"""
		DEBUG_MSG( "onRequestJoin: userDBID=%i, targetDBID=%i" % ( userDBID, targetDBID ) )
		userInfo = self.getMemberInfos( userDBID )
		userBaseMailbox = userInfo.getBaseMailbox()

		# 检查合法后则进行邀请通知
		state = self.checkJoinTongConditions( userDBID, targetBaseMailbox, targetDBID )
		if state != csstatus.TONG_NORMAL:
			self.statusMessage( userBaseMailbox, state )
			return

		self.onAddRequestJoinInfo( userDBID, targetBaseMailbox, targetDBID )
		if hasattr( targetBaseMailbox, "client" ):
			targetBaseMailbox.client.tong_onReceiveRequestJoin( userInfo.getName(), self.databaseID, self.playerName, \
			self.chiefName, self.level, self.memberCount )
		else:
			ERROR_MSG( "target %i:%i no has client."  % ( targetBaseMailbox.id, targetDBID ) )

	def onAnswerRequestJoin( self, targetDBID, agree, targetName ):
		"""
		define method.
		被邀请后 做出回答了
		@param targetDBID		: 本次的被邀请目标的databaseID
		@param agree			: bool, true = 接受
		@param targetName		: 本次的被邀请目标的名字
		"""
		DEBUG_MSG( "playerDBID %i answer to tong %i" % ( targetDBID, self.databaseID ) )
		if not self.hasRequestJoin( targetDBID ):
			DEBUG_MSG( "not of the request! may is the timeout!" ) # 可能超时了 记录已经被系统删除 不做回答
			return

		requestJoinInfo = self.getRequestJoinInfo( targetDBID )
		if requestJoinInfo is None:
			ERROR_MSG( "request info is Error! %i" % targetDBID )
			return

		# 删除这个邀请记录
		self.removeRequestJoinInfo( targetDBID )
		if self.checkRequestJoinTimeOut( requestJoinInfo[ "time" ] ):
			DEBUG_MSG( "request time out." )
			return
		userDBID = requestJoinInfo["userDBID"]
		userBaseMailbox = self.getMemberInfos( userDBID ).getBaseMailbox()
		if not agree:
			self.statusMessage( userBaseMailbox, csstatus.TONG_REJECT_JOIN_TONG, targetName )
			return
		if self.isTongMemberFull():
			self.statusMessage( userBaseMailbox, csstatus.TONG_MEMBER_FULL )
			return
		targetBaseMailbox = requestJoinInfo[ "targetBaseMailbox" ]
		self.addMemberJoinCheck( targetDBID )
		# 从玩家的cell开始处理加帮会流程，防止帮会加入玩家但玩家entity有可能被销毁而设置数据不成功的情况
		targetBaseMailbox.cell.tong_onJoin( self.databaseID, csdefine.TONG_DUTY_MEMBER, csconst.JOIN_TONG_INIT_CONTRIBUTE, self )

	def onJoin( self, mDBID, mName, mLevel, mClass, mBaseMailbox, tongGrade, tongContribute ):
		"""
		Define method.
		玩家入帮信息注册
		"""
		memberInfo = self.createMemberInfo( mDBID, mName, mLevel, mClass, \
							mBaseMailbox, tongGrade, '', tongContribute )
		self.addMember( mDBID, memberInfo )
		memberDBIDList = [mDBID]
		
		
		if self.tongAbaGatherFlag:
			mBaseMailbox.client.tongAbaGather( self.tongAbaGatherFlag )
			mBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
		
		if self.tongAbaRound:
			mBaseMailbox.client.receiveAbaRound( self.tongAbaRound )

		if self.tongCompetitionGatherFlag:
			mBaseMailbox.client.tongCompetitionGather()
			mBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )

		# 更新所有在线成员的客户端的成员列表中加入新成员
		# 由于这里memberDBIDList可能非常的多，因此也来一个异步更新机制
		for dbid in self._onlineMemberDBID:
			if self.isInDelayTaskList( dbid ):
				# 如果该成员正在异步更新中， 那么向该成员的异步处理任务表中加入新加的成员
				self.addMembersToDelayTaskMember( dbid, memberDBIDList )
			else:
				# 该成员当前不在异步更新处理中，那么给他新加一个异步处理任务并通知客户端主动获取数据
				d = {}
				d[ "tasks" ] = [ TASK_KEY_MEMBER_DATA ]
				d[ TASK_KEY_MEMBER_DATA ] = list( memberDBIDList )
				self._delayDataTasks[ dbid ] = d
				otherMember = self.getMemberInfos( dbid ).getBaseMailbox()
				if hasattr( otherMember, "client" ):
					otherMember.client.tong_onReceiveData()	# 由于客户端初始化家族数据是在角色进入游戏后就停止了， 现在需要告诉客户端重新激活一次数据获取的申请.
				self.statusMessage( otherMember, csstatus.TONG_ADD_MEMBER, mName )
		self.onMemberOnlineStateChanged( mBaseMailbox, mDBID, True, False )# 将此人注册到在线成员信息里与注册到其他成员
		if hasattr( mBaseMailbox, "client" ):
			mBaseMailbox.client.tong_onReceiveData() 		# 由于客户端初始化家族数据是在角色进入游戏后就停止了， 现在需要告诉客户端重新激活一次数据获取的申请.
		self.memberJoinSuccess( mDBID )
		self.writeToDB()

	#-----------------------------------------------------------------------------------------------------------
	def onStatusMessage( self, statusID, sargs ) :
		"""
		<defined/>
		接收服务器返回来的状态消息
		@type				statusID : MACRO DEFINATION
		@param				statusID : 状态消息，在 common/csstatus.py 中定义
		@type				sargs	 : STRING
		@param				sargs	 : 消息附加参数
		@return						 : None
		"""
		args = () if sargs == "" else eval( sargs )
		self.statusMessageToOnlineMember( statusID, *args )

	def statusMessage( self, targetBaseMailbox, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = "" if args == () else str( args )
		if hasattr( targetBaseMailbox, "client" ):
			targetBaseMailbox.client.onStatusMessage( statusID, args )

	def statusMessageToOnlineMember( self, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			self.statusMessage( member, statusID, *args )

	def onSendMessage( self, userName, memberDBID, msg ):
		"""
		define method.
		向某成员发送信息
		"""
		info = self.getMemberInfos( memberDBID )
		if not info.isOnline():
			return
		e = info.getBaseMailbox()
		e.chat_handleMessage( csdefine.CHAT_CHANNEL_WHISPER, userName, msg, [] )

	def doAllOnlineMemberClientFunc( self, funcName, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			method = getattr( member.client, funcName )
			method( *args )

	def onSendChatMessageAll( self, memberDBID, msg, playerID, playerName, blobArgs ):
		"""
		Define method.
		发送消息给所有军团成员

		@param msg	: message
		@type  msg	: STRING
		@param playerID : player's id
		@type  playerID : OBJECT_ID
		@param playerName : player's name
		@type  playerName : STRING
		"""
		info = self.getMemberInfos( memberDBID )
		grade = info.getGrade()
		if not self.checkMemberDutyRights( grade, csdefine.TONG_RIGHT_GRADE_CHAT ):
			e = info.getBaseMailbox()
			if hasattr( e, "client" ):
				e.client.onStatusMessage( csstatus.CHAT_TONG_UNPROMISE, "" )
			return

		for dbid in self._onlineMemberDBID:
			info = self.getMemberInfos( dbid )
			grade = info.getGrade()
			if not self.isInDelayTaskList( dbid ) and self.checkMemberDutyRights( grade, csdefine.TONG_RIGHT_GRADE_CHAT ):
				emb = info.getBaseMailbox()
				if hasattr( emb, "client" ):
					emb.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_TONG, playerID, playerName, msg, blobArgs )


	#-----------------------------------------------------------------------------------------------------------
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		TongTerritory.onTimer( self, timerID, cbID )
		TongCampaign.onTimer( self, timerID, cbID )
		TongStorage.onTimer( self, timerID, cbID )

		if self._check_RequestJoinTimerID == timerID:					# 删除过时的邀请请求
			self.onCheckRequestJoinTimer()
		elif self._check_RequestLeagueTimerID == timerID:				# 删除过时的邀请请求
			self.onCheckRequestLeagueTimer()
		elif self._check_conjureTimerID == timerID:						# 集结令
			self.onCheckConjureTimer()
		elif self._check_payChiefMoney_timerID == timerID:				# 检查帮主工资发放情况
			self.checkPayChiefMoney()
		elif self._startupTimerID == timerID:
			self.onTongStartup()
			self._startupTimerID = 0
		elif self._afterFeteTimerID == timerID:
			self.__unapplyStatusAfterFete()						# 撤销帮会祭祀后获得的状态
			self._afterFeteTimerID = 0
		elif self.tempDataCheckTimer == timerID:
			self.onTempDataCheckTimerCheck()
		elif timerID == self.destroyTimerID:
			del BigWorld.globalData[ "tong.%i" % self.databaseID ]
			self.destroy( deleteFromDB = True, writeToDB = True )
		elif self._check_inviteBattleLeagueTimerID == timerID:			# 删除过时的战争结盟邀请请求
			self.onCheckRequestBattleLeagueTimer()

	#-----------------------------------------------------------------------------------------------------------
	def checkQuitLeagueLog( self ):
		"""
		检测过期的帮会禁止同盟记录
		"""
		dels = []
		for idx, info in enumerate( self.quitLeagueLog ):
			if time.time() >= info[ "timeout" ]:
				dels.append( idx )

		dels.reverse()
		for d in dels:
			self.quitLeagueLog.pop( d )

	def checkRequestLeagueTimeOut( self, time ):
		"""
		检查time是否超过最大邀请时间
		"""
		return BigWorld.time() - time > CONST_REQUEST_JOIN_TIMEOUT

	def onRequestTongLeague( self, userDBID, requestTongDBID, requestTongName ):
		"""
		define method.
		本帮会将邀请帮会同盟
		@param user				:使用功能者baseMailbox
		@param userTongName		:使用功能者 帮会的名称
		@param userTongDBID		:使用功能者 帮会的DBID
		"""
		DEBUG_MSG( "%i request tong %s to league." % ( userDBID, requestTongName ) )
		user = self.getMemberInfos( userDBID ).getBaseMailbox()

		if requestTongDBID <= 0 :
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_NO_FIND )
			return

		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( user, csstatus.TONG_TONG_LEAGUE_FULL )
			return

		if self._requestLeagueRecord.has_key( requestTongDBID ):
			self.statusMessage( user, csstatus.TONG_WAITING_RESPONSE )
			return
		else:
			self.checkQuitLeagueLog()
			for item in self.quitLeagueLog:
				if requestTongDBID == item[ "tongDBID" ]:
					#未到一个星期 不允许再同盟
					self.statusMessage( user, csstatus.TONG_INVALID_NO_TIMEOUT )
					return

		d = {}
		d["userDBID"] = userDBID
		d["requestTongName" ] = requestTongName
		d[ "time" ] = BigWorld.time()
		self._requestLeagueRecord[ requestTongDBID ] = d

		if self.checkMemberDutyRights( self.getMemberInfos( userDBID ).getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			self.getTongManager().requestTongLeague( user, self.databaseID, requestTongName )
		else:
			self.statusMessage( user, csstatus.TONG_GRADE_INVALID )

		# 如果没有时钟检测了 那么开启检测过时请求
		if self._check_RequestLeagueTimerID <= 0:
			self._check_RequestLeagueTimerID = self.addTimer( CONST_REQUEST_JOIN_TIMEOUT, CONST_REQUEST_JOIN_TIMEOUT, TIME_CBID_CHECK_REQUEST_JOIN )

	def onCheckRequestLeagueTimer( self ):
		"""
		删除过时的邀请请求
		"""
		rme = []
		for key, info in self._requestLeagueRecord.iteritems():
			if self.checkRequestLeagueTimeOut( info[ "time" ] ):
				rme.append( key )

		for key in rme:
			self._requestLeagueRecord.pop( key )

		if len( self._requestLeagueRecord ) <= 0:
			self.delTimer( self._check_RequestLeagueTimerID )
			self._check_RequestLeagueTimerID = 0

	def requestTongLeague( self, user, userTongName, userTongDBID ):
		"""
		define method.
		邀请帮会同盟
		@param user				:使用功能者baseMailbox
		@param userTongName		:使用功能者 帮会的名称
		@param userTongDBID		:使用功能者 帮会的DBID
		"""
		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_LEAGUE_FULL )
			self.getTongManager().onRequestTongLeagueFailed( userTongDBID, self.databaseID )
			return

		self.checkQuitLeagueLog()
		for dbid, info in self._memberInfos.iteritems():
			if self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
				if info.isOnline():
					info.getBaseMailbox().client.tong_onRequestTongLeague( userTongName, userTongDBID )
					return

		self.statusMessage( user, csstatus.TONG_TARGET_TONG_CHIEF_OFFLINE )
		self.getTongManager().onRequestTongLeagueFailed( userTongDBID, self.databaseID )

	def onRequestTongLeagueFailed( self, targetTongDBID ):
		"""
		define method.
		邀请同盟在对方帮会entity中失败了（可能是帮主不在线）做个回调
		"""
		self._requestLeagueRecord.pop( targetTongDBID )

	def onAnswerRequestTongLeague( self, answerRoleBaseEntity, requestTongDBID, agree ):
		"""
		define method.
		本帮会将回答邀请方是否愿意加入同盟。
		"""
		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( answerRoleBaseEntity, csstatus.TONG_TONG_LEAGUE_FULL )
			self.getTongManager().onRequestTongLeagueFailed( requestTongDBID, self.databaseID )
			return

		self.getTongManager().answerRequestTongLeague( answerRoleBaseEntity, self.databaseID, agree, requestTongDBID )

	def answerRequestTongLeague( self, answerRoleBaseEntity, requestTong, requestTongDBID, agree ):
		"""
		define method.
		收到对方回答是否愿意加入同盟。
		"""
		DEBUG_MSG( "%i answer tong %i to league." % ( requestTongDBID, self.databaseID ) )
		info = self._requestLeagueRecord[ requestTongDBID ]
		user = self.getMemberInfos( info[ "userDBID" ] ).getBaseMailbox()
		requestTongName = info["requestTongName" ]
		del self._requestLeagueRecord[ requestTongDBID ]

		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( answerRoleBaseEntity, csstatus.TONG_TARGET_TONG_LEAGUE_FULL )
			return

		# 超时了 返回
		if self.checkRequestLeagueTimeOut( info[ "time" ] ):
			return

		if not agree:
			if user:
				self.statusMessage( user, csstatus.TONG_LEAGUE_FAIL, requestTongName )
			return

		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_ALIGNMENT_NOTIFY % ( requestTongName, self.playerName ), [] )
		requestTong.onTongLeague( self.databaseID, self.playerName )
		self.onTongLeagueNotify( requestTongDBID, requestTongName )

	def onTongLeague( self, leagueTongDBID, leagueTongName ):
		"""
		define method.
		收到对方帮会与我同盟
		"""
		if not self.hasLeagueTong( leagueTongDBID ):
			self.onTongLeagueNotify( leagueTongDBID, leagueTongName )
		else:
			ERROR_MSG( "league %s %i is exist." % ( leagueTongName, leagueTongDBID ) )

	def onTongLeagueNotify( self, tongDBID, tongName ):
		"""
		双方结为同盟的通报
		"""
		self.leagues.append( { "dbID" : tongDBID, "tongName" : tongName, "tid" : 0, "ad" : "" } )
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			if not self.isInDelayTaskList( dbid ):
				member.client.tong_addLeague( tongDBID, tongName )
			else:
				self.addLeagueToDelayTaskMember( dbid, tongDBID, tongName )

		# 将数据更新到管理器
		self.getTongManager().updateTongLeagues( self.databaseID, self.leagues )

	def leagueDispose( self, memberDBID, leagueTongDBID ):
		"""
		define method.
		解除联盟关系
		"""
		if memberDBID != -1:	#-1 由系统调用 主要原因是另一个帮会解散了
			if not self.checkMemberDutyRights( self.getMemberInfos( memberDBID ).getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ): # 权限检查
				return

		self.onTongLeagueDisposeNotify( leagueTongDBID, True )

	def onLeagueDispose( self, leagueTongDBID ):
		"""
		define method.
		收到对方帮会与我脱离了同盟关系
		"""
		self.onTongLeagueDisposeNotify( leagueTongDBID, False )

	def onTongLeagueDisposeNotify( self, tongDBID, initiative ):
		"""
		双方解除了同盟的通报
		"""
		msgKey = csstatus.TONG_LEAGUE_QUIT_TO
		if not initiative:
			msgKey = csstatus.TONG_LEAGUE_QUIT

		for idx, item in enumerate( self.leagues ):
			if item[ "dbID" ] == tongDBID:
				self.leagues.pop( idx )
				d = { "tongDBID" : tongDBID, "timeout" : int( time.time() + 60 * 60 * 24 * 7 ) }
				self.quitLeagueLog.append( d )

				if initiative:
					self.getTongManager().onLeagueDispose( tongDBID, self.databaseID )

				for dbid in self._onlineMemberDBID:
					member = self.getMemberInfos( dbid ).getBaseMailbox()
					self.statusMessage( member, msgKey, item[ "tongName" ] )

					if not self.isInDelayTaskMember_LeaguesList( dbid, tongDBID ):
						member.client.tong_delLeague( tongDBID )
					else:
						self.delLeagueInDelayTaskMember( dbid, tongDBID, item[ "tongName" ] )
				break

	def hasLeagueTong( self, leagueTongDBID ):
		"""
		是否有该同盟帮会
		"""
		for t in self.leagues:
			if t[ "dbID" ] == leagueTongDBID:
				return True

		return False

	#-----------------------------------------------------------------------------------------------------------
	def requestMemberMapInfo( self, baseEntity, userDBID ):
		"""
		define method.
		客户端请求获取成员所在地图信息
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.cell.tong_onMemberRequestMapInfo( baseEntity )

	#-----------------------------------------------------------------------------------------------------------
	def onAbdication( self, userDBID, memberDBID ):
		"""
		define method.
		帮主让位
		"""
		if not self.hasMember( userDBID ) or not self.hasMember( memberDBID ):
			return

		userInfo = self.getMemberInfos( userDBID )
		userGrade = userInfo.getGrade()
		if userGrade != csdefine.TONG_DUTY_CHIEF:
			return
		DEBUG_MSG( "userDBID=%i grade=%i, memberDBID=%i" % ( userDBID, userGrade, memberDBID ) )
		memberInfo = self.getMemberInfos( memberDBID )
		memberInfo.setGrade( csdefine.TONG_DUTY_CHIEF )
		userInfo.setGrade( csdefine.TONG_DUTY_MEMBER )
		self.chiefDBID = memberDBID
		self.chiefName = memberInfo.getName()

		# 既然是帮主让位,那么可以认定帮主的BaseMailbox存在.
		userMB = userInfo.getBaseMailbox()
		userMB.tong_setGrade( csdefine.TONG_DUTY_MEMBER )
		self.statusMessage( userMB, csstatus.TONG_CHANGE_CHIEF_TO, self.chiefName )
		self.addChangeGradeChek( userDBID, csdefine.TONG_DUTY_MEMBER )
		# 对于接受帮主位子的玩家，要根据其在不在线分别处理
		emb = memberInfo.getBaseMailbox()

		if emb:
			self.addChangeGradeChek( userDBID, csdefine.TONG_DUTY_CHIEF )
			emb.tong_setGrade( csdefine.TONG_DUTY_CHIEF )
			emb.cell.sendTongFaction( self.factionCount )
			self.statusMessage( emb, csstatus.TONG_CHANGE_CHIEF_FROM, self.playerName )
		else:
			self.updateGrade2DB( memberDBID, csdefine.TONG_DUTY_CHIEF )
			content = cschannel_msgs.TONG_INFO_26 % self.playerName
			self.getMailMgr().send( None, self.chiefName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
					cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_25, content, 0, "" )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onAbdication( userDBID, memberDBID )    # 更新其他成员的客户端

		# 保存新帮主就职时间, 主要是提供给工资发放使用
		self.saveChiefdate = int( time.time() )
		try:
			g_logger.tongLeaderChangeLog( self.databaseID, self.getName(), userDBID, userInfo.getName(), 0 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

		# 将数据更新到管理器
		self.getTongManager().updateTongChiefName( self.databaseID, self.chiefName )
		self.save()
		self.statusMessageToOnlineMember( csstatus.TONG_CHIEF_ABDCATION, userInfo.getName(), memberInfo.getName(), self.playerName )

	def updateGrade2DB( self, memberDBID, grade ):
		"""
		玩家不在线，更新玩家帮会权限到db
		"""
		cmd = "update tbl_Role set sm_tong_grade=%i where id=%i;" % ( grade, memberDBID )
		BigWorld.executeRawDatabaseCommand( cmd )

	def setDutyName( self, userDBID, duty, newName ):
		"""
		define method.
		设置某职位的名称
		"""
		if len( newName ) <= 0 or not self.hasMember( userDBID ) or self.getMemberInfos( userDBID ).getGrade() != csdefine.TONG_DUTY_CHIEF:
			return

		if duty not in csdefine.TONG_DUTYS:
			return
		
		# 如果有相同的名称则不允许设置
		for item in self.dutyNames:
			if newName == item[ "dutyName" ]:
				return

		# 设置新名字
		for item in self.dutyNames:
			if item[ "duty" ] == duty:
				INFO_MSG( "TONG:( %i, %s ) set duty %s's name which is %s to %s" % ( userDBID, self.getMemberInfos( userDBID ).getName(), duty, item["dutyName"], newName ) )
				item[ "dutyName" ] = newName
				self.onDutyNameChanged( duty, newName )
				return

	def onDutyNameChanged( self, duty, newName ):
		"""
		某职位名称已经改变
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if hasattr( emb, "client" ) and not self.hasDelayTaskData( dbid, TASK_KEY_DUTY_NAMES_DATA ):
				emb.client.tong_onDutyNameChanged( duty, newName )    # 更新其他成员的客户端

	def sendDailogByTongDutyName( self, duty, dailog, NPC_id, playerMB ):
		"""
		Define method
		根据帮会自定义名称来组织NPC对话内容
		纯蛋疼
		"""
		for dn in self.dutyNames:
			dutyID, dutyName = dn.values()
			if dutyID == duty:
				playerMB.client.onSetGossipText( dailog%(dutyName) )
				playerMB.client.onGossipComplete( NPC_id )
				break
	#-----------------------------------------------------------------------------------------------------------
	def checkCommandValid_conjure( self, memberDBID ):
		"""
		检查族长是否对该成员使用了命令 以及是否仍然生效
		"""
		if self._chiefCommandInfo.has_key( "conjure" ) and memberDBID in self._chiefCommandInfo[ "conjure" ][ "members" ]:
			return True
		return False

	def chiefCommand_conjure( self, userDBID, lineNumber, mapName, position ):
		"""
		define mothod.
		帮主令 传送所有队员到帮主身边
		"""
		# 如果没有一个队员在线 那还招什么?
		if len( self._onlineMemberDBID ) < 2:
			return

		userInfo = self.getMemberInfos( userDBID )
		user = userInfo.getBaseMailbox()
		self._chiefCommandInfo[ "conjure" ] = {}

		if self._check_conjureTimerID > 0:
			self.delTimer( self._check_conjureTimerID )

		self._check_conjureTimerID = self.addTimer( CONST_CHIEF_CONJURE_TIMEOUT, 0, 1 )
		if not user or not self.checkMemberDutyRights( userInfo.getGrade(), csdefine.TONG_RIGHT_CALL_ALL_MEMBER ):
			return

		self._chiefCommandInfo[ "conjure" ][ "members" ] 	= list( self._onlineMemberDBID )
		self._chiefCommandInfo[ "conjure" ][ "mapName" ] 	= mapName
		self._chiefCommandInfo[ "conjure" ][ "position" ] 	= position
		self._chiefCommandInfo[ "conjure" ][ "lineNumber" ] = lineNumber

		for dbid in self._onlineMemberDBID:
			if userDBID != dbid:
				self.getMemberInfos( dbid ).getBaseMailbox().client.tong_onChiefConjure()

	def onCheckConjureTimer( self ):
		"""
		"""
		if self._chiefCommandInfo.has_key( "conjure" ):
			del self._chiefCommandInfo[ "conjure" ]
		self._check_conjureTimerID = 0

	def onAnswer_conjure( self, memberDBID ):
		"""
		define mothod.
		队员回应集结令
		"""
		if not self.checkCommandValid_conjure( memberDBID ):
			return

		info = self._chiefCommandInfo[ "conjure" ]
		info[ "members" ].remove( memberDBID )
		emb = self.getMemberInfos( memberDBID ).getBaseMailbox()

		if emb:
			mapName = info[ "mapName" ]
			position = info[ "position" ]
			lineNumber = info[ "lineNumber" ]
			emb.cell.gotoSpaceLineNumber( mapName, lineNumber, position, ( 0, 0, 0 ) )
		else:
			DEBUG_MSG( "not found member %i" % memberDBID )

	#-----------------------------------------------------------------------------------------------------------
	def checkPayChiefMoney( self ):
		"""
		检查帮会支付帮主和副帮主工资情况
		"""
		tinfo = time.localtime()
		# 计算今天是否是星期天
		if tinfo[6] == 6:
			if not self.querySunday:
				chiefWage = 0
				adjutantChiefWages = []

				# 计算出帮主的工资
				if len( self.chiefName ) > 0:
					remainTime = int( time.time() - self.saveChiefdate )
					day = remainTime / ( 24 * 60 * 60 )
					chiefWage = int( Const.TONG_CHIEF_WAGE[ "chief" ][ self.level ] * min( 7.0, day ) )
						
				# 获取副帮主们的工资
				for memberDBID, info in self._memberInfos.items():
					if info.getGrade() != csdefine.TONG_DUTY_DEPUTY_CHIEF:
						continue
					for recordTime in self.saveAdjutantChiefdate:
						if recordTime[ "dbID" ] == memberDBID:
							remainTime = int( time.time() - recordTime[ "time" ] )
							day = remainTime / ( 24 * 60 * 60 )
							wage = int( Const.TONG_CHIEF_WAGE[ "adjutantChief" ][ self.level ] * min( 7.0, day ) )
							wageInfo = ( info.getName(), wage )
							adjutantChiefWages.append( wageInfo )
							break
						
				# 计算工资总额
				totalWage = chiefWage
				for wageInfo in adjutantChiefWages:
					totalWage += wageInfo[1]
				
				# 可用资金不足则取消本次发放 CSOL-2364
				if totalWage > self.getValidMoney():
					INFO_MSG( "Tong[%s : %s] valid money is not enough for wage!" % ( self.databaseID, self.getName() ) )
				else:
					# 发帮主工资
					if chiefWage >= 1:
						self.payMoney( chiefWage, True, csdefine.TONG_CHANGE_MONEY_PAYFIRSTCHIEF )
						self.getMailMgr().send( None, self.chiefName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
								cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_4, cschannel_msgs.TONG_INFO_5, chiefWage, "" )
						g_logger.tongWageLog( self.databaseID, self.getName(), self.chiefName, csdefine.TONG_DUTY_CHIEF, chiefWage )
						
					# 发副帮主工资
					for wageInfo in adjutantChiefWages:
						if wageInfo[1] > 1:
							self.payMoney( wageInfo[1], True, csdefine.TONG_CHANGE_MONEY_PAYSECONDCHIEF )
							self.getMailMgr().send( None, wageInfo[0], csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
									cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_6, cschannel_msgs.TONG_INFO_7, wageInfo[1], "" )
							g_logger.tongWageLog( self.databaseID, self.getName(), wageInfo[0], csdefine.TONG_DUTY_DEPUTY_CHIEF, wageInfo[1] )
				
				# 今天已经发过了 做个标记
				self.querySunday = True
		else:
			self.querySunday = False

	def queryTongInfo( self, queryer, args ):
		"""
		"""
		infos = {
					cschannel_msgs.GMMGR_JIN_QIAN 		: 	self.money,
					cschannel_msgs.TONG_INFO_9	:	self.level,
					cschannel_msgs.TONG_INFO_11	:	self.prestige,
					 }

		if not args in infos:
			queryer.client.onStatusMessage( csstatus.TONG_NO_THIS_INFO_SUPPORT, "" )
			queryer.client.onStatusMessage( csstatus.TONG_INFO_SELECT, "" )
			return

		queryer.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, ( args + ":" + str(infos[args]), ) )
	
	#------------------------------------帮会物品-----------------------------------------------------------------------

	def initTongItems( self, reset = False ):
		"""
		初始化帮会物品,reset为0表示初始化，为1表示重置
		"""
		TongTerritory.onInitTongItems( self, reset )
		
		self.items = []
		itemDatas = g_tongItems.getDatas()

		for itemID, item in itemDatas.iteritems():
			# 防止超过物品最大级别
			if self.sd_level >= item[ "repBuildingLevel" ]:
				itemData = { "itemID":itemID, "amount":item["amount"]}
				self.items.append( itemData )
		
		self.items.sort( key = lambda item : item["itemID"], reverse = False )

	def resetTongItems( self ):
		"""
		define method
		重置帮会物品，商品数据暂时沿用物品研发数据
		"""
		self.initTongItems( 1 )

	def removeBuyTongItemRecord( self, dbid ):
		"""
		移除玩家购买帮会物品记录
		"""
		for record in self.weekMemberBuyItemRecord:
			if record[ "dbID" ] == dbid:
				self.weekMemberBuyItemRecord.remove( record )

	def resetMemberBuyItemRecord( self ):
		"""
		define method
		重置帮众购买物品记录
		"""
		self.weekMemberBuyItemRecord = []
	
	def removeChiefBuyTongSpecItemRecord( self, dbid ):
		"""
		移除帮主分配特殊商品记录
		"""
		for record in self.chiefBuySpecItemForMemberRecord:
			if record[ "dbID" ] == dbid:
				self.chiefBuySpecItemForMemberRecord.remove( record )

	def resetChiefBuyTongSpecItemRecord( self ):
		"""
		define method
		重置移除帮主分配特殊商品记录
		"""
		self.chiefBuySpecItemForMemberRecord = []
	
	#--------------------------------------------修理装备-------------------------------------------------------
	def requestRepairOneEquip( self, repairType, kitBagID, orderID, memberDBID ):
		"""
		define method.
		帮会成员要求修理装备
		"""
		if not memberDBID in self._onlineMemberDBID:
			return

		member = self.getMemberInfos( memberDBID ).getBaseMailbox()
		member.cell.tong_onRepairOneEquipBaseCB( repairType, kitBagID, orderID, csconst.TONG_TJP_REBATE[ self.tjp_level ] )

	def requestRepairAllEquip( self, repairType, memberDBID ):
		"""
		define method.
		帮会成员要求修理装备
		"""
		if not memberDBID in self._onlineMemberDBID:
			return

		member = self.getMemberInfos( memberDBID ).getBaseMailbox()
		member.cell.tong_requestRepairAllEquipBaseCB( repairType, csconst.TONG_TJP_REBATE[ self.tjp_level ] )

	#---------------------------------------------客户端打开帮会界面所需求情的数据-----------------------------------
	def onClientOpenTongWindow( self, playerBase ):
		"""
		define method.
		客户端打开了帮会界面， 所需请求数据
		"""
		playerBase.client.tong_onSetAfterFeteStatus( self._afterFeteStatus )

		playerBase.tong_requestSignInRecord()		# 请求帮会签到数据

		self.calBasePrestige()
		playerBase.client.tong_onSetVariablePrestige( self.prestige - self.basePrestige ) # 将额外声望传送到客户端( CSOL-9992 )

	def isTongMemberFull( self ):
		"""
		玩家成员数是否达到上限
		"""
		return len( self._memberInfos ) + len( self.joinMemberTempInfo ) >= self.getMemberLimit()

	#--------------------------------------玩家在帮会列表界面上申请加入帮会相关工作-----------------------------------
	def requestJoinToTong( self, playerBase, playerDBID, playerName, playerCamp ):
		"""
		define method.
		申请加入到某个帮会
		"""
		if self.isTongMemberFull():	# 帮会人数达到上限
			self.statusMessage( playerBase, csstatus.TONG_MEMBER_FULL )
			return
		
		if playerCamp != self.getCamp():
			self.statusMessage( playerBase, csstatus.TONG_CAMP_DIFFERENT )
			return 
			
		if self.chiefDBID in self._onlineMemberDBID:
			userInfo = self.getMemberInfos( self.chiefDBID )
			userInfo.getBaseMailbox().client.tong_onReceiveiJoinInfo( playerDBID, playerName )
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_JOIN_SEND_SUCCESS )
			self.onAddRequestJoinInfo( self.chiefDBID, playerBase, playerDBID )
		else:
			self.statusMessage( playerBase, csstatus.TONG_JOINGRADE_MEMBER_OFFLINE )

	def answerJoinToTong( self, targetDBID, agree ):
		"""
		define method.
		接受玩家加入到某个帮会
		"""
		requestJoinInfo = self.getRequestJoinInfo( targetDBID )
		if requestJoinInfo is None:
			ERROR_MSG( "request info is Error! %i" % targetDBID )
			return
		self.removeRequestJoinInfo( targetDBID )		# 删除这个邀请记录
		if self.checkRequestJoinTimeOut( requestJoinInfo[ "time" ] ):
			return

		userDBID = requestJoinInfo["userDBID"]
		targetBaseMailbox = requestJoinInfo[ "targetBaseMailbox" ]
		if not agree:
			self.statusMessage( targetBaseMailbox, csstatus.TONG_REQUEST_JOIN_NO_ACCEPT )
			return
		userBaseMailbox = self.getMemberInfos( userDBID ).getBaseMailbox()
		if self.isTongMemberFull():
			self.statusMessage( userBaseMailbox, csstatus.TONG_MEMBER_FULL )
			return

		self.addMemberJoinCheck( targetDBID )
		# 从玩家的cell开始处理加帮会流程，防止帮会加入玩家但玩家entity有可能被销毁而设置数据不成功的情况
		targetBaseMailbox.cell.tong_onJoin( self.databaseID, csdefine.TONG_DUTY_MEMBER, csconst.JOIN_TONG_INIT_CONTRIBUTE, self )

	#----------------------------------------------帮会祭祀活动------------------------------------------------------
	def requestFete( self, playerBase ):
		"""
		define method.
		申请帮会祭祀活动
		"""
		if self.getValidMoney() < csconst.TONG_FETE_REQUEST_MONEY:
			playerBase.client.onStatusMessage( csstatus.TONG_OPEN_ACT_MONEY_LACK, "" )
			return
		self.onRequestFeteSuccessfully( playerBase )

	def onRequestFeteSuccessfully( self, playerBase ):
		"""
		申请帮会祭祀成功
		"""
		TongTerritory.onRequestFeteSuccessfully( self )
		self.getTongManager().onRequestFeteSuccessfully( self.databaseID )
		self.statusMessageToOnlineMember( csstatus.TONG_FETE_START )
		self.payMoney( csconst.TONG_FETE_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_REQUEST_FETE  )

		for dbid in self._onlineMemberDBID:
			self.initMemberFeteData( dbid, 0 )
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_JISHI_QUEST, csdefine.ACTIVITY_JOIN_TONG, self.databaseID, self.getName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def initMemberFeteData( self, memberDBID, value ):
		"""
		define method.
		初始化某成员的祭祀活动数据
		@param value: 当前供奉值
		"""
		member = self.getMemberInfos( memberDBID ).getBaseMailbox()
		if member and hasattr( member, "client" ):
			member.client.tong_setFeteData( value )

	def onUpdateFeteData( self, val ):
		"""
		define method.
		更新帮会成员的祭祀活动数据
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			if member and hasattr( member, "client" ):
				member.client.tong_setFeteData( val )

	def onFeteComplete( self ):
		"""
		define method.
		帮会祭祀活动成功完成了
		"""
		TongTerritory.onFeteComplete( self )
		self.addExp( csconst.TONG_EXP_REWARD_FETE, csdefine.TONG_CHANGE_EXP_FETE )
		self.statusMessageToOnlineMember( csstatus.TONG_FETE_COMPLETE )

		# 随机获取：星辉甘露、月晕甘露、日光甘露 状态之一
		self._afterFeteStatus = self.__choseStatusAfterFete()
		# 根据所获得的状态倍增相应的指标
		self.__applyStatusAfterFete( self._afterFeteStatus )
		# 设定一个定时器在指定时间后取消这个状态
		self.__setupRestoreTimerAfterFete( self._afterFeteStatus )
		# 将已经获得的状态写入，防止服务器强行重启后丢失相关状态
		self.writeToDB()

	def __initAfterFeteStatus( self ):
		"""
		根据帮会祭祀完毕后的状态初始化帮会多种指标的增益速度
		"""
		# 状态： NONE_STATUS,LUNARHALO,SUNSHINE,STARLIGHT

		##服务器重启，恢复帮会祭祀后获得的状态
		##注意，整个状态的恢复和计算都假设服务器时间是正确的
		restoreTimeInSec = None
		if self._afterFeteStatusRestoreTime == "":
			self.__unapplyStatusAfterFete()
			return
		try:
			stTime = time.strptime( self._afterFeteStatusRestoreTime, "%Y %m %d %H %M %S" )
			restoreTimeInSec = time.mktime( stTime )
		except:
			# 如果没有成功获取服务器上保存的恢复时间，直接撤销所有状态
			self.__unapplyStatusAfterFete()
			ERROR_MSG( "Can't load restore time of status gained after fete! All status reset!" )
			return

		if not self._afterFeteStatus:
			ERROR_MSG( "Data inconsistent, reset and ignored!" )
			self.__unapplyStatusAfterFete()
			return

		currentTimeInSec = time.time()
		# if 恢复时间没有到
		if restoreTimeInSec > currentTimeInSec:
			# 重新应用状态
			self.__applyStatusAfterFete( self._afterFeteStatus )
			# 重新设定状态复原定时器
			self._afterFeteTimerID = self.addTimer( restoreTimeInSec - currentTimeInSec, 0, 0 )
		# else
		else:
			# 重置状态
			self.__unapplyStatusAfterFete()


	def __choseStatusAfterFete( self ):
		"""
		@choseStatusAfterFete: 在帮会祭祀活动完成之后，随机选择星辉甘露、月晕甘露、日光甘露 状态之一（CSOL-9750）
		@return: 所选择的状态
		"""
		return random.choice( csconst.FETE_COMPLETE_STATUS )

	def __applyStatusAfterFete( self, status ):
		"""
		@applyStatusAfterFete: 在帮会祭祀活动完成之后，根据所获得的状态倍增相应的指标
		"""
		return


	def __setupRestoreTimerAfterFete( self, status ):
		"""
		@setupRestoreTimerAfterFete： 设定一个定时器，撤销帮会祭祀之后获得的状态
		"""
		## 获取从现在开始到下周周六晚24点的秒数
		tm = time.localtime()
		year = tm[0]
		month = tm[1]
		day = tm[2]
		weekDay = tm[6] # 0 表示周一

		daysToSun = 6 - weekDay

		# 下周日零点的时间
		timeString = "%s %s %s %s %s %s"%( year, month, day + daysToSun, 0, 0, 0 )
		restoreTime = time.strptime( timeString, "%Y %m %d %H %M %S" )

		secToNextSat = time.mktime( restoreTime ) - time.time() # 从现在开始到周日0点的秒数

		# 将复原时间按字符串的形式保存
		self._afterFeteStatusRestoreTime = timeString


		# 设定恢复定时器
		self._afterFeteTimerID = self.addTimer( secToNextSat, 0, 0 )

	def __unapplyStatusAfterFete( self ):
		"""
		@unapplyStatusAfterFete: 撤销帮会祭祀完成后获得的状态
		"""
		self._afterFeteStatus = NONE_STATUS
		self._afterFeteStatusRestoreTime = ""

		# 写入数据库，防止服务器强行重启后丢失相关状态
		self.writeToDB()

	def onOverFete( self ):
		"""
		define method.
		帮会祭祀活动结束了  时间到了
		"""
		TongTerritory.onOverFete( self )
		self.statusMessageToOnlineMember( csstatus.TONG_FETE_OVER )

	#-----------------------------------------------------------------------------------------------------------
	"""#########################################################################################################
			以下接口为异步数据处理相关接口， 主要用于异步更新客户端数据
			设计思想: 任务，与数据缓冲.
					 一个需要异步处理的玩家 客户端会主动向服务器请求获取数据，服务器按照这个玩家
					 的异步处理任务列表决定每次请求所给出的数据， 如果数据为空了，则清除这个任务
					 开始下一个任务的数据处理， 在这个过程中，可能新加入成员或者删除， 成员数据改变
					 这些都需要及时的处理数据缓冲的改变
	"""#########################################################################################################
	#----------------------------------------------------------------------------------------------------------
	def requestDelayDatas( self, delayTaskMemberDBID, delayTaskMemberBaseMailbox ):
		"""
		define method.
		客户端主动向服务器请求获得异步数据处理的数据
		"""
		if len( self._delayDataTasks ) <= 0:
			return

		# 如果该成员不在异步处理队列中则忽略
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return

		# 如果帮会中没有该成员数据则清理他的异步处理队列
		if not self._memberInfos.has_key( delayTaskMemberDBID ):
			self._delayDataTasks.pop( delayTaskMemberDBID )
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return

		# 向客户端异步发送成员数据
		datas = self._delayDataTasks[ delayTaskMemberDBID ]
		memberBaseMailbox = self.getMemberInfos( delayTaskMemberDBID ).getBaseMailbox()
		# 如果找不到该成员的mailbox则忽略 且做相关清理
		if not memberBaseMailbox:
			self._delayDataTasks.pop( delayTaskMemberDBID )
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return

		# 如果该成员的异步处理表队列中的任务已经全部完成 那么可以清理该成员在异步处理队列的所有数据
		if len( datas[ "tasks" ] ) <= 0:
			self._delayDataTasks.pop( delayTaskMemberDBID )
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return
		else:
			key = datas[ "tasks" ][ 0 ]
			if not self.onSendClientDelayDatas( key, memberBaseMailbox, datas ):
				self._delayDataTasks.pop( delayTaskMemberDBID )
				delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()

	def onSendClientDelayDatas( self, key, memberBaseMailbox, datas ):
		"""
		发送数据到客户端 主要是异步发送一些帮会的信息
		@param key				: TASK_KEY_*** 定义的一些帮会任务关键字
		@param memberBaseMailbox: 该玩家的mailbox
		@param datas			:任务数据池
		@return type: 成功发送一个任务返回True 否则返回false
		"""
		DEBUG_MSG( "[%i]key:%s, currentDatas:%s, delayDataTasks:%s" % ( memberBaseMailbox.id, key, datas, self._delayDataTasks ) )
		if TongTerritory.onSendClientDelayDatas( self, key, memberBaseMailbox, datas ):
			return True

		if key == TASK_KEY_MEMBER_DATA:				# 异步数据处理  处理成员数据
			ls = datas[ TASK_KEY_MEMBER_DATA ]
			if len(ls) > 0:
				otherMemberDBID = ls.pop( 0 )
				item = self.getMemberInfos( otherMemberDBID )
				memberBaseMailbox.client.tong_onSetMemberInfo( otherMemberDBID, \
				item.getName(), item.getLevel(), item.getClass(), item.getGrade(), item.getScholium(), item.getContribute(), \
				item.getTotalContribute(), item.isOnline() )
			else:
				ERROR_MSG( "tongDebug:this tong[%i-%i] without member!" % (self.id, self.databaseID) )

			if len( ls ) <= 0:
				datas[ "tasks" ].pop( 0 )
			return True
		elif key == TASK_KEY_PERSTIGE_DATA:				# 异步数据处理  处理声望数据
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongPrestige( self.prestige )
			return True
		elif key == TASK_KEY_AFFICHE_DATA:				# 异步数据处理  处理公告数据
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetAffiche( self.affiche )
			return True
		elif key == TASK_KEY_MONEY_DATA:				# 异步数据处理  处理金钱数据
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongMoney( self.money )
			return True
		elif key == TASK_KEY_LEVEL_DATA:				# 异步数据处理  处理级别数据
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.cell.tong_onSetTongLevel( self.level )
			return True
		elif key == TASK_KEY_LEAGUES_DATA:
			ls = datas[ TASK_KEY_LEAGUES_DATA ]
			d = ls.pop( 0 )
			if len( ls ) <= 0:
				datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_setLeague( d[0], d[1] )
			return True
		elif key == TASK_KEY_DUTY_NAMES_DATA:
			datas[ "tasks" ].pop( 0 )
			
			# 这里做一下检测是为了兼容以前的数据，保证客户端接收到的职位名称数据的正确性
			dutys = []
			for item in self.dutyNames:
				dutys.append( item[ "duty" ] )
			interDuty = set( dutys ) & set( csdefine.TONG_DUTYS )
			if len( interDuty ) != len( csdefine.TONG_DUTYS ):
				self.dutyNames = copy.deepcopy( Const.TONG_DUTY_NAME )
			 
			for item in self.dutyNames:
				memberBaseMailbox.client.tong_initDutyName( item[ "duty" ], item[ "dutyName" ] )
			return True
		elif key == TASK_KEY_HOLD_CITY_DATA:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.cell.tong_onSetHoldCity( self.holdCity, True )
			return True
		elif key == TASK_KEY_TONG_SIGN_MD5:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongSignMD5( self.tongSignMD5 )
			return True
		elif key == TASK_KEY_TONG_EXP:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongExp( self.EXP )
			return True
		elif key == TASK_KEY_TONG_SKILL:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.cell.tong_updateTongSkills( self.yjy_level )
			return True
		elif key == TASK_KEY_BATTLE_LEAGUES_DATA:
			datas[ "tasks" ].pop( 0 )
			if memberBaseMailbox == self.getMemberInfos( self.chiefDBID ):	# 只需给帮主发消息
				leagues = []
				for league in self.battleLeagues:
					leagues.append( league[ "dbID" ] )
				memberBaseMailbox.client.tong_receiveBattleLeagues( self.databaseID, self.getName(), self.getCamp(), leagues )
			return True
		return False

	def resetMemberDelayTaskData( self ):
		DEBUG_MSG( "reset to table of task." )
		self._delayDataTasks = {}

	def hasDelayTaskData( self, delayTaskMemberDBID, task ):
		"""
		是否有正在异步处理某任务数据
		@param key: TASK_KEY_*
		"""
		return self.isInDelayTaskList( delayTaskMemberDBID ) and task in self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ]

	def isInDelayTaskList( self, memberDBID ):
		"""
		该成员是否在一个异步数据处理队列中
		"""
		return self._delayDataTasks.has_key( memberDBID )

	def isInDelayTaskMember_MemberList( self, delayTaskMember, memberDBID ):
		"""
		某成员是否在异步数据处理的成员的数据处理列表中
		"""
		if not self.isInDelayTaskList( delayTaskMember ):
			return False

		info = self._delayDataTasks[ delayTaskMember ]
		if not TASK_KEY_MEMBER_DATA in info[ "tasks" ]:
			return False

		if not memberDBID in info[ TASK_KEY_MEMBER_DATA ]:
			return False

		return  True

	def isInDelayTaskMember_LeaguesList( self, delayTaskMember, tongDBID ):
		"""
		某同盟数据是否在异步数据处理的成员的数据处理列表中
		"""
		if not self.isInDelayTaskList( delayTaskMember ):
			return False

		info = self._delayDataTasks[ delayTaskMember ]
		if not TASK_KEY_LEAGUES_DATA in info[ "tasks" ]:
			return False

		if not tongDBID in info[ TASK_KEY_LEAGUES_DATA ]:
			return False

		return  True

	def createSendDataTask( self, memberDBID ):
		"""
		创建一个成员的异步数据发送任务
		"""
		d = {}

		# 新建一个任务数据池
		d[ "tasks" ] = [
				TASK_KEY_LEVEL_DATA,			# 异步数据处理  处理级别数据
				TASK_KEY_DUTY_NAMES_DATA,		# 异步数据处理  处理帮会职位名称数据
				TASK_KEY_MEMBER_DATA, 			# 异步数据处理  处理成员数据
				TASK_KEY_PERSTIGE_DATA, 		# 异步数据处理  处理声望数据
				TASK_KEY_AFFICHE_DATA, 			# 异步数据处理  处理公告数据
				TASK_KEY_MONEY_DATA,			# 异步数据处理  处理金钱数据
				TASK_KEY_HOLD_CITY_DATA,
				TASK_KEY_TONG_SIGN_MD5,
				TASK_KEY_TONG_EXP,				# 异步数据处理  处理经验数据
				TASK_KEY_TONG_SKILL,			# 异步数据处理  处理技能数据
				TASK_KEY_BATTLE_LEAGUES_DATA,	# 异步数据处理 战争同盟数据
		  ]

		# 记录同盟信息到缓冲
		leagues = []
		for litem in self.leagues:
			leagues.append( ( litem[ "dbID" ], litem[ "tongName" ] ) )
		if len( leagues ) > 0:	# 如果有同盟则增加这个任务
			d[ "tasks" ].append( TASK_KEY_LEAGUES_DATA )

		d[ TASK_KEY_MEMBER_DATA ] = self._memberInfos.keys()
		d[ TASK_KEY_LEAGUES_DATA ] = leagues
		self._delayDataTasks[ memberDBID ] = d
		
		TongTerritory.createSendDataTask( self, memberDBID )

	def addSendDataTask( self, memberDBID, taskID, taskData ):
		"""
		添加新任务 该接口主要提供给createSendDataTask被重写在其他模块时避免暴露一些东西
		也就是说在其他模块重载createSendDataTask接口时要向底层添加任务时应该使用本接口添加
		@param taskData: 该任务(taskID)可能携带一些需要传输的大量的数据系列 具体看参见tongEntity.createSendDataTask
						 里面使用的一些方法
		"""
		if not self.isInDelayTaskList( memberDBID ):
			return

		self._delayDataTasks[ memberDBID ][ "tasks" ].append( taskID )
		if taskData:
			self._delayDataTasks[ memberDBID ] = d

	def addMembersToDelayTaskMember( self, delayTaskMemberDBID, memberDBIDList ):
		"""
		向正在异步数据处理的entity发送列表里添加一个新成员
		"""
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			return

		if not TASK_KEY_MEMBER_DATA in self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ]:
			self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ].append( TASK_KEY_MEMBER_DATA )

		self._delayDataTasks[ delayTaskMemberDBID ][ TASK_KEY_MEMBER_DATA ].extend( memberDBIDList )

	def addLeagueToDelayTaskMember( self, delayTaskMemberDBID, tongDBID, tongName ):
		"""
		向正在异步数据处理的league发送列表里添加一个新同盟
		"""
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			return

		if not TASK_KEY_LEAGUES_DATA in self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ]:
			self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ].append( TASK_KEY_LEAGUES_DATA )

		self._delayDataTasks[ delayTaskMemberDBID ][ TASK_KEY_LEAGUES_DATA ].extend( ( tongDBID, tongName ) )

	def delDelayTaskMember( self, memberDBID ):
		"""
		删除一个成员在异步数据发送队列
		"""
		DEBUG_MSG( "delete a taskMember %i." % memberDBID )
		self._delayDataTasks.pop( memberDBID )

	def delDelayTaskMemberTask( self, delayTaskMember, task ):
		"""
		删除异步处理成员的任务列表中的一个任务
		"""
		DEBUG_MSG( "member % i remove a task % i." % ( delayTaskMember, task ) )
		for item in self._delayDataTasks.values():
			if task in item[ "tasks" ]:
				item[ "tasks" ].remove( task )

	def delMemberFromDelayTaskMembers( self, memberDBID ):
		"""
		从所有异步数据成员数据发送队列中清除该成员
		"""
		DEBUG_MSG( "from allTaskMember the list remove member %i" % memberDBID )
		for item in self._delayDataTasks.values():
			if item.has_key( TASK_KEY_MEMBER_DATA ):
				ls = item[ TASK_KEY_MEMBER_DATA ]
				if memberDBID in ls:
					ls.remove( memberDBID )

	def delMemberFromDelayTaskMember( self, delayTaskMemberDBID, memberDBID ):
		"""
		从所有异步数据成员数据发送队列中清除该成员
		"""
		DEBUG_MSG( "from taskMember %i the list remove member %i" % ( delayTaskMemberDBID, memberDBID ) )
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			return

		item = self._delayDataTasks[ delayTaskMemberDBID ]
		if item.has_key( TASK_KEY_MEMBER_DATA ):
			ls = item[ TASK_KEY_MEMBER_DATA ]
			if memberDBID in ls:
				ls.remove( memberDBID )

	def delLeagueInDelayTaskMember( self, memberDBID, tongDBID ):
		"""
		从所有异步数据成员数据发送队列中清除该成员
		"""
		DEBUG_MSG( "from taskMember %i the list remove leagueTong %i" % ( memberDBID, tongDBID ) )
		if not self.isInDelayTaskList( memberDBID ):
			return

		if self._delayDataTasks[ memberDBID ].has_key( TASK_KEY_LEAGUES_DATA ):
			leagues = self._delayDataTasks[ memberDBID ][ TASK_KEY_LEAGUES_DATA ]
			for idx, item in enumerate( leagues ):
				if item[0] == tongDBID:
					leagues.pop( idx )
					return

	#------------------------------------------------------------------------------------------------------------
	def changeName( self, newName ):
		"""
		Define method.
		帮会改名
		"""
		self.playerName = newName
		for dbid in self._onlineMemberDBID:	# 通知所有在线玩家
			try:
				self.getMemberInfos( dbid ).getBaseMailbox().cell.onTongNameChange( newName )
			except:
				continue

	#------------------------------------------------------------------------------------------------------------
	def queryMerchantCount( self, playerMB, questID, count ):
		"""
		Define method
		查询当前帮会等级允许玩家接跑商任务的次数

		"""
		maxCount = TONG_MERCHANT_QUEST_MAX_MAP[self.level]  # 当前帮会等级允许的跑商任务次数

		if count < maxCount:
			playerMB.cell.remoteQuestAccept( questID )
			return

		playerMB.client.onStatusMessage( csstatus.TONG_MERCHANT_MOST, "" )

	def queryDartCount( self, playerMB, questID ):
		"""
		Define method.
		查询帮会运镖次数
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		record = self._dartRecord.split("_")
		if len(record) == 1 or record[0] != day or int(record[1]) < ( csconst.TONG_MEMBER_LIMIT_DICT[self.level]/10):
			playerMB.cell.remoteQuestAccept( questID )
			return

		playerMB.client.onStatusMessage( csstatus.TONG_IS_DART_ONCE, "" )

	def addDartCount( self ):
		"""
		define method
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		record = self._dartRecord.split( "_" )
		if len(record) == 1:
			self._dartRecord = day + "_" + "1"
		else:
			n = int(record[1]) + 1
			self._dartRecord = record[0] + "_" + str(n)

	def addTongNormalCount( self ):
		"""
		define method
		增加帮会日常任务次数
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		record = self.tongNormalRecord.split("_")
		if len(record) == 1 or record[0] != day:
			self.tongNormalRecord = day + "_" + "1"
			return
		else:
			n = int(record[1]) + 1
			self.tongNormalRecord = record[0] + "_" + str(n)

	def queryTongNormalCount(  self, playerMB, questID ):
		"""
		define method added by dqh
		查询帮会日常任务次数
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		count = TONG_NORMAL_QUEST_MAX_MAP[self.level]
		record = self.tongNormalRecord.split("_")

		if len(record) == 1 or record[0] != day:
			playerMB.cell.remoteQuestAccept( questID )
			return

		if int(record[1]) < count:
			playerMB.cell.remoteQuestAccept( questID )
			return

		playerMB.client.onStatusMessage( csstatus.TONG_NORMAL_QUEST_MOST, "" )

	def clearTongDartRecord( self ):
		"""
		define method
		"""
		self._dartRecord = ""

	def setTongFactionCount( self, count ):
		"""
		define method
		设置帮会时装标余量
		"""
		self.factionCount = count

	#--------------------------------------帮会捐献----------------------------------------------------------
	def onContributeToMoney( self, playerBase, playerName, money ):
		"""
		define method
		帮会捐献金钱
		"""
		ConTimes = 100000				# 每获得1点贡献度需要捐献的金钱数
		if money <= 0:
			return

		val = Const.TONG_MONEY_LIMIT[ self.jk_level ][ 1 ] - self.money
		val1 = money - val

		if val1 > 0:
			money -= val1

		if money <= 0:
			self.statusMessage( playerBase, csstatus.TONG_MONEY_MAX )
			return
		self.addMoney( money, csdefine.TONG_CHANGE_MONEY_CONTRIBUTE_TO )
		playerBase.cell.tong_onContributeToMoneySuccessfully( money, val1 > 0 )
		contribute = money / ConTimes 	# 应该增加的贡献度
		if contribute:
			playerBase.cell.tong_addContribute( contribute )
			self.statusMessageToOnlineMember( csstatus.TONG_CONTRIBUTE_TO_MONEY_SUCCESS_2, playerName, Function.switchMoney( money ), contribute, playerName )
		else:
			self.statusMessageToOnlineMember( csstatus.TONG_CONTRIBUTE_TO_MONEY_SUCCESS, playerName, Function.switchMoney( money ), playerName )


	# -------------------------------------会标 by 姜毅--------------------------------------------
	def setTongSignMD5( self, iconMD5 ):
		"""
		define method
		"""
		self.tongSignMD5 = iconMD5
		Love3.g_tongSignMgr.changeTongSign( self.databaseID, iconMD5 )
		# 通知帮会成员换标
		for dbid in self._onlineMemberDBID:	# 通知所有在线玩家
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.tong_onSetTongSignMD5( iconMD5 )

	def getTongSignMD5( self, tongDBID, playerMB ):
		"""
		exposed method
		根据DBID获取其它帮会的帮会会标DBID
		"""
		if not Love3.g_tongSignMgr.hasDymTongSignDatas( tongDBID ):
			return
		iconMD5 = Love3.g_tongSignMgr.getDymTongSignMD5( tongDBID )
		playerMB.client.onGetTongSignMD5( tongDBID, iconMD5 )

	def sendTongSignString( self, tongDBID, playerMB ):
		"""
		defined method
		处理会标发送给客户端
		"""
		iconString = Love3.g_tongSignMgr.getTongSignStrByDBID( tongDBID )
		iconStringList = []
		iconstrlen = len( iconString )
		packs_num = int( iconstrlen/250 ) + 1
		for i in xrange( 0, packs_num ):
			index = i * 250
			end = index + 250
			sList = iconString[index:end]
			iconStringList.append( sList )
		playerMB.tongSignSendStart( self.databaseID, self.tongSignMD5, iconStringList )

	def submitTongSign( self, iconString, iconMD5, playerMB ):
		"""
		define method.
		上传帮会图标

		@param iconString : 图标转换成的字符串
		@type  iconString : STRING
		@param iconMD5 : 图标生成的MD5码
		@type  iconMD5 : INT64
		"""
		# 扣费
		cost = 1 * csconst.USER_TONG_SIGN_REQ_MONEY
		if cost != 0:
			if self.getValidMoney() < cost:
				playerMB.client.onStatusMessage( csstatus.TONG_SIGN_CHANGE_NOT_MONEY, "" )
				return
		Love3.g_tongSignMgr.submitTongSign( self.databaseID, self.getName(), iconString, iconMD5, playerMB )

	def changeTongSing( self, isSysIcon, reqMoney, iconMD5, playerMB ):
		"""
		define method.
		更换帮会图标

		@param iconMD5 : 图标生成的MD5码
		@type  iconMD5 : INT64
		"""
		if self.tongSignMD5 == iconMD5:
			playerMB.client.onStatusMessage( csstatus.TONG_SIGN_USING_NOW, "" )
			return
		if iconMD5 == "sub":	# sub为更换上传会标的指令
			ics = Love3.g_tongSignMgr._TongSignMgr__iconDatas
			if ics.has_key( self.databaseID ):
				iconMD5 = Love3.g_tongSignMgr._TongSignMgr__datas[self.databaseID]
				if self.tongSignMD5 == iconMD5:
					playerMB.client.onStatusMessage( csstatus.TONG_SIGN_USING_NOW, "" )
					return
			else:
				playerMB.client.onStatusMessage( csstatus.TONG_SIGN_SUBMIT_PLEASE, "" )
				return
		if self.getValidMoney() < reqMoney:
			playerMB.client.onStatusMessage( csstatus.TONG_SIGN_CHANGE_NOT_MONEY, "" )
			return
		if not isSysIcon and not Love3.g_tongSignMgr.hasUserTongSignDatas( self.databaseID, iconMD5 ):
			ERROR_MSG( "Tong %s(%i) not has that user define Icon."%( self.getName(), self.databaseID ) )
			return
		# 扣费
		if reqMoney != 0:
			if not self.payMoney( reqMoney, True, csdefine.TONG_CHANGE_MONEY_SUBMIT_TONG_SIGN ):
				ERROR_MSG( "change TongSign pay Money Failed." )
				return
		self.setTongSignMD5( iconMD5 )
		playerMB.client.onStatusMessage( csstatus.TONG_SIGN_CHANGE_SUCCESS, "" )

	# ------------------------- 帮会擂台赛相关 ------------------------------
	def requestAbattoir( self, playerBaseEntity ):
		"""
		Define method.
		申请帮会擂台赛

		@param playerBaseEntity : 帮主的base mailbox
		@type playerBaseEntity : MAILBOX
		"""
		self.calBasePrestige()
		# variablePrestige = self.prestige - self.basePrestige
		#if variablePrestige < csconst.TONG_ABATTOIR_PRESTIGE_LIMIT:
		#	self.statusMessage( playerBaseEntity, csstatus.TONG_ABATTOIR_PRESTIGE_LIMIT )
		#	return

		# CSOL-9992 帮会擂台声望要求修改为总声望
		if self.prestige < csconst.TONG_ABATTOIR_PRESTIGE_LIMIT:
			self.statusMessage( playerBaseEntity, csstatus.TONG_ABATTOIR_PRESTIGE_LIMIT )
			return

		self.getTongManager().requestAbattoir( playerBaseEntity, self.databaseID )

	def onWarKillerPlayer( self, isKiller, memberDBID ):
		"""
		define method.
		帮会擂台中有人被杀或者杀人通知
		"""
		key = csstatus.TONG_WAR_KILL_TO
		if not isKiller:
			key = csstatus.TONG_WAR_KILL_FROM
		self.statusMessageToOnlineMember( key, self.getMemberInfos( memberDBID ).getName() )

	def onWarBuyItemsMessage( self, memberDBID, itemCount, itemName, payMarks ):
		"""
		define method.
		玩家在副本内购买物品 产生的消息
		"""
		name = self.getMemberInfos( memberDBID ).getName()
		self.statusMessageToOnlineMember( csstatus.TONG_WAR_BUY_INFO, name, itemCount, itemName, payMarks )
				
	def tongAbaGather( self,round ):
		"""
		通知帮会成员擂台赛集合开始
		@param round : 当前轮数
		@type round : UINT8
		"""
		self.tongAbaGatherFlag = round
		for dbid in self._onlineMemberDBID:			# 通知所有在线玩家
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.tongAbaGather( round )
			memberMB.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
	
	def tongAbaCloseGather( self ):
		"""
		通知帮会成员擂台赛集合结束
		"""
		self.tongAbaGatherFlag = None
		for dbid in self._onlineMemberDBID:			# 通知所有在线玩家
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )

	def tongCompetitionGather( self,flag ):
		"""
		define method
		通知帮会成员帮会竞技集合开始
		@param round : 标志
		@type round : UINT8
		"""
		self.tongCompetitionGatherFlag = flag
		for dbid in self._onlineMemberDBID:			# 通知所有在线玩家
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.tongCompetitionGather()
			memberMB.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )
	
	def tongCompetitionCloseGather( self ):
		"""
		define method
		通知帮会成员帮会竞技集合结束
		"""
		self.tongCompetitionGatherFlag = None
		for dbid in self._onlineMemberDBID:			# 通知所有在线玩家
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )


	def updateTongAbaRound( self,round ):
		"""
		帮会擂台当前比赛情况更新
		"""
		self.tongAbaRound = round
		for dbid in self._onlineMemberDBID:			# 通知所有在线玩家
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.receiveAbaRound( round )

	# ------------------------- 帮会竞技相关 ------------------------------

	def requestCompetition( self, playerBaseEntity ):
		"""
		Define method.
		申请帮会擂台赛

		@param playerBaseEntity : 帮主的base mailbox
		@type playerBaseEntity : MAILBOX
		"""
		self.calBasePrestige()
		if self.prestige < csconst.TONG_ABATTOIR_PRESTIGE_LIMIT:
			self.statusMessage( playerBaseEntity, csstatus.TONG_ABATTOIR_PRESTIGE_LIMIT )
			return

		if not self.isTongMemberLimit():		# 报名帮会60级以上玩家人数必须达到10个或以上
			self.statusMessage( playerBaseEntity, csstatus.TONG_COMPETETION_NOTICE_4 )
			return

		BigWorld.globalData["TongCompetitionMgr"].onRequestCompetition( playerBaseEntity, self.databaseID )

	def isTongMemberLimit( self ):
		"""
		统计自己帮会60级以上玩家人数
		"""
		memberCount = len( self._memberInfos )
		if memberCount == 0:	# 没有帮会成员
			return False
		if memberCount >= COMPETITION_MEMBER_LIMIT:
			k = 0
			for info in self._memberInfos.itervalues():
				tongMemberLevel = info.getLevel()
				if tongMemberLevel >= COMPETITION_LEVEL_LIMIT:
					k += 1
			return k >= COMPETITION_MEMBER_LIMIT
		else:
			return False

	def sendAwardToChief( self ):
		"""
		Define method.
		副本活动结束后，统一发送奖励到冠军帮主的邮箱
		"""
		chiefName = self.chiefName		# 帮主名字
		itemDatas = []
		item = g_item.createDynamicItem( 60101261, 1 )
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
			BigWorld.globalData["MailMgr"].send(None, chiefName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.TONGCOMPETITION_CHIEF_MAIL_REWARD_TITLE, "", 0, itemDatas)
	
	# ---------------------------------- 帮众领取俸禄相关--------------------------------------------
	def calTongSalary( self ):
		"""
		define mehtod
		处理帮会俸禄相关数据
		"""
		self.lastWeekTongTotalMoney = self.weekTongMoney					# 上周帮会资金总输入
		self.weekTongMoney = 0
		
		self.lastWeekSalaryExchangeRate = self.weekSalaryExchangeRate		# 上周俸禄兑换额
		self.weekSalaryExchangeRate = self.nextWeekSalaryExchangeRate		# 本周俸禄兑换额
		
		self.lastWeekTotalExchangedSalary = self.weekTotalExchangedSalary	# 上周帮会实际俸禄支出
		self.weekTotalExchangedSalary = 0
		
		self.lastWeekTongTotalContribute = self.weekTongTotalContribute 	# 上周帮会帮贡总值 
		self.weekTongTotalContribute = 0
		
		self.lastWeekTongTotalCost = self.weekTotalCost						# 上周帮会资金总支出
		self.weekTotalCost = 0
		
		self.lastWeekTongMoneyRemain = self.money							# 上周帮会资金余额
		
		# 帮会成员相关数据重置
		for memberDBID, memberInfo in self._memberInfos.iteritems():
			for item in self.memberTotalContributes:
				if item[ "dbID" ] == memberDBID:
					item[ "lastWeekTotalContribute" ] = memberInfo.getWeekTongContribute()
					memberInfo.setLastWeekTotalContribute( memberInfo.getWeekTongContribute() )
					item[ "weekTongContribute" ] = 0
					memberInfo.updateWeekTongContribute( 0 )
					
					item[ "lastWeekSalaryReceived" ] = memberInfo.getWeekSalaryReceived()
					memberInfo.setLastWeekSalaryReceived( memberInfo.getWeekSalaryReceived() ) 
					item[ "weekSalaryReceived" ] = 0
					memberInfo.setWeekSalaryReceived( 0 )
					
	def requestMemberContributeInfos( self, userDBID ):
		"""
		define method
		客户端请求本帮会玩家的帮贡信息:累计帮贡总值、剩余帮贡值、本周获得帮贡、上周获得帮贡
		"""
		for dbid in self._onlineMemberDBID:
			info = self.getMemberInfos( dbid )
			info.getBaseMailbox().client.tong_updateMemberContributeInfos( dbid, info.getTotalContribute(), \
							info.getContribute(), info.getWeekTongContribute(), info.getLastWeekTotalContribute() )
	
	def onRequireSalaryInfo(self, baseEntity, playerDBID ):
		"""
		define method 
		客户端请求玩家俸禄信息
		"""
		info = self.getMemberInfos( playerDBID )
		lastWeekTotalContribute = info.getLastWeekTotalContribute()			# 上周获取帮贡累计总值
		lastWeekSalaryChangeRate = self.lastWeekSalaryExchangeRate			# 上周帮会俸禄兑换额
		lastReceivedSalary = info.getLastWeekSalaryReceived()				# 上周领取俸禄总额
		thisWeelTotalContribute = info.getWeekTongContribute()				# 本周获取帮贡累计总值
		thisWeekSalaryChangeRate = self.weekSalaryExchangeRate				# 本周帮会俸禄兑换额
		baseEntity.client.tong_receiveSalaryInfo( lastWeekTotalContribute, lastWeekSalaryChangeRate, lastReceivedSalary,\
							thisWeelTotalContribute, thisWeekSalaryChangeRate )
							
	def onClientOpenTongMoneyWindow( self, playerBase ):
		"""
		define method 
		客户端打开了帮会资金子界面，所需求数据
		"""
		# 上周帮会资金总收入、上周俸禄兑换额、上周帮贡总值、上周帮会俸禄实际支出、上周帮会资金总支出、上周帮会资金余额
		lastWeekInfo = [ self.lastWeekTongTotalMoney, self.lastWeekSalaryExchangeRate, self.lastWeekTongTotalContribute, \
						self.lastWeekTotalExchangedSalary, self.lastWeekTongTotalCost, self.lastWeekTongMoneyRemain ]
		# 本周帮会资金收入、本周帮会俸禄兑换额、本周帮会帮贡总值、本周帮会资金支出、下周帮会兑换额
		thisWeekInfo = [ self.weekTongMoney, self.weekSalaryExchangeRate, self.weekTongTotalContribute, self.weekTotalCost,self.nextWeekSalaryExchangeRate ]
		
		playerBase.client.tong_receiveTongMoneyInfo( lastWeekInfo, thisWeekInfo )

	def onDrawTongSalary( self, memberDBID ):
		"""
		define method
		玩家领取俸禄
		"""
		info = self.getMemberInfos( memberDBID )
		
		if info.getWeekTongContribute() == 0:			# 本周帮贡为0
			self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SALARY_HAVE_NO_CONTRIBUTE )
			return 
		
		if info.getWeekSalaryReceived() > 0:			# 已经领取过俸禄
			self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SALARY_ALREDY_RECEIVED )
			return 
			
		weekSalaryReceive = info.getWeekTongContribute() * self.weekSalaryExchangeRate 		# 本周总帮贡 * 本周每点帮会兑换额*铜/点
		
		if not self.payMoney( weekSalaryReceive, True, csdefine.TONG_CHANGE_MONEY_SALARY ):			# 帮会资金小于保底资金
			self.statusMessage( info.getBaseMailbox(), csstatus.TONG_LSEE_KEEP_MONEY )
			return 
		
		info.setWeekSalaryReceived( weekSalaryReceive )
		# 这里需要将信息同步到帮会的成员结构中
		for item in self.memberTotalContributes:
			if item[ "dbID" ] == memberDBID:
				item[ "weekSalaryReceived" ] = weekSalaryReceive
		self.weekTotalExchangedSalary += weekSalaryReceive												# 本周帮会支付俸禄
		if self.holdCity:
			weekSalaryReceive *=2
		
		info.getBaseMailbox().cell.addMoney( weekSalaryReceive, csdefine.TONG_CHANGE_MONEY_SALARY )		# 给玩家身上加钱
		self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SALARY_DRAW_SUCCESS )
	
	def setContributeExchangeRate( self, memberDBID, rate ):
		"""
		define method
		帮主设定帮会俸禄兑换额
		"""
		info = self.getMemberInfos( memberDBID )
		if not self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_SALARY_RATE):	# 如果不是帮主，返回	
			return
		self.nextWeekSalaryExchangeRate = rate
		self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SET_SALARY_CHANGE_RATE_SUCCESS, rate )	
		info.getBaseMailbox().client.tong_updateNextWeekExchangeRate( self.nextWeekSalaryExchangeRate )
	
	def queryTongChiefInfos( self ):
		# define method
		# 获取帮主模型信息
		if self.getMemberInfos( self.chiefDBID ).isOnline():
			self.getMemberInfos( self.chiefDBID ).getBaseMailbox().cell.tong_queryTongChiefInfos()
		else:
			self.queryDatabaseChiefInfos()
	
	def queryDatabaseChiefInfos( self ):
		sqlStr = "SELECT sm_raceclass, sm_hairNumber, sm_faceNumber, sm_bodyFDict_iLevel, sm_bodyFDict_modelNum, sm_volaFDict_iLevel,sm_volaFDict_modelNum, sm_breechFDict_iLevel, sm_breechFDict_modelNum, sm_feetFDict_iLevel, sm_feetFDict_modelNum, sm_lefthandFDict_iLevel, sm_lefthandFDict_modelNum, sm_lefthandFDict_stAmount, sm_righthandFDict_iLevel, sm_righthandFDict_modelNum, sm_righthandFDict_stAmount, sm_talismanNum, sm_fashionNum, sm_adornNum from tbl_Role where id =%d" % self.chiefDBID
		
		def queryTableResult( result, rows, errstr ):
			infosData = [ int( i ) for i in result[0] ]
			obj = MasterChiefData()
			obj[ "uname" ]  = self.chiefName
			obj[ "tongName" ] = self.playerName
			obj[ "raceclass" ] = infosData[ 0 ]
			obj[ "hairNumber" ] = infosData[ 1 ]
			obj[ "faceNumber" ] = infosData[ 2 ]
			obj[ "bodyFDict" ] = { "iLevel":infosData[3], "modelNum":infosData[4] }
			obj[ "volaFDict" ] = { "iLevel":infosData[5], "modelNum":infosData[6] }
			obj[ "breechFDict" ] = { "iLevel":infosData[7], "modelNum":infosData[8] }
			obj[ "feetFDict" ] = { "iLevel":infosData[9], "modelNum":infosData[10] }
			obj[ "lefthandFDict" ] = { "iLevel":infosData[11], "modelNum":infosData[12], "stAmount": infosData[13] }
			obj[ "righthandFDict" ] = { "iLevel":infosData[14], "modelNum":infosData[15], "stAmount": infosData[16] }
			obj[ "talismanNum" ] = infosData[ 17 ]
			obj[ "fashionNum" ] = infosData[ 18 ]
			obj[ "adornNum" ] = infosData[ 19 ]
			BigWorld.globalData[ "TongManager" ].cityWarOnQueryMasterInfo( self.databaseID, obj )
		
		BigWorld.executeRawDatabaseCommand( sqlStr, queryTableResult )
		
	def infoCallMember( self, userDBID, lineNumber, spaceName, position, direction, limitLevel, showMessage ):
		"""
		define method
		"""
		if len( self._onlineMemberDBID ) < 2:
			return

		userInfo = self.getMemberInfos( userDBID )
		user = userInfo.getBaseMailbox()
		
		for dbid in self._onlineMemberDBID:
			memberLevel = self.getMemberInfos( dbid ).getLevel()				# 在线帮会成员等级
			casterLevel = self.getMemberInfos( userDBID ).getLevel()			# 施法者的等级
			casterName = self.getMemberInfos( userDBID ).getName()				# 施法者的名字
			if userDBID != dbid and (( memberLevel >= casterLevel - limitLevel ) and ( memberLevel <= casterLevel + limitLevel )):
				self.getMemberInfos( dbid ).getBaseMailbox().client.infoTongMember( lineNumber, casterName, showMessage, spaceName, position, direction )
				
	def addTongTurnWarPoint( self, cityName, amount ):
		"""
		define method
		
		给帮会加车轮战积分
		
		@param cityName: 哪个城市的积分
		@param amount: 分值
		"""
		for oneCityPoint in self.tongTurnWarPoint:		# tongTurnWarPoint 结构为[ { "cityName", "point" } ]
			if oneCityPoint["cityName"] == cityName:
				oneCityPoint["point"] += amount
				self.getTongManager().updateTongTurnWarPoint( self.databaseID, cityName, oneCityPoint["point"] )
				self.writeToDB()
				return
				
		#如果列表中没有该城市的积分信息，则需要添加
		info = { "cityName": cityName, "point": amount }
		self.tongTurnWarPoint.append( info )
		self.getTongManager().updateTongTurnWarPoint( self.databaseID, cityName, amount )
		self.writeToDB()
		
	def roleRequestTongExp( self, roleDBID ):
		"""
		define method
		玩家请求帮会经验数据
		"""
		if roleDBID not in self._onlineMemberDBID:
			return
		
		roleMB = self.getMemberInfos( roleDBID ).getBaseMailbox()
		if roleMB and not self.hasDelayTaskData( roleDBID, TASK_KEY_TONG_EXP ):
			roleMB.client.tong_onSetTongExp( self.EXP )

	# -------------------------------------------------战争结盟功能-------------------------------------------

	def inviteTongBattleLeague( self, inviterDBID, inviteeTongDBID, msg, maxNum ):
		"""
		define method
		本帮会邀请战争结盟
		"""
		self.battleLeagueMaxNum = maxNum
		DEBUG_MSG( "TONG: %i invite tong %s to battle league." % ( inviterDBID, inviteeTongDBID ) )
		inviter = self.getMemberInfos( inviterDBID ).getBaseMailbox()
		inviterGrade = self.getMemberInfos( inviterDBID ).getGrade()
		# 权限检测
		if not self.checkMemberDutyRights( inviterGrade, csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			self.statusMessage( inviter, csstatus.TONG_GRADE_INVALID )
			return
		
		if inviteeTongDBID <= 0:
			self.statusMessage( inviter, csstatus.TONG_TARGET_TONG_NO_FIND )
			return
		
		# 最大战争结盟帮会数量判断
		if len( self.battleLeagues ) >= self.battleLeagueMaxNum:
			self.statusMessage( inviter, csstatus.TONG_BATTLE_LEAGUE_FULL)
			return
		
		# 是否已经提交过申请
		if self._inviteBattleLeagueRecord.has_key( inviteeTongDBID ):
			self.statusMessage( inviter, csstatus.TONG_WAITING_RESPONSE )
			return
		
		dict = {}
		dict[ "inviterDBID" ] = inviterDBID
		dict[ "inviteeTongDBID" ] = inviteeTongDBID
		dict[ "time" ] = BigWorld.time()
		self._inviteBattleLeagueRecord[ inviteeTongDBID ] = dict
		self.getTongManager().onInviteTongBattleLeague( inviter, self.databaseID, inviteeTongDBID, msg )

		# 如果没有时钟检测了 那么开启检测过时请求
		if self._check_inviteBattleLeagueTimerID <= 0:
			self._check_inviteBattleLeagueTimerID = self.addTimer( CONST_REQUEST_JOIN_TIMEOUT, CONST_REQUEST_JOIN_TIMEOUT, TIME_CBID_CHECK_REQUEST_JOIN )

	def receiveBattleLeagueInvitation( self, inviter, inviterTongName, inviterTongDBID, msg, maxNum ):
		"""
		define method
		被邀请方帮会收到战争结盟申请 第五步
		@param inviter				:使用功能者baseMailbox
		@param userTongName		:使用功能者 帮会的名称
		@param userTongDBID		:使用功能者 帮会的DBID
		"""
		self.battleLeagueMaxNum = maxNum
		# 最大战争结盟帮会数量判断
		if len( self.battleLeagues ) > self.battleLeagueMaxNum:
			self.statusMessage( inviter, csstatus.TONG_TARGET_BATTLE_LEAGUE_FULL)
			self.getTongManager().onInviteTongBattleLeagueFailed( inviterTongDBID, self.databaseID )
			return

		for dbid, info in self._memberInfos.iteritems():
			if self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
				if info.isOnline():
					info.getBaseMailbox().client.tong_receiveBattleLeagueInvitation( inviterTongName, inviterTongDBID, msg )
					return

		self.statusMessage( inviter, csstatus.TONG_BATTLE_LEAGUE_CHIEF_OFFLINE )
		self.getTongManager().onInviteTongBattleLeagueFailed( inviterTongDBID, self.databaseID )

	def onInviteTongBattleLeagueFailed( self, inviteeTongDBID ):
		"""
		define method
		邀请战争同盟帮会失败
		"""
		self._inviteBattleLeagueRecord.pop( inviteeTongDBID )

	def replyBattleLeagueInvitation( self, replierBaseMailbox, inviterTongDBID, response ):
		"""
		define method
		被邀请帮会回复战争结盟邀请
		"""
		# 最大战争结盟帮会数量判断
		if len( self.battleLeagues ) > self.battleLeagueMaxNum:
			self.statusMessage( replierBaseMailbox, csstatus.TONG_TARGET_BATTLE_LEAGUE_FULL)
			self.getTongManager().onInviteTongBattleLeagueFailed( inviterTongDBID, self.databaseID )
			return
		
		self.getTongManager().replyBattleLeagueInvitation( replierBaseMailbox, self.databaseID, inviterTongDBID, response )

	def receiveBattleLeagueReply( self, replierBaseMailbox, replierTong, replierTongDBID, replierTongName, response ):
		"""
		define method
		收到邀请回复
		"""
		DEBUG_MSG( "TONG: %i answer tong %i to battle league." % ( replierTongDBID, self.databaseID ) )
		
		if replierTongDBID not in self._inviteBattleLeagueRecord:
			return
		
		info = self._inviteBattleLeagueRecord[ replierTongDBID ]
		# 超时了 返回
		if self.checkRequestLeagueTimeOut( info[ "time" ] ):
			return
		inviter = self.getMemberInfos( info[ "inviterDBID" ] ).getBaseMailbox()
		inviteeTongDBID = info[ "inviteeTongDBID" ]
		del self._inviteBattleLeagueRecord[ replierTongDBID ]
		
		if len( self.battleLeagues ) >= self.battleLeagueMaxNum:
			self.statusMessage( replierBaseMailbox, csstatus.TONG_TARGET_BATTLE_LEAGUE_FULL )
			return
		
		if not response:	# 拒绝
			if inviter:
				self.statusMessage( inviter, csstatus.TONG_BATTLE_LEAGUE_FAIL, replierTongName )
			return
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_BATTLE_ALIGNMENT_NOTIFY % ( replierTongName, self.playerName ), [] )
		replierTong.addBattleLeague( self.databaseID, self.playerName )
		self.onAddBattleLeague( replierTongDBID, replierTongName )

	def addBattleLeague( self, leagueDBID, leagueName ):
		"""
		define method
		被动添加战争同盟
		"""
		if self.hasBattleLeaguesTong( leagueDBID ):
			ERROR_MSG( "TONG: battle league %s %i is exist." % ( leagueName, leagueDBID ) )
			return
		
		self.onAddBattleLeague( leagueDBID, leagueName  )

	def onAddBattleLeague( self, leagueDBID, leagueName ):
		"""
		处理建立战争同盟
		"""
		self.battleLeagues.append( { "dbID" : leagueDBID, "tongName" : leagueName, "tid" : 0, "ad" : "" } )
		if self.chiefDBID in self._onlineMemberDBID:
			userInfo = self.getMemberInfos( self.chiefDBID )
			userInfo.getBaseMailbox().client.tong_addBattleLeague( leagueDBID, leagueName )

		# 将数据更新到管理器
		self.getTongManager().updateTongBattleLeagues( self.databaseID, self.battleLeagues )
	
	def hasBattleLeaguesTong( self, leagueDBID ):
		"""
		判断是否有该战争同盟帮会
		"""
		for league in self.battleLeagues:
			if league[ "dbID" ] == leagueDBID:
				return True
		return False

	def onCheckRequestBattleLeagueTimer( self ):
		"""
		删除过时的战争结盟请求
		"""
		outdatedInvite = []
		for key, info in self._inviteBattleLeagueRecord.iteritems():
			if self.checkRequestLeagueTimeOut( info[ "time" ] ):
				outdatedInvite.append( key )

		for key in outdatedInvite:
			self._inviteBattleLeagueRecord.pop( key )

		if len( self._inviteBattleLeagueRecord ) <= 0:
			self.delTimer( self._check_inviteBattleLeagueTimerID )
			self._check_inviteBattleLeagueTimerID = 0

	def requestBattleLeagueDispose( self,  userDBID, battleLeagueDBID ):
		"""
		define method
		客户端申请解除战争同盟
		"""
		if userDBID != -1:
			user = self.getMemberInfos( userDBID ).getBaseMailbox()
			userGrade = self.getMemberInfos( userDBID ).getGrade()
			# 权限判断
			if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
				self.statusMessage( user, csstatus.TONG_GRADE_INVALID )
				return
		
		self.onBattleLeagueDispose( battleLeagueDBID, True )

	def battleLeagueDispose( self, leagueTongDBID ):
		"""
		define method
		被动解除战争同盟关系
		"""
		self.onBattleLeagueDispose( leagueTongDBID, False )

	def onBattleLeagueDispose( self, battleLeagueDBID, initiative ):
		"""
		处理解除战争同盟
		@param initiative: 是否主动解除同盟关系
		"""
		msgKey = csstatus.TONG_BATTLE_LEAGUE_QUIT_TO
		if not initiative:
			msgKey = csstatus.TONG_BATTLE_LEAGUE_QUIT
		
		for idx, item in enumerate( self.battleLeagues ):
			if item[ "dbID" ] == battleLeagueDBID:
				self.battleLeagues.pop( idx )

				if initiative:
					self.getTongManager().onBattleLeagueDispose( battleLeagueDBID, self.databaseID )
				
				if self.chiefDBID in self._onlineMemberDBID:
					chiefMB = self.getMemberInfos( self.chiefDBID ).getBaseMailbox()
					chiefMB.client.tong_delBattleLeague( battleLeagueDBID )
				
				for dbid in self._onlineMemberDBID:
					member = self.getMemberInfos( dbid ).getBaseMailbox()
					self.statusMessage( member, msgKey, item[ "tongName" ] )

				break
				
	# ----------------------------------------帮会特殊商品----------------------------------------------
	def initTongSpecialItems( self, reset = False ):
		"""
		初始化帮会特殊商品
		"""
		TongTerritory.onInitTongSpecialItems( self, reset )
		self.specItems = []
		itemDatas = g_tongSpecItems.getDatas()

		for itemID, item in itemDatas.iteritems():
			# 防止超过物品最大级别
			if self.level >= item[ "reqTongLevel" ]:
				itemData = { "itemID":itemID, "amount":item["amount"], "reqMoney":item["reqMoney"]}
				self.specItems.append( itemData )
		
		self.specItems.sort( key = lambda item : item["itemID"], reverse = False )

	def resetTongSpecialItems( self ):
		"""
		define method
		重置帮会特殊商品
		"""
		self.initTongSpecialItems( 1 )

	def addSpecialItemReward( self,  itemID, amount ):
		"""
		define method
		给帮会发放特殊物品奖励，存放到特殊商人NPC
		没有金钱和帮会等级购买要求
		"""
		rewardItem = { "itemID":itemID, "amount":amount, "reqMoney":0}
		copySpecItems = copy.deepcopy( self.specItems )
		copySpecItems.append( rewardItem )
		copySpecItems.sort( key = lambda item : item["itemID"], reverse = False )
		self.specItems = copySpecItems
		TongTerritory.onAddSpecialItemReward(  self, itemID, amount )

#
# $Log: not supported by cvs2svn $
# Revision 1.21  2008/08/15 07:38:22  kebiao
# add:getMemberInfos
#
# Revision 1.20  2008/08/14 09:11:34  kebiao
# 增加帮会工资功能
#
# Revision 1.19  2008/08/12 08:52:02  kebiao
# 添加帮主集结令功能
#
# Revision 1.18  2008/07/24 02:04:47  kebiao
# 修改权限的实现方式
#
# Revision 1.17  2008/07/22 08:50:07  songpeifang
# 按照黄栋要求把所有GUILD都改成了TONG，因为TONG是帮会，而GUILD是旧军团
#
# Revision 1.16  2008/07/22 03:43:31  huangdong
# 修改了帮会聊天一个接口名
#
# Revision 1.15  2008/07/22 01:58:28  huangdong
# 完善帮派聊天
#
# Revision 1.14  2008/07/02 02:36:35  kebiao
# 修正一条数据库指令
#
# Revision 1.13  2008/07/02 02:02:18  kebiao
# 修正权限设置的关系问题， 不能设置比自己职位高的， 也不能把别人设置
# 的比自己高
#
# Revision 1.12  2008/07/01 02:22:27  kebiao
# 添加设置职位名称判断
#
# Revision 1.10  2008/07/01 01:40:46  kebiao
# 修改一个Const.TONG_USE_GRADES地址共享造成的一个BUG
#
# Revision 1.9  2008/06/30 04:15:23  kebiao
# 增加帮会职位名称编辑
#
# Revision 1.8  2008/06/27 09:02:25  kebiao
# 加入帮会销毁后同盟关系自动解除 一个BUG修正
#
# Revision 1.7  2008/06/27 08:25:52  kebiao
# 加入帮会销毁后同盟关系自动解除
#
# Revision 1.6  2008/06/27 07:12:31  kebiao
# 增加了帮会和家族的异步数据传输机制
#
# Revision 1.5  2008/06/23 08:11:31  kebiao
# 增加某些地方的数据库及时更新
# 某些在线成员属性值没有来的及在一个tick存入数据库,
# 而不在线成员的值却被写入造成的不可预料的错误
#
# Revision 1.4  2008/06/21 03:42:50  kebiao
# 加入帮会贡献度
#
# Revision 1.3  2008/06/16 09:13:04  kebiao
# 增加权衡关系
#
# Revision 1.2  2008/06/14 09:18:51  kebiao
# 新增帮会功能
#
# Revision 1.1  2008/06/09 09:24:33  kebiao
# 加入帮会相关
#
#