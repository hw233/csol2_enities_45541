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
from Resource.TongRobWarRewardLoader import TongRobWarRewardLoader		# ��������������Ϊ�������

from TongCityWarFightInfos import MasterChiefData

g_tongRobWarRewards = TongRobWarRewardLoader.instance()
g_feteDataLoader = TongFeteDataLoader.instance()

FETE_MATERIAL_LIST = [ 80101003, 80101009, 80101015, 80101021, 80101027 ]	# 2�����������Ʒid�б�

TONG_GRADE_MEMBER_MAX_MAP = { 0:0, 1:30, 2:60, 3:90, 4:120, 5:150 }

CITY_WAR_CHIEF_REWARD_BOX_FAIL	= 60101267 # ������ս�������⽱����ʧ�ܱ���
CITY_WAR_CHIEF_REWARD_BOX_WIN	= 60101268 # ������ս�������⽱����ʤ������
CITY_WAR_CHIEF_REWARD_ITEM		= 50101101 # ������ս�������⽱������������ӡ��

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
		��ȡ���entity
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
		����Լ�����mailbox
		"""
		return self.tong_getTongEntity( self.tong_dbID )

	def tong_getMemberCountMax( self ):
		"""
		����Լ�����������������
		"""
		return TONG_GRADE_MEMBER_MAX_MAP[self.tong_level]

	def isJoinTong(self):
		"""
		�ж�����Ƿ������
		tong_grade ��Ϊ0 ��ʾ���һ�������˰��
		"""
		return self.tong_dbID > 0

	def tong_onSetContribute( self, contribute ):
		"""
		define method.
		���ð�ṱ�׶�
		"""
		# ������tongEntity����  �����ֶ����ô˽ӿ�
		self.tong_contribute = contribute

	def tong_payContribute( self, contribute ):
		"""
		֧����ṱ�׶�
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
		��Ӱ�ṱ�׶�
		"""
		#--------- ����Ϊ������ϵͳ���ж� --------#
		gameYield = self.wallow_getLucreRate()
		if contribute >=0:
			contribute = contribute * gameYield
		#--------- ����Ϊ������ϵͳ���ж� --------#
		self.tong_contribute += contribute
		self.statusMessage( csstatus.ACCOUNT_STATE_GAIN_TONGCONTRIBUTE, int(contribute) )
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onMemberContributeChanged( self.databaseID, self.tong_contribute )
		else:
			ERROR_MSG( "not found tongMailbox %i." % self.tong_dbID )

	def tong_addMoney( self, money, reason = csdefine.TONG_CHANGE_MONEY_NORMAL  ):
		"""
		��Ӱ���ʽ�
		"""
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.addMoney( money, reason )

	def tong_onSetTongName( self, tongName ):
		"""
		define method.
		���ð������
		"""
		self.tongName = tongName

	def optionReduceRD_tong( self ):
		"""
		���ȼ��ı����������������ӡ�ɾ��
		"""
		reduceRate = self.queryTemp( "ADD_REDUCE_ROEL_D_TONG", 0.0 )
		if self.tong_dbID == 0:#�˳������
			if reduceRate > 0.0 : #�а���������������
				self.reduce_role_damage_extra -= reduceRate
				self.calcReduceRoleDamage()
				self.setTemp( "ADD_REDUCE_ROEL_D_TONG", 0.0 )
		else: #�ڰ����
			if self.tong_level in Const.TONG_ADD_REDUCE_ROLE_DAMAGE: #���ȼ����Դ���������������
				rm = Const.TONG_ADD_REDUCE_ROLE_DAMAGE[self.tong_level]
				if reduceRate <= 0.0 : #��û�а���������������
					self.reduce_role_damage_extra += rm
					self.calcReduceRoleDamage()
					self.setTemp( "ADD_REDUCE_ROEL_D_TONG", rm )
				if reduceRate > 0.0 and reduceRate != rm: #�Ѿ�����ˣ��������ڰ��������
					self.reduce_role_damage_extra -= reduceRate
					self.reduce_role_damage_extra += rm
					self.calcReduceRoleDamage()
					self.setTemp( "ADD_REDUCE_ROEL_D_TONG", rm )
			else: #���ȼ����ܴ���������������
				if reduceRate > 0.0 : #�а���������������
					self.reduce_role_damage_extra -= reduceRate
					self.calcReduceRoleDamage()
					self.setTemp( "ADD_REDUCE_ROEL_D_TONG", 0.0 )
		
	
	def tong_onSetTongLevel( self, level ):
		"""
		define method.
		���ð�ἶ��
		"""
		self.tong_level = level
		self.optionReduceRD_tong()
		self.client.tong_onSetTongLevel( level )

	def tong_onChanged( self ):
		"""
		virtual method.
		��ҵİ��ı���  ��������˳���
		"""
		self.optionReduceRD_tong()
		# �������ɢ�����˳������
		if self.tong_dbID == 0:
			spaceType = self.getCurrentSpaceType()
			# ��һ��ڳ�ս�������䴫��
			if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
				self.tong_onCityWarOver()
			# �������������������ɾ������
			merchantQuest = self.getMerchantQuest()
			if merchantQuest is None: return
			self.questRemove( merchantQuest.getID(), True )  # ����������������

	def tong_setGrade( self, grade ):
		"""
		define method.
		���ø�player grade
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
		��½���
		"""
		DEBUG_MSG( "player %s:%i login tong dbid=%i id =%i " % ( self.playerName, self.id, self.tong_dbID, tongBaseMailbox.id ) )

	#---------------------------------------------------------------------------------------------------------
	def createTong( self, selfEntityID, tongName, reason ):
		"""
		Exposed method.
		����һ�����
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

		# ������ƺϷ��Լ��
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
		���󴴽���ᣬ�����������ķ��ؽ��
		"""
		self.popTemp( "createTongData" )
		self.statusMessage( statusID )

	def tong_createSuccess( self, tongDBID, tongBaseMailbox ):
		"""
		define method.
		��ᴴ���ɹ��Ļص�
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
		��ȡ������߳�Ա
		"""
		return self.tong_onlineMemberMailboxs

	def tong_addMemberOL( self, baseEntityDBID, baseEntity ):
		"""
		define method.
		������߳�Ա
		"""
		DEBUG_MSG( "addMemberOL:%i" % baseEntityDBID )
		self.tong_onlineMemberMailboxs[ baseEntityDBID ] = baseEntity

	def tong_onMemberRemoveOL( self, baseEntityDBID ):
		"""
		define method.
		�г�Ա������
		"""
		DEBUG_MSG( "MemberRemoveOL:%i" % baseEntityDBID )
		self.tong_onlineMemberMailboxs.pop( baseEntityDBID )

	#---------------------------------------------------------------------------------------------------------

	def tong_requestJoin( self, selfEntityID, targetEntityID ):
		"""
		Exposed method.
		����ĳ�˼���tong
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
		������� �����ش�
		@param agree: bool, true = ����
		"""
		DEBUG_MSG( "player %i answer to tong %i " % ( selfEntityID, tongDBID ) )
		if self.id != selfEntityID:
			DEBUG_MSG( "player %i has a tong! dbid = %i" % ( selfEntityID, self.tong_dbID ) )
			return
		if self.isJoinTong():	# ����Ѿ������˰�ᣬ������Ҿܾ�����
			agree = False
		tongMailbox = self.tong_getTongEntity( tongDBID )
		if tongMailbox:
			tongMailbox.onAnswerRequestJoin( self.databaseID, agree, self.getName() )
		else:
			ERROR_MSG( "not found tongMailbox %i." % tongDBID )

	def tong_onJoin( self, tongDBID, grade, tongContribute, tongBaseMailbox ):
		"""
		Define method.
		�Ӱ��ɹ������ð������

		@param tongDBID : ����dbid
		@type tongDBID : DATABASE_ID
		@param grade : ���ְλ
		@type grade : UINT8
		@param tongContribute : ���ĳ�ʼ����
		@type tongContribute : UINT32
		@param tongBaseMailbox : ����base mailbox
		@type tongBaseMailbox : MAILBOX
		"""
		if self.isJoinTong():			# �п����ȼ������������
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
		������λ
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
		���÷�������ṫ��
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
		��ɢ���
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
		���Ҫ���˳����
		"""
		if selfEntityID != self.id:
			return
		# ����ֻ����λ�˳�
		if self.isTongChief():
			self.statusMessage( csstatus.TONG_CHIEF_QUIT )
			return
			
		tongEntity = self.tong_getSelfTongEntity()
		if tongEntity:
			tongEntity.memberLeave( self.databaseID )

	def tong_kickMember( self, selfEntityID, targetDBID ):
		"""
		Exposed method.
		���Ҫ��ĳ���߳����
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
		user����targetȨ��
		@param targetDBID : ��������DBID
		@param grade  	  : ����Ҫ���õ�Ȩ��
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
		user����targetȨ��
		@param targetDBID : ��������DBID
		@param scholium	  : ����Ҫ���õ���ע��Ϣ
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
		������ͬ��
		@param requestTongName	:Ҫ�����Ŀ��������
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
		������ͬ��
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
		���ĳ���ͬ�˹�ϵ
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
		�ͻ���������������ð�������
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
		���ð��ְλ������
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
		��Ӧ�ӳ�������
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
			# ����з�������buff
			if len( self.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
				return
			tongMailbox.onAnswer_conjure( self.databaseID )

	#---------------------------------------------------------------------------------------------------------
	def tong_gotoCityWar( self, spaceName ):
		"""
		define method.
		ս������ϵͳѡ���˽���ս����ս���������ս�������ڳ�ս�Լ������ս������������죩����
		@param warlevel:ս�����е����� 1 or 2
		"""
		self.gotoSpace( spaceName, ( 0, 0, 0 ), ( 0, 0, 0 ) )
	
	def tong_leaveCityWar( self ):
		# define method
		# �뿪������ս
		
		enterInfos = self.query( "cityWarEnterInfos" )
		if enterInfos:
			self.gotoSpace( enterInfos[ 0 ], enterInfos[ 1 ], enterInfos[ 2 ] )
			self.remove( "cityWarEnterInfos" )
		else:
			self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )

	def tong_onSetHoldCity( self, city, isInit ):
		"""
		define mothod.
		���ð����Ƶĳ���
		@param city: spaceName
		"""
		self.tong_holdCity = city
		if city and not isInit:
			self.tong_onCityWarMasterOnlineReward()

	def tong_onCityWarOver( self ):
		"""
		define method.
		����ս�������ˣ� ������ڸ������ͳ���
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# �ı�״̬,��Ѫ��ħ
				self.reviveActivity()
			
			self.tong_leaveCityWar()
		
		self.client.tong_onCityWarOver()

	def tong_onCityWarRelive( self, selfEntityID, reliveType ):
		"""
		Exposed method.
		�ڳ�սս������ ����
		@param reliveType: ���ʽ 0��ԭ�ظ�� ��0���سǸ���
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
		# ��ս�����Լ������ս������������죩����
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #ˢ���ٶ�
		self.gotoSpace( spaceName, position, direction )

	def tong_leaveCityWarSpace( self, selfEntityID ):
		"""
		Exposed method.
		��������뿪ս�� ʹ�ô˽ӿ�
		"""
		if self.id != selfEntityID:
			return
		self.tong_leaveCityWar()

	def tong_onCityWarOverReward( self ):
		"""
		define method.
		��ս��������轱��
		702����25+5����ɫ�ȼ�^1.2��, ��ṱ�׶� 50
		"""
		exp = 702 * ( 25 + 5 * pow( self.level, 1.2 ) )
		self.addExp( exp, csdefine.CHANGE_EXP_CITYWAR_OVER )
		#������ṱ�׶�
		self.tong_addContribute( 50 )
	
	def tong_onCityWarMasterOnlineReward( self ):
		# ��������Ա����
		exp = 702 * ( 25 + 5 * pow( self.level, 1.2 ) ) 	# 702����25+5����ɫ�ȼ�^1.2��, ��ṱ�׶� 50
		self.addExp( exp, csdefine.CHANGE_EXP_CITYWAR_MASTER )
		#������ṱ�׶�
		self.tong_addContribute( 50 )
	
	def tong_cityWarSetRewardChampion( self, rewardTime ):
		# define method
		# ������ȡ���ܳ�ս����
		self.set( "tongCityWarChampion", ( rewardTime, False ) )
	
	def tong_cityWarGetChiefReward( self, isCityMaster, winNum ):
		# define method
		# ��ȡ�������⽱��
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
			# �����ռ䲻��
			self.statusMessage( csstatus.CIB_MSG_CANT_OPERATER_FULL )
			return
		
		for item in items:
			self.addItem( item, csdefine.REWARD_TONG_TONG_CITY_WAR )
		
		self.getTongManager().onGetCityTongChiefRewardSuccess( self.tong_dbID )

	def tong_requestQueryCityTongMasters( self, selfEntityID, cityName ):
		"""
		Exposed method.
		����鿴����Ӣ�۰�
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().onQueryCityTong( cityName, self.base )

	def tong_onQueryCityWarTable( self, selfEntityID, cityName ):
		"""
		Exposed method.
		����鿴�������̱� ���� ������
		"""
		if self.id != selfEntityID:
			return
		BigWorld.globalData[ "TongManager" ].onQeryCityWarVersus( cityName, self.base )

	def tong_confirmContest( self, selfEntityID, tonglevel, repMoney ):
		"""
		Exposed method.
		ȷ�ϲμӰ�����ս
		"""
		if self.id != selfEntityID:
			return
		BigWorld.globalData[ "TongManager" ].requestContestCityWar( self.base, self.tong_dbID, self.databaseID, tonglevel, repMoney, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )

	def tong_requestSetCityRevenueRate( self, selfEntityID, rate ):
		"""
		Exposed method.
		������ó�������˰��
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
		������ó�������˰�ʳɹ�
		"""
		revenueRate = BigWorld.globalData[ cityName + ".revenueRate" ]
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CITY_REVENUE, revenueRate )
	
	def tong_queryTongChiefInfos( self ):
		# define method
		# ��ȡ������Ϣ
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
		# ȷ����ȡ���˰��
		self.tong_getSelfTongEntity().onGetCityTongRevenue( self.databaseID )
		
	#----------------------------------��Ὠ��--------------------------------------------------------------

	def tong_onSelectShouShou( self, selfEntityID, shenshouType ):
		"""
		Exposed method.
		�������ѡ������
		"""
		if self.id != selfEntityID:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onSelectShouShou( self.base, self.tong_grade, shenshouType )
	
	#---------------------------------�Ӷ�ս-------------------------------------------------------------------
	def tong_onAnswerRobWar( self, selfEntityID, targetTongName ):
		"""
		Exposed method.
		��������ύҪ�Ӷ�İ��
		"""
		if self.id != selfEntityID:
			return
		if len( targetTongName ) > 0 and self.isJoinTong():
			self.getTongManager().onAnswerRobWar( self.base, self.databaseID, self.tong_dbID, targetTongName )

	def tong_findRequestRobWar( self, selfEntityID, targetTongName ):
		"""
		Exposed method.
		��Ҳ������Ҫ�Ӷ�İ��
		"""
		if self.id != selfEntityID:
			return
		if len( targetTongName ) > 0 and self.isJoinTong():
			self.getTongManager().findRequestRobWar( self.base, targetTongName )

	def tong_isInRobWar( self, tongDBID ):
		"""
		�Ƿ������Ӷ�ս�еĵж԰��
		"""
		return BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ) and self.robWarTargetTong == tongDBID

	def tong_setRobWarTargetTong( self, tongDBID ):
		"""
		define method.
		���ð���Ӷ�ս����
		"""
		self.robWarTargetTong = tongDBID
		self.client.tong_setRobWarTargetTong( tongDBID )

	def tong_onRobWarOver( self, isWin ):
		"""
		define method.
		�Ӷ�ս������
		"""
		#����ÿ��ÿ��ֻ�ܻ�ȡһ���Ӷ�ս���������� by ������ 2010.10.11
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
		self.setRoleRecord( "rewardTongRobWarTime", curT ) #������ȡ����ʱ�� by ������ 2010.10.11

	def tong_rewardRobWar( self, order ):
		"""
		define method.
		�Ӷ�ս������ȡ
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

	#----------------------------------------------��Ἴ��----------------------------------------------------
	
	def tong_updateTongSkills( self, yjy_level ):
		"""
		define method
		���°�Ἴ��
		"""
		canActiveSkills = self.getCanActiveSkills( yjy_level )
		for skillID in canActiveSkills:
			self.updateTongSkill( skillID )

	def updateTongSkill( self, skillID ):
		"""
		���µ�����Ἴ�ܣ�����Ѿ���������£���֮�����
		"""
		skillMap = self.getTongSkillsMap( skillID )
		iterSet =  set( skillMap ) & set( self.attrSkillBox )
		
		if len( iterSet ) > 1:		# ��������£�ĳ�����ܵĿ��������ܱ����ɫ���ϼ��ܵĽ��������һ��ֵ
			ERROR_MSG( " %s: There has some error in updating tong skill, role has %s skills existed!" % ( self.getNameAndID(), iterSet ) )
			return
		
		if len( iterSet ) == 0:		# û�н����������
			self.addSkill( skillID )
			return
		
		oldSkill = iterSet.pop()
		if g_skills[ oldSkill ].getLevel() >= g_skills[ skillID ].getLevel():
			DEBUG_MSG( "%s has learned skill %s , to learn skill is %s" % ( self.getNameAndID(), oldSkill, skillID ) )
			return
		
		self.updateSkill( oldSkill, skillID )

	def getTongSkillsMap( self, skillID ):
		"""
		��ȡĳ���ܶ�Ӧ�����еȼ�����
		"""
		skillsMap = []
		skillDatas = g_tongSkills.getDatas().get( skillID / 1000 * 1000 , None )
		if skillDatas is not None:
			for level,item in skillDatas.iteritems():
				skillsMap.append( item[ "id" ] )
		return skillsMap

	def getCanActiveSkills( self, yjy_level ):
		"""
		��ȡ�����Լ���ļ���
		���������ܶ�Ӧ���о�Ժ�ȼ����ܴ��ڵ�ǰ�о�Ժ�ȼ�
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
		���������ϵİ�Ἴ�ܣ��뿪���ʱ����
		"""
		tongSkillMap = []		# ���а�Ἴ�ܼ���
		for skillID in g_tongSkills.getDatas().keys():
			skillMap = self.getTongSkillsMap( skillID )
			tongSkillMap.extend( skillMap )
		
		learnedTongSkills = set( tongSkillMap ) & set( self.attrSkillBox )
		if len( learnedTongSkills ) == 0:
			return
		for skillID in learnedTongSkills:
			self.removeSkill( skillID )
		self.statusMessage( csstatus.TONG_SKILL_CLEARED )

	#-----------------------------------���---------------------------------------------------------------

	def tong_reuqestCampaignMonsterRaidWindow( self, selfEntityID, npcID, campaignLevel ):
		"""
		Exposed method.
		��������� ħ����Ϯ
		"""
		if self.id != selfEntityID or not BigWorld.entities.has_key( npcID ):
			return
		npc = BigWorld.entities[ npcID ]
		if not self.position.flatDistTo( npc.position ) < csconst.COMMUNICATE_DISTANCE:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.startCampaign_monsterRaid( self.databaseID, campaignLevel )

	#-----------------------------------------����ĳ������----------------------------------------------------------
	def tong_enterTongTerritoryByDBID( self, tongDBID, position, direction ):
		"""
		define method.
		����ָ��DBID�İ�����
		"""
		self.setTemp( "enter_tong_territory_datas", { "enterOtherTong" : tongDBID } )
		self.gotoSpace( "fu_ben_bang_hui_ling_di", position, direction )

	def tong_setLastTongTerritoryDBID( self, tongDBID ):
		"""
		define method.
		�������һ�ν���İ�����DBID
		"""
		self.lastTongTerritoryDBID = tongDBID
		# self.writeToDB()

	# ----------------------------------- ���ֿ� -----------------------------------------------
	def tong_enterStorage( self ):
		"""
		����򿪲ֿ�
		"""
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.enterStorage( self.databaseID )


	def tong_storeItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		�����ֿ���洢��Ʒ�Ľӿڣ���֪Ŀ����Ʒ��

		param srcOrder:	�������Ӻ�
		type srcOrder:	INT16
		param dstOrder:	���ֿ���Ӻ�
		type dstOrder:	INT16
		param entityID:	���npc��id
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
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return

		if kitbagItem.isFrozen():
			WARNING_MSG( "������������" )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "��Ʒ������" )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������." )
			return

		# �ض���Ʒ�ȼ����Ʋ��ܴ���ֿ�
		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.LEVEL_RESTRAIN_ITEM_NOT_TRADE, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return

		if item.isBinded():
			self.statusMessage( csstatus.TONG_STORAGE_CANT_STORE )
			return

		tempItem = item.copy()		# ȡ��һ�ݸɾ�����Ʒ���ݣ����ڰ�������֮ǰ
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			kitbagItem.freeze()			# ������������Ϊ���ֻ������Ʒ�Ļ�����cell����Ʒ���ݷ��͸�base��cell�İ������ܻᱻ����������һЩ����
			tongMailbox.storeItem2Order( srcOrder, tempItem, dstOrder, self.databaseID )


	def tong_storeItem2Bag( self, srcEntityID, srcOrder, bagID, entityID ):
		"""
		Exposed method.
		�洢��Ʒ��ָ���İ���

		@param srcOrder:	�������Ӻ�
		@type srcOrder:	INT16
		@param bagID:	���ֿ����id
		@type bagID:	INT16
		@param entityID:	���npc��id
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
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return

		if kitbagItem.isFrozen():
			WARNING_MSG( "������������" )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "��Ʒ������" )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������." )
			return

		# �ض���Ʒ�ȼ����Ʋ��ܴ���ֿ�
		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.LEVEL_RESTRAIN_ITEM_NOT_TRADE, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return

		if item.isBinded():
			self.statusMessage( csstatus.TONG_STORAGE_CANT_STORE )
			return
		tempItem = item.copy()		# ȡ��һ�ݸɾ�����Ʒ���ݣ����ڰ�������֮ǰ
		kitbagItem.freeze()			# ������������Ϊ���ֻ������Ʒ�Ļ�����cell����Ʒ���ݷ��͸�base��cell�İ������ܻᱻ����������һЩ����
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.storeItem2Bag( srcOrder, tempItem, bagID, self.databaseID )


	def tong_storeItem2Storage( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		�洢��Ʒ�����ֿ�

		param srcOrder:	�������Ӻ�
		type srcOrder:	INT16
		param dstOrder:	���ֿ���Ӻ�
		type dstOrder:	INT16
		param entityID:	���npc��id
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
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return

		if kitbagItem.isFrozen():
			WARNING_MSG( "������������" )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "��Ʒ������" )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������." )
			return

		# �ض���Ʒ�ȼ����Ʋ��ܴ���ֿ�
		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.LEVEL_RESTRAIN_ITEM_NOT_TRADE, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return

		if item.isBinded():
			self.statusMessage( csstatus.TONG_STORAGE_CANT_STORE )
			return
		tempItem = item.copy()		# ȡ��һ�ݸɾ�����Ʒ���ݣ����ڰ�������֮ǰ
		kitbagItem.freeze()			# ������������Ϊ���ֻ������Ʒ�Ļ�����cell����Ʒ���ݷ��͸�base��cell�İ������ܻᱻ����������һЩ����
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.storeItem2Storage( srcOrder, tempItem, self.databaseID )


	def tong_unfreezeBag( self, kitbagNum ):
		"""
		Define method.
		�ṩ��base�Ļ������������б����������Ľӿ�

		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		"""
		if self.kitbags[kitbagNum].isFrozen():
			self.kitbags[kitbagNum].unfreeze()


	def tong_storeItemSuccess01( self, order ):
		"""
		Define method.
		�����ֿ��λ�洢һ����Ʒ�ɹ�����cell������ɾ����Ʒ
		��base��,���������ֿ�洢һ����Ʒ�ɹ��Ļص�����
		"""
		kitbagNum = order / csdefine.KB_MAX_SPACE
		self.kitbags[kitbagNum].unfreeze()
		self.removeItem_( order, reason = csdefine.DELETE_ITEM_TONG_STOREITEM )


	def tong_storeItemSuccess02( self, order, item ):
		"""
		Define method.
		����һ����Ʒ��ʣ�࣬������ֿ�Ŀ����ӽ�����Ʒ����ʣ����Ʒ�򽻻�����Ʒ�Żر���
		��base��,���������ֿ�洢һ����Ʒ�ɹ��Ļص�����
		"""
		kitbagNum = order / csdefine.KB_MAX_SPACE
		self.kitbags[kitbagNum].unfreeze()
		self.removeItem_( order, reason = csdefine.DELETE_ITEM_TONG_STOREITEM )
		if self.addItemByOrderAndNotify_( item, order, reason = csdefine.ADD_ITEM_TONG_STOREITEM ):
			pass
		else:
			# ����˵���ﲻӦ�û������������˿�����BUG
			ERROR_MSG( "���򱳰�������һ������ʱʧ�ܡ�kitTote = %i, kitName = %s, orderID = %i" % ( kitbagNum, self.kitbags[kitbagNum].srcID, order ) )


	def tong_fetchItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		����ϰ��ֿ���Ʒ����Ʒ��ȷ���ı�����Ʒ��

		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param entityID:	���ֿ�npc��id
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
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			kitbag.freeze()
			tongMailbox.fetchItem2Order( srcOrder, dstOrder, self.databaseID  )


	def tong_fetchItem2OrderCB( self, dstOrder, item, srcOrder ):
		"""
		Define method.
		�Ӱ��ֿ�ȡ����Ʒ�Ļص�
		"""
		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE

		kitbagItem = self.kitbags[kitbagNum]
		kitbagItem.unfreeze()

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			if not self.tong_addItem2Order( dstOrder, srcOrder, item, tongMailbox ):	# ���ʧ��
				tongMailbox.unFreezeStorageRemote()
				return


	def tong_fetchItem2Kitbags( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		�Ӱ��ֿ���ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ

		param entityID:	���ֿ�npc��id
		type entityID:	OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		order = self.getNormalKitbagFreeOrder()
		if order == -1:
			DEBUG_MSG( "���(%s)�����޿�λ��" % ( self.getName() ) )
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
		�Ӱ��ֿ���ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ

		@param entityID:	���ֿ�npc��id
		@type entityID:	OBJECT_ID
		@param srcOrder: �ֿ�λ��
		@type srcOrder: int16
		@param amount: ��ȡ��Ʒ����
		@type amount : int16
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		order = self.getNormalKitbagFreeOrder()
		if order == -1:
			DEBUG_MSG( "���(%s)�����޿�λ��" % ( self.getName() ) )
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
		��base��tong_fetchItem2Kitbags���ã���base����������Ʒ���õ�������
		"""
		tongMailbox = self.tong_getSelfTongEntity()

		# ��������
		kitbagNum = self.getNormalKitbagFreeOrder() / csdefine.KB_MAX_SPACE
		self.tong_unfreezeBag( kitbagNum )

		if srcItem.getStackable() > 1:	# �ɵ��ӵ������⴦��
			if self.stackableItem( srcItem, reason = csdefine.ADD_ITEM_TONG_FETCHITEM  ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				tongMailbox.fetchItemSuccess01( srcOrder, self.databaseID )
				try:
					self.questItemAmountChanged( srcItem, srcItem.getAmount() )
				except:
					ERROR_MSG( "���( %s )�Ӱ��ֿ�ȡ��Ʒ�������������������" % self.getName() )
				return
		order = self.getNormalKitbagFreeOrder()		# getNormalKitbagFreeOrder()������itemBagRole.py�У��ڱ����в��ҿ�λ
		if self.addItemByOrderAndNotify_( srcItem, order, reason = csdefine.ADD_ITEM_TONG_FETCHITEM ):
			tongMailbox.fetchItemSuccess01( srcOrder, self.databaseID )

	def tong_fetchSplitItem2KitbagsCB( self, srcOrder, srcItem ):
		"""
		Define method.
		��base��tong_fetchItem2Kitbags���ã���base����������Ʒ���õ�������
		"""
		tongMailbox = self.tong_getSelfTongEntity()

		# ��������
		kitbagNum = self.getNormalKitbagFreeOrder() / csdefine.KB_MAX_SPACE
		self.tong_unfreezeBag( kitbagNum )

		if srcItem.getStackable() > 1:	# �ɵ��ӵ������⴦��
			if self.stackableItem( srcItem, reason = csdefine.ADD_ITEM_TONG_FETCHITEM  ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				tongMailbox.fetchItemSuccess03( srcOrder, srcItem.amount,  self.databaseID )
				try:
					self.questItemAmountChanged( srcItem, srcItem.getAmount() )
				except:
					ERROR_MSG( "���( %s )�Ӱ��ֿ�ȡ��Ʒ�������������������" % self.getName() )
				return
		order = self.getNormalKitbagFreeOrder()		# getNormalKitbagFreeOrder()������itemBagRole.py�У��ڱ����в��ҿ�λ
		if self.addItemByOrderAndNotify_( srcItem, order, reason = csdefine.ADD_ITEM_TONG_FETCHITEM ):
			tongMailbox.fetchItemSuccess03( srcOrder, srcItem.amount,  self.databaseID )

	def tong_moveStorageItem( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		�ƶ����ֿ����Ʒ
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.moveStorageItem( srcOrder, dstOrder, self.databaseID  )


	def tong_addItem2Order( self, dstOrder, tongOrder, srcItem, tongMailbox ):
		"""
		��һ����Ʒ�ŵ�ָ�������ĸ�����,��tong_fetchItem2OrderCB����
		�ɹ��򷵻�true�����򷵻�false

		param kitbag:	����ʵ��
		type kitbag:	KITBAG
		param dstOrder:	���Ӻ�
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

		if srcItem.getStackable() > 1 and dstItem.id == srcItem.id:	# �ɵ��ӵ������⴦��
			overlapAmount = srcItem.getStackable()
			dstAmount = dstItem.getAmount()
			srcAmount = srcItem.getAmount()
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount, self, csdefine.ADD_ITEM_TONG_ADDITEM2ORDER )
			try:
				self.questItemAmountChanged( dstItem, dstItem.getAmount() )
			except:
				ERROR_MSG( "���( %s )�Ӱ��ֿ�ȡ��Ʒ�������������������" % self.getName() )
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# ��Ŀ��λ�õ��Ӻ���ʣ�࣬�Żزֿ�
				srcItem.setAmount( srcAmount )
				tongMailbox.fetchItemSuccess02( tongOrder, srcItem, self.databaseID )
				return True
			else:
				tongMailbox.fetchItemSuccess01( tongOrder, self.databaseID )
				return True
		else:	# id��ͬ�Ĳ��ɵ�����Ʒ �� id��ͬ�Ŀɵ�����Ʒ �ǽ�������
			self.removeItem_( dstOrder, reason = csdefine.DELETE_ITEM_TONG_STOREITEM )
			if self.addItemByOrderAndNotify_( srcItem, dstOrder, csdefine.ADD_ITEM_TONG_ADDITEM2ORDER ):
				self.statusMessage( csstatus.CIB_MSG_GAIN_ITEMS,  srcItem.query( "name" ), srcItem.getAmount() )
				tongMailbox.fetchItemSuccess02( tongOrder, dstItem, self.databaseID )
				return True
		return False


	def _tongStorageOperateVerify( self, srcEntityID, entityID ):
		"""
		��֤�Ƿ��ܹ����а��ֿ����

		@param entityID:����npc��id
		@type entityID: OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return False

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return False
		return True

	def tong_renameStorageBag( self, srcEntityID, bagID, newName, entityID ):
		"""
		Exposed method.

		@param bagID : ����id
		@type bagID : UINT8
		@param newName : ����λ����
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
		���ֿ��Ȩ�޸���
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.changeStorageBagLimit( bagID, officialPos, limitNum, self.databaseID )

	def tong_changeStorageQualityLower( self, srcEntityID, bagID, quality, entityID ):
		"""
		Exposed method.
		�ı���ֿ������Ʒ������

		@param bagID : ����λid
		@type bagID : UINT8
		@param quality : Ʒ��
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
		�ı���ֿ������Ʒ������

		@param bagID : ����λid
		@type bagID : UINT8
		@param quality : Ʒ��
		@type quality : UINT8
		@param entityID : npcID
		@type entityID : OBJECT_ID
		"""
		if not self._tongStorageOperateVerify( srcEntityID, entityID ):
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.changeStorageQualityUp( bagID, quality, self.databaseID )

	#------------------------------------------���װ������-------------------------------------------------------
	def tong_repairOneEquip( self, repairType, kitBagID, orderID ):
		"""
		define method.
		����װ������
		@param    repairType: ��������
		@type     repairType: int
		@param    kitBagID: ��������
		@type     kitBagID: UINT16
		@param    orderID: ��Ʒ����
		@type     orderID: INT32
		@return   ��
		"""
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_REPARE, "" )
			return
		# ��ȡҪ���������װ��
		equip = self.getItem_( orderID )
		if equip == None:
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_EXIST )
			return
		#  �ж�װ���ܷ�����
		if not equip.canRepair():
			self.statusMessage( csstatus.EQUIP_REPAIR_CANT_REPAIR )
			return
		#  �ж�װ���;ö��Ƿ���������
		if equip.getHardiness() == equip.getHardinessLimit():
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_REPAIR )
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.requestRepairOneEquip( repairType, kitBagID, orderID, self.databaseID  )

	def tong_onRepairOneEquipBaseCB( self, repairType, kitBagID, orderID, abate ):
		"""
		define method.
		����װ������
		@param    repairType: ��������
		@type     repairType: int
		@param    kitBagID: ��������
		@type     kitBagID: UINT16
		@param    orderID: ��Ʒ����
		@type     orderID: INT32
		@param abate : �ۿ�
		@param abate : FLOAT
		@return   ��
		"""
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_REPARE, "" )
			return
		# ��ȡҪ���������װ��
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
		������������װ��
		@param    repairType: ��������
		@type     repairType: int
		@return   ��
		"""
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.requestRepairAllEquip( repairType, self.databaseID  )

	def tong_requestRepairAllEquipBaseCB( self, repairType, abate ):
		"""
		define method.
		������������װ��
		@param    repairType: ��������
		@type     repairType: int
		@param abate : �ۿ�
		@param abate : FLOAT
		@return   ��
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

	#-------------------------------��ȡ���ռ���������---------------------------------------------------------

	def tong_getCityTongItem( self ):
		"""
		define method.
		��ȡ����ռ����ľ����ʵ
		"""
		awarder = g_rewards.fetch( csdefine.RCG_TONG_CITY_EXP, self )
		if awarder is None or len( awarder.items ) <= 0:
			self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		item = awarder.items[0]		# ������ֻ��1����Ʒ�����˾�����������
		if item.id == 40401019:
			amount = 0
			for r_item in self.getAllItems():
				if r_item.id == item.id: # Ģ���ı��
					amount += 1
				if amount >= 5:
					self.statusMessage( csstatus.TONG_JYGS_ITEM_MAX )
					return
		awarder.award( self, csdefine.ADD_ITEM_GETCITYTONGITEM )
		self.getTongManager().onGetCityTongItemSuccess( self.databaseID )

	# ---------------------------------------- �������ɽ��븱�� -------------------------------------------------
	def tong_onProtectTongDie( self, selfEntityID ):
		"""
		define method.
		�������ɻ����������
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

	#-----------------------------------------�ͻ��˴򿪰�����----------------------------------------------------------
	def tong_onClientOpenTongWindow( self, selfEntityID ):
		"""
		Expose method.
		�ͻ��˴򿪰����棬 ��Ҫ����һЩ��Ϣ��
		"""
		if self.id != selfEntityID:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onClientOpenTongWindow( self.base )

	#-----------------------------------------����ѯ----------------------------------------------------------
	def tong_setTongAD( self, selfEntityID, tongDBID, strAD ):
		"""
		Expose method.
		���ð����
		@param strAD: �����
		"""
		if self.id != selfEntityID or tongDBID <= 0 or tongDBID != self.tong_dbID or \
			not self.checkDutyRights( csdefine.TONG_RIGHT_SET_AD ):
			return

		self.getTongManager().setTongAD( self.base, tongDBID, strAD )

	def tong_requestTongList( self, selfEntityID, index, camp ):
		"""
		Exposed method.
		ĳ����������ȡ����б�
		@param index: �ͻ�������������������
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().requestTongList( self.base, index, camp )

	def tong_queryTongInfo( self, selfEntityID, tongDBID ):
		"""
		Exposed method.
		��ѯĳ��������Ϣ
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().queryTongInfo( self.base, tongDBID )

	#--------------------------------------------------------------------------------------------------------
	def tong_requestJoinToTong( self, selfEntityID, tongDBID ):
		"""
		Exposed method.
		������뵽ĳ�����
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
		�����ش��Ƿ�Ը�����������
		"""
		if self.id != selfEntityID or not self.isJoinTong():
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.answerJoinToTong( playerDBID, agree )

	def tong_tongListEnterTongTerritory( self, selfEntityID, tongDBID ):
		"""
		Exposed method.
		����ָ��DBID�İ�����
		"""
		if self.id != selfEntityID and tongDBID > 0:
			return
		self.tong_enterTongTerritoryByDBID( tongDBID, ( 0, 0, 0 ), ( 0, 0, 0 ) )

	#--------------------------------------------------------------------------------------------------------
	def isTongChief( self ):
		"""
		�Ƿ����
		"""
		return self.tong_grade == csdefine.TONG_DUTY_CHIEF
	
	def isTongDeputyChief( self ):
		"""
		�Ƿ񸱰���
		"""
		return self.tong_grade == csdefine.TONG_DUTY_DEPUTY_CHIEF

	def checkDutyRights( self, right):
		"""
		���ĳλ�õ�Ȩ��
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
		if len( newName ) > 14:	# ������ƺϷ��Լ��
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
		������ָı�
		"""
		self.statusMessage( csstatus.TONG_RENAME_SUCCESS, self.tongName, newTongName )
		self.tongName = newTongName

	#--------------------------------------------------------------------------------------------------------
	def tong_contributeToMoney( self, srcEntityID, money ):
		"""
		Exposed method.
		������׽�Ǯ�����
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
		���׽�Ǯ�ɹ�
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
		�뿪���Ĵ���
		"""
		tongBase = self.tong_getSelfTongEntity()
		if tongBase:
			tongBase.memberLeave( self.databaseID )
		self.base.tong_leave()
		self.tong_reset()
		self.tong_onChanged()
		self.tong_clearTongSkills()
		self.writeToDB()

	# ------------------------- �����̨����� ------------------------------
	def tong_dlgAbattoirRequest( self ):
		"""
		����npc��������̨��
		"""
		if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_ABA ): # Ȩ���ж�
			self.statusMessage( csstatus.TONG_ABATTOIR_NOT_LEADER )
			return
		self.tong_getSelfTongEntity().requestAbattoir( self.base )

	def tong_onInTongAbaRelivePoint( self, srcEntityID, index ):
		"""
		Exposed method.
		�����̨��������
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
			# ��������ص��� ��Ҫ���ڸ��������� ��ɫδ��� ������ʩ���޵�BUFF�� �Ƚ�ɫ����� �ᴦ���ޱ���״̬�� ����
			# �ص��������� ������������¼���
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
		�����̨�������ˣ�������ڸ������ͳ���
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_TONG_ABA:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )
				# �ı�״̬,��Ѫ��ħ
				self.changeState( csdefine.ENTITY_STATE_FREE )
				self.setHP( self.HP_Max )
				self.setMP( self.MP_Max )
			else:
				self.gotoForetime()

	def tong_chooseAbaRelivePoint( self, selfEntityID, index ):
		"""
		Exposed method.
		�����ս����ѡ���˸����λ��
		@param index : 3�����������һ������ 0, 1, 2
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
			# ��������ص��� ��Ҫ���ڸ��������� ��ɫδ��� ������ʩ���޵�BUFF�� �Ƚ�ɫ����� �ᴦ���ޱ���״̬�� ����
			# �ص��������� ������������¼���
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
		������ս��������ϵ�ս����Ʒ
		"""
		dropItems = []
		for item in self.getAllItems():
			if str( item.id )[ 0 : 3 ] == "403": # ȡǰ3λ�ж��Ƿ���ս������Ʒ
				dropItems.append( item )
		for item in dropItems:
			self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_CLEARWARITEMS )

	def tong_AbaItemsDropOnDied( self ):
		"""
		�Լ��ڰ��ս�������� �������ս����Ʒ
		"""
		pos = self.position
		dropItems = []

		for item in self.getAllItems():
			if str( item.id )[ 0 : 3 ] == "403": # ȡǰ3Ϊ�ж��Ƿ���ս������Ʒ
				dropItems.append( item )

		# ��ʼ�ڵ�ͼ�ϰڷ�
		for item in dropItems:
			x1 = random.random() * 4 - 2
			z1 = random.random() * 4 - 2
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# ��������õ�λ��
			g_items.createEntity( item.id, self.spaceID, (x, y, z), self.direction, { "itemProp" : item } )
			self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_ABAITEMSDROPONDIED )

	def tong_leaveWarSpace( self, selfEntityID ):
		"""
		Exposed method.
		���Ҫ����ս��
		"""
		if selfEntityID != self.id:
			return
		if self.getState() == csdefine.ENTITY_STATE_FREE:
			self.gotoForetime()

	def sendTongFaction( self, tongFaction ):
		"""
		define method
		���ܰ��ʱװ����
		"""
		self.factionCount = tongFaction

	def tong_competitionRequest( self, talkEntity ):
		"""
		��npc���뱨����Ὰ��
		"""
		if not self.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_COMPETITION ): # Ȩ���ж�
			self.statusMessage( csstatus.TONG_COMPETETION_TONG_REQUIRED )
			return
		self.tong_getSelfTongEntity().requestCompetition( self.base )
	
	#----------------------------���ٺ»���------------------------------------------------
	def tong_onDrawTongSalary( self, selfEntityID ):
		"""
		Exposed method
		��ȡ���ٺ»
		"""
		#if selfEntityID != self.id:
		#	return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onDrawTongSalary( self.databaseID )
		
	def tong_onSalaryExchangeRate( self, selfEntityID, rate ):
		"""
		Exposed method
		�����趨ÿ��ﹱ�һ���
		"""
		if selfEntityID != self.id:
			return
		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.setContributeExchangeRate(  self.databaseID, rate )		
			
	def tong_onClientOpenTongMoneyWindow(  self, selfEntityID ):
		"""
		Exposed method
		�򿪰���ʽ����,��ѯ����ʽ��ٺ»�����Ϣ
		"""
		if self.id != selfEntityID:
			return

		tongMailbox = self.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onClientOpenTongMoneyWindow( self.base )

	def tong_onAbandonTongCity( self, selfEntityID, city ):
		"""
		Exposed method
		����ռ�����
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
		�����ս������������죩�����ˣ� ������ڸ������ͳ���
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN:
			if self.state == csdefine.ENTITY_STATE_DEAD:
				# �ı�״̬,��Ѫ��ħ
				self.reviveActivity()
			
		
		self.client.tong_onFengHuoLianTianOver()

	def tong_leaveFengHuoLianTian( self ):
		# define method
		# �뿪�����ս������������죩
		
		enterInfos = self.query( "TongFengHuoLianTianEnterInfos" )
		if enterInfos:
			self.gotoSpace( enterInfos[ 0 ], enterInfos[ 1 ], enterInfos[ 2 ] )
			self.remove( "TongFengHuoLianTianEnterInfos" )
		else:
			self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )
			
	def tong_onQueryFHLTTable( self, selfEntityID, cityName ):
		"""
		Exposed method.
		����鿴�������̱� ���� ������
		"""
		if self.id != selfEntityID:
			return
		BigWorld.globalData[ "TongManager" ].onQeryFHLTVersus( cityName, self.base )

	#---------------------------------------------����������-------------------------------------------
	def onDartQuestStatusChange( self, isOpen ):
		"""
		define method
		�������������״̬�ı�
		
		@param isOpen: TrueΪ������FalseΪ�ر�
		@type isOpen: BOOL
		"""
		self.tongDartQuestIsOpen = isOpen
		self.client.onDartQuestStatusChange( isOpen )
		
	def onNormalQuestStatusChange( self, openType ):
		"""
		define method
		����ճ�������״̬�ı�
		
		@param openType: �������ͣ�Ϊ0��ʾ�ر�
		@type openType: UINT8
		"""
		self.tongNormalQuestOpenType = openType
		self.client.onNormalQuestStatusChange( openType )

	#---------------------------------------------ս������-------------------------------------------
	
	def tong_requestBattleLeagues( self, selfEntityID, index, camp ):
		"""
		Exposed method
		��ѯ���ս��������Ϣ
		"""
		if self.id != selfEntityID:
			return
		self.getTongManager().queryTongBattleLeagues( self.base, index, camp, self.spaceType )
	
	def tong_inviteTongBattleLeagues( self, selfEntityID, inviteeTongDBID, msg ):
		"""
		Exposed method
		����ս������
		@param tongDBID :Ҫ�������DBID
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
		�ظ�ս����������
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
		���ս��ͬ�˹�ϵ
		"""
		if srcEntityID != self.id:
			return

		DEBUG_MSG( "TONG: %i dispose to tong %i of league." % ( self.tong_dbID, battleLeagueDBID ) )
		self.getTongManager().requestBattleLeagueDispose( self.databaseID, self.base, self.tong_dbID, battleLeagueDBID )

	def tong_onCityWarFinalReliveCB( self, pos, dir, space, spaceID ):
		"""
		define method
		�����ս��������ص�
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )
		self.updateTopSpeed() #ˢ���ٶ�
		self.teleportToSpace( pos, dir, space, spaceID )

# $Log: not supported by cvs2svn $
# Revision 1.10  2008/08/12 08:51:48  kebiao
# ��Ӱ����������
#
# Revision 1.9  2008/07/22 01:58:59  huangdong
# ���ư�������
#
# Revision 1.8  2008/06/30 04:15:09  kebiao
# ���Ӱ��ְλ���Ʊ༭
#
# Revision 1.7  2008/06/27 07:12:15  kebiao
# �����˰��ͼ�����첽���ݴ������
#
# Revision 1.6  2008/06/23 08:12:28  kebiao
# no message
#
# Revision 1.5  2008/06/21 03:42:36  kebiao
# �����ṱ�׶�
#
# Revision 1.4  2008/06/16 09:14:14  kebiao
# base �ϲ��ֱ�¶�ӿ�ת�Ƶ�cell
#
# Revision 1.3  2008/06/14 09:18:26  kebiao
# ������Ṧ��
#
# Revision 1.2  2008/06/10 01:55:02  kebiao
# add:tong_reset
#
# Revision 1.1  2008/06/09 09:24:13  kebiao
# ���������
#
# Revision 1.6  2008/05/22 03:47:57  kebiao
# fix condition bug
#
# Revision 1.5  2008/05/15 07:04:58  kebiao
# ���Ȩ���ϵ
#
# Revision 1.4  2008/05/14 02:54:36  kebiao
# ����������ȹ���
#
# Revision 1.3  2008/05/09 08:26:13  kebiao
# �����Ϣ��ʾ �ӿ�ע��
#
# Revision 1.2  2008/05/09 03:16:21  kebiao
# ��1�׶ο�ܴ������
#
# Revision 1.1  2008/05/06 09:02:17  kebiao
# no message
#
#