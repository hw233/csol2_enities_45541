# -*- coding: gb18030 -*-
#
# $Id: Role.py,v 1.119 2008-09-05 03:50:30 zhangyuxing Exp $


"""
��ҽ�ɫ��Base���֡�

"""

# python
import sys
import _md5
import time
import cPickle
import random
# ����
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

# Role �Ļ���
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

# from ��ʽ�� import
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
	�����԰汾���������� by ����
	"""
	@staticmethod
	def locale_big5( role ):
		"""
		�����
		"""
		languageDepart_AFTimer.originalFunc( role )
		isoverday = role.checkOverDay()
		if isoverday:
			role.af_time_limit = int( Const.AUTO_FIGHT_PERSISTENT_TIME_TW )
			role.client.onAFLimitTimeChanged( role.af_time_limit )
		today0tick = role.getToday0Tick()
		leftTime = ( today0tick + 86400 - int( time.time() ) )
		INFO_MSG( "Role charge auto fight time. Is over day:%s, today 0 tick:%s ,left time:%s, auto fight time:%s, last offline:%s."%( isoverday, today0tick, leftTime, role.af_time_limit, role.role_last_offline ) )
		role.AFTimer = role.addTimer( leftTime, 0.0, ECBExtend.ROLE_AF_TIME_CHARGE )	# ����������ʱ����Ϊ����

class Role(
	BigWorld.Proxy,						#
	GameObject,							#
	BaseECBExtend,						# ��չ��onTimer����
	OPRecorder,							# �ͻ��˲�����¼( hyw )
	QuickBar,							# �����( wanhaipeng )
	RoleChat,							# ��Ϣ( hyw )
	Team,								# ���
	Bank,								# Ǯׯ( wsf )
	RoleImageVerify,
	SpaceFace,							# �ռ����(pck)
	PostInterface,						# �ʼ�ϵͳ(pck)
	PetCage,							# ����
	RoleMail,							# �ʼ�ϵͳ(zyx)
	RoleRelation,						# ��ҹ�ϵ( wsf )
	ItemsBag,							# ����( phw )
	TongInterface,						# ���ϵͳ(kebiao)
	RoleCredit,							# �����������( wangshufeng )
	AntiWallow,						# ������ϵͳ
	RoleSpecialShop,					# ��ɫ�̳�(wangshufeng & huangyongwei)
	RoleGem,							# ��ɫ����ʯ( wsf )
	RoleQuizGame,						# ��ɫ֪ʶ�ʴ�( wsf )
	PresentChargeUnite,					# ��Ʒ�ͳ�ֵ��ȡģ��( hd )
	GameRanking,						# ���а�ϵͳ
	LivingSystem,						# ����ϵͳ( jy )
	YuanBaoTradeInterface,				# Ԫ������( jy )
	CopyMatcherInterface,				# �������ϵͳ�����ӿ�
	RoleCampInterface, 					# ��Ӫ
	ZhengDaoInterface,					# ֤��ϵͳ
	Fisher,								# �������
	):
	"""
	��ҽ�ɫBase���֡�
	@ivar 		spaceManager :	����������Mailbox��������ת��ʱʹ��
	@type 		spaceManager :	mailbox
	"""
	def __init__(self):
		"""
		���캯����
		"""
		INFO_MSG("now init base role  %s..............." % self.cellData["playerName"] )
		# ����ģ��
		BigWorld.Proxy.__init__( self )
		BaseECBExtend.__init__( self )
		OPRecorder.__init__( self )
		TongInterface.__init__( self )
		RoleCredit.__init__( self )
		AntiWallow.__init__( self )
		# ������ʼ��
		self.spaceManager = BigWorld.globalData["SpaceManager"]

		# ����ģ��2
		Team.__init__( self )
		RoleChat.__init__ ( self )

		INFO_MSG("now init base role  %s datas..............." % self.cellData["playerName"] )
		# ��չģ��
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

		# �����
		QuickBar.__init__( self )

		Fisher.__init__( self )

		# ��ʱ����
		self._lasttime = BigWorld.time()

		self._isLogout = False						# ��ʾ�Լ��Ƿ�Ϊ��ע��,�������ᱻ�ͻؽ�ɫѡ�����

		self.frozenGold = 0			# ������Ľ�Ԫ��
		self.frozenSilver = 0		# ���������Ԫ��

		# ���ڱ�ʶ��ҵ���Ʒ�����Ƿ���Ч
		# �����Ч�����onClientGetCell()��ʱ�������߳�
		self.validItemData = True

		# ���MD5У��ʧ�������onClientGetCell()ʱ���������
		self.validMD5Check = True

		# ��ʼ������cellData
		# ���entityû�д浽db�У���databaseIDΪ0��
		# �������ڵĴ�������¼������˵��Ӧ�ò�����ִ����
		# ���ڵĻ����Ǵ���һ��entity��ֱ�ӱ�saveToDB()��destroy()��
		self.cellData["databaseID"] = self.databaseID

		# �����û����͵ȼ�
		self.playerName = self.cellData["playerName"]
		self.level = self.cellData["level"]
		self.raceclass = self.cellData["raceclass"]
		self.grade = self.cellData["grade"]
		self.headTextureID = self.cellData["headTextureID"]
		self.last_login_ip = 0		#��ʼ����½IP

		# �������֤���ݣ�16:04 2009-11-12��wsf
		self.antiRobotTime = time.time() + 600		# ���һ����֤ʱ�䣬�������10���Ӻ�ſ�ʼ��֤
		self.antiRobotCount = 0		# �ڼ�����֤
		self._tongSignSenderTimer = None		# ����귢�ͼ�ʱ��
		self.accountName = ""				# ��ʼ���˺���Ϊ��
		self.itemAwards = ItemAwards()		# ��ȡ��Ʒģ��

		# �Զ�ս��ʱ�� by ����
		self.isAFing = False		# �Ƿ��Զ�ս��״̬
		self.startTickAF = 0.0	# �Զ�ս����ʼʱ��

		# �ϴ���ȡ�ܹ��ʵ�ʱ�䣬�˱�������������ҿ�����ͬһ��tick�ڽ��ж������
		self.getWeekOnlineGiftTime = 0.0

		INFO_MSG("now init base role %s end..............." % self.playerName )

	def fixTimeReward( self ):
		if self.level > csconst.OLD_REWARD_LEVEL_LIM:			# ����60����û�н�����
			return
		if len( self.receivedRewardTick ) >= g_onlineReward.getCount():	# ��ʵû���ܴ��ڣ�ֻ�������ݳ�����
			if self.checkOverDay():		# ���ϴ������Ƿ��ѹ���0ʱ��������ˢ�½�����¼
				self.oldRewardReflash()
			self.oldPlayerReward()
			self.oldPlayerRewardTimeReflash()		# ����timer��0��ˢ���콱��¼
		else:
			self.newPlayerReward()
			
	def newPlayerReward( self ):
		"""
		���ֽ���
		"""
		lifeTime = self.getNowlifetime()
		# ֪ͨcell����һ����������ʾ���ͻ���
		rewardNum = len( self.receivedRewardTick )
		self.cell.sendNextAwarderToClient( lifeTime, rewardNum,0 )
		
	def confirmToReceiveNewPlayerReward( self ):
		"""
		Exposed method
		��Ӧ�ͻ�����ȡ���ֽ���������
		"""
		lifeTime = self.getNowlifetime()
		rewardNum = len( self.receivedRewardTick )+1
		self.cell.giveNewPlayerReward( lifeTime, rewardNum )
		
	def addRewardRecord( self, rewardTick ):
		"""
		define method
		�����콱��¼
		"""
		self.receivedRewardTick.append( rewardTick )
		if len( self.receivedRewardTick ) == g_onlineReward.getCount():	# ������ֽ���û�ˣ��Ϳ�ʼ�����ֽ���
			self.oldPlayerReward()

	def oldPlayerReward( self ):
		"""
		���ֽ���
		"""
		if self.level > csconst.OLD_REWARD_LEVEL_LIM:
			return
		levelLimit = max( self.level/10, 3 )	# �õȼ�������ȡ
		if self.dailyRewardTimes >= levelLimit:	# ����Ľ���������
			return
		
		timer = self.oldPlayerRewardTick - self.getNowlifetime()
		if timer < 0:timer = Const.OLD_REWARD_WAIT_LIM_SECONDS	# ���ʱ����Ҿ͵�10������Ϊ����
		
		onlineTime = self.getNowlifetime() - self.lifetime
		if onlineTime < 10:								# ���ڸ����ߴ���������ʱ��
			self.client.onOldFixTimeReward( timer, self.dailyRewardTimes , 0, 0 )	# ֪ͨ�ͻ�����һ�ν���ʾ
			
	def confirmToReceiveOldPlayerReward( self ):
		"""
		Exposed method
		��Ӧ�ͻ�����ȡ���ֽ���������
		"""
		self.cell.giveOldPlayerReward( self.dailyRewardTimes )
		self.dailyRewardTimes += 1
		self.oldPlayerRewardTick = Const.OLD_REWARD_WAIT_LIM_SECONDS + Const.OLD_REWARD_WAIT_LIM_SECONDS * self.dailyRewardTimes + self.getNowlifetime()
		self.oldPlayerReward()

	def oldRewardReflash( self ):
		"""
		ˢ�¶�ʱ���ֶ�ʱ�������� by ����
		"""
		INFO_MSG( "oldRewardReflash: dailyRewardTimes %i , oldPlayerRewardTick %i ."%(  self.dailyRewardTimes, self.oldPlayerRewardTick ) )
		self.dailyRewardTimes = 0
		self.oldPlayerRewardTick = 0

	def oldPlayerRewardTimeReflash( self ):
		"""
		��ʱˢ�����ֽ�����ʱ�� by����
		"""
		nowTime = int( time.time() )
		nowDayTime = int( self.getToday0Tick() )	# ���յ�0ʱ��
		leftTime = 3600 * Const.OLD_REWARD_REFLASH_TIME + nowDayTime - nowTime + 60	# ����1���ӵ����
		INFO_MSG( "oldPlayerRewardTimeReflash:%i"%(leftTime) )
		self.reflashTimer = self.addTimer( leftTime, 0.0, ECBExtend.FIX_TIME_OLD_PLAYER_REWARD_REFLASH )
		
	def onTimer_fixTimeOldPlayerReflash( self, id, arg ):
		"""
		ˢ�����ֽ������� by����
		"""
		self.delTimer( self.reflashTimer )
		self.oldRewardReflash()
		self.oldPlayerReward()
		self.reflashTimer = self.addTimer( 3600 * Const.OLD_REWARD_REFLASH_TIME, 0.0, ECBExtend.FIX_TIME_OLD_PLAYER_REWARD_REFLASH )
		
	def requestInitialize( self, initType ) :
		"""
		<Exposed/>
		�����ʼ��( hyw -- 2008.06.05 )
		@type				initType : MACRO DEFINATION
		@param				initType : ��ʼ�����ͣ��� csdefine.py �ж���
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
		��ȡͷ��ͼ��ID
		"""
		if self.headTextureID is None: return 0
		return self.headTextureID

	def getNowlifetime( self ):
		"""
		��ȡ��ǰ�����������ʱ��
		ע:����ֱ��ʹ��lifetime��Ϊlifetime��ÿ������ʱ�ż�¼
		"""
		return self.lifetime + BigWorld.time() - self._lasttime

	def clientDead( self ):
		"""
		�Ͽ��ͻ��ˡ�
		"""
		INFO_MSG( "Help: The base just told us (id %d) we're dead!" % self.id )
		self.onLeaveAutoFight()
		self.liv_onLeave()
		self.logoff()

	def logoff( self ):
		"""
		������ߡ�
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
		��λ���λ�����ڳ��������������cellʵ��׼����
		"""
		INFO_MSG("now role %s enabled..............."  % self.playerName )
		self.last_login_ip = self.clientAddr[0]	#��¼�������¼��IP
		if hasattr( self, "cellData" ) and self.cellData != None:
			"""
			#INFO_MSG( "%s: login to '%s' space." % ( self.cellData["playerName"], self.cellData["spaceType"] ) )
			self.addMailboxCallback( self.spaceManager, [self.cellData["spaceType"], "cell"], CBF_ROLE_GETSTARTSPACE, "onGetStartSpace" )
			"""
			# check uid of items of kitbags

			# ������ݿ�ĳЩ�ֶξ����Ƿ��޸ģ�ֱ���߳� by ����
			self.checkPropertyMD5( self.cellData )

			self.itemDataCheck( self.cellData["itemsBag"], self.bankItemsBag )

			self.onRestoreCooldown( self.cellData["attrCooldowns"] )	# ����entityMailbox�Ƿ���ڣ����Ƕ�����ָ�cooldown
			self.onRestoreBuffs( self.cellData["attrBuffs"] )
			self.onCheckLoopQuestLogs( self.cellData["loopQuestLogs"] )	# ��黷�����¼���������������
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
		��¼��ɫ���ߵ���־
		"""
		try:
			g_logger.roleLogonLog( self.databaseID, self.getName(), self.accountName, self.getNowlifetime(), self.clientAddr[0], cschannel_msgs.ROLE_INFO_2 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onGetCell(self):
		"""
		cell ʵ�崴����ɡ�
		"""
		INFO_MSG("now role %s getCell..............."  % self.playerName )
		# ע�ᵽ����baseapp��ȫ���б��У�������������Ҫ�������ֲ���player��ֱ����ѭ����player�ĵط�
		Love3.g_baseApp.registerPlayer( self )
		self.updateRoleRecord()
		self.logonForTeam()		# ����ϵͳ���������
		self.postLogon()		# �ʼ�ϵͳ��¼
		RoleRelation.onGetCell( self )
		PetCage.onGetCell( self )
		RoleChat.onGetCell( self )
		AntiWallow.onGetCell( self )
		ZhengDaoInterface.onGetCell( self )
		BigWorld.globalData["MessyMgr"].requestRoleMessyInfo( self.databaseID, self.accountEntity.databaseID )
		BigWorld.globalData["CommissionSaleMgr"].queryForLogin( self, self.playerName )	# ����ϵͳ
		self.pcu_takeThings( csconst.PCU_TAKECHARGE, 0 )	# ������߸����Լ��ĳ�ֵ��Ϣ

		#��������֪ͨ���ң���ɫ�����ˡ�
		apexProxy = Love3.g_apexProxyMgr.onGetApexProxy()
		if(apexProxy.getApexStartFlag()):
			apexProxy.noticeApexProxyMsgL(self.id,self.getName(),len(self.getName( )))
			apexProxy.noticeApexProxyMsgS(self.id,self.clientAddr[0])
			self.client.startClientApex( )#֪ͨ�ͻ����𶯷����

		if self.level >= csconst.QUIZ_MIN_LEVEL_LIMIT and ( BigWorld.globalData.has_key( "QuizGame_start" ) and BigWorld.globalData[ "QuizGame_start" ] == True ):	# ���ߣ�֪ʶ�ʴ��ڽ�����
			BigWorld.globalData["QuizGameMgr"].onRoleGetCell( self )

		BigWorld.globalData["WuDaoMgr"].updateDBIDToBaseMailbox( self.databaseID, self )		# ����������DBIDToBaseMailbox

		# ���һ��ʼ�Ͷ�ʧ��client��Ҳ��û�д��ڵļ�ֵ�ˡ�
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
		# ����ʱ�ӱ��ص�baseappȫ���б���ȥ���Լ�
		# ������ÿ��ܻ�����쳣���������ú���Ĵ��������ȥ��
		try:
			Love3.g_baseApp.deregisterPlayer( self )
		except:
			EXCEHOOK_MSG( "onLoseCell: %s(%i)" % ( self.getName(), self.id ) )

		# �������µ������ռ����������
		# ��ʹ��team_onLogout()��������˶���������ã�
		# ��ĳЩ�������Ȼ����_teamMembers�����ж�����������ã�
		# ��ˣ������ڵ���team_onLogout()֮ǰ�Ĵ���������쳣��
		# ���ԣ���team_onLogout()�����Ƶ���ǰ�档
		# ����ϵͳ���������
		#��������buff���ۼ�ʱ��	
		self.team_onLogout()

		PetCage.onLoseCell( self )
		RoleRelation.onLoseCell( self )
		AntiWallow.onLoseCell( self )
		# �ǳ����ϵͳ
		self.tong_onLogout()

		# �������ͨ���ռ�
		#self.offLineOfSpace()

		# �ʼ�ϵͳͨ��ͨ��
		self.postLogout()

		# Ԫ�������˳�
		self.ybt_onLeave()

		self.destroySelf()
		
		#�����˳��������
		self.cmi_onLogout()
		
		# ֪ʶ�ʴ�����֪ͨ
		if self.level > csconst.QUIZ_MIN_LEVEL_LIMIT and BigWorld.globalData.has_key( "QuizGame_start" ):
			BigWorld.globalData["QuizGameMgr"].playerQuit( self.databaseID )

		BigWorld.globalData["WuDaoMgr"].delDBIDToBaseMailbox( self.databaseID )		# ���ߺ�ɾ��������DBIDToBaseMailbox


	def logout( self ):
		"""
		ע������¼����

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
		�ͻ��˶Ͽ�����ͨ���������������߲�����
		"""
		DEBUG_MSG( "The base just told us (id %d) we're dead!" % self.id )
		try:
			g_logger.roleLogoutLog( self.databaseID, self.getName(), self.accountName, self.getNowlifetime(), self.clientAddr[0], cschannel_msgs.ROLE_INFO_1 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		#RoleImageVerify.stopVerifyCount( self )	������1.8.1��ȱ����Ӧ��gd�⣬������ͣ
		PetCage.onClientDeath( self )
		self.onLeaveAutoFight()
		self.liv_onLeave()
		self.ybt_onLeave()
		self.cmi_onLogout()
		self.destroySelf()


	def destroySelf( self ):
		"""
		�����Լ�
		"""
		#֪ͨ����ҡ�����ɫ����
		Love3.g_apexProxyMgr.onGetApexProxy( ).noticeApexProxyMsgG( self.id,self.getName(),len(self.getName( )) )
		if self.jueDiFanJiState:
			BigWorld.globalData[ "JueDiFanJiMgr" ].onJueDiFanJiRoleDestroy( self.databaseID )
		if hasattr( self, "cell" ):
			# for catch "ValueError: Base.destroyCellEntity: Base xxxxx is in the process of creating an associated cell entity."
			# �������ִ��󣬽������һ�£����ǻ���onGetCell()�ص����ж���ҵ�ǰ�Ƿ���client�����û�����ٴ�destroy�Լ���
			# ��ǰ��־�����Ϊ����֤��onGetCell()��ȷʵ����������Ϊ������ȷ�Ϻ����ɾ������쳣�������
			try:
				self.destroyCellEntity()
			except ValueError, errstr:
				EXCEHOOK_MSG( "destroySelf: %s(%i)" % ( self.getName(), self.id ) )
		else:
			# �����account entity��һ��Ҫ֪ͨaccount entity
			if self.accountEntity is not None:
				if self._isLogout and self.hasClient and not self.accountEntity.hasClient:
					# �����ע�������Լ���һ��client�������Լ���accountEntityû��client������԰�client����account��
					# ��Ҫ�ж�accountEntity.hasClient��Ϊ�˱�����Ҷ��ߺ����µ�¼�����һ̨����ʹ����ͬ�ʺŵ�¼ʱע���ɵĽ�ɫ���裬
					self.giveClientTo( self.accountEntity )		# �ѿ���Ȩ����account��
				self.accountEntity.onAvatarDeath()				# ֪ͨaccount�������ڵ���giveClientTo()֮����ã��꿴Account::onAvatarDeath()
			else:
				INFO_MSG( "%s(%i): is not account entity." % (self.getName(), self.id) )
			self.destroy()	# destroy�����ڵ���giveClientTo()֮�����

	def onClientGetCell( self ):
		"""
		If present, this method is called when the message to the client that it now has a cell is called.
		"""
		self.loginTime = time.time()		# ֻ��client�����cell�ű���Ϊ�ǵ�¼�ˡ�
		self._lasttime = BigWorld.time()	# ��ʱ����
		#RoleImageVerify.firstVerifyCount( self )	������1.8.1��ȱ����Ӧ��gd�⣬������ͣ
		PetCage.onClientGetCell( self )
		self.cell.onCellReady()
		self.client.updateGold( self.gold, csdefine.CHANGE_GOLD_INITIAL )
		self.client.updateSilver( self.silver, csdefine.CHANGE_SILVER_INITIAL )
		self.tong_onLogin()		# ������ߵ�½���ϵͳ
		#self.statusMessage( csstatus.ACCOUNT_STATE_SERVER_VERSION, Love3.versions ) ע���յ�¼ʱ�İ汾��ʾ��Ŀǰ�Ѳ���Ҫ
		if self.firstLoginTime == 0:				# ��¼��ɫ�����ʺź��һ�ε�½��������ʱ��
			self.firstLoginTime = int( time.time())
			self.writeToDB()
		self.accountEntity.onAvatarClientGetCell()
		Fisher.onClientGetCell( self )
		
		# �����ͨ�����ݿ��ֶ�MD5У�飬ֱ���߳�
		if not self.validMD5Check:
			self.statusMessage( csstatus.ROLE_DATA_MD5_CHECK_ERROR )
			self.logoff()

		# �����Ʒ���ݲ��Ϸ���ֱ���߳�
#		if not self.validItemData:
#			self.statusMessage( csstatus.ROLE_ITEM_CHECK_ERROR )
#			self.logoff()

		self.fixTimeReward()	# ��ʱ���߽��� by����
		self.chargeVimTimer()	# ����ֵ��ֵ��ʱ by ����
		self.chargeAFTimer()	# �Զ�ս��ʱ���ֵ by ����
		self.initSuit()			# ��ʼ����ɫһ����װ by ����
		# ����귢�ͼ�ʱ�� by ͬ��
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
		if t > 1:	# ����Ҫ1��
			self.lifetime += t
			self._lasttime = now
			daysSec = 24 * 3600
			wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)
			if not self.weekOnlineTime.has_key(wT):
				if len(self.weekOnlineTime) >= 2:		# weekOnlineTimeֻ��Ҫ���汾�ܡ����ܵ�����ʱ��
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
		����Role���Ի�û���Role�ֶε�MD5�� by ����
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
		����Role��������Role����ҪУ����ֶε�MD5У���� by ����
		"""
		if not self.validMD5Check: return
		self.baseSectionMD5Code = self.calcPropertyMD5Code( cellData )

	def checkPropertyMD5( self, cellData ):
		"""
		����Role���Լ��Role����ҪУ����ֶε�MD5У���� by ����
		"""
		if not Const.MD5Checker_Switcher: return
		if self.baseSectionMD5Code == self.calcPropertyMD5Code( cellData ):
			INFO_MSG( "%s[%i]MD5 check successed��"%( self.getName(), self.id ) )
			self.validMD5Check = True
		else:
			ERROR_MSG( "%s[%i]MD5 check failed��your database may be modified nonlicet��"%( self.getName(), self.id ) )
			self.validMD5Check = False

	def onSaveCooldown( self, cooldownsInstance ):
		"""
		cooldownд�����ݿ�ʱ�Ĵ���
		"""
		dels = []
		for cd in cooldownsInstance:
			try:
				cooldown = Love3.g_cooldowns[ cd ]
			except KeyError:
				dels.append( cd ) 	# cooldown ���Ͳ�������ɾ����������Ŀ������ֶ��޸������ݿ��������Ѵ��ڵľɵ�cooldown
				continue

			cdData = cooldownsInstance[ cd ]
			endTime = cdData[ 2 ]
			if cooldown.isTimeout( endTime ):
				dels.append( cd )	# ɾ���ѹ�ʱ��cooldown
				continue

			if cooldown.isSave():
				cooldownsInstance[ cd ] = cooldown.calculateOnSave( cdData )
			else:
				dels.append( cd )	# �������cooldownȫ��ɾ��

		for cd in dels:
			cooldownsInstance.pop( cd )

	def onRestoreCooldown( self, cooldownsInstance ):
		"""
		�ָ�cooldown���������㣬���ô˷�����Ч�����ڵ���createCellEntity()֮ǰ����
		"""
		#INFO_MSG( "start", cooldownsInstance )
		dels = []
		for cd in cooldownsInstance:
			try:
				cooldown = Love3.g_cooldowns[ cd ]
			except KeyError:
				dels.append( cd ) 	# cooldown ���Ͳ�������ɾ����������Ŀ������ֶ��޸������ݿ��������Ѵ��ڵľɵ�cooldown
				continue

			cdData = cooldownsInstance[ cd ]
			cooldownsInstance[ cd ] = cooldown.calculateOnLoad( cdData )
			endTime = cooldownsInstance[ cd ][2]
			# ��coolDown���ݻָ�֮������жϣ�ɾ���ѹ�ʱ��coolDown
			if cooldown.isTimeout( endTime ):
				dels.append( cd )

		#INFO_MSG( "deletes", dels )
		for cd in dels:
			cooldownsInstance.pop( cd )
		#INFO_MSG( "end", cooldownsInstance )

	def onSaveBuffs( self, buffsInstance ):
		"""
		buff�����ݿ���д��ʱ�Ĵ���
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

		rmb.reverse()	# �Ӻ�����ǰɾ��
		for r in rmb:
			buffsInstance.pop( r )
		#INFO_MSG( "--> buffs calculate after:", buffsInstance )


	def onRestoreBuffs( self, buffsInstance ):
		"""
		�ָ�buff���������㣬���ô˷�����Ч�����ڵ���createCellEntity()֮ǰ����
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
			t = spell.calculateOnLoad( buff["persistent"] )	# �����Ȼָ�������ж�buff�Ƿ����
			buff[ "persistent" ] = t

		rmb.reverse()	# �Ӻ�����ǰɾ��
		for r in rmb:
			buffsInstance.pop( r )

		# �����һ��δ��buff,��������ڵ�¼���̲����˺�
		if self.cellData["state"] != csdefine.ENTITY_STATE_DEAD:
			tempTime = int( 30 + time.time() )
			notHasBuff = True

			for buff in self.cellData["attrBuffs"]:
				if buff[ "skill" ][ "id" ] == csconst.PENDING_BUFF_ID:	# �������Ѿ�����δ��buff,ֻ����δ��buff��persistentʱ��
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
		���ÿ��������εĻ�������������������뵱ǰ���ڲ�һ��������������Ա����ۻ���������
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
		���±��ݵ�level��������Դ��cellApp
		"""
		oldLevel = self.level
		self.level = level

		self.tong_onLevelChanged()	# �ȼ��仯,֪ͨ���
		self.rlt_onLevelUp()			# �ȼ��仯��֪ͨ��ϵ��
		self.zd_onLevelUp()				# �ȼ��仯��֪֤ͨ��ϵͳ

		try:
			g_logger.roleUpgradeLog( self.databaseID, self.getName(), oldLevel, self.level, self.getNowlifetime() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def itemDataCheck( self, kitbagsInstance, bankBags ):
		"""
		��鱳���Ͳֿ���������Ʒ�Ƿ�����ͬ��uid��
		���������������е���Ʒ���ݡ�

		@param kitbagsInstance: ��ɫ����ʵ��
		@param bankBags: ��ɫ���а�ʵ��
		"""
		uids = set()
		for kitbag in ( kitbagsInstance, bankBags ):
			for item in kitbag.getDatas():
				if item.uid not in uids:
					uids.add( item.uid )
				else:
					#�������ͬUID��Ʒ�Ĵ���
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
			# ���������ʱ�����logout�������������崻������������µĴ���
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
		�Ա������ֿ���ӵ�е���ͬUID��Ʒ�Ĵ���
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
		#��¼�������
		tempDict = recordItem.addToDict()
		del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
		itemData = BigWorld.escape_string( cPickle.dumps( tempDict, 2 ) )
		query = "insert ignore into custom_sameUIDItemTable ( sm_itemUID, sm_roleDBID, sm_recordTime, sm_Item )Value ( %d, %d,%d,\'%s\' )"% ( recordItem.uid, self.databaseID, int( time.time() ), itemData )
		BigWorld.executeRawDatabaseCommand( query,  self.__onInsertRecord )
		#�Ƴ��ֿ��е�item
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
		��������ڵ�cellapp���ˣ�base�ڻָ����cell����ʱ���Զ�����
		"""
		#��ʱֻ������ͬuid���
		self.itemDataCheck( self.cellData["itemsBag"], self.bankItemsBag )

	def getGender( self ):
		"""
		�����ҵ��Ա�
		"""
		return self.raceclass & csdefine.RCMASK_GENDER

	def getClass( self ):
		"""
		ȡ������ְҵ
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def getCamp( self ):
		"""
		ȡ��������Ӫ
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_CAMP ) >> 20

	# ----------------------------------------------------------------
	# ���̰���( 2008.08.04 -- hyw )
	# ----------------------------------------------------------------
	def addDartData( self, key, value ):
		"""
		define method
		"""
		BigWorld.globalBases[ "DartManager" ].add( self.getName(), key, value )


	def updateDartPrestige( self, xValue, cValue ):
		"""
		define method
		�����ھ�����ֵ
		@param xValue	:��¡�ھ�����ֵ
		@param cValue	:��ƽ�ھ�����ֵ
		"""
		self.cell.updateDartPrestige( xValue, cValue )

	def onWuDaoOver( self, playerBaseMB, result ):
		"""
		֪ͨ������������������
		"""
		BigWorld.globalData[ "WuDaoMgr" ].onWuDaoOverFromSpace( playerBaseMB, self.databaseID, self.level, result )	# ֪ͨ�������������ĳ��ս�����

	def queryActivityScheme( self, index ):
		"""
		exposed method
		��ѯһ���������¼
		"""
		keys = CrondDatas.instance().getAllActivityData().keys()
		if len( keys ) > index:
			key = keys[index]
			for iScheme in CrondDatas.instance().getAllActivityData()[key]:
				if iScheme['showOnClient'] and iScheme['act']:
					# �ͻ���������ʾ ���� �û�Ǽ����	2009-07-13 SPF
					self.client.onAddScheme( iScheme['name'], iScheme['isStart'], iScheme['description'], iScheme['cmd'], iScheme['condition'], iScheme['area'], iScheme["activityType"], iScheme["line"], iScheme["star"], iScheme["persist"]  )
			self.client.onOneActivityDataSendOver()
		else:
			self.client.onActivityDataSendOver()

	"""
	GM ��Ϣ��ѯ
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
		������
		"""
		self.logoff()

	def queryIPAction( self, queryerMB, params ):
		"""
		define method
		��ѯIP
		"""
		queryerMB.client.onStatusMessage( csstatus.IP, str(( self.clientAddr[0], )) )

	def queryPlayerAmountAction( self, queryerMB, params ):
		"""
		define method
		��ѯ��������
		"""
		Love3.g_baseApp.queryAllPlayerAmount( queryerMB, params )

	def queryPlayerNameAction( self, queryerMB, params ):
		"""
		define method
		��ѯ��������
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
		BigWorld.executeRawDatabaseCommand( query, self.__onBlockCB )#��¼�����ݿ�
		"""

	def __onBlockCB( self, resultSet, rows, errstr ):
		"""
		"""
		pass

	def payGold( self, value, reason = None ):
		"""
		��Ҹ�Ԫ��
		"""
		if self.getUsableGold() - value < 0:
			return False
		self.addGold( -value, reason )
		return True

	def gainGold( self, value, reason = None  ):
		"""
		����ҽ�Ԫ��
		"""
		if self.gold + value > csconst.ROLE_GOLD_UPPER_LIMIT:
			return False
		self.addGold( value, reason )
		return True

	def addGold( self, value, reason = None ):
		"""
		������ҵ�Ԫ��ֵ
		@param value : Ԫ��ֵ
		@type value : INT64
		"""
		self.accountEntity.addGold( value, reason )

	def setGold( self, value, reason = None ):
		"""
		������ҵĽ�Ԫ��ֵ

		@param value : ���õ�ֵ
		@type value : UINT32
		"""
		self.accountEntity.addGold( value - self.gold,  reason )

	def updateGold( self, value, reason = csdefine.CHANGE_GOLD_NORMAL ):
		"""
		������ҵ�Ԫ��ֵ
		"""
		self.gold = value
		if hasattr( self, "client" ):
			self.client.updateGold( value, reason )

	def freezeGold( self, value ):
		"""
		����һ�������Ľ�Ԫ��

		@param value : ����ֵ
		"""
		self.frozenGold += value

	def thawGold( self, value ):
		"""
		�ⶳ��Ԫ��
		"""
		self.frozenGold -= value

	def paySilver( self, value, reason ):
		"""
		��Ҹ���Ԫ��
		"""
		if self.getUsableSilver() - value < 0:
			return False
		self.addSilver( -value, reason )
		return True

	def gainSilver( self, value, reason = None ):
		"""
		�������Ԫ��
		"""
		if self.silver + value > csconst.ROLE_SILVER_UPPER_LIMIT:
			return False
		self.addSilver( value, reason )
		return True

	def addSilver( self, value, reason = None ):
		"""
		�����Ԫ��ֵ�����仯
		@param value : Ԫ��ֵ
		@type value : INT64
		"""
		self.accountEntity.addSilver( value, reason )

	def setSilver( self, value, reason = None ):
		"""
		������ҵĽ�Ԫ��ֵ

		@param value : ���õ�ֵ
		@type value : UINT32
		"""
		self.accountEntity.addSilver( value - self.silver, reason )

	def updateSilver( self, value, reason = csdefine.CHANGE_SILVER_NORMAL ):
		"""
		������ҵ�Ԫ��ֵ
		"""
		self.silver = value
		if hasattr( self, "client" ):
			self.client.updateSilver( value, reason )

	def freezeSilver( self, value ):
		"""
		����һ����������Ԫ��

		@param value : ����ֵ
		"""
		self.frozenSilver += value

	def thawSilver( self, value ):
		"""
		�ⶳ��Ԫ��
		"""
		self.frozenSilver -= value

	def getUsableGold( self ):
		"""
		��ÿ��õĽ�Ԫ������ǰֵ��ȥ�������ֵ
		"""
		return self.gold - self.frozenGold

	def getUsableSilver( self ):
		"""
		��ÿ��õ���Ԫ������ǰֵ��ȥ�������ֵ
		"""
		return self.silver - self.frozenSilver


	def updateRoleRecord( self ):
		"""
		��ɫ���ߣ��ѽ�ɫ��һЩ��Ϸ��¼���»�ã����浽cell�ϡ�
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
		�������ݵ�apex�Ŀͻ���
		"""
		self.client.clientRecvApexMessage( strMsg,nLength)

	def clientSendApexMessage( self ,strMsg,nLength):
		"""
		��apex�Ŀͻ��˽�������
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
		��base��д��־ʱ��Ҫ��gradeд��
		@type  grade ��INT8
		@param grade : Ȩ�޵�ֵ
		"""
		self.grade = grade

	def queryWeekOnlineTime( self, targetID ):
		"""
		define method
		��ѯ��ɫ��������ʱ��
		"""
		text = ""
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec)
		weekOnlineTime = self.weekOnlineTime.get(wT, 0)	# ȡ����������ʱ��
		nowWeekOnlineTime = weekOnlineTime + BigWorld.time() - self._lasttime
		text += cschannel_msgs.BASE_GOSSIP_ROLE_0 %( nowWeekOnlineTime/3600, nowWeekOnlineTime%3600/60, nowWeekOnlineTime%60 )

		self.client.onSetGossipText( text )
		self.client.onGossipComplete( targetID )

	def setLastWeekOnlineTime( self, value ):
		"""
		���������������ʱ��
		"""
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1		#��ȡ��һ���ǵڼ���
		self.weekOnlineTime[wT] = value

	def setOnlineTime( self, value ):
		"""
		�����������ʱ��
		"""
		self.lifetime = value

	def getWeekOnlineTimeGift( self, lastWeek ):
		"""
		define method
		��ȡ��ɫ���ܹ��ʽ���
		@param lastWeek : �����ǵڼ���
		@type lastWeek : int32
		"""
		# ������cell����Ƿ��ܹ���ȡ���ʣ�baseֻ��������ʣ�Ȼ��֪ͨcell�����仯��������Ϊ�����������ر��ֶ���ͬһ��tick��
		# ��cell�������ͨ����Ȼ��base�ɹ��Ķ����ȡ���ʣ�����ڴ˴�������һ��ʱ����ֻ������ȡһ�ι��ʡ�
		now = time.time()
		if now - self.getWeekOnlineGiftTime < 0.2:
			ERROR_MSG( "���( %s )��0.2�����������뻻ȡ���ʽ�����������������Ϊ��" % self.getName() )
			return
		self.getWeekOnlineGiftTime = now

		lastWeekOnlineTime = self.weekOnlineTime.get( lastWeek, 0 )
		if lastWeekOnlineTime < 10 * 3600:
			self.statusMessage( csstatus.WEEK_ONLINE_TIME_LIMIT_TIME )
			return

		base_gift_mapping = { 6:75, 7:125, 8:200, 9:250, 10:375, 11:375, 12:375, 13:375, 14:375, 15:375 }	# ���ݵȼ�����������
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
		self.cell.setAccountRecord( "weekOnlineTimeGift", str( lastWeek + 1 ) )		# ���ñ�����ȡ�����ܵĹ���

	def getjackarooCardGift( self, level, presentID ):
		"""
		@define method
		��ȡ���ֿ�����
		@type  level     : Ҫ��ȡ�Ľ�Ʒ�ĵȼ� �� 5�����ֿ���Ʒ
		@param level     : UINT8
		@type  presentID : Ҫ��ȡ�Ľ�Ʒ��ID ע,��ֵ�Ǵ�cell�Ϸ���base���ɹ����ֻᷢ��cell�������ǲ���setTemp��ʽ�ŵ�cell�ˣ�
							���������Ľ����base����ÿһ�����󶼱��뽫�������cell�ˣ���ֱ�Ӵ�ֵֻ�ڳɹ��󷵻أ����Ժ���Ӧ�øĸ��á�
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
			# ��λ�����㣬�ȱ�Ǹ���Ʒ�Ѿ�����ȡ�����ʧ�����ٷ���base��ֵ��ԭ��ͨ������ʧ�ܡ�
			self.cell.getjkCardGiftResult( presentID )
		else:
			self.statusMessage( csstatus.JC_HAVE_DRAW_BEFORE )
			return

	def onGetjkCardGiftFailed( self ):
		"""
		@define method
		��ȡ�ɹ���֪ͨbase�����ȡ���
		"""
		self.accountEntity.jackarooCardState = self.oldJackarooCardState
		self.oldJackarooCardState = 0

	# ----------------------------------------------------------------
	# �µ������
	# ----------------------------------------------------------------
	def getVehicleID( self ):
		"""
		��ȡ���˳��ID
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
		ʹ�������Ʒ
		@return None
		"""
		uid = item.uid
		# ��ȡ���˳��ID
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
			
		#ͨ�����û�ȡ����������
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
		ʹ��ת���������Ʒ
		"""
		uid = item.uid
		# ��ȡ���˳��ID
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
	
	
	#��輤�����
	def canActivate( self, id ):
		"""
		�жϵ�ǰ�Ƿ��ܹ���������
		"""
		if id not in self.vehicleDatas: return False
		
		# �жϱ�����
		vehicleData = self.vehicleDatas[id]
		fullDegree = vehicleData["fullDegree"]
		if int( time.time() ) >= fullDegree:
			self.statusMessage( csstatus.VEHICLE_NO_ACTIVATE )
			return False
		
		# �жϹ���ʱ��
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
		ͨ��ָ����id�������
		@param id: �����������ݵ�Ψһ��ʾ��
		@type  id:	UINT8
		@return None
		"""
		# �Ƿ��ܼ���
		if not self.canActivate( id ): return
		
		vehicleData = self.vehicleDatas[id]
		# ֪ͨcell�ٻ�
		self.cell.activateVehicle( vehicleData )
	
	
	#����ٻ����
	def canMount( self, id ):
		"""
		�жϵ�ǰ�Ƿ��ܹ�������
		"""
		if id not in self.vehicleDatas: return False
		
		# �жϱ�����
		vehicleData = self.vehicleDatas[id]
		fullDegree = vehicleData["fullDegree"]
		if int( time.time() ) >= fullDegree:
			self.statusMessage( csstatus.VEHICLE_NO_JOYANCY )
			return False
		
		# �жϹ���ʱ��
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
		ͨ��ָ����id�ٻ����
		@param id: �����������ݵ�Ψһ��ʾ��
		@type  id:	UINT8
		@return None
		"""
		# �Ƿ����ٻ�
		if not self.canMount( id ): return

		vehicleData = self.vehicleDatas[id]
		# ֪ͨcell�ٻ�
		self.cell.actAndConjureVehicle( vehicleData )


	#���buff���
	def addVehicleBuff( self, id, buff ):
		"""
		Define method
		������buff
		"""
		if id not in self.vehicleDatas:
			return
		self.vehicleDatas[id]["attrBuffs"].append( buff )

	def updateVehicleBuffs( self, id, buffs ):
		"""
		Define method
		�������buff
		"""
		if id not in self.vehicleDatas:
			return
		self.vehicleDatas[id]["attrBuffs"] = buffs

	#��豥�������
	def addVehicleFullDegree( self, id, fullDegree ):
		"""
		Define Method
		���ӱ�����
		@param fullDegree	: ������
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
		������豥����
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		
		currFullDegree = vehicleData["fullDegree"]
		if currFullDegree == fullDegree: return
		#���������ֵ��ȡ���ֵ
		maxFullDegree = int( time.time() ) + csconst.MAX_FULL_DEGREE
		if fullDegree > maxFullDegree:
			fullDegree = maxFullDegree
		vehicleData["fullDegree"] = fullDegree

		self.cell.onUpdateVehicleFullDegree( id, fullDegree )
		self.client.onUpdateVehicleFullDegree( id, fullDegree )
	
	#����
	def transVehicle( self, id ):
		"""
		exposed method
		�ͻ������봫��
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		
		level = vehicleData["level"]
		# ��ȡ��ǰ�ȼ����辭��ֵ
		expMax = Love3.g_vehicleExp.getExp( level )
		self.cell.transVehicle( id, expMax - vehicleData["exp"]  )

	def transAddVehicleExp( self, id, exp ):
		"""
		Define Method
		����������辭��ֵ
		@param exp	: ����
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
		# ��ȡ��ǰ�ȼ����辭��ֵ
		expMax = Love3.g_vehicleExp.getExp( level )

		while totalExp >= expMax:
			totalExp -= expMax
			level += 1
			expMax = Love3.g_vehicleExp.getExp( level )
			if expMax <= 0: break

		vehicleData["exp"] = totalExp
		level = min( 150, level )
		# ֪ͨ�ͻ��˾���ֵ�ı�
		self.client.onUpdateVehicleExp( id, totalExp )

		currLevel = vehicleData["level"]
		if currLevel == level: return
		if level > currLevel:	# ���������ʾ
			self.statusMessage( csstatus.VEHICLE_LEVEL_UP_POTENTIAL_TRANS, exp, itemName, level )
		vehicleData["level"] = level

		# ���ü��ܵ�
		skPoint = ( level - currLevel ) / 2
		self.addVehicleSkPoint( id, skPoint )

		strength,intellect,dexterity,corporeity = Love3.g_vehicleData.getSIDC( level, vehicleData["growth"] )
		vehicleData["strength"] = strength
		vehicleData["intellect"] = intellect
		vehicleData["dexterity"] = dexterity
		vehicleData["corporeity"] = corporeity	

		# ֪ͨcell
		self.cell.onVehiclePropertyNotify( id, level, strength, intellect, dexterity, corporeity, csdefine.VEHICLE_UPDATE_REASON_LEVEL_UP )
		# ֪ͨ�ͻ��˵ȼ��ı�
		self.client.onUpdateVehicleProperty( id, level, strength, intellect, dexterity, corporeity, vehicleData["step"], vehicleData["growth"], vehicleData["srcItemID"] )

	def addVehicleExp( self, id, exp ):
		"""
		Define Method
		������辭��ֵ
		@param exp	: ����
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
		������辭��ֵ
		@param exp	: ����
		@type exp	: INT32
		@return		: None
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		level = vehicleData["level"]
		# ��ȡ��ǰ�ȼ����辭��ֵ
		expMax = Love3.g_vehicleExp.getExp( level )

		while exp >= expMax :
			exp -= expMax
			level += 1
			expMax = Love3.g_vehicleExp.getExp( level )
			if expMax <= 0 :break

		vehicleData["exp"] = exp
		level = min(150,level)
		self.setVehicleLevel( id, level )
		# ֪ͨ�ͻ��˾���ֵ�ı�
		self.client.onUpdateVehicleExp( id, exp )

	def setVehicleLevel( self, id, level ):
		"""
		Define Method
		�������ĵȼ�
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		currLevel = vehicleData["level"]
		if currLevel == level: return
		if level > currLevel:	# ���������ʾ
			vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
			itemName = vehicleItem.name().split("(")[-1].split(")")[0]
			self.statusMessage( csstatus.VEHICLE_LEVEL_UP, itemName, level )
		vehicleData["level"] = level

		# ���ü��ܵ�
		skPoint = ( level - currLevel ) /2
		self.addVehicleSkPoint( id, skPoint )
		
		strength,intellect,dexterity,corporeity = Love3.g_vehicleData.getSIDC( level, vehicleData["growth"] )
		vehicleData["strength"] = strength
		vehicleData["intellect"] = intellect
		vehicleData["dexterity"] = dexterity
		vehicleData["corporeity"] = corporeity	
		
		# ֪ͨcell
		self.cell.onVehiclePropertyNotify( id, level,strength,intellect,dexterity,corporeity,csdefine.VEHICLE_UPDATE_REASON_LEVEL_UP )
		# ֪ͨ�ͻ��˵ȼ��ı�
		self.client.onUpdateVehicleProperty( id, level,strength,intellect,dexterity,corporeity,vehicleData["step"], vehicleData["growth"], vehicleData["srcItemID"] )

	def setVehicleGrowth( self, id, growth ):
		"""
		Define Method.
		�������ĳɳ��ȣ�����ֻ��GM�����õ���
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		currGrowth = vehicleData["growth"]
		if currGrowth == growth: return
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return  #���������Ч
		vehicleData["growth"] = growth
		level = vehicleData["level"]

		strength, intellect, dexterity, corporeity = Love3.g_vehicleData.getSIDC( level, growth )
		vehicleData["strength"] = strength
		vehicleData["intellect"] = intellect
		vehicleData["dexterity"] = dexterity
		vehicleData["corporeity"] = corporeity

		# ֪ͨcell
		self.cell.onVehiclePropertyNotify( id, level, strength, intellect, dexterity, corporeity, csdefine.VEHICLE_UPDATE_REASON_LEVEL_UP )
		# ֪ͨ�ͻ��˳ɳ��ȸı�
		self.client.onUpdateVehicleProperty( id, level, strength, intellect, dexterity, corporeity, vehicleData["step"], growth, vehicleData["srcItemID"] )

	#�������
	def upStepVehicle( self, mainID, oblationID, needItem ):
		"""
		define method
		�������
		"""
		#�ж������Ƿ���������
		vehicleData = self.vehicleDatas.get( mainID )
		if vehicleData is None: return
		nextStepItemID = vehicleData["nextStepItemID"]
		if not nextStepItemID:return #����һ�׶�Ӧ��Ʒ����������
		if vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return #������Ƿ�����費������
		if not nextStepItemID : return #����豾��Ͳ�������
		if vehicleData["level"] < U_DATA[ vehicleData["step"] ]["needLevel"]: #�ж������ȼ�
			self.statusMessage( csstatus.VEHICLE_UPSTEP_MAIN_NO_LEVEL )
			return
		
		#�жϼ����Ƿ���������
		o_vehicleData = self.vehicleDatas.get( oblationID )
		if o_vehicleData is None: return
		if o_vehicleData["type"] == csdefine.VEHICLE_TYPE_FLY : return
		if o_vehicleData["step"] != vehicleData["step"]: #����ͼ���״��ǲ���һ��
			self.statusMessage( csstatus.VEHICLE_UPSTEP_STEP_NOT_SAME )
			return
		
		#��ʼ����
		pro = U_DATA[ vehicleData["step"] ]["successPro"]
		#������ʧ
		self.vehicleDatas.pop( oblationID )
		self.client.onFreeVehicle( oblationID )
		obItem = g_items.createDynamicItem( o_vehicleData["srcItemID"] )
		obName = obItem.name().split("(")[-1].split(")")[0]
		self.statusMessage( csstatus.VEHICLE_UPSTEP_DELETE_OB, obName )
		
		#֪ͨcellɾ����������Ʒ
		self.cell.onUpStepVehicle(  )
		
		#���ԭ�����
		vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		itemName = vehicleItem.name().split("(")[-1].split(")")[0]
			
		if random.random() <= pro: #���׳ɹ�
			#�������ס��ɳ�ֵ��������
			nextStep = U_DATA[ vehicleData["step"] ]["nextStep"]
			growth = vehicleData["growth"]
			needItem_low = U_DATA[ vehicleData["step"] ]["needItem_low"]
			needItem_high = U_DATA[ vehicleData["step"] ]["needItem_high"]
			
			#�������Ա仯
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
			# ֪ͨ�ͻ��˵ȼ��ı�
			self.client.onUpdateVehicleProperty( mainID, level, strength, intellect, dexterity, corporeity, nextStep, growth, nextStepItemID )
			
			#������׺������
			dstVehicleItem = g_items.createDynamicItem( nextStepItemID )
			dstItemName = dstVehicleItem.name().split("(")[-1].split(")")[0]
			
			self.statusMessage( csstatus.VEHICLE_UPSTEP_SUCCESS, itemName, dstItemName )
			self.statusMessage( csstatus.VEHICLE_UPSTEP_SUCCESS_TISHI, itemName, dstItemName )
		else:
			self.statusMessage( csstatus.VEHICLE_UPSTEP_FAILED, itemName )
	
	#�������Ʒ����
	def vehicleToItem( self, id, needItem ):
		"""
		Exposed method
		�������Ʒ
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		self.cell.vehicleToItem( vehicleData, needItem )
		
	def vehicleToItemSuc( self, id ):
		"""
		define method
		�������Ʒ�ɹ�
		"""
		self.freeVehicle( id )


	def freeVehicle( self, id ):
		"""
		Define method
		������
		"""
		if id not in self.vehicleDatas: return
		vehicleData = self.vehicleDatas.pop( id )

		vehicleItem = g_items.createDynamicItem( vehicleData["srcItemID"] )
		itemName = vehicleItem.name().split("(")[-1].split(")")[0]
		self.statusMessage( csstatus.VEHICLE_UPSTEP_DELETE_OB, itemName )
		# ֪ͨ�ͻ���
		self.client.onFreeVehicle( id )
	
	
	#��輼�ܵ����
	def addVehicleSkPoint( self, id, skpoint ):
		"""
		���Ӽ��ܵ�
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return
		
		currSkPoint = vehicleData["skPoint"]
		self.setVehicleSkPoint( id, currSkPoint + skpoint )

	def setVehicleSkPoint( self, id, skpoint ):
		"""
		Define Method
		���ü��ܵ�
		"""
		vehicleData = self.vehicleDatas.get( id )
		if vehicleData is None: return

		if skpoint < 0: skpoint = 0
		currSkPoint = vehicleData["skPoint"]
		if currSkPoint == skpoint: return
		vehicleData["skPoint"] = skpoint
		# ֪ͨcell
		self.cell.onVehicleSkPointNotify( id, skpoint )
		# ֪ͨ�ͻ��˼��ܵ�ı�
		self.client.onUpdateVehicleSkPoint( id, skpoint )


	#�����ʱ�����	
	def addVehicleDeadTime( self, id, deadTime ):
		"""
		Define Method
		���Ӵ��ʱ��
		@param id		: id
		@type id		: UINT8
		@param deadTime	: ���ʱ��
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
		���������ʱ��
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
		# ֪ͨ�ͻ���
		self.client.onUpdateVehicleDead( id, addDeadTime )

	def requestVehicleData( self ):
		"""
		�ͻ��������������
		"""
		for vehicleData in self.vehicleDatas.itervalues():
			self.client.onAddVehicle( vehicleData )
		self.client.onInitialized( csdefine.ROLE_INIT_VEHICLES )

	def feedVehicle( self, id ):
		"""
		Exposed method
		���ιʳ
		"""
		if id not in self.vehicleDatas: return
		
		vehicleData = self.vehicleDatas[id]
		srcItemID = vehicleData["srcItemID"]
		
		self.cell.feedVehicle( id, srcItemID )


	def addVehicleSkill( self, id, skillID ):
		"""
		Define Method
		���ѧϰ����
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
		��������
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
		��ü��۵ĳ���
		"""
		self.pcg_addPet_( epitome, csdefine.ADDPET_RECEIVETSPET )
		self.cell.addMoney( -price, csdefine.CHANGE_MONEY_RECEIVETSPET )


	def sellPointCard( self, cardNo, pwd, serverName, cardPrice ):
		"""
		define method
		��Ҽ��۵㿨
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
		�ͻ�������ȡ����֤
		"""
		Love3.g_antiRobotVerify.cancelVerify( self.id )
		self.antiRobotCount -= 1
		if self.antiRobotCount < 0:
			self.antiRobotCount = 0
		
	def triggerAntiRobot( self ):
		"""
		Define method.
		�����������֤
		"""
		if time.time() - self.antiRobotTime < Const.ANTI_ROBOT_INTERVAL:
			return
		self.antiRobotCount += 1	# ��֤��һ��
		self.antiRobotTime = time.time()
		Love3.g_antiRobotVerify.triggerVerify( self, self.antiRobotCallback )

	def antiRobotCallback( self, result ):
		"""
		�������֤�ʴ����ص�

		@param result : True or False��True��ʾ��֤�ɹ���False��ʾ��֤ʧ��
		"""
		#DEBUG_MSG( "--->>>player( %s ),result( %s ),self.antiRobotCount( %i )" % ( self.getName(), str( result ), self.antiRobotCount ) )
		if self.isDestroyed:
			return
		if result:
			# ������
			self.cell.onRobotVerifyResult( csstatus.ANTI_ROBOT_FIGHT_VERIFY_RIGHT )
			self.antiRobotCount = 0
		else:
			# ����self.antiRobotCount�Ĵ�������������֤
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
		�ͻ��˻ش���֤����

		@param answer: �����ͼƬ�������( x, y )
		"""
		Love3.g_antiRobotVerify.verify( self.id, answer )

	# -------------------------------�������� by jy-------------------------------
	def onTimer_roleTongSignSender( self, id, arg ):
		"""
		�Ѱ���귢�͵���������嵽�������Լ�����
		����ҽ�ɫ�������ߣ��������������ʱ����ʱ�����Լ����ϵİ������������
		"""
		self.sendTongSignString()
		self.delTimer( self._tongSignSenderTimer )
		self._tongSignSenderTimer = 0
		self._tongSignSenderTimer = self.addTimer( Const.SEND_TONG_SIGN_TIME_TICK, 0.0, ECBExtend.ROLE_TONG_SIGN_SENDER )

	def tongSignSendStart( self, tongDBID, iconMD5, iconStringList ):
		"""
		define method
		��ʼ�ְ��������ַ���
		"""
		TongInterface.tongSignSendStart( self, tongDBID, iconMD5, iconStringList )
		self._tongSignSenderTimer = self.addTimer( 0.1, 0.0, ECBExtend.ROLE_TONG_SIGN_PACKS_SENDER )

	def onTimer_roleTongSignPacksSender( self, id, arg ):
		"""
		���ְ�����
		"""
		TongInterface.sendIconPackToClient( self )
		self.delTimer( self._tongSignSenderTimer )
		self._tongSignSenderTimer = 0
		self._tongSignSenderTimer = self.addTimer( 0.1, 0.0, ECBExtend.ROLE_TONG_SIGN_PACKS_SENDER )

	#------------------ItemAwards ��ȡ��Ʒ����
	def onAwardItem( self, itemList, state = 0 ):
		"""
		��ȡ��Ʒ����
		"""
		if self.isDestroyed:
			return
		if state == 1:
			self.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )		# ��ʾû���ҵ����������Ľ���
			return
		if state == 2:
			self.statusMessage( csstatus.PCU_YOU_ARE_BUSY )			# ��ʾ֮ǰ�������ڴ�����
			return
		self.cell.awardItem( itemList)

	def awardResult( self, ifAward ):
		"""
		�Ƿ���ȡ�ɹ�
		@define method
		"""
		if ifAward:
			self.itemAwards.awardsSuccess( self.playerName, self.databaseID )
		else:
			self.itemAwards.awardsFailed()

	def awardItem( self, Type, parameter ):
		"""
		����BASE��ȡ��ҽ���������
		@type  Type : UINT8
		@param Type : ��ȡ������
		@type  parameter : STRING
		@param parameter : �Զ������չ����
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

	# -------------------------------�Զ�ս����ʱ��� by jy-------------------------------
	@languageDepart_AFTimer
	def chargeAFTimer( self ):
		"""
		�Զ�ս����ֵ/��ʱ
		"""
		self.AFExtraTimer = 0
		if self.af_time_extra > 0:
			self.af_time_extra -= (int( time.time() ) - self.role_last_offline)
			self.client.onAFLimitTimeExtraChanged( self.af_time_extra )
			self.AFExtraTimer = self.addTimer( 1, 1.0, ECBExtend.ROLE_AF_TIME_EXTRA )

	def onTimer_roleAFTimeCharge( self, id, arg ):
		"""
		�Զ�ս����ֵʱ��
		"""
		self.af_time_limit = Const.AUTO_FIGHT_PERSISTENT_TIME_TW
		self.client.onAFLimitTimeChanged( self.af_time_limit )
		self.AFTimer = self.addTimer( 86400, 0.0, ECBExtend.ROLE_AF_TIME_CHARGE )	# ����������ʱ����Ϊ����

	def onTimer_roleAFTimeExtra( self, id, arg ):
		"""
		�Զ�ս�����ѳ�ֵʱ���ʱ��
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
		�������Զ�ս��
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
		���뿪�Զ�ս����
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
		�����Զ�ս������ʱ��
		"""
		self.af_time_limit += timeAdd
		if self.af_time_limit < 0:
			self.af_time_limit = 0
		self.client.onAFLimitTimeChanged( self.af_time_limit )

	def autoFightExtraTimeCharge( self, timeAdd ):
		"""
		define method
		��ֵ������Զ�ս��ʱ��
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
		���ڴ���һЩ������Ϊ�Ľ����ص�
		"""
		BigWorld.globalData["MessyMgr"].onMessyOver( messyID, self.databaseID )


	def sendLoveMsg( self, receiverName, msg, isAnonymity, isSendMail ):
		"""
		Exposed method
		�ǳ����ţ����͸����Ϣ
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

	# ----------------------------һ����װ by ����---------------------------------
	def addSuit( self, suitIndex, suitName, suitEquips ):
		"""
		Exposed method
		�������װ
		"""
		BigWorld.globalData["OneKeySuitMgr"].addSuit( self.databaseID, suitIndex, suitName, suitEquips, self )

	def updateSuit( self, suitIndex, suitEquips ):
		"""
		Exposed method
		����������װ
		"""
		BigWorld.globalData["OneKeySuitMgr"].updateSuit( self.databaseID, suitIndex, suitEquips, self )

	def initSuit( self ):
		"""
		��ɫ����ʱ��ʼ����ɫ��װ
		"""
		self.switchEquipTick = 0.0	# ��װ��ʱ���¼����Ϊ���ƻ�װ��Ϊ����Ƶ�����ֶ�
		BigWorld.globalData["OneKeySuitMgr"].getSuitDatas( self.databaseID, self )

	def renameSuit( self, suitIndex, suitName ):
		"""
		Exposed method
		��������װ
		"""
		BigWorld.globalData["OneKeySuitMgr"].updateSuitName( self.databaseID, suitIndex, suitName, self )

	def onSwitchSuit( self, suitIndex ):
		"""
		Exposed method
		����װ��֪ͨ
		"""
		#t = time.time()
		#if t - self.switchEquipTick < Const.OKS_TIME_INTERVAL:
		#	print "hey too hurry."
		#	return
		self.oksIndex = suitIndex
		self.switchEquipTick = time.time()
		self.client.onSwitchSuit( suitIndex )
	# ----------------------------һ����װ---------------------------------

	def queryMatchLog( self ):
		"""
		Exposed method.
		��Ҳ�ѯ������־��Ϣ
		"""
		RoleMatchRecorder.query( self )

	def updateMatchLog( self, matchType, scoreOrRound ):
		"""
		Define method.
		���±�����־

		@pram matchType:UINT8���������ͣ�������csdefine�е�MATCH_TYPE_***
		@param scoreOrRound: INT32�����־���ݣ����β�����û��� �� ���β����������
		"""
		RoleMatchRecorder.update( self.databaseID, matchType, scoreOrRound, self )
	
	#���贫�����	
	def getAllVehicleDatasFromBase( self ):
		"""
		Define method.
		���������еķ��������modelNumber
		"""
		self.cell.onGetAllVehicleDatas( self.vehicleDatas )
	
	def baoZangBroadCastEnemyPos( self, enemyId, pos ):
		"""
		Exposed method.
		���ظ����㲥����λ�ø�����
		"""
		for mailbox in self._teamMembers.itervalues():
			if mailbox:
				mailbox.client.baoZangOnReceiveEnemyPos( enemyId, pos )
	
	def baoZangBroadCastDisposeEnemy( self, enemyId ):
		"""
		Exposed method.
		���ظ����㲥���ѵ��˲����ҵ�AOI
		"""
		for mailbox in self._teamMembers.itervalues():
			if mailbox:
				mailbox.client.baoZangOnDisPoseEnemy( enemyId )
				
#-------------------------------------------------------------------
#����ʱ��
#-------------------------------------------------------------------
	def noticeDanceMgrIsChallenged(self, challengeIndex):
		#Exposed method
		BigWorld.globalData["DanceMgr"].indexIsChallenged(self, challengeIndex, True) #����True��ʾ���challengeIndexλ����������ս
		
	def canChallengeDanceKing(self, challengeIndex):
		#exposed method
		BigWorld.globalData["DanceMgr"].canChallengeDanceKing(self, challengeIndex, self.playerName)

	def enterWuTing(self):
		#defined method
		BigWorld.globalData["DanceMgr"].addPlayerMailbox(self.databaseID, self)

	
	def leaveWuTing(self):
		BigWorld.globalData["DanceMgr"].removePlayerMailbox(self.databaseID)
		
	#Զ�̻�ȡ���װ����Ϣ
	def queryRoleEquipItems( self, queryName ):
		"""
		exposed method.
		ͨ�����֣�Զ�̲�ѯ���װ��
		"""
		Love3.g_baseApp.queryRoleEquipItems( self, queryName )
		
		
	def setJueDiFanJiState( self, state ):
		"""
		���þ��ط����״̬���Ա���������ٵ�ʱ��֪ͨ����������Ӧ������
		"""
		self.jueDiFanJiState = state
		
# end of class: Role
