# -*- coding: gb18030 -*-
#
# $Id: TongManager.py,v 1.10 2008-08-25 09:30:09 kebiao Exp $
import sys
import cschannel_msgs
import ShareTexts as ST
import time
import BigWorld
import csdefine
import csstatus
import csconst
import Const
from bwdebug import *
from Function import Functor
from interface.TongCityWarManager import TongCityWarManager
from interface.TongTerritoryManager import TongTerritoryManager
from interface.TongRobWarManager import TongRobWarManager
from interface.TongFeteManager import TongFeteManager
from interface.TongAbattoirMgr import TongAbattoirMgr
from interface.TongTurnWarManager import TongTurnWarManager
from interface.TongFengHuoLianTianMgr import TongFengHuoLianTianMgr
from interface.TongCityWarFinalManager import TongCityWarFinalManager
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger


CLEAR_CREATE_TEMP_DATA_INTERVAL = 5			# 清理帮会建立临时数据的timer检测间隔


def calcToPointTime( point ):
	"""
	始终返回 离point的时间差  比如point=21点 返回现在离下一次21点所需要的时间
	@param point: 一个时间点 比如21点 只能是整数 不超过24
	"""
	t = time.localtime()
	h = t[ 3 ]
	m = t[ 4 ]
	s = t[ 5 ]
	h = point - h

	if h <= 0:
		h = point + ( 24 - t[ 3 ] )

	if m > 0:
		m = 60 - m
		h -= 1

	if s > 0:
		s = 60 - s
		m -= 1
	return abs( ( h * 60 * 60 ) + ( m * 60 ) + s )

CLEAR_REQUESTJOINTONGINFO_POINT = 24

class TongManager( BigWorld.Base,
				   TongCityWarManager,
				   TongTerritoryManager,
				   TongRobWarManager,
				   TongFeteManager,
				   TongAbattoirMgr,
				   TongTurnWarManager,
				   TongFengHuoLianTianMgr,
				   TongCityWarFinalManager,
):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		TongCityWarManager.__init__( self )
		TongTerritoryManager.__init__( self )
		TongRobWarManager.__init__( self )
		TongFeteManager.__init__( self )
		TongAbattoirMgr.__init__( self )
		TongTurnWarManager.__init__( self )
		TongFengHuoLianTianMgr.__init__( self )
		TongCityWarFinalManager.__init__( self )

		self._tongBaseDatas = {}										# 帮会基础数据 包括 帮会名称”、“帮主”、“帮会等级”、“人数”、“当前建设”、“占领城市”、“帮会同盟”
																		# 服务器每次启动就会从数据库中查询一次， 之后如果有在线帮会改变某些数据也会更新进来。
		self._enterTongMembers_temp = {}								# 在一个帮会Entity还未被加载时 成员要求进入的临时记录数据. 在创建后将这些成员送入帮会entity后清空
		self._tongEntitys = {}											# 所有的帮会实体 { dbid: tongEntity }
		
		self.tempCreateInfo = {}				# 正在建立的帮会信息，建立帮会是一个异步过程，like as:{creatorDBID:(tongName,recordTime,tongEntity), ... }，记录下来表示建立帮会的请求已经通过验证。
		self.clearTempCreateInfoTimerID = 0		# 清理过期建立帮会临时数据的timerID
		
		self.loadAllTongTimerID = 0										# 加载帮会的timerID
		self.loadAllTongBaseDatas()										# 加载所有的帮会的基础数据
		self.registerGlobally( "TongManager", self.onRegisterTongManager )
		
	#--------------------------------------------------------------------------------------------------------------------------
	def onManagerInitOver( self ):
		"""
		virtual method.
		管理器初始化完毕
		"""
		TongCityWarManager.onManagerInitOver( self )
		TongRobWarManager.onManagerInitOver( self )
		TongTerritoryManager.onManagerInitOver( self )
		TongFeteManager.onManagerInitOver( self )
		TongAbattoirMgr.onManagerInitOver( self )
		TongTurnWarManager.onManagerInitOver( self )
		TongFengHuoLianTianMgr.onManagerInitOver( self )
		TongCityWarFinalManager.onManagerInitOver( self )
		self.tongManagerRegisterCrond()

	#-------------------------TongManager本身的相关初始化和注册-----------------------------------------------------------------
	def onRegisterTongManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TongManager Failed!" )
			# again
			self.registerGlobally( "TongManager", self.onRegisterTongManager )
		else:
			DEBUG_MSG( "TongManager Register Succeed!" )
			BigWorld.globalData["TongManager"] = self					# 注册到所有的服务器中
			if self.playerName == "":
				DEBUG_MSG( "TongManager Write To DB Now..." )
				self.playerName = "TongManager"
				self.writeToDB( self.onCreatedTongManager )

	def onCreatedTongManager( self, success, entity ):
		"""
		把实体写入数据库回调
		"""
		if success:
			DEBUG_MSG( "TongManager Write To Data Base Succeed!" )
		else:
			ERROR_MSG( "TongManager can't write to DataBase!" )

	def statusMessage( self, targetBaseMailbox, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = args == () and "" or str( args )
		targetBaseMailbox.client.onStatusMessage( statusID, args )

	def statusTongMessage( self, tongEntity, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = args == () and "" or str( args )
		tongEntity.onStatusMessage( statusID, args )

	#--------------------------从数据库加载帮会　初始化----------------------------------------------------------------
	def onLoadAllTongOver( self ):
		"""
		virtual method.
		所有帮会加载完毕.
		"""
		TongCityWarManager.onLoadAllTongOver( self )

	def onLoadAllTongTimer( self ):
		"""
		加载帮会timer被触发
		"""
		if len( self.tmpTongInfos ) <= 0:
			return

		for x in xrange( 1 ):
			dbID = self.tmpTongInfos.pop(0)
			tongInfo = self._tongBaseDatas[ dbID ]
			if dbID > 0:
				BigWorld.createBaseFromDBID( "TongEntity", dbID, Functor( self.onCreateTongEntityBaseFromDBID, dbID, tongInfo["tongName"] ) )

			if len( self.tmpTongInfos ) <= 0:
				self.delTimer( self.loadAllTongTimerID )
				self.loadAllTongTimerID = 0
				self.onLoadAllTongOver()
				DEBUG_MSG( "All tong[count=%i] is load complete! use time:%s" % ( len( self._tongBaseDatas ), time.time() - self.loadAllTongTime ) )
				del self.tmpTongInfos
				del self.loadAllTongTime
				return
		
	def onCreateTongEntityBaseFromDBID( self, tongDBID, tongName, baseRef, databaseID, wasActive ):
		"""
		加载帮会entity时createBaseFromDBID回调。
		"""
		assert wasActive is False, "%s(%i): the target entity was active, I can't do it. tongDBID %i %s" % ( self.playerName, self.id, tongDBID, tongName )
		if baseRef == None:
			ERROR_MSG( "TongEntity Create From DBID Error! tongDBID %i, tongName:%s" % ( tongDBID, tongName ) )
		else:
			pass

	def loadTongByDBIDFromDB( self, tongDBID ):
		"""
		从数据库加载帮会
		"""
		if tongDBID != 0:
			if hasattr( self, "tmpTongInfos" ):
				for tongDBID in self.tmpTongInfos:
					self.tmpTongInfos.remove( tongDBID )
					break
				else:
					return
			else:
				return
			BigWorld.createBaseFromDBID( "TongEntity", tongDBID, Functor( self.onCreateTongEntityBaseByDBIDFromDBID, tongDBID ) )
		else:
			ERROR_MSG( "create tong dbid=%i is failed." % ( tongDBID ) )

	def onCreateTongEntityBaseByDBIDFromDBID( self, tongDBID, baseRef, databaseID, wasActive ):
		"""
		加载帮会entity时createBaseFromDBID回调。
		"""
		assert wasActive is False, "%s(%i): the target entity was active, I can't do it. tongDBID %i" % ( self.playerName, self.id, tongDBID )
		if baseRef == None:
			ERROR_MSG( "TongEntity Create From DBID Error! tongDBID %i" % ( tongDBID ) )
		else:
			pass

	def onTongEntityLoadMemberInfoComplete( self, tongDBID, tongEntity, chiefName ):
		"""
		virtual method.
		帮会实体加载完成员数据了
		"""
		self._tongEntitys[ tongDBID ] = tongEntity
		self._tongBaseDatas[tongDBID]["chiefName"] = chiefName
		TongCityWarManager.onTongEntityLoadMemberInfoComplete( self, tongDBID, tongEntity, chiefName )

		if self._enterTongMembers_temp.has_key( tongDBID ):
			for info in self._enterTongMembers_temp[ tongDBID ]:
				tongEntity.onMemberLogin( info[ "baseEntity" ], info[ "dbid" ] )
			self._enterTongMembers_temp.pop( tongDBID )

	#-----------------------------计划任务-------------------------------------------------------------
	def tongManagerRegisterCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	"chargeSpendMoney": "onChargeSpendMoney",				# 检查帮会建筑维护费
					  	"registerPreMonthRobWarPoint" : "onRegisterPreMonthRobWarPoint", 	# 登记上月掠夺战积分
					  	"CalTongSalary": "onCalTongSalary",									# 计算帮会俸禄
					  	"ResetTongItem": "onResetTongItems",								# 重置帮会物品
					  	"ResetMemberBuyItemRecord" : "onResetMemberBuyItemRecord",			# 重置帮众购买帮会物品记录
					  	"resetTongQuest" : "onResetTongQuest",
					  	"ResetTongSpecialItems": "onResetTongSpecialItems",							# 重置帮会特殊商品
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		BigWorld.globalData["Crond"].addAutoStartScheme( "chargeSpendMoney", self, "onChargeSpendMoney" )
	
	def onCalTongSalary( self ):
		"""
		define method
		每周一零点计算帮会俸禄：保存上周俸禄值，清空本周俸禄
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.calTongSalary()

	def onResetTongItems( self ):
		"""
		define method
		每周定时重置帮会商人商品数据
		"""
		for databaseID, tongEntity in self._tongEntitys.iteritems():
			INFO_MSG( "TONG: %i reset tong items due to sys !" %databaseID )
			tongEntity.resetTongItems()
	

	def onResetMemberBuyItemRecord( self ):
		"""
		define method
		每周定时重置帮众购买帮会物品数据
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.resetMemberBuyItemRecord()
	
	def onChargeSpendMoney( self ):
		"""
		define method.
		收维护费
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.chargeSpendMoney()

	def onRegisterPreMonthRobWarPoint( self ):
		"""
		define method.
		登记上月掠夺战积分
		"""
		TongRobWarManager.onRegisterPreMonthRobWarPoint( self )
		
	#-----------------------------申请创建一个帮会-------------------------------------------------------------
	def checkTongName( self, tongName ):
		"""
		检查帮会的名称 合法则返回ture
		"""
		# 暂时未实现
		return True

	def createTong( self, tongName, creatorBase, creatorName, creatorDBID, creatorLevel, creatorRaceclass, reason ):
		"""
		define method.
		创建一个帮会  不可直接调用这里， 请调用cell.role.createTong
		@param tongName  : 帮会名称
		@param creatorBase   : 创建者的baseMailbox
		"""
		DEBUG_MSG( "createTong: tongName=%s, creatorName=%s" % ( tongName, creatorName ) )
		creatorND = creatorName + "(%s)" % creatorDBID
		
		if len( self._tongBaseDatas ) + len( self.tempCreateInfo ) >= csdefine.TONG_AMOUNT_MAX:
			creatorBase.cell.tong_checkCreateFail( csstatus.TONG_AMOUNT_MAX )
			return
		if self.hasTongName( tongName ):
			creatorBase.cell.tong_checkCreateFail( csstatus.TONG_NAME_EXIST )
			return
		if not self.checkTongName( tongName ): # 您输入的名称不合法。
			creatorBase.cell.tong_checkCreateFail( csstatus.TONG_NAME_INVALID )
			return

		# 这里开始创建帮会entity
		arg = {}
		arg[ "playerName" ] = tongName
		arg[ "tempMapping" ] = { "isCreate" : True }
		creatorInfo = { "databaseID":creatorDBID, \
						"playerName":creatorName, \
						"level":creatorLevel, \
						"raceclass":creatorRaceclass, \
						"baseMailbox":creatorBase, \
						}
		arg["creatorInfo"] = creatorInfo
		tongBase = BigWorld.createBaseLocally( "TongEntity", arg )

		if tongBase == None:
			ERROR_MSG( "player( %s ) create Tong failed!" % creatorName )
			# 给创建者一个回调通知
			creatorBase.client.onStatusMessage( csstatus.TONG_CREATE_FAIL, "(\'%s\',)" % tongName )
			return
			
		self.tempCreateInfo[creatorDBID] = ( tongName, time.time(), tongBase )
		if not self.clearTempCreateInfoTimerID:
			self.clearTempCreateInfoTimerID = self.addTimer( CLEAR_CREATE_TEMP_DATA_INTERVAL, CLEAR_CREATE_TEMP_DATA_INTERVAL )


	def onRegisterTongOnCreated( self, creatorDBID, baseTongEntity, tongName, tongDBID, chiefName, camp ):
		"""
		define method.
		注册这个创建的帮会实体
		"""
		# 获得一个新的帮会ID
		tid = self.getNewTongID()
		DEBUG_MSG( "create Tong:%s, id:%i is successfully!" % ( tongName, tid ) )
		if self.hasTong( tongDBID ):
			ERROR_MSG( "tong %s %i is exist" % ( tongName, tongDBID ) )
			return
		data =  {
					"chiefName"		: 		chiefName,
					"dbID"			:		tongDBID,
					"tid"			:		tid,
					"ad"			:		cschannel_msgs.TONG_INFO_17,
					"tongName"		:		tongName,
					"camp"			:		camp,
					"level"			: 		1,
					"jk_level"		: 		1,
					"ssd_level"		: 		1,
					"ck_level"		: 		1,
					"tjp_level"		: 		1,
					"sd_level"		: 		1,
					"yjy_level"		: 		1,
					"memberCount"	:		0,
					"prestige"		:		0,
					"holdCity"		: 		"",
					"leagues"		:		{},
					"tongTurnWarPoint":		[],
					"battleLeagues"	:		[],
				}
		self._tongBaseDatas[ tongDBID ] = data
		# 将这个帮会加入在线帮会记录中
		self._tongEntitys[ tongDBID ] = baseTongEntity
		# 设置帮会的id
		baseTongEntity.initTongIDAndAD( tid, data[ 'ad' ] )

		#这里仍然做一次数据库写入避免这时候服务器强制重起而上面给角色刚设置的
		#某些属性值没有来的及在一个tick存入数据库,造成的不可预料的错误
		self.writeToDB()
		del self.tempCreateInfo[creatorDBID]
		if len( self.tempCreateInfo ) == 0:
			self.delTimer( self.clearTempCreateInfoTimerID )
			self.clearTempCreateInfoTimerID = 0
		
		try:
			g_logger.tongCreateLog( tongDBID, tongName, creatorDBID,chiefName )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def onTongDismiss( self, tongDBID, reason ):
		"""
		define method.
		某个帮会被解散了，准备销毁它的相关数据
		"""
		TongTerritoryManager.onTongDismiss( self, tongDBID )
		TongCityWarManager.onTongDismiss( self, tongDBID )
		TongTurnWarManager.onTongDismiss( self, tongDBID )
		if tongDBID in self._tongBaseDatas:
			tongInfo = self._tongBaseDatas[ tongDBID ]
			self._tongEntitys.pop( tongDBID )
			self.delTongInTongBaseDatas( tongDBID )
			self.writeToDB() 										# 及时保存
			try:
				g_logger.tongDismissLog( tongDBID, tongInfo['tongName'], None )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return

	#------------------------------------------------------------------------------------------
	def getNewTongID( self ):
		"""
		获取一个新的帮会ID
		"""
		tids = []
		for item in self._tongBaseDatas.itervalues():
			tids.append( item[ "tid" ] )

		# 这里预留这么多个ID， 即使合并服务器也用不完
		for tid in xrange( 1, 1000000 ):
			if tid not in tids:
				return tid

		return 0

	#------------------------------------------------------------------------------------------
	def findTongByName( self, tongName ):
		"""
		通过帮会名称找到他的mailbox
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tongName" ] == tongName:
				return self.findTong( item[ "dbID" ] )
		return None

	def findTongByTID( self, tid ):
		"""
		通过帮会id找到他的mailbox
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tid" ] == tid:
				return self.findTong( item[ "dbID" ] )
		return None

	def hasTongName( self, tongName ):
		"""
		是否有一个此帮会名称的帮会存在
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tongName" ] == tongName:
				return True
		for item in self.tempCreateInfo.itervalues():
			if item[0] == tongName:	# 和正在创建中的帮会同名
				return True
		return False

	def hasTongID( self, tid ):
		"""
		是否有一个此帮会id的帮会存在
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tid" ] == tid:
				return True
		return False

	def hasTong( self, tongDBID ):
		return tongDBID in self._tongBaseDatas

	def hasTongEntity( self, tongDBID ):
		"""
		是否有一个此帮会dbid的帮会存在
		"""
		return tongDBID in self._tongEntitys

	def findTong( self, tongDBID ):
		"""
		是否有一个此帮会dbid的帮会存在
		"""
		if not self.hasTongEntity( tongDBID ):
			return None
		return self._tongEntitys[ tongDBID ]

	def getTongNameByDBID( self, tongDBID ):
		"""
		通过帮会DBID获取帮会名称
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ "tongName" ]
		return ""

	def getTongDBIDByName( self, tongName ):
		"""
		通过帮会DBID获取帮会名称
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tongName" ] == tongName:
				return item[ "dbID" ]
		return 0
		
	def getTongSignMD5ByDBID( self, tongDBID ):
		"""
		通过帮会DBID获取帮会会标MD5 by 姜毅
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ "tongSignMD5" ]
		return ""
	
	def getTongCampByDBID( self, tongDBID ):
		"""
		通过帮会DBID获取帮会的阵营
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ "camp" ]
			
		return 0

	#------------------------------------------------------------------------------------------
	def save( self ):
		"""
		服务器将要重启
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.save()
		self.writeToDB()

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
	def onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		成员登陆通知
		"""
		TongRobWarManager.onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID )
		TongFeteManager.onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onMemberLogin( baseEntity, baseEntityDBID )
		else:
			if not self.hasTong( tongDBID ):
				ERROR_MSG( "%i:tong %i not exist." % ( baseEntity.id, tongDBID ) )
				baseEntity.tong_reset()		# 如果帮会已经不存在，则清理玩家帮会相关的数据
			else:
				d = {}
				d[ "dbid" ] = baseEntityDBID
				d[ "baseEntity" ] = baseEntity
				if self._enterTongMembers_temp.has_key( tongDBID ):
					self._enterTongMembers_temp[ tongDBID ].append( d )
				else:
					self._enterTongMembers_temp[ tongDBID ] = [d]
					self.loadTongByDBIDFromDB( tongDBID )

	def onMemberLogoutTong( self, tongDBID, baseEntityDBID ):
		"""
		define method.
		成员下线通知
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onMemberLogout( baseEntityDBID )
		else:
			ERROR_MSG( "%i:tong %i not exist." % ( baseEntityDBID, tongDBID ) )

	def addPrestige( self, tongDBID, prestige ):
		"""
		define method.
		添加声望
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.addPrestige( prestige, csdefine.TONG_PRESTIGE_CHANGE_REST )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def onRequestTongLeague( self, userDBID, userTongDBID, requestTongName ):
		"""
		define method.
		邀请帮会同盟
		"""
		requestTongDBID = 0
		for t in self._tongBaseDatas.itervalues():
			if t["tongName"] == requestTongName:
				requestTongDBID = t[ 'dbID' ]

		tongEntity = self.findTong( userTongDBID )
		if tongEntity:
			tongEntity.onRequestTongLeague( userDBID, requestTongDBID, requestTongName )
		else:
			ERROR_MSG( "tong %i not exist." % ( userTongDBID ) )


	def requestTongLeague( self, user, userTongDBID, requestTongName ):
		"""
		define method.
		邀请帮会同盟
		@param user				:使用功能者baseMailbox
		@param userTongDBID		:使用功能者 帮会的DBID
		@param requestTongName	:要邀请的目标帮会名称
		"""
		if not self.hasTongName( requestTongName ):
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_NO_FIND )
			return

		tong = self.findTongByName( requestTongName )
		tongName = ""
		item = self._tongBaseDatas.get( userTongDBID )
		if item:
			tongName = item[ 'tongName' ]

		if tong:
			tong.requestTongLeague( user, tongName, userTongDBID )
		else:
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_CHIEF_OFFLINE )

	def onRequestTongLeagueFailed( self, userTongDBID, targetTongDBID ):
		"""
		define method.
		邀请同盟在对方帮会entity中失败了（可能是帮主不在线）做个回调
		"""
		tongEntity = self.findTong( userTongDBID )
		if tongEntity:
			tongEntity.onRequestTongLeagueFailed( targetTongDBID )
		else:
			ERROR_MSG( "tong %i not exist." % ( userTongDBID ) )

	def answerRequestTongLeague( self, memberBaseEntity, memberTongDBID, agree, requestByTongDBID ):
		"""
		define method.
		对方回答了我的邀请
		"""
		tongEntity = self.findTong( requestByTongDBID )
		if tongEntity:
			tongEntity.answerRequestTongLeague( memberBaseEntity, self.findTong( memberTongDBID ), memberTongDBID, agree )
		else:
			ERROR_MSG( "tong %i not exist." % ( requestByTongDBID ) )

	def onLeagueDispose( self, tongDBID, leagueTongDBID ):
		"""
		define method.
		收到对方帮会与我脱离了同盟关系
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onLeagueDispose( leagueTongDBID )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def leagueDispose( self, tongDBID, leagueTongDBID ):
		"""
		define method.
		一个帮会通知同盟帮会 解除同盟关系，  可能是由帮会解散导致的
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.leagueDispose( -1, leagueTongDBID )
		else:
			if not self.hasTong( tongDBID ):
				ERROR_MSG( "%i:tong %i not exist." % ( tongDBID, leagueTongDBID ) )
			else:
				cmd = "DELETE from tbl_TongEntity_leagues where sm_dbID=%i;" % leagueTongDBID
				BigWorld.executeRawDatabaseCommand( cmd )

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if timerID == self.loadAllTongTimerID:
			self.onLoadAllTongTimer()
		elif timerID == self.clearTempCreateInfoTimerID:
			for creatorDBID, info in self.tempCreateInfo.items():
				if time.time() - info[1] > CLEAR_CREATE_TEMP_DATA_INTERVAL:	# 建立帮会超时了，删除帮会entity
					tempInfo = self.tempCreateInfo.pop( creatorDBID )
					tempInfo[2].destroy( deleteFromDB = True )				# 创建帮会entity时会写入db，超时要从db中删除
					ERROR_MSG( "player( %i ) create tong( %s ) failed." % ( creatorDBID, tempInfo[0] ) )
			if len( self.tempCreateInfo ) == 0:	# 如果没有数据那么停掉timer
				self.delTimer( self.clearTempCreateInfoTimerID )
				self.clearTempCreateInfoTimerID = 0
		else:
			TongCityWarManager.onTimer( self, timerID, cbID )
			TongTerritoryManager.onTimer( self, timerID, cbID )
			TongRobWarManager.onTimer( self, timerID, cbID )
			TongFeteManager.onTimer( self, timerID, cbID )
			TongAbattoirMgr.onTimer( self, timerID, cbID )
			TongFengHuoLianTianMgr.onTimer( self, timerID, cbID )
			TongCityWarFinalManager.onTimer( self, timerID, cbID )

	def onRegisterTerritory( self, tongDBID, territory ):
		"""
		define method.
		@param tongDBID: 帮会DBID
		@param territory:领地副本的basemailbox
		"""
		TongTerritoryManager.onRegisterTerritory( self, tongDBID, territory )
		TongRobWarManager.onRegisterTerritory( self, tongDBID, territory )

	def requestTongItems( self, tongDBID, chapmanBase ):
		"""
		define method.
		帮会商人被创建后向帮会获取帮会物品数据
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onChapmanRequestItems( chapmanBase )
		else:
			DEBUG_MSG( "tong %i not exist or offline." % ( tongDBID ) )

	def onSellItems( self, tongDBID, roleDBID, itemID, amount ):
		"""
		define method.
		帮会物品被出售了
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onSellItems( roleDBID, itemID, amount )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def onCappaign_monsterRaidComplete( self, tongDBID ):
		"""
		define method.
		魔物来袭 活动帮会已经完成
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onCappaign_monsterRaidComplete()
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def onProtectTongStart( self, tongDBID, protectType ):
		"""
		define method.
		保护帮派活动开始了
		"""
	  	territory = self.findTerritoryByTongDBID( tongDBID )
	  	if territory:
	  		territory.onProtectTongStart( protectType )

	def onProtectTongEnd( self, tongDBID ):
		"""
		define method.
		保护帮派活动结束了
		"""
	  	territory = self.findTerritoryByTongDBID( tongDBID )
	  	if territory:
	  		territory.onProtectTongEnd()

	#------------------------------------------------------------------------------------------
	def loadAllTongBaseDatas( self ):
		"""
		加载所有帮会的基础数据
		"""
		sqlcmd = "select id, sm_level, sm_jk_level, sm_ssd_level, sm_ck_level, sm_tjp_level, sm_sd_level, sm_yjy_level, sm_memberCount, sm_prestige, sm_playerName, sm_camp, sm_tongSignMD5, sm_tid, sm_ad from tbl_TongEntity;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 0 ) )
		sqlcmd = "select parentID, sm_dbID, sm_tongName from tbl_TongEntity_leagues;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 1 ) )
		sqlcmd = "select parentID, sm_cityName, sm_point from tbl_TongEntity_tongTurnWarPoint;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 2 ) )
		sqlcmd = "select parentID, sm_dbID from tbl_TongEntity_battleLeagues;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 3 ) )

	def queryAllTongBaseData_Callback( self, queryType, result, dummy, error ):
		"""
		查询所有帮会基础数据 数据库回调
		"""
		if ( error ):
			ERROR_MSG( error )
			return

		if queryType == 0:	# 查询基础数据
			for r in result:
				tongDBID 		= int( r[ 0 ] )
				datas = self._tongBaseDatas.get( tongDBID )

				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas
					
				datas[ "dbID" ] 			= int( r[ 0 ] )
				datas[ "level" ] 			= int( r[ 1 ] )
				datas[ "jk_level" ] 		= int( r[ 2 ] )
				datas[ "ssd_level" ] 		= int( r[ 3 ] )
				datas[ "ck_level" ] 		= int( r[ 4 ] )
				datas[ "tjp_level" ] 		= int( r[ 5 ] )
				datas[ "sd_level" ] 		= int( r[ 6 ] )
				datas[ "yjy_level" ] 		= int( r[ 7 ] )
				datas[ "memberCount" ]		= int( r[ 8 ] )
				datas[ "prestige" ]			= int( r[ 9 ] )
				datas[ "tongName" ] 		= r[ 10 ]
				datas[ "camp" ] 			= int( r[ 11 ] )
				datas[ "tongSignMD5" ]		= r[ 12 ]
				datas[ "tid" ] 				= int( r[ 13 ] )
				datas[ "ad" ] 				= r[ 14 ]
				
				# 帮会被加载后会向管理器更新以下信息
				datas[ "holdCity" ]			= ""
				datas[ "chiefName" ] 		= ""
				
				# 防止某些帮会没有联盟 无论如何我们先进行初始化
				if not datas.has_key( "leagues" ):
					datas[ "leagues" ] = {}
					
				# 帮会车轮战积分信息
				if not datas.has_key( "tongTurnWarPoint" ):
					datas[ "tongTurnWarPoint" ] = []
				
				# 战争结盟帮会
				if not datas.has_key( "battleLeagues" ):
					datas[ "battleLeagues" ] = []
			
			# 开始创建所有帮会entity
			self.tmpTongInfos = self._tongBaseDatas.keys()
			self.loadAllTongTime = time.time()
			self.loadAllTongTimerID = self.addTimer( 0, 0.1, 0 )			# 开启加载帮会的timer
			self.onManagerInitOver()
		elif queryType == 1:	# 查询联盟数据
			for r in result:
				tongDBID 		= int( r[ 0 ] )
				datas = self._tongBaseDatas.get( tongDBID )

				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas

				leagues = datas.get( "leagues" )
				if not leagues:
					leagues = {}	# { tongDBID:tongName }
					self._tongBaseDatas[ tongDBID ][ "leagues" ] = leagues

				leagues[  int( r[ 1 ] )  ] = r[ 2 ]
		elif queryType == 2:	# 查询车轮战积分
			for r in result:
				tongDBID = int( r[0] )
				datas = self._tongBaseDatas.get( tongDBID )
				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas
					
				tongTurnWarPoint = datas.get( "tongTurnWarPoint" )
				if not tongTurnWarPoint:
					self._tongBaseDatas[ tongDBID ][ "tongTurnWarPoint" ] = []		# [ { "cityName", "point" } ]
				
				info = { "cityName": r[1], "point": int( r[2] ) }
				self._tongBaseDatas[ tongDBID ][ "tongTurnWarPoint" ].append( info )
				TongTurnWarManager.updateTurnWarTopTable( self, tongDBID, r[1], int( r[2] ) )
		elif queryType == 3:				# 查询战争联盟数据
			for r in result:
				tongDBID 		= int( r[ 0 ] )
				datas = self._tongBaseDatas.get( tongDBID )

				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas

				battleLeagues = datas.get( "battleLeagues" )
				if not battleLeagues:
					battleLeagues = []		# [ tongDBID, tongDBID ]
					self._tongBaseDatas[ tongDBID ][ "battleLeagues" ] = battleLeagues
				
				battleLeagues.append(  int( r[ 1 ] ) )

	def getTongAD( self, tongDBID ):
		"""
		获取某帮会的广告
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ 'ad' ]
		return ""

	def requestTongList( self, playerBase, index, camp = 0 ):
		"""
		define method.
		某个玩家申请获取帮会列表
		@param index: 客户端向服务器申请的批次
		"""
		for idx in xrange( index, index + 5  ):
			if len( self._tongBaseDatas ) < idx + 1:
				playerBase.client.tong_receiveTongListCompleted()
				break

			t = self._tongBaseDatas.values()[ idx ]
			tongDBID = t["dbID"]
			tongName = t[ 'tongName']
			tongID = t[ 'tid' ]

			if tongDBID in self._tongBaseDatas:
				if camp and self.getTongCampByDBID( tongDBID ) != camp:
					continue
				prestige = self._tongBaseDatas[ tongDBID ][ "prestige" ]
				holdCity = self._tongBaseDatas[ tongDBID ][ "holdCity" ]
				level = self._tongBaseDatas[ tongDBID ][ "level" ]
				playerBase.client.tong_onReceiveTongList( tongDBID, tongName, tongID, level, prestige, len( holdCity ) > 0 )

	def queryTongInfo( self, playerBase, tongDBID ):
		"""
		define method.
		查询某个帮会的信息
		"""
		holdCity 		= self._tongBaseDatas[ tongDBID ][ "holdCity" ]
		memberCount 	= self._tongBaseDatas[ tongDBID ][ "memberCount" ]
		chiefName 		= self._tongBaseDatas[ tongDBID ][ "chiefName" ]
		leagues 		= self._tongBaseDatas[ tongDBID ][ "leagues" ].values()
		ad 				= self.getTongAD( tongDBID )

		# 返回给客户端帮会的信息
		playerBase.client.tong_onReceiveTongInfo( tongDBID, memberCount, chiefName, holdCity, leagues, ad )

	def setTongAD( self, playerBase, tongDBID, strAD ):
		"""
		define method.
		设置帮会广告
		@param strAD: 帮会广告
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			item[ 'ad' ] = strAD
			self.findTong( tongDBID ).setAD( strAD )

	def delTongInTongBaseDatas( self, tongDBID ):
		"""
		从帮会基本数据里删除某个帮会
		"""
		self._tongBaseDatas.pop( tongDBID )

	def updateTongLevel( self, tongDBID, level ):
		"""
		define method.
		更新帮会级别
		"""
		self._tongBaseDatas[ tongDBID ][ "level" ] = level

	def updateTongChiefName( self, tongDBID, chiefName ):
		"""
		define method.
		更新帮主
		"""
		self._tongBaseDatas[ tongDBID ][ "chiefName" ] = chiefName
		TongCityWarManager.updateTongChiefName( self, tongDBID )

	def updateTongMemberCount( self, tongDBID, memberCount ):
		"""
		define method.
		更新帮会成员数量
		"""
		if tongDBID not in self._tongBaseDatas:
			self._tongBaseDatas[ tongDBID ] = { "memberCount" : memberCount }
			return

		self._tongBaseDatas[ tongDBID ][ "memberCount" ] = memberCount

	def updateTongHoldCity( self, tongDBID, holdCity ):
		"""
		define method.
		更新帮会占领城市
		"""
		self._tongBaseDatas[ tongDBID ][ "holdCity" ] = holdCity

	def updateTongPrestige( self, tongDBID, prestige ):
		"""
		define method.
		更新帮会声望
		"""
		self._tongBaseDatas[ tongDBID ][ "prestige" ] = prestige

	def updateTongBuildingLevel( self, tongDBID, jk_level, ssd_level, ck_level, tjp_level, sd_level, yjy_level ):
		"""
		define method.
		更新帮会建筑级别
		"""
		self._tongBaseDatas[ tongDBID ][ "jk_level" ] = jk_level
		self._tongBaseDatas[ tongDBID ][ "ssd_level" ] = ssd_level
		self._tongBaseDatas[ tongDBID ][ "ck_level" ] = ck_level
		self._tongBaseDatas[ tongDBID ][ "tjp_level" ] = tjp_level
		self._tongBaseDatas[ tongDBID ][ "sd_level" ] = sd_level
		self._tongBaseDatas[ tongDBID ][ "yjy_level" ] = yjy_level

	def updateTongLeagues( self, tongDBID, leagues ):
		"""
		define method.
		更新帮会同盟
		"""
		datas = {}
		self._tongBaseDatas[ tongDBID ][ "leagues" ] = datas

		for league in leagues:
			datas[ league[ "dbID" ] ] = league[ "tongName" ]

	def changeTongName( self, playerBase, tongDBID, newName ):
		"""
		Define method.
		帮会改名。

		"""
		if self.hasTongName( newName ):
			playerBase.client.onStatusMessage( csstatus.TONG_NAME_EXIST, "" )
			return
		tongBase = self.findTong( tongDBID )
		if tongBase is None:
			DEBUG_MSG( "cannot find tong( tongDBID:%i ) base." % tongDBID )
			return

		tongBase.changeName( newName )
		self._tongBaseDatas[tongDBID]["tongName"] = newName
		playerBase.client.onStatusMessage( csstatus.TONG_RENAME_SUCCEED, "" )


	def onActivityLogHandle( self ):
		"""
		define method
		统计帮会相关活动日志
		"""
		try:
			g_logger.countTongNumLog( len( self._tongBaseDatas ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def memberNameChanged( self, dbid, playerDBID, newName ):
		"""
		define method
		角色名字被改变了
		"""
		tongEntity = self.findTong( dbid )
		if tongEntity:
			tongEntity.onMemberNameChanged( playerDBID, newName )

	def updateTongExp( self, tongDBID, exp ):
		"""
		define method.
		更新帮会经验
		"""
		self._tongBaseDatas[ tongDBID ][ "EXP" ] = exp
		
#------------------------------------------------------------
#六王墓
#------------------------------------------------------------		
	def findChiefNameByTongName(self, type, index, tongName):
		#define method, used in LiuWangMuMgr
		tongDBID = self.getTongDBIDByName(tongName)
		chiefName = self._tongBaseDatas[tongDBID]["chiefName"]
		BigWorld.globalData["LiuWangMuMgr"].sendLiuWangMuRewardToTongChief(type, index,  tongName, chiefName)

			
#----------------------------------------------------------------------
# 帮会运镖相关
#----------------------------------------------------------------------
	def onResetTongQuest( self ):
		"""
		define method
		关闭帮会运镖任务
		"""
		for tongEntity in self._tongEntitys.values():
			tongEntity.resetTongQuest()
#---------------------------------------------------------------------
# 帮会赛马相关
#---------------------------------------------------------------------
	def onTongRaceOver( self, tongDBID ):
		"""
		define method
		帮会赛马结束
		"""
		tongMB = self.findTong( tongDBID )
		if tongMB:
			tongMB.onTongRaceOver()

	#-----------------------------战争结盟-------------------------------------------
	def reqOpenBattleLeaguesWindow( self, playerBase, camp, spaceName ):
		"""
		define method
		玩家请求打开战争结盟界面
		"""
		tongRecord = self.getQuarterFinalRecord( camp, spaceName )
		if len( tongRecord ) == 0:
			self.statusMessage( playerBase, csstatus.TONG_BATTLE_LEAGUE_SPECIFIC_TIME )
			return
		
		playerBase.client.tong_openTongBattleLeagueWindow( tongRecord )
	
	def queryTongBattleLeagues( self, playerBase, index, camp, spaceName ):
		"""
		define method
		查询战争同盟信息
		"""
		for idx in xrange( index, index + 5  ):
			if len( self._tongBaseDatas ) < idx + 1:
				playerBase.client.tong_receiveBattleLeagueCompleted()
				break

			t = self._tongBaseDatas.values()[ idx ]
			tongDBID = t[ "dbID" ]
			tongCamp = t[ 'camp' ]

			tongRecords = self.getQuarterFinalRecord( camp )					# 同阵营的所有可参赛的帮会，来自烽火连天的结果
			qualifiedTong = self.getQuarterFinalRecord( camp, spaceName )		# 当前城市的可参赛帮会
			if tongDBID not in qualifiedTong and tongDBID in tongRecords:
				continue
			
			if tongDBID in self._tongBaseDatas:
				if camp and tongCamp != camp:
					continue
				tongName = t[ 'tongName' ]
				battleLeagues = t[ "battleLeagues" ]
				
				playerBase.client.tong_receiveBattleLeagues( tongDBID, tongName, camp, battleLeagues )

	def getTongBattleLeagueMaxNum( self, tongDBID ):
		"""
		获取帮会可邀请战争结盟的最大数量（第一名可邀请一个，第二名可邀请两个）
		"""
		tongRecord = self.getQuarterFinalRecord( 0 )
		if tongDBID in tongRecord.keys():
			return tongRecord[ tongDBID ]
		return 1

	def inviteTongBattleLeague( self, inviterDBID, inviterBase, inviterTongDBID, inviteeTongDBID, msg ):
		"""
		define method
		邀请帮会战争同盟
		"""
		# 条件判断
		if len( self.cityWarFinalInfos ) == 0:
			self.statusMessage( inviterBase, csstatus.TONG_BATTLE_LEAGUE_SPECIFIC_TIME )
			return
		
		# 双方敌对帮会，不能战争结盟
		tongRecord = self.getQuarterFinalRecord( 0 )
		if ( inviterTongDBID in tongRecord.keys() ) and ( inviteeTongDBID in tongRecord.keys() ):
			self.statusMessage( inviterBase, csstatus.TONG_BATTLE_LEAGUE_NOT_ENEMY )
			return
		
		# 必须有一方有参赛资格
		if ( inviterTongDBID not in tongRecord.keys() ) and ( inviteeTongDBID not in tongRecord.keys() ):
			self.statusMessage( inviterBase, csstatus.TONG_BATTLE_LEAGUE_NOT_QUALIFIED )
			return
		
		tongEntity = self.findTong( inviterTongDBID )
		if not tongEntity:
			RROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		maxNum = self.getTongBattleLeagueMaxNum( inviterTongDBID )
		tongEntity.inviteTongBattleLeague( inviterDBID, inviteeTongDBID, msg, maxNum )

	def onInviteTongBattleLeague( self, inviter, inviterTongDBID, inviteeTongDBID, msg ):
		"""
		define method
		邀请帮会战争同盟，已通过邀请方帮会验证 第四步
		@param inviter				:邀请者baseMailbox
		@param inviterTongDBID		:邀请者帮会的DBID
		@param inviteeTongDBID		:被邀请帮会的DBID
		"""
		if not self.findTong( inviterTongDBID ):
			self.statusMessage( inviter, csstatus.TONG_TARGET_TONG_NO_FIND )
			return
		inviteeTong = self.findTong( inviteeTongDBID )
		inviterTongName = self._tongBaseDatas[inviterTongDBID]["tongName"]
		
		if not inviteeTong:
			ERROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		maxNum = self.getTongBattleLeagueMaxNum( inviteeTongDBID )
		inviteeTong.receiveBattleLeagueInvitation( inviter, inviterTongName, inviterTongDBID, msg, maxNum )

	def onInviteTongBattleLeagueFailed( self, inviterTongDBID, inviteeTongDBID ):
		"""
		define method
		邀请战争同盟失败回调（可能是被邀请方帮主不在线）
		"""
		inviterTong = self.findTong( inviterTongDBID )
		if not inviterTong:
			ERROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		inviterTong.onRequestTongLeagueFailed( inviteeTongDBID )

	def replyBattleLeagueInvitation( self, replierBaseMailbox, replierTongDBID, inviterTongDBID, response ):
		"""
		define method
		收到被邀请帮会回复
		"""
		inviterTong = self.findTong( inviterTongDBID )
		replierTong = self.findTong( replierTongDBID )
		replierTongName = self._tongBaseDatas[replierTongDBID]["tongName"]
		if not inviterTong:
			ERROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		inviterTong.receiveBattleLeagueReply( replierBaseMailbox, replierTong, replierTongDBID, replierTongName, response )

	def updateTongBattleLeagues( self, tongDBID, leagues ):
		"""
		define method
		更新战争同盟
		"""
		if tongDBID in self._tongBaseDatas[ tongDBID ][ "battleLeagues" ]:
			return
		
		for league in leagues:
			if league[ "dbID" ] in self._tongBaseDatas[ tongDBID ][ "battleLeagues" ]:
				continue
			self._tongBaseDatas[ tongDBID ][ "battleLeagues" ].append( league[ "dbID" ] )

	def requestBattleLeagueDispose( self, userDBID, userBaseEntity, userTongDBID, battleLeagueDBID ):
		"""
		define method
		申请解除战争结盟关系
		"""
		if BigWorld.globalData.has_key( "AS_TONG_CITY_WAR_FINAL"):	# 活动期间，不能解除结盟关系
			self.statusMessage( userBaseEntity, csstatus.TONG_BATTLE_LEAGUE_DISPOSE_NOT_ALLOW )
			return
		
		userTong = self.findTong( userTongDBID )
		if not userTong:
			ERROR_MSG( "TONG: tong %i not exist." % ( tongDBID ) )
			return
		userTong.requestBattleLeagueDispose( userDBID, battleLeagueDBID )

	def onBattleLeagueDispose( self, tongDBID, leagueTongDBID ):
		"""
		define metdho
		一个帮会通知战争同盟帮会解除同盟关系
		"""
		tongEntity = self.findTong( tongDBID )
		if not tongEntity:
			ERROR_MSG( "TONG: tong %i is not exist." % ( tongDBID ) )
			return
		tongEntity.battleLeagueDispose( leagueTongDBID )

	def battleLeagueAutoDispose( self,  tongDBID, battleLeagueDBID ):
		"""
		define mtehod
		自动解除战争同盟关系（同盟帮会解散导致）
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.requestBattleLeagueDispose( -1, battleLeagueDBID )
		else:
			if not self.hasTong( tongDBID ):
				ERROR_MSG( "TONG: %i 's tong battleLeagues  %i is not exist." % ( tongDBID, battleLeagueDBID ) )
			else:
				cmd = "DELETE from tbl_TongEntity_battleLeagues where sm_dbID=%i;" % battleLeagueDBID
				BigWorld.executeRawDatabaseCommand( cmd )

	def getBattleLeagueByTongDBID( self, tongDBID ):
		"""
		define method
		根据帮会DBID获得其同盟帮会
		"""
		return self._tongBaseDatas[tongDBID]["battleLeagues"]

	# --------------------------------------------------------------
	# 帮会特殊商城
	# --------------------------------------------------------------
	def requestTongSpecialItems( self, tongDBID, chapmanBase ):
		"""
		define method.
		帮会特殊商人被创建后向帮会获取帮会物品数据
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onChapmanRequestSpecialItems( chapmanBase )
		else:
			DEBUG_MSG( "tong %i not exist or offline." % ( tongDBID ) )

	def onResetTongSpecialItems( self ):
		"""
		define method
		每周定时重置帮会商人商品数据
		"""
		for databaseID, tongEntity in self._tongEntitys.iteritems():
			INFO_MSG( "TONG: %i reset tong items due to sys !" %databaseID )
			tongEntity.resetTongSpecialItems()

	def onSellSpecialItems( self, tongDBID, playerBase, memberDBID, itemID, amount ):
		"""
		define method.
		帮会特殊物品被出售
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onSellSpecialItems( playerBase, memberDBID, itemID, amount )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )
	
	def buyTongSpecialArrayFromNPC( self, chapmanBase, tongDBID, playerDBID, memberDBID, invoiceIDs, argAmountList ):
		"""
		帮会购买特殊商品
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.buyTongSpecialArrayFromNPC( chapmanBase, playerDBID, memberDBID, invoiceIDs, argAmountList )
#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/08/07 07:10:40  phw
# BigWorld.base() -> BigWorld.createBaseLocally()
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
# Revision 1.5  2008/06/24 01:49:52  kebiao
# 修改了一个异步加载可能存在的一个BUG
#
# Revision 1.4  2008/06/23 08:11:31  kebiao
# 增加某些地方的数据库及时更新
# 某些在线成员属性值没有来的及在一个tick存入数据库,
# 而不在线成员的值却被写入造成的不可预料的错误
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