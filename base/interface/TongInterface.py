# -*- coding: gb18030 -*-
#
# $Id: TongInterface.py,v 1.6 2008-08-25 09:30:09 kebiao Exp $

import time
import _md5
import BigWorld
from bwdebug import *
from Function import Functor
import csdefine
import csstatus
import csconst
import TongEntity
import Love3
import Const
from Love3 import g_tongSignMgr


class TongInterface:
	def __init__( self ):
		self.tongEntity = None		# ���ڽ�ɫ��base�ǹ̶��ģ���˿���ֱ������
		self.tong_dbID = self.cellData[ "tong_dbID" ]
		self.tong_grade = self.cellData[ "tong_grade" ]
		self._tong_sign_string_req_list = []	# ���嵽�ý�ɫ�İ�������������
		self.signSending = False		# �Ƿ�������ͻ��˴��ͻ��
		self.isSignSendReady = False	# �Ƿ�����ɷ���׼��

		try:
			self.cellData[ "tong_level" ] = BigWorld.baseAppData[ "tong.%i" % self.tong_dbID ][ "level" ]
		except:
			pass
			
	def tong_logonInTerritory( self, position, direction ):
		"""
		define method.
		������е�½
		"""
		DEBUG_MSG( "because not found spaceCopy�� so is login to tong territory��", position, direction )
		if self.cellData[ "lastTongTerritoryDBID" ] <= 0:
			self.cellData[ "spaceType" ] = self.cellData[ "reviveSpace" ]
			self.cellData[ "position" ] = self.cellData[ "revivePosition" ]
			self.cellData[ "direction" ] = self.cellData[ "reviveDirection" ]
		else:
			self.cellData[ "spaceType" ] = "fu_ben_bang_hui_ling_di"
			self.cellData[ "position" ] = position
			self.cellData[ "direction" ] = direction
		self.logonSpace()

	def tong_logonInTerritoryError( self ):
		"""
		define method.
		������е�½���� ����ĳ��ᱻ��ɢ������һ�������ڵİ�����
		"""
		WARNING_MSG( "player login find a not exist the territory[%i]�� begin goto spawnpoint��" % self.cellData[ "lastTongTerritoryDBID" ] )
		self.cellData[ "spaceType" ] = self.cellData[ "reviveSpace" ]
		self.cellData[ "position" ] = self.cellData[ "revivePosition" ]
		self.cellData[ "direction" ] = self.cellData[ "reviveDirection" ]
		self.logonSpace()

	def getTongManager( self ):
		return BigWorld.globalBases["TongManager"]

	def tong_reset( self ):
		"""
		define method
		"""
		self.tong_dbID = 0
		self.tong_grade = 0
		self.tongEntity = None
		self.tong_totalSignInRecord = 0

		# �����û��cell ��ôд��celldata��
		if not hasattr( self, "cell" ):
			self.cellData[ "tong_dbID" ] = 0
			self.cellData[ "tong_grade" ] = 0
			self.writeToDB()
		else:
			self.cell.tong_reset()

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

	def tong_setGrade( self, grade ):
		"""
		define method.
		���ø�player grade
		"""
		if self.tong_grade != grade:
			self.tong_grade = grade

			if hasattr( self, "cell" ):
				self.cell.tong_setGrade( grade )
			else:
				self.cellData[ "tong_grade" ] = grade
				self.writeToDB()
				tongBaseMailbox = self.tong_getSelfTongEntity()
				if tongBaseMailbox is None:
					return
				self.tong_getSelfTongEntity().changeGradeSuccess( self.databaseID )
				
	def tong_setScholium( self, scholium ):
		"""
		define method.
		���ø�player grade
		"""
		if self.tong_scholium != scholium:
			self.tong_scholium = scholium

	def tong_onLogin( self ):
		"""
		define method.
		��½���
		"""
		if self.tong_dbID > 0:
			self.getTongManager().onMemberLoginTong( self.tong_dbID, self, self.databaseID )

	def tong_onLogout( self ):
		"""
		���߰��
		"""
		if self.tong_dbID > 0:
			self.getTongManager().onMemberLogoutTong( self.tong_dbID, self.databaseID )

	def tong_onLoginCB( self, tongEntity ):
		"""
		define method.
		��½��ϻص�
		@param tongEntity: ���entity��baseEntity �����½ʧ�ܷ��ص���none
		"""
		if tongEntity:
			self.tongEntity = tongEntity
			self.cell.tong_onLoginCB( tongEntity )
		else:
			# ��½ʧ����
			ERROR_MSG( "player %s:%i >>cannot login to tong dbid=%i!" % ( self.playerName, self.id, self.tong_dbID ) )

	#-------------------------------------------------------------------------------------------------------
	def tong_sendMessage( self, memberDBID, msg ):
		"""
		Exposed method.
		��ĳ��Ա������Ϣ
		"""
		self.tongEntity.onSendMessage( self.playerName, memberDBID, msg )

	def tong_onLevelChanged( self ):
		"""
		�����𱻸ı���
		"""
		if self.tongEntity:
			self.tongEntity.onMemberLevelChanged( self.databaseID, self.level )

	def tong_requestMemberMapInfos( self ):
		"""
		Exposed method.
		��ĳ��Ա������Ϣ
		"""
		if self.tongEntity:
			self.tongEntity.requestMemberMapInfo( self, self.databaseID )

	def isJoinTong(self):
		"""
		�ж�����Ƿ������
		tong_grade ��Ϊ0 ��ʾ���һ�������˰��
		"""
		return self.tong_grade!=0


	def sendMessage2Tong(self, playerID, playerName, msg, blobArgs ):
		"""
		������Ϣ������������
		"""
		if self.tongEntity:
			self.tongEntity.onSendChatMessageAll( self.databaseID, msg, playerID, playerName, blobArgs )

	def onTeleportCityWar( self, spaceMailbox, position, direction ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "TongManager" ].onTeleportCityWar( spaceMailbox, position, direction, self, self.tong_dbID )


	# ------------------------------------------------ ���ֿ� -----------------------------------------------------
	def tong_requestStorageItem( self, count ):
		"""
		Exposed method.
		����ֿ���Ʒ����

		@param count : ����Ĵ���
		@type count : INT8
		"""
		if count > 11:	# ÿ������40����Ʒ�������,���ֿ�һ��6������,����11˵���˲�������ȷ
			return
		if self.tongEntity:
			self.tongEntity.requestStorageItem( self.databaseID, count )


	def tong_requestStorageLog( self, count ):
		"""
		Exposed method.
		����ֿ�log��Ϣ

		@param count : ����Ĵ���
		@type count : INT8
		"""
		if self.tongEntity:
			self.tongEntity.requestStorageLog( self.databaseID, count )

	# ------------------------------------------------ ����� by ����-----------------------------------------------------
	def tong_submitSignReady( self, iconMD5, iconstrlen, packs_num ):
		"""
		Exposed method.
		�ϴ����ͼ��Ԥ��

		@param iconMD5 : ͼ��ת���ɵ�MD5,��������ϴ���У��
		@type  iconMD5 : STRING
		@param iconstrlen : ����ַ�������,����У��too
		@type  iconstrlen : INT32
		@param packs_num : ���ֿ����ĸ���,����У��three
		@type  packs_num : UINT8
		"""
		self.submiting_IconMD5 = iconMD5
		self.submiting_Iconstrlen = iconstrlen
		self.submiting_PacksNum = packs_num
		self.submiting_IconDict = {}
		self.client.onTong_submitSignReady()
		
	def tong_submitSign( self, iconString, index):
		"""
		Exposed method.
		�ϴ����ͼ��

		@param iconString : ͼ��ת���ɵ��ַ���
		@type  iconString : STRING
		@param index : �ְ�ͼ��İ����
		@type  index : INT8
		"""
		self.submiting_IconDict[index] = iconString
		dictLen = len( self.submiting_IconDict )
		if dictLen < self.submiting_PacksNum:
			DEBUG_MSG( "submitting icon continue, index %i, len %i. "%( index, dictLen ) )
			return
		fullIconString = ""
		for k in self.submiting_IconDict.iterkeys():
			fullIconString += self.submiting_IconDict[k]
		if fullIconString == "":
			ERROR_MSG( "Getting user tong sign failed, iconString is empty." )
			self.onTong_submitSign( "" )
			return
		iconMD5 = _md5.new(fullIconString).digest()
		if iconMD5 != self.submiting_IconMD5:
			self.client.onStatusMessage( csstatus.TONG_SIGN_SUBMIT_FAILED, "" )
			self.onTong_submitSign( "" )
			return
		self.tongEntity.submitTongSign( fullIconString, iconMD5, self )
		self.onTong_submitSign( iconMD5 )
		
	def onTong_submitSign( self, iconMD5 ):
		"""
		defined method
		�ϴ����ɹ��ص�
		
		@param iconMD5 : ͼ�����ɵ�MD5��
		@type  iconMD5 : INT64
		"""
		self.submiting_IconMD5 = ""
		self.submiting_Iconstrlen = 0
		self.submiting_PacksNum = 0
		self.submiting_IconDict.clear()
		cost = 1 * csconst.USER_TONG_SIGN_REQ_MONEY
		if iconMD5 != "":
			self.tong_changeSing( False, cost, iconMD5 )
			self.client.onStatusMessage( csstatus.TONG_SIGN_SUBMIT_SUCCESS, "" )
		self.client.onTong_submitSign()

	def tong_changeSing( self, isSysIcon, reqMoney, iconMD5 ):
		"""
		Exposed method.
		�������ͼ��

		@param isSysIcon : �Ƿ�ϵͳͼ��
		@type  isSysIcon : BOOL
		@param reqMoney  : �����Ǯ
		@type  reqMoney  : INT32
		@param iconMD5 : ͼ�����ɵ�MD5��
		@type  iconMD5 : INT64
		"""
		self.tongEntity.changeTongSing( isSysIcon, reqMoney, iconMD5, self )

	def tong_cancleSing( self ):
		"""
		Exposed method.
		ȡ�����ͼ��
		"""
		self.tongEntity.setTongSignMD5( "" )
		self.statusMessage( csstatus.TONG_SIGN_CANCLE_SUCCESS )

	def getTongSignMD5( self, tongDBID ):
		"""
		Exposed method
		����DBID��ȡ�������İ����DBID
		"""
		if tongDBID <= 0:
			ERROR_MSG( "tong dbid error %i ."%tongDBID )
			return
		tongMB = BigWorld.globalData["tong.%i"%tongDBID]
		if tongMB is None:
			ERROR_MSG( "getTongSignMD5 tong %i is None."%tongDBID )
			return
		tongMB.getTongSignMD5( tongDBID, self )

	def clientGetTongSignIcon( self, tongDBID ):
		"""
		Exposed method
		�ͻ��������ð����string����
		"""
		if tongDBID <= 0:
			ERROR_MSG( "get tong sign string tong dbid error %i ."%tongDBID )
			return
		self._tong_sign_string_req_list.append( tongDBID )
		
	def sendTongSignString( self ):
		"""
		�����귢�͸��ͻ���
		"""
		if self.signSending:
			# DEBUG_MSG( "tong sign sending to player %i now."%self.id )
			return
		if len( self._tong_sign_string_req_list ) <= 0:
			# DEBUG_MSG( "tong string request list empty." )
			return
		tongDBID = self._tong_sign_string_req_list.pop(0)
		if tongDBID <= 0:
			DEBUG_MSG( "send tong sign string tong dbid error %i ."%tongDBID )
			return
		tongMB = BigWorld.globalData["tong.%i"%tongDBID]
		if tongMB is None:
			ERROR_MSG( "sendTongSignString tong %i is None."%tongDBID )
			return
		self.signSending = True
		tongMB.sendTongSignString( tongDBID, self )
		
	def tongSignSendStart( self, tongDBID, iconMD5, iconStringList ):
		"""
		��ʼ�ְ��������ַ���
		"""
		self.iconStringList = iconStringList
		self.iconSendingTongDBID = tongDBID
		self.client.clientGetTongSignReady( tongDBID, len( self.iconStringList ), iconMD5 )
		
	def onClientGetTongSignReady( self ):
		"""
		Exposed
		�ͻ�����׼���ý���ͼ��Ļص�
		"""
		self.isSignSendReady = True
		
	def sendIconPackToClient( self ):
		"""
		���ͻ������ͻ���
		"""
		index = len( self.iconStringList )
		if self.isSignSendReady == False or index <= 0:
			return
		iconString = self.iconStringList.pop( index - 1 )
		self.client.onClientGetTongSignIcon( self.iconSendingTongDBID, index, iconString )
		if index <= 1:
			self.iconSendingTongDBID = 0
			self.signSending = False
			self.isSignSendReady = False

	# -------------------------------------------------------------------------------------------
	def tong_requestJoinByPlayerName( self, playerName ):
		"""
		Exposed method.
		ͨ���������������Ҽ�����
		"""
		if self.playerName == playerName:
			self.statusMessage( csstatus.TONG_TARGET_SELF )
			return

		if self.tong_dbID > 0 and self.tongEntity:
			Love3.g_baseApp.lookupRoleBaseByName( playerName, self.tong_findBeInvitedPlayerBaseCB )

	def tong_findBeInvitedPlayerBaseCB( self, baseMailbox ):
		"""
		@param baseMailbox : ���Ŀ���������������base mailbox������ΪNone
		"""
		if baseMailbox:
			baseMailbox.tong_onPlayerRequestJoinByMyName( self.tongEntity, self, self.databaseID, self.getCamp() )
		else:
			self.statusMessage( csstatus.TONG_TARGET_NO_FIND )
			
	def tong_onPlayerRequestJoinByMyName( self, tongEntity, user, userDBID, userCamp ):
		"""
		����ͨ���ҵ�����Զ�������Ҽ���tong
		"""
		if self.tong_dbID > 0:
			user.client.onStatusMessage( csstatus.TONG_ALREADY_HAS_TONG, ""  )
			return
		
		if userCamp != self.getCamp():
			user.client.onStatusMessage( csstatus.TONG_CAMP_DIFFERENT, ""  )
			return 
			
		if self.level < csconst.TONG_JOIN_MIN_LEVEL:
			user.client.onStatusMessage( csstatus.TONG_CANT_JOIN_LEVEL_LACK, str( (csconst.TONG_JOIN_MIN_LEVEL,) )  )
			return
		if tongEntity:
			tongEntity.onRequestJoin( userDBID, self, self.databaseID )
		else:
			ERROR_MSG( "player( %s ) be invited join tong, but tongEntity is None.invitor dbid: %i." % ( self.getName(), userDBID ) )
			
	def tong_onJoin( self, tongDBID, grade, tongBaseMailbox ):
		"""
		�Ӱ��ɹ������ð������
		
		@param tongDBID : ����dbid
		@type tongDBID : DATABASE_ID
		@param grade : ���ְλ
		@type grade : UINT8
		@param tongBaseMailbox : ����base mailbox
		@type tongBaseMailbox : MAILBOX
		"""
		self.tongEntity = tongBaseMailbox
		self.tong_dbID = tongDBID
		self.tong_grade = grade
		self.tong_totalSignInRecord = 0

	def tong_leave( self ):
		"""
		Define method.
		�뿪���Ĵ���
		"""
		self.tong_dbID = 0
		self.tong_grade = 0
		self.tong_totalSignInRecord = 0
		self.tongEntity = None
		
	def clearTongDartRecord( self ):
		"""
		Define method
		���������ڼ�¼
		"""
		self.tongEntity.clearTongDartRecord()
		
	def setTongFactionCount( self, count ):
		"""
		Define method
		���ð��ʱװ������
		"""
		self.tongEntity.setTongFactionCount( count )

	#---------------------------------------- ���ٺ»��� ---------------------------------------------------
	def tong_requestMemberContributeInfos( self ):
		"""
		Exposed method.
		��ĳ��Ա���Ͱﹱ�����Ϣ
		"""
		if self.tongEntity:
			self.tongEntity.requestMemberContributeInfos( self.databaseID )

	#---------------------------------------- ���ǩ����� ---------------------------------------------------
	def tong_requestSignInRecord( self ):
		"""
		define method
		�򿪰����棬������ǩ������
		"""
		if not self.tong_dailySignInRecord.checklastTime():
			self.tong_dailySignInRecord.reset()
		
		self.client.tong_onSetSignInRecord( self.tong_dailySignInRecord.getDegree(), self.tong_totalSignInRecord )
		
	def tong_requestSignIn( self ):
		"""
		Exposed method
		���ǩ��
		"""
		if not self.tongEntity:
			return
		
		if not self.tong_dailySignInRecord.checklastTime():
			self.tong_dailySignInRecord.reset()
		
		if self.tong_dailySignInRecord.getDegree() >= Const.TONG_SIGN_UP_TIMES_LIMIT:
			return

		# ǩ����������
		self.tong_dailySignInRecord.incrDegree()
		self.tong_totalSignInRecord += 1
		INFO_MSG( "TONG: %s sign in , his totoal sign in record is %i " % ( self.getNameAndID(), self.tong_totalSignInRecord ) )
		# ����þ���
		self.tongEntity.addExp( Const.TONG_SIGN_UP_GAIN_EXP, csdefine.TONG_CHANGE_EXP_SIGN_IN )
		self.statusMessage( csstatus.TONG_SIGN_IN_SUCCESS, Const.TONG_SIGN_UP_GAIN_EXP )

		self.client.tong_onSetSignInRecord( self.tong_dailySignInRecord.getDegree(), self.tong_totalSignInRecord )
	
	def requestTongExp( self ):
		"""
		Exposed method
		��������ᾭ������
		"""
		self.tongEntity.roleRequestTongExp( self.databaseID )

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/07/22 03:43:42  huangdong
# �޸��˰������һ���ӿ���
#
# Revision 1.4  2008/07/22 01:58:33  huangdong
# ���ư�������
#
# Revision 1.3  2008/06/16 09:13:04  kebiao
# ����Ȩ���ϵ
#
# Revision 1.2  2008/06/14 09:18:51  kebiao
# ������Ṧ��
#
# Revision 1.1  2008/06/09 09:24:33  kebiao
# ���������
#
#