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

tongSignMap = {}						# ��̬�İ�����б����ڹ������еĽ�ɫ����� by ����

class MemberInfos:
	"""
	�����г�Ա��һЩ��Ϣ�ṹ
	"""
	def __init__( self ):
		"""
		��ʼ����Ա��Ϣ
		"""
		self._memberDBID = 0
		self._isOnline = False					# �ó�Ա�Ƿ�����
		self._name = ""							# �ó�Ա������
		self._grade = 0							# �ó�Ա�İ��Ȩ��
		self._class = 0							# �ó�Ա��ְҵ
		self._level = 0							# �ó�Ա�ļ���
		self._spaceType = ""					# �ó�Ա����spaceλ��
		self._lastPosition = ( 0, 0, 0 )		# �ó�Ա���һ�β�ѯ����λ��
		self._scholium = ''						# �ó�Ա����ע
		self._contribute = 0					# �ó�Ա��ṱ�׶�
		self._totalContribute = 0				# �ó�Ա����ۻ����׶�
		self.tong_storage_npcID = 0				# ��¼���ֿ�npcID by����

		self._lastWeekTotalContribute = 0		# �ó�Ա���ܰ���ۼưﹱֵ
		self._lastWeekSalaryReceived = 0		# �ó�Ա������ȡٺ»ֵ
		self._weekTongContribute = 0 			# �ó�Ա���ܻ�ȡ�ﹱֵ
		self._weekSalaryReceived = 0			# �ó�Ա������ȡٺ»ֵ
		self._lastWeekTotalContribute = 0		# �ó�Ա���ܻ�ȡ�ﹱ

	def init( self, memberDBID, name, grade, eclass, level, scholium ):
		"""
		��ʽ�ĳ�ʼ����������
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
		��������״̬
		@param online: bool, ���߻��߲�����
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
		�ۼưﹱ��ֵ��ʣ��ﹱֵ�����ܻ�ðﹱ�����ܻ�ðﹱ
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
		self.tong_leagues = {} #���ͬ��
		self.tong_isRequestDataEnd = False
		self.robWarTargetTong = 0
		self.tong_dutyNames = {}
		self.tong_ck_requestItemCount = 0	# ���ֿ���Ʒ�����������
		self.tong_ck_requestLogCount = 0	# ���ֿ�log��Ϣ�������
		self.tong_storageLog = []			# ���ֿ��log����
		self.storageBagPopedom = []		# ���ֿ��������array of TONG_STORAGE_POPEDOM
		self.fetchRecord = None
		self.tongMoney = 0
		self.tongLevel = 0
		self.tongQueryTongListIndex = 0
		self.TongListInfos = {}
		self.tong_buildDatas = {} 			# ��Ὠ����Ϣ
		self.applyMsgBox = None
		self.__isInCityWar = False				# �Ƿ��ڳ�ս�����
		self.cityWarPointLogs = {}				# ��ս��������
		self.tongInfos = {}						# ����˫����Ϣ
		self.rightTongDBID = self.tong_dbID					# ���ذ��dbID��Ĭ��Ϊ�Լ����
		self.tong_sign_md5 = None					# �ó�Ա�����MD5 by����
		self.tong_sign_searching_list = {}			# ��¼�����������ݵİ��ID����ֹ�ظ����� by����
		self.tong_sign_searcher_list = {}			# ��¼��������Ķ���entity����Ҫ����ң���������ȷ��ʾ��� by ����
		self.submitting = False						# �Ƿ������ϴ��� by ����
		self.tong_prestige = 0					#�������
		self.variable_prestige = 0				#��������
		self.tong_territoriesNPCs = {}		# �����ص�NPC���������������ص�NPC��
		self.tongExp = 0					# ��ᾭ��
		self.tong_totalSignInRecord = 0		# �ó�Աǩ������
		self.tong_battleLeagues = {}		# ���ս��ͬ��
		self.tong_quarterFinalRecord = {}	# �����ս��������
		self.tongQueryBattleLeagueIndex = 0 

		# ���������ļ�¼��Ϊ��ֹɧ�ţ���ͬһ�������������Ҫ���20���ӡ�
		# like as: { tongDBID:time, ... }
		self.tongRequestInfo = {}


	def tong_reset( self ):
		self.tong_memberInfos = {}
		self.tong_leagues = {} #���ͬ��
		self.tong_isRequestDataEnd = True
		self.tong_ck_requestItemCount = 0	# ���ֿ���Ʒ�����������
		self.tong_ck_requestLogCount = 0	# ���ֿ�log��Ϣ�������
		self.tong_storageLog = []			# ���ֿ��log����
		self.storageBagPopedom = []		# ���ֿ��������array of TONG_STORAGE_POPEDOM
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
		��ᴴ���ɹ�֪ͨ
		"""
		self.statusMessage( csstatus.TONG_CREATE_SUCCESS, tongName )
		self.tong_requestDatas()
		rds.helper.courseHelper.tongFamilyTrigger( "jianlibanghui" )		# ��һ�ν��������ʱ���������̰�����ʾ��hyw--2009.06.13��

	def tong_onReceiveData( self ):
		"""
		define method.
		�յ�������֪ͨ ���µ����ݿ��Ի�ȡ��
		"""
		if self.tong_isRequestDataEnd:
			self.tong_isRequestDataEnd = False
			self.tong_requestDatas()

	def tong_requestDatas( self ):
		"""
		ȥ���������ð������
		"""
		requestDatas( self.id )

	def onEndInitialized( self ) :
		"""
		��ɫ��ʼ������������
		"""
		if not self.isJoinTong():
			self.tong_isRequestDataEnd = True
			return
		self.tong_requestDatas()

	def tong_onRequestDatasCallBack( self ):
		"""
		define method.
		�յ����������ݷ�����ϵ�֪ͨ
		"""
		self.tong_isRequestDataEnd = True

	#--------------------------------------------------------------------------------------------------------

	def tong_setLeague( self, tongDBID, tongName ):
		"""
		define method.
		����ͬ�˰��
		"""
		self.tong_leagues[tongDBID] = tongName
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_LEAGUE" )
#		self.chat_say( "���ͬ��:%s" % tongName )

	def tong_addLeague( self, tongDBID, tongName ):
		"""
		define method.
		�¼���ͬ�˰��
		"""
		self.tong_leagues[tongDBID] = tongName
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_ADD_LEAGUE", tongDBID )
		self.statusMessage( csstatus.TONG_LEAGUE_SUCCESS, tongName )

	def tong_delLeague( self, tongDBID ):
		"""
		define method.
		�����ĳͬ�˰��
		"""
		if self.tong_leagues.has_key( tongDBID ):
			del self.tong_leagues[tongDBID]
			ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_DEL_LEAGUE", tongDBID )
#		self.chat_say( "������ͬ��:%s" % tongName )

	#--------------------------------------------------------------------------------------------------------

	def tong_onSetMemberInfo( self, memberDBID, memberName, memberLevel, \
							memberClass, memberTongGrade, memberTongScholium, memberTongContribute, memberTongTotalContribute, online ):
		"""
		define method.
		���������ÿͻ��˰���Ա��Ϣ
		"""
		# ����facade���� ʹ�õ�ǰ�����ĵ�ַ�� ���Լ��ٺ����ܶ�Ĳ������Ч��
		if not GUIFacade.tong_hasSetMemberInfo():
			GUIFacade.tong_setMemberInfo( self.tong_memberInfos )

		info = MemberInfos()
		info.init( memberDBID, memberName, memberTongGrade, memberClass, memberLevel, memberTongScholium )
		info.setOnlineState( online )
		info.setContribute( memberTongContribute )
		info.updateTotalContribute( memberTongTotalContribute )
		self.tong_memberInfos[ memberDBID ] = info
		GUIFacade.tong_onSetMemberInfo( 0, 0, memberDBID )	# ȡ�����壬�����滹û�޸ģ���ʱ0��ʾfamilyDBID��familyGrade��15:36 2010-11-11��wsf

	def tong_onDeleteMemberInfo( self, memberDBID ):
		"""
		define method.
		������ɾ���ͻ��˰���Ա��Ϣ
		"""
		info = self.tong_memberInfos[ memberDBID ]
		name = info.getName()
		self.tong_memberInfos.pop( memberDBID )
		self.statusMessage( csstatus.TONG_MEMBER_QUIT, name )
		GUIFacade.tong_onRemoveMember( memberDBID )

	#--------------------------------------------------------------------------------------------------------
	def tong_kickMember( self, memberDBID ):
		"""
		��ĳ��Ա�����
		"""
		self.cell.tong_kickMember( memberDBID )

	#--------------------------------------------------------------------------------------------------------
	def tong_quit( self ):
		"""
		�˳����tong
		"""
		if self.tong_grade == csdefine.TONG_DUTY_CHIEF:
			self.statusMessage( csstatus.TONG_CHIEF_QUIT )
			return
		self.cell.tong_quit()

	def tong_meQuit( self ):
		"""
		define method.
		�Լ��뿪�˰�ᣬ �����������˳����߼����˳�������ɵġ�
		"""
		self.tong_reset()
		self.statusMessage( csstatus.TONG_MEMBER_QUIT_ME )

	def tong_onDismissTong( self ):
		"""
		����ɢ
		"""
		self.tong_reset()
		self.statusMessage( csstatus.TONG_DISMISS )

	#--------------------------------------------------------------------------------------------------------

	def tong_abdication( self, memberDBID ):
		"""
		������λ
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
		�����°�����
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
				if val > 0:							# ����Ǯ��
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
		if self.tong_dbID > 0 and iconMD5 != "tcbh":		# ����ԭ�����˳���ᣬtcbh��Ϊʶ����
			tongSignMap[self.tong_dbID] = iconMD5
			self.tong_sign_md5 = iconMD5
		self.initTongSign()		# ��ʼ���Լ��İ����

	def tong_getCanUseMoney( self ):
		"""
		����������ʽ�,������Ҫ��ʾ�������ʽ�Ľ���Ͳ���Ҫ����������
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
		���������ÿͻ��˰������
		@param prestige: ��������
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
		���������ð�������ɺ��״̬�� ���θ�¶���ǻԸ�¶���չ��¶֮һ ��
		"""
		#״̬�����csdefine
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_WEEKSTATE", val )

	def tong_onSetVariablePrestige( self, val ):
		"""
		defined method
		���������ð���������
		"""
		self.variable_prestige = val
		DEBUG_MSG( "Current variable prestige: %s"%val )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_VARIABLE_PRESTIAGE", val )

	def tong_setAffiche( self, affiche ):
		"""
		�ͻ������÷������ϵĹ���
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
		���������ÿͻ��˰�ṫ��
		"""
		GUIFacade.tong_onSetAffiche( affiche )

	def tong_onMemberOnlineStateChanged( self, memberDBID, onlineState ):
		"""
		define method.
		ĳ��Ա������״̬�ı���
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
		ĳ��Ա�ļ���ı���
		"""
		self.tong_memberInfos[ memberDBID ].setLevel( level )
		GUIFacade.tong_onMemberLevelChanged( memberDBID, level )

	def tong_onMemberNameChanged( self, memberDBID, name ):
		"""
		define method.
		ĳ��Ա�����ָı���
		"""
		self.tong_memberInfos[ memberDBID ].setName( name )
		GUIFacade.tong_onMemberNameChanged( memberDBID, name )

	def tong_onMemberContributeChanged( self, memberDBID, contribute, totalContribute ):
		"""
		define method.
		ĳ��Ա�Ĺ��׶ȸı���
		"""
		if self.databaseID == memberDBID:		# ������Լ��Ĺ��׶ȱ仯
			oldContribut = self.tong_memberInfos[ memberDBID ].getContribute()
			dispersion = contribute - oldContribut
			if dispersion > 0:
				self.statistic["statTongContribute"] += dispersion

		self.tong_memberInfos[ memberDBID ].setContribute( contribute )
		self.tong_memberInfos[ memberDBID ].updateTotalContribute( totalContribute )
		GUIFacade.tong_onMemberContributeChanged( memberDBID, contribute, totalContribute )

	def tong_setMemberScholium( self, memberDBID, scholium ): #
		"""
		�ͻ������������������ĳ��Ա����ע
		"""
		if len( scholium ) <= csdefine.TONG_MEMBER_SCHOLIUM_LENGTH_MAX:
			self.cell.tong_setMemberScholium( memberDBID, scholium )
		else:
			self.statusMessage( csstatus.TONG_SET_STRING_LENGTH_MAX, csdefine.TONG_MEMBER_SCHOLIUM_LENGTH_MAX )

	def tong_onMemberScholiumChanged( self, memberDBID, scholium ):
		"""
		define method.
		ĳ��Ա����ע�ı���
		"""
		self.tong_memberInfos[ memberDBID ].setScholium( scholium )
		GUIFacade.tong_onMemberScholiumChanged( memberDBID, scholium )

	def tong_updateMemberMapInfo( self, memberDBID, spaceType, position, lineNumber ):
		"""
		define method.
		���������¿ͻ��˳�Ա���ڵ�ͼ��Ϣ
		"""
		if self.tong_memberInfos.has_key( memberDBID ):
			memInfo = self.tong_memberInfos[ memberDBID ]
			memInfo.setPosition( position )
			memInfo.setSpaceType( spaceType )
			GUIFacade.tong_updateMemberMapInfo( memberDBID, spaceType, position, lineNumber )

	def tong_onSetTongExp( self, exp ):
		"""
		define method.
		���������ÿͻ��˰������
		@param prestige: ��������
		@type  prestige: int32
		"""
		self.tongExp = exp
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_EXP", exp )

	#--------------------------------------------------------------------------------------------------------

	def tong_setMemberGrade( self, targetDBID, grade ):
		"""
		����ĳ��Ա��Ȩ��
		"""
		if self.tong_grade <= 0 or self.tong_dbID <= 0:
			self.statusMessage( csstatus.TONG_NO_TONG )
			return
		self.cell.tong_setMemberGrade( targetDBID, grade )

	def tong_onMemberGradeChanged( self, userDBID, memberDBID, memberGrade ):
		"""
		define method.
		ĳ��Ա��Ȩ�޸ı���
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
		#������ �������������NPC����״̬�������� by ����
		for key, entity in BigWorld.entities.items():
			if hasattr( entity, "refurbishQuestStatus" ):
				entity.refurbishQuestStatus()

	#---------------------------------------------------------------------------------------------------------
	def tong_requestJoinByPlayerName( self, playerName ):
		"""
		����ĳ�˼���tong ͨ������
		@param playerName: Ҫ������˵�����
		"""
		if self.tong_grade <= 0 or self.tong_dbID <= 0:
			self.statusMessage( csstatus.TONG_NO_TONG )
			return
		self.statusMessage( csstatus.TONG_NEW_MEMBER_REQUEST, playerName )
		self.base.tong_requestJoinByPlayerName( playerName )

	def tong_requestJoin( self, tergetEntityID ):
		"""
		����ĳ�˼���tong ���ؽӿ�
		@param tergetEntityID: Ҫ������˵�ID
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
		�յ����������
		@param requestEntityName: ����������
		@oaram tongDBID			: tong��dbid, ����������ʱ����Ҫ�õ�
		"""
		GUIFacade.tong_onReceiveRequestJoinMessage( requestEntityName,tongName, chiefName,\
		 tongLevel, memberCount )
		GUIFacade.tong_onReceiveRequestJoin( requestEntityName, tongDBID, tongName,chiefName,\
		tongLevel, memberCount )

	def tong_answerRequestJoin( self, agree, tongDBID ):
		"""
		������� �����ش�
		@param agree			: bool, true = ����
		@oaram tongDBID		: ���ĵ�dbid
		"""
		self.cell.tong_answerRequestJoin( agree, tongDBID )

	#---------------------------------------------------------------------------------------------------------

	def tong_requestTongLeague( self, requestTongName ):
		"""
		����ĳ����Ϊͬ��
		@param requestTongName	:Ҫ�����Ŀ��������
		"""
		if len( requestTongName ) <= 0:
			return
		self.cell.tong_requestTongLeague( requestTongName )

	def tong_onRequestTongLeague( self, requestByTongName, requestByTongDBID ):
		"""
		define method.
		�յ������������ͬ��
		"""
		GUIFacade.tong_onRequestTongLeague( requestByTongName, requestByTongDBID )

	def tong_answerRequestTongLeague( self, agree, requestByTongDBID ):
		"""
		��Ӧ�������Ƿ�Ը���Ϊͬ�ˡ�
		"""
		self.cell.tong_answerRequestTongLeague( agree, requestByTongDBID )

	def tong_leagueDispose( self, leagueTongDBID ):
		"""
		���ĳ���ͬ�˹�ϵ
		"""
		self.cell.tong_leagueDispose( leagueTongDBID )

	#---------------------------------------------------------------------------------------------------------
	def tong_initDutyName( self, duty, dutyName ):
		"""
		define method.
		���ְλ������
		"""
		self.tong_dutyNames[ duty ] = dutyName
		GUIFacade.tong_initDutyName( duty, dutyName )

	def tong_setDutyName( self, duty, newName ):
		"""
		���ð��ְλ������
		"""
		BigWorld.player().cell.tong_setDutyName( duty, newName )

	def tong_onDutyNameChanged( self, duty, newName ):
		"""
		define method.
		���ð��ְλ������
		"""
		self.tong_dutyNames[ duty ] = newName
		GUIFacade.tong_onDutyNameChanged( duty, newName )

	def tong_enterFound( self, objectID ):
		"""
		Define Method
		��npc�Ի������󴴽����
		@param   objectID: �Ի�Ŀ��
		@type    objectID: OBJECT_ID
		@return: ��
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
		�յ��ӳ������� ���ȷ����ʹ��tong_onAnswerConjure��Ӧ��û��ȷ�������κ�����
		"""
		GUIFacade.tong_onChiefConjure()

	def isJoinTong( self ):
		"""
		�ж�����Ƿ������
		tong_grade ��Ϊ0 ��ʾ���һ�������˰��
		"""
		return self.tong_dbID > 0

	def tong_checkDutyRights( self, duty, right ):
		"""
		�����Ȩ��
		"""
		if duty not in csdefine.TONG_DUTY_RIGHTS_MAPPING.keys():	# �ж�ְλ�Ƿ����
			return False
		
		if right not in csdefine.TONG_DUTY_RIGHTS_MAPPING[ duty ]:	# �ж�Ȩ���Ƿ����
			return False
		
		return True
	#--------------------------------------------������ս��--------------------------------------------------
	def set_tong_holdCity( self, oldValue ):
		"""
		define mothod.
		���ð����Ƶĳ���
		@param city: spaceName
		"""
		GUIFacade.onSetHoldCity( self, self.tong_holdCity )

	def tong_onCityWarDie( self ):
		"""
		��ս������ ��������Ի���
		��ԭ�ظ���ͻسǸ��� ���سǸ���ػص���ظ��
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )

	def tong_onCityWarRelive( self, reliveType ):
		"""
		������Ҫ����Ƿ��� ������������ԭ�ظ���
		@param reliveType: ���ʽ 0��ԭ�ظ�� ��0���سǸ���
		"""
		self.cell.tong_onCityWarRelive( reliveType )

	def tong_leaveCityWarSpace( self ):
		"""
		�������ս��
		��������뿪ս�� ʹ�ô˽ӿ�
		"""
		BigWorld.player().cell.tong_leaveCityWarSpace()

	def tong_onUpdateWarReportTop( self, playerName, tongDBID, killCount, deadCount ):
		"""
		define method.
		���¸�������ҿͻ���ս����������Ϣ
		"""
		pass
#		ECenter.fireEvent( "EVT_ON_UPDTAE_WAR_REPORT", playerName, tongDBID, killCount, deadCount )

	def tong_onCityWarReport( self, tongDBID,  playerName, kill, dead, isInWar ):
		"""
		define method.
		���¸�������ҿͻ���ս����������Ϣ
		"""
		ECenter.fireEvent( "EVT_ON_UPDTAE_WAR_REPORT", playerName, tongDBID, kill, dead, isInWar )

	def tong_onEnterCityWarSpace( self, warRemainTime, tongInfos ):
		"""
		define method.
		��ҽ������ս���������֪ͨ, Ŀǰû��ʲô��������� �������ܻ��ʼ��һЩ����
		"""
		self.tongInfos = tongInfos 
		# tongInfos :{"left":����DBID, "leftTongName": ��������, "right" : �Ұ��DBID, "rightTongName" : �Ұ������, "defend":���ط�DBID, "defendTongName":���ط�������� }
		self.__isInCityWar = True
		ECenter.fireEvent( "EVT_ON_ENTER_CITYWAR_SPACE", warRemainTime, tongInfos )
		ECenter.fireEvent( "EVT_ON_ENTER_CITYWAR_SPACE_ROLE_NAME", self )

	def tong_onLeaveCityWarSpace( self ):
		"""
		define method.
		����뿪����ս���������֪ͨ, Ŀǰû��ʲô��������� �������ܻ����һЩ����
		"""
		self.__isInCityWar = False
		self.rightTongDBID = self.tong_dbID
		ECenter.fireEvent( "EVT_ON_ROLE_LEAVE_CITYWAR_SPACE",self )
	
	def tong_onCityWarOver( self ):
		# define method
		# ��ս����
		ECenter.fireEvent( "EVT_ON_TONG_CITYWAR_OVER" )

	def tong_openQueryCityWarInfoWindow( self, type ):
		"""
		define method.
		�򿪲鿴��ս�����Ϣ����
		"""
		ECenter.fireEvent( "EVT_ON_OPEN_CITYWAR_INFO_WND", type )

	def tong_onQueryCityWarTable( self, datas ):
		"""
		define method.
		��ս ���̲鿴
		"""
		DEBUG_MSG( "--->>>", datas )
		ECenter.fireEvent( "EVT_ON_RECIEVE_CITYWAR_TABLE", datas )

	def tong_onQueryContest( self, reqLevel, reqMoney ):
		"""
		�������ս�����ص�
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				self.cell.tong_confirmContest( reqLevel, reqMoney )
		moneyText = utils.currencyToViewText( reqMoney )
		showMessage( mbmsgs[0x0c43] % moneyText, "", MB_OK_CANCEL, query )

	def tong_requestQueryCityTongMasters( self, cityName ):
		"""
		����鿴����Ӣ�۰�
		"""
		self.cell.tong_requestQueryCityTongMasters( cityName )
		

	def tong_onQueryCityTongMasters( self, index, tongName, date, chiefName ):
		"""
		define method.
		�鿴����Ӣ�۰�
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
		�Ƿ��ǳ�ս����Ա
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
		����������ó�������˰  �򿪽���
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_CITY_TAXRATE", rate )

	def tong_requestSetCityRevenueRate( self, rate ):
		"""
		����������ó�������˰ ֪ͨ������
		"""
		self.cell.tong_requestSetCityRevenueRate( rate )

	def tong_onUpdateCityWarPoint( self, tongDBID, point ):
		"""
		define method.
		�������������ĵ�ǰĳ����ս������
		"""
#		DEBUG_MSG( "current:%d, %d" % (tongDBID, point) )
		ECenter.fireEvent( "EVT_ON_UPDATE_CITYWAR_POINTS", tongDBID, point )
		self.cityWarPointLogs[ tongDBID ] = point
	
	def tong_onRequestCityTongRevenue( self, money ):
		# define method
		# ������ȡ����˰�ջص�
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.tong_onRequestCityTongRevenue()
				
		showMessage( mbmsgs[0x0c44] % ( money / 10000 ), "", MB_YES_NO, result )
	
	def tong_onAbandonTongCityNotify( self, city ):
		"""
		����ռ����еĻص�
		"""
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.tong_onAbandonTongCity( city )
		cityNameCN = csconst.TONG_CITYWAR_CITY_MAPS.get( city, "" )
		showMessage( mbmsgs[0x0c45] %cityNameCN, "", MB_YES_NO, result )

	#---------------------------------------------��Ὠ��---------------------------------------------
	def tong_onReceiveTongBuildInfo( self, buildData ):
		"""
		define method.
		���շ��������İ�Ὠ����Ϣ
		ͨ�� cell.tong_onGetBuildInfo ��ȡ
		@param buildingType:�������
		@param data: �������� �鿴 def -> TONGBUILDINFO
		"""
		if buildData is None:return
		type = buildData["type"]
		self.tong_buildDatas[type] = buildData
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_BUILD_INFO", buildData )

	def tong_openBuildingWindow( self, buildingType ):
		"""
		define method.
		������֪ͨ�򿪽�������
		@param buildingType: csdefine.TONG_BUILDING_TYPE_**
		"""
		#if self.tong_grade&( csdefine.TONG_GRADES &~ csdefine.TONG_GRADE_BUILDING ) > 0:return
		# �򿪽���� ֱ�ӵ���
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_BUILDS_RESEARCH", buildingType )

	def tong_onSetShenShouType( self, shenshouLevel, shenshouType ):
		"""
		define method.
		���������ÿͻ������޼��������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_SHENSHOU_INFO", shenshouLevel, shenshouType )

	def tong_openShenShouSelectWindow( self, shenshouLevel, shenshouType ):
		"""
		define method.
		������֪ͨ������ѡ�����
		csdefine.TONG_SHENSHOU_TYPE_*
		"""
		if not self.tong_checkDutyRights( self.tong_grade, csdefine.TONG_RIGHT_PET_SELECT ):
			return
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SHENSHOU_BRECKON", shenshouLevel, shenshouType )
		# �򿪽���� ֱ�ӵ���
	
	def tong_onPauseBuildTongBuilding( self, pauseType ):
		"""
		define method.
		������������ͣ��Ὠ��
		"""
		if self.tong_curBuildType == pauseType:
			self.tong_curBuildType = 0
		if pauseType in self.tong_pauseBuilds:
			return
		self.tong_pauseBuilds.append( pauseType )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_SET_PAUSE_BUILD", pauseType )

	def tong_shenShouSelect( self, type = 1 ):
		"""
		ѡȡĳ������
		"""
		BigWorld.player().cell.tong_onSelectShouShou( type )

	#-------------------------------------------�Ӷ�ս-----------------------------------------------------

	def tong_onRequestRobWar( self ):
		"""
		define method.
		�����NPC�����Ӷ�ս
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_REQUEST_ROB_WAR" )
		# ����Ҫ�������
#		from gbref import rds # ��ʱʹ��  �������Ӧ��ȥ��
#		BigWorld.player().chat_say( "ʹ�ô˹��ܣ��������������������������,��Ҫ���س���Ȼ���NPC�Ի����Ƚ���������Ͻ��޸Ĵ˹��ܡ�" )
#		self.tong_requestRobWar( rds.ruisMgr.chatWindow._ChatWindow__pyCBMsg.text )

	def tong_findRequestRobWar( self, tongName ):
		"""
		��Ҳ������Ҫ�Ӷ�İ��
		"""
		BigWorld.player().cell.tong_findRequestRobWar( tongName )

	def onfindRequestRobWarCallBack( self, tongLevel, tongShenShouType, shenshouLevel, tongRobWarIsFailure ):
		"""
		define method.
		��Ҳ������Ҫ�Ӷ�İ�� �ķ������ص�
		@param tongLevel			: ��ѯ���ĵȼ� Ϊ0����û���ҵ���¼
		@param tongShenShouType		: ���޵�����	Ϊ0������û������
		@param shenshouLevel		: ���޵ļ���
		@param tongRobWarIsFailure	: ����ڱ����Ӷ�ս�Ƿ���ʧ�ܹ� bool
		"""
		if tongLevel <= 0: # û���ҵ�������
			return
		BigWorld.player().statusMessage( csstatus.CITYWAR_EXPLAIN, tongLevel, tongShenShouType, shenshouLevel, tongRobWarIsFailure )

	def tong_requestRobWar( self, tongName ):
		"""
		��������ύҪ�Ӷ�İ�� ȷ�������ս��Ŀ����
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
		���ð���Ӷ�ս����
		������Դ���ս����ʼ�ͽ��� tongDBIDΪ0������ ����
		�ָ���������ɫ������������
		"""
		if tongDBID == 0 :
			self.tong_onRobWarOver()

		self.robWarTargetTong = tongDBID
		if tongDBID != 0 :
			self.tong_onRobWarBegin()

	def tong_isRobWarEnemyTong( self, tongDBID ) :
		"""
		�Ƿ������Ӷ�ս�еĵж԰��
		"""
		return self.robWarTargetTong == tongDBID and tongDBID != 0

	def tong_isInRobWar( self ):
		"""
		�Ƿ����ڽ��а���Ӷ�ս
		"""
		return self.robWarTargetTong != 0

	def tong_isTongMember( self, role ) :
		"""
		�Ƿ��ǰ���Ա
		"""
		return self.tong_dbID != 0 and self.tong_dbID == role.tong_dbID

	#-----------------------------------���---------------------------------------------------------------

	def tong_openReuqestCampaignMonsterRaidWindow( self, npcID, campaignLevelList ):
		"""
		define method.
		�򿪰���������
		@param campaignLevelList: ������м���
		"""
		BigWorld.player().statusMessage( csstatus.MONSTER_RAID_LEVEL, campaignLevelList )

	def tong_requestCampaignMonsterRaidWindow( self, npcID, campaignLevel ):
		"""
		���������������
		"""
		BigWorld.player().cell.tong_reuqestCampaignMonsterRaidWindow( npcID, campaignLevel )


	# ----------------------------------------- ���ֿ� ------------------------------------------------
	def tong_receiveStorageItem( self, items ):
		"""
		Define method.
		���հ��ֿ���Ʒ��Ϣ�ĺ���

		@param items : ��Ʒ�б�
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
		������ֿ�

		@param storageLevel : �ֿ�ȼ�
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
		������ֿ���Ʒ����,ÿ������40����Ʒ����.

		"""
		#orderCount = csconst.TONG_WAREHOUSE_LIMIT[ self.tong_ck_level ]
		if self.tong_ck_requestItemCount + 1 > len( self.storageBagPopedom ) * 2:
			self.tong_ck_requestItemCount = 0
			self.tong_requestStorageLog()		# ��������Ʒ������ʼ����log����
			return

		self.base.tong_requestStorageItem( self.tong_ck_requestItemCount )
		self.tong_ck_requestItemCount += 1
		BigWorld.callback( 0.2, self.tong_requestStorageItem )	# ÿ��0.2������һ������

	def tong_requestStorageLog( self ):
		"""
		����ֿ��log��Ϣ,ÿ������50��
		"""
		if self.tong_ck_requestLogCount >= 3:	# �Ѿ��������
			self.tong_ck_requestLogCount = 0
			return
		if self.tong_ck_requestLogCount * 50 > len( self.tong_storageLog ):	# ��������������������,˵�������Ѿ��������
			self.tong_ck_requestLogCount = 0
			return
		self.base.tong_requestStorageLog( self.tong_ck_requestLogCount )
		self.tong_ck_requestLogCount += 1
		BigWorld.callback( 0.5, self.tong_requestStorageLog )	# ÿ��0.5������һ������

	def tong_receiveStorageLog( self, log ):
		"""
		Define method.
		���հ��ֿ�log��Ϣ�ĺ���

		@param log : һ��log��Ϣ[ playerName, operation, itemID, itemCount ]
		@type log : PYTHON
		"""
		self.tong_storageLog.append( log )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_LOG", log )

	def tong_storeItem2Order( self, srcOrder, dstOrder, entityID ):
		"""
		�����ֿ���洢��Ʒ�Ľӿڣ���֪Ŀ����Ʒ��

		param srcOrder:	�������Ӻ�
		type srcOrder:	INT16
		param dstOrder:	���ֿ���Ӻ�
		type dstOrder:	INT16
		param entityID:	���npc��id
		type entityID:	OBJECT_ID
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_storeItem2Order( srcOrder, dstOrder, entityID )

	def tong_storeItem2Bag( self, srcOrder, bagID ):
		"""
		�����ֿ���洢��Ʒ�Ľӿڣ���֪Ŀ����Ʒ��

		@param srcOrder:	�������Ӻ�
		@type srcOrder:	INT16
		@param bagID : ����id
		@type bagID : UINT8
		@param entityID:	���npc��id
		@type entityID:	OBJECT_ID
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_storeItem2Bag( srcOrder, bagID, entityID )

	def tong_storeItem2Storage( self, srcOrder, entityID ):
		"""
		�����ֿ���洢��Ʒ�Ľӿڣ���֪Ŀ����Ʒ��

		param srcOrder:	�������Ӻ�
		type srcOrder:	INT16
		param entityID:	���npc��id
		type entityID:	OBJECT_ID
		"""
		if entityID == 0: entityID = self.tong_storage_npcID
		self.cell.tong_storeItem2Storage( srcOrder, entityID )


	def tong_fetchItem2Order( self, srcOrder, dstOrder, entityID ):
		"""
		����Ϸ���Ʒ������ұ���

		param dstOrder:	�������Ӻ�
		type dstOrder:	INT16
		param srcOrder:	���ֿ���Ӻ�
		type srcOrder:	INT16
		param entityID:	���npc��id
		type entityID:	OBJECT_ID
		"""
		item = self.getItem_( dstOrder )
		if item is not None:
			try:
				BagPopedom = self.storageBagPopedom[srcOrder / csdefine.KB_MAX_SPACE]
			except:
				DEBUG_MSG( "�Ҳ�����Ӧ������Ȩ�����ݡ�" )
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
		�Ҽ�����ֿ���Ʒ����ұ���

		param srcOrder:	�������Ӻ�
		type srcOrder:	INT16
		param entityID:	���npc��id
		type entityID:	OBJECT_ID
		"""
		npc = BigWorld.entities.get(self.tong_storage_npcID, None)
		if npc is not None and self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			return False

		self.cell.tong_fetchItem2Kitbags( srcOrder, npc.id )

	def tong_fetchSplitItem2Kitbags(self, srcOrder, amount):
		"""
		�ݲ�ֿ���Ʒ����ұ���

		param srcOrder:	�������Ӻ�
		type srcOrder:	INT16
		param amount:	����
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
		������Ǯׯ�洢һ����Ʒ�ĸ��º���

		param item:	��Ʒʵ��
		type item:	ITEM
		"""
		order = item.order
		itemInfo = ObjectItem( item )
		bankIndex = order/csdefine.KB_MAX_SPACE
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_ITEM_UPDATE", bankIndex, order, itemInfo )

	def tong_moveStorageItem( self, srcOrder, dstOrder ):
		"""
		�ֿ�����Ʒ����
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_moveStorageItem( srcOrder, dstOrder, entityID )

	def tong_moveItemCB( self, srcOrder, dstOrder ):
		"""
		Define method.
		���ֿ��ƶ���Ʒ�Ŀͻ���֪ͨ����
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_MOVE_ITEM", srcOrder, dstOrder )


	def tong_delItemUpdate( self, order ):
		"""
		Define method.
		���ֿ�ɾ��һ����Ʒ�Ŀͻ���֪ͨ����
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_DEL_ITEM", order )

	def tong_fetchStorageItemCB( self, amount ):
		"""
		Define method.
		ȡ��Ʒ�ɹ�,������ҽ���ȡ��Ʒ����

		@param amount : ȡ����Ʒ������
		@type amount : INT32
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_FETCH_CHANGE", amount )

	def tong_renameStorageBag( self, bagID, newName ):
		"""
		���İ��ֿ������

		@param bagID : ����id
		@type bagID : UINT8
		@param newName : ����λ����
		@type newName : STRING
		"""
		# ������г����Ĳ������
		entityID = self.tong_storage_npcID
		self.cell.tong_renameStorageBag( bagID, newName, entityID )

	def tong_updateStorageBagName( self, bagID, newName ):
		"""
		Define method.
		���ֿ���������º���

		@param bagID : ����id
		@type bagID : UINT8
		@param newName : ����λ����
		@type newName : STRING
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_STORAGE_NAME_CHANGE", bagID, newName )

	def tong_changeStorageBagLimit( self, bagID, officialPos, limitNum ):
		"""
		�ı���ְλ�Ĳֿ�洢Ȩ��

		@param bagID : ����id
		@type bagID : UINT8
		@param officialPos : ְλ
		@param officialPos : INT32
		@param newName : ����λ����
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
		�ı���ֿ������Ʒ����������

		@param bagID : ����id
		@type bagID : UINT8
		@param quality : Ʒ��
		@param quality : UINT8
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_changeStorageQualityLower( bagID, quality, entityID )
		for storagePopedom in self.storageBagPopedom:
			if storagePopedom["bagID"] == bagID:
				storagePopedom["qualityLowerLimit"] = quality

	def tong_changeStorageQualityUp( self, bagID, quality ):
		"""
		�ı���ֿ������Ʒ����������

		@param bagID : ����id
		@type bagID : UINT8
		@param quality : Ʒ��
		@param quality : UINT8
		"""
		entityID = self.tong_storage_npcID
		self.cell.tong_changeStorageQualityUp( bagID, quality, entityID )
		for storagePopedom in self.storageBagPopedom:
			if storagePopedom["bagID"] == bagID:
				storagePopedom["qualityUpLimit"] = quality

	#------------------------------------------�����׽�Ǯ-------------------------------------------------------
	def tong_onContributeToMoney( self ):
		"""
		define method.
		���׽�Ǯ �򿪽���
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_DONATE_WND_OPEN" )

	def tong_contributeToMoney( self, money ):
		"""
		��������������
		"""
		self.cell.tong_contributeToMoney( money )

	#------------------------------------------������-------------------------------------------------------

	def tong_setFeteData( self, value ):
		"""
		define method.
		��������ֵ
		@param value: ��ǰ����ֵ
		"""
		if value < 0:
			# С��������ʾ�� �������뿪��ػ��߻������
			BigWorld.player().statusMessage( csstatus.FETE_DATA_OVERRUN )
		else:
			spaceType = self.getCurrentSpaceType()
			if spaceType == csdefine.SPACE_TYPE_TONG_TERRITORY:
				BigWorld.player().statusMessage( csstatus.FETE_DATA_VALUE, value )


	def tong_feteExchange( self, npcID ):
		"""
		Define method.
		��ʼ�������黻��

		@param npcID : ���黻��npc id
		@type npcID : OBJECT_ID
		"""
		pass

	def tong_onRobWarBegin( self ) :
		"""
		����Ӷ�ս��ʼ���ı丽���ж԰����ҵ�������ɫ
		"""
		enemies = self.findEnemyTongMembersNearby()
		for ent in enemies :
			ECenter.fireEvent( "EVT_ON_TONG_ROB_WAR_BEING", ent )		# ֪ͨ����ı�������ɫ

	def tong_onRobWarOver( self ) :
		"""
		����Ӷ�ս�������ָ������ж԰����ҵ�������ɫ
		"""
		enemies = self.findEnemyTongMembersNearby()
		for ent in enemies :
			ECenter.fireEvent( "EVT_ON_TONG_ROB_WAR_OVER", ent )		# ֪ͨ����ָ�������ɫ

	#------------------------------------------�������ɻ-------------------------------------------------------
	def tong_onProtectTongDie( self ) :
		"""
		�������ɻ����������
		"""
		self.cell.tong_onProtectTongDie()

	#------------------------------------------����ѯ����-------------------------------------------------------
	def tong_setTongAD( self, ad ):
		"""
		�����Լ����Ĺ�棬 ����б������
		"""
		if self.tong_dbID <= 0:
			return
		self.cell.tong_setTongAD( self.tong_dbID, ad )

	def tong_requestTongList( self, camp = 0 ):
		"""
		������������ð���б�
		"""
		self.tongQueryTongListIndex = 0
		requestTongList( self.id, camp )

	def tong_onReceiveTongList( self, tongDBID, tongName, tongID, tongLevel, tongPrestige, isHoldCity ):
		"""
		define method.
		���հ���б�
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
		���հ���б����
		"""
		self.tongQueryTongListIndex = -1
		ECenter.fireEvent( "EVT_ON_TONG_RECEIVE_TONG_COMPLETED", len( self.TongListInfos ) )

	def tong_queryTongInfo( self, tongDBID ):
		"""
		������������ð����Ϣ
		"""
		self.cell.tong_queryTongInfo( tongDBID )

	def tong_onReceiveTongInfo( self, tongDBID, memberCount, chiefName, holdCity, leagues, ad ):
		"""
		define method.
		����tong_queryTongInfo����ĳ���Ļ�����Ϣ
		"""
		toBuildType, toBuildLevel = 0, 0
		ECenter.fireEvent( "EVT_ON_TONG_RECEIVE_TONG_INFO", tongDBID, memberCount, toBuildType, toBuildLevel, chiefName, holdCity, leagues, ad )

	def tong_requestJoinToTong( self, tongDBID ):
		"""
		������뵽ĳ�����
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
			if requestTime + Const.JOIN_TONG_REQUEST_LIMIT_INTERVAL > now:	# 20�����������
				self.statusMessage( csstatus.TONG_REQUEST_JOIN_LIMIT, int(Const.JOIN_TONG_REQUEST_LIMIT_INTERVAL/60) )
				return
			self.tongRequestInfo[tongDBID] = now
		self.cell.tong_requestJoinToTong( tongDBID )

	def tong_answerJoinToTong( self, playerDBID, rs_id = RS_NO ):
		"""
		��Ӧ��Ҽ���������
		"""
		if self.tong_dbID <= 0:
			return
		agree = rs_id == RS_YES
		self.cell.tong_answerJoinToTong( playerDBID, agree )

	def tong_onReceiveiJoinInfo( self, playerDBID, playerName ):
		"""
		define method.
		�������������������Ϣ
		"""
		# "[%s]ϣ��������Ƿ�ͬ�⣿"
		jionMsg = mbmsgs[0x0c41] %playerName
		if self.applyMsgBox:
			self.applyMsgBox.hide()
		self.applyMsgBox = showAutoHideMessage( 30, jionMsg, "", MB_YES_NO, Functor( self.tong_answerJoinToTong, playerDBID ), gstStatus = Define.GST_IN_WORLD )

	def tong_openTongQueryWindow( self ):
		"""
		define method.
		��NPC�Ի��󣬽������ѯ����
		"""
		ECenter.fireEvent( "EVT_ON_TONG_QUERY_WND_SHOW" )
		self.tong_requestTongList()

	def tong_openTongADEditWindow( self ):
		"""
		define method.
		��NPC�Ի��󣬽����������༭����
		"""
		ECenter.fireEvent( "EVT_ON_TONG_AD_EDIT_SHOW" )

	# ----------------------------------------------------------------
	# ��������ӵķ���
	# ----------------------------------------------------------------
	def findEnemyTongMembersNearby( self ) :
		"""
		��Ѱ�����ж԰���Ա
		@rtype		list	����б�
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
		����������
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_CHANGE_NAME", npcID )

	#------------------------------------------����� by ����-------------------------------------------------------
	#------------------------���������------------------------
	def submitTongSign( self, path ):
		"""
		�ϴ����ͼ��

		@param path : ͼ��·��
		@type  path : string
		"""
		if self.submitting:
			self.statusMessage( csstatus.TONG_SIGN_SUBMITTING )
			return
		self.iconString = Function.getIconStringByPath( path )
		iconstrlen = len( self.iconString )
		DEBUG_MSG( "Length of the submit icon %i ."%iconstrlen )
		if len( self.iconString ) > 4500:	# ͼƬ����
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
		�ϴ����Ԥ���ص�
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
		�ϴ�ͼ���timer�ص���ÿ���ϴ�self.iconStringList�е�һ��Ԫ��
		"""
		index = len( self.iconStringList )
		if index <= 0: return
		iconString = self.iconStringList.pop(index - 1)
		self.base.tong_submitSign( iconString, index )
		BigWorld.callback( 0.1, self.submitIconDetect )

	def onTong_submitSign( self ):
		"""
		define method
		�ϴ����ɹ��ص�
		"""
		self.submitting = False

	def changeTongSign( self, isSysIcon, reqMoney, path = None ):
		"""
		���������

		@param isSysIcon : �Ƿ�ϵͳͼ��
		@type  isSysIcon : BOOL
		@param reqMoney  : �����Ǯ
		@type  reqMoney  : INT32
		@param path : ͼ��·��
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
			if len( iconString ) > 4500:	# ͼƬ����
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
		ȡ�������
		"""
		if self.tong_sign_md5 is None or self.tong_sign_md5 == "":
			return
		self.base.tong_cancleSing()

	def tongSignTalkResult( self, result ):
		"""
		Define method.
		�����NPC�Ի����
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

	#------------------------��괫�����------------------------
	def tongSignCheck( self ):
		"""
		�Զ������⹦����Ȼ��Ȥ�������紦����ܵ��ۣ�������ʡ��ʡ
		"""
		player = BigWorld.player()
		if player is None:
			return
		r_tong_dbid = self.tong_dbID
		# �ް������޻���
		if r_tong_dbid <= 0:
			return
		# �����̬����б����иð��Ļ�����ݣ��ñ�����Դ����꣬����������������������
		if r_tong_dbid in tongSignMap:
			self.showLocalTongSign( tongSignMap[r_tong_dbid] )
			return
		# ��������Ĳ���
		if r_tong_dbid in player.tong_sign_searching_list:
			return

		player.tong_sign_searching_list[r_tong_dbid] = self.tongName
		player.tong_sign_searcher_list[r_tong_dbid] = self
		player.base.getTongSignMD5( r_tong_dbid )

	def onGetTongSignMD5( self, tongDBID, iconMD5 ):
		"""
		define method
		��ð����MD5�ص�
		"""
		DEBUG_MSG( "get player tong icon md5 %s( %i )"%( iconMD5, tongDBID ) )
		if iconMD5 is None or iconMD5 == "":
			if tongDBID not in tongSignMap:
				tongSignMap[tongDBID] = ""
			if tongDBID in self.tong_sign_searching_list:
				self.tong_sign_searching_list.pop( tongDBID )
				self.tong_sign_searcher_list.pop( tongDBID )
			return
		# ��Ȿ����Դ�������еĻ�ֱ���ñ�����Դ
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
		# ���������������
		self.base.clientGetTongSignIcon( tongDBID )

	def clientGetTongSignReady( self, tongDBID, packs_num, iconMD5 ):
		"""
		define method
		�ͻ���׼�����ܻ��
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
		��ð����ͼ��ص�
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
		self.saveTongSign( imgStr, iconMD5 )	# �Ѹð����Զ�������뱾��

		target.showLocalTongSign( iconMD5 )
		self.clientGetTongSignFinished()

	#------------------------�����ʾ���洢���------------------------
	def initTongSign( self ):
		"""
		��ʼ���������Ļ����Ϣ
		"""
		player = BigWorld.player()
		self.showLocalTongSign( player.tong_sign_md5 )

	def showLocalTongSign( self, iconMD5 ):
		"""
		��ʾ������Դ���еĻ��
		ǰ���Ƕ����Ѿ��д������
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
		��Ⲣ����ĳ�����·��
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
		�ѻ����Դ���뱾��
		"""
		path = "TongIcons"		# ͼ���ļ���
		sec = openSection( path, True )	# ����϶���Ϊ�գ�Ҫ������ͻ�����
		encodeName =  str( struct.unpack_from("l", iconMD5)[0] )
		fileName = encodeName + ".bmp"	# �ļ���
		if sec.has_key("fileName"):
			return
		Function.makeFile( path, fileName, imgStr )	# ����·����д���ļ�


	# ---------------------------- �����̨����� -------------------------------------------
	def tong_onEnterAbaSpace( self ):
		"""
		define method
		��ҽ�������̨ս��
		"""
		BigWorld.callback( 2, self.onUpdateRoleNameColor )
		
	def tong_onLeaveWarSpace( self ):
		"""
		define method.
		����뿪��ս��
		������һЩ������
		�磺���֣� ս�� ��
		"""
		GUIFacade.tong_onLeaveWarSpace()

	def tong_leaveWarSpace( self ):
		"""
		����ս��
		��������뿪ս�� ʹ�ô˽ӿ�
		"""
		if self.getState() != csdefine.ENTITY_STATE_FREE :
			self.statusMessage( csstatus.TONG_ABATTOIR_ESCAPE_IN_FREE_STATE )
			return
		BigWorld.player().cell.tong_leaveWarSpace()
#		self.tong_onLeaveWarSpace()

	def tong_onInTongAbaRelivePoint( self, index = 0 ): #����ѡ��һ������㣬����ѡ��A��
		"""
		�����ս����ѡ���˸����λ��
		@param index : 3�����������һ������ 0, 1, 2
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_TONG_ABA:
			self.cell.tong_onInTongAbaRelivePoint( index )
			self.onStateChanged( csdefine.ENTITY_STATE_DEAD, csdefine.ENTITY_STATE_FREE )
			return

	def tong_onInitRemainAbaTime( self, restTime,abaRound ):
		"""
		Define method.
		�����̨��ʣ��ʱ����º���

		@param restTime : ��̨�������೤ʱ��
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
		��̨��ս������º���

		@param playerName : �������
		@type playerName : STRING
		@param killNum : ���ɱ����
		@type killNum : INT16
		@param beKilledNum : ��ɱ��
		@type beKilledNum : INT16
		@param tongDBID : ������ڵİ��dbid
		@type tongDBID : INT64
		"""
		DEBUG_MSG( "--->>>playerName:%s,killNum:%i,beKilledNum:%i,tongDBID:%i." % ( playerName, killNum, beKilledNum, tongDBID ) )
		GUIFacade.tong_updatePlayerWarReport( self.id, playerName, tongDBID, killNum, beKilledNum )


	def tong_updateAbaBuyPoint( self, point ):
		"""
		Define method.
		��ҹ�����ֵĸ��º���

		@param point : ��ҹ������
		@type point : INT16
		"""
		DEBUG_MSG( "--->>>buyPoint:%i." % point )
		ECenter.fireEvent( "EVT_ON_TOGGLE_BUY_RECORD_CHANGE", point )


	def updateAllTongAbaPoint( self, targetTongName, targetPoint, myPoint ):
		"""
		Define method.
		�����̨�����а��Ļ��ָ��º���

		@param targetTongName : �Է��������
		@type targetTongName : STRING
		@param targetPoint : �Է����Ļ���
		@type targetPoint : INT16
		@param myPoint : ��Ұ��Ļ���
		@type myPoint : INT16
		"""
		DEBUG_MSG( "--->>>targetTongName:%s, targetPoint:%i, myPoint:%i." % ( targetTongName, targetPoint, myPoint ) )
		GUIFacade.tong_onAbaMarkChanged( targetTongName, targetPoint, myPoint )


	def updateTongAbaPoint( self, tongName, point, tongDBID ):
		"""
		Define method.
		���¶�Ӧ���Ļ��ֵ��ͻ���

		@param familyName : �������
		@type familyName : STRING
		@param point : �Է����Ļ���
		@type point : INT16
		@param tongDBID : Ҫ���µİ���DBID
		@type tongDBID : DATABASE_ID
		"""
		DEBUG_MSG( "--->>>tongName:%s, Point:%i." % ( tongName, point ) )
		if self.tong_dbID == tongDBID:	# ��������Լ�������
			GUIFacade.tong_onAbaMarkChanged( tongName, 0, point, True )
		else:
			GUIFacade.tong_onAbaMarkChanged( tongName, point, 0, False )

	def tong_onTongAbaDie( self ):
		"""
		�����̨������
		"""
		# ֱ�Ӹ���
		#self.cell.tong_onInTongAbaRelivePoint()
		GUIFacade.tong_onTongAbaDie()

	def tong_onTongAbaOver( self ):
		"""
		defined method

		�����̨�����еı�������ʱ�����ô˽ӿ�
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_SHOW_ABA_RESULT" )

	#------------------------------------- ���ٺ»��� ------------------------------------
	def tong_onDrawSalary(self ):
		"""
		ȷ����ȡٺ»
		"""
		self.cell.tong_onDrawTongSalary( )

	def tong_updateMemberContributeInfos( self, memberDBID, totalContribute, currentContribute, thisWeekTotalContribute, lastWeekTotalContribute ):
		"""
		define method
		���������¿ͻ��˳�Ա�ﹱ��Ϣ���ۼưﹱ��ֵ��ʣ��ﹱֵ�����ܻ�ðﹱ�����ܻ�ðﹱ
		"""
		if self.tong_memberInfos.has_key( memberDBID ):
			memInfo = self.tong_memberInfos[ memberDBID ]
			memInfo.setTongContributeRelated( totalContribute, currentContribute, thisWeekTotalContribute, lastWeekTotalContribute )

	def tong_receiveSalaryInfo( self, lastWeekTotalContribute, lastWeekSalaryChangeRate,\
							lastWeekReceivedSalary, thisWeekTotalContribute,  thisWeekSalaryChangeRate ):
		"""
		define method
		���շ����������������ٺ»��ص���Ϣ
		"""
		thisWeekSalaryChange = thisWeekTotalContribute * thisWeekSalaryChangeRate
		if self.tong_holdCity:
			thisWeekSalaryChange *= 2
			
		sararyInfo = [lastWeekTotalContribute, lastWeekSalaryChangeRate, lastWeekReceivedSalary, thisWeekTotalContribute, thisWeekSalaryChangeRate, thisWeekSalaryChange ]
		GUIFacade.tong_receiveSalaryInfo( sararyInfo )

	def tong_receiveTongMoneyInfo( self, lastWeekInfo, thisWeekInfo ):
		"""
		define method
		���ܷ������������İ�����ʽ���Ϣ
		"""
		GUIFacade.tong_onInitFund( lastWeekInfo, thisWeekInfo )

	def tong_setSalaryExchangeRate( self, rate ):
		"""
		��������ÿ��ﹱ�ɶһ���Ǯ��
		"""
		minRate = csconst.TONG_SALARY_EXCHANGE_MIN_RATE
		if rate < minRate:									# �趨ֵС����С��
			self.statusMessage( csstatus.TONG_SALARY_CHANGE_RATE_LOWER_THAN_MIN, minRate )
			return
		maxRate = csconst.TONG_SALARY_EXCHANGE_RATE[ self.tongLevel ]
		if rate > maxRate:									# �趨ֵ���ڸõȼ������������ֵ
			self.statusMessage( csstatus.TONG_SALARY_CHANGE_RATE_LARGER_THAN_MAX, maxRate )
			return
		self.cell.tong_onSalaryExchangeRate( rate )

	def tong_updateNextWeekExchangeRate( self, rate ):
		"""
		define mothod
		���շ����������������ܰ��ٺ»�һ������Ϣ
		"""
		GUIFacade.tong_onUpdateNextWeekChangeRate( rate )

	def tong_receiveTerritoryNPCData( self, tongDBID, npcID ) :
		"""
		<Define method>
		@param	tongDBID : �������ݿ�ID
		@type	tongDBID : DATABASE_ID( INT64 )
		@param	npcID : NPC��ΨһID( className )
		@type	npcID : STRING
		���շ��������͵İ�����NPC����
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
		��ȡָ�������ص�NPC����
		"""
		return self.tong_territoriesNPCs.get( tongDBID, [] )
		
	#------------------------------------- �����ս������������죩��� ------------------------------------
	def tong_onFengHuoLianTianOver( self ):
		"""
		������ս������������죩����
		"""
		ECenter.fireEvent( "EVT_ON_FHLT_SPACE_OVER" )
		
	def tong_onEnterFengHuoLianTianSpace( self, warRemainTime, tongInfos ):
		"""
		���������ս������������죩
		"""
		ECenter.fireEvent( "EVT_ON_ENTER_FHLT_SPACE", warRemainTime, tongInfos )
		
	def tong_onQueryFHLTTable( self, datas ):
		"""
		define method.
		������ս������������죩���̲鿴
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_FHLTAGST_DATAS", datas )
	
	def tongFHLTProtectTime( self, time ):
		"""
		define method.
		������ս������������죩׼��ʱ��
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_FHLT_PROTECT_TIME", time )
		
	def tong_onFHLTReport( self, tongDBID,  playerName, kill, dead, isInWar ):
		"""
		define method.
		������ս������������죩���¸�������ҿͻ���ս����������Ϣ
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_FHLTRANK_DATAS", tongDBID,  playerName, kill, dead, isInWar )
		
	def tong_onUpdateFHLTPoint( self, tongDBID, point ):
		"""
		define method.
		������ս������������죩�������������ĵ�ǰĳ����ս������
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_FHLT_POINT", tongDBID, point )
	
	def tong_onLeaveFengHuoLianTianSpace( self ):
		"""
		define method.
		������ս������������죩����뿪����
		"""
		ECenter.fireEvent( "EVT_ON_LEAVE_FHLT_SPACE" )

	#------------------------------------- ���ǩ����� ------------------------------------
	def tong_requestSignIn( self ):
		"""
		����ǩ��
		"""
		self.base.tong_requestSignIn()

	def tong_onSetSignInRecord( self, dailyRecord, totalRecord ):
		"""
		define method
		����ǩ������
		"""
		self.tong_dailySignInRecord = dailyRecord
		self.tong_totalSignInRecord = totalRecord
		ECenter.fireEvent( "EVT_ON_UPDATE_TONG_SINGCOUNT", totalRecord )
		
	#----------------------------------- ����������� ---------------------------------------
	def onDartQuestStatusChange( self, newState ):
		"""
		define method
		�������������״̬�ı�
		"""
		if newState:
			self.statusMessage( csstatus.TONG_OPEN_DART_QUEST )
		self.refurbishAroundQuestStatus()
		
	def onNormalQuestStatusChange( self, openType ):
		"""
		define method
		����ճ�������״̬�ı�
		"""
		if openType != 0:
			self.statusMessage( csstatus.TONG_OPEN_NORMAL_QUEST )
		self.refurbishAroundQuestStatus()
			
	#----------------------------------- ս������ ---------------------------------------
	def tong_openTongBattleLeagueWindow( self, quarterFinalRecord ):
		"""
		define method
		��ս�����˽���
		"""
		INFO_MSG( "TONG: ( %s, %i ) open tong battle league window, get quarterFinalRecord %s " % ( self.getName(), self.id, quarterFinalRecord ) )
		self.tong_quarterFinalRecord = quarterFinalRecord				# �����سǰ��{ ���ID: ����; }
		self.tong_requestBattleLeagues( self.getCamp() )				# ������ս�����˰��

	def tong_requestBattleLeagues( self, camp ):
		"""
		������ս�����˰��
		"""
		self.tongQueryBattleLeagueIndex = 0
		requestTongBattleLeagueList( self.id, camp )

	def tong_receiveBattleLeagues( self, tongDBID, tongName, camp, leagues ):
		"""
		define method
		���հ��ս��ͬ����Ϣ
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
		ս���������ݽ������
		"""
		self.tongQueryBattleLeagueIndex = -1
		INFO_MSG( "TONG: Finish receive battle leagues!")
		ECenter.fireEvent("EVT_ON_TONG_ALLIANCE_WINDOW_SHOW" )

	def tong_inviteTongBattleLeagues( self, tongDBID, msg ):
		"""
		����ս������
		"""
		if tongDBID == 0:
			return
		self.cell.tong_inviteTongBattleLeagues( tongDBID, msg )

	def tong_receiveBattleLeagueInvitation( self, inviterTongName, inviterTongDBID, msg ):
		"""
		define method
		�յ������������ս��ͬ��
		"""
		GUIFacade.tong_receiveBattleLeagueInvitation( inviterTongName, inviterTongDBID, msg )

	def tong_replyBattleLeagueInvitation( self, inviterTongDBID, response ):
		"""
		�ظ�ս����������
		"""
		INFO_MSG( "TONG: %s, %i reply inviterTongDBID %i 's battleLeague invitation, response is %i " % ( self.getName(), inviterTongDBID, self.id, response ) )
		self.cell.tong_replyBattleLeagueInvitation( inviterTongDBID, response )

	def tong_setBattleLeague( self, tongDBID, tongName ):
		"""
		define method
		����ս��ͬ�˰��
		"""
		self.tong_battleLeagues[ tongDBID ] = tongName
		DEBUG_MSG( "TONG:Set battle league tong: %i, %s" % ( tongDBID, tongName ) )
	
	def tong_addBattleLeague( self, tongDBID, tongName ):
		"""
		define method
		���ս��ͬ�˰��
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
		���ĳ���ս�����˹�ϵ
		"""
		self.cell.tong_battleLeagueDispose( battleLeagueDBID )

	def tong_delBattleLeague( self, tongDBID ):
		"""
		define method
		�����ĳս��ͬ�˰��
		"""
		DEBUG_MSG( "TONG:Del battle league tong: %i" % ( tongDBID ) )
		if self.tong_dbID not in self.tong_battleLeagues.keys():
			ERROR_MSG( "TONG: Self tongDBID not in my tong_battleLeagues %s" % ( self.tong_dbID, self.battleLeagues ) )
			return

		if tongDBID in self.tong_battleLeagues[ self.tong_dbID ][ "battleLeagues" ]:
			self.tong_battleLeagues[ self.tong_dbID ][ "battleLeagues" ].remove( tongDBID )

		
	def getCityWarTongBelong( self, tongDBID ):
		"""
		��ȡ�����ս�����İ����������ǻ����سǷ�
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
		�����ս�����а����� 
		"""
		if self.tongInfos.has_key( "tongInfos" ):
			for key, info in self.tongInfos[ "tongInfos"].iteritems():
				if ownTongDBID in info.keys():
					if targetTongDBID in info:
						return True
		return False

def requestDatas( playerEntityID ):
	"""
	ÿ��һ��ʱ�������������һ�ΰ���������
	"""
	p = BigWorld.player()
	if not p or p.id != playerEntityID or p.tong_isRequestDataEnd:
		return

	p.cell.tong_requestDatas()
	BigWorld.callback( 0.3, Functor( requestDatas, playerEntityID ) )

def requestTongList( playerEntityID, camp ):
	"""
	ÿ��һ��ʱ�������������һ�ΰ���б��������
	"""
	p = BigWorld.player()
	if not p or p.id != playerEntityID or p.tongQueryTongListIndex == -1:
		return

	p.cell.tong_requestTongList( p.tongQueryTongListIndex, camp )
	p.tongQueryTongListIndex += 5
	BigWorld.callback( 0.3, Functor( requestTongList, playerEntityID, camp ) )

def requestTongBattleLeagueList( playerEntityID, camp ):
	"""
	�����������ս���������ݣ���������б���Ϣ��
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
# ���������Ҽ������ϵͳ��Ϣ
#
# Revision 1.22  2008/08/21 10:15:02  qilan
# ���������Ҽ������ϵͳ��Ϣ
#
# Revision 1.21  2008/08/12 08:51:36  kebiao
# ��Ӱ����������
#
# Revision 1.20  2008/07/25 03:45:32  kebiao
# ���Ӱ���ɢ��ʾ��Ϣ
#
# Revision 1.19  2008/07/24 04:08:02  kebiao
# ȥ��һЩ������Ϣ
#
# Revision 1.18  2008/07/24 03:21:24  kebiao
# ������ʱ������Ϣ������ͬ�²鿴
#
# Revision 1.17  2008/07/24 02:03:42  kebiao
# ȥ��һЩ������Ϣ
#
# Revision 1.16  2008/07/22 01:59:43  huangdong
# ���ư�������ϵͳ
#
# Revision 1.15  2008/07/02 01:42:51  kebiao
# ����һ����ʾ����
#
# Revision 1.14  2008/07/02 01:34:08  kebiao
# ����ְλ���Ʊ���
#
# Revision 1.13  2008/07/01 11:19:01  fangpengjun
# ��Ӵ������ӿ�
#
# Revision 1.12  2008/07/01 10:45:44  fangpengjun
# �����˽ӿ�tong_onMemberFamilyGradeChanged��һ����������
#
# Revision 1.11  2008/06/30 10:25:06  fangpengjun
# �޸Ĳ�����Ϣ
#
# Revision 1.10  2008/06/30 04:15:33  kebiao
# ���Ӱ��ְλ���Ʊ༭
#
# Revision 1.9  2008/06/29 08:57:17  fangpengjun
# ��ӽ���������Ϣ
#
# Revision 1.8  2008/06/27 07:11:48  kebiao
# �����˰��ͼ�����첽���ݴ������
#
# Revision 1.7  2008/06/23 08:13:23  kebiao
# no message
#
# Revision 1.6  2008/06/23 02:56:05  kebiao
# �޸�һ����ʾ����
#
# Revision 1.5  2008/06/21 04:15:58  kebiao
# no message
#
# Revision 1.4  2008/06/21 03:42:00  kebiao
# �����ṱ�׶�
#
# Revision 1.3  2008/06/16 09:15:00  kebiao
# base �ϲ��ֱ�¶�ӿ�ת�Ƶ�cell �ı���÷�ʽ
#
# Revision 1.2  2008/06/14 09:15:27  kebiao
# ������Ṧ��
#
# Revision 1.1  2008/06/09 09:23:27  kebiao
# ���������
#
#