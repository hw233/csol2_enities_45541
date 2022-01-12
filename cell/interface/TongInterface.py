# -*- coding: gb18030 -*-
#
# $Id: TongInterface.py,v 1.11 2008-08-25 09:30:45 kebiao Exp $
import math
import sys
import time
import random
import BigWorld

import csstatus
import cschannel_msgs
import ShareTexts as ST

import Language
import csdefine
import csconst
import ItemTypeEnum
import Function
from bwdebug import *

import Const
import items
g_items = items.instance()
from Love3 import g_rewards
from Love3 import g_skills, g_tongSkills
from Resource.SkillLoader import g_skills
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.TongFeteDataLoader import TongFeteDataLoader
from ChatProfanity import chatProfanity
from Resource.TongRobWarRewardLoader import TongRobWarRewardLoader		# 奖励，奖励内容为表格配置

from TongCityWarFightInfos import MasterChiefData

g_tongRobWarRewards = TongRobWarRewardLoader.instance()
g_feteDataLoader = TongFeteDataLoader.instance()

FETE_MATERIAL_LIST = [ 80101003, 80101009, 80101015, 80101021, 80101027 ]	# 2级打造材料物品id列表

TONG_GRADE_MEMBER_MAX_MAP = { 0:0, 1:30, 2:60, 3:90, 4:120, 5:150 }

CITY_WAR_CHIEF_REWARD_BOX_FAIL	= 60101267 # 帮会城市战帮主额外奖励，失败宝箱
CITY_WAR_CHIEF_REWARD_BOX_WIN	= 60101268 # 帮会城市战帮主额外奖励，胜利宝箱
CITY_WAR_CHIEF_REWARD_ITEM		= 50101101 # 帮会城市战帮主额外奖励，布雨青龙印记

OLD_GRADE_MAPPING = { 0x00000001:1, 0x00000010: 2, 0x00000040:3, 0x00000080: 4 ,}

class TongInterface:
	def __init__( self ):
		pass

	def getTongManager( self ):
		return BigWorld.globalData["TongManager"]

	def tong_reset( self ):
		self.tong_dbID = 0
		self.tong_grade = 0
		self.tong_level = 0
		self.tongName = ""
		self.tong_holdCity = ""
		self.tong_onlineMemberMailboxs.clear()
		self.tong_clearTongSkills()
		self.onDartQuestStatusChange( False )
		self.onNormalQuestStatusChange( 0 )

	def tong_getTongEntity( self, tongDBID ):
		"""
		获取帮会entity
		"""
		k = "tong.%i" % tongDBID
		try:
			tongMailbox = BigWorld.globalData[ k ]
		except KeyError:
			ERROR_MSG( "tong %s not found." % k )
			return None
		return tongMailbox

	def tong_getSelfTongEntity( self ):
		"""
		获得自己帮会的mailbox
		"""
		return self.tong_getTongEntity( self.tong_dbID )

	def tong_getMemberCountMax( self ):
		"""
		获得自己帮会的容纳人数上限
		"""
		return TONG_GRADE_MEMBER_MAX_MAP[self.tong_level]

	def isJoinTong(self):
		"""
		判断玩家是否加入帮会
		tong_grade 不为0 表示玩家一定加入了帮会
		"""
		return self.tong_dbID > 0

	def tong_onSetContribute( self, contribute ):
		"""
		define method.
		设置帮会贡献度
		"""
		# 这里由tongEntity设置  不可手动调用此接口
		self.tong_contribute = contribute

	def tong_payContribute( self, contribute ):
		"""
		支付帮会贡献度
		"""
		if self.tong_contribute >= contribute:
			self.tong_contribute -= contribute
			self.statusMessage( csstatus.ACCOUNT_STATE_PAY_TONGCONTRIBUTE, int(contribute) )
			tongMailbox = self.tong_getSelfTongEntity()
			if tongMailbox:
				tongMailbox.onMemberContributeChanged( self.databaseID, self.tong_contribute )
			else:
				ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )
			return True
		return False

	def tong_addContribute( self, contribute ):
		"""
		define method.
		添加帮会贡献度
		"""
		#--------- 以下为防沉迷系统的判断 --------#
		gameYield = self.wallow_getLucreRate()
		if contribute >=0:
			contribute = contribute * gameYield
		#--------- 以上为防沉迷系统的判断 --------#
		self.tong_contribute += contribute
		self.statusMessage( csstatus.ACCOUNT_STATE_GAIN_TONGCONTRIBUTE, int(contribute) )
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onMemberContributeChanged( self.databaseID, self.tong_contribute )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	def tong_addMoney( self, money, reason = csdefine.TONG_CHANGE_MONEY_NORMAL  ):
		"""
		添加帮会资金
		"""
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.addMoney( money, reason )

	def tong_onSetTongName( self, tongName ):
		"""
		define method.
		设置帮会名称
		"""
		self.tongName = tongName

	def optionReduceRD_tong( self ):
		"""
		帮会等级改变带来的玩家御敌增加、删除
		"""
		reduceRate = self.queryTemp( "ADD_REDUCE_ROEL_D_TONG", 0.0 )
		if self.tong_dbID == 0:#退出帮会了
			if reduceRate > 0.0 : #有帮会带来的御敌增加
				self.reduce_role_damage_extra -= reduceRate
				self.calcReduceRoleDamage()
				self.setTemp( "ADD_REDUCE_ROEL_D_TONG", 0.0 )
		else: #在帮会中
			if self.tong_level in Const.TONG_ADD_REDUCE_ROLE_DAMAGE: #帮会等级可以带来御敌属性增加
				rm = Const.TONG_ADD_REDUCE_ROLE_DAMAGE[self.tong_level]
				if reduceRate <= 0.0 : #还没有帮会带来的御敌增加
					self.reduce_role_damage_extra += rm
					self.calcReduceRoleDamage()
					self.setTemp( "ADD_REDUCE_ROEL_D_TONG", rm )
				if reduceRate > 0.0 and reduceRate != rm: #已经获得了，但是现在帮会升级了
					self.reduce_role_damage_extra -= reduceRate
					self.reduce_role_damage_extra += rm
					self.calcReduceRoleDamage()
					self.setTemp( "ADD_REDUCE_ROEL_D_TONG", rm )
			else: #帮会等级不能带来御敌属性增加
				if reduceRate > 0.0 : #有帮会带来的御敌增加
					self.reduce_role_damage_extra -= reduceRate
					self.calcReduceRoleDamage()
					self.setTemp( "ADD_REDUCE_ROEL_D_TONG", 0.0 )
		
	
	def tong_onSetTongLevel( self, level ):
		"""
		define method.
		设置帮会级别
		"""
		self.tong_level = level
		self.optionReduceRD_tong()
		self.client.tong_onSetTongLevel( level )

	def tong_onChanged( self ):
		"""
		virtual method.
		玩家的帮会改变了  加入或者退出了
		"""
		self.optionReduceRD_tong()
		# 如果帮会解散或者退出帮会了
		if self.tong_dbID == 0:
			spaceType = self.getCurrentSpaceType()
			# 玩家还在城战副本则将其传出
			if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
				self.tong_onCityWarOver()
			# 玩家身上有跑商任务则删除任务
			merchantQuest = self.getMerchantQuest()
			if merchantQuest is None: return
			self.questRemove( merchantQuest.getID(), True )  # 算作主动放弃任务

	def tong_setGrade( self, grade ):
		"""
		define method.
		设置该player grade
		"""
		if not self.isJoinTong():
			return
		if self.tong_grade != grade:
			self.tong_grade = grade
		self.writeToDB()
		tongBase = self.tong_getSelfTongEntity()
		if tongBase:
			tongBase.changeGradeSuccess( self.databaseID )

	def tong_onLoginCB( self, tongBaseMailbox ):
		"""
		define method.
		登陆完毕
		"""
		DEBUG_MSG( "player %s:%i login tong dbid=%i id =%i " % ( self.playerName, self.id, self.tong_dbID, tongBaseMailbox.id ) )

	#---------------------------------------------------------------------------------------------------------
	def createTong( self, selfEntityID, tongName, reason ):
		"""
		Exposed method.
		创建一个帮会
		"""
		if selfEntityID != self.id:
			return

		if self.isJoinTong():
			self.statusMessage( csstatus.TONG_CREATE_HAS_A_TONG )
			return
		if self.level < csdefine.TONG_CREATE_LEVEL:
			self.statusMessage( csstatus.TONG_CREATE_LEVEL_INVALID, csdefine.TONG_CREATE_LEVEL )
			return
		if self.money < csdefine.TONG_CREATE_MONEY:
			self.statusMessage( csstatus.TONG_CREATE_MONEY_INVALID )
			return

		# 帮会名称合法性检测
		if len( tongName ) > 14:
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if tongName == "":
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if not chatProfanity.isPureString( tongName ):
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if chatProfanity.searchNameProfanity( tongName ) is not None:
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if self.queryTemp( "createTongData", None ):
			HACK_MSG( "tong is creating..player( %s ) Duplicate request.." % self.getName() )
			return
		self.setTemp( "createTongData", {"tongName":tongName} )
		self.getTongManager().createTong( tongName, self.base, self.getName(), self.databaseID, self.getLevel(), self.raceclass, reason )

	def tong_checkCreateFail( self, statusID ):
		"""
		请求创建帮会，帮会管理器检查的返回结果
		"""
		self.popTemp( "createTongData" )
		self.statusMessage( statusID )

	def tong_createSuccess( self, tongDBID, tongBaseMailbox ):
		"""
		define method.
		帮会创建成功的回调
		"""
		self.popTemp( "createTongData" )
		if not self.payMoney( csdefine.TONG_CREATE_MONEY, csdefine.CHANGE_MONEY_CREATETONG ):
			self.statusMessage( csstatus.TONG_CREATE_PAYMONEY_FAILED )
			return
		self.tong_dbID = tongDBID
		self.tong_grade = csdefine.TONG_DUTY_CHIEF
		self.tong_contribute = csconst.JOIN_TONG_CHIEF_INIT_CONTRIBUTE
		tongBaseMailbox.createSuccess()
		self.tong_onChanged()
		self.writeToDB()

	#---------------------------------------------------------------------------------------------------------
	def getTongOnlineMember( self ):
		"""
		获取帮会在线成员
		"""
		return self.tong_onlineMemberMailboxs

	def tong_addMemberOL( self, baseEntityDBID, baseEntity ):
		"""
		define method.
		添加在线成员
		"""
		DEBUG_MSG( "addMemberOL:%i" % baseEntityDBID )
		self.tong_onlineMemberMailboxs[ baseEntityDBID ] = baseEntity

	def tong_onMemberRemoveOL( self, baseEntityDBID ):
		"""
		define method.
		有成员下线了
		"""
		DEBUG_MSG( "MemberRemoveOL:%i" % baseEntityDBID )
		self.tong_onlineMemberMailboxs.pop( baseEntityDBID )

	#---------------------------------------------------------------------------------------------------------

	def tong_requestJoin( self, selfEntityID, targetEntityID ):
		"""
		Exposed method.
		邀请某人加入tong
		"""
		DEBUG_MSG( "player %i request player %i to join to tong %i " % ( selfEntityID, targetEntityID, self.tong_dbID ) )
		if self.id != selfEntityID or selfEntityID == targetEntityID:
			return
		if not self.isJoinTong():
			self.statusMessage( csstatus.TONG_NO_HAS_TONG )
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if not tongMailbox:
			ERROR_MSG( "player( %s ) cant find tong base mailbox." % self.getName() )
			return
		try:
			targetEntity = BigWorld.entities[ targetEntityID ]
		except KeyError:
			self.statusMessage( csstatus.TONG_TARGET_INVALID )
			return
		if not targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			ERROR_MSG( "player( %s ) add target( %s ) is not role entity." % ( self.getName(), targetEntity.getName() ) )
			return
		if targetEntity.isJoinTong():
			self.statusMessage( csstatus.TONG_ALREADY_HAS_TONG )
			return
			
		if self.getCamp() != targetEntity.getCamp():
			self.statusMessage( csstatus.TONG_CAMP_DIFFERENT )
			return 
			
		if targetEntity.level < csconst.TONG_JOIN_MIN_LEVEL:
			self.statusMessage( csstatus.TONG_CANT_JOIN_LEVEL_LACK, csconst.TONG_JOIN_MIN_LEVEL  )
			return
		tongMailbox.onRequestJoin( self.databaseID, targetEntity.base, targetEntity.databaseID )

	def tong_answerRequestJoin( self, selfEntityID, agree, tongDBID ):
		"""
		Exposed method.
		被邀请后 做出回答
		@param agree: bool, true = 接受
		"""
		DEBUG_MSG( "player %i answer to tong %i " % ( selfEntityID, tongDBID ) )
		if self.id != selfEntityID:
			DEBUG_MSG( "player %i has a tong! dbid = %i" % ( selfEntityID, self.tong_dbID ) )
			return
		if self.isJoinTong():	# 如果已经加入了帮会，当作玩家拒绝邀请
			agree = False
		tongMailbox = self.tong_getTongEntity( tongDBID )
		if tongMailbox:
			tongMailbox.onAnswerRequestJoin( self.databaseID, agree, self.getName() )
		else:
			ERROR_MSG( "not found tongMailbox %i." % tongDBID )

	def tong_onJoin( self, tongDBID, grade, tongContribute, tongBaseMailbox ):
		"""
		Define method.
		加帮会成功，设置帮会数据

		@param tongDBID : 帮会的dbid
		@type tongDBID : DATABASE_ID
		@param grade : 帮会职位
		@type grade : UINT8
		@param tongContribute : 帮会的初始贡献
		@type tongContribute : UINT32
		@param tongBaseMailbox : 帮会的base mailbox
		@type tongBaseMailbox : MAILBOX
		"""
		if self.isJoinTong():			# 有可能先加入了其他帮会
			return
		self.tong_dbID = tongDBID
		self.tong_grade = grade
		self.tong_contribute = tongContribute
		self.base.tong_onJoin( tongDBID, grade, tongBaseMailbox )
		tongBaseMailbox.onJoin( self.databaseID, self.getName(), self.getLevel(), self.raceclass, self.base, grade, tongContribute )
		self.tong_onChanged()


	#---------------------------------------------------------------------------------------------------------

	def tong_abdication( self, selfEntityID, memberDBID ):
		"""
		Exposed method.
		帮主让位
		"""
		if selfEntityID != self.id:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onAbdication( self.databaseID, memberDBID )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	def tong_setAffiche( self, selfEntityID, affiche ):
		"""
		Exposed method.
		设置服务器帮会公告
		"""
		if selfEntityID != self.id:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.setAffiche( self.databaseID, affiche )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )


	#---------------------------------------------------------------------------------------------------------

	def onDismissTong( self, selfEntityID ):
		"""
		Expose method
		解散帮会
		"""
		if selfEntityID != self.id:
			return

		if not self.checkDutyRights( csdefine.TONG_RIGHT_DISMISS_TONG ):
			self.statusMessage( csstatus.TONG_DISMISS_GRADE )
			return

		if BigWorld.globalData.has_key("AS_ProtectTong"):
			self.statusMessage( csstatus.TONG_PROTECT_TONG_DISMISS )
			return

		tongEntity = self.tong_getSelfTongEntity()
		if tongEntity:
			tongEntity.onDismissTong( self.databaseID, csdefine.TONG_DELETE_REASON_NOMAL )

	def tong_quit( self, selfEntityID ):
		"""
		Exposed method.
		玩家要求退出帮会
		"""
		if selfEntityID != self.id:
			return
		# 帮主只能让位退出
		if self.isTongChief():
			self.statusMessage( csstatus.TONG_CHIEF_QUIT )
			return
			
		tongEntity = self.tong_getSelfTongEntity()
		if tongEntity:
			tongEntity.memberLeave( self.databaseID )

	def tong_kickMember( self, selfEntityID, targetDBID ):
		"""
		Exposed method.
		玩家要求将某人踢出帮会
		"""
		if selfEntityID != self.id:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.kickMember( self.databaseID, targetDBID )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	#---------------------------------------------------------------------------------------------------------

	def tong_setMemberGrade( self, selfEntityID, targetDBID, grade ):
		"""
		Expose method.
		user设置target权限
		@param targetDBID : 被设置者DBID
		@param grade  	  : 最终要设置的权限
		"""
		if selfEntityID != self.id:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.setMemberGrade( self.databaseID, targetDBID, grade )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	def tong_setMemberScholium( self, selfEntityID, targetDBID, scholium ):
		"""
		Expose method.
		user设置target权限
		@param targetDBID : 被设置者DBID
		@param scholium	  : 最终要设置的批注信息
		"""
		if selfEntityID != self.id:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.setMemberScholium( self.databaseID, targetDBID, scholium )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	#---------------------------------------------------------------------------------------------------------

	def tong_requestTongLeague( self, selfEntityID, requestTongName ):
		"""
		Expose method.
		邀请帮会同盟
		@param requestTongName	:要邀请的目标帮会名称
		"""
		DEBUG_MSG( "%i request tong %s to league." % ( selfEntityID, requestTongName ) )
		if selfEntityID != self.id:
			return
		if self.checkDutyRights( csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			self.getTongManager().onRequestTongLeague( self.databaseID, self.tong_dbID, requestTongName )
		else:
			self.statusMessage( csstatus.TONG_GRADE_INVALID )

	def tong_answerRequestTongLeague( self, selfEntityID, agree, requestByTongDBID ):
		"""
		Expose method.
		邀请帮会同盟
		"""
		DEBUG_MSG( "%i answer tong %i to league." % ( selfEntityID, requestByTongDBID ) )
		if selfEntityID != self.id:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onAnswerRequestTongLeague( self.base, requestByTongDBID, agree )

	def tong_leagueDispose( self, selfEntityID, leagueTongDBID ):
		"""
		Expose method.
		解除某帮会同盟关系
		"""
		DEBUG_MSG( "%i dispose to tong %i of league." % ( self.tong_dbID, leagueTongDBID ) )
		if selfEntityID != self.id:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.leagueDispose( self.databaseID, leagueTongDBID )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	def tong_requestDatas( self, selfEntityID ):
		"""
		Expose method.
		客户端向服务器请求获得帮会的数据
		"""
		if selfEntityID != self.id or not self.isJoinTong():
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.requestDelayDatas( self.databaseID, self.base )
		else:
			ERROR_MSG( "%i not found tongMailbox %i." % ( self.id, self.tong_dbID ) )
			self.client.tong_onRequestDatasCallBack()

	def tong_setDutyName( self, selfEntityID, duty, newName ):
		"""
		Expose method.
		设置帮会职位的名称
		"""
		if selfEntityID != self.id:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.setDutyName( self.databaseID, duty, newName )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	def tong_onAnswerConjure( self, selfEntityID ):
		"""
		Exposed method.
		回应队长集结令
		"""
		if self.id != selfEntityID:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			if self.getState() == csdefine.ENTITY_STATE_CHANGING:
				self.changeState( csdefine.ENTITY_STATE_FREE )
			if self.hasMerchantItem():
				self.statusMessage( csstatus.MERCHANT_ITEM_CANT_FLY )
				return
			# 如果有法术禁咒buff
			if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
				return
			tongMailbox.onAnswer_conjure( self.databaseID )

	#---------------------------------------------------------------------------------------------------------
	def tong_gotoCityWar( self, spaceName ):
		"""
		define method.
		战场管理系统选择了进入战场的战场级别进入战场，用于城战以及帮会夺城战复赛（烽火连天）进入
		@param warlevel:战争进行到级别 1 or 2
		"""
		self.gotoSpace( spaceName, ( 0, 0, 0 ), ( 0, 0, 0 ) )
	
	def tong_leaveCityWar( self ):
		# define method
		# 离开帮会城市战
		
		enterInfos = self.query( "cityWarEnterInfos" )
		if enterInfos:
			self.gotoSpace( enterInfos[ 0 ], enterInfos[ 1 ], enterInfos[ 2 ] )
			self.remove( "cityWarEnterInfos" )
		else:
			self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )

	def tong_onSetHoldCity( self, city, isInit ):
		"""
		define mothod.
		设置帮会控制的城市
		@param city: spaceName
		"""
		self.tong_holdCity = city
		if city and not isInit:
			self.tong_onCityWarMasterOnlineReward()

	def tong_onCityWarOver( self ):
		"""
		define method.
		城市战争结束了， 如果还在副本则传送出来
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# 改变状态,满血满魔
				self.reviveActivity()
			
			self.tong_leaveCityWar()
		
		self.client.tong_onCityWarOver()

	def tong_onCityWarRelive( self, selfEntityID, reliveType ):
		"""
		Exposed method.
		在城战战场死亡 复活
		@param reliveType: 复活方式 0：原地复活， 非0：回城复活
		"""
		if self.id != selfEntityID:
			return

		if reliveType == 0:
			if not self.findItemsByIDFromNKCK( 110103001 ) :
				return
			else:
				self.useItemRevive( selfEntityID )
		else:
			self.getCurrentSpaceBase().cell.onRoleRelive( self.base, self.tong_dbID )
	
	def tong_onCityWarReliveCallback( self, spaceName, position, direction ):
		# define method
		# 城战复活以及帮会夺城战复赛（烽火连天）复活
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #刷新速度
		self.gotoSpace( spaceName, position, direction )

	def tong_leaveCityWarSpace( self, selfEntityID ):
		"""
		Exposed method.
		玩家主动离开战场 使用此接口
		"""
		if self.id != selfEntityID:
			return
		self.tong_leaveCityWar()

	def tong_onCityWarOverReward( self ):
		"""
		define method.
		城战结束后给予奖励
		702×（25+5×角色等级^1.2）, 帮会贡献度 50
		"""
		exp = 702 * ( 25 + 5 * pow( self.level, 1.2 ) )
		self.addExp( exp, csdefine.CHANGE_EXP_CITYWAR_OVER )
		#奖励帮会贡献度
		self.tong_addContribute( 50 )
	
	def tong_onCityWarMasterOnlineReward( self ):
		# 城主帮会成员奖励
		exp = 702 * ( 25 + 5 * pow( self.level, 1.2 ) ) 	# 702×（25+5×角色等级^1.2）, 帮会贡献度 50
		self.addExp( exp, csdefine.CHANGE_EXP_CITYWAR_MASTER )
		#奖励帮会贡献度
		self.tong_addContribute( 50 )
	
	def tong_cityWarSetRewardChampion( self, rewardTime ):
		# define method
		# 请求领取本周城战奖励
		self.set( "tongCityWarChampion", ( rewardTime, False ) )
	
	def tong_cityWarGetChiefReward( self, isCityMaster, winNum ):
		# define method
		# 领取帮主额外奖励
		if not self.isTongChief():
			self.statusMessage( csstatus.TONG_CITY_WAR_CHIEF_REWARD_GRADE )
			return
		
		items = []
		if isCityMaster:
			items.append( self.createDynamicItem( CITY_WAR_CHIEF_REWARD_BOX_WIN ) )
		else:
			items.append( self.createDynamicItem( CITY_WAR_CHIEF_REWARD_BOX_FAIL ) )
		
		if winNum:
			items.append( g_items.createDynamicItem( CITY_WAR_CHIEF_REWARD_ITEM, winNum ) )
			
		if  self.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包空间不够
			self.statusMessage( csstatus.CIB_MSG_CANT_OPERATER_FULL )
			return
		
		for item in items:
			self.addItem( item, csdefine.REWARD_TONG_TONG_CITY_WAR )
		
		self.getTongManager().onGetCityTongChiefRewardSuccess( self.tong_dbID )

	def tong_requestQueryCityTongMasters( self, selfEntityID, cityName ):
		"""
		Exposed method.
		请求查看城市英雄榜
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().onQueryCityTong( cityName, self.base )

	def tong_onQueryCityWarTable( self, selfEntityID, cityName ):
		"""
		Exposed method.
		请求查看城市赛程表 或者 赛况表
		"""
		if self.id != selfEntityID:
			return
		BigWorld.globalData[ "TongManager" ].onQeryCityWarVersus( cityName, self.base )

	def tong_confirmContest( self, selfEntityID, tonglevel, repMoney ):
		"""
		Exposed method.
		确认参加帮会城市战
		"""
		if self.id != selfEntityID:
			return
		BigWorld.globalData[ "TongManager" ].requestContestCityWar( self.base, self.tong_dbID, self.databaseID, tonglevel, repMoney, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )

	def tong_requestSetCityRevenueRate( self, selfEntityID, rate ):
		"""
		Exposed method.
		玩家设置城市消费税率
		"""
		if self.id != selfEntityID:
			return
		spaceName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if self.tong_holdCity == spaceName:
			if self.isTongChief():
				BigWorld.globalData[ "TongManager" ].onSetCityRevenueRate(self.base, self.playerName, self.tong_dbID, spaceName, rate)

	def tong_onSetCityRevenueRateSuccessfully( self, cityName, rate ):
		"""
		define method.
		玩家设置城市消费税率成功
		"""
		revenueRate = BigWorld.globalData[ cityName + ".revenueRate" ]
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CITY_REVENUE, revenueRate )
	
	def tong_queryTongChiefInfos( self ):
		# define method
		# 获取帮主信息
		obj = MasterChiefData()
		obj[ "uname" ] = self.playerName
		obj[ "tongName" ] = self.tongName
		obj[ "raceclass" ] = self.raceclass
		obj[ "hairNumber" ] = self.hairNumber
		obj[ "faceNumber" ] = self.faceNumber
		obj[ "bodyFDict" ] = self.bodyFDict
		obj[ "volaFDict" ] = self.volaFDict
		obj[ "breechFDict" ] = self.breechFDict
		obj[ "feetFDict" ] = self.feetFDict
		obj[ "lefthandFDict" ] = self.lefthandFDict
		obj[ "righthandFDict" ] = self.righthandFDict
		obj[ "talismanNum" ] = self.talismanNum
		obj[ "fashionNum" ] = self.fashionNum
		obj[ "adornNum" ] = self.adornNum
		BigWorld.globalData[ "TongManager" ].cityWarOnQueryMasterInfo( self.tong_dbID, obj )
	
	def tong_onRequestCityTongRevenue( self, exposed ):
		# Exposed method
		# 确认领取帮会税收
		self.tong_getSelfTongEntity().onGetCityTongRevenue( self.databaseID )
		
	#----------------------------------帮会建筑--------------------------------------------------------------

	def tong_onSelectShouShou( self, selfEntityID, shenshouType ):
		"""
		Exposed method.
		玩家申请选择神兽
		"""
		if self.id != selfEntityID:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onSelectShouShou( self.base, self.tong_grade, shenshouType )
	
	#---------------------------------掠夺战-------------------------------------------------------------------
	def tong_onAnswerRobWar( self, selfEntityID, targetTongName ):
		"""
		Exposed method.
		玩家申请提交要掠夺的帮会
		"""
		if self.id != selfEntityID:
			return
		if len( targetTongName ) > 0 and self.isJoinTong():
			self.getTongManager().onAnswerRobWar( self.base, self.databaseID, self.tong_dbID, targetTongName )

	def tong_findRequestRobWar( self, selfEntityID, targetTongName ):
		"""
		Exposed method.
		玩家查找这个要掠夺的帮会
		"""
		if self.id != selfEntityID:
			return
		if len( targetTongName ) > 0 and self.isJoinTong():
			self.getTongManager().findRequestRobWar( self.base, targetTongName )

	def tong_isInRobWar( self, tongDBID ):
		"""
		是否正在掠夺战中的敌对帮会
		"""
		return BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ) and self.robWarTargetTong == tongDBID

	def tong_setRobWarTargetTong( self, tongDBID ):
		"""
		define method.
		设置帮会掠夺战对象
		"""
		self.robWarTargetTong = tongDBID
		self.client.tong_setRobWarTargetTong( tongDBID )

	def tong_onRobWarOver( self, isWin ):
		"""
		define method.
		掠夺战结束了
		"""
		#增加每人每天只能获取一次掠夺战奖励的限制 by 陈晓鸣 2010.10.11
		lastTakeTime = self.queryRoleRecord( "rewardTongRobWarTime" )
		lt = time.localtime()
		curT = str( lt[1]) + "+" + str(lt[2] )
		if lastTakeTime == curT:
			self.statusMessage( csstatus.TONG_ROB_WAR_REWARD_FORBID )
			return

		exp = int( g_tongRobWarRewards.get( self.level )['exp'] )
		rate = 1.3
		if not isWin:
			rate = 0.1
		else:
			self.tong_addContribute( 50 )
			self.addHonor( 20, csdefine.HONOR_CHANGE_REASON_ZHENG_DUO )

		exp *= rate
		self.addExp( exp, csdefine.CHANGE_EXP_TONG_ROB )
		self.setRoleRecord( "rewardTongRobWarTime", curT ) #设置领取奖励时间 by 陈晓鸣 2010.10.11

	def tong_rewardRobWar( self, order ):
		"""
		define method.
		掠夺战奖励领取
		"""
		awarder = g_rewards.fetch( csconst.RCG_TONG_ROB_WARS.get(order, 1), self )
		if awarder is None or len( awarder.items ) <= 0:
			self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		if self.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.TONG_ROB_WAR_REWARD_ERROR )
			return
		awarder.award( self, csdefine.ADD_ITEM_ROB_WAR_ITEM )
		BigWorld.globalData["TongManager"].onRewardRobWarPlayerCB( self.tong_dbID, True )

	#----------------------------------------------帮会技能----------------------------------------------------
	
	def tong_updateTongSkills( self, yjy_level ):
		"""
		define method
		更新帮会技能
		"""
		canActiveSkills = self.getCanActiveSkills( yjy_level )
		for skillID in canActiveSkills:
			self.updateTongSkill( skillID )

	def updateTongSkill( self, skillID ):
		"""
		更新单个帮会技能，如果已经存在则更新，反之则添加
		"""
		skillMap = self.getTongSkillsMap( skillID )
		iterSet =  set( skillMap ) & set( self.attrSkillBox )
		
		if len( iterSet ) > 1:		# 正常情况下，某个技能的可升级技能表与角色身上技能的交集最多有一个值
			ERROR_MSG( " %s: There has some error in updating tong skill, role has %s skills existed!" % ( self.getNameAndID(), iterSet ) )
			return
		
		if len( iterSet ) == 0:		# 没有交集，则添加
			self.addSkill( skillID )
			return
		
		oldSkill = iterSet.pop()
		if g_skills[ oldSkill ].getLevel() >= g_skills[ skillID ].getLevel():
			DEBUG_MSG( "%s has learned skill %s , to learn skill is %s" % ( self.getNameAndID(), oldSkill, skillID ) )
			return
		
		self.updateSkill( oldSkill, skillID )

	def getTongSkillsMap( self, skillID ):
		"""
		获取某技能对应的所有等级技能
		"""
		skillsMap = []
		skillDatas = g_tongSkills.getDatas().get( skillID / 1000 * 1000 , None )
		if skillDatas is not None:
			for level,item in skillDatas.iteritems():
				skillsMap.append( item[ "id" ] )
		return skillsMap

	def getCanActiveSkills( self, yjy_level ):
		"""
		获取帮会可以激活的技能
		条件：技能对应的研究院等级不能大于当前研究院等级
		"""
		skills = []
		skillDatas = g_tongSkills.getDatas( )
		for skillID, skillItem in skillDatas.iteritems():
			for level, item in skillItem.iteritems():
				if item[ "repBuildingLevel"] > yjy_level:
					level = level - 1 
					break
			newSkillID = skillItem[ level ][ "id" ]
			skills.append( newSkillID )
		return skills

	def tong_clearTongSkills( self ):
		"""
		define method
		清除玩家身上的帮会技能，离开帮会时调用
		"""
		tongSkillMap = []		# 所有帮会技能集合
		for skillID in g_tongSkills.getDatas().keys():
			skillMap = self.getTongSkillsMap( skillID )
			tongSkillMap.extend( skillMap )
		
		learnedTongSkills = set( tongSkillMap ) & set( self.attrSkillBox )
		if len( learnedTongSkills ) == 0:
			return
		for skillID in learnedTongSkills:
			self.removeSkill( skillID )
		self.statusMessage( csstatus.TONG_SKILL_CLEARED )

	#-----------------------------------帮会活动---------------------------------------------------------------

	def tong_reuqestCampaignMonsterRaidWindow( self, selfEntityID, npcID, campaignLevel ):
		"""
		Exposed method.
		玩家申请活动了 魔物来袭
		"""
		if self.id != selfEntityID or not BigWorld.entities.has_key( npcID ):
			return
		npc = BigWorld.entities[ npcID ]
		if not self.position.flatDistTo( npc.position ) < csconst.COMMUNICATE_DISTANCE:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.startCampaign_monsterRaid( self.databaseID, campaignLevel )

	#-----------------------------------------进入某帮会领地----------------------------------------------------------
	def tong_enterTongTerritoryByDBID( self, tongDBID, position, direction ):
		"""
		define method.
		进入指定DBID的帮会领地
		"""
		self.setTemp( "enter_tong_territory_datas", { "enterOtherTong" : tongDBID } )
		self.gotoSpace( "fu_ben_bang_hui_ling_di", position, direction )

	def tong_setLastTongTerritoryDBID( self, tongDBID ):
		"""
		define method.
		设置最后一次进入的帮会领地DBID
		"""
		self.lastTongTerritoryDBID = tongDBID
		# self.writeToDB()

	# ----------------------------------- 帮会仓库 -----------------------------------------------
	def tong_enterStorage( self ):
		"""
		申请打开仓库
		"""
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.enterStorage( self.databaseID )


	def tong_storeItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		往帮会仓库里存储物品的接口，已知目标物品格

		param srcOrder:	背包格子号
		type srcOrder:	INT16
		param dstOrder:	帮会仓库格子号
		type dstOrder:	INT16
		param entityID:	帮会npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbagItem = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return

		if kitbagItem.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "物品不存在" )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定." )
			return

		# 特定物品等级限制不能存帮会仓库
		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.LEVEL_RESTRAIN_ITEM_NOT_TRADE, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return

		if item.isBinded():
			self.statusMessage( csstatus.TONG_STORAGE_CANT_STORE )
			return

		tempItem = item.copy()		# 取得一份干净的物品数据，且在包裹锁定之前
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			kitbagItem.freeze()			# 锁定包裹，因为如果只锁定物品的话，在cell把物品数据发送给base后，cell的包裹可能会被交换或其他一些操作
			tongMailbox.storeItem2Order( srcOrder, tempItem, dstOrder, self.databaseID )


	def tong_storeItem2Bag( self, srcEntityID, srcOrder, bagID, entityID ):
		"""
		Exposed method.
		存储物品到指定的包裹

		@param srcOrder:	背包格子号
		@type srcOrder:	INT16
		@param bagID:	帮会仓库包裹id
		@type bagID:	INT16
		@param entityID:	帮会npc的id
		@type entityID:	OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbagItem = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return

		if kitbagItem.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "物品不存在" )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定." )
			return

		# 特定物品等级限制不能存帮会仓库
		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.LEVEL_RESTRAIN_ITEM_NOT_TRADE, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return

		if item.isBinded():
			self.statusMessage( csstatus.TONG_STORAGE_CANT_STORE )
			return
		tempItem = item.copy()		# 取得一份干净的物品数据，且在包裹锁定之前
		kitbagItem.freeze()			# 锁定包裹，因为如果只锁定物品的话，在cell把物品数据发送给base后，cell的包裹可能会被交换或其他一些操作
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.storeItem2Bag( srcOrder, tempItem, bagID, self.databaseID )


	def tong_storeItem2Storage( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		存储物品到帮会仓库

		param srcOrder:	背包格子号
		type srcOrder:	INT16
		param dstOrder:	帮会仓库格子号
		type dstOrder:	INT16
		param entityID:	帮会npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbagItem = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return

		if kitbagItem.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "物品不存在" )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定." )
			return

		# 特定物品等级限制不能存帮会仓库
		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.LEVEL_RESTRAIN_ITEM_NOT_TRADE, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return

		if item.isBinded():
			self.statusMessage( csstatus.TONG_STORAGE_CANT_STORE )
			return
		tempItem = item.copy()		# 取得一份干净的物品数据，且在包裹锁定之前
		kitbagItem.freeze()			# 锁定包裹，因为如果只锁定物品的话，在cell把物品数据发送给base后，cell的包裹可能会被交换或其他一些操作
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.storeItem2Storage( srcOrder, tempItem, self.databaseID )


	def tong_unfreezeBag( self, kitbagNum ):
		"""
		Define method.
		提供给base的回来解锁背包中被锁定包裹的接口

		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		"""
		if self.kitbags[kitbagNum].isFrozen():
			self.kitbags[kitbagNum].unfreeze()


	def tong_storeItemSuccess01( self, order ):
		"""
		Define method.
		往帮会仓库空位存储一个物品成功，回cell解锁并删除物品
		给base的,背包往帮会仓库存储一个物品成功的回调函数
		"""
		kitbagNum = order / csdefine.KB_MAX_SPACE
		self.kitbags[kitbagNum].unfreeze()
		self.removeItem_( order, reason = csdefine.DELETE_ITEM_TONG_STOREITEM )


	def tong_storeItemSuccess02( self, order, item ):
		"""
		Define method.
		叠加一个物品有剩余，或与帮会仓库目标格子交换物品，把剩余物品或交换的物品放回背包
		给base的,背包往帮会仓库存储一个物品成功的回调函数
		"""
		kitbagNum = order / csdefine.KB_MAX_SPACE
		self.kitbags[kitbagNum].unfreeze()
		self.removeItem_( order, reason = csdefine.DELETE_ITEM_TONG_STOREITEM )
		if self.addItemByOrderAndNotify_( item, order, reason = csdefine.ADD_ITEM_TONG_STOREITEM ):
			pass
		else:
			# 按理说这里不应该会出错，如果出错了可能有BUG
			ERROR_MSG( "当向背包里增加一个道具时失败。kitTote = %i, kitName = %s, orderID = %i" % ( kitbagNum, self.kitbags[kitbagNum].srcID, order ) )


	def tong_fetchItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		左键拖帮会仓库物品栏物品到确定的背包物品格

		param dstOrder:	格子号
		type dstOrder:	INT16
		param dstOrder:	格子号
		type dstOrder:	INT16
		param entityID:	帮会仓库npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE

		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			kitbag.freeze()
			tongMailbox.fetchItem2Order( srcOrder, dstOrder, self.databaseID  )


	def tong_fetchItem2OrderCB( self, dstOrder, item, srcOrder ):
		"""
		Define method.
		从帮会仓库取出物品的回调
		"""
		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE

		kitbagItem = self.kitbags[kitbagNum]
		kitbagItem.unfreeze()

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			if not self.tong_addItem2Order( dstOrder, srcOrder, item, tongMailbox ):	# 添加失败
				tongMailbox.unFreezeStorageRemote()
				return


	def tong_fetchItem2Kitbags( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		从帮会仓库里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位

		param entityID:	帮会仓库npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		order = self.getNormalKitbagFreeOrder()
		if order == -1:
			DEBUG_MSG( "玩家(%s)背包无空位。" % ( self.getName() ) )
			return
		kitbagNum = order / csdefine.KB_MAX_SPACE
		kitbag = self.kitbags[kitbagNum]
		if kitbag.isFrozen():
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			kitbag.freeze()
			tongMailbox.fetchItem2Kitbags( kitbagNum, srcOrder, self.databaseID  )

	def tong_fetchSplitItem2Kitbags(self, srcEntityID, entityID, srcOrder, amount):
		"""
		Exposed method.
		从帮会仓库里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位

		@param entityID:	帮会仓库npc的id
		@type entityID:	OBJECT_ID
		@param srcOrder: 仓库位置
		@type srcOrder: int16
		@param amount: 提取物品数量
		@type amount : int16
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		order = self.getNormalKitbagFreeOrder()
		if order == -1:
			DEBUG_MSG( "玩家(%s)背包无空位。" % ( self.getName() ) )
			return
		kitbagNum = order / csdefine.KB_MAX_SPACE
		kitbag = self.kitbags[kitbagNum]
		if kitbag.isFrozen():
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			kitbag.freeze()
			tongMailbox.fetchSplitItem2Kitbags( kitbagNum, srcOrder, amount, self.databaseID )


	def tong_fetchItem2KitbagsCB( self, srcOrder, srcItem ):
		"""
		Define method.
		被base的tong_fetchItem2Kitbags调用，把base发过来的物品放置到包裹中
		"""
		tongMailbox = self.tong_getSelfTongEntity()

		# 背包解锁
		kitbagNum = self.getNormalKitbagFreeOrder() / csdefine.KB_MAX_SPACE
		self.tong_unfreezeBag( kitbagNum )

		if srcItem.getStackable() > 1:	# 可叠加道具特殊处理
			if self.stackableItem( srcItem, reason = csdefine.ADD_ITEM_TONG_FETCHITEM  ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				tongMailbox.fetchItemSuccess01( srcOrder, self.databaseID )
				try:
					self.questItemAmountChanged( srcItem, srcItem.getAmount() )
				except:
					ERROR_MSG( "玩家( %s )从帮会仓库取物品到背包触发任务检测出错。" % self.getName() )
				return
		order = self.getNormalKitbagFreeOrder()		# getNormalKitbagFreeOrder()定义在itemBagRole.py中，在背包中查找空位
		if self.addItemByOrderAndNotify_( srcItem, order, reason = csdefine.ADD_ITEM_TONG_FETCHITEM ):
			tongMailbox.fetchItemSuccess01( srcOrder, self.databaseID )

	def tong_fetchSplitItem2KitbagsCB( self, srcOrder, srcItem ):
		"""
		Define method.
		被base的tong_fetchItem2Kitbags调用，把base发过来的物品放置到包裹中
		"""
		tongMailbox = self.tong_getSelfTongEntity()

		# 背包解锁
		kitbagNum = self.getNormalKitbagFreeOrder() / csdefine.KB_MAX_SPACE
		self.tong_unfreezeBag( kitbagNum )

		if srcItem.getStackable() > 1:	# 可叠加道具特殊处理
			if self.stackableItem( srcItem, reason = csdefine.ADD_ITEM_TONG_FETCHITEM  ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				tongMailbox.fetchItemSuccess03( srcOrder, srcItem.amount,  self.databaseID )
				try:
					self.questItemAmountChanged( srcItem, srcItem.getAmount() )
				except:
					ERROR_MSG( "玩家( %s )从帮会仓库取物品到背包触发任务检测出错。" % self.getName() )
				return
		order = self.getNormalKitbagFreeOrder()		# getNormalKitbagFreeOrder()定义在itemBagRole.py中，在背包中查找空位
		if self.addItemByOrderAndNotify_( srcItem, order, reason = csdefine.ADD_ITEM_TONG_FETCHITEM ):
			tongMailbox.fetchItemSuccess03( srcOrder, srcItem.amount,  self.databaseID )

	def tong_moveStorageItem( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		移动帮会仓库的物品
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.moveStorageItem( srcOrder, dstOrder, self.databaseID  )


	def tong_addItem2Order( self, dstOrder, tongOrder, srcItem, tongMailbox ):
		"""
		把一个物品放到指定包裹的格子中,被tong_fetchItem2OrderCB调用
		成功则返回true，否则返回false

		param kitbag:	包裹实例
		type kitbag:	KITBAG
		param dstOrder:	格子号
		type dstOrder:		INT16
		"""
		if self.addItemByOrderAndNotify_( srcItem, dstOrder, csdefine.ADD_ITEM_TONG_ADDITEM2ORDER ):
			tongMailbox.fetchItemSuccess01( tongOrder, self.databaseID )
			return True
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		dstItem = self.getItem_( dstOrder )
		if dstItem.isFrozen() == 1:
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return False
		if dstItem.isBinded():
			self.statusMessage( csstatus.TONG_STORAGE_CANT_STORE )
			return False

		if srcItem.getStackable() > 1 and dstItem.id == srcItem.id:	# 可叠加道具特殊处理
			overlapAmount = srcItem.getStackable()
			dstAmount = dstItem.getAmount()
			srcAmount = srcItem.getAmount()
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount, self, csdefine.ADD_ITEM_TONG_ADDITEM2ORDER )
			try:
				self.questItemAmountChanged( dstItem, dstItem.getAmount() )
			except:
				ERROR_MSG( "玩家( %s )从帮会仓库取物品到背包触发任务检测出错。" % self.getName() )
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# 在目标位置叠加后还有剩余，放回仓库
				srcItem.setAmount( srcAmount )
				tongMailbox.fetchItemSuccess02( tongOrder, srcItem, self.databaseID )
				return True
			else:
				tongMailbox.fetchItemSuccess01( tongOrder, self.databaseID )
				return True
		else:	# id相同的不可叠加物品 与 id不同的可叠加物品 是交换操作
			self.removeItem_( dstOrder, reason = csdefine.DELETE_ITEM_TONG_STOREITEM )
			if self.addItemByOrderAndNotify_( srcItem, dstOrder, csdefine.ADD_ITEM_TONG_ADDITEM2ORDER ):
				self.statusMessage( csstatus.CIB_MSG_GAIN_ITEMS,  srcItem.query( "name" ), srcItem.getAmount() )
				tongMailbox.fetchItemSuccess02( tongOrder, dstItem, self.databaseID )
				return True
		return False


	def _tongStorageOperateVerify( self, srcEntityID, entityID ):
		"""
		验证是否能够进行帮会仓库操作

		@param entityID:寄卖npc的id
		@type entityID: OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return False

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return False
		return True

	def tong_renameStorageBag( self, srcEntityID, bagID, newName, entityID ):
		"""
		Exposed method.

		@param bagID : 包裹id
		@type bagID : UINT8
		@param newName : 包裹位名字
		@type newName : STRING
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.renameStorageBag( bagID, newName, self.databaseID  )


	def tong_changeStorageBagLimit( self, srcEntityID, bagID, officialPos, limitNum, entityID ):
		"""
		Exposed method.
		帮会仓库的权限更改
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.changeStorageBagLimit( bagID, officialPos, limitNum, self.databaseID )

	def tong_changeStorageQualityLower( self, srcEntityID, bagID, quality, entityID ):
		"""
		Exposed method.
		改变帮会仓库包裹的品质下限

		@param bagID : 包裹位id
		@type bagID : UINT8
		@param quality : 品质
		@type quality : UINT8
		@param entityID : npcID
		@type entityID : OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.changeStorageQualityLower( bagID, quality, self.databaseID )


	def tong_changeStorageQualityUp( self, srcEntityID, bagID, quality, entityID ):
		"""
		Exposed method.
		改变帮会仓库包裹的品质上限

		@param bagID : 包裹位id
		@type bagID : UINT8
		@param quality : 品质
		@type quality : UINT8
		@param entityID : npcID
		@type entityID : OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.changeStorageQualityUp( bagID, quality, self.databaseID )

	#------------------------------------------帮会装备修理-------------------------------------------------------
	def tong_repairOneEquip( self, repairType, kitBagID, orderID ):
		"""
		define method.
		单个装备修理
		@param    repairType: 修理类型
		@type     repairType: int
		@param    kitBagID: 背包索引
		@type     kitBagID: UINT16
		@param    orderID: 物品索引
		@type     orderID: INT32
		@return   无
		"""
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_REPARE, "" )
			return
		# 获取要单个修理的装备
		equip = self.getItem_( orderID )
		if equip == None:
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_EXIST )
			return
		#  判断装备能否修理
		if not equip.canRepair():
			self.statusMessage( csstatus.EQUIP_REPAIR_CANT_REPAIR )
			return
		#  判断装备耐久度是否无需修理
		if equip.getHardiness() == equip.getHardinessLimit():
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_REPAIR )
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.requestRepairOneEquip( repairType, kitBagID, orderID, self.databaseID  )

	def tong_onRepairOneEquipBaseCB( self, repairType, kitBagID, orderID, abate ):
		"""
		define method.
		单个装备修理
		@param    repairType: 修理类型
		@type     repairType: int
		@param    kitBagID: 背包索引
		@type     kitBagID: UINT16
		@param    orderID: 物品索引
		@type     orderID: INT32
		@param abate : 折扣
		@param abate : FLOAT
		@return   无
		"""
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_REPARE, "" )
			return
		# 获取要单个修理的装备
		equip = self.getItem_( orderID )
		if equip == None:
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_EXIST )
			return

		val = self._calcuRepairEquipMoney( equip, repairType, 0 )[0]
		repairMoney = int( math.ceil( val * abate ) )
		if not self.payMoney( repairMoney, csdefine.CHANGE_MONEY_REPAIRONEEQUIPBASE  ):
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
			return

		if repairType != csdefine.EQUIP_REPAIR_SPECIAL:
			equip.addHardinessLimit( - int( equip.getHardinessMax() * 0.05 ),  self )
		equip.addHardiness( equip.getHardinessLimit(),  self )
		self.statusMessage( csstatus.EQUIP_REPAIR_SUCCEED, equip.name() )
		self.client.equipRepairCompleteNotify()

	def tong_repairAllEquip( self, repairType ):
		"""
		define method.
		修理身上所有装备
		@param    repairType: 修理类型
		@type     repairType: int
		@return   无
		"""
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.requestRepairAllEquip( repairType, self.databaseID  )

	def tong_requestRepairAllEquipBaseCB( self, repairType, abate ):
		"""
		define method.
		修理身上所有装备
		@param    repairType: 修理类型
		@type     repairType: int
		@param abate : 折扣
		@param abate : FLOAT
		@return   无
		"""
		repairMoney = 0
		repairEquips = []

		for item in self.getAllItems():
			if item.isEquip():
				if not item.canRepair():	# wsf,16:21 2008-7-2
					DEBUG_MSG( "( %i )'s equip( id:%s ) can not be repaired." % ( self.id, item.id ) )
					continue
				if item.getHardiness() == item.getHardinessLimit():
					continue
				repairEquips.append( item )
				repairMoney += self._calcuRepairEquipMoney( item, repairType, 0 )[0]

		if len( repairEquips ) == 0:
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_REPAIR )
			return

		repairMoney = int( math.ceil( repairMoney * abate ) )
		if not self.payMoney( repairMoney, csdefine.CHANGE_MONEY_REPAIRALLEQUIPBASE ):
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
			return

		for equip in repairEquips:
			if repairType != csdefine.EQUIP_REPAIR_SPECIAL:
				equip.addHardinessLimit( - int( equip.getHardinessMax() * 0.05 ), self )
			equip.addHardiness( equip.getHardinessLimit(), self )

		self.statusMessage( csstatus.EQUIP_REPAIR_ALL_SUCCEED )
		self.client.equipRepairCompleteNotify()

	#-------------------------------领取帮会占领城市利益---------------------------------------------------------

	def tong_getCityTongItem( self ):
		"""
		define method.
		领取城市占领帮会的经验果实
		"""
		awarder = g_rewards.fetch( csdefine.RCG_TONG_CITY_EXP, self )
		if awarder is None or len( awarder.items ) <= 0:
			self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		item = awarder.items[0]		# 理论上只有1个物品，多了就是配置问题
		if item.id == 40401019:
			amount = 0
			for r_item in self.getAllItems():
				if r_item.id == item.id: # 蘑菇的编号
					amount += 1
				if amount >= 5:
					self.statusMessage( csstatus.TONG_JYGS_ITEM_MAX )
					return
		awarder.award( self, csdefine.ADD_ITEM_GETCITYTONGITEM )
		self.getTongManager().onGetCityTongItemSuccess( self.databaseID )

	# ---------------------------------------- 保护帮派进入副本 -------------------------------------------------
	def tong_onProtectTongDie( self, selfEntityID ):
		"""
		define method.
		保护帮派活动副本中死亡
		"""
		if self.id != selfEntityID:
			return

		spaceType = self.getCurrentSpaceType()
		if spaceType & csdefine.SPACE_TYPE_PROTECT_TONG > 0:
			spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			space = g_objFactory.getObject( spaceKey )
			self.teleport( None, space.playerEnterPoint[ 0 ], space.playerEnterPoint[ 1 ] )
			self.changeState( csdefine.ENTITY_STATE_FREE )
			self.setHP( self.HP_Max )
			self.setMP( self.MP_Max )
		else:
			self.revive( selfEntityID, csdefine.REVIVE_ON_CITY )

	def tong_onMemberRequestMapInfo( self, pBase ):
		"""
		"""
		pBase.client.tong_updateMemberMapInfo( self.databaseID, self.spaceType, self.position, self.getCurrentSpaceLineNumber() )

	#-----------------------------------------客户端打开帮会界面----------------------------------------------------------
	def tong_onClientOpenTongWindow( self, selfEntityID ):
		"""
		Expose method.
		客户端打开帮会界面， 需要请求一些信息。
		"""
		if self.id != selfEntityID:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onClientOpenTongWindow( self.base )

	#-----------------------------------------帮会查询----------------------------------------------------------
	def tong_setTongAD( self, selfEntityID, tongDBID, strAD ):
		"""
		Expose method.
		设置帮会广告
		@param strAD: 帮会广告
		"""
		if self.id != selfEntityID or tongDBID <= 0 or tongDBID != self.tong_dbID or \
			not self.checkDutyRights( csdefine.TONG_RIGHT_SET_AD ):
			return

		self.getTongManager().setTongAD( self.base, tongDBID, strAD )

	def tong_requestTongList( self, selfEntityID, index, camp ):
		"""
		Exposed method.
		某个玩家申请获取帮会列表
		@param index: 客户端向服务器申请的批次
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().requestTongList( self.base, index, camp )

	def tong_queryTongInfo( self, selfEntityID, tongDBID ):
		"""
		Exposed method.
		查询某个帮会的信息
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().queryTongInfo( self.base, tongDBID )

	#--------------------------------------------------------------------------------------------------------
	def tong_requestJoinToTong( self, selfEntityID, tongDBID ):
		"""
		Exposed method.
		申请加入到某个帮会
		"""
		if self.id != selfEntityID or self.isJoinTong():
			return
		if self.level < csconst.TONG_JOIN_MIN_LEVEL:
			self.statusMessage( csstatus.TONG_CANT_REQUEST_JOIN_LEVEL_LACK, csconst.TONG_JOIN_MIN_LEVEL  )
			return
		tongMailbox = self.tong_getTongEntity( tongDBID )
		if tongMailbox:
			tongMailbox.requestJoinToTong( self.base, self.databaseID, self.getName(), self.getCamp() )
		else:
			ERROR_MSG( "not found tongMailbox %i." % tongDBID )

	def tong_answerJoinToTong( self, selfEntityID, playerDBID, agree ):
		"""
		define method.
		帮主回答是否愿意加入这个玩家
		"""
		if self.id != selfEntityID or not self.isJoinTong():
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.answerJoinToTong( playerDBID, agree )

	def tong_tongListEnterTongTerritory( self, selfEntityID, tongDBID ):
		"""
		Exposed method.
		进入指定DBID的帮会领地
		"""
		if self.id != selfEntityID and tongDBID > 0:
			return
		self.tong_enterTongTerritoryByDBID( tongDBID, ( 0, 0, 0 ), ( 0, 0, 0 ) )

	#--------------------------------------------------------------------------------------------------------
	def isTongChief( self ):
		"""
		是否帮主
		"""
		return self.tong_grade == csdefine.TONG_DUTY_CHIEF
	
	def isTongDeputyChief( self ):
		"""
		是否副帮主
		"""
		return self.tong_grade == csdefine.TONG_DUTY_DEPUTY_CHIEF

	def checkDutyRights( self, right):
		"""
		检测某位置的权限
		"""
		dutyMapping = csdefine.TONG_DUTY_RIGHTS_MAPPING
		if right not in dutyMapping[ self.tong_grade ]:
			return False
		
		return True
	#--------------------------------------------------------------------------------------------------------
	def requestChangeTongName( self, srcEntityID, newName ):
		"""
		Exposed method.
		"""
		if srcEntityID != self.id:
			HACK_MSG( "srcEntityID( %i ) != dstEntityID( %i )" % ( srcEntityID, self.id ) )
			return
		if not self.checkDutyRights( csdefine.TONG_RIGHT_CHANGE_NAME ):
			self.statusMessage( csstatus.TONG_GRADE_INVALID )
			return
		if newName == self.tongName:
			return
		if len( newName ) > 14:	# 帮会名称合法性检测
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if newName == "":
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if not chatProfanity.isPureString( newName ):
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if chatProfanity.searchNameProfanity( newName ) is not None:
			self.statusMessage( csstatus.TONG_NAME_INVALID )
			return
		if not self.tongName.endswith( cschannel_msgs.ACCOUNT_NOTICE_7 ):
			return
		self.getTongManager().changeTongName( self, self.tong_dbID, newName )

	def onTongNameChange( self, newTongName ):
		"""
		Define method.
		帮会名字改变
		"""
		self.statusMessage( csstatus.TONG_RENAME_SUCCESS, self.tongName, newTongName )
		self.tongName = newTongName

	#--------------------------------------------------------------------------------------------------------
	def tong_contributeToMoney( self, srcEntityID, money ):
		"""
		Exposed method.
		请求捐献金钱给帮会
		"""
		if srcEntityID != self.id:
			HACK_MSG( "srcEntityID( %i ) != dstEntityID( %i )" % ( srcEntityID, self.id ) )
			return

		if money > self.money:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onContributeToMoney( self.base, self.playerName, money )

	def tong_onContributeToMoneySuccessfully( self, money, isFull ):
		"""
		define method.
		捐献金钱成功
		"""
		if not self.payMoney( money, csdefine.CHANGE_MONEY_TONG_CONTRIBUTE ):
			return

		if isFull:
			self.statusMessage( csstatus.TONG_CONTRIBUTE_TO_MONEY_OVER, Function.switchMoney( money ) )

		if money >= 1000000:
			self.addTitle( 90 )

	def tong_leave( self ):
		"""
		Define method.
		离开帮会的处理
		"""
		tongBase = self.tong_getSelfTongEntity()
		if tongBase:
			tongBase.memberLeave( self.databaseID )
		self.base.tong_leave()
		self.tong_reset()
		self.tong_onChanged()
		self.tong_clearTongSkills()
		self.writeToDB()

	# ------------------------- 帮会擂台赛相关 ------------------------------
	def tong_dlgAbattoirRequest( self ):
		"""
		向帮会npc申请帮会擂台赛
		"""
		if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_ABA ): # 权限判断
			self.statusMessage( csstatus.TONG_ABATTOIR_NOT_LEADER )
			return
		self.tong_getSelfTongEntity().requestAbattoir( self.base )

	def tong_onInTongAbaRelivePoint( self, srcEntityID, index ):
		"""
		Exposed method.
		帮会擂台死亡复活
		"""
		if srcEntityID != self.id:
			HACK_MSG( "-------->>>srcEntityID( %i ) != self.id( %i )." % ( srcEntityID, self.id ) )
			return

		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_TONG_ABA:
			spaceSID = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			space = g_objFactory.getObject( spaceSID )
			points = space.right_relivePoints
			if not self.queryTemp( "aba_right", False ):
				points = space.left_relivePoints
			if len( points ) - 1 < index:
				self.revive( srcEntityID, csdefine.REVIVE_ON_CITY )
				return
			self.teleport( None, points[ index ][ 0 ], points[ index ][1] )
			self.changeState( csdefine.ENTITY_STATE_FREE )
			self.setHP( self.HP_Max )
			self.setMP( self.MP_Max )
			# 做个复活回调， 主要是在副本结束后 角色未复活， 副本会施放无敌BUFF， 等角色复活后 会处于无保护状态， 所以
			# 回调到副本， 副本会给他重新加上
			spaceBase = self.getCurrentSpaceBase()
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal():
				spaceEntity.getScript().onPlayerRelive( spaceEntity, self.id, self.databaseID )
			else:
				spaceBase.cell.remoteScriptCall( "onPlayerRelive", ( self.id, self.databaseID, ) )
		else:
			self.revive( srcEntityID, csdefine.REVIVE_ON_CITY )

	def tong_onAbattoirOver( self ):
		"""
		define method.
		帮会擂台赛结束了，如果还在副本则传送出来
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_TONG_ABA:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )
				# 改变状态,满血满魔
				self.changeState( csdefine.ENTITY_STATE_FREE )
				self.setHP( self.HP_Max )
				self.setMP( self.MP_Max )
			else:
				self.gotoForetime()

	def tong_chooseAbaRelivePoint( self, selfEntityID, index ):
		"""
		Exposed method.
		玩家在战场内选择了复活点位置
		@param index : 3个复活点其中一个索引 0, 1, 2
		"""
		if selfEntityID != self.id:
			return

		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_TONG_ABA:
			spaceSID = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			space = g_objFactory.getObject( spaceSID )
			points = space.right_relivePoints
			if len( self.tongNPC ) <= 0:
				points = space.left_relivePoints
			if len( points ) - 1 < index:
				self.revive( selfEntityID, csdefine.REVIVE_ON_CITY )
				return
			self.teleport( None, points[ index ][ 0 ], points[ index ][1] )
			self.changeState( csdefine.ENTITY_STATE_FREE )
			self.setHP( self.HP_Max )
			self.setMP( self.MP_Max )
			# 做个复活回调， 主要是在副本结束后 角色未复活， 副本会施放无敌BUFF， 等角色复活后 会处于无保护状态， 所以
			# 回调到副本， 副本会给他重新加上
			spaceBase = self.getCurrentSpaceBase()
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal():
				spaceEntity.getScript().onPlayerRelive( spaceEntity, self.id )
			else:
				spaceBase.cell.remoteScriptCall( "onPlayerRelive", ( self.id, ) )
		else:
			self.revive( selfEntityID, csdefine.REVIVE_ON_CITY )

	def tong_clearWarItems( self ):
		"""
		define method.
		清除帮会战阵玩家身上的战场物品
		"""
		dropItems = []
		for item in self.getAllItems():
			if str( item.id )[ 0 : 3 ] == "403": # 取前3位判断是否是战场类物品
				dropItems.append( item )
		for item in dropItems:
			self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_CLEARWARITEMS )

	def tong_AbaItemsDropOnDied( self ):
		"""
		自己在帮会战场死亡， 计算掉落战场物品
		"""
		pos = self.position
		dropItems = []

		for item in self.getAllItems():
			if str( item.id )[ 0 : 3 ] == "403": # 取前3为判断是否是战场类物品
				dropItems.append( item )

		# 开始在地图上摆放
		for item in dropItems:
			x1 = random.random() * 4 - 2
			z1 = random.random() * 4 - 2
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# 计算出放置的位置
			g_items.createEntity( item.id, self.spaceID, (x, y, z), self.direction, { "itemProp" : item } )
			self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_ABAITEMSDROPONDIED )

	def tong_leaveWarSpace( self, selfEntityID ):
		"""
		Exposed method.
		玩家要逃离战场
		"""
		if selfEntityID != self.id:
			return
		if self.getState() == csdefine.ENTITY_STATE_FREE:
			self.gotoForetime()

	def sendTongFaction( self, tongFaction ):
		"""
		define method
		接受帮会时装余量
		"""
		self.factionCount = tongFaction

	def tong_competitionRequest( self, talkEntity ):
		"""
		向npc申请报名帮会竞技
		"""
		if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_COMPETITION ): # 权限判断
			self.statusMessage( csstatus.TONG_COMPETETION_TONG_REQUIRED )
			return
		self.tong_getSelfTongEntity().requestCompetition( self.base )
	
	#----------------------------帮会俸禄相关------------------------------------------------
	def tong_onDrawTongSalary( self, selfEntityID ):
		"""
		Exposed method
		领取帮会俸禄
		"""
		#if selfEntityID != self.id:
		#	return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onDrawTongSalary( self.databaseID )
		
	def tong_onSalaryExchangeRate( self, selfEntityID, rate ):
		"""
		Exposed method
		帮主设定每点帮贡兑换额
		"""
		if selfEntityID != self.id:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.setContributeExchangeRate(  self.databaseID, rate )		
			
	def tong_onClientOpenTongMoneyWindow(  self, selfEntityID ):
		"""
		Exposed method
		打开帮会资金界面,查询帮会资金和俸禄相关信息
		"""
		if self.id != selfEntityID:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onClientOpenTongMoneyWindow( self.base )

	def tong_onAbandonTongCity( self, selfEntityID, city ):
		"""
		Exposed method
		放弃占领城市
		"""
		if self.id != selfEntityID:
			return
		if not self.isTongChief():
			self.statusMessage( csstatus.TONG_ABANDON_HOLD_CITY_NO_GRADE )
			return
		cityNameCN = csconst.TONG_CITYWAR_CITY_MAPS.get( city, "" )
		if cityNameCN != "":
			BigWorld.globalData[ "TongManager" ].cityWarDelMaster( cityNameCN )

	def tong_onFengHuoLianTianOver( self ):
		"""
		define method.
		帮会夺城战复赛（烽火连天）结束了， 如果还在副本则传送出来
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# 改变状态,满血满魔
				self.reviveActivity()
			
		
		self.client.tong_onFengHuoLianTianOver()

	def tong_leaveFengHuoLianTian( self ):
		# define method
		# 离开帮会夺城战复赛（烽火连天）
		
		enterInfos = self.query( "TongFengHuoLianTianEnterInfos" )
		if enterInfos:
			self.gotoSpace( enterInfos[ 0 ], enterInfos[ 1 ], enterInfos[ 2 ] )
			self.remove( "TongFengHuoLianTianEnterInfos" )
		else:
			self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )
			
	def tong_onQueryFHLTTable( self, selfEntityID, cityName ):
		"""
		Exposed method.
		请求查看城市赛程表 或者 赛况表
		"""
		if self.id != selfEntityID:
			return
		BigWorld.globalData[ "TongManager" ].onQeryFHLTVersus( cityName, self.base )

	#---------------------------------------------帮会任务相关-------------------------------------------
	def onDartQuestStatusChange( self, isOpen ):
		"""
		define method
		帮会运镖任务开启状态改变
		
		@param isOpen: True为开启，False为关闭
		@type isOpen: BOOL
		"""
		self.tongDartQuestIsOpen = isOpen
		self.client.onDartQuestStatusChange( isOpen )
		
	def onNormalQuestStatusChange( self, openType ):
		"""
		define method
		帮会日常任务开启状态改变
		
		@param openType: 开启类型，为0表示关闭
		@type openType: UINT8
		"""
		self.tongNormalQuestOpenType = openType
		self.client.onNormalQuestStatusChange( openType )

	#---------------------------------------------战争结盟-------------------------------------------
	
	def tong_requestBattleLeagues( self, selfEntityID, index, camp ):
		"""
		Exposed method
		查询帮会战争联盟信息
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().queryTongBattleLeagues( self.base, index, camp, self.spaceType )
	
	def tong_inviteTongBattleLeagues( self, selfEntityID, inviteeTongDBID, msg ):
		"""
		Exposed method
		邀请战争结盟
		@param tongDBID :要邀请帮会的DBID
		"""
		if selfEntityID != self.id:
			return
		
		if not self.checkDutyRights( csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			self.statusMessage( csstatus.TONG_GRADE_INVALID )
			return
		
		DEBUG_MSG( "TONG:%s invite tong %s to  battle league." % ( self.getNameAndID(), inviteeTongDBID ) )
		self.getTongManager().inviteTongBattleLeague( self.databaseID, self.base, self.tong_dbID, inviteeTongDBID, msg )

	def tong_replyBattleLeagueInvitation( self, selfEntityID, inviterTongDBID, response ):
		"""
		Exposed method
		回复战争结盟邀请
		"""
		if selfEntityID != self.id:
			return
		
		DEBUG_MSG( "TONG:%i answer tong %i to league." % ( selfEntityID, inviterTongDBID ) )
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.replyBattleLeagueInvitation( self.base, inviterTongDBID, response )

	def tong_battleLeagueDispose( self, srcEntityID, battleLeagueDBID ):
		"""
		Exposed method
		解除战争同盟关系
		"""
		if srcEntityID != self.id:
			return

		DEBUG_MSG( "TONG: %i dispose to tong %i of league." % ( self.tong_dbID, battleLeagueDBID ) )
		self.getTongManager().requestBattleLeagueDispose( self.databaseID, self.base, self.tong_dbID, battleLeagueDBID )

	def tong_onCityWarFinalReliveCB( self, pos, dir, space, spaceID ):
		"""
		define method
		帮会夺城战决赛复活回调
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #刷新速度
		self.teleportToSpace( pos, dir, space, spaceID )

# $Log: not supported by cvs2svn $
# Revision 1.10  2008/08/12 08:51:48  kebiao
# 添加帮主集结令功能
#
# Revision 1.9  2008/07/22 01:58:59  huangdong
# 完善帮派聊天
#
# Revision 1.8  2008/06/30 04:15:09  kebiao
# 增加帮会职位名称编辑
#
# Revision 1.7  2008/06/27 07:12:15  kebiao
# 增加了帮会和家族的异步数据传输机制
#
# Revision 1.6  2008/06/23 08:12:28  kebiao
# no message
#
# Revision 1.5  2008/06/21 03:42:36  kebiao
# 加入帮会贡献度
#
# Revision 1.4  2008/06/16 09:14:14  kebiao
# base 上部分暴露接口转移到cell
#
# Revision 1.3  2008/06/14 09:18:26  kebiao
# 新增帮会功能
#
# Revision 1.2  2008/06/10 01:55:02  kebiao
# add:tong_reset
#
# Revision 1.1  2008/06/09 09:24:13  kebiao
# 加入帮会相关
#
# Revision 1.6  2008/05/22 03:47:57  kebiao
# fix condition bug
#
# Revision 1.5  2008/05/15 07:04:58  kebiao
# 添加权衡关系
#
# Revision 1.4  2008/05/14 02:54:36  kebiao
# 添加邀请加入等功能
#
# Revision 1.3  2008/05/09 08:26:13  kebiao
# 添加信息提示 接口注释
#
# Revision 1.2  2008/05/09 03:16:21  kebiao
# 第1阶段框架代码设计
#
# Revision 1.1  2008/05/06 09:02:17  kebiao
# no message
#
#