# -*- coding: gb18030 -*-
#
# $Id: Role.py,v 1.119 2008-09-05 03:50:30 zhangyuxing Exp $


"""
玩家角色的Base部分。

"""

# python
import sys
import _md5
import time
import cPickle
import random
# 引擎
import BigWorld

# common
import Language
import csstatus
import csdefine
import csconst
import Const
from AbstractTemplates import MultiLngFuncDecorator

# base
import cschannel_msgs
import ShareTexts as ST
import Love3
import CrondDatas
import ECBExtend
import RoleMatchRecorder
import items

# Role 的基类
from interface.GameObject import GameObject
from ECBExtend import ECBExtend as BaseECBExtend
from OPRecorder import OPRecorder
from interface.QuickBar import QuickBar
from interface.RoleChat import RoleChat
from interface.Team import Team
from interface.Bank import Bank
from interface.RoleImageVerify import RoleImageVerify
from interface.SpaceFace import SpaceFace
from interface.PostInterface import PostInterface
from interface.PetCage import PetCage
from interface.RoleMail import RoleMail
from interface.RoleRelation import RoleRelation
from interface.ItemsBag import ItemsBag
from interface.TongInterface import TongInterface
from interface.RoleCredit import RoleCredit
from interface.AntiWallow import AntiWallow
from interface.RoleSpecialShop import RoleSpecialShop
from interface.RoleGem import RoleGem
from interface.RoleQuizGame import RoleQuizGame
from interface.PresentChargeUnite import PresentChargeUnite
from interface.GameRanking import GameRanking
from interface.LivingSystem import LivingSystem
from interface.YuanBaoTradeInterface import YuanBaoTradeInterface
from interface.CopyMatcherInterface import CopyMatcherInterface
from interface.RoleCampInterface import RoleCampInterface
from interface.ZhengDaoInterface import ZhengDaoInterface
from interface.Fisher import Fisher

from config.VehicleUpStep import Datas as U_DATA

# from 形式的 import
from bwdebug import *
from Function import Functor
from OnlineRewardMgr import OnlineRewardMgr
from PointCardInfo import PointCardInfo
from MsgLogger import g_logger
from ItemAwards import ItemAwards

g_items = items.instance()
g_onlineReward = OnlineRewardMgr.instance()

class languageDepart_AFTimer( MultiLngFuncDecorator ):
	"""
	多语言版本的内容区分 by 姜毅
	"""
	@staticmethod
	def locale_big5( role ):
		"""
		繁体版
		"""
		languageDepart_AFTimer.originalFunc( role )
		isoverday = role.checkOverDay()
		if isoverday:
			role.af_time_limit = int( Const.AUTO_FIGHT_PERSISTENT_TIME_TW )
			role.client.onAFLimitTimeChanged( role.af_time_limit )
		today0tick = role.getToday0Tick()
		leftTime = ( today0tick + 86400 - int( time.time() ) )
		INFO_MSG( "Role charge auto fight time. Is over day:%s, today 0 tick:%s ,left time:%s, auto fight time:%s, last offline:%s."%( isoverday, today0tick, leftTime, role.af_time_limit, role.role_last_offline ) )
		role.AFTimer = role.addTimer( leftTime, 0.0, ECBExtend.ROLE_AF_TIME_CHARGE )	# 以整数化的时间作为参数

class Role(
	BigWorld.Proxy,						#
	GameObject,							#
	BaseECBExtend,						# 扩展的onTimer机制
	OPRecorder,							# 客户端操作记录( hyw )
	QuickBar,							# 快捷栏( wanhaipeng )
	RoleChat,							# 消息( hyw )
	Team,								# 组队
	Bank,								# 钱庄( wsf )
	RoleImageVerify,
	SpaceFace,							# 空间管理(pck)
	PostInterface,						# 邮件系统(pck)
	PetCage,							# 宠物
	RoleMail,							# 邮件系统(zyx)
	RoleRelation,						# 玩家关系( wsf )
	ItemsBag,							# 背包( phw )
	TongInterface,						# 帮会系统(kebiao)
	RoleCredit,							# 处理玩家信誉( wangshufeng )
	AntiWallow,						# 防沉迷系统
	RoleSpecialShop,					# 角色商城(wangshufeng & huangyongwei)
	RoleGem,							# 角色经验石( wsf )
	RoleQuizGame,						# 角色知识问答( wsf )
	PresentChargeUnite,					# 奖品和充值领取模块( hd )
	GameRanking,						# 排行榜系统
	LivingSystem,						# 生活系统( jy )
	YuanBaoTradeInterface,				# 元宝交易( jy )
	CopyMatcherInterface,				# 副本组队系统方法接口
	RoleCampInterface, 					# 阵营
	ZhengDaoInterface,					# 证道系统
	Fisher,								# 捕鱼达人
	):
	"""
	玩家角色Base部分。
	@ivar 		spaceManager :	场景管理器Mailbox，供场景转换时使用
	@type 		spaceManager :	mailbox
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		INFO_MSG("now init base role  %s..............." % self.cellData["playerName"] )
		# 基本模块
		BigWorld.Proxy.__init__( self )
		BaseECBExtend.__init__( self )
		OPRecorder.__init__( self )
		TongInterface.__init__( self )
		RoleCredit.__init__( self )
		AntiWallow.__init__( self )
		# 基本初始化
		self.spaceManager = BigWorld.globalData["SpaceManager"]

		# 基本模块2
		Team.__init__( self )
		RoleChat.__init__ ( self )

		INFO_MSG("now init base role  %s datas..............." % self.cellData["playerName"] )
		# 扩展模块
		Bank.__init__( self )
		RoleImageVerify.__init__( self )
		SpaceFace.__init__( self )
		PostInterface.__init__( self )
		PetCage.__init__( self )
		RoleMail.__init__( self )
		RoleRelation.__init__( self )
		ItemsBag.__init__( self )
		RoleGem.__init__( self )
		RoleQuizGame.__init__( self )
		PresentChargeUnite.__init__( self )
		GameRanking.__init__( self )
		LivingSystem.__init__( self )
		YuanBaoTradeInterface.__init__( self )
		CopyMatcherInterface.__init__( self )
		RoleCampInterface.__init__( self )
		ZhengDaoInterface.__init__( self )

		# 快捷栏
		QuickBar.__init__( self )

		Fisher.__init__( self )

		# 临时数据
		self._lasttime = BigWorld.time()

		self._isLogout = False						# 表示自己是否为被注销,如果是则会被送回角色选择界面

		self.frozenGold = 0			# 被冻结的金元宝
		self.frozenSilver = 0		# 被冻结的银元宝

		# 用于标识玩家的物品数据是否有效
		# 如果无效则会在onClientGetCell()的时候把玩家踢出
		self.validItemData = True

		# 如果MD5校验失败则会在onClientGetCell()时候把玩家提出
		self.validMD5Check = True

		# 初始化部份cellData
		# 如果entity没有存到db中，则databaseID为0，
		# 但以现在的创建、登录机制来说，应该不会出现此情况
		# 现在的机制是创建一个entity后直接被saveToDB()并destroy()；
		self.cellData["databaseID"] = self.databaseID

		# 复制用户名和等级
		self.playerName = self.cellData["playerName"]
		self.level = self.cellData["level"]
		self.raceclass = self.cellData["raceclass"]
		self.grade = self.cellData["grade"]
		self.headTextureID = self.cellData["headTextureID"]
		self.last_login_ip = 0		#初始化登陆IP

		# 反外挂验证数据，16:04 2009-11-12，wsf
		self.antiRobotTime = time.time() + 600		# 最近一次验证时间，玩家上线10分钟后才开始验证
		self.antiRobotCount = 0		# 第几次验证
		self._tongSignSenderTimer = None		# 帮会会标发送计时器
		self.accountName = ""				# 初始化账号名为空
		self.itemAwards = ItemAwards()		# 领取物品模块

		# 自动战斗时限 by 姜毅
		self.isAFing = False		# 是否自动战斗状态
		self.startTickAF = 0.0	# 自动战斗起始时刻

		# 上次领取周工资的时间，此变量用于限制玩家可能在同一个tick内进行多次申请
		self.getWeekOnlineGiftTime = 0.0

		INFO_MSG("now init base role %s end..............." % self.playerName )

	def fixTimeReward( self ):
		if self.level > csconst.OLD_REWARD_LEVEL_LIM:			# 大于60级就没有奖励了
			return
		if len( self.receivedRewardTick ) >= g_onlineReward.getCount():	# 其实没可能大于，只是怕数据出问题
			if self.checkOverDay():		# 距上次下线是否已过了0时，超过则刷新奖励记录
				self.oldRewardReflash()
			self.oldPlayerReward()
			self.oldPlayerRewardTimeReflash()		# 增加timer在0点刷新领奖记录
		else:
			self.newPlayerReward()
			
	def newPlayerReward( self ):
		"""
		新手奖励
		"""
		lifeTime = self.getNowlifetime()
		# 通知cell发下一个奖励的提示给客户端
		rewardNum = len( self.receivedRewardTick )
		self.cell.sendNextAwarderToClient( lifeTime, rewardNum,0 )
		
	def confirmToReceiveNewPlayerReward( self ):
		"""
		Exposed method
		响应客户端领取新手奖励的请求
		"""
		lifeTime = self.getNowlifetime()
		rewardNum = len( self.receivedRewardTick )+1
		self.cell.giveNewPlayerReward( lifeTime, rewardNum )
		
	def addRewardRecord( self, rewardTick ):
		"""
		define method
		增加领奖记录
		"""
		self.receivedRewardTick.append( rewardTick )
		if len( self.receivedRewardTick ) == g_onlineReward.getCount():	# 如果新手奖励没了，就开始算老手奖励
			self.oldPlayerReward()

	def oldPlayerReward( self ):
		"""
		老手奖励
		"""
		if self.level > csconst.OLD_REWARD_LEVEL_LIM:
			return
		levelLimit = max( self.level/10, 3 )	# 该等级最多可领取
		if self.dailyRewardTimes >= levelLimit:	# 今天的奖励已领完
			return
		
		timer = self.oldPlayerRewardTick - self.getNowlifetime()
		if timer < 0:timer = Const.OLD_REWARD_WAIT_LIM_SECONDS	# 如果时间错乱就等10分钟作为调整
		
		onlineTime = self.getNowlifetime() - self.lifetime
		if onlineTime < 10:								# 用于刚上线触发倒数计时的
			self.client.onOldFixTimeReward( timer, self.dailyRewardTimes , 0, 0 )	# 通知客户端下一次奖励示
			
	def confirmToReceiveOldPlayerReward( self ):
		"""
		Exposed method
		响应客户端领取老手奖励的请求
		"""
		self.cell.giveOldPlayerReward( self.dailyRewardTimes )
		self.dailyRewardTimes += 1
		self.oldPlayerRewardTick = Const.OLD_REWARD_WAIT_LIM_SECONDS + Const.OLD_REWARD_WAIT_LIM_SECONDS * self.dailyRewardTimes + self.getNowlifetime()
		self.oldPlayerReward()

	def oldRewardReflash( self ):
		"""
		刷新定时老手定时奖励数据 by 姜毅
		"""
		INFO_MSG( "oldRewardReflash: dailyRewardTimes %i , oldPlayerRewardTick %i ."%(  self.dailyRewardTimes, self.oldPlayerRewardTick ) )
		self.dailyRewardTimes = 0
		self.oldPlayerRewardTick = 0

	def oldPlayerRewardTimeReflash( self ):
		"""
		零时刷新老手奖励计时器 by姜毅
		"""
		nowTime = int( time.time() )
		nowDayTime = int( self.getToday0Tick() )	# 当日的0时刻
		leftTime = 3600 * Const.OLD_REWARD_REFLASH_TIME + nowDayTime - nowTime + 60	# 增加1分钟的误差
		INFO_MSG( "oldPlayerRewardTimeReflash:%i"%(leftTime) )
		self.reflashTimer = self.addTimer( leftTime, 0.0, ECBExtend.FIX_TIME_OLD_PLAYER_REWARD_REFLASH )
		
	def onTimer_fixTimeOldPlayerReflash( self, id, arg ):
		"""
		刷新老手奖励数据 by姜毅
		"""
		self.delTimer( self.reflashTimer )
		self.oldRewardReflash()
		self.oldPlayerReward()
		self.reflashTimer = self.addTimer( 3600 * Const.OLD_REWARD_REFLASH_TIME, 0.0, ECBExtend.FIX_TIME_OLD_PLAYER_REWARD_REFLASH )
		
	def requestInitialize( self, initType ) :
		"""
		<Exposed/>
		请求初始化( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : 初始化类型，在 csdefine.py 中定义
		"""
		initializer = {
			csdefine.ROLE_INIT_OPRECORDS	: self.opr_updateClient,
			csdefine.ROLE_INIT_PETS			: self.pcg_updateClient,
			csdefine.ROLE_INIT_QUICK_BAR	: self.qb_updateClient,
			csdefine.ROLE_INIT_VEHICLES		: self.requestVehicleData,
			csdefine.ROLE_INIT_OFLMSGS		: self.requestOFLMsgs,
			csdefine.ROLE_INIT_DAOFA		: self.daofa_updateClient,
			}
		initializer[initType]()

	def getNameAndID( self ):
		"""
		virtual method.
		@return: the name of character entity and database id
		@rtype:  STRING
		"""
		return self.playerName + "(%s)" % self.databaseID

	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return self.playerName

	def getHeadTextureID( self ):
		"""
		获取头像图标ID
		"""
		if self.headTextureID is None: return 0
		return self.headTextureID

	def getNowlifetime( self ):
		"""
		获取当前的玩家总在线时间
		注:不能直接使用lifetime因为lifetime在每次下线时才记录
		"""
		return self.lifetime + BigWorld.time() - self._lasttime

	def clientDead( self ):
		"""
		断开客户端。
		"""
		INFO_MSG( "Help: The base just told us (id %d) we're dead!" % self.id )
		self.onLeaveAutoFight()
		self.liv_onLeave()
		self.logoff()

	def logoff( self ):
		"""
		玩家下线。
		"""
		INFO_MSG( "%s(%i): logoff." % (self.getName(), self.id) )
		try:
			g_logger.roleLogoffLog( self.clientAddr[0], self.accountName, self.getNameAndID(), self.getNowlifetime(), cschannel_msgs.ROLE_INFO_1 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		if hasattr( self, "reflashTimer" ) and self.reflashTimer is not None:
			self.delTimer( self.reflashTimer )
		self.onLeaveAutoFight()
		self.liv_onLeave()
		self.ybt_onLeave()
		self.cmi_onLogout()
		self.destroySelf()

	def onEntitiesEnabled( self ):
		"""
		定位玩家位置所在场景，供创建玩家cell实体准备。
		"""
		INFO_MSG("now role %s enabled..............."  % self.playerName )
		self.last_login_ip = self.clientAddr[0]	#记录玩家最后登录的IP
		if hasattr( self, "cellData" ) and self.cellData != None:
			"""
			#INFO_MSG( "%s: login to '%s' space." % ( self.cellData["playerName"], self.cellData["spaceType"] ) )
			self.addMailboxCallback( self.spaceManager, [self.cellData["spaceType"], "cell"], CBF_ROLE_GETSTARTSPACE, "onGetStartSpace" )
			"""
			# check uid of items of kitbags

			# 如果数据库某些字段经过非法修改，直接踢出 by 姜毅
			self.checkPropertyMD5( self.cellData )

			self.itemDataCheck( self.cellData["itemsBag"], self.bankItemsBag )

			self.onRestoreCooldown( self.cellData["attrCooldowns"] )	# 无论entityMailbox是否存在，我们都必须恢复cooldown
			self.onRestoreBuffs( self.cellData["attrBuffs"] )
			self.onCheckLoopQuestLogs( self.cellData["loopQuestLogs"] )	# 检查环任务记录，以清除冗余数据
			presentee = self.accountEntity.customData.query( "presentee")
			if presentee and int(presentee):
				self.cellData["flags"]  |= 1 << csdefine.ROLE_FLAG_SPREADER
			if hasattr( self, "cell" ):
				INFO_MSG("===== already has CELL!" )
				return

			self.logonSpace()
			#self.enterSpace( self.cellData["spaceType"], self.cellData["position"], self.cellData["direction"] )


	def statusMessage( self, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = len(args) and str(args) or ""
		self.client.onStatusMessage( statusID, args )

	def roleLogonMessage( self ):
		"""
		记录角色上线的日志
		"""
		try:
			g_logger.roleLogonLog( self.databaseID, self.getName(), self.accountName, self.getNowlifetime(), self.clientAddr[0], cschannel_msgs.ROLE_INFO_2 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onGetCell(self):
		"""
		cell 实体创建完成。
		"""
		INFO_MSG("now role %s getCell..............."  % self.playerName )
		# 注册到本地baseapp的全局列表中，可用于其它需要根据名字查找player或直接轮循所有player的地方
		Love3.g_baseApp.registerPlayer( self )
		self.updateRoleRecord()
		self.logonForTeam()		# 队伍系统，玩家上线
		self.postLogon()		# 邮件系统登录
		RoleRelation.onGetCell( self )
		PetCage.onGetCell( self )
		RoleChat.onGetCell( self )
		AntiWallow.onGetCell( self )
		ZhengDaoInterface.onGetCell( self )
		BigWorld.globalData["MessyMgr"].requestRoleMessyInfo( self.databaseID, self.accountEntity.databaseID )
		BigWorld.globalData["CommissionSaleMgr"].queryForLogin( self, self.playerName )	# 寄卖系统
		self.pcu_takeThings( csconst.PCU_TAKECHARGE, 0 )	# 玩家上线更新自己的充值信息

		#下两句是通知反挂，角色上线了。
		apexProxy = Love3.g_apexProxyMgr.onGetApexProxy()
		if(apexProxy.getApexStartFlag()):
			apexProxy.noticeApexProxyMsgL(self.id,self.getName(),len(self.getName( )))
			apexProxy.noticeApexProxyMsgS(self.id,self.clientAddr[0])
			self.client.startClientApex( )#通知客户端起动反外挂

		if self.level >= csconst.QUIZ_MIN_LEVEL_LIMIT and ( BigWorld.globalData.has_key( "QuizGame_start" ) and BigWorld.globalData[ "QuizGame_start" ] == True ):	# 上线，知识问答活动在进行中
			BigWorld.globalData["QuizGameMgr"].onRoleGetCell( self )

		BigWorld.globalData["WuDaoMgr"].updateDBIDToBaseMailbox( self.databaseID, self )		# 更新武道大会DBIDToBaseMailbox

		# 如果一开始就丢失了client，也就没有存在的价值了。
		if not self.hasClient:
			INFO_MSG( "%s(%i): I have no client proxy, destroy myself." % ( self.getName(), self.id ) )
			self.destroySelf()

		BigWorld.globalData["TiShouMgr"].queryTiShouInfo( self, self.databaseID )
		BigWorld.globalData["CollectionMgr"].queryCollectionDeposit( self, self.databaseID )
		BigWorld.globalData["TaoismAndDemonBattleMgr"].onPlayerLogin( self, self.getName() )
		
		try:
			g_logger.roleOnLineLog( self.databaseID, self.getName(), self.level, self.tong_dbID, self.tong_grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onLoseCell(self):
		DEBUG_MSG( "The base just told us (id %d) we're lose cell component!" % self.id )
		try:
			g_logger.roleLogoutLog( self.databaseID, self.getName(), self.accountName, self.getNowlifetime(), self.clientAddr[0], cschannel_msgs.ROLE_INFO_3 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		# 下线时从本地的baseapp全局列表中去掉自己
		# 这个调用可能会产生异常，但必须让后面的代码继续下去。
		try:
			Love3.g_baseApp.deregisterPlayer( self )
		except:
			EXCEHOOK_MSG( "onLoseCell: %s(%i)" % ( self.getName(), self.id ) )

		# 根据最新的垃圾收集情况来看，
		# 即使在team_onLogout()里面清除了对自身的引用，
		# 在某些情况下仍然会在_teamMembers变量中对自身进行引用，
		# 因此，怀疑在调用team_onLogout()之前的代码产生了异常，
		# 所以，把team_onLogout()调用移到最前面。
		# 队伍系统，玩家下线
		#处理舞厅buff的累计时间	
		self.team_onLogout()

		PetCage.onLoseCell( self )
		RoleRelation.onLoseCell( self )
		AntiWallow.onLoseCell( self )
		# 登出帮会系统
		self.tong_onLogout()

		# 玩家下线通报空间
		#self.offLineOfSpace()

		# 邮件系统通出通报
		self.postLogout()

		# 元宝交易退出
		self.ybt_onLeave()

		self.destroySelf()
		
		#触发退出副本组队
		self.cmi_onLogout()
		
		# 知识问答下线通知
		if self.level > csconst.QUIZ_MIN_LEVEL_LIMIT and BigWorld.globalData.has_key( "QuizGame_start" ):
			BigWorld.globalData["QuizGameMgr"].playerQuit( self.databaseID )

		BigWorld.globalData["WuDaoMgr"].delDBIDToBaseMailbox( self.databaseID )		# 下线后，删除武道大会DBIDToBaseMailbox


	def logout( self ):
		"""
		注销到登录界面

		Exposed for client
		"""
		INFO_MSG( "%s(%i): logout." % (self.getName(), self.id) )
		try:
			g_logger.roleLogoutLog( self.databaseID, self.getName(), self.accountName, self.getNowlifetime(), self.clientAddr[0], cschannel_msgs.ROLE_INFO_4 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		self._isLogout = True
		self.onLeaveAutoFight()
		self.liv_onLeave()
		self.ybt_onLeave()
		self.cmi_onLogout()
		self.destroySelf()

	def onClientDeath( self ):
		"""
		客户端断开连接通报，销毁自身即下线操作。
		"""
		DEBUG_MSG( "The base just told us (id %d) we're dead!" % self.id )
		try:
			g_logger.roleLogoutLog( self.databaseID, self.getName(), self.accountName, self.getNowlifetime(), self.clientAddr[0], cschannel_msgs.ROLE_INFO_1 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		#RoleImageVerify.stopVerifyCount( self )	升级到1.8.1后缺少相应的gd库，功能暂停
		PetCage.onClientDeath( self )
		self.onLeaveAutoFight()
		self.liv_onLeave()
		self.ybt_onLeave()
		self.cmi_onLogout()
		self.destroySelf()


	def destroySelf( self ):
		"""
		销毁自己
		"""
		#通知反外挂　，角色下线
		Love3.g_apexProxyMgr.onGetApexProxy( ).noticeApexProxyMsgG( self.id,self.getName(),len(self.getName( )) )
		if self.jueDiFanJiState:
			BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiRoleDestroy( self.databaseID )
		if hasattr( self, "cell" ):
			# for catch "ValueError: Base.destroyCellEntity: Base xxxxx is in the process of creating an associated cell entity."
			# 对于这种错误，仅仅输出一下，我们会在onGetCell()回调中判断玩家当前是否有client，如果没有则再次destroy自己。
			# 当前日志输出是为了验证在onGetCell()中确实能完成这个行为，将来确认后可以删除这个异常的输出。
			try:
				self.destroyCellEntity()
			except ValueError, errstr:
				EXCEHOOK_MSG( "destroySelf: %s(%i)" % ( self.getName(), self.id ) )
		else:
			# 如果有account entity则一定要通知account entity
			if self.accountEntity is not None:
				if self._isLogout and self.hasClient and not self.accountEntity.hasClient:
					# 如果是注销，且自己有一个client，并且自己的accountEntity没有client，则可以把client交到account中
					# 需要判断accountEntity.hasClient是为了避免玩家断线后重新登录或从另一台电脑使用相同帐号登录时注销旧的角色而设，
					self.giveClientTo( self.accountEntity )		# 把控制权交到account中
				self.accountEntity.onAvatarDeath()				# 通知account，必须在调用giveClientTo()之后调用，详看Account::onAvatarDeath()
			else:
				INFO_MSG( "%s(%i): is not account entity." % (self.getName(), self.id) )
			self.destroy()	# destroy必须在调用giveClientTo()之后调用

	def onClientGetCell( self ):
		"""
		If present, this method is called when the message to the client that it now has a cell is called.
		"""
		self.loginTime = time.time()		# 只有client获得了cell才被认为是登录了。
		self._lasttime = BigWorld.time()	# 临时数据
		#RoleImageVerify.firstVerifyCount( self )	升级到1.8.1后缺少相应的gd库，功能暂停
		PetCage.onClientGetCell( self )
		self.cell.onCellReady()
		self.client.updateGold( self.gold, csdefine.CHANGE_GOLD_INITIAL )
		self.client.updateSilver( self.silver, csdefine.CHANGE_SILVER_INITIAL )
		self.tong_onLogin()		# 玩家上线登陆帮会系统
		#self.statusMessage( csstatus.ACCOUNT_STATE_SERVER_VERSION, Love3.versions ) 注掉刚登录时的版本提示，目前已不需要
		if self.firstLoginTime == 0:				# 记录角色创建帐号后第一次登陆服务器的时间
			self.firstLoginTime = int( time.time())
			self.writeToDB()
		self.accountEntity.onAvatarClientGetCell()
		Fisher.onClientGetCell( self )
		
		# 如果不通过数据库字段MD5校验，直接踢出
		if not self.validMD5Check:
			self.statusMessage( csstatus.ROLE_DATA_MD5_CHECK_ERROR )
			self.logoff()

		# 如果物品数据不合法，直接踢出
#		if not self.validItemData:
#			self.statusMessage( csstatus.ROLE_ITEM_CHECK_ERROR )
#			self.logoff()

		self.fixTimeReward()	# 计时在线奖励 by姜毅
		self.chargeVimTimer()	# 活力值充值计时 by 姜毅
		self.chargeAFTimer()	# 自动战斗时间充值 by 姜毅
		self.initSuit()			# 初始化角色一键套装 by 姜毅
		# 帮会会标发送计时器 by 同上
		self._tongSignSenderTimer = self.addTimer( Const.SEND_TONG_SIGN_TIME_TICK, 0.0, ECBExtend.ROLE_TONG_SIGN_SENDER )

	def onClientGetVersion( self ):
		"""
		Exposed method; get server version
		"""
		self.client.onGetServerVersion( Love3.versions )

	def onWriteToDB( self, cellData ):
		"""
		see also api_python/python_base.chm
		"""
		w_time = int(time.time())
		INFO_MSG( "onWriteToDB info role %s(%s) role_last_offline %s"%( self.id, self.getName(), w_time ) )
		now = BigWorld.time()
		self.role_last_offline = w_time
		self.oldPlayerRewardTick = Const.OLD_REWARD_WAIT_LIM_SECONDS + Const.OLD_REWARD_WAIT_LIM_SECONDS * self.dailyRewardTimes + self.getNowlifetime()
		t = now - self._lasttime
		if t > 1:	# 最少要1秒
			self.lifetime += t
			self._lasttime = now
			daysSec = 24 * 3600
			wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)
			if not self.weekOnlineTime.has_key(wT):
				if len(self.weekOnlineTime) >= 2:		# weekOnlineTime只需要保存本周、上周的在线时间
					minKey = min( self.weekOnlineTime.keys() )
					del self.weekOnlineTime[minKey]
				self.weekOnlineTime[wT] = t
			else:
				self.weekOnlineTime[wT] += t

		PetCage.onWriteToDB( self, cellData )

		# check cooldown
		self.onSaveCooldown( cellData["attrCooldowns"] )

		# check buff
		self.onSaveBuffs( cellData["attrBuffs"] )

		# check uid of items of kitbags
		self.itemDataCheck( cellData["itemsBag"], self.bankItemsBag )

		# create the database section MD5 code, this must be the END, by jy
		self.setPropertyMD5( cellData )


	def sendLifetime2Client( self ):
		"""
		Exposed method; pass lifetime to client
		"""
		self.client.set_lifetime( self.lifetime )

	def calcPropertyMD5Code( self, cellData ):
		"""
		根据Role属性获得基于Role字段的MD5码 by 姜毅
		"""
		sectionValue = []
		sectionValue.append( self.grade )
		sectionValue.append( self.level )
		sectionValue.append( cellData["money"] )
		sectionValue.append( cellData["potential"] )
		sectionValue.append( cellData["bankMoney"] )
		sectionValue.append( cellData["absorbableEXPLevelValue"] )
		sectionValue.append( cellData["_PetTrainer__trainGem"]["exp"] )
		sectionValue.append( cellData["_PetTrainer__trainGem"]["remainTime"] )
		sectionValue.append( cellData["roleTrainGem"]["exp"] )
		sectionValue.append( cellData["roleTrainGem"]["remainTime"] )
		sectionValue.append( int( self.lifetime ) )
		secVal_str = str( sectionValue )

		itemDataList = []
		itemsInBag = cellData["itemsBag"].getDatas()
		itemDataList = [ ( e.uid, e.id, e.amount, e.order ) for e in cellData["itemsBag"].getDatas() ]
		itemDataList.extend( [( e.uid, e.id, e.amount, e.order ) for e in self.bankItemsBag.getDatas()] )
		itemDataList.sort( key = lambda x:x[0] )

		item_str = str( itemDataList )
		MD5_str = secVal_str + item_str

		return _md5.new( MD5_str ).hexdigest()

	def setPropertyMD5( self, cellData ):
		"""
		根据Role属性生成Role的需要校验的字段的MD5校验码 by 姜毅
		"""
		if not self.validMD5Check: return
		self.baseSectionMD5Code = self.calcPropertyMD5Code( cellData )

	def checkPropertyMD5( self, cellData ):
		"""
		根据Role属性检测Role的需要校验的字段的MD5校验码 by 姜毅
		"""
		if not Const.MD5Checker_Switcher: return
		if self.baseSectionMD5Code == self.calcPropertyMD5Code( cellData ):
			INFO_MSG( "%s[%i]MD5 check successed。"%( self.getName(), self.id ) )
			self.validMD5Check = True
		else:
			ERROR_MSG( "%s[%i]MD5 check failed，your database may be modified nonlicet。"%( self.getName(), self.id ) )
			self.validMD5Check = False

	def onSaveCooldown( self, cooldownsInstance ):
		"""
		cooldown写入数据库时的处理
		"""
		dels = []
		for cd in cooldownsInstance:
			try:
				cooldown = Love3.g_cooldowns[ cd ]
			except KeyError:
				dels.append( cd ) 	# cooldown 类型不存在则删除，此情况的可能是手动修改了数据库或废弃了已存在的旧的cooldown
				continue

			cdData = cooldownsInstance[ cd ]
			endTime = cdData[ 2 ]
			if cooldown.isTimeout( endTime ):
				dels.append( cd )	# 删除已过时的cooldown
				continue

			if cooldown.isSave():
				cooldownsInstance[ cd ] = cooldown.calculateOnSave( cdData )
			else:
				dels.append( cd )	# 不保存的cooldown全部删除

		for cd in dels:
			cooldownsInstance.pop( cd )

	def onRestoreCooldown( self, cooldownsInstance ):
		"""
		恢复cooldown的正常计算，想让此方法生效必须在调用createCellEntity()之前调用
		"""
		#INFO_MSG( "start", cooldownsInstance )
		dels = []
		for cd in cooldownsInstance:
			try:
				cooldown = Love3.g_cooldowns[ cd ]
			except KeyError:
				dels.append( cd ) 	# cooldown 类型不存在则删除，此情况的可能是手动修改了数据库或废弃了已存在的旧的cooldown
				continue

			cdData = cooldownsInstance[ cd ]
			cooldownsInstance[ cd ] = cooldown.calculateOnLoad( cdData )
			endTime = cooldownsInstance[ cd ][2]
			# 在coolDown数据恢复之后进行判断，删除已过时的coolDown
			if cooldown.isTimeout( endTime ):
				dels.append( cd )

		#INFO_MSG( "deletes", dels )
		for cd in dels:
			cooldownsInstance.pop( cd )
		#INFO_MSG( "end", cooldownsInstance )

	def onSaveBuffs( self, buffsInstance ):
		"""
		buff往数据库里写入时的处理
		"""
		#INFO_MSG( "--> buffs calculate before:", buffsInstance )
		rmb = []
		for idx, buff in enumerate( buffsInstance ):
			try:
				spell = Love3.g_skills[buff["skill"]["id"]]
			except KeyError:
				rmb.append( idx )
				continue

			if spell.isSave():
				buff["persistent"] = spell.calculateOnSave( buff["persistent"] )
			else:
				rmb.append( idx )

		rmb.reverse()	# 从后面往前删除
		for r in rmb:
			buffsInstance.pop( r )
		#INFO_MSG( "--> buffs calculate after:", buffsInstance )


	def onRestoreBuffs( self, buffsInstance ):
		"""
		恢复buff的正常计算，想让此方法生效必须在调用createCellEntity()之前调用
		"""
		buffIndex = 0
		rmb = []
		bt = time.time()
		for idx, buff in enumerate( buffsInstance ):
			try:
				spell = Love3.g_skills[buff["skill"]["id"]]
			except KeyError:
				rmb.append( idx )
				continue

			if not spell:
				rmb.append( idx )
				continue

			buff[ "index" ]	= buffIndex
			buffIndex += 1
			t = spell.calculateOnLoad( buff["persistent"] )	# 必须先恢复后才能判断buff是否过期
			buff[ "persistent" ] = t

		rmb.reverse()	# 从后面往前删除
		for r in rmb:
			buffsInstance.pop( r )

		# 给玩家一个未决buff,保护玩家在登录过程不受伤害
		if self.cellData["state"] != csdefine.ENTITY_STATE_DEAD:
			tempTime = int( 30 + time.time() )
			notHasBuff = True

			for buff in self.cellData["attrBuffs"]:
				if buff[ "skill" ][ "id" ] == csconst.PENDING_BUFF_ID:	# 如果玩家已经存在未决buff,只更新未决buff的persistent时间
					buff[ "persistent" ] = tempTime
					buff[ "index" ] = buffIndex
					notHasBuff = False
					break

			if notHasBuff:
				buffData = { "skill" : { "id":csconst.PENDING_BUFF_ID, "param":0, "uid":0 }, \
				"persistent" : tempTime, "currTick" : 0, "caster" : 0, "state" : 0, "index" : buffIndex,"sourceType" : 0, "isNotIcon" : False }

				self.cellData["attrBuffs"].append( buffData )

			buffIndex += 1
			self.cellData["lastBuffIndex"] = buffIndex


	def onCheckLoopQuestLogs( self, loopQuestLogs ):
		"""
		检查每天可做几次的环任务，如果做任务日期与当前日期不一样的则清除掉，以避免累积冗余数据
		"""
		rmb = []
		for index, value in enumerate( loopQuestLogs ):
			if not value.checkStartTime():
				rmb.insert( 0, index )

		for index in rmb:
			loopQuestLogs.pop( index )

	def updateLevel( self, level ):
		"""
		Define method.
		更新备份的level，数据来源于cellApp
		"""
		oldLevel = self.level
		self.level = level

		self.tong_onLevelChanged()	# 等级变化,通知帮会
		self.rlt_onLevelUp()			# 等级变化，通知关系人
		self.zd_onLevelUp()				# 等级变化，通知证道系统

		try:
			g_logger.roleUpgradeLog( self.databaseID, self.getName(), oldLevel, self.level, self.getNowlifetime() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def itemDataCheck( self, kitbagsInstance, bankBags ):
		"""
		检查背包和仓库中所有物品是否有相同的uid，
		如果存在则输出所有的物品数据。

		@param kitbagsInstance: 角色背包实例
		@param bankBags: 角色银行包实例
		"""
		uids = set()
		for kitbag in ( kitbagsInstance, bankBags ):
			for item in kitbag.getDatas():
				if item.uid not in uids:
					uids.add( item.uid )
				else:
					#插入对相同UID物品的处理
					self.recordSameUIDItem( item )
					self.validItemData = False

		if not self.validItemData:
			INFO_MSG( "%s(%i): found same uid, outputing player all item..." % ( self.getName(), self.databaseID ) )
			try:
				for kitbag in ( kitbagsInstance, bankBags ):
					for item in kitbag.getDatas():
						INFO_MSG( item.addToDict() )
			except:
				pass
			# 不能在这个时候调用logout，否则服务器会宕机，并出现如下的错误
			# Base.chat_fbds should not be accessed since Role entity id 9514 is destroyed
			# Base.qbItems should not be accessed since Role entity id 9514 is destroyed
			# Base.bankBags should not be accessed since Role entity id 9514 is destroyed
			# Base.bankItemsBag should not be accessed since Role entity id 9514 is destroyed
			# Base.tong_scholium should not be accessed since Role entity id 9514 is destroyed
			# Base.roleState should not be accessed since Role entity id 9514 is destroyed
			# Base.deleteTime should not be accessed since Role entity id 9514 is destroyed
			# more...
			#self.logout()
			INFO_MSG( "%s(%i): item output over." % ( self.getName(), self.databaseID ) )

	def recordSameUIDItem( self, item ):
		"""
		对背包、仓库中拥有的相同UID物品的处理
		"""
		recordItem = None
		bankBags = self.bankItemsBag
		if item in bankBags.getDatas():
			recordItem = item
		else:
			for bank_item in bankBags.getDatas():
				if bank_item.uid == item.uid:
					recordItem = bank_item
					break
		if not recordItem:
			INFO_MSG( "%s(%i): bankItemsBag has no same uid(%i) item ." % ( self.getName(), self.databaseID, recordItem.uid ))
			return
		#记录到表格中
		tempDict = recordItem.addToDict()
		del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
		itemData = BigWorld.escape_string( cPickle.dumps( tempDict, 2 ) )
		query = "insert ignore into custom_sameUIDItemTable ( sm_itemUID, sm_roleDBID, sm_recordTime, sm_Item )Value ( %d, %d,%d,\'%s\' )"% ( recordItem.uid, self.databaseID, int( time.time() ), itemData )
		BigWorld.executeRawDatabaseCommand( query,  self.__onInsertRecord )
		#移除仓库中的item
		if self.bankItemsBag.removeByOrder( recordItem.getOrder() ):		
			INFO_MSG( "%s(%i): bankItemsBag has same uid(%i) item ." % ( self.getName(), self.databaseID, recordItem.uid ))

	def __onInsertRecord( self,  result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "recordSameUIDItem: insert new item Info failed! playerName is %s"%( playerDBID ) )
			return
	
	def onRestoreCellFailed( self ):
		"""
		当玩家所在的cellapp挂了，base在恢复玩家cell数据时，自动调用
		"""
		#暂时只进行相同uid检查
		self.itemDataCheck( self.cellData["itemsBag"], self.bankItemsBag )

	def getGender( self ):
		"""
		获得玩家的性别。
		"""
		return self.raceclass & csdefine.RCMASK_GENDER

	def getClass( self ):
		"""
		取得自身职业
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def getCamp( self ):
		"""
		取得自身阵营
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_CAMP ) >> 20

	# ----------------------------------------------------------------
	# 过程帮助( 2008.08.04 -- hyw )
	# ----------------------------------------------------------------
	def addDartData( self, key, value ):
		"""
		define method
		"""
		BigWorld.globalBases[ "DartManager" ].add( self.getName(), key, value )


	def updateDartPrestige( self, xValue, cValue ):
		"""
		define method
		更新镖局声望值
		@param xValue	:兴隆镖局声望值
		@param cValue	:昌平镖局声望值
		"""
		self.cell.updateDartPrestige( xValue, cValue )

	def onWuDaoOver( self, playerBaseMB, result ):
		"""
		通知武道大会管理器比赛结果
		"""
		BigWorld.globalData[ "WuDaoMgr" ].onWuDaoOverFromSpace( playerBaseMB, self.databaseID, self.level, result )	# 通知武道大会管理器，某场战斗结果

	def queryActivityScheme( self, index ):
		"""
		exposed method
		查询一个活动多条记录
		"""
		keys = CrondDatas.instance().getAllActivityData().keys()
		if len( keys ) > index:
			key = keys[index]
			for iScheme in CrondDatas.instance().getAllActivityData()[key]:
				if iScheme['showOnClient'] and iScheme['act']:
					# 客户端允许显示 而且 该活动是激活的	2009-07-13 SPF
					self.client.onAddScheme( iScheme['name'], iScheme['isStart'], iScheme['description'], iScheme['cmd'], iScheme['condition'], iScheme['area'], iScheme["activityType"], iScheme["line"], iScheme["star"], iScheme["persist"]  )
			self.client.onOneActivityDataSendOver()
		else:
			self.client.onActivityDataSendOver()

	"""
	GM 信息查询
	"""
	def queryBankInfo( self, queryerMB, params ):
		"""
		define method
		"""
		items = self.bankItemsBag.getDatasByRange()
		itemNames = []
		for i in items:
			itemNames.append( i.name() )
		if len(itemNames) == 0:
			queryerMB.client.onStatusMessage( csstatus.STRING_BAG_HAS_NO_ITEM, "" )
		else:
			for i in itemNames:
				info += i + ", "
			queryerMB.client.onStatusMessage( csstatus.STRING_BAG_ITEM, str(( info, )) )


	def queryLoginInfo( self, queryerMB, params ):
		"""
		define method
		"""

		queryerMB.client.onStatusMessage( csstatus.STRING_LOGININFO, "" )

	def queryLastLoginInfo( self, queryerMB, params ):
		"""
		define method
		"""

		queryerMB.client.onStatusMessage( csstatus.STRING_LASTLOGININFO, "" )

	def queryAccountInfo( self, queryerMB, params ):
		"""
		define method
		"""

		queryerMB.client.onStatusMessage( csstatus.ACCOUNT, str(( self.accountEntity.playerName, )) )

	def kickAction(  self, kickerMB, params ):
		"""
		define method
		踢下线
		"""
		self.logoff()

	def queryIPAction( self, queryerMB, params ):
		"""
		define method
		查询IP
		"""
		queryerMB.client.onStatusMessage( csstatus.IP, str(( self.clientAddr[0], )) )

	def queryPlayerAmountAction( self, queryerMB, params ):
		"""
		define method
		查询在线人数
		"""
		Love3.g_baseApp.queryAllPlayerAmount( queryerMB, params )

	def queryPlayerNameAction( self, queryerMB, params ):
		"""
		define method
		查询在线人数
		"""
		Love3.g_baseApp.queryAllPlayerName( queryerMB, params )

	def blockPlayerAccount( self, params ):
		"""
		define method
		"""
		endDate 			= params["endDate"]

		self.accountEntity.block_state = 1
		self.accountEntity.block_end_time = endDate
		self.logoff()

		return
		"""
		query = "update tbl_Account set sm_block_end_time = %i, sm_block_state = %i  where sm_playerName = \'%s\' "% ( endDate, 1, self.accountEntity.playerName )
		BigWorld.executeRawDatabaseCommand( query, self.__onBlockCB )#记录到数据库
		"""

	def __onBlockCB( self, resultSet, rows, errstr ):
		"""
		"""
		pass

	def payGold( self, value, reason = None ):
		"""
		玩家给元宝
		"""
		if self.getUsableGold() - value < 0:
			return False
		self.addGold( -value, reason )
		return True

	def gainGold( self, value, reason = None  ):
		"""
		给玩家金元宝
		"""
		if self.gold + value > csconst.ROLE_GOLD_UPPER_LIMIT:
			return False
		self.addGold( value, reason )
		return True

	def addGold( self, value, reason = None ):
		"""
		增减玩家的元宝值
		@param value : 元宝值
		@type value : INT64
		"""
		self.accountEntity.addGold( value, reason )

	def setGold( self, value, reason = None ):
		"""
		设置玩家的金元宝值

		@param value : 设置的值
		@type value : UINT32
		"""
		self.accountEntity.addGold( value - self.gold,  reason )

	def updateGold( self, value, reason = csdefine.CHANGE_GOLD_NORMAL ):
		"""
		更新玩家的元宝值
		"""
		self.gold = value
		if hasattr( self, "client" ):
			self.client.updateGold( value, reason )

	def freezeGold( self, value ):
		"""
		冻结一定数量的金元宝

		@param value : 冻结值
		"""
		self.frozenGold += value

	def thawGold( self, value ):
		"""
		解冻金元宝
		"""
		self.frozenGold -= value

	def paySilver( self, value, reason ):
		"""
		玩家给银元宝
		"""
		if self.getUsableSilver() - value < 0:
			return False
		self.addSilver( -value, reason )
		return True

	def gainSilver( self, value, reason = None ):
		"""
		给玩家银元宝
		"""
		if self.silver + value > csconst.ROLE_SILVER_UPPER_LIMIT:
			return False
		self.addSilver( value, reason )
		return True

	def addSilver( self, value, reason = None ):
		"""
		玩家银元宝值发生变化
		@param value : 元宝值
		@type value : INT64
		"""
		self.accountEntity.addSilver( value, reason )

	def setSilver( self, value, reason = None ):
		"""
		设置玩家的金元宝值

		@param value : 设置的值
		@type value : UINT32
		"""
		self.accountEntity.addSilver( value - self.silver, reason )

	def updateSilver( self, value, reason = csdefine.CHANGE_SILVER_NORMAL ):
		"""
		更新玩家的元宝值
		"""
		self.silver = value
		if hasattr( self, "client" ):
			self.client.updateSilver( value, reason )

	def freezeSilver( self, value ):
		"""
		冻结一定数量的银元宝

		@param value : 冻结值
		"""
		self.frozenSilver += value

	def thawSilver( self, value ):
		"""
		解冻银元宝
		"""
		self.frozenSilver -= value

	def getUsableGold( self ):
		"""
		获得可用的金元宝，当前值减去被冻结的值
		"""
		return self.gold - self.frozenGold

	def getUsableSilver( self ):
		"""
		获得可用的银元宝，当前值减去被冻结的值
		"""
		return self.silver - self.frozenSilver


	def updateRoleRecord( self ):
		"""
		角色上线，把角色的一些游戏记录从新获得，保存到cell上。
		"""
		query = "select sm_recordKey, sm_recordValue from custom_RoleRecord where sm_roleDBID = %i"%self.databaseID
		BigWorld.executeRawDatabaseCommand( query, self.onReceiveRoleRecord )

		query = "select sm_recordKey, sm_recordValue from custom_AccountRecord where sm_accountDBID = %i"%self.accountEntity.databaseID
		BigWorld.executeRawDatabaseCommand( query, self.onReceiveAccountRecord )

		nextUpdateTime = ( 24 - time.localtime()[3] ) * 3600 - time.localtime()[4] * 60
		self.addTimer( nextUpdateTime, 0.0, ECBExtend.PLAYER_ACTIVITY_RECORD_REFRESH_CBID )


	def onReceiveRoleRecord( self, result, dummy, errstr):
		"""
		"""
		if self.isDestroyed:
			ERROR_MSG( "role is destroyed" )
			return
		if result and len( result ) != 0:
			resultString = cPickle.dumps( result, 2 )
			self.cell.initRoleRecord( resultString )
		self.cell.remoteCall( "onRoleRecordInitFinish", () )

	def onReceiveAccountRecord( self, result, dummy, errstr):
		"""
		"""
		if self.isDestroyed:
			ERROR_MSG( "role is destroyed" )
			return
		if result and len( result ) != 0:
			resultString = cPickle.dumps( result, 2 )
			self.cell.createAccountRecord( resultString )
		self.cell.remoteCall( "onAccountRecordInitFinish", () )


	def sendMsgToApexClient(self ,strMsg,nLength):
		"""
		发送数据到apex的客户端
		"""
		self.client.clientRecvApexMessage( strMsg,nLength)

	def clientSendApexMessage( self ,strMsg,nLength):
		"""
		从apex的客户端接收数据
		"""
		pos = strMsg.find("StartApexClient re =")
		if( pos != -1):
			numberStr = strMsg[strMsg.find('=')+1:]
			nRetNumber = int(numberStr)
			Love3.g_apexProxyMgr.onGetApexProxy().noticeApexProxyMsgR( self.id,nRetNumber )
		else:
			Love3.g_apexProxyMgr.onGetApexProxy().noticeApexProxyMsgT(self.id,strMsg,nLength)


	def saveRoleRecord( self, recordString ):
		"""
		define method
		"""
		recordDict = cPickle.loads( recordString )

		updateQuery = "REPLACE INTO custom_RoleRecord(sm_roleDBID, sm_recordKey, sm_recordValue) VALUES"
		removeQuery = "DELETE from custom_RoleRecord where sm_roleDBID = %i and sm_recordKey = '%s'"
		for i in recordDict:
			if recordDict[i] == "":
				BigWorld.executeRawDatabaseCommand( removeQuery%( self.databaseID, i ), Functor( self.onSaveRecord, self.accountEntity.databaseID, i, recordDict[i] )  )
			else:
				BigWorld.executeRawDatabaseCommand( updateQuery + str( "(%i,'%s','%s')"%( self.databaseID, i, recordDict[i] ) ), Functor( self.onSaveRecord, self.accountEntity.databaseID, i, recordDict[i] ) )


	def saveAccountRecord( self, recordString ):
		"""
		define method
		"""
		recordDict = cPickle.loads( recordString )

		query = "REPLACE INTO custom_AccountRecord(sm_accountDBID, sm_recordKey, sm_recordValue) VALUES"
		for i in recordDict:
			BigWorld.executeRawDatabaseCommand( query + str( "(%i,'%s','%s')"%( self.accountEntity.databaseID, i, recordDict[i] ) ), Functor( self.onSaveRecord, self.accountEntity.databaseID, i, recordDict[i] ) )


	def onSaveRecord(  self, databaseID, key, value, result, dummy, errstr):
		"""
		"""

		if errstr:
			ERROR_MSG( "Save account(role)(%i) record (key: %s value: %s) Failed! Error: '%s'"%( databaseID, key, value, errstr ) )
			return
		INFO_MSG( "Save account(role)(%i) record (key: %s value: %s) Success ! "%( databaseID, key, value ) )

	def update_grade( self, grade ):
		"""
		define method
		在base端写日志时需要将grade写入
		@type  grade ：INT8
		@param grade : 权限的值
		"""
		self.grade = grade

	def queryWeekOnlineTime( self, targetID ):
		"""
		define method
		查询角色本周在线时间
		"""
		text = ""
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)
		weekOnlineTime = self.weekOnlineTime.get(wT, 0)	# 取出本周在线时间
		nowWeekOnlineTime = weekOnlineTime + BigWorld.time() - self._lasttime
		text += cschannel_msgs.BASE_GOSSIP_ROLE_0 %( nowWeekOnlineTime/3600, nowWeekOnlineTime%3600/60, nowWeekOnlineTime%60 )

		self.client.onSetGossipText( text )
		self.client.onGossipComplete( targetID )

	def setLastWeekOnlineTime( self, value ):
		"""
		设置玩家上周在线时间
		"""
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1		#获取上一周是第几周
		self.weekOnlineTime[wT] = value

	def setOnlineTime( self, value ):
		"""
		设置玩家在线时间
		"""
		self.lifetime = value

	def getWeekOnlineTimeGift( self, lastWeek ):
		"""
		define method
		领取角色上周工资奖励
		@param lastWeek : 上周是第几周
		@type lastWeek : int32
		"""
		# 由于在cell检查是否能够领取工资，base只负责给工资，然后通知cell条件变化，这种行为会造成玩家用特别手段在同一个tick内
		# 在cell检查条件通过，然后到base成功的多次领取工资，因此在此处限制在一段时间内只允许领取一次工资。
		now = time.time()
		if now - self.getWeekOnlineGiftTime < 0.2:
			ERROR_MSG( "玩家( %s )在0.2秒内连续申请换取工资奖励，不允许这种行为。" % self.getName() )
			return
		self.getWeekOnlineGiftTime = now

		lastWeekOnlineTime = self.weekOnlineTime.get( lastWeek, 0 )
		if lastWeekOnlineTime < 10 * 3600:
			self.statusMessage( csstatus.WEEK_ONLINE_TIME_LIMIT_TIME )
			return

		base_gift_mapping = { 6:75, 7:125, 8:200, 9:250, 10:375, 11:375, 12:375, 13:375, 14:375, 15:375 }	# 根据等级，基础工资
		lastWeekOnlineHour = int(lastWeekOnlineTime/3600)
		levelStep = int(self.level/10)

		if lastWeekOnlineHour < 14:
			giftMultiple = 1
			gift = giftMultiple * (base_gift_mapping.get(levelStep, 0))
			if not self.gainSilver( gift, csdefine.CHANGE_SILVER_WEEKONLINETIMEGIFT ):
				return
			self.statusMessage( csstatus.WEEK_ONLINE_TIME_GET_GIFT1, lastWeekOnlineHour, gift )
		elif lastWeekOnlineHour < 18:
			giftMultiple = 2
			gift = giftMultiple * (base_gift_mapping.get(levelStep, 0))
			if not self.gainSilver( gift, csdefine.CHANGE_SILVER_WEEKONLINETIMEGIFT ):
				return
			self.statusMessage( csstatus.WEEK_ONLINE_TIME_GET_GIFT2, lastWeekOnlineHour, gift )
		else:
			giftMultiple = 4
			gift = giftMultiple * (base_gift_mapping.get(levelStep, 0))
			if not self.gainSilver( gift, csdefine.CHANGE_SILVER_WEEKONLINETIMEGIFT ):
				return
			self.statusMessage( csstatus.WEEK_ONLINE_TIME_GET_GIFT3, lastWeekOnlineHour, gift )

		self.cell.addTeachCredit( -3000, csdefine.CHANGE_TEACH_CREDIT_NORMAL )
		self.cell.setAccountRecord( "weekOnlineTimeGift", str( lastWeek + 1 ) )		# 设置本周领取过上周的工资

	def getjackarooCardGift( self, level, presentID ):
		"""
		@define method
		领取新手卡奖励
		@type  level     : 要领取的奖品的等级 如 5级新手卡奖品
		@param level     : UINT8
		@type  presentID : 要领取的奖品的ID 注,该值是从cell上发到base，成功后又会发回cell，本考虑采用setTemp形式放到cell端，
							但是这样的结果是base对于每一次请求都必须将结果返回cell端，而直接传值只在成功后返回，所以后者应该改更好。
		@param presentID : ITEM_ID
		"""
		entity = self.accountEntity
		if entity.jackarooCard != 1:
			self.statusMessage( csstatus.JC_NOT_USE_JACKAROOCARD )
			return
		if level > self.level:
			self.statusMessage( csstatus.JC_NOT_ENOUGH_LEVEL )
			return
		mask = 1 << (level - 5) / 10
		if entity.jackarooCardState & mask == 0:
			self.oldJackarooCardState = entity.jackarooCardState
			entity.jackarooCardState = entity.jackarooCardState | mask
			# 做位或运算，先标记该物品已经被领取，如果失败了再返回base将值还原。通常不会失败。
			self.cell.getjkCardGiftResult( presentID )
		else:
			self.statusMessage( csstatus.JC_HAVE_DRAW_BEFORE )
			return

	def onGetjkCardGiftFailed( self ):
		"""
		@define method
		领取成功后通知base添加领取标记
		"""
		self.accountEntity.jackarooCardState = self.oldJackarooCardState
		self.oldJackarooCardState = 0

	# ----------------------------------------------------------------
	# 新单人骑宠
	# ----------------------------------------------------------------
	def getVehicleID( self ):
		"""
		获取骑宠顺序ID
		@return UINT8
		"""
		vehicleKeys = self.vehicleDatas.keys()
		for index in xrange( 1, csconst.VEHICLE_AMOUNT_MAX + 1 ):
			if index not in vehicleKeys:
				return index
		return 0
		
	def useVehicleItem( self, item ):
		"""
		Define Method
		使用骑宠物品
		@return None
		"""
		uid = item.uid
		# 获取骑宠顺序ID
		id = self.getVehicleID()
		if id == 0:
			self.cell.onUseVehicleItemNotify( uid, False )
			return

		itemID = item.id
		lifeTime = item.getLifeTime()
		if lifeTime:
			deadTime = int( time.time() ) + lifeTime
		else:
			deadTime = 0
			
		#通过配置获取骑宠相关属性
		level,step,fullDegree,type = Love3.g_vehicleData.getProperty( itemID )
		if type == csdefine.VEHICLE_TYPE_FLY:
			growth = 0
			strength,intellect,dexterity,corporeity = (0,0,0,0)
		else:
			growth = Love3.g_vehicleData.getGrowth( step, Const.VEHICLE_SOURCE_INCUBATE )
			strength,intellect,dexterity,corporeity = Love3.g_vehicleData.getSIDC( level, growth )
		nextStepItemID = Love3.g_vehicleData.getCanUpStep( itemID )
			
		vehicleData = {		"id"		: id,
					"srcItemID" 	: itemID,
					"level"		: level,
					"exp" 		: 0,
					"step"          : step,
					"fullDegree"    : int( time.time() ) +  fullDegree ,
					"growth"        : growth,
					"nextStepItemID"     : nextStepItemID,
					"type"          : type,
					"strength"      : strength,
					"intellect"     : intellect,
					"dexterity"     : dexterity,
					"corporeity"    : corporeity,
					"skPoint" 	: 0,
					"deadTime" 	: deadTime,
					"attrSkillBox" 	: [],
					"attrBuffs"	: [],
						}
		
		self.vehicleDatas[id] = vehicleData
		itemName = item.name().split("(")[-1].split(")")[0]
		self.statusMessage( csstatus.VEHICLE_GET_NEW, itemName )
		self.cell.onUseVehicleItemNotify( uid, True )
		self.client.onAddVehicle( vehicleData )

	def useTurnVehicleItem( self, item ):
		"""
		Define Method
		使用转换的骑宠物品
		"""
		uid = item.uid
		# 获取骑宠顺序ID
		id = self.getVehicleID()
		if id == 0:
			self.cell.onUseVehicleItemNotify( uid, False )
			return
		
		itemID 	     = item.id
		level  	     = int( item.queryInt("param1") )
		exp    	     = int( item.queryInt("param2") )
		fullDegree   = int( item.queryInt("param3") )
		growth       = int( item.queryInt("param4") )
		strength     = int( item.queryInt("param5") )
		intellect    = int( item.queryInt("param6") )
		dexterity    = int( item.queryInt("param7") )
		corporeity   = int( item.queryInt("param8") )
		deadTime     = int( item.queryInt("param9") )
		
		otherInfos   = item.queryStr("param10").split(";")
		step         = int( otherInfos[0] )
		type         = int( otherInfos[1] )
		nextStepItemID = int( otherInfos[2] )
		skPoint      = int( otherInfos[3] )
		attrSkillBox = eval( otherInfos[4] )
		attrBuffs    = eval( otherInfos[5] )
		
		vehicleData = {		"id"		: id,
					"srcItemID" 	: itemID,
					"level"		: level,
					"exp" 		: exp,
					"step"          : step,
					"fullDegree"    : fullDegree,
					"growth"        : growth,
					"nextStepItemID": nextStepItemID,
					"type"          : type,
					"strength"      : strength,
					"intellect"     : intellect,
					"dexterity"     : dexterity,
					"corporeity"    : corporeity,
					"skPoint" 	: skPoint,
					"deadTime" 	: deadTime,
					"attrSkillBox" 	: attrSkillBox,
					"attrBuffs"	: attrBuffs }
		self.vehicleDatas[id] = vehicleData
		itemName = item.name().split("(")[-1].split(")")[0]
		self.statusMessage( csstatus.VEHICLE_GET_NEW, itemName )
		self.cell.onUseTurnVehicleItemNotify( uid, True )
		self.client.onAddVehicle( vehicleData )
	
	
	#骑宠激活相关
	def canActivate( self, id ):
		"""
		判断当前是否能够激活坐骑
		"""
		if id not in self.vehicleDatas: return False
		
		# 判断饱腹度
		vehicleData = self.vehicleDatas[id]
		fullDegree = vehicleData["fullDegree"]
		if int( time.time() ) >= fullDegree:
			self.statusMessage( csstatus.VEHICLE_NO_ACTIVATE )
			return False
		
		# 判断过期时间
		deadTime = vehicleData["deadTime"]
		if deadTime != 0:
			nowTime = int( time.time() )
			if nowTime > deadTime:
				self.statusMessage( csstatus.VEHICLE_NO_ACTIVATE )
				return False
		
		return True
	
	def activateVehicle( self, id ):
		"""
		Exposed Method
		通过指定的id激活骑宠
		@param id: 骑宠在玩家数据的唯一标示符
		@type  id:	UINT8
		@return None
		"""
		# 是否能激活
		if not self.canActivate( id ): return
		
		vehicleData = self.vehicleDatas[id]
		# 通知cell召唤
		self.cell.activateVehicle( vehicleData )
	
	
	#骑宠召唤相关
	def canMount( self, id ):
		"""
		判断当前是否能够上坐骑
		"""
		if id not in self.vehicleDatas: return False
		
		# 判断饱腹度
		vehicleData = self.vehicleDatas[id]
		fullDegree = vehicleData["fullDegree"]
		if int( time.time() ) >= fullDegree:
			self.statusMessage( csstatus.VEHICLE_NO_JOYANCY )
			return False
		
		# 判断过期时间
		deadTime = vehicleData["deadTime"]
		if deadTime != 0:
			nowTime = int( time.time() )
			if nowTime > deadTime:
				self.statusMessage( csstatus.VEHICLE_FEED_DIE )
				return False
		return True
		
	def conjureVehicle( self, id ):
		"""
		Exposed Method
		通过指定的id召唤骑宠
		@param id: 骑宠在玩家数据的唯一标示符
		@type  id:	UINT8
		@return None
		"""
		# 是否能召唤
		if not self.canMount( id ): return

		vehicleData = self.vehicleDatas[id]
		# 通知cell召唤
		self.cell.actAndConjureVehicle( vehicleData )


	#骑宠buff相关
	def addVehicleBuff( self, id, buff ):
		"""
		Define method
		添加骑宠buff
		"""
		if id not in self.vehicleDatas:
			return
		self.vehicleDatas[id]["attrBuffs"].append( buff )

	def updateVehicleBuffs( self, id, buffs ):
		"""
		Define method
		更新骑宠buff
		"""
		if id not in self.vehicleDatas:
			return
		self.vehicleDatas[id]["attrBuffs"] = buffs

	#骑宠饱腹度相关
	def addVehicleFullDegree( self, id, fullDegree ):
		"""
		Define Method
		增加饱腹度
		@param fullDegree	: 饱腹度
		@type fullDegree	: UINT16
		@return			: None
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		if int( time.time()) > vehicleData["fullDegree"]:
			fullDegree += int( time.time())
		else:
			fullDegree += vehicleData["fullDegree"]	
		self.setVehicleFullDegree( id, fullDegree )

	def setVehicleFullDegree( self, id, fullDegree ):
		"""
		Define Method
		设置骑宠饱腹度
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		
		currFullDegree = vehicleData["fullDegree"]
		if currFullDegree == fullDegree: return
		#超出了最大值就取最大值
		maxFullDegree = int( time.time() ) + csconst.MAX_FULL_DEGREE
		if fullDegree > maxFullDegree:
			fullDegree = maxFullDegree
		vehicleData["fullDegree"] = fullDegree

		self.cell.onUpdateVehicleFullDegree( id, fullDegree )
		self.client.onUpdateVehicleFullDegree( id, fullDegree )
	
	#传功
	def transVehicle( self, id ):
		"""
		exposed method
		客户端申请传功
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		
		level = vehicleData["level"]
		# 获取当前等级所需经验值
		expMax = Love3.g_vehicleExp.getExp( level )
		self.cell.transVehicle( id, expMax - vehicleData["exp"]  )

	def transAddVehicleExp( self, id, exp ):
		"""
		Define Method
		传功增加骑宠经验值
		@param exp	: 经验
		@type exp	: INT32
		@return		: None
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		itemName = vehicleItem.name().split( "(" )[-1].split( ")" )[0]

		currExp = vehicleData["exp"]
		totalExp = currExp + exp
		level = vehicleData["level"]
		# 获取当前等级所需经验值
		expMax = Love3.g_vehicleExp.getExp( level )

		while totalExp >= expMax:
			totalExp -= expMax
			level += 1
			expMax = Love3.g_vehicleExp.getExp( level )
			if expMax <= 0: break

		vehicleData["exp"] = totalExp
		level = min( 150, level )
		# 通知客户端经验值改变
		self.client.onUpdateVehicleExp( id, totalExp )

		currLevel = vehicleData["level"]
		if currLevel == level: return
		if level > currLevel:	# 骑宠升级提示
			self.statusMessage( csstatus.VEHICLE_LEVEL_UP_POTENTIAL_TRANS, exp, itemName, level )
		vehicleData["level"] = level

		# 设置技能点
		skPoint = ( level - currLevel ) / 2
		self.addVehicleSkPoint( id, skPoint )

		strength,intellect,dexterity,corporeity = Love3.g_vehicleData.getSIDC( level, vehicleData["growth"] )
		vehicleData["strength"] = strength
		vehicleData["intellect"] = intellect
		vehicleData["dexterity"] = dexterity
		vehicleData["corporeity"] = corporeity	

		# 通知cell
		self.cell.onVehiclePropertyNotify( id, level, strength, intellect, dexterity, corporeity, csdefine.VEHICLE_UPDATE_REASON_LEVEL_UP )
		# 通知客户端等级改变
		self.client.onUpdateVehicleProperty( id, level, strength, intellect, dexterity, corporeity, vehicleData["step"], vehicleData["growth"], vehicleData["srcItemID"] )

	def addVehicleExp( self, id, exp ):
		"""
		Define Method
		增加骑宠经验值
		@param exp	: 经验
		@type exp	: INT32
		@return		: None
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		
		currExp = vehicleData["exp"]

		vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		itemName = vehicleItem.name().split("(")[-1].split(")")[0]
		self.statusMessage( csstatus.VEHICLE_ADD_EXP, itemName, exp )
		self.setVehicleExp( id, currExp + exp )

	def setVehicleExp( self, id, exp ):
		"""
		Define Method
		设置骑宠经验值
		@param exp	: 经验
		@type exp	: INT32
		@return		: None
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		level = vehicleData["level"]
		# 获取当前等级所需经验值
		expMax = Love3.g_vehicleExp.getExp( level )

		while exp >= expMax :
			exp -= expMax
			level += 1
			expMax = Love3.g_vehicleExp.getExp( level )
			if expMax <= 0 :break

		vehicleData["exp"] = exp
		level = min(150,level)
		self.setVehicleLevel( id, level )
		# 通知客户端经验值改变
		self.client.onUpdateVehicleExp( id, exp )

	def setVehicleLevel( self, id, level ):
		"""
		Define Method
		设置骑宠的等级
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		currLevel = vehicleData["level"]
		if currLevel == level: return
		if level > currLevel:	# 骑宠升级提示
			vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
			itemName = vehicleItem.name().split("(")[-1].split(")")[0]
			self.statusMessage( csstatus.VEHICLE_LEVEL_UP, itemName, level )
		vehicleData["level"] = level

		# 设置技能点
		skPoint = ( level - currLevel ) /2
		self.addVehicleSkPoint( id, skPoint )
		
		strength,intellect,dexterity,corporeity = Love3.g_vehicleData.getSIDC( level, vehicleData["growth"] )
		vehicleData["strength"] = strength
		vehicleData["intellect"] = intellect
		vehicleData["dexterity"] = dexterity
		vehicleData["corporeity"] = corporeity	
		
		# 通知cell
		self.cell.onVehiclePropertyNotify( id, level,strength,intellect,dexterity,corporeity,csdefine.VEHICLE_UPDATE_REASON_LEVEL_UP )
		# 通知客户端等级改变
		self.client.onUpdateVehicleProperty( id, level,strength,intellect,dexterity,corporeity,vehicleData["step"], vehicleData["growth"], vehicleData["srcItemID"] )

	def setVehicleGrowth( self, id, growth ):
		"""
		Define Method.
		设置骑宠的成长度（暂且只有GM命令用到）
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		currGrowth = vehicleData["growth"]
		if currGrowth == growth: return
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return  #飞行骑宠无效
		vehicleData["growth"] = growth
		level = vehicleData["level"]

		strength, intellect, dexterity, corporeity = Love3.g_vehicleData.getSIDC( level, growth )
		vehicleData["strength"] = strength
		vehicleData["intellect"] = intellect
		vehicleData["dexterity"] = dexterity
		vehicleData["corporeity"] = corporeity

		# 通知cell
		self.cell.onVehiclePropertyNotify( id, level, strength, intellect, dexterity, corporeity, csdefine.VEHICLE_UPDATE_REASON_LEVEL_UP )
		# 通知客户端成长度改变
		self.client.onUpdateVehicleProperty( id, level, strength, intellect, dexterity, corporeity, vehicleData["step"], growth, vehicleData["srcItemID"] )

	#骑宠升阶
	def upStepVehicle( self, mainID, oblationID, needItem ):
		"""
		define method
		骑宠升阶
		"""
		#判断主宠是否满足条件
		vehicleData = self.vehicleDatas.get( mainID )
		if vehicleData is None: return
		nextStepItemID = vehicleData["nextStepItemID"]
		if not nextStepItemID:return #无下一阶对应物品，不能升阶
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return #主骑宠是飞行骑宠不能升阶
		if not nextStepItemID : return #主骑宠本身就不能升阶
		if vehicleData["level"] < U_DATA[ vehicleData["step"] ]["needLevel"]: #判断主骑宠等级
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_NO_LEVEL )
			return
		
		#判断祭宠是否满足条件
		o_vehicleData = self.vehicleDatas.get( oblationID )
		if o_vehicleData is None: return
		if o_vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		if o_vehicleData["step"] != vehicleData["step"]: #主宠和祭宠阶次是不是一样
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NOT_SAME )
			return
		
		#开始升阶
		pro = U_DATA[ vehicleData["step"] ]["successPro"]
		#祭宠消失
		self.vehicleDatas.pop( oblationID )
		self.client.onFreeVehicle( oblationID )
		obItem = g_items.createDynamicItem( o_vehicleData["srcItemID"] )
		obName = obItem.name().split("(")[-1].split(")")[0]
		self.statusMessage( csstatus.VEHICLE_UPSTEP_DELETE_OB, obName )
		
		#通知cell删除、解锁物品
		self.cell.onUpStepVehicle(  )
		
		#获得原骑宠名
		vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		itemName = vehicleItem.name().split("(")[-1].split(")")[0]
			
		if random.random() <= pro: #升阶成功
			#主宠升阶、成长值重新生成
			nextStep = U_DATA[ vehicleData["step"] ]["nextStep"]
			growth = vehicleData["growth"]
			needItem_low = U_DATA[ vehicleData["step"] ]["needItem_low"]
			needItem_high = U_DATA[ vehicleData["step"] ]["needItem_high"]
			
			#主宠属性变化
			if vehicleData["step"] <= nextStep:
				vehicleData["step"] = nextStep
			
			if  needItem  == needItem_low:
				growth = Love3.g_vehicleData.getGrowth( vehicleData["step"], Const.VEHICLE_SOURCE_UP_STEEP_LOW )
			elif needItem == needItem_high:
				growth = Love3.g_vehicleData.getGrowth( vehicleData["step"], Const.VEHICLE_SOURCE_UP_STEEP_HIGH )
			
			vehicleData["growth"] = growth
			level = vehicleData["level"]
			strength,intellect,dexterity,corporeity = Love3.g_vehicleData.getSIDC( level, growth )
			vehicleData["strength"] = strength
			vehicleData["intellect"] = intellect
			vehicleData["dexterity"] = dexterity
			vehicleData["corporeity"] = corporeity
			
			new_nextStepItemID = Love3.g_vehicleData.getCanUpStep( nextStepItemID )
			vehicleData["srcItemID"]      = nextStepItemID
			vehicleData["nextStepItemID"] = new_nextStepItemID
			
			self.cell.onVehiclePropertyNotify( mainID, level,strength,intellect,dexterity,corporeity, csdefine.VEHICLE_UPDATE_REASON_STEP_UP )
			# 通知客户端等级改变
			self.client.onUpdateVehicleProperty( mainID, level, strength, intellect, dexterity, corporeity, nextStep, growth, nextStepItemID )
			
			#获得升阶后骑宠名
			dstVehicleItem = g_items.createDynamicItem( nextStepItemID )
			dstItemName = dstVehicleItem.name().split("(")[-1].split(")")[0]
			
			self.statusMessage( csstatus.VEHICLE_UPSTEP_SUCCESS, itemName, dstItemName )
			self.statusMessage( csstatus.VEHICLE_UPSTEP_SUCCESS_TISHI, itemName, dstItemName )
		else:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_FAILED, itemName )
	
	#骑宠变回物品操作
	def vehicleToItem( self, id, needItem ):
		"""
		Exposed method
		骑宠变回物品
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		self.cell.vehicleToItem( vehicleData, needItem )
		
	def vehicleToItemSuc( self, id ):
		"""
		define method
		骑宠变回物品成功
		"""
		self.freeVehicle( id )


	def freeVehicle( self, id ):
		"""
		Define method
		骑宠放生
		"""
		if id not in self.vehicleDatas: return
		vehicleData = self.vehicleDatas.pop( id )

		vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		itemName = vehicleItem.name().split("(")[-1].split(")")[0]
		self.statusMessage( csstatus.VEHICLE_UPSTEP_DELETE_OB, itemName )
		# 通知客户端
		self.client.onFreeVehicle( id )
	
	
	#骑宠技能点相关
	def addVehicleSkPoint( self, id, skpoint ):
		"""
		增加技能点
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		
		currSkPoint = vehicleData["skPoint"]
		self.setVehicleSkPoint( id, currSkPoint + skpoint )

	def setVehicleSkPoint( self, id, skpoint ):
		"""
		Define Method
		设置技能点
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		if skpoint < 0: skpoint = 0
		currSkPoint = vehicleData["skPoint"]
		if currSkPoint == skpoint: return
		vehicleData["skPoint"] = skpoint
		# 通知cell
		self.cell.onVehicleSkPointNotify( id, skpoint )
		# 通知客户端技能点改变
		self.client.onUpdateVehicleSkPoint( id, skpoint )


	#骑宠存活时间相关	
	def addVehicleDeadTime( self, id, deadTime ):
		"""
		Define Method
		增加存活时间
		@param id		: id
		@type id		: UINT8
		@param deadTime	: 存活时间
		@type deadTime	: INT64
		@return			: None
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		oldDeadTime = vehicleData["deadTime"]
		nowTime = int( time.time() )
		if oldDeadTime < nowTime: oldDeadTime = nowTime

		deadTime += oldDeadTime
		self.setVehicleDeadTime( id, deadTime )

	def setVehicleDeadTime( self, id, deadTime ):
		"""
		Define Method
		设置骑宠存活时间
		"""
		if deadTime > csconst.VEHICLE_DEADTIEM_LIMIT:
			deadTime = csconst.VEHICLE_DEADTIEM_LIMIT
		elif deadTime < csconst.VEHICLE_DEADTIEM_MIN:
			deadTime = csconst.VEHICLE_DEADTIEM_MIN

		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		currDeadTime = vehicleData["deadTime"]
		if currDeadTime == deadTime: return
		addDeadTime = deadTime - currDeadTime

		vehicleData["deadTime"] = deadTime
		# 通知客户端
		self.client.onUpdateVehicleDead( id, addDeadTime )

	def requestVehicleData( self ):
		"""
		客户端请求骑宠数据
		"""
		for vehicleData in self.vehicleDatas.itervalues():
			self.client.onAddVehicle( vehicleData )
		self.client.onInitialized( csdefine.ROLE_INIT_VEHICLES )

	def feedVehicle( self, id ):
		"""
		Exposed method
		骑宠喂食
		"""
		if id not in self.vehicleDatas: return
		
		vehicleData = self.vehicleDatas[id]
		srcItemID = vehicleData["srcItemID"]
		
		self.cell.feedVehicle( id, srcItemID )


	def addVehicleSkill( self, id, skillID ):
		"""
		Define Method
		骑宠学习技能
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		skills = vehicleData["attrSkillBox"]
		if len( skills ) >= csconst.VEHICLE_SKILLS_TOTAL: return

		vehicleData["attrSkillBox"].append( skillID )
		self.cell.onVehicleAddSkillNotify( id, skillID )
		self.client.onVehicleAddSkill( skillID )

	def updateVehicleSkill( self, id, oldSkillID, newSkillID ):
		"""
		Define Method
		技能升级
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		skills = vehicleData["attrSkillBox"]
		index = skills.index( oldSkillID )
		vehicleData["attrSkillBox"][index] = newSkillID
		self.cell.onUpdateVehicleSkillNotify( id, oldSkillID, newSkillID )
		self.client.onVehicleUpdateSkill( oldSkillID, newSkillID )

	def onReceiveTSPet( self, epitome, price ):
		"""
		define method
		获得寄售的宠物
		"""
		self.pcg_addPet_( epitome, csdefine.ADDPET_RECEIVETSPET )
		self.cell.addMoney( -price, csdefine.CHANGE_MONEY_RECEIVETSPET )


	def sellPointCard( self, cardNo, pwd, serverName, cardPrice ):
		"""
		define method
		玩家寄售点卡
		"""
		cardInfo = PointCardInfo()
		cardInfo.cardNo 	= cardNo.lower()
		cardInfo.passWord 	= pwd
		cardInfo.serverName = serverName
		cardInfo.salesName  = self.playerName
		cardInfo.salesAccount = self.accountEntity.playerName
		cardInfo.price		= cardPrice
		cardInfo.salesIP	= self.clientAddr[0]

		BigWorld.globalData["PointCardMgr"].sellPointCard( cardInfo, self )


	def buyPointCard( self, cardNo, money ):
		"""
		define method
		"""
		BigWorld.globalData["PointCardMgr"].buyPointCard( cardNo, money, self, self.playerName, self.accountEntity.playerName )


	def queryPointCards( self, page ):
		"""
		exposed method
		"""
		BigWorld.globalData["PointCardMgr"].queryPointCards( self, page )


	def queryPointCardsByValue( self, page, value ):
		"""
		exposed method
		"""
		BigWorld.globalData["PointCardMgr"].queryPointCardsByValue( self, page, value )


	def onTimer_refreshActivityRecord( self, timerID, userData ):
		"""
		define method
		"""
		self.updateRoleRecord()


	def addTSPet( self, dbid, price, NPCbaseMailbox, roleProcess ):
		"""
		define method
		"""
		epitome = self.pcg_getPetEpitome( dbid )
		NPCbaseMailbox.addTSPet( epitome, price, self.databaseID, self, roleProcess )
		self.pcg_removePet_( dbid, csdefine.DELETEPET_TSPET )



	def queryTishouShopInfo( self, page, params ):
		"""
		exposed method
		"""
		BigWorld.globalData["TiShouMgr"].queryShopInfo( self, page, params )

	def queryTishouItemInfo( self, page, params ):
		"""
		exposed method
		"""
		BigWorld.globalData["TiShouMgr"].queryItemInfo( self, page, params )

	def queryTishouPetInfo( self, page, params ):
		"""
		exposed method
		"""
		BigWorld.globalData["TiShouMgr"].queryPetInfo( self, page, params )

	def takeTSMoneyFromTiShouMgr( self ):
		"""
		exposed method
		"""
		BigWorld.globalData["TiShouMgr"].takeTSMoneyFromTiShouMgr( self, self.getName(), self.databaseID )


	def takeTSItemFromTiShouMgr( self ):
		"""
		exposed method
		"""
		BigWorld.globalData["TiShouMgr"].takeTSItemFromTiShouMgr( self, self.getName(), self.databaseID )


	def takeTSPetFromTiShouMgr( self ):
		"""
		exposed method
		"""
		BigWorld.globalData["TiShouMgr"].takeTSPetFromTiShouMgr( self, self.getName(), self.databaseID )

	def testTakeTishouPets( self, pets ):
		"""
		define method
		"""
		for pet in pets:
			self.client.onStatusMessage( csstatus.RETAKE_PET, str( ( pet.getDisplayName(), ) ) )
			self.onReceiveTSPet( pet, 0 )

	def requestCancelVerify( self ):
		"""
		define method
		客户端申请取消验证
		"""
		Love3.g_antiRobotVerify.cancelVerify( self.id )
		self.antiRobotCount -= 1
		if self.antiRobotCount < 0:
			self.antiRobotCount = 0
		
	def triggerAntiRobot( self ):
		"""
		Define method.
		触发反外挂验证
		"""
		if time.time() - self.antiRobotTime < Const.ANTI_ROBOT_INTERVAL:
			return
		self.antiRobotCount += 1	# 验证了一次
		self.antiRobotTime = time.time()
		Love3.g_antiRobotVerify.triggerVerify( self, self.antiRobotCallback )

	def antiRobotCallback( self, result ):
		"""
		反外挂验证问答结果回调

		@param result : True or False，True表示验证成功，False表示验证失败
		"""
		#DEBUG_MSG( "--->>>player( %s ),result( %s ),self.antiRobotCount( %i )" % ( self.getName(), str( result ), self.antiRobotCount ) )
		if self.isDestroyed:
			return
		if result:
			# 给奖励
			self.cell.onRobotVerifyResult( csstatus.ANTI_ROBOT_FIGHT_VERIFY_RIGHT )
			self.antiRobotCount = 0
		else:
			# 根据self.antiRobotCount的次数继续进行验证
			if self.antiRobotCount < len( csconst.IMAGE_VERIFY_TIME_MAP ):
				self.antiRobotCount += 1
				self.antiRobotTime = time.time()
				Love3.g_antiRobotVerify.triggerVerify( self, self.antiRobotCallback )
			else:
				self.antiRobotCount = 0
				self.cell.onRobotVerifyResult( csstatus.ANTI_ROBOT_FIGHT_VERIFY_ERROR )

	def answerRobotVerify( self, answer ):
		"""
		Exposed method.
		客户端回答验证问题

		@param answer: 鼠标点击图片的坐标点( x, y )
		"""
		Love3.g_antiRobotVerify.verify( self.id, answer )

	# -------------------------------帮会会标相关 by jy-------------------------------
	def onTimer_roleTongSignSender( self, id, arg ):
		"""
		把帮会会标发送的请求处理具体到请求者自己身上
		当玩家角色（请求者）身上有请求队列时，则定时处理自己身上的帮会会标下载请求
		"""
		self.sendTongSignString()
		self.delTimer( self._tongSignSenderTimer )
		self._tongSignSenderTimer = 0
		self._tongSignSenderTimer = self.addTimer( Const.SEND_TONG_SIGN_TIME_TICK, 0.0, ECBExtend.ROLE_TONG_SIGN_SENDER )

	def tongSignSendStart( self, tongDBID, iconMD5, iconStringList ):
		"""
		define method
		开始分包传输会标字符串
		"""
		TongInterface.tongSignSendStart( self, tongDBID, iconMD5, iconStringList )
		self._tongSignSenderTimer = self.addTimer( 0.1, 0.0, ECBExtend.ROLE_TONG_SIGN_PACKS_SENDER )

	def onTimer_roleTongSignPacksSender( self, id, arg ):
		"""
		会标分包发送
		"""
		TongInterface.sendIconPackToClient( self )
		self.delTimer( self._tongSignSenderTimer )
		self._tongSignSenderTimer = 0
		self._tongSignSenderTimer = self.addTimer( 0.1, 0.0, ECBExtend.ROLE_TONG_SIGN_PACKS_SENDER )

	#------------------ItemAwards 领取物品奖励
	def onAwardItem( self, itemList, state = 0 ):
		"""
		领取物品奖励
		"""
		if self.isDestroyed:
			return
		if state == 1:
			self.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )		# 提示没有找到符合条件的奖励
			return
		if state == 2:
			self.statusMessage( csstatus.PCU_YOU_ARE_BUSY )			# 提示之前的请求还在处理中
			return
		self.cell.awardItem( itemList)

	def awardResult( self, ifAward ):
		"""
		是否领取成功
		@define method
		"""
		if ifAward:
			self.itemAwards.awardsSuccess( self.playerName, self.databaseID )
		else:
			self.itemAwards.awardsFailed()

	def awardItem( self, Type, parameter ):
		"""
		请求BASE获取玩家奖励的数据
		@type  Type : UINT8
		@param Type : 领取的类型
		@type  parameter : STRING
		@param parameter : 自定义的扩展参数
		@define method
		"""
		if Type == csconst.AWARDITEM_ACCOUNT:
			self.itemAwards.queryItemByAccount( self.accountEntity.playerName, self.onAwardItem, self.playerName, self.databaseID )
		elif Type == csconst.AWARDITEM_NAME:
			self.itemAwards.queryItemByPlayerName( self.accountEntity.playerName, self.playerName, self.onAwardItem, self.databaseID )
		elif Type == csconst.AWARDITEM_ORDER:
			self.itemAwards.queryItemByOrder( self.accountEntity.playerName, parameter, self.onAwardItem, self.playerName, self.databaseID )
		elif Type == csconst.AWARDITEM_ANO:
			self.itemAwards.queryItemByANO( self.accountEntity.playerName, self.playerName, parameter, self.onAwardItem, self.databaseID )

	# -------------------------------自动战斗限时相关 by jy-------------------------------
	@languageDepart_AFTimer
	def chargeAFTimer( self ):
		"""
		自动战斗充值/计时
		"""
		self.AFExtraTimer = 0
		if self.af_time_extra > 0:
			self.af_time_extra -= (int( time.time() ) - self.role_last_offline)
			self.client.onAFLimitTimeExtraChanged( self.af_time_extra )
			self.AFExtraTimer = self.addTimer( 1, 1.0, ECBExtend.ROLE_AF_TIME_EXTRA )

	def onTimer_roleAFTimeCharge( self, id, arg ):
		"""
		自动战斗充值时刻
		"""
		self.af_time_limit = Const.AUTO_FIGHT_PERSISTENT_TIME_TW
		self.client.onAFLimitTimeChanged( self.af_time_limit )
		self.AFTimer = self.addTimer( 86400, 0.0, ECBExtend.ROLE_AF_TIME_CHARGE )	# 以整数化的时间作为参数

	def onTimer_roleAFTimeExtra( self, id, arg ):
		"""
		自动战斗付费充值时间计时器
		"""
		if self.af_time_extra > 0:
			self.af_time_extra -= 1
			if self.af_time_extra < 0:
				self.af_time_extra = 0
		else:
			self.client.onAFLimitTimeExtraChanged( self.af_time_extra )
			self.delTimer( self.AFExtraTimer )
			self.AFExtraTimer = 0

	def onEnterAutoFight( self ):
		"""
		Exposed
		当进入自动战斗
		"""
		if self.af_time_extra > 0:
			self.client.onAFLimitTimeExtraChanged( self.af_time_extra )
			return
		t = time.time()
		if self.af_time_limit <= 0 or self.isAFing:
			return
		self.isAFing = True
		self.startTickAF = t

	def onLeaveAutoFight( self ):
		"""
		Exposed
		当离开自动战斗了
		"""
		if self.af_time_extra > 0:
			self.client.onAFLimitTimeExtraChanged( self.af_time_extra )
			return
		if not self.isAFing:
			return
		t = time.time()
		self.isAFing = False
		self.af_time_limit -= ( t - self.startTickAF )
		if self.af_time_limit < 0:
			self.af_time_limit = 0
		self.client.onAFLimitTimeChanged( self.af_time_limit )

	def autoFightTimeCharge( self, timeAdd ):
		"""
		define method
		for gm command
		增减自动战斗赠送时间
		"""
		self.af_time_limit += timeAdd
		if self.af_time_limit < 0:
			self.af_time_limit = 0
		self.client.onAFLimitTimeChanged( self.af_time_limit )

	def autoFightExtraTimeCharge( self, timeAdd ):
		"""
		define method
		充值额外的自动战斗时间
		"""
		if self.af_time_extra <= 0:
			self.af_time_extra = 0
			if timeAdd > 0 and self.AFExtraTimer == 0:
				self.AFExtraTimer = self.addTimer( 1, 1.0, ECBExtend.ROLE_AF_TIME_EXTRA )
		self.af_time_extra += timeAdd
		INFO_MSG( "Role charge extra auto fight time. Add: %s, eaf time: %s"%( self.af_time_extra, timeAdd ) )
		self.client.onAFLimitTimeExtraChanged( self.af_time_extra )

	def takeSilver( self ):
		"""
		define method
		"""
		BigWorld.globalData["MessyMgr"].do( csdefine.MESSY_JOB_TAKE_SILVER, self.databaseID, self.accountEntity.databaseID, self, {} )


	def onMessyRecall( self, messyID ):
		"""
		用于处理一些杂乱行为的结束回调
		"""
		BigWorld.globalData["MessyMgr"].onMessyOver( messyID, self.databaseID )


	def sendLoveMsg( self, receiverName, msg, isAnonymity, isSendMail ):
		"""
		Exposed method
		非诚勿扰，发送告白信息
		"""
		if not BigWorld.globalData.has_key( "AS_Feichengwurao" ):
			self.statusMessage( csstatus.FCWR_NOT_START )
			return
		if not self.hasFriend( receiverName ):
			return
		if self.level < 10:
			self.statusMessage( csstatus.FCWR_WRITE_LOVE_MSG_NEED_LEVEL )
			return

		if len( msg ) < csconst.FCWR_LOVE_MSG_MIN_LENGTH or len( msg ) > csconst.FCWR_LOVE_MSG_MAX_LENGTH:
			self.statusMessage( csstatus.FCWR_LOVE_MSG_LENGTH_NOT_FIT )
			return

		curTime = time.time()
		if curTime - getattr( self, "lastSendLoveMsgTime", 0 ) < 1:
			return
		setattr( self , "lastSendLoveMsgTime", curTime )

		self.cell.sendLoveMsg( receiverName, msg, isAnonymity, isSendMail )


	def queryLoveMsgByIndex( self, index ):
		"""
		Exposed method
		"""
		BigWorld.globalData["FeichengwuraoMgr"].queryLoveMsgByIndex( self, index )


	def queryLoveMsgsByRange( self, rangeIndex ):
		"""
		Exposed method
		"""
		BigWorld.globalData["FeichengwuraoMgr"].queryLoveMsgsByRange( self, rangeIndex )


	def queryLoveMsgsByReceiverName( self, playerName ):
		"""
		Exposed method
		"""
		BigWorld.globalData["FeichengwuraoMgr"].queryLoveMsgsByReceiverName( self, playerName )


	def queryLoveMsgsBySenderName( self, playerName ):
		"""
		Exposed method
		"""
		BigWorld.globalData["FeichengwuraoMgr"].queryLoveMsgsBySenderName( self, playerName )


	def voteLoveMsg( self, index, chooseSubject ):
		"""
		Exposed method
		"""
		if not BigWorld.globalData.has_key( "AS_Feichengwurao" ):
			self.statusMessage( csstatus.FCWR_NOT_START )
			return
		BigWorld.globalData["FeichengwuraoMgr"].voteLoveMsg( self, self.databaseID, self.playerName, index, chooseSubject )

	def queryLoveMsgsResult( self ):
		"""
		Exposed method
		"""
		BigWorld.globalData["FeichengwuraoMgr"].queryLoveMsgsResult( self )

	# ----------------------------一键换装 by 姜毅---------------------------------
	def addSuit( self, suitIndex, suitName, suitEquips ):
		"""
		Exposed method
		添加新套装
		"""
		BigWorld.globalData["OneKeySuitMgr"].addSuit( self.databaseID, suitIndex, suitName, suitEquips, self )

	def updateSuit( self, suitIndex, suitEquips ):
		"""
		Exposed method
		更新已有套装
		"""
		BigWorld.globalData["OneKeySuitMgr"].updateSuit( self.databaseID, suitIndex, suitEquips, self )

	def initSuit( self ):
		"""
		角色上线时初始化角色套装
		"""
		self.switchEquipTick = 0.0	# 换装的时间记录，作为限制换装行为过于频繁的手段
		BigWorld.globalData["OneKeySuitMgr"].getSuitDatas( self.databaseID, self )

	def renameSuit( self, suitIndex, suitName ):
		"""
		Exposed method
		重命名套装
		"""
		BigWorld.globalData["OneKeySuitMgr"].updateSuitName( self.databaseID, suitIndex, suitName, self )

	def onSwitchSuit( self, suitIndex ):
		"""
		Exposed method
		更换装备通知
		"""
		#t = time.time()
		#if t - self.switchEquipTick < Const.OKS_TIME_INTERVAL:
		#	print "hey too hurry."
		#	return
		self.oksIndex = suitIndex
		self.switchEquipTick = time.time()
		self.client.onSwitchSuit( suitIndex )
	# ----------------------------一键换装---------------------------------

	def queryMatchLog( self ):
		"""
		Exposed method.
		玩家查询比赛日志信息
		"""
		RoleMatchRecorder.query( self )

	def updateMatchLog( self, matchType, scoreOrRound ):
		"""
		Define method.
		更新比赛日志

		@pram matchType:UINT8，比赛类型，定义在csdefine中的MATCH_TYPE_***
		@param scoreOrRound: INT32，活动日志数据，本次参赛获得积分 或 本次参赛获得名次
		"""
		RoleMatchRecorder.update( self.databaseID, matchType, scoreOrRound, self )
	
	#飞翔传送相关	
	def getAllVehicleDatasFromBase( self ):
		"""
		Define method.
		获得玩家所有的飞行坐骑的modelNumber
		"""
		self.cell.onGetAllVehicleDatas( self.vehicleDatas )
	
	def baoZangBroadCastEnemyPos( self, enemyId, pos ):
		"""
		Exposed method.
		宝藏副本广播敌人位置给队友
		"""
		for mailbox in self._teamMembers.itervalues():
			if mailbox:
				mailbox.client.baoZangOnReceiveEnemyPos( enemyId, pos )
	
	def baoZangBroadCastDisposeEnemy( self, enemyId ):
		"""
		Exposed method.
		宝藏副本广播队友敌人不在我的AOI
		"""
		for mailbox in self._teamMembers.itervalues():
			if mailbox:
				mailbox.client.baoZangOnDisPoseEnemy( enemyId )
				
#-------------------------------------------------------------------
#劲舞时刻
#-------------------------------------------------------------------
	def noticeDanceMgrIsChallenged(self, challengeIndex):
		#Exposed method
		BigWorld.globalData["DanceMgr"].indexIsChallenged(self, challengeIndex, True) #参数True表示这个challengeIndex位置有人在挑战
		
	def canChallengeDanceKing(self, challengeIndex):
		#exposed method
		BigWorld.globalData["DanceMgr"].canChallengeDanceKing(self, challengeIndex, self.playerName)

	def enterWuTing(self):
		#defined method
		BigWorld.globalData["DanceMgr"].addPlayerMailbox(self.databaseID, self)

	
	def leaveWuTing(self):
		BigWorld.globalData["DanceMgr"].removePlayerMailbox(self.databaseID)
		
	#远程获取玩家装备信息
	def queryRoleEquipItems( self, queryName ):
		"""
		exposed method.
		通过名字，远程查询玩家装备
		"""
		Love3.g_baseApp.queryRoleEquipItems( self, queryName )
		
		
	def setJueDiFanJiState( self, state ):
		"""
		设置绝地反击活动状态，以便在玩家销毁的时候通知管理器做相应的事情
		"""
		self.jueDiFanJiState = state
		
# end of class: Role
