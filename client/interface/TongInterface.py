# -*- coding: gb18030 -*-
#
# $Id: TongInterface.py,v 1.24 2008-08-25 09:33:03 kebiao Exp $

import time
import os
import zlib
import _md5
import base64
import struct
import BigWorld
from bwdebug import *
from ResMgr import openSection
import event.EventCenter as ECenter
import csdefine
import csstatus
import csconst
import Const
import Define
from config.client.msgboxtexts import Datas as mbmsgs
import math
import GUIFacade
import random
from Function import Functor
import Function
from gbref import rds
from ItemsFactory import ObjectItem
import csstatus_msgs as StatusMsgs
import guis.general.bigmap.Map
from NPCQuestSignMgr import npcQSignMgr
from MessageBox import *
from Time import Time
import utils

tongSignMap = {}						# 动态的帮会会标列表，用于管理眼中的角色帮会会标 by 姜毅

class MemberInfos:
	"""
	家族中成员的一些信息结构
	"""
	def __init__( self ):
		"""
		初始化成员信息
		"""
		self._memberDBID = 0
		self._isOnline = False					# 该成员是否在线
		self._name = ""							# 该成员的名称
		self._grade = 0							# 该成员的帮会权限
		self._class = 0							# 该成员的职业
		self._level = 0							# 该成员的级别
		self._spaceType = ""					# 该成员所在space位置
		self._lastPosition = ( 0, 0, 0 )		# 该成员最后一次查询所在位置
		self._scholium = ''						# 该成员的批注
		self._contribute = 0					# 该成员帮会贡献度
		self._totalContribute = 0				# 该成员帮会累积贡献度
		self.tong_storage_npcID = 0				# 记录帮会仓库npcID by姜毅

		self._lastWeekTotalContribute = 0		# 该成员上周帮会累计帮贡值
		self._lastWeekSalaryReceived = 0		# 该成员上周领取俸禄值
		self._weekTongContribute = 0 			# 该成员本周获取帮贡值
		self._weekSalaryReceived = 0			# 该成员本周领取俸禄值
		self._lastWeekTotalContribute = 0		# 该成员上周获取帮贡

	def init( self, memberDBID, name, grade, eclass, level, scholium ):
		"""
		正式的初始填充各项属性
		"""
		self._memberDBID = memberDBID
		self._name = name
		self._grade = grade
		self._class = eclass
		self._level = level
		self._scholium = scholium

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

	def getSpaceType( self ):
		return self._spaceType

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

	def setOnlineState( self, online ):
		"""
		设置在线状态
		@param online: bool, 在线或者不在线
		"""
		self._isOnline = online

	def setGrade( self, grade ):
		self._grade = grade

	def setLevel( self, level ):
		self._level = level

	def setPosition( self, pos ):
		self._lastPosition = pos

	def setSpaceType( self, spaceType ):
		self._spaceType = spaceType

	def setScholium( self, scholium ):
		self._scholium = scholium

	def setContribute( self, contribute ):
		self._contribute = contribute

	def setName( self, name ):
		self._name = name

	def getWeekTongContribute( self ):
		return self._weekTongContribute


	def setLastWeekTotalContribute( self, lastWeekTotalContribute ):
		self._lastWeekTotalContribute = lastWeekTotalContribute


	def getLastWeekTotalContribute( self ):
		return self._lastWeekTotalContribute

	def getCurrentContribute( self ):
		return self._currentContribute

	def setTongContributeRelated( self, totalContribute, currentContribute, thisWeekTotalContribute, lastWeekTotalContribute ):
		"""
		累计帮贡总值、剩余帮贡值、本周获得帮贡、上周获得帮贡
		"""
		self._totalContribute = totalContribute
		self._currentContribute = totalContribute
		self._weekTongContribute = thisWeekTotalContribute
		self._lastWeekTotalContribute = lastWeekTotalContribute

	def setLastWeekSalaryReceived( self, lastWeekSalaryReceived ):
		self._lastWeekSalaryReceived = lastWeekSalaryReceived

	def getLastWeekSalaryReceived( self ):
		return self._lastWeekSalaryReceived

	def setWeekTongContribute( self, weekTongContribute ):
		self._weekTongContribute = weekTongContribute

	def getWeekTongContribute( self ):
		return self._weekTongContribute

	def setWeekSalaryReceived( self, weekSalaryReceived ):
		self._weekSalaryReceived = weekSalaryReceived

	def getWeekSalaryReceived( self ):
		return self_weekSalaryReceived


class TongInterface:
	def __init__( self ):
		self.tong_memberInfos = {}
		self.tong_leagues = {} #帮会同盟
		self.tong_isRequestDataEnd = False
		self.robWarTargetTong = 0
		self.tong_dutyNames = {}
		self.tong_ck_requestItemCount = 0	# 帮会仓库物品数据请求计数
		self.tong_ck_requestLogCount = 0	# 帮会仓库log信息请求计数
		self.tong_storageLog = []			# 帮会仓库的log数据
		self.storageBagPopedom = []		# 帮会仓库额外数据array of TONG_STORAGE_POPEDOM
		self.fetchRecord = None
		self.tongMoney = 0
		self.tongLevel = 0
		self.tongQueryTongListIndex = 0
		self.TongListInfos = {}
		self.tong_buildDatas = {} 			# 帮会建筑信息
		self.applyMsgBox = None
		self.__isInCityWar = False				# 是否在城战领地中
		self.cityWarPointLogs = {}				# 城战攻方数据
		self.tongInfos = {}						# 攻守双方信息
		self.rightTongDBID = self.tong_dbID					# 防守帮会dbID，默认为自己帮会
		self.tong_sign_md5 = None					# 该成员帮会会标MD5 by姜毅
		self.tong_sign_searching_list = {}			# 记录正在请求数据的帮会ID，防止重复请求 by姜毅
		self.tong_sign_searcher_list = {}			# 记录正在请求的对象entity（主要是玩家），用于正确显示会标 by 姜毅
		self.submitting = False						# 是否正在上传中 by 姜毅
		self.tong_prestige = 0					#帮会声望
		self.variable_prestige = 0				#额外声望
		self.tong_territoriesNPCs = {}		# 帮会领地的NPC（包括其它帮会领地的NPC）
		self.tongExp = 0					# 帮会经验
		self.tong_totalSignInRecord = 0		# 该成员签到总数
		self.tong_battleLeagues = {}		# 帮会战争同盟
		self.tong_quarterFinalRecord = {}	# 帮会夺城战半决赛结果
		self.tongQueryBattleLeagueIndex = 0 

		# 申请加入帮会的记录，为防止骚扰，对同一帮会的入帮申请需要间隔20分钟。
		# like as: { tongDBID:time, ... }
		self.tongRequestInfo = {}


	def tong_reset( self ):
		self.tong_memberInfos = {}
		self.tong_leagues = {} #帮会同盟
		self.tong_isRequestDataEnd = True
		self.tong_ck_requestItemCount = 0	# 帮会仓库物品数据请求计数
		self.tong_ck_requestLogCount = 0	# 帮会仓库log信息请求计数
		self.tong_storageLog = []			# 帮会仓库的log数据
		self.storageBagPopedom = []		# 帮会仓库额外数据array of TONG_STORAGE_POPEDOM
		self.fetchRecord = None
		self.tongMoney = 0
		self.tongLevel = 0
		self.TongListInfos = {}
		self.tong_prestige = 0
		self.variable_prestige = 0
		self.tongExp = 0
		self.tong_battleLeagues = {}
		self.tong_quarterFinalRecord = {}
		GUIFacade.tong_reset()

	def tong_onCreateSuccessfully( self, tongDBID, tongName ):
		"""
		define method.
		帮会创建成功通知
		"""
		self.statusMessage( csstatus.TONG_CREATE_SUCCESS, tongName )
		self.tong_requestDatas()
		rds.helper.courseHelper.tongFamilyTrigger( "jianlibanghui" )		# 第一次建立帮会族时，触发过程帮助提示（hyw--2009.06.13）

	def tong_onReceiveData( self ):
		"""
		define method.
		收到服务器通知 有新的数据可以获取了
		"""
		if self.tong_isRequestDataEnd:
			self.tong_isRequestDataEnd = False
			self.tong_requestDatas()

	def tong_requestDatas( self ):
		"""
		去服务器上拿帮会数据
		"""
		requestDatas( self.id )

	def onEndInitialized( self ) :
		"""
		角色初始化进度条结束
		"""
		if not self.isJoinTong():
			self.tong_isRequestDataEnd = True
			return
		self.tong_requestDatas()

	def tong_onRequestDatasCallBack( self ):
		"""
		define method.
		收到服务器数据发送完毕的通知
		"""
		self.tong_isRequestDataEnd = True

	#--------------------------------------------------------------------------------------------------------

	def tong_setLeague( self, tongDBID, tongName ):
		"""
		define method.
		设置同盟帮会
		"""
		self.tong_leagues[tongDBID] = tongName
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_LEAGUE" )
#		self.chat_say( "帮会同盟:%s" % tongName )

	def tong_addLeague( self, tongDBID, tongName ):
		"""
		define method.
		新加入同盟帮会
		"""
		self.tong_leagues[tongDBID] = tongName
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_ADD_LEAGUE", tongDBID )
		self.statusMessage( csstatus.TONG_LEAGUE_SUCCESS, tongName )

	def tong_delLeague( self, tongDBID ):
		"""
		define method.
		解除了某同盟帮会
		"""
		if self.tong_leagues.has_key( tongDBID ):
			del self.tong_leagues[tongDBID]
			ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_DEL_LEAGUE", tongDBID )
#		self.chat_say( "解除帮会同盟:%s" % tongName )

	#--------------------------------------------------------------------------------------------------------

	def tong_onSetMemberInfo( self, memberDBID, memberName, memberLevel, \
							memberClass, memberTongGrade, memberTongScholium, memberTongContribute, memberTongTotalContribute, online ):
		"""
		define method.
		服务器设置客户端帮会成员信息
		"""
		# 设置facade变量 使用当前变量的地址， 可以减少后续很多的操作提高效率
		if not GUIFacade.tong_hasSetMemberInfo():
			GUIFacade.tong_setMemberInfo( self.tong_memberInfos )

		info = MemberInfos()
		info.init( memberDBID, memberName, memberTongGrade, memberClass, memberLevel, memberTongScholium )
		info.setOnlineState( online )
		info.setContribute( memberTongContribute )
		info.updateTotalContribute( memberTongTotalContribute )
		self.tong_memberInfos[ memberDBID ] = info
		GUIFacade.tong_onSetMemberInfo( 0, 0, memberDBID )	# 取消家族，帮会界面还没修改，暂时0表示familyDBID和familyGrade，15:36 2010-11-11，wsf

	def tong_onDeleteMemberInfo( self, memberDBID ):
		"""
		define method.
		服务器删除客户端帮会成员信息
		"""
		info = self.tong_memberInfos[ memberDBID ]
		name = info.getName()
		self.tong_memberInfos.pop( memberDBID )
		self.statusMessage( csstatus.TONG_MEMBER_QUIT, name )
		GUIFacade.tong_onRemoveMember( memberDBID )

	#--------------------------------------------------------------------------------------------------------
	def tong_kickMember( self, memberDBID ):
		"""
		踢某成员出帮会
		"""
		self.cell.tong_kickMember( memberDBID )

	#--------------------------------------------------------------------------------------------------------
	def tong_quit( self ):
		"""
		退出这个tong
		"""
		if self.tong_grade == csdefine.TONG_DUTY_CHIEF:
			self.statusMessage( csstatus.TONG_CHIEF_QUIT )
			return
		self.cell.tong_quit()

	def tong_meQuit( self ):
		"""
		define method.
		自己离开了帮会， 可能是主动退出或者家族退出被动造成的。
		"""
		self.tong_reset()
		self.statusMessage( csstatus.TONG_MEMBER_QUIT_ME )

	def tong_onDismissTong( self ):
		"""
		帮会解散
		"""
		self.tong_reset()
		self.statusMessage( csstatus.TONG_DISMISS )

	#--------------------------------------------------------------------------------------------------------

	def tong_abdication( self, memberDBID ):
		"""
		帮主让位
		"""
		if self.tong_grade != csdefine.TONG_DUTY_CHIEF:
			self.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		if not self.tong_memberInfos.has_key( memberDBID ):
			self.statusMessage( csstatus.TONG_CANT_ABDICATION_NOT_MEMBER )
			return
		BigWorld.player().cell.tong_abdication( memberDBID )

	def tong_onAbdication( self, oldChief, newChief ):
		"""
		define method.
		更换新帮主了
		"""
		oldChiefInfo = self.tong_memberInfos[ oldChief ]
		newChiefInfo = self.tong_memberInfos[ newChief ]
		oldChiefInfo.setGrade( csdefine.TONG_DUTY_MEMBER )
		newChiefInfo.setGrade( csdefine.TONG_DUTY_CHIEF )

		self.statusMessage( csstatus.TONG_ABDICATION, newChiefInfo.getName() )
		GUIFacade.tong_onMemberGradeChanged( oldChief, csdefine.TONG_DUTY_MEMBER )
		GUIFacade.tong_onMemberGradeChanged( newChief, csdefine.TONG_DUTY_CHIEF )

	#--------------------------------------------------------------------------------------------------------

	def onGetBuildingSpendMoney( self, spendingMoney ):
		GUIFacade.onGetBuildingSpendMoney( spendingMoney )

	def tong_onSetTongMoney( self, money ):
		"""
		define method.
		"""
		if money != self.tongMoney:
			if self.tongMoney > 0:
				val = self.tongMoney - money
				if val > 0:							# 被扣钱了
					self.statusMessage( csstatus.TONG_LOST_MONEY, Function.switchMoney( val ) )
				else:
					self.statusMessage( csstatus.TONG_ADD_MONEY, Function.switchMoney( -val ) )

			self.tongMoney = money
			GUIFacade.tong_onSetTongMoney( money )

	def tong_onSetTongLevel( self, level ):
		"""
		define method.
		"""
		self.tongLevel = level
		GUIFacade.tong_onSetTongLevel( level )

	def tong_onSetTongSignMD5( self, iconMD5 ):
		"""
		define method
		"""
		if self.tong_dbID > 0 and iconMD5 != "tcbh":		# 对于原因是退出帮会，tcbh作为识别码
			tongSignMap[self.tong_dbID] = iconMD5
			self.tong_sign_md5 = iconMD5
		self.initTongSign()		# 初始化自己的帮会会标

	def tong_getCanUseMoney( self ):
		"""
		计算帮会可用资金,这样需要显示帮会可用资金的界面就不需要单独计算了
		"""
		buildData = self.tong_buildDatas.get( csdefine.TONG_BUILDING_TYPE_JK, None )
		if buildData is None:
			return 0
		else:
			jkLevel = buildData["level"]
			downLimitMoney = Const.TONG_MONEY_LIMIT[ jkLevel ][ 0 ]
			return self.tongMoney-downLimitMoney

	def tong_onSetTongPrestige( self, prestige ):
		"""
		define method.
		服务器设置客户端帮会声望
		@param prestige: 家族声望
		@type  prestige: int32
		"""
		self.tong_prestige = prestige
		GUIFacade.tong_onSetTongPrestige( prestige )

	def set_tongName( self, tongName ):
		GUIFacade.tong_onSetTongName( self, tongName, self.tongName )

	def set_tong_grade( self, tongGrade ):
		GUIFacade.tong_onSetTongGrade( self, tongGrade, self.tong_grade )


	def tong_onSetAfterFeteStatus( self, val ):
		"""
		defined method.
		服务器设置帮会祭祀完成后的状态（ 月晕甘露、星辉甘露、日光甘露之一 ）
		"""
		#状态定义见csdefine
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_WEEKSTATE", val )

	def tong_onSetVariablePrestige( self, val ):
		"""
		defined method
		服务器设置帮会额外声望
		"""
		self.variable_prestige = val
		DEBUG_MSG( "Current variable prestige: %s"%val )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_VARIABLE_PRESTIAGE", val )

	def tong_setAffiche( self, affiche ):
		"""
		客户端设置服务器上的公告
		"""
		if self.tong_grade <= 0 or self.tong_dbID <= 0:
			self.statusMessage( csstatus.TONG_NO_TONG )
			return
		if len( affiche ) <= csdefine.TONG_AFFICHE_LENGTH_MAX:
			self.cell.tong_setAffiche( affiche )
		else:
			self.statusMessage( csstatus.TONG_SET_STRING_LENGTH_MAX, csdefine.TONG_AFFICHE_LENGTH_MAX )

	def tong_onSetAffiche( self, affiche ):
		"""
		define method.
		服务器设置客户端帮会公告
		"""
		GUIFacade.tong_onSetAffiche( affiche )

	def tong_onMemberOnlineStateChanged( self, memberDBID, onlineState ):
		"""
		define method.
		某成员的在线状态改变了
		"""
		info = self.tong_memberInfos[ memberDBID ]
		info.setOnlineState( onlineState )
		name = info.getName()
		if memberDBID != BigWorld.player().databaseID and onlineState:
			self.statusMessage( csstatus.TONG_MEMBER_LOGIN, name )
		else:
			self.statusMessage( csstatus.TONG_MEMBER_LOGOUT, name )
		GUIFacade.tong_onMemberOnlineStateChanged( memberDBID, onlineState )

	def tong_onMemberLevelChanged( self, memberDBID, level ):
		"""
		define method.
		某成员的级别改变了
		"""
		self.tong_memberInfos[ memberDBID ].setLevel( level )
		GUIFacade.tong_onMemberLevelChanged( memberDBID, level )

	def tong_onMemberNameChanged( self, memberDBID, name ):
		"""
		define method.
		某成员的名字改变了
		"""
		self.tong_memberInfos[ memberDBID ].setName( name )
		GUIFacade.tong_onMemberNameChanged( memberDBID, name )

	def tong_onMemberContributeChanged( self, memberDBID, contribute, totalContribute ):
		"""
		define method.
		某成员的贡献度改变了
		"""
		if self.databaseID == memberDBID:		# 如果是自己的贡献度变化
			oldContribut = self.tong_memberInfos[ memberDBID ].getContribute()
			dispersion = contribute - oldContribut
			if dispersion > 0:
				self.statistic["statTongContribute"] += dispersion

		self.tong_memberInfos[ memberDBID ].setContribute( contribute )
		self.tong_memberInfos[ memberDBID ].updateTotalContribute( totalContribute )
		GUIFacade.tong_onMemberContributeChanged( memberDBID, contribute, totalContribute )

	def tong_setMemberScholium( self, memberDBID, scholium ): #
		"""
		客户端向服务器请求设置某成员的批注
		"""
		if len( scholium ) <= csdefine.TONG_MEMBER_SCHOLIUM_LENGTH_MAX:
			self.cell.tong_setMemberScholium( memberDBID, scholium )
		else:
			self.statusMessage( csstatus.TONG_SET_STRING_LENGTH_MAX, csdefine.TONG_MEMBER_SCHOLIUM_LENGTH_MAX )

	def tong_onMemberScholiumChanged( self, memberDBID, scholium ):
		"""
		define method.
		某成员的批注改变了
		"""
		self.tong_memberInfos[ memberDBID ].setScholium( scholium )
		GUIFacade.tong_onMemberScholiumChanged( memberDBID, scholium )

	def tong_updateMemberMapInfo( self, memberDBID, spaceType, position, lineNumber ):
		"""
		define method.
		服务器更新客户端成员所在地图信息
		"""
		if self.tong_memberInfos.has_key( memberDBID ):
			memInfo = self.tong_memberInfos[ memberDBID ]
			memInfo.setPosition( position )
			memInfo.setSpaceType( spaceType )
			GUIFacade.tong_updateMemberMapInfo( memberDBID, spaceType, position, lineNumber )

	def tong_onSetTongExp( self, exp ):
		"""
		define method.
		服务器设置客户端帮会声望
		@param prestige: 家族声望
		@type  prestige: int32
		"""
		self.tongExp = exp
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_EXP", exp )

	#--------------------------------------------------------------------------------------------------------

	def tong_setMemberGrade( self, targetDBID, grade ):
		"""
		设置某成员的权限
		"""
		if self.tong_grade <= 0 or self.tong_dbID <= 0:
			self.statusMessage( csstatus.TONG_NO_TONG )
			return
		self.cell.tong_setMemberGrade( targetDBID, grade )

	def tong_onMemberGradeChanged( self, userDBID, memberDBID, memberGrade ):
		"""
		define method.
		某成员的权限改变了
		"""
		if not self.tong_dutyNames.has_key( memberGrade ):
			return
		grade = self.tong_memberInfos[ memberDBID ].getGrade()
		self.tong_memberInfos[ memberDBID ].setGrade( memberGrade )
		sid = csstatus.TONG_GRADE_ADD
		if grade > memberGrade:
			sid = csstatus.TONG_GRADE_DEC
		self.statusMessage( sid, self.tong_memberInfos[ userDBID ].getName(), self.tong_memberInfos[ memberDBID ].getName(), self.tong_dutyNames[ memberGrade ] )
		GUIFacade.tong_onMemberGradeChanged( memberDBID, memberGrade )
		#在这里 就是在这里加入NPC任务状态更新请求 by 姜毅
		for key, entity in BigWorld.entities.items():
			if hasattr( entity, "refurbishQuestStatus" ):
				entity.refurbishQuestStatus()

	#---------------------------------------------------------------------------------------------------------
	def tong_requestJoinByPlayerName( self, playerName ):
		"""
		邀请某人加入tong 通过名称
		@param playerName: 要邀请的人的名称
		"""
		if self.tong_grade <= 0 or self.tong_dbID <= 0:
			self.statusMessage( csstatus.TONG_NO_TONG )
			return
		self.statusMessage( csstatus.TONG_NEW_MEMBER_REQUEST, playerName )
		self.base.tong_requestJoinByPlayerName( playerName )

	def tong_requestJoin( self, tergetEntityID ):
		"""
		邀请某人加入tong 本地接口
		@param tergetEntityID: 要邀请的人的ID
		"""
		if self.tong_grade <= 0 or self.tong_dbID <= 0:
			self.statusMessage( csstatus.TONG_NO_TONG )
			return
		tergetEntity = BigWorld.entities.get( tergetEntityID, None )
		if tergetEntity is None:return
		self.statusMessage( csstatus.TONG_NEW_MEMBER_REQUEST, tergetEntity.playerName )
		target = BigWorld.entities.get( tergetEntityID, None )
		if target is not None :
			self.cell.tong_requestJoin( tergetEntityID )

	def tong_onReceiveRequestJoin( self, requestEntityName, tongDBID, tongName, chiefName, tongLevel, memberCount ):
		"""
		define method.
		收到邀请加入帮会
		@param requestEntityName: 邀请者名称
		@oaram tongDBID			: tong的dbid, 后面答复邀请的时候需要用到
		"""
		GUIFacade.tong_onReceiveRequestJoinMessage( requestEntityName,tongName, chiefName,\
		 tongLevel, memberCount )
		GUIFacade.tong_onReceiveRequestJoin( requestEntityName, tongDBID, tongName,chiefName,\
		tongLevel, memberCount )

	def tong_answerRequestJoin( self, agree, tongDBID ):
		"""
		被邀请后 做出回答
		@param agree			: bool, true = 接受
		@oaram tongDBID		: 帮会的的dbid
		"""
		self.cell.tong_answerRequestJoin( agree, tongDBID )

	#---------------------------------------------------------------------------------------------------------

	def tong_requestTongLeague( self, requestTongName ):
		"""
		邀请某帮会结为同盟
		@param requestTongName	:要邀请的目标帮会名称
		"""
		if len( requestTongName ) <= 0:
			return
		self.cell.tong_requestTongLeague( requestTongName )

	def tong_onRequestTongLeague( self, requestByTongName, requestByTongDBID ):
		"""
		define method.
		收到其他帮会邀请同盟
		"""
		GUIFacade.tong_onRequestTongLeague( requestByTongName, requestByTongDBID )

	def tong_answerRequestTongLeague( self, agree, requestByTongDBID ):
		"""
		回应服务器是否愿意结为同盟。
		"""
		self.cell.tong_answerRequestTongLeague( agree, requestByTongDBID )

	def tong_leagueDispose( self, leagueTongDBID ):
		"""
		解除某帮会同盟关系
		"""
		self.cell.tong_leagueDispose( leagueTongDBID )

	#---------------------------------------------------------------------------------------------------------
	def tong_initDutyName( self, duty, dutyName ):
		"""
		define method.
		帮会职位的名称
		"""
		self.tong_dutyNames[ duty ] = dutyName
		GUIFacade.tong_initDutyName( duty, dutyName )

	def tong_setDutyName( self, duty, newName ):
		"""
		设置帮会职位的名称
		"""
		BigWorld.player().cell.tong_setDutyName( duty, newName )

	def tong_onDutyNameChanged( self, duty, newName ):
		"""
		define method.
		设置帮会职位的名称
		"""
		self.tong_dutyNames[ duty ] = newName
		GUIFacade.tong_onDutyNameChanged( duty, newName )

	def tong_enterFound( self, objectID ):
		"""
		Define Method
		与npc对话，请求创建帮会
		@param   objectID: 对话目标
		@type    objectID: OBJECT_ID
		@return: 无
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_FOUND", entity )

	def tong_onChiefConjure( self ):
		"""
		define method.
		收到队长集结令 点击确定后使用tong_onAnswerConjure回应，没点确定不做任何事情
		"""
		GUIFacade.tong_onChiefConjure()

	def isJoinTong( self ):
		"""
		判断玩家是否加入帮会
		tong_grade 不为0 表示玩家一定加入了帮会
		"""
		return self.tong_dbID > 0

	def tong_checkDutyRights( self, duty, right ):
		"""
		检测帮会权限
		"""
		if duty not in csdefine.TONG_DUTY_RIGHTS_MAPPING.keys():	# 判断职位是否存在
			return False
		
		if right not in csdefine.TONG_DUTY_RIGHTS_MAPPING[ duty ]:	# 判断权限是否存在
			return False
		
		return True
	#--------------------------------------------帮会城市战争--------------------------------------------------
	def set_tong_holdCity( self, oldValue ):
		"""
		define mothod.
		设置帮会控制的城市
		@param city: spaceName
		"""
		GUIFacade.onSetHoldCity( self, self.tong_holdCity )

	def tong_onCityWarDie( self ):
		"""
		在战场死亡 弹出复活对话框
		有原地复活和回城复活 （回城复活回回到领地复活）
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )

	def tong_onCityWarRelive( self, reliveType ):
		"""
		界面需要检查是否有 归命符才允许原地复活
		@param reliveType: 复活方式 0：原地复活， 非0：回城复活
		"""
		self.cell.tong_onCityWarRelive( reliveType )

	def tong_leaveCityWarSpace( self ):
		"""
		逃离城市战场
		玩家主动离开战场 使用此接口
		"""
		BigWorld.player().cell.tong_leaveCityWarSpace()

	def tong_onUpdateWarReportTop( self, playerName, tongDBID, killCount, deadCount ):
		"""
		define method.
		更新副本内玩家客户端战果新排名信息
		"""
		pass
#		ECenter.fireEvent( "EVT_ON_UPDTAE_WAR_REPORT", playerName, tongDBID, killCount, deadCount )

	def tong_onCityWarReport( self, tongDBID,  playerName, kill, dead, isInWar ):
		"""
		define method.
		更新副本内玩家客户端战果新排名信息
		"""
		ECenter.fireEvent( "EVT_ON_UPDTAE_WAR_REPORT", playerName, tongDBID, kill, dead, isInWar )

	def tong_onEnterCityWarSpace( self, warRemainTime, tongInfos ):
		"""
		define method.
		玩家进入城市战场副本后的通知, 目前没有什么事情可做， 将来可能会初始化一些东西
		"""
		self.tongInfos = tongInfos 
		# tongInfos :{"left":左帮会DBID, "leftTongName": 左帮会名字, "right" : 右帮会DBID, "rightTongName" : 右帮会名字, "defend":防守方DBID, "defendTongName":防守方帮会名字 }
		self.__isInCityWar = True
		ECenter.fireEvent( "EVT_ON_ENTER_CITYWAR_SPACE", warRemainTime, tongInfos )
		ECenter.fireEvent( "EVT_ON_ENTER_CITYWAR_SPACE_ROLE_NAME", self )

	def tong_onLeaveCityWarSpace( self ):
		"""
		define method.
		玩家离开城市战场副本后的通知, 目前没有什么事情可做， 将来可能会清除一些东西
		"""
		self.__isInCityWar = False
		self.rightTongDBID = self.tong_dbID
		ECenter.fireEvent( "EVT_ON_ROLE_LEAVE_CITYWAR_SPACE",self )
	
	def tong_onCityWarOver( self ):
		# define method
		# 城战结束
		ECenter.fireEvent( "EVT_ON_TONG_CITYWAR_OVER" )

	def tong_openQueryCityWarInfoWindow( self, type ):
		"""
		define method.
		打开查看城战相关信息界面
		"""
		ECenter.fireEvent( "EVT_ON_OPEN_CITYWAR_INFO_WND", type )

	def tong_onQueryCityWarTable( self, datas ):
		"""
		define method.
		城战 赛程查看
		"""
		DEBUG_MSG( "--->>>", datas )
		ECenter.fireEvent( "EVT_ON_RECIEVE_CITYWAR_TABLE", datas )

	def tong_onQueryContest( self, reqLevel, reqMoney ):
		"""
		申请帮会城战报名回调
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				self.cell.tong_confirmContest( reqLevel, reqMoney )
		moneyText = utils.currencyToViewText( reqMoney )
		showMessage( mbmsgs[0x0c43] % moneyText, "", MB_OK_CANCEL, query )

	def tong_requestQueryCityTongMasters( self, cityName ):
		"""
		请求查看城市英雄榜
		"""
		self.cell.tong_requestQueryCityTongMasters( cityName )
		

	def tong_onQueryCityTongMasters( self, index, tongName, date, chiefName ):
		"""
		define method.
		查看城市英雄榜
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_CITY_TONGMASTER", index, tongName, date, chiefName )
	
	def tong_onQueryCityChanged( self, city ) :
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_MASTERCITY", city )
		
	def tong_onQueryCurMaster( self, tongName ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_CURMASTER", tongName )

	def tong_isCityWarTong( self, tong_dbID ) :
		"""
		是否是城战帮会成员
		"""
		if not self.__isInCityWar : return False
		lTongDBID = self.tongInfos.get( "left", 0 )
		rTongDBID = self.tongInfos.get( "right", 0 )
		dTongDBID = self.tongInfos.get( "defend", 0 )
		cityWars = [lTongDBID, rTongDBID, dTongDBID]
		return tong_dbID in cityWars

	def tong_onRequestSetCityRevenueRate( self, rate ):
		"""
		define method.
		玩家请求设置城市消费税  打开界面
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_CITY_TAXRATE", rate )

	def tong_requestSetCityRevenueRate( self, rate ):
		"""
		玩家请求设置城市消费税 通知服务器
		"""
		self.cell.tong_requestSetCityRevenueRate( rate )

	def tong_onUpdateCityWarPoint( self, tongDBID, point ):
		"""
		define method.
		服务器传过来的当前某帮会的战场积分
		"""
#		DEBUG_MSG( "current:%d, %d" % (tongDBID, point) )
		ECenter.fireEvent( "EVT_ON_UPDATE_CITYWAR_POINTS", tongDBID, point )
		self.cityWarPointLogs[ tongDBID ] = point
	
	def tong_onRequestCityTongRevenue( self, money ):
		# define method
		# 申请领取城市税收回调
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.tong_onRequestCityTongRevenue()
				
		showMessage( mbmsgs[0x0c44] % ( money / 10000 ), "", MB_YES_NO, result )
	
	def tong_onAbandonTongCityNotify( self, city ):
		"""
		放弃占领城市的回调
		"""
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.tong_onAbandonTongCity( city )
		cityNameCN = csconst.TONG_CITYWAR_CITY_MAPS.get( city, "" )
		showMessage( mbmsgs[0x0c45] %cityNameCN, "", MB_YES_NO, result )

	#---------------------------------------------帮会建筑---------------------------------------------
	def tong_onReceiveTongBuildInfo( self, buildData ):
		"""
		define method.
		接收服务器给的帮会建筑信息
		通过 cell.tong_onGetBuildInfo 获取
		@param buildingType:建筑类别
		@param data: 建筑数据 查看 def -> TONGBUILDINFO
		"""
		if buildData is None:return
		type = buildData["type"]
		self.tong_buildDatas[type] = buildData
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_BUILD_INFO", buildData )

	def tong_openBuildingWindow( self, buildingType ):
		"""
		define method.
		服务器通知打开建筑界面
		@param buildingType: csdefine.TONG_BUILDING_TYPE_**
		"""
		#if self.tong_grade&( csdefine.TONG_GRADES &~ csdefine.TONG_GRADE_BUILDING ) > 0:return
		# 打开界面后 直接调用
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_BUILDS_RESEARCH", buildingType )

	def tong_onSetShenShouType( self, shenshouLevel, shenshouType ):
		"""
		define method.
		服务器设置客户端神兽级别与类别
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_SHENSHOU_INFO", shenshouLevel, shenshouType )

	def tong_openShenShouSelectWindow( self, shenshouLevel, shenshouType ):
		"""
		define method.
		服务器通知打开神兽选择界面
		csdefine.TONG_SHENSHOU_TYPE_*
		"""
		if not self.tong_checkDutyRights( self.tong_grade, csdefine.TONG_RIGHT_PET_SELECT ):
			return
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SHENSHOU_BRECKON", shenshouLevel, shenshouType )
		# 打开界面后 直接调用
	
	def tong_onPauseBuildTongBuilding( self, pauseType ):
		"""
		define method.
		服务器设置暂停帮会建筑
		"""
		if self.tong_curBuildType == pauseType:
			self.tong_curBuildType = 0
		if pauseType in self.tong_pauseBuilds:
			return
		self.tong_pauseBuilds.append( pauseType )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_PAUSE_BUILD", pauseType )

	def tong_shenShouSelect( self, type = 1 ):
		"""
		选取某个神兽
		"""
		BigWorld.player().cell.tong_onSelectShouShou( type )

	#-------------------------------------------掠夺战-----------------------------------------------------

	def tong_onRequestRobWar( self ):
		"""
		define method.
		玩家向NPC申请掠夺战
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_REQUEST_ROB_WAR" )
		# 这里要打开输入框
#		from gbref import rds # 临时使用  做界面后应该去掉
#		BigWorld.player().chat_say( "使用此功能：请先在聊天输入框输入帮会名称,不要按回车，然后和NPC对话。等界面制作完毕将修改此功能。" )
#		self.tong_requestRobWar( rds.ruisMgr.chatWindow._ChatWindow__pyCBMsg.text )

	def tong_findRequestRobWar( self, tongName ):
		"""
		玩家查找这个要掠夺的帮会
		"""
		BigWorld.player().cell.tong_findRequestRobWar( tongName )

	def onfindRequestRobWarCallBack( self, tongLevel, tongShenShouType, shenshouLevel, tongRobWarIsFailure ):
		"""
		define method.
		玩家查找这个要掠夺的帮会 的服务器回调
		@param tongLevel			: 查询帮会的等级 为0代表没有找到记录
		@param tongShenShouType		: 神兽的类型	为0代表帮会没有神兽
		@param shenshouLevel		: 神兽的级别
		@param tongRobWarIsFailure	: 帮会在本周掠夺战是否有失败过 bool
		"""
		if tongLevel <= 0: # 没有找到这个帮会
			return
		BigWorld.player().statusMessage( csstatus.CITYWAR_EXPLAIN, tongLevel, tongShenShouType, shenshouLevel, tongRobWarIsFailure )

	def tong_requestRobWar( self, tongName ):
		"""
		向服务器提交要掠夺的帮会 确认了这个战争目标帮会
		"""
		player = BigWorld.player()
		for dbid, league in player.tong_leagues.iteritems():
			if tongName == league:
				player.statusMessage( csstatus.TONG_ROB_WAR_LEAGUE_INVALID )
				return
		player.cell.tong_onAnswerRobWar( tongName )

	def tong_setRobWarTargetTong( self, tongDBID ):
		"""
		define method.
		设置帮会掠夺战对象
		这里可以代表战争开始和结束 tongDBID为0结束， 可以
		恢复如名字颜色，其他特征等
		"""
		if tongDBID == 0 :
			self.tong_onRobWarOver()

		self.robWarTargetTong = tongDBID
		if tongDBID != 0 :
			self.tong_onRobWarBegin()

	def tong_isRobWarEnemyTong( self, tongDBID ) :
		"""
		是否正在掠夺战中的敌对帮会
		"""
		return self.robWarTargetTong == tongDBID and tongDBID != 0

	def tong_isInRobWar( self ):
		"""
		是否正在进行帮会掠夺战
		"""
		return self.robWarTargetTong != 0

	def tong_isTongMember( self, role ) :
		"""
		是否是帮会成员
		"""
		return self.tong_dbID != 0 and self.tong_dbID == role.tong_dbID

	#-----------------------------------帮会活动---------------------------------------------------------------

	def tong_openReuqestCampaignMonsterRaidWindow( self, npcID, campaignLevelList ):
		"""
		define method.
		打开帮会活动申请界面
		@param campaignLevelList: 活动的所有级别
		"""
		BigWorld.player().statusMessage( csstatus.MONSTER_RAID_LEVEL, campaignLevelList )

	def tong_requestCampaignMonsterRaidWindow( self, npcID, campaignLevel ):
		"""
		向服务器申请活动级别
		"""
		BigWorld.player().cell.tong_reuqestCampaignMonsterRaidWindow( npcID, campaignLevel )


	# ----------------------------------------- 帮会仓库 ------------------------------------------------
	def tong_receiveStorageItem( self, items ):
		"""
		Define method.
		接收帮会仓库物品信息的函数

		@param items : 物品列表
		@type items : ARRAY OF ITEM
		"""
		for item in items:
			order = item.order
			bankIndex = order/csdefine.KB_MAX_SPACE
			itemInfo = ObjectItem( item )
			ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_ITEM", bankIndex, order, itemInfo )

	def tong_enterStorage( self, storageBagPopedom, fetchRecord ):
		"""
		Define method.
		进入帮会仓库

		@param storageLevel : 仓库等级
		@type storageLevel : UINT8
		"""

		try:
			self.tong_storage_npcID = self.targetEntity.id
		except:
			self.tong_storage_npcID = 0
		self.storageBagPopedom = storageBagPopedom
		self.fetchRecord = fetchRecord

		#self.tong_ck_level = storageLevel
		self.tong_ck_requestItemCount = 0
		self.tong_requestStorageItem()
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_ENTER_STORAGE" )

	def tong_requestStorageItem( self ):
		"""
		请求帮会仓库物品数据,每次请求40个物品数据.

		"""
		#orderCount = csconst.TONG_WAREHOUSE_LIMIT[ self.tong_ck_level ]
		if self.tong_ck_requestItemCount + 1 > len( self.storageBagPopedom ) * 2:
			self.tong_ck_requestItemCount = 0
			self.tong_requestStorageLog()		# 请求完物品数据则开始请求log数据
			return

		self.base.tong_requestStorageItem( self.tong_ck_requestItemCount )
		self.tong_ck_requestItemCount += 1
		BigWorld.callback( 0.2, self.tong_requestStorageItem )	# 每隔0.2秒请求一次数据

	def tong_requestStorageLog( self ):
		"""
		请求仓库的log信息,每次请求50条
		"""
		if self.tong_ck_requestLogCount >= 3:	# 已经请求完毕
			self.tong_ck_requestLogCount = 0
			return
		if self.tong_ck_requestLogCount * 50 > len( self.tong_storageLog ):	# 如果数据少于请求的条数,说明数据已经发送完毕
			self.tong_ck_requestLogCount = 0
			return
		self.base.tong_requestStorageLog( self.tong_ck_requestLogCount )
		self.tong_ck_requestLogCount += 1
		BigWorld.callback( 0.5, self.tong_requestStorageLog )	# 每隔0.5秒请求一次数据

	def tong_receiveStorageLog( self, log ):
		"""
		Define method.
		接收帮会仓库log信息的函数

		@param log : 一条log信息[ playerName, operation, itemID, itemCount ]
		@type log : PYTHON
		"""
		self.tong_storageLog.append( log )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_LOG", log )

	def tong_storeItem2Order( self, srcOrder, dstOrder, entityID ):
		"""
		往帮会仓库里存储物品的接口，已知目标物品格

		param srcOrder:	背包格子号
		type srcOrder:	INT16
		param dstOrder:	帮会仓库格子号
		type dstOrder:	INT16
		param entityID:	帮会npc的id
		type entityID:	OBJECT_ID
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_storeItem2Order( srcOrder, dstOrder, entityID )

	def tong_storeItem2Bag( self, srcOrder, bagID ):
		"""
		往帮会仓库里存储物品的接口，已知目标物品格

		@param srcOrder:	背包格子号
		@type srcOrder:	INT16
		@param bagID : 包裹id
		@type bagID : UINT8
		@param entityID:	帮会npc的id
		@type entityID:	OBJECT_ID
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_storeItem2Bag( srcOrder, bagID, entityID )

	def tong_storeItem2Storage( self, srcOrder, entityID ):
		"""
		往帮会仓库里存储物品的接口，已知目标物品格

		param srcOrder:	背包格子号
		type srcOrder:	INT16
		param entityID:	帮会npc的id
		type entityID:	OBJECT_ID
		"""
		if entityID == 0: entityID = self.tong_storage_npcID
		self.cell.tong_storeItem2Storage( srcOrder, entityID )


	def tong_fetchItem2Order( self, srcOrder, dstOrder, entityID ):
		"""
		左键拖放物品进入玩家背包

		param dstOrder:	背包格子号
		type dstOrder:	INT16
		param srcOrder:	帮会仓库格子号
		type srcOrder:	INT16
		param entityID:	帮会npc的id
		type entityID:	OBJECT_ID
		"""
		item = self.getItem_( dstOrder )
		if item is not None:
			try:
				BagPopedom = self.storageBagPopedom[srcOrder / csdefine.KB_MAX_SPACE]
			except:
				DEBUG_MSG( "找不到对应包裹的权限数据。" )
				return
			quality = item.getQuality()
			if BagPopedom["qualityLowerLimit"] > quality:
				self.statusMessage( csstatus.TONG_STORAGE_QUALITY_LOWER )
				return
			elif BagPopedom["qualityUpLimit"] < quality:
				self.statusMessage( csstatus.TONG_STORAGE_QUALITY_HIGHER )
				return

		npc = BigWorld.entities.get(self.tong_storage_npcID, None)
		if npc is not None and self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			return False

		self.cell.tong_fetchItem2Order( srcOrder, dstOrder, npc.id )


	def tong_fetchItem2Kitbags( self, srcOrder ):
		"""
		右键点击仓库物品到玩家背包

		param srcOrder:	背包格子号
		type srcOrder:	INT16
		param entityID:	帮会npc的id
		type entityID:	OBJECT_ID
		"""
		npc = BigWorld.entities.get(self.tong_storage_npcID, None)
		if npc is not None and self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			return False

		self.cell.tong_fetchItem2Kitbags( srcOrder, npc.id )

	def tong_fetchSplitItem2Kitbags(self, srcOrder, amount):
		"""
		份拆仓库物品到玩家背包

		param srcOrder:	背包格子号
		type srcOrder:	INT16
		param amount:	数量
		type amount: INT16
		"""
		npc = BigWorld.entities.get(self.tong_storage_npcID, None)
		if npc is not None and self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			return False

		self.cell.tong_fetchSplitItem2Kitbags(npc.id ,srcOrder, amount)

	def tong_storeItemUpdate( self, item ):
		"""
		Define method.
		背包往钱庄存储一个物品的更新函数

		param item:	物品实例
		type item:	ITEM
		"""
		order = item.order
		itemInfo = ObjectItem( item )
		bankIndex = order/csdefine.KB_MAX_SPACE
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_ITEM_UPDATE", bankIndex, order, itemInfo )

	def tong_moveStorageItem( self, srcOrder, dstOrder ):
		"""
		仓库内物品互换
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_moveStorageItem( srcOrder, dstOrder, entityID )

	def tong_moveItemCB( self, srcOrder, dstOrder ):
		"""
		Define method.
		帮会仓库移动物品的客户端通知函数
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_MOVE_ITEM", srcOrder, dstOrder )


	def tong_delItemUpdate( self, order ):
		"""
		Define method.
		帮会仓库删除一个物品的客户端通知函数
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_DEL_ITEM", order )

	def tong_fetchStorageItemCB( self, amount ):
		"""
		Define method.
		取物品成功,更新玩家今日取物品数据

		@param amount : 取出物品得数量
		@type amount : INT32
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_FETCH_CHANGE", amount )

	def tong_renameStorageBag( self, bagID, newName ):
		"""
		更改帮会仓库包裹名

		@param bagID : 包裹id
		@type bagID : UINT8
		@param newName : 包裹位名字
		@type newName : STRING
		"""
		# 这里进行初步的参数检查
		entityID = self.tong_storage_npcID
		self.cell.tong_renameStorageBag( bagID, newName, entityID )

	def tong_updateStorageBagName( self, bagID, newName ):
		"""
		Define method.
		帮会仓库包裹名更新函数

		@param bagID : 包裹id
		@type bagID : UINT8
		@param newName : 包裹位名字
		@type newName : STRING
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_NAME_CHANGE", bagID, newName )

	def tong_changeStorageBagLimit( self, bagID, officialPos, limitNum ):
		"""
		改变帮会职位的仓库存储权限

		@param bagID : 包裹id
		@type bagID : UINT8
		@param officialPos : 职位
		@param officialPos : INT32
		@param newName : 包裹位名字
		@type newName : STRING
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_changeStorageBagLimit( bagID, officialPos, limitNum, entityID )
		for storagePopedom in self.storageBagPopedom:
			if storagePopedom["bagID"] == bagID:
				dutyPopedom = storagePopedom["fetchItemLimit"]
				dutyPopedom[officialPos] = limitNum

	def tong_changeStorageQualityLower( self, bagID, quality ):
		"""
		改变帮会仓库包裹的品质下限限制

		@param bagID : 包裹id
		@type bagID : UINT8
		@param quality : 品质
		@param quality : UINT8
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_changeStorageQualityLower( bagID, quality, entityID )
		for storagePopedom in self.storageBagPopedom:
			if storagePopedom["bagID"] == bagID:
				storagePopedom["qualityLowerLimit"] = quality

	def tong_changeStorageQualityUp( self, bagID, quality ):
		"""
		改变帮会仓库包裹的品质上限限制

		@param bagID : 包裹id
		@type bagID : UINT8
		@param quality : 品质
		@param quality : UINT8
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_changeStorageQualityUp( bagID, quality, entityID )
		for storagePopedom in self.storageBagPopedom:
			if storagePopedom["bagID"] == bagID:
				storagePopedom["qualityUpLimit"] = quality

	#------------------------------------------帮会捐献金钱-------------------------------------------------------
	def tong_onContributeToMoney( self ):
		"""
		define method.
		捐献金钱 打开界面
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_DONATE_WND_OPEN" )

	def tong_contributeToMoney( self, money ):
		"""
		向服务器请求捐献
		"""
		self.cell.tong_contributeToMoney( money )

	#------------------------------------------帮会祭祀活动-------------------------------------------------------

	def tong_setFeteData( self, value ):
		"""
		define method.
		祭祀活动供奉值
		@param value: 当前供奉值
		"""
		if value < 0:
			# 小于零则不显示， 可能是离开领地或者活动结束了
			BigWorld.player().statusMessage( csstatus.FETE_DATA_OVERRUN )
		else:
			spaceType = self.getCurrentSpaceType()
			if spaceType == csdefine.SPACE_TYPE_TONG_TERRITORY:
				BigWorld.player().statusMessage( csstatus.FETE_DATA_VALUE, value )


	def tong_feteExchange( self, npcID ):
		"""
		Define method.
		开始祭祀活动仙灵换物

		@param npcID : 仙灵换物npc id
		@type npcID : OBJECT_ID
		"""
		pass

	def tong_onRobWarBegin( self ) :
		"""
		帮会掠夺战开始，改变附近敌对帮会玩家的名字颜色
		"""
		enemies = self.findEnemyTongMembersNearby()
		for ent in enemies :
			ECenter.fireEvent( "EVT_ON_TONG_ROB_WAR_BEING", ent )		# 通知界面改变名字颜色

	def tong_onRobWarOver( self ) :
		"""
		帮会掠夺战结束，恢复附近敌对帮会玩家的名字颜色
		"""
		enemies = self.findEnemyTongMembersNearby()
		for ent in enemies :
			ECenter.fireEvent( "EVT_ON_TONG_ROB_WAR_OVER", ent )		# 通知界面恢复名字颜色

	#------------------------------------------保护帮派活动-------------------------------------------------------
	def tong_onProtectTongDie( self ) :
		"""
		保护帮派活动副本中死亡
		"""
		self.cell.tong_onProtectTongDie()

	#------------------------------------------帮会查询界面-------------------------------------------------------
	def tong_setTongAD( self, ad ):
		"""
		设置自己帮会的广告， 帮会列表界面上
		"""
		if self.tong_dbID <= 0:
			return
		self.cell.tong_setTongAD( self.tong_dbID, ad )

	def tong_requestTongList( self, camp = 0 ):
		"""
		向服务器请求获得帮会列表
		"""
		self.tongQueryTongListIndex = 0
		requestTongList( self.id, camp )

	def tong_onReceiveTongList( self, tongDBID, tongName, tongID, tongLevel, tongPrestige, isHoldCity ):
		"""
		define method.
		接收帮会列表
		"""
		datas = self.TongListInfos.get( tongDBID )
		if not datas:
			datas = {}
			self.TongListInfos[ tongDBID ] = datas
		datas[ "tongName" ] = tongName
		datas[ "tongID" ] = tongID
		datas[ "tongLevel" ] = tongLevel
		datas[ "tongPrestige" ] = tongPrestige
		datas["tongDBID"] = tongDBID
		datas["isHoldCity"] = isHoldCity
		ECenter.fireEvent( "EVT_ON_TONG_RECEIVE_TONG_DATAS", datas )

	def tong_receiveTongListCompleted( self ):
		"""
		define method.
		接收帮会列表完毕
		"""
		self.tongQueryTongListIndex = -1
		ECenter.fireEvent( "EVT_ON_TONG_RECEIVE_TONG_COMPLETED", len( self.TongListInfos ) )

	def tong_queryTongInfo( self, tongDBID ):
		"""
		向服务器请求获得帮会信息
		"""
		self.cell.tong_queryTongInfo( tongDBID )

	def tong_onReceiveTongInfo( self, tongDBID, memberCount, chiefName, holdCity, leagues, ad ):
		"""
		define method.
		接收tong_queryTongInfo返回某帮会的基础信息
		"""
		toBuildType, toBuildLevel = 0, 0
		ECenter.fireEvent( "EVT_ON_TONG_RECEIVE_TONG_INFO", tongDBID, memberCount, toBuildType, toBuildLevel, chiefName, holdCity, leagues, ad )

	def tong_requestJoinToTong( self, tongDBID ):
		"""
		申请加入到某个帮会
		"""
		if self.tong_dbID > 0:
			self.statusMessage( csstatus.TONG_HAS_TONG )
			return
		try:
			requestTime = self.tongRequestInfo[tongDBID]
		except KeyError:
			self.tongRequestInfo[tongDBID] = time.time()
		else:
			now = time.time()
			if requestTime + Const.JOIN_TONG_REQUEST_LIMIT_INTERVAL > now:	# 20分钟内申请过
				self.statusMessage( csstatus.TONG_REQUEST_JOIN_LIMIT, int(Const.JOIN_TONG_REQUEST_LIMIT_INTERVAL/60) )
				return
			self.tongRequestInfo[tongDBID] = now
		self.cell.tong_requestJoinToTong( tongDBID )

	def tong_answerJoinToTong( self, playerDBID, rs_id = RS_NO ):
		"""
		回应玩家加入帮会申请
		"""
		if self.tong_dbID <= 0:
			return
		agree = rs_id == RS_YES
		self.cell.tong_answerJoinToTong( playerDBID, agree )

	def tong_onReceiveiJoinInfo( self, playerDBID, playerName ):
		"""
		define method.
		接收申请加入帮会的玩家信息
		"""
		# "[%s]希望加入贵帮，是否同意？"
		jionMsg = mbmsgs[0x0c41] %playerName
		if self.applyMsgBox:
			self.applyMsgBox.hide()
		self.applyMsgBox = showAutoHideMessage( 30, jionMsg, "", MB_YES_NO, Functor( self.tong_answerJoinToTong, playerDBID ), gstStatus = Define.GST_IN_WORLD )

	def tong_openTongQueryWindow( self ):
		"""
		define method.
		与NPC对话后，进入帮会查询界面
		"""
		ECenter.fireEvent( "EVT_ON_TONG_QUERY_WND_SHOW" )
		self.tong_requestTongList()

	def tong_openTongADEditWindow( self ):
		"""
		define method.
		与NPC对话后，进入帮会宣传编辑界面
		"""
		ECenter.fireEvent( "EVT_ON_TONG_AD_EDIT_SHOW" )

	# ----------------------------------------------------------------
	# 按需求添加的方法
	# ----------------------------------------------------------------
	def findEnemyTongMembersNearby( self ) :
		"""
		搜寻附近敌对帮会成员
		@rtype		list	玩家列表
		"""
		player = BigWorld.player()
		members = []
		nearbyEntities = BigWorld.entities.values()
		for ent in nearbyEntities :
			if not ent.isEntityType( csdefine.ENTITY_TYPE_ROLE ) : continue
			if not player.tong_isRobWarEnemyTong( ent.tong_dbID ) : continue
			members.append( ent )
		return members

	def askChangeTongName( self, npcID ):
		"""
		Define method.
		触发帮会改名
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_CHANGE_NAME", npcID )

	#------------------------------------------帮会会标 by 姜毅-------------------------------------------------------
	#------------------------会标管理相关------------------------
	def submitTongSign( self, path ):
		"""
		上传帮会图标

		@param path : 图标路径
		@type  path : string
		"""
		if self.submitting:
			self.statusMessage( csstatus.TONG_SIGN_SUBMITTING )
			return
		self.iconString = Function.getIconStringByPath( path )
		iconstrlen = len( self.iconString )
		DEBUG_MSG( "Length of the submit icon %i ."%iconstrlen )
		if len( self.iconString ) > 4500:	# 图片过大
			self.statusMessage( csstatus.TONG_SIGN_NOT_ICON_SIZE )
			self.iconString = None
			return
		iconMD5 = _md5.new(self.iconString).digest()
		if iconMD5 == self.tong_sign_md5:
			self.statusMessage( csstatus.TONG_SIGN_HAS_NOW )
			return
		packs_num = int( iconstrlen/250 ) + 1
		encodeName = str( struct.unpack_from("l", iconMD5)[0] )
		imgStr = Function.getIconByString( self.iconString )
		self.saveTongSign( imgStr, iconMD5 )
		del imgStr
		self.base.tong_submitSignReady( iconMD5, iconstrlen, packs_num )

	def onTong_submitSignReady( self ):
		"""
		define method
		上传会标预备回调
		"""
		self.iconStringList = []
		iconstrlen = len( self.iconString )
		packs_num = int( iconstrlen/250 ) + 1
		for i in xrange( 0, packs_num ):
			index = i * 250
			end = index + 250
			sList = self.iconString[index:end]
			self.iconStringList.append( sList )
		self.iconString = None
		self.submitting = True
		self.submitTimerID = BigWorld.callback( 0.1, self.submitIconDetect )

	def submitIconDetect( self ):
		"""
		上传图标的timer回调，每次上传self.iconStringList中的一个元素
		"""
		index = len( self.iconStringList )
		if index <= 0: return
		iconString = self.iconStringList.pop(index - 1)
		self.base.tong_submitSign( iconString, index )
		BigWorld.callback( 0.1, self.submitIconDetect )

	def onTong_submitSign( self ):
		"""
		define method
		上传会标成功回调
		"""
		self.submitting = False

	def changeTongSign( self, isSysIcon, reqMoney, path = None ):
		"""
		更换帮会会标

		@param isSysIcon : 是否系统图标
		@type  isSysIcon : BOOL
		@param reqMoney  : 所需金钱
		@type  reqMoney  : INT32
		@param path : 图标路径
		@type  path : string
		"""
		if self.tongMoney < reqMoney:
			self.statusMessage( csstatus.TONG_SIGN_CHANGE_NOT_MONEY )
			return
		if isSysIcon and path is not None:
			if path == self.tong_sign_md5:
				self.statusMessage( csstatus.TONG_SIGN_USING_NOW )
				return
			self.base.tong_changeSing( isSysIcon, reqMoney, path )
		else:
			iconString = Function.getIconStringByPath( path )
			if iconString is None or len( iconString ) <= 0:
				ERROR_MSG( "icon string empty." )
				return
			if len( iconString ) > 4500:	# 图片过大
				self.statusMessage( csstatus.TONG_SIGN_NOT_ICON_SIZE )
				del iconString
				return
			iconMD5 = _md5.new(iconString).digest()
			if iconMD5 == self.tong_sign_md5:
				self.statusMessage( csstatus.TONG_SIGN_HAS_NOW )
				return
			imgStr = Function.getIconByString( iconString )
			self.saveTongSign( imgStr, iconMD5 )
			self.base.tong_changeSing( isSysIcon, reqMoney, iconMD5 )
			del iconString
			del imgStr

	def cancleTongSign( self ):
		"""
		取消帮会会标
		"""
		if self.tong_sign_md5 is None or self.tong_sign_md5 == "":
			return
		self.base.tong_cancleSing()

	def tongSignTalkResult( self, result ):
		"""
		Define method.
		帮会会标NPC对话结果
		"""
		if result == 1:
			if self.tongMoney < csconst.USER_TONG_SIGN_REQ_MONEY:
				self.statusMessage( csstatus.TONG_SIGN_NOT_THAT_MONEY )
				return
			ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SUBMIT_TONG_SIGN" )
		elif result == 2:
			ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_CHANGE_TONG_SIGN" )
		elif result == 3:
			def query( rs_id ):
				if rs_id == RS_OK:
					self.cancleTongSign()
			showMessage( mbmsgs[0x0c42], "", MB_OK_CANCEL, query )
		else:
			ERROR_MSG( "tong sign NPC talk Result Error." )

	#------------------------会标传输相关------------------------
	def tongSignCheck( self ):
		"""
		自定义会标这功能虽然有趣但在网络处理方面很蛋疼，所以能省就省
		"""
		player = BigWorld.player()
		if player is None:
			return
		r_tong_dbid = self.tong_dbID
		# 无帮会或者无会标的
		if r_tong_dbid <= 0:
			return
		# 如果动态会标列表里有该帮会的会标数据，用本地资源做会标，否则向服务器申请相关数据
		if r_tong_dbid in tongSignMap:
			self.showLocalTongSign( tongSignMap[r_tong_dbid] )
			return
		# 正在请求的不管
		if r_tong_dbid in player.tong_sign_searching_list:
			return

		player.tong_sign_searching_list[r_tong_dbid] = self.tongName
		player.tong_sign_searcher_list[r_tong_dbid] = self
		player.base.getTongSignMD5( r_tong_dbid )

	def onGetTongSignMD5( self, tongDBID, iconMD5 ):
		"""
		define method
		获得帮会会标MD5回调
		"""
		DEBUG_MSG( "get player tong icon md5 %s( %i )"%( iconMD5, tongDBID ) )
		if iconMD5 is None or iconMD5 == "":
			if tongDBID not in tongSignMap:
				tongSignMap[tongDBID] = ""
			if tongDBID in self.tong_sign_searching_list:
				self.tong_sign_searching_list.pop( tongDBID )
				self.tong_sign_searcher_list.pop( tongDBID )
			return
		# 检测本地资源，本地有的话直接用本地资源
		target = self.tong_sign_searcher_list[tongDBID]
		if target is None and tongDBID in self.tong_sign_searching_list:
			self.tong_sign_searching_list.pop( tongDBID )
			self.tong_sign_searcher_list.pop( tongDBID )
			return
		if target.showLocalTongSign( iconMD5 ):
			tongSignMap[tongDBID] = iconMD5
			if tongDBID in self.tong_sign_searching_list:
				self.tong_sign_searching_list.pop( tongDBID )
				self.tong_sign_searcher_list.pop( tongDBID )
			return
		# 否则，向服务器申请
		self.base.clientGetTongSignIcon( tongDBID )

	def clientGetTongSignReady( self, tongDBID, packs_num, iconMD5 ):
		"""
		define method
		客户端准备接受会标
		"""
		self.buf_IconMD5 = iconMD5
		self.buf_PacksNum = packs_num
		self.buf_iconString = {}
		self.base.onClientGetTongSignReady()

	def clientGetTongSignFinished( self ):
		"""
		"""
		self.buf_IconMD5 = ""
		self.buf_PacksNum = 0
		self.buf_iconString.clear()

	def onClientGetTongSignIcon( self, tongDBID, index, iconString ):
		"""
		define method
		获得帮会会标图标回调
		"""
		self.buf_iconString[index] = iconString
		dictLen = len( self.buf_iconString )
		if dictLen < self.buf_PacksNum:
			DEBUG_MSG( "tong %i submitting icon continue, index %i, len %i. "%( tongDBID, index, dictLen ) )
			return
		fullIconString = ""
		for k in self.buf_iconString.iterkeys():
			fullIconString += self.buf_iconString[k]

		target = None
		if tongDBID in self.tong_sign_searching_list:
			tongName = self.tong_sign_searching_list.pop( tongDBID )
			target = self.tong_sign_searcher_list.pop( tongDBID )

		if fullIconString == "":
			ERROR_MSG( "Getting user tong sign failed, iconString is empty." )
			self.clientGetTongSignFinished()
			return
		iconMD5 = _md5.new(fullIconString).digest()
		if iconMD5 != self.buf_IconMD5:
			ERROR_MSG( "Get icon error, tong %i ."%tongDBID )
			self.clientGetTongSignFinished()
			return
		DEBUG_MSG( "get player tong icon string len %i( %i )"%( len( fullIconString ), tongDBID ) )

		encodeName =  str( struct.unpack_from("l", iconMD5)[0] )
		tongSignMap[tongDBID] = iconMD5
		imgStr = Function.getIconByString( fullIconString )
		self.saveTongSign( imgStr, iconMD5 )	# 把该帮会的自定义会标存入本地

		target.showLocalTongSign( iconMD5 )
		self.clientGetTongSignFinished()

	#------------------------会标显示、存储相关------------------------
	def initTongSign( self ):
		"""
		初始化玩家自身的会标信息
		"""
		player = BigWorld.player()
		self.showLocalTongSign( player.tong_sign_md5 )

	def showLocalTongSign( self, iconMD5 ):
		"""
		显示本地资源已有的会标
		前提是对象已经有从属帮会
		"""
		if iconMD5 is None or iconMD5 == "":
			ECenter.fireEvent( "EVT_ON_TOGGLE_HAS_TONG_SIGN", self, "", False )
			return False

		if self.getTongSignPath( iconMD5 ) is not None:
			ECenter.fireEvent( "EVT_ON_TOGGLE_HAS_TONG_SIGN", self, iconMD5, True )
			return True
		else:
			encodeName =  str( struct.unpack_from("l", iconMD5)[0] )
			s_path = self.getTongSignPath( encodeName )
			if s_path is not None:
				ECenter.fireEvent( "EVT_ON_TOGGLE_HAS_TONG_SIGN", self, s_path, True )
				return True
		return False

	def getTongSignPath( self, fullName ):
		"""
		检测并返回某个会标路径
		"""
		sec = openSection( "TongIcons", True )
		if sec.has_key( fullName + ".dds" ):
			del sec
			return "TongIcons/" + fullName + ".dds"
		elif sec.has_key( fullName + ".bmp" ):
			del sec
			return "TongIcons/" + fullName + ".bmp"
		sec = openSection( fullName )
		if sec is not None:
			del sec
			return fullName
		return None

	def saveTongSign( self, imgStr, iconMD5 ):
		"""
		把会标资源存入本地
		"""
		path = "TongIcons"		# 图标文件夹
		sec = openSection( path, True )	# 这个肯定不为空，要不地球就毁灭了
		encodeName =  str( struct.unpack_from("l", iconMD5)[0] )
		fileName = encodeName + ".bmp"	# 文件名
		if sec.has_key("fileName"):
			return
		Function.makeFile( path, fileName, imgStr )	# 创建路径，写入文件


	# ---------------------------- 帮会擂台赛相关 -------------------------------------------
	def tong_onEnterAbaSpace( self ):
		"""
		define method
		玩家进入帮会擂台战场
		"""
		BigWorld.callback( 2, self.onUpdateRoleNameColor )
		
	def tong_onLeaveWarSpace( self ):
		"""
		define method.
		玩家离开了战场
		可以做一些清理工作
		如：积分， 战果 等
		"""
		GUIFacade.tong_onLeaveWarSpace()

	def tong_leaveWarSpace( self ):
		"""
		逃离战场
		玩家主动离开战场 使用此接口
		"""
		if self.getState() != csdefine.ENTITY_STATE_FREE :
			self.statusMessage( csstatus.TONG_ABATTOIR_ESCAPE_IN_FREE_STATE )
			return
		BigWorld.player().cell.tong_leaveWarSpace()
#		self.tong_onLeaveWarSpace()

	def tong_onInTongAbaRelivePoint( self, index = 0 ): #界面选择一个复活点，否则选择A点
		"""
		玩家在战场内选择了复活点位置
		@param index : 3个复活点其中一个索引 0, 1, 2
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_TONG_ABA:
			self.cell.tong_onInTongAbaRelivePoint( index )
			self.onStateChanged( csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_FREE )
			return

	def tong_onInitRemainAbaTime( self, restTime,abaRound ):
		"""
		Define method.
		帮会擂台赛剩余时间更新函数

		@param restTime : 擂台赛持续多长时间
		@type restTime : INT64
		"""
		DEBUG_MSG( "--->>>This abattoir's rest time is %i." % restTime )
		if abaRound != csdefine.ABATTOIR_FINAL:
			GUIFacade.tong_onInitRemainWarTime( (15 * 60 - restTime) + Time.time() )
		else:
			GUIFacade.tong_onInitRemainWarTime( (20 * 60 - restTime) + Time.time() )

	def updatePlayerAbaRecord( self, playerName, killNum, beKilledNum, tongDBID ):
		"""
		Define method.
		擂台赛战果表更新函数

		@param playerName : 玩家名字
		@type playerName : STRING
		@param killNum : 玩家杀人数
		@type killNum : INT16
		@param beKilledNum : 被杀数
		@type beKilledNum : INT16
		@param tongDBID : 玩家所在的帮会dbid
		@type tongDBID : INT64
		"""
		DEBUG_MSG( "--->>>playerName:%s,killNum:%i,beKilledNum:%i,tongDBID:%i." % ( playerName, killNum, beKilledNum, tongDBID ) )
		GUIFacade.tong_updatePlayerWarReport( self.id, playerName, tongDBID, killNum, beKilledNum )


	def tong_updateAbaBuyPoint( self, point ):
		"""
		Define method.
		玩家购买积分的更新函数

		@param point : 玩家购买积分
		@type point : INT16
		"""
		DEBUG_MSG( "--->>>buyPoint:%i." % point )
		ECenter.fireEvent( "EVT_ON_TOGGLE_BUY_RECORD_CHANGE", point )


	def updateAllTongAbaPoint( self, targetTongName, targetPoint, myPoint ):
		"""
		Define method.
		玩家擂台赛所有帮会的积分更新函数

		@param targetTongName : 对方帮会名字
		@type targetTongName : STRING
		@param targetPoint : 对方帮会的积分
		@type targetPoint : INT16
		@param myPoint : 玩家帮会的积分
		@type myPoint : INT16
		"""
		DEBUG_MSG( "--->>>targetTongName:%s, targetPoint:%i, myPoint:%i." % ( targetTongName, targetPoint, myPoint ) )
		GUIFacade.tong_onAbaMarkChanged( targetTongName, targetPoint, myPoint )


	def updateTongAbaPoint( self, tongName, point, tongDBID ):
		"""
		Define method.
		更新对应帮会的积分到客户端

		@param familyName : 帮会名字
		@type familyName : STRING
		@param point : 对方帮会的积分
		@type point : INT16
		@param tongDBID : 要更新的帮会的DBID
		@type tongDBID : DATABASE_ID
		"""
		DEBUG_MSG( "--->>>tongName:%s, Point:%i." % ( tongName, point ) )
		if self.tong_dbID == tongDBID:	# 如果更新自己帮会积分
			GUIFacade.tong_onAbaMarkChanged( tongName, 0, point, True )
		else:
			GUIFacade.tong_onAbaMarkChanged( tongName, point, 0, False )

	def tong_onTongAbaDie( self ):
		"""
		帮会擂台赛死亡
		"""
		# 直接复活
		#self.cell.tong_onInTongAbaRelivePoint()
		GUIFacade.tong_onTongAbaDie()

	def tong_onTongAbaOver( self ):
		"""
		defined method

		帮会擂台副本中的比赛结束时，调用此接口
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_SHOW_ABA_RESULT" )

	#------------------------------------- 帮会俸禄相关 ------------------------------------
	def tong_onDrawSalary(self ):
		"""
		确定领取俸禄
		"""
		self.cell.tong_onDrawTongSalary( )

	def tong_updateMemberContributeInfos( self, memberDBID, totalContribute, currentContribute, thisWeekTotalContribute, lastWeekTotalContribute ):
		"""
		define method
		服务器更新客户端成员帮贡信息：累计帮贡总值、剩余帮贡值、本周获得帮贡、上周获得帮贡
		"""
		if self.tong_memberInfos.has_key( memberDBID ):
			memInfo = self.tong_memberInfos[ memberDBID ]
			memInfo.setTongContributeRelated( totalContribute, currentContribute, thisWeekTotalContribute, lastWeekTotalContribute )

	def tong_receiveSalaryInfo( self, lastWeekTotalContribute, lastWeekSalaryChangeRate,\
							lastWeekReceivedSalary, thisWeekTotalContribute,  thisWeekSalaryChangeRate ):
		"""
		define method
		接收服务器传过来的玩家俸禄相关的信息
		"""
		thisWeekSalaryChange = thisWeekTotalContribute * thisWeekSalaryChangeRate
		if self.tong_holdCity:
			thisWeekSalaryChange *= 2
			
		sararyInfo = [lastWeekTotalContribute, lastWeekSalaryChangeRate, lastWeekReceivedSalary, thisWeekTotalContribute, thisWeekSalaryChangeRate, thisWeekSalaryChange ]
		GUIFacade.tong_receiveSalaryInfo( sararyInfo )

	def tong_receiveTongMoneyInfo( self, lastWeekInfo, thisWeekInfo ):
		"""
		define method
		接受服务器传过来的帮会在资金信息
		"""
		GUIFacade.tong_onInitFund( lastWeekInfo, thisWeekInfo )

	def tong_setSalaryExchangeRate( self, rate ):
		"""
		帮主设置每点帮贡可兑换金钱数
		"""
		minRate = csconst.TONG_SALARY_EXCHANGE_MIN_RATE
		if rate < minRate:									# 设定值小于最小额
			self.statusMessage( csstatus.TONG_SALARY_CHANGE_RATE_LOWER_THAN_MIN, minRate )
			return
		maxRate = csconst.TONG_SALARY_EXCHANGE_RATE[ self.tongLevel ]
		if rate > maxRate:									# 设定值大于该等级帮会允许的最大值
			self.statusMessage( csstatus.TONG_SALARY_CHANGE_RATE_LARGER_THAN_MAX, maxRate )
			return
		self.cell.tong_onSalaryExchangeRate( rate )

	def tong_updateNextWeekExchangeRate( self, rate ):
		"""
		define mothod
		接收服务器传过来的下周帮会俸禄兑换额的信息
		"""
		GUIFacade.tong_onUpdateNextWeekChangeRate( rate )

	def tong_receiveTerritoryNPCData( self, tongDBID, npcID ) :
		"""
		<Define method>
		@param	tongDBID : 帮会的数据库ID
		@type	tongDBID : DATABASE_ID( INT64 )
		@param	npcID : NPC的唯一ID( className )
		@type	npcID : STRING
		接收服务器发送的帮会领地NPC数据
		"""
		npcIDs = self.tong_territoriesNPCs.get( tongDBID, None )
		if npcIDs is None :
			npcIDs = [ npcID ]
			self.tong_territoriesNPCs[tongDBID] = npcIDs
		else :
			npcIDs.append( npcID )
		ECenter.fireEvent( "EVT_ON_ADD_TONG_TERRITORY_NPC", tongDBID, npcID )

	def tong_getTerritoryNPCs( self, tongDBID ) :
		"""
		获取指定帮会领地的NPC数据
		"""
		return self.tong_territoriesNPCs.get( tongDBID, [] )
		
	#------------------------------------- 帮会夺城战复赛（烽火连天）相关 ------------------------------------
	def tong_onFengHuoLianTianOver( self ):
		"""
		帮会城市战复赛（烽火连天）结束
		"""
		ECenter.fireEvent( "EVT_ON_FHLT_SPACE_OVER" )
		
	def tong_onEnterFengHuoLianTianSpace( self, warRemainTime, tongInfos ):
		"""
		进入帮会城市战复赛（烽火连天）
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_FHLT_SPACE", warRemainTime, tongInfos )
		
	def tong_onQueryFHLTTable( self, datas ):
		"""
		define method.
		帮会城市战复赛（烽火连天）赛程查看
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_FHLTAGST_DATAS", datas )
	
	def tongFHLTProtectTime( self, time ):
		"""
		define method.
		帮会城市战复赛（烽火连天）准备时间
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_FHLT_PROTECT_TIME", time )
		
	def tong_onFHLTReport( self, tongDBID,  playerName, kill, dead, isInWar ):
		"""
		define method.
		帮会城市战复赛（烽火连天）更新副本内玩家客户端战果新排名信息
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_FHLTRANK_DATAS", tongDBID,  playerName, kill, dead, isInWar )
		
	def tong_onUpdateFHLTPoint( self, tongDBID, point ):
		"""
		define method.
		帮会城市战复赛（烽火连天）服务器传过来的当前某帮会的战场积分
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_FHLT_POINT", tongDBID, point )
	
	def tong_onLeaveFengHuoLianTianSpace( self ):
		"""
		define method.
		帮会城市战复赛（烽火连天）玩家离开副本
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_FHLT_SPACE" )

	#------------------------------------- 帮会签到相关 ------------------------------------
	def tong_requestSignIn( self ):
		"""
		申请签到
		"""
		self.base.tong_requestSignIn()

	def tong_onSetSignInRecord( self, dailyRecord, totalRecord ):
		"""
		define method
		设置签到次数
		"""
		self.tong_dailySignInRecord = dailyRecord
		self.tong_totalSignInRecord = totalRecord
		ECenter.fireEvent( "EVT_ON_UPDATE_TONG_SINGCOUNT", totalRecord )
		
	#----------------------------------- 帮主任务相关 ---------------------------------------
	def onDartQuestStatusChange( self, newState ):
		"""
		define method
		帮会运镖任务开启状态改变
		"""
		if newState:
			self.statusMessage( csstatus.TONG_OPEN_DART_QUEST )
		self.refurbishAroundQuestStatus()
		
	def onNormalQuestStatusChange( self, openType ):
		"""
		define method
		帮会日常任务开启状态改变
		"""
		if openType != 0:
			self.statusMessage( csstatus.TONG_OPEN_NORMAL_QUEST )
		self.refurbishAroundQuestStatus()
			
	#----------------------------------- 战争结盟 ---------------------------------------
	def tong_openTongBattleLeagueWindow( self, quarterFinalRecord ):
		"""
		define method
		打开战争结盟界面
		"""
		INFO_MSG( "TONG: ( %s, %i ) open tong battle league window, get quarterFinalRecord %s " % ( self.getName(), self.id, quarterFinalRecord ) )
		self.tong_quarterFinalRecord = quarterFinalRecord				# 攻、守城帮会{ 帮会ID: 名次; }
		self.tong_requestBattleLeagues( self.getCamp() )				# 申请已战争结盟帮会

	def tong_requestBattleLeagues( self, camp ):
		"""
		申请已战争结盟帮会
		"""
		self.tongQueryBattleLeagueIndex = 0
		requestTongBattleLeagueList( self.id, camp )

	def tong_receiveBattleLeagues( self, tongDBID, tongName, camp, leagues ):
		"""
		define method
		接收帮会战争同盟信息
		leagues:[ tongDBID, tongDBID ]
		"""
		datas = self.tong_battleLeagues.get( tongDBID )
		if not datas:
			datas = {}
			self.tong_battleLeagues[ tongDBID ] = datas
		datas[ "tongName" ] = tongName
		datas[ "camp" ] = camp
		datas[ "tongDBID" ] = tongDBID
		datas[ "battleLeagues" ] = leagues
	
		INFO_MSG( "TONG:My tong %i, Receive tong battle league info tongDBID %i, tongName %s, camp %i, leagues %s " % ( self.tong_dbID, tongDBID, tongName, camp, leagues ) )

	def tong_receiveBattleLeagueCompleted( self ):
		"""
		define method
		战争结盟数据接收完成
		"""
		self.tongQueryBattleLeagueIndex = -1
		INFO_MSG( "TONG: Finish receive battle leagues!")
		ECenter.fireEvent("EVT_ON_TONG_ALLIANCE_WINDOW_SHOW" )

	def tong_inviteTongBattleLeagues( self, tongDBID, msg ):
		"""
		邀请战争结盟
		"""
		if tongDBID == 0:
			return
		self.cell.tong_inviteTongBattleLeagues( tongDBID, msg )

	def tong_receiveBattleLeagueInvitation( self, inviterTongName, inviterTongDBID, msg ):
		"""
		define method
		收到其他帮会邀请战争同盟
		"""
		GUIFacade.tong_receiveBattleLeagueInvitation( inviterTongName, inviterTongDBID, msg )

	def tong_replyBattleLeagueInvitation( self, inviterTongDBID, response ):
		"""
		回复战争结盟邀请
		"""
		INFO_MSG( "TONG: %s, %i reply inviterTongDBID %i 's battleLeague invitation, response is %i " % ( self.getName(), inviterTongDBID, self.id, response ) )
		self.cell.tong_replyBattleLeagueInvitation( inviterTongDBID, response )

	def tong_setBattleLeague( self, tongDBID, tongName ):
		"""
		define method
		设置战争同盟帮会
		"""
		self.tong_battleLeagues[ tongDBID ] = tongName
		DEBUG_MSG( "TONG:Set battle league tong: %i, %s" % ( tongDBID, tongName ) )
	
	def tong_addBattleLeague( self, tongDBID, tongName ):
		"""
		define method
		添加战争同盟帮会
		"""
		if self.tong_dbID not in self.tong_battleLeagues.keys():
			self.tong_battleLeagues[ self.tong_dbID ] = {}
			self.tong_battleLeagues[ self.tong_dbID ][ "battleLeagues" ] = []
		
		if tongDBID in self.tong_battleLeagues[ self.tong_dbID ][ "battleLeagues" ]:
			return
		else:
			self.tong_battleLeagues[ self.tong_dbID ][ "battleLeagues" ].append( tongDBID )

		self.statusMessage( csstatus.TONG_BATTLE_LEAGUE_SUCCESS, tongName )
		DEBUG_MSG( "TONG:Add battle league tong: %i, %s" % ( tongDBID, tongName ) )

	def tong_battleLeagueDispose( self, battleLeagueDBID ):
		"""
		解除某帮会战争结盟关系
		"""
		self.cell.tong_battleLeagueDispose( battleLeagueDBID )

	def tong_delBattleLeague( self, tongDBID ):
		"""
		define method
		解除了某战争同盟帮会
		"""
		DEBUG_MSG( "TONG:Del battle league tong: %i" % ( tongDBID ) )
		if self.tong_dbID not in self.tong_battleLeagues.keys():
			ERROR_MSG( "TONG: Self tongDBID not in my tong_battleLeagues %s" % ( self.tong_dbID, self.battleLeagues ) )
			return

		if tongDBID in self.tong_battleLeagues[ self.tong_dbID ][ "battleLeagues" ]:
			self.tong_battleLeagues[ self.tong_dbID ][ "battleLeagues" ].remove( tongDBID )

		
	def getCityWarTongBelong( self, tongDBID ):
		"""
		获取帮会夺城战决赛的帮会归属，攻城还是守城方
		"""
		belong = 0
		if self.tongInfos.has_key("tongInfos"):
			for key, info in self.tongInfos["tongInfos"].iteritems():
				if tongDBID in info.keys():
					if key == "right":
						belong = csdefine.CITY_WAR_FINAL_FACTION_ATTACK
					else:
						belong = csdefine.CITY_WAR_FINAL_FACTION_DEFEND
		return belong

	def checkCityWarTongBelong( self, ownTongDBID, targetTongDBID ):
		""" 
		检测夺城战决赛中帮会归属 
		"""
		if self.tongInfos.has_key( "tongInfos" ):
			for key, info in self.tongInfos[ "tongInfos"].iteritems():
				if ownTongDBID in info.keys():
					if targetTongDBID in info:
						return True
		return False

def requestDatas( playerEntityID ):
	"""
	每隔一段时间向服务器请求一次帮会相关数据
	"""
	p = BigWorld.player()
	if not p or p.id != playerEntityID or p.tong_isRequestDataEnd:
		return

	p.cell.tong_requestDatas()
	BigWorld.callback( 0.3, Functor( requestDatas, playerEntityID ) )

def requestTongList( playerEntityID, camp ):
	"""
	每隔一段时间向服务器请求一次帮会列表相关数据
	"""
	p = BigWorld.player()
	if not p or p.id != playerEntityID or p.tongQueryTongListIndex == -1:
		return

	p.cell.tong_requestTongList( p.tongQueryTongListIndex, camp )
	p.tongQueryTongListIndex += 5
	BigWorld.callback( 0.3, Functor( requestTongList, playerEntityID, camp ) )

def requestTongBattleLeagueList( playerEntityID, camp ):
	"""
	向服务器请求战争结盟数据（包括帮会列表信息）
	"""
	p = BigWorld.player()
	if not p or p.id != playerEntityID or p.tongQueryBattleLeagueIndex == -1:
		return
	
	p.cell.tong_requestBattleLeagues( p.tongQueryBattleLeagueIndex, camp )
	p.tongQueryBattleLeagueIndex += 5
	BigWorld.callback( 0.3, Functor( requestTongBattleLeagueList, playerEntityID, camp ) )


#
# $Log: not supported by cvs2svn $
# Revision 1.23  2008/08/25 02:50:36  qilan
# 添加邀请玩家加入帮会的系统信息
#
# Revision 1.22  2008/08/21 10:15:02  qilan
# 添加邀请玩家加入帮会的系统信息
#
# Revision 1.21  2008/08/12 08:51:36  kebiao
# 添加帮主集结令功能
#
# Revision 1.20  2008/07/25 03:45:32  kebiao
# 增加帮会解散提示信息
#
# Revision 1.19  2008/07/24 04:08:02  kebiao
# 去掉一些调试信息
#
# Revision 1.18  2008/07/24 03:21:24  kebiao
# 增加临时调试信息供其他同事查看
#
# Revision 1.17  2008/07/24 02:03:42  kebiao
# 去掉一些调试信息
#
# Revision 1.16  2008/07/22 01:59:43  huangdong
# 完善帮派聊天系统
#
# Revision 1.15  2008/07/02 01:42:51  kebiao
# 修正一处提示错误
#
# Revision 1.14  2008/07/02 01:34:08  kebiao
# 增加职位名称变量
#
# Revision 1.13  2008/07/01 11:19:01  fangpengjun
# 添加创建帮会接口
#
# Revision 1.12  2008/07/01 10:45:44  fangpengjun
# 修正了接口tong_onMemberFamilyGradeChanged的一个参数错误
#
# Revision 1.11  2008/06/30 10:25:06  fangpengjun
# 修改部分消息
#
# Revision 1.10  2008/06/30 04:15:33  kebiao
# 增加帮会职位名称编辑
#
# Revision 1.9  2008/06/29 08:57:17  fangpengjun
# 添加界面所需信息
#
# Revision 1.8  2008/06/27 07:11:48  kebiao
# 增加了帮会和家族的异步数据传输机制
#
# Revision 1.7  2008/06/23 08:13:23  kebiao
# no message
#
# Revision 1.6  2008/06/23 02:56:05  kebiao
# 修改一处提示错误
#
# Revision 1.5  2008/06/21 04:15:58  kebiao
# no message
#
# Revision 1.4  2008/06/21 03:42:00  kebiao
# 加入帮会贡献度
#
# Revision 1.3  2008/06/16 09:15:00  kebiao
# base 上部分暴露接口转移到cell 改变调用方式
#
# Revision 1.2  2008/06/14 09:15:27  kebiao
# 新增帮会功能
#
# Revision 1.1  2008/06/09 09:23:27  kebiao
# 加入帮会相关
#
#