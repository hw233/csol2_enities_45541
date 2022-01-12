# -*- coding: gb18030 -*-

# $Id: LoginMgr.py,v 1.46 2008-08-28 01:42:51 huangyongwei Exp $

"""
implement login module
-- 2007/10/10 : written by huangyongwei
-- 2009.03.14 : modified by hyw
				��ɫ�����У�ѡ���ɫ��Ϊ�̶���ͷ��ʽ
				����ְҵ��ɫ��Ϊ�� callback �ֲ������ķ�ʽ
"""

import re
import time
import math
import BigWorld
import Pixie
import Math
import csdefine
import csconst
import Const
import Define
import Sources
import event.EventCenter as ECenter
import copy
from bwdebug import *
from Function import Functor
from cscollections import CycleList
from cscollections import MapList
from gbref import rds
from GameMgr import gameMgr
from CamerasMgr import FLCShell
from CamerasMgr import RCCamHandler
from CamerasMgr import LNCamHandler
from RoleMaker import RoleInfo
from RoleMaker import getCommonRoleInfo
from RoleMaker import getDefaultRoleInfo
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs
from config.client.ProfessionDsp import Datas as g_ProfessionDspData
from config.client.ProfessionDsp import Teacher_Desc as g_teacherData
from config.client.CampDsp import Datas as g_CampDspData
from guis.loginuis.roleselector.AttachName import AttachName
from guis.loginuis.logindialog.AutoActWnd import AutoActWindow

LOGIN_SPACE_TYPE_MAP = {
	Define.LOGIN_TYPE_MAP : "universes/fu_ben_chang_jing_jue_se",
	Define.SELECT_CAMP_TYPE_MAP : "universes/zhen_ying_xuan_zhe",
	csdefine.ENTITY_CAMP_TAOISM : "universes/zy_wa_huang_gong",
	csdefine.ENTITY_CAMP_DEMON  : "universes/zy_xiu_luo_dian",
}

P_D_M_T_CAMERA = {
	Define.SELECT_CAMP_TYPE_MAP : ((18.708733,8.872690,-56.010227),(-1.8, 0.000488, math.pi)),
	csdefine.ENTITY_CAMP_TAOISM : ((27.568,170.144,-123.611),( 179.908 * math.pi / 180, -6.875 * math.pi / 180, math.pi ), "selectclass_xian" ),
	csdefine.ENTITY_CAMP_DEMON  : ((48.208,158.399,56.178),  ( 1.145 * math.pi / 180, 0.572 * math.pi / 180, math.pi ), "selectclass_mo" ),
		}  #������ɫ��ͼ�����λ�úͳ���(1 �����Ӫ,2ħ����Ӫ)
TAOISM_YAW_PREVIEWROLE_MAP = {
	csdefine.CLASS_FIGHTER		: ( -15* math.pi / 180, -15* math.pi / 180 ),		# սʿ
	csdefine.CLASS_SWORDMAN		: ( 45* math.pi / 180, 45* math.pi / 180 ),			# ����
	csdefine.CLASS_ARCHER		: ( -30* math.pi / 180, -45* math.pi / 180),			# ����
	csdefine.CLASS_MAGE		: ( 30* math.pi / 180, 30* math.pi / 180),			# ��ʦ
	} #�ɵ��˸���ɫ�Ƕ�ֵ
DEMON_YAW_PREVIEWROLE_MAP = {
	csdefine.CLASS_FIGHTER		: ( 165* math.pi / 180, 165* math.pi / 180 ),		# սʿ
	csdefine.CLASS_SWORDMAN		: ( -135* math.pi / 180, -135* math.pi / 180 ),			# ����
	csdefine.CLASS_ARCHER		: ( 150* math.pi / 180, 150* math.pi / 180),			# ����
	csdefine.CLASS_MAGE		: ( 180* math.pi / 180, -165* math.pi / 180),			# ��ʦ
	}#ħ���˸���ɫ�Ƕ�ֵ
ALL_PREVIEWROLE_MAP = {
	csdefine.ENTITY_CAMP_TAOISM:TAOISM_YAW_PREVIEWROLE_MAP,
	csdefine.ENTITY_CAMP_DEMON:DEMON_YAW_PREVIEWROLE_MAP,
}

ROLE_PROFESSION = ( csdefine.CLASS_FIGHTER, csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER, csdefine.CLASS_MAGE )
ROLE_GENDER = ( csdefine.GENDER_MALE, csdefine.GENDER_FEMALE )

# --------------------------------------------------------------------
# ablut login
# --------------------------------------------------------------------
loginResult = {
	( 0, 0 ) 	: mbmsgs[0x0031],		# "The connection could not be initiated as either the client was already connected to a server!"
	( 1, 1 )	: mbmsgs[0x0032],		# "��¼�ɹ���"	"The client has successfully logged in to the server."
	( 1, -2 )	: mbmsgs[0x0033],		# "�޷����ӵ���������"	"The client failed to make a connection to the network."
	( 1, -3 )	: mbmsgs[0x0034],		# "�޷����ӵ���������"	"The client failed to locate the server IP address via DNS."
	( 1, -4 )	: mbmsgs[0x0035],		# "CLIENT ERROR: An unknown client-side error has occurred."
	( 1, -5 )	: mbmsgs[0x0036],		# "�ͻ�������ȡ����¼��"	"CLIENT ERROR: The login was cancelled by the client."
	( 1, -6 )	: mbmsgs[0x0037],		# "CLIENT ERROR: The client is already online locally (i.e. exploring a space offline). "
	( 1, -64 )	: mbmsgs[0x0038],		# "�Ƿ���¼���ݡ�"	"SERVER ERROR: The login packet sent to the server was malformed."
	( 1, -65 )	: mbmsgs[0x0039],		# "�汾��ƥ�䣬�����������°汾��"	"SERVER ERROR: The login protocol the client used does not match the one on the server."
	( 1, -66 )	: mbmsgs[0x003a],		# "�ʺŻ����벻��ȷ��"	"SERVER ERROR: The server database did not contain an entry for the specified username and was running in a mode that did not allow for unknown users to connect, or could not create a new entry for the user. The database would most likely be unable to create a new entry for a user if an inappropriate entity type being listed in bw.xml as database/entityType.
	( 1, -67 )	: mbmsgs[0x003b],		# "�ʺŻ����벻��ȷ��"	"SERVER ERROR: A global password was specified in bw.xml, and it did not match the password with which the login attempt was made."
	( 1, -68 )	: mbmsgs[0x003c],		# "���ʺ��ѵ�¼��"	"SERVER ERROR: A client with this username is already logged into the server."
	( 1, -69 )	: mbmsgs[0x003d],		# "�汾��ƥ�䣬�����������°汾��"	"SERVER ERROR: The defs and/or entities.xml are not identical on the client and the server."
	( 1, -70 )	: mbmsgs[0x003e],		# "������δ����"	"SERVER ERROR: A general database error has occurred, for example the database may have been corrupted."
	( 1, -71 )	: mbmsgs[0x003f],		# "������δ����"	"SERVER ERROR: The database is not ready yet."
	( 1, -72 )	: mbmsgs[0x0040],		# "�ʺŻ����벻��ȷ��"	 "SERVER ERROR: There are illegal characters in either the username or password."
	( 1, -73 )	: mbmsgs[0x0041],		# "������δ������1, -73����""SERVER ERROR: The baseappmgr is not ready yet."
	( 1, -74 )	: mbmsgs[0x0042],		# "SERVER ERROR: The updater is not ready yet."
	( 1, -75 )	: mbmsgs[0x0043],		# "������δ����"	"SERVER ERROR: There are no baseapps registered at present."
	( 1, -76 )	: mbmsgs[0x0044],		# "���������ع��أ����Ժ�����"	"SERVER ERROR: Baseapps are overloaded and logins are being temporarily disallowed."
	( 1, -77 )	: mbmsgs[0x0045],		# "��������æ�����Ժ�����"	"SERVER ERROR: Cellapps are overloaded and logins are being temporarily disallowed."
	( 1, -78 )	: mbmsgs[0x0046],		# "������δ����"	"SERVER ERROR: The baseapp that was to act as the proxy for the client timed out on its reply to the dbmgr. or The baseappmgr is not responding."
	( 1, -79 )	: mbmsgs[0x0047],		# "���������ع���"	"SERVER ERROR: The dbmgr is overloaded."
	( 1, -80 )	: mbmsgs[0x0048],		# "������δ����"	"SERVER ERROR: No reply from DBMgr."
	( 1, -250 )	: mbmsgs[0x0049],		# "�˺��ѱ� GM �йܣ�"	"�˺��ѱ� GM �йܣ�"
	( 1, -251 )	: mbmsgs[0x004a],		# "�Զ�����������������Ժ����ԡ�"	"SERVER ERROR: The auto active queue is overflow."
	( 2, 1 )	: mbmsgs[0x004b],		# "��¼�ɹ�����ʼ��������"	"The client has begun to receive data from the server. This indicates that the conection process is complete."
	( 6, 1 )	: mbmsgs[0x004c],		# "�ӷ������Ͽ�"	"SERVER ERROR: The client has been disconnected from the server."
	}


# -----------------------------------------------------
class Loginer :
	def __init__( self, mgr ) :
		self.__lastStatus = Define.GST_NONE						# ��¼�µ�¼ǰ��״̬
		self.__lockedTime = None								# �˺��Ƿ���ס
		self.__camHandler = LNCamHandler()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __parseDate( date ):
		"""
		��ʱ��������ת��������
		@type  date : int
		@param date : ������ʱ��
		"""
		if int(date) == -1:
			return mbmsgs[0x0024]
		return time.strftime( mbmsgs[0x0025], time.localtime(date) )

	def __onConnected( self, stage, status, msg = "" ) :
		"""
		feedback from server after connection
		"""
		if loginResult.has_key( ( stage, status ) ):
			INFO_MSG( "login info: ", loginResult[( stage, status )], ( stage, status) )
		else:
			INFO_MSG( "login info: no such state.", ( stage, status) )

		if self.__lockedTime:													# �кű�����
			rds.resLoader.cancelCurrLoading()									# ֹͣ��Դ����
			rds.statusMgr.changeStatus( self.__lastStatus )						# ���ص�¼ǰ��״̬
			msg = mbmsgs[0x0023] % self.__parseDate( self.__lockedTime )
			ECenter.fireEvent( "EVT_ON_LOGIN_FAIL", msg )
			return

		if status == -254 :														# ���� WGS Error Message
			msg = re.sub( "^[\d\s]+", "", msg )									# ȥ����Ϣǰ��ĺ���
			ECenter.fireEvent( "EVT_ON_LOGIN_FAIL", msg )
			return

		if stage == 1 and status <= 0 :
			if AutoActWindow.handleFeedback( ( stage, status ) ) :
				return
			if loginResult.has_key( ( stage, status ) ) :
				msg = mbmsgs[0x0021] % loginResult[( stage, status )]
			else :
				msg = mbmsgs[0x0022] % ( stage, status )
			ERROR_MSG( "login fail:( %d, %d )" % ( stage, status ) )
			ECenter.fireEvent( "EVT_ON_LOGIN_FAIL", msg )
		if stage == 6 :															# ����ʧ��
			if not rds.statusMgr.isCurrStatus( Define.GST_LOGIN ) :
				BigWorld.resetEntityManager()
				gameMgr.onDisconnected()
		if stage == 1 and status == 1 :											# ���ӳɹ�
			# �����ӳɹ�ʱ����Ҫ�ص� gameMgr �� onConnected���� onConnected ��
			# ����֪ͨ��Դ���ء������ʱ������˺ű��⣬������������Ժ��ʱ��
			# ����������ʱΪ 0.5 �룩�ص������ onAccountlockedNotify ������
			# ��ʱ�������ɫѡ���еĳ�����Դ���ص��㹻�죨��С�� 0.2 �룩��ô�ܿ���
			# ������뵽��ɫѡ�����ʱ�򣬿ͻ��˲ŵ�֪���˺��Ǳ���ġ�
			# Ϊ�˽�����������⣬������ʱ 0.5 ����֪ͨ���ӳɹ������н�ɫѡ�����Դ����
			BigWorld.callback( 0.5, gameMgr.onConnected )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnter( self ) :
		loginSpace = loginSpaceMgr.loadLoginSpace( Define.LOGIN_TYPE_MAP )
		self.__camHandler.use()
		BigWorld.cameraSpaceID( loginSpace )		# ������������򳡾�
		BigWorld.spaceHold( True )
		self.__camHandler.run()

	def onLeave( self ) :
		pass

	def stopCamera( self ) :
		"""
		�����ֹͣת��
		"""
		self.__camHandler.stop()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def requestLogin( self, server, userName, passwd ) :
		"""
		�����¼
		"""
		self.__lastStatus = rds.statusMgr.currStatus()
		self.__lockedTime = None						# ������ű��
		gameMgr.requestLogin( server, userName, passwd, self.__onConnected )

	def onAccountlockedNotify( self, lockedTime ) :
		"""
		�˺ű���סʱ����
		"""
		self.__lockedTime = lockedTime


# --------------------------------------------------------------------
# implement space manager of roleselector
# --------------------------------------------------------------------
class RoleSelector :
	def __init__( self, mgr ) :
		self.__mgr = mgr
		self.__camShell = FLCShell()			# ���
		self.__camTarget = None					# ����Խ��� entity
		self.__faceRole = None					# ���ڶ�λ����� entity
		self.__vehicleEntity = None				# ������תentity��Բ��entity
		self.__previewRoles = []				# ���ڴ����ʾ��ɫλ�õ�entity
		self.__starePos = ( 0, 0, 0 )			# ������ӵĵ�

		self.__loginRoles = []					# ÿ��Ԫ����һ���ֵ䣬���Ƿ������������Ľ�ɫԭʼ����
		self.__selectable = True				# �Ƿ�����ѡ���ɫ
		self.__gpIndex = 0						# ��ѡ��ɫ������

		self.__roleModels = {}					# { ��ɫ���ݿ�ID : pyModel }

		self.__onPoseTime = False				# ����ʩչʱ�䣬�����������Ϸ
		self.__isVerifySucess = False			# �Ƿ�ͨ��ͼƬ��֤
		self.__loadDefaultModelRoleIDs = []		# ������Ӧģ��ʧ�ܣ��п���ȱ����Դ����ʹ��Ĭ��ģ�����ļ���ģ�͵Ľ�ɫid
		self.__newRoleCreating = False			# �ж��Ƿ������½��˺�״̬
		
	def dispose( self ) :
		"""
		when enter world or accountLogoff, it will be called
		"""
		for ent in self.__previewRoles :
			try :
				BigWorld.destroyEntity( ent.id )
			except :
				DEBUG_MSG( "destroy preview role fail!" )
		self.__previewRoles = []

		try : BigWorld.destroyEntity( self.__faceRole.id )
		except : DEBUG_MSG( "destroy face role fail!" )
		self.__faceRole = None
		try : BigWorld.destroyEntity( self.__camTarget.id )
		except : DEBUG_MSG( "destroy camera target fail!" )
		self.__camTarget = None
		try : BigWorld.destroyEntity( self.__vehicleEntity.id )
		except : DEBUG_MSG( "destroy vehicle entity fail!" )
		self.__vehicleEntity = None

		self.__loginRoles = []
		self.__roleModels = {}
		self.__gpIndex = 0						# ��ѡ��ɫ������


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# ��ʼ������
	# -------------------------------------------------
	def __initCamTarget( self, callback ) :
		"""
		��ʼ������� entity
		"""
		self.__camTarget = None
		self.__faceRole = None
		for entity in BigWorld.entities.values() :
			
			flag = getattr( entity, "flag", None )
			if flag == "RS_CAM_TARGET" :
				self.__camTarget = entity
			elif flag == "RS_FACE_ROLE" :
				self.__faceRole = entity
			if self.__camTarget and self.__faceRole :
				callback( 1 )
				return
		BigWorld.callback( 0.5, Functor( self.__initCamTarget, callback ) )
		ERROR_MSG( "RoleSelector: can't find camera target or facerole entity in role selector!" )

	def __initPosList( self, callback ) :
		"""
		��ʼ����ɫѡ���м��ת��Բ�̼�����Բ���ϵ� entity
		"""
		self.__previewRoles = []
		for entity in BigWorld.entities.values() :						# �ȳ�ʼ���м��ת��Բ��
			flag = getattr( entity, "flag", None )
			if flag == "RS_PLATFORM":
				self.__vehicleEntity = entity
				entity.setToControl()
				break
		if self.__vehicleEntity is None:
			ERROR_MSG( "could't find entity which flag eq PLATFORM." )
			callback( 0 )
			return

		self.__previewRoles = range( 1, 10 )		# Ԥ��9��λ�ã����Ҽ��������9����ɫ��ʵ���ϵ�ǰֻ��3��
		for entity in BigWorld.entities.values() :
			flag = getattr( entity, "flag", None )
			if flag and flag.startswith( "RS_AVATAR_" ):
				# ע����ǰֱ��ʹ��name��������ʾ��(�ǿ�ֵ���񣨿�ֵ����ʹ�ã�Ĭ��name����Ϊ�ա�
				# �꿴self.addRole()��self.__getEmptyEntity()����
				entity.setToControl()
				entity.physics.teleportVehicle( self.__vehicleEntity )		# ʹ�� entity �̶�������� vehicle ��λ��
				self.__previewRoles[int( flag[-1] )] = entity	# ��flag�е�ֵ��˳�����
				# ��ʼ��������¼������ӿ�
				entity.onClick = self.__onClickRole
				entity.onMouseEnter = self.__onMouseEnterRole
				entity.onMouseLeave = self.__onMouseLeaveRole
				entity.oppositeTo( self.__vehicleEntity.position )
				continue

		# ȥ�������ڵ�λ��
		for i in xrange( len( self.__previewRoles ) - 1, -1, -1 ):
			if isinstance( self.__previewRoles[i], int ):
				self.__previewRoles.pop( i )

		if len( self.__previewRoles ) > 0 :
			self.__resortPreviewRoles()						# �����뾵ͷ����Ľ�ɫ�ŵ���һλ
			callback( 1 )
		else :
			callback( 0 )

	def __initStarePos( self, callback ) :
		"""
		��ʼ�����ӵ�
		"""
		patrolPath = self.__camTarget.patrolList
		if not patrolPath.isReady() :
			ERROR_MSG( "RoleSelector: the preview roles direction is not ready!" )
		else :
			nodeID = self.__camTarget.patrolPathNode
			self.__starePos = patrolPath.worldPosition( nodeID )
		callback( 1 )

	def __initCamera( self, callback ) :
		cparam = self.__camShell
		cparam.camera.positionAcceleration = 0.0
		cparam.camera.trackingAcceleration = 0.0
		cparam.setEntityTarget( self.__camTarget )
		cparam.setRadius( 1.5, True )				# ʹ����� entity ��ͬһ�ط�
		cparam.stareAt( self.__starePos )
		callback( 1 )

	# ---------------------------------------
	def __initRoleModels( self, callback ) :
		"""
		�������к�ѡ��ɫģ��
		"""
		loginRoles = copy.deepcopy( self.__loginRoles )
		# �������Ҫ���صĽ�ɫΪ�գ���ֱ��֪ͨ�������
		totalCount = len( loginRoles )
		if totalCount == 0: callback( 1.0 )

		for loginRole in loginRoles:
			roleInfo = RoleInfo( loginRole )
			roleID = roleInfo.getID()
			func = Functor( self.__onRoleModelLoad, callback, roleID, totalCount  )
			rds.roleMaker.createPartModelBG( roleID, roleInfo, func )

	def __initRoleDefaultModels( self, callback, roleID, totalCount ):
		"""
		���ؽ�ɫ��Ĭ��ģ��
		"""
		if roleID in self.__loadDefaultModelRoleIDs:	# �Ƿ��Ѿ����ع�Ĭ��ģ��
			return
		self.__loadDefaultModelRoleIDs.append( roleID )
		loginRole = None
		for info in self.__loginRoles:
			if info["roleID"] == roleID:
				loginRole = dict( info )
				break
		if loginRole is None:
			return
		roleInfo = getDefaultRoleInfo( loginRole )
		func = Functor( self.__onRoleModelLoad, callback, roleID, totalCount  )
		rds.roleMaker.createPartModelBG( roleID, roleInfo, func )
		
	def __onRoleModelLoad( self, callback, roleID, totalCount, model ):
		"""
		ģ�ͼ�����ص�
		"""
		if model is None:	# �п��ܻᷴ������Ҳ�޷����سɹ����³�����ʱ�����������
			self.__initRoleDefaultModels( callback, roleID, totalCount )
			return
			
		self.__roleModels[roleID] = model
		# ֪ͨ ResourceLoader ģ�ͼ������
		currCount = len( self.__roleModels )
		callback( float( currCount/totalCount ) )
		if roleID in self.__loadDefaultModelRoleIDs:
			self.__loadDefaultModelRoleIDs.remove( roleID )
			
	def __showRoles( self, callback ) :
		"""
		��ʾ��ѡ��ɫ
		"""
		roleCount = len( self.__loginRoles ) 			# ��ѡ��ɫ����
		if roleCount == 0 :
			ECenter.fireEvent( "EVT_ON_DESELECT_ROLE" )
		else :
			entCount = len( self.__previewRoles )		# ÿҳ��ɫ����
			count = min( roleCount, entCount )
			for idx in xrange( count ) :
				role = self.__previewRoles[idx]
				self.__resetPreviewRole( role, self.__loginRoles[idx] )
				if role.model: role.model.visible = False
		ECenter.fireEvent( "EVT_ON_RS_PAGE_CHANGED" )
		callback( 1.0 )

	# -------------------------------------------------
	# ˽�� callback
	# -------------------------------------------------
	def __onClickRole( self, role ) :
		"""
		��ĳ����ɫ�����ʱ������
		"""
		self.selectRole( role, True, True )

	def __onMouseEnterRole( self, role ) :
		"""
		��������ĳ��ɫʱ������
		"""
		if role == self.__getFaceEntity() : #ȡ������ƶ�����ǰѡ���ɫʱ��������ʾ�ĸ���Ч����
			try:
				role.model.enableShine = False
			except:
				pass

	def __onMouseLeaveRole( self, role ) :
		"""
		������뿪ĳ��ɫʱ������
		"""
		pass


	# -------------------------------------------------
	# ����˽�з���
	# -------------------------------------------------
	def __getEntity( self, roleID ) :
		"""
		���ݽ�ɫ dbid����ȡ��ɫ�� entity
		"""
		for role in self.__previewRoles :
			roleInfo = role.roleInfo
			if not roleInfo : continue
			if role.name == "yes" and \
				roleInfo.getID() == roleID :
					return role
		return None

	def __getEmptyEntity( self ) :
		"""
		��ȡһ���յ�λ��
		"""
		for e in self.__previewRoles :
			if e.name == '' :
				return e
		return None

	def __getFaceEntity( self, used = True ) :
		"""
		�ҳ�������������һ����ɫ��used �Ƿ�ֻ������ģ�͵�
		"""
		role = self.__previewRoles[0]
		minDst = role.position.distTo( self.__camTarget.position )
		for r in self.__previewRoles :
			if r == role : continue
			dst = r.position.distTo( self.__camTarget.position )
			if dst > minDst : continue
			minDst = dst
			role = r
		if not used or role.name == "yes" :
			return role
		return None

	# -------------------------------------------------
	def __resortPreviewRoles( self ) :
		"""
		�����뾵ͷ����Ľ�ɫ�ŵ���һλ
		"""
		role = self.__getFaceEntity( False )
		self.__previewRoles.remove( role )
		self.__previewRoles.insert( 0, role )

	def __resetRolesYaw( self ):
		"""
		�������ý�ɫ������
		"""
		for role in self.__previewRoles :
			role.oppositeTo( self.__vehicleEntity.position )

	# -------------------------------------------------
	def __resetPreviewRole( self, role, loginRole ) :
		"""
		����һ�� PreviewRole ��ģ��
		"""
		if loginRole is None :
			role.clearAttachments()
			role.name = ""
			role.setModel( None )
			role.setInfo( None )
		else :
			role.name = "yes"
			roleInfo = RoleInfo( loginRole )
			role.setInfo( roleInfo )
			model = self.__roleModels.get( roleInfo.getID(), None )
			if model :
				role.onPartModelLoad( model )
				role.attach( AttachName() )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnter( self ) :
		"""
		when entered role selector, it will be called
		"""
		self.__resetRolesYaw()

		BigWorld.camera( self.__camShell.camera )
		self.__camShell.camera.viewOffset = 0, 0, -0.2

		for role in self.__previewRoles:
			if role.model:
				role.model.visible = True

		if self.__newRoleCreating:
			return

		entity = self.__getFaceEntity()								# ��ȡ��ǰѡ�еĽ�ɫ
		if entity is None: return
		self.selectRole( entity, False, True )

	def onLeave( self, newStatus ) :
		"""
		when left role selector, it will be called
		"""
		if newStatus != Define.GST_ROLE_CREATE:
			self.__roleModels = {}
		self.__isVerifySucess = False
		self.unlockContrl()
		for role in self.__previewRoles:
			if role.model:
				role.model.visible = False

	# -------------------------------------------------
	def getLoginRolesCount( self ):
		"""
		����Ѿ������Ľ�ɫ����
		"""
		return len( self.__loginRoles )

	def onInitRoles( self, loginRoles ) :
		"""
		when logined, informations of all roles in the account will receive
		@type			loginRoles : list of dictionary
		@param			loginRoles : [LOGIN_ROLE defined in alias.xml, ... ]
		"""
		self.__loginRoles = loginRoles
		historyID = gameMgr.getAccountOption( "selRoleID" )			# ��ȡ�ϴ�ѡ��Ľ�ɫ������wsf
		historyLoginRole = None										# ǰһ�ν�����Ϸ�Ľ�ɫ
		for index,loginRole in enumerate( loginRoles ):				# ����ǰһ�ν�����Ϸ�Ľ�ɫ
			if loginRole["roleID"] == historyID :
				for i,v in enumerate( loginRoles[index:] ):
					historyLoginRole = loginRole
					self.__loginRoles.remove( v )				# ����ǰһ�ν�����Ϸ�Ľ�ɫ
					if historyLoginRole is not None :
						self.__loginRoles.insert( i, v )			# ��ǰһ�ν�����Ϸ�Ľ�ɫ�ŵ���һλ
				break

	def onAddRole( self, loginRole ) :
		"""
		call to add a preview role
		"""
		self.__loginRoles.append( loginRole )
		self.__onPoseTime = False
		roleInfo = RoleInfo( loginRole )
		def callback( model ):
			"""
			ģ�ͼ�����ص�
			"""
			BigWorld.callback( 0.38, self.__resetRolesYaw )
			if model is None :
				ERROR_MSG( "create role model fail which id is %i!" % roleInfo.getID() )
				return
			self.__roleModels[roleInfo.getID()] = model
			role = self.__getEmptyEntity()
			if not role : return
			self.__resetPreviewRole( role, loginRole )
			self.selectRole( role, False, False )							# ѡ���´����Ľ�ɫ
		rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, callback )

	def onDeleteRole( self, roleID ) :
		"""
		call to delete a preview role
		"""
		for loginRole in self.__loginRoles[:] :						# �ӽ�ɫ�б������
			if loginRole['roleID'] == roleID :
				self.__loginRoles.remove( loginRole )
				break
		if roleID in self.__roleModels :
			self.__roleModels.pop( roleID )							# ��ģ���б���ȥ����ɫ��Ӧ��ģ��
		role = self.__getEntity( roleID )
		if role is None : return
		self.__resetPreviewRole( role, None )						# �����ɫģ�ͱ���
		ECenter.fireEvent( "EVT_ON_DESELECT_ROLE" )

	def onNameChanged( self, roleID, newName ) :
		"""
		��ɫ���ָı�
		"""
		for loginRole in self.__loginRoles :						# ���ҽ�ɫ
			if loginRole['roleID'] == roleID :
				loginRole['roleName'] = newName
				role = self.__getEntity( roleID )
				if role is None : return
				role.setInfo( RoleInfo( loginRole ) )
				ECenter.fireEvent( "EVT_ON_RENAME_ROLE_SUCCESS", roleID, newName )
				break

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getInitializers( self ) :
		"""
		��ȡ��ʼ������ÿ����ʼ��������ʼ���ɹ���һ��Ҫ���� True
		"""
		return [
			self.__initCamTarget,				# ��ʼ������� entity
			self.__initPosList,					# ��ʼ��������
			self.__initStarePos,				# ��ʼ��������ӵ�
			self.__initCamera,					# ��ʼ�����
			self.__initRoleModels,				# ��ʼ����ѡ��ɫģ�ͣ���̨��
			self.__showRoles,					# ��ʾ��ɫģ��
			]

	# -------------------------------------------------
	def getRoleCount( self ) :
		"""
		��ȡ��ѡ��ɫ����
		"""
		return len( self.__loginRoles )

	def getPreviewCount( self ) :
		"""
		��ȡÿҳ��ɫ����
		"""
		return len( self.__previewRoles )

	def getPageCount( self ) :
		"""
		��ȡ��ҳ��ҳ��
		"""
		roleCount = len( self.__loginRoles )						# ��ѡ��ɫ����
		viewCount = len( self.__previewRoles )						# ÿ���ɫ�ĸ���
		return int( math.ceil( float( roleCount ) / viewCount ) )

	def getSelectedRoleInfo( self ) :
		"""
		��ȡѡ�н�ɫ����Ϣ
		"""
		faceRole = self.__getFaceEntity()
		role = self.__getFaceEntity( False )
		if role == faceRole :
			return role.roleInfo
		return None

	# -------------------------------------------------
	def nextGroup( self ) :
		"""
		ת����һ���ѡ��ɫ
		"""
		self.setlectGroup( self.__gpIndex + 1 )
		if self.getPageCount() <= 1 :
			ECenter.fireEvent( "EVT_ON_RS_PAGE_CHANGED" )

	# -------------------------------------------------
	def setlectGroup( self, gpIdx ) :
		"""
		����������
		"""
		roleCount = len( self.__loginRoles )						# ��ѡ��ɫ����
		if not roleCount :											# û���κν�ɫ
			ECenter.fireEvent( "EVT_ON_DESELECT_ROLE" )
			return

		for role in self.__previewRoles :							# ���������ģ��
			self.__resetPreviewRole( role, None )					# �������������潫�޷�����

		gpCount = self.getPageCount()								# ������
		gpIdx = gpIdx % gpCount										# ��������������Ҫ�����������
		self.__gpIndex = gpIdx

		startIdx = gpIdx * len( self.__previewRoles )				# ��ʼ����
		for i, role in enumerate( self.__previewRoles ) :
			index = startIdx + i
			if index < roleCount :
				self.__resetPreviewRole( role, self.__loginRoles[index] )

	def selectRole( self, role, slowly, isPose = True ) :
		"""
		ѡ��һ����ɫ
		slowly				: �Ƿ�������ת��Բ̨ѡ��
		isPose				: �Ƿ񲥷�pose����
		"""
		if not self.__selectable : return
		self.lockContrl()
		func = Functor( self.onSelectRoleArrived, role, slowly, isPose )
		if slowly :
			self.__vehicleEntity.sostenutoRotate( role.position, \
				self.__faceRole.position, 0.1, 0.005, func, self.rotating )	# ����ת��
		else :
			self.__vehicleEntity.instantRotate( role.position, self.__faceRole.position, func )

	def rotating( self, yaw ):
		"""
		�����ƶ��еĻص�
		"""
		self.__resetRolesYaw()

	def onSelectRoleArrived( self, role, slowly, isPose, success = True ):
		"""
		ѡ���ɫת��ת��Ŀ���
		"""
		self.unlockContrl()
		if not success: return
		ECenter.fireEvent( "EVT_ON_SELECT_ROLE" )
		role.switchRandomAction( True )									# �����������
		if isPose:
			func = Functor( self.onPlayerPoseActionOver, role )
			self.__onPoseTime = True
			INFO_MSG( "set pose flag true." )
			if not role.playPoseAction( cb = func ):							# ����ѡ�н�ɫ����
				self.__onPoseTime = False
				
		BigWorld.callback( 0.5, self.__resortPreviewRoles )				# ���½�����ͷ����Ľ�ɫ�ŵ��б�ĵ�һλ
		if not slowly :													# �����˲��ת��
			self.__resetRolesYaw()										# ��ת����Ϻ��������ý�ɫ����

	def onPlayerPoseActionOver( self, role ):
		"""
		��ɫpose����������ϻص�
		"""
		INFO_MSG( "Pose over." )
		if role is None: 
			INFO_MSG( "Role is none." )
			return
		selectRoleInfo = self.getSelectedRoleInfo()
		if selectRoleInfo and selectRoleInfo.getID() == role.roleInfo.getID():
			self.__onPoseTime = False
			INFO_MSG( "set pose flag false." )
			if self.__isVerifySucess:
				rds.gameMgr.enterGame()

	# ---------------------------------------
	def lockContrl( self ) :
		"""
		��ס��������ѡ���ɫ
		"""
		self.__selectable = False
		ECenter.fireEvent( "EVT_ON_LOST_CONTROL" )

	def unlockContrl( self ) :
		"""
		����������ѡ���ɫ
		"""
		self.__selectable = True
		ECenter.fireEvent( "EVT_ON_GOT_CONTROL" )

	# -------------------------------------------------
	def renameSelRole( self, newName ) :
		"""
		��������ɫ
		"""
		roleInfo = self.getSelectedRoleInfo()
		if not roleInfo : return
		BigWorld.player().base.changeName( roleInfo.getID(), newName )

	# -------------------------------------------------
	def createRole( self ) :
		"""
		leave role selector
		"""
		rds.statusMgr.changeStatus( Define.GST_ROLE_CREATE )

	def deleteRole( self, roleID, roleName ) :
		"""
		call to delete a role
		@type			roleID : INT 64
		@param			roleID : the role's database id
		"""
		BigWorld.player().deleteRole( roleID, roleName )

	def enterGame( self ) :
		"""
		call to let the current selected role to enter game
		"""
		roleInfo = self.getSelectedRoleInfo()
		if roleInfo is None :
			ERROR_MSG( "no select role!" )
		else :
			gameMgr.setAccountOption( "selRoleID", roleInfo.getID() )		# ������Ϸ���������һ��ѡ��Ľ�ɫ index��wsf
			rds.gameMgr.requestEnterGame( roleInfo )

	def cleanAvatars( self ) :
		"""
		�����н�ɫģ�����
		"""
		for role in self.__previewRoles :
			self.__resetPreviewRole( role, None )

	def onVerifySuccess( self ):
		"""
		��֤ͼƬͨ��
		"""
		self.__isVerifySucess = True
		if self.__onPoseTime: 
			INFO_MSG( "Role in pose!" )
			return
		rds.gameMgr.enterGame()

# --------------------------------------------------------------------
# implement space manager of rolecreator
# --------------------------------------------------------------------
class RoleCreator :
	__cc_close_radius	= 1.0							# ����ͷ
	__cc_far_radius		= 2.5							# Զ��ͷ

	def __init__( self, mgr ) :
		self.__mgr = mgr
		self.__camHandler = RCCamHandler()				# ���
		self.__dsps = {}								# ְҵ����
		self.__selectRole = None
		self.__spaceID =  0
		self.__faceRole = None							# ���ڶ�λ����� entity
		self.__yaw = 0.0 #ѡ�еĽ�ɫ�ĳ���ı�ֵ
		#self.__avatar = None							# ��ɫ
		self.__camYaw = 0								# ��� yaw ֵ
		self.__turnRoleCBID = 0							# ��ת��ɫ�� callbackID
		self.__currCamp = csdefine.ENTITY_CAMP_NONE		# ��ǰѡ��Ľ�ɫ��Ӫ
		self.__currGender = None						# ��ǰѡ��Ľ�ɫ�Ա�
		self.__currProfession = None					# ��ǰѡ��Ľ�ɫְҵ
		self.__roleModels = {}							# ����ְҵ���Ա��Ӧ��ģ��
		self.__allModelInfo = {}						# ����ְҵ���Ա��Ӧ��ģ��info
		self.__currHairNum = 0							# ��ǰѡ��ķ��ͱ��
		self.__currFaceNum = 0							# ��ǰѡ������ͱ��
		self.__currHeadTextureID = 0					# ��ǰѡ���ͷ���� by����
		self.__canSelectRoles = []
		self.cbid = 0
		self.__selectedCampEn = None #ѡ�е���Ӫentity
		self.__models = {}
		self.__models[ csdefine.ENTITY_CAMP_TAOISM ] = ( BigWorld.Model( Const.EMPTY_MODEL_PATH ), Pixie.create( Sources.PARTICLE_CAMP_TAOISM ) )
		self.__models[ csdefine.ENTITY_CAMP_DEMON ]  = ( BigWorld.Model( Const.EMPTY_MODEL_PATH ), Pixie.create( Sources.PARTICLE_CAMP_DEMON ) )
		self.onBackToSelector = False #�Ƿ����˳���ѡ���ɫ����Ĳ���

	def dispose( self ) :
		BigWorld.cancelCallback( self.cbid )
		self.__faceRole = None
		#self.__avatar = None
		self.__currCamp = csdefine.ENTITY_CAMP_NONE
		self.__currGender = None
		self.__currProfession = None
		self.__selectRole = None
		self.__canSelectRoles = []
		#��������������CameraEntity
		for en in BigWorld.entities.values():
			if en.__class__.__name__ == "CameraEntity":
				BigWorld.destroyEntity( en.id )
		self.cbid = 0

	def getSelectRole( self ):
		return self.__selectRole
	
	def loadModelSource( self ):
		"""
		Ԥ����ģ����Դ
		"""
		for profession in ROLE_PROFESSION:
			for gender in ROLE_GENDER:
			    roleInfo = getCommonRoleInfo( profession, gender )
			    func = Functor( self.onModelLoadCompleted2, roleInfo )
			    rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )
	
	def onModelLoadCompleted2( self, roleInfo, model ):
		"""
		ģ�ͼ�����ص�
		"""
		self.onCreateModelLoad( roleInfo, model )

	def showAllEntities( self ) :
		"""
		��ʼ������ entity
		"""
		canSelectRoles = []
		self.__canSelectRoles = []
		for entity in BigWorld.entities.values() :
			flag = getattr( entity, "flag", None )
			if flag and flag.startswith( "RC_AVATAR_" ) and entity.spaceID == self.getSpaceID() :
				entity.onMouseEnter = self.__onMouseEnterRole
				entity.onClick = self.__onClickRole
				entity.setToControl()
				canSelectRoles.append( entity )
		if len( canSelectRoles ) != 8:
			BigWorld.callback( 0.1, self.showAllEntities )
			return
		for en in canSelectRoles:
			flag = en.flag
			profession = int( flag[-2:] )
			gender     = int( flag[-3] )
			self.__canSelectRoles.append( en )
			roleInfo = getCommonRoleInfo( profession, gender )
			roleInfo._RoleInfo__level = 0
			func = Functor( self.onModelLoadCompleted1, roleInfo, en )
			rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )

	def onModelLoadCompleted1( self, roleInfo, entity, model ):
		"""
		ģ�ͼ�����ص�
		"""
		if self.__selectRole: #����Ѿ�ѡ����Ҫ�����Ľ�ɫ����Ҫ��ʾ��
			model.visible = False
		entity.setInfo( roleInfo )
		entity.setModel( model )
		self.onCreateModelLoad( roleInfo, model )
		entity.attach( AttachName() )
		yaw = self.getPreviewRoleYaw( roleInfo )
		entity.turnaroundToYaw( yaw )
		entity.model.action(P_D_M_T_CAMERA[self.getCamp()][2])()
	
	def checkRoleCreate( self, callback ):
		"""
		���8��role�Ƿ�������
		"""
		canSelectRoles = []
		for entity in BigWorld.entities.values() :
			flag = getattr( entity, "flag", None )
			if flag and flag.startswith( "RC_AVATAR_" ) and entity.spaceID == self.getSpaceID() and entity.getModel() :
				canSelectRoles.append( entity )
		if len( canSelectRoles ) != 8:
			BigWorld.callback( 0.1, Functor(self.checkRoleCreate,callback) )
		else:
			callback( 1.0 )
	
	def getPreviewRoleYaw( self, roleInfo ):
		"""
		��ȡĳ����ɫ�ĳ���
		"""
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		camp = self.getCamp()
		yaw = ALL_PREVIEWROLE_MAP[camp][profession][gender]
		return yaw
	
	def resetCamp( self, camp ) :
		"""
		reset camp of all preview roles
		"""
		self.__currCamp = camp
	
	def getCamp( self ):
		return self.__currCamp
	
	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnterSelectCamp( self ) :
		"""
		when entered role creator it will be called
		����������˳���ťҲ�ᴥ��������
		"""
		self.cancelSelectedCamp()
		self.__currCamp = csdefine.ENTITY_CAMP_NONE
		self.__currGender = None
		self.__currProfession = None
		self.__roleModels = {}
		self.__selectRole = None
		self.__spaceID =  0
		self.__canSelectRoles = []
		self.cbid = 0
		self.__camHandler.use( self.__camYaw )
		self.loadSelectCampInfo()
		ECenter.fireEvent( "EVT_ON_CAMP_SELECTOR_SHOW" )
		ECenter.fireEvent( "EVT_ON_HIDE_ROLE_SELECTOR" )
	
	def loadSelectCampInfo( self ):
		"""
		������Ӫѡ����桢ģ�͵������Դ
		"""
		self.preLoadSpace( Define.SELECT_CAMP_TYPE_MAP )
		spaceID = self.getSpaceID()
		self.checkCreateOver( )
	
	def checkCreateOver( self ):
		"""
		����Ƿ��Ѿ��������
		"""
		cameraEntities = []
		for en in BigWorld.entities.values():
			if en.__class__.__name__ == "CameraEntity" and en.spaceID == self.getSpaceID() and en.getModel():
				cameraEntities.append( en )
		if len(cameraEntities) == 2 :
			for entity in cameraEntities:
				entity.isAlwaysExist = True
				entity.setSelectable( True )# ���� targetCaps ����
				entity.selectable = True
				entity.onMouseEnter = self.onEnterCampEntity
				entity.onMouseLeave = self.onLeaveCampEntity
				entity.onClick = self.onClickCampEntity
				model = self.__models[entity.flagID][0]
				if len( entity.models ) == 0 :
					entity.addModel( model )
					model.position = entity.position
		else:
			BigWorld.callback( 0.1, self.checkCreateOver ) #��һ���ӳ�ʱ��

	def cancelSelectedCamp( self ):
		"""
		ȡ����ǰ����Ӫѡ��
		"""
		if self.__selectedCampEn:
			self.__selectedCampEn.model.enableShine = False
			self.delEffect( self.__selectedCampEn )
		self.__selectedCampEn = None

	def onEnterCampEntity( self, en ):
		if self.__selectedCampEn:
			return
		en.model.enableShine = True
		self.addEffect( en )
	
	def onLeaveCampEntity( self, en ):
		if self.__selectedCampEn:
			return
		en.model.enableShine = False
		self.delEffect( en )

	def onClickCampEntity( self, en ):
		"""
		"""
		if self.__selectedCampEn:
			return
		self.__selectedCampEn = en
		self.addEffect( en )
		en.model.enableShine = True
		ECenter.fireEvent( "EVT_ON_ROLECREATOR_CAMP_CHANGED", en.flagID )
	
	def addEffect( self, en ):
		"""
		�����Ĺ�Ч
		"""
		if len( self.__models[en.flagID][0].root.attachments ) == 0:
			self.__models[en.flagID][0].root.attach( self.__models[en.flagID][1] )
	
	def delEffect( self, en ):
		"""
		ɾ����Ч
		"""
		if len( self.__models[en.flagID][0].root.attachments ) == 1:
			self.__models[en.flagID][0].root.detach( self.__models[en.flagID][1] )
	
	def startEnterRoleCreator( self, camp ):
		"""
		��Ӫѡ����������봴����ɫ��ͼ
		"""
		def readyCallback() :
			self.onEnterRoleCreate( camp )
		self.resetCamp( camp )
		rds.resLoader.loadCreatorSpace( readyCallback )
		if self.__selectedCampEn:
			self.__selectedCampEn.model.enableShine = False
			self.delEffect( self.__selectedCampEn )
		self.__selectedCampEn = None

	def preLoadSomething( self, callback ):
		"""
		����ѡ���ɫ��ͼ����Ҫ�ȼ���һЩ����
		"""
		camp = self.__currCamp
		self.preLoadSpace( camp )
		callback( 1.0 )
	
	def preLoadSpace( self, camp ):
		"""
		�ȼ��ص�ͼ
		"""
		loginSpace = loginSpaceMgr.loadLoginSpace( camp )
		self.__spaceID = loginSpace
		BigWorld.cameraSpaceID( loginSpace )	
		BigWorld.spaceHold( True )
		try:
			pos = P_D_M_T_CAMERA[camp][0]
			dir = P_D_M_T_CAMERA[camp][1]
			self.__camHandler.use( self.__camYaw )
			cc = BigWorld.camera()
			m = Math.Matrix()
			m.setTranslate( pos )							# ���㵽 space ������� chunk ��������
			cc.target = m								# ʹ�ó�������ʱ������ּ���λ�ò���
			self.__camHandler.disable() #������޷���ת
			
			#���ýǶ�ֵ
			#cc.source.setRotateYPR( dir )
			self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
			self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
			self.__camHandler.cameraShell.update()
			cc.pivotMaxDist = 1.1
		except:	# ��Ϊ�������ط�Χ�Ǹ������λ����ȷ����
			pass
	
	def initRoleEntity( self, callback ):
		"""
		��ʼ����ͼ8����ɫʵ��
		"""
		self.showAllEntities()
		callback( 1.0 )
	
	def onEnterRoleCreate( self, camp ):
		"""
		���봴����ɫ����
		"""
		self.resetCamp( camp )
		ECenter.fireEvent( "EVT_ON_ROLE_CREATOR_SHOW" )
		loginSpace = self.getSpaceID()
		DEBUG_MSG( "RoleCreator enter space", loginSpace )
		BigWorld.cameraSpaceID( loginSpace )							# ������������򳡾�
		BigWorld.spaceHold( True )
		try:
			pos = P_D_M_T_CAMERA[camp][0]
			dir = P_D_M_T_CAMERA[camp][1]
			self.__camHandler.use( self.__camYaw )
			cc = BigWorld.camera()
			m = Math.Matrix()
			m.setTranslate( pos )			# ���㵽 space ������� chunk ��������
			cc.target = m				# ʹ�ó�������ʱ������ּ���λ�ò���
			
			self.__camHandler.disable() #������޷���ת
			#���ýǶ�ֵ
			self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
			self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
			self.__camHandler.cameraShell.update()
			cc.pivotMaxDist = 1.1
		except:	# ��Ϊ�������ط�Χ�Ǹ������λ����ȷ����
			pass

	def getSpaceID( self ):
		"""
		���spaceID
		"""
		return self.__spaceID
	
	def onBackRoleCreate( self ):
		"""
		����ѡ��Ҫ�����Ľ�ɫ����(��һ����ť)
		"""
		self.showAllEntities()
		self.__selectRole = None
		self.__yaw = 0.0
		camp = self.__currCamp
		try:
			pos = P_D_M_T_CAMERA[camp][0]
			dir = P_D_M_T_CAMERA[camp][1]
			cc = BigWorld.camera()
			m = Math.Matrix()
			m.setTranslate( pos )							# ���㵽 space ������� chunk ��������
			cc.target = m								# ʹ�ó�������ʱ������ּ���λ�ò���
			
			self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
			self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
			self.__camHandler.cameraShell.update()
			cc.pivotMaxDist = 1.1
		except:	# ��Ϊ�������ط�Χ�Ǹ������λ����ȷ����
			pass

	def onLeave( self ) :
		"""
		when left role creator it will be called
		"""
		self.__currCamp = csdefine.ENTITY_CAMP_NONE
		self.__currGender = None
		self.__currProfession = None
		self.__roleModels = {}
		self.__selectRole = None
		self.__spaceID =  0
		self.__canSelectRoles = []
		self.cbid = 0
		

	def __onMouseEnterRole( self, role ) :
		"""
		��������ĳ��ɫʱ������
		"""
		if role == self.__selectRole : #ȡ������ƶ�����ǰѡ���ɫʱ��������ʾ�ĸ���Ч����
			try:
				role.model.enableShine = False
			except:
				pass

	def __onClickRole( self, role ):
		"""
		�����ѡ��ĳ��ɫʱ������
		"""
		if self.__selectRole: return
		self.__selectRole = role
		self.__yaw = role.yaw
		role.clearAttachments()
		role.playPoseAction( cb = self.onSelectedOver )
		#����������ɫ
		for en in self.__canSelectRoles:
			if en.id != role.id and en.model:
				en.model.visible = False
		#�����λ�øı�			
		self.__camHandler.cameraShell.setEntityTarget( role )
		camp = self.__currCamp
		dir = P_D_M_T_CAMERA[camp][1]
		self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
		self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
		self.__camHandler.cameraShell.update()
		
	def onSelectedOver( self ):
		"""
		ѡ�н�ɫ���궯���ص�
		"""
		role = self.getClickRole()
		profession = role.roleInfo.getClass()
		gender     = role.roleInfo.getGender()
		ECenter.fireEvent( "EVT_ON_ROLE_CREATOR_COMPLETE_SHOW" )
		ECenter.fireEvent( "EVT_ON_ROLECREATOR_PROFESSION_CHANGED", profession )
		ECenter.fireEvent( "EVT_ON_ROLECREATOR_GENDER_CHANGED", gender )
		self.__currGender = gender
		self.__currProfession = profession
	
	def getClickRole( self ):
		"""
		ѡ�еĽ�ɫ
		"""
		return self.__selectRole

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		self.__camHandler.handleKeyEvent( down, key, mods )

	def handleMouseEvent( self, dx, dy, dz ) :
		self.__camHandler.handleMouseEvent( dx, dy, dz )

	# -------------------------------------------------
	#def getInitializers( self ) :
	#	"""
	#	��ȡ���г�ʼ������ÿ����ʼ��������ʼ���ɹ���һ��Ҫ���� True
	#	"""
	#	initializers = [
	#		self.__initEntities
	#		]
	#	initializers.append( self.__initialize )
	#	return initializers

	# -------------------------------------------------
	def selectProfession( self, profession ) :
		"""
		"""
		if self.__currProfession == profession: return
		self.__currHairNum = 0
		self.__currFaceNum = 0
		self.__currProfession = profession
		self.__selectRole.setModel( None )
		ECenter.fireEvent( "EVT_ON_ROLECREATOR_PROFESSION_CHANGED", profession )
		
		if self.__currGender is None: return
		gender = self.__currGender
		key = gender | profession
		model = self.__roleModels.get( key )
		if model is None:
			roleInfo = getCommonRoleInfo( profession, gender )
			func = Functor( self.onModelLoadCompleted, roleInfo )
			rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )
		else:
			info = self.__allModelInfo.get( key )
			self.__selectRole.setInfo( info )
			self.__selectRole.setModel( model )
			self.__selectRole.playPoseAction()
			model.visible = True
			yaw = self.getPreviewRoleYaw( info )
			self.__selectRole.turnaroundToYaw( yaw )

	def resetGender( self, gender ) :
		"""
		reset gender of all preview roles
		"""
		if self.__currGender == gender: return
		self.__currHairNum = 0
		self.__currFaceNum = 0
		self.__currGender = gender
		self.__selectRole.setModel( None )
		ECenter.fireEvent( "EVT_ON_ROLECREATOR_GENDER_CHANGED", gender )

		if self.__currProfession is None: return
		profession = self.__currProfession
		key = gender | profession
		model = self.__roleModels.get( key )
		if model is None:
			roleInfo = getCommonRoleInfo( profession, gender )
			func = Functor( self.onModelLoadCompleted, roleInfo )
			rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )
		else:
			info = self.__allModelInfo.get( key )
			self.__selectRole.setInfo( info )
			self.__selectRole.setModel( model )
			self.__selectRole.playPoseAction()
	
	

	def selectHair( self, hairNum ):
		"""
		ѡ����
		"""
		def onHairModelLoad( hairModel ):
			"""
			"""
			if gender != self.__currGender: return
			if profession != self.__currProfession: return
			key = "HP_head"
			rds.effectMgr.linkObject( self.__selectRole.model, key, hairModel )
			rds.actionMgr.playAction( hairModel, Const.MODEL_ACTION_HAIR_BONE_1 )

		gender = self.__currGender
		profession = self.__currProfession
		rds.roleMaker.createHairModelBG( hairNum, 0, profession, gender, onHairModelLoad )
		self.__currHairNum = hairNum

	def selectFace( self, faceNum ):
		"""
		ѡ������
		"""
		def onFaceModelLoad( model ):
			func = Functor( onDelay, model )
			BigWorld.callback( 0.1, func )

		def onDelay( model ):
			if gender != self.__currGender: return
			if profession != self.__currProfession: return
			self.onCreateModelLoad( info, model )
			self.__selectRole.setModel( model )

		gender = self.__currGender
		profession = self.__currProfession
		info = getCommonRoleInfo( profession, gender )
		info.update( {"faceNumber" : faceNum } )
		info.update( {"hairNumber" : self.__currHairNum } )
		rds.roleMaker.createPartModelBG( info.getID(), info, onFaceModelLoad )
		self.__currFaceNum = faceNum
		self.__selectRole.setInfo( info )

	def selectHead( self, headIndex ):
		"""
		ѡ��ͷ��
		"""
		self.__currHeadTextureID = headIndex

	def onModelLoadCompleted( self, roleInfo, model ):
		"""
		ģ�ͼ�����ص�
		"""
		gender = roleInfo.getGender()
		profession = roleInfo.getClass()
		key = gender | profession
		self.__roleModels[key] = model
		self.__allModelInfo[key] = roleInfo
		self.onCreateModelLoad( roleInfo, model )
		# ����ص���ʱ���ģ�Ͳ�����ҵ����Ҫ��ģ�;�return
		if self.__currProfession is None: return
		if self.__currGender is None: return
		if key != ( self.__currProfession | self.__currGender ):return
		self.__selectRole.setInfo( roleInfo )
		self.__selectRole.setModel( model )
		model.visible = True
		self.__selectRole.playPoseAction()
		self.__selectRole.physics.teleport( self.__selectRole.position, ( self.__camYaw, 0, 0 ) )
		yaw = self.getPreviewRoleYaw( roleInfo )
		self.__selectRole.turnaroundToYaw( yaw )

	def weaponAttachEffect( self, model, weaponDict ):
		"""
		������������Ч��
		@type		model 		: pyModel
		@param		model 		: ģ��
		@type		weaponDict 	: FDict
		@param		weaponDict 	: ��������
		"""
		pType = Define.TYPE_PARTICLE_PLAYER
		# ģ��Dyes
		dyes = rds.roleMaker.getMWeaponModelDyes( weaponDict )
		rds.effectMgr.createModelDye( model, dyes )
		# �Դ���Ч
		weaponNum = weaponDict["modelNum"]

		effectIDs = rds.itemModel.getMEffects( weaponNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, pType, pType )
			effect.start()

		# ��Ƕ��Ч
		stAmount = weaponDict["stAmount"]
		xqHp = rds.equipParticle.getXqHp( stAmount )
		xqGx = rds.equipParticle.getXqGx( stAmount )
		for hp, particle in zip( xqHp, xqGx ):
			rds.effectMgr.createParticleBG( model, hp, particle, type = pType )
		# ǿ���Է���
		intensifyLevel = weaponDict["iLevel"]
		if intensifyLevel >= Const.EQUIP_WEAPON_GLOW_LEVEL:
			paths = rds.roleMaker.getMWeaponModelPath( weaponDict )
			if len( paths ) == 0: return
			weaponKey = paths[0]
			type = rds.equipParticle.getWType( weaponKey )
			texture = rds.equipParticle.getWTexture( weaponKey )
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, intensifyLevel )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )
			
	def onCreateModelLoad( self, roleInfo, model ):
		"""
		��ɫ�����������������ģ�ͼ�����ص�
		"""
		def onLoadRightModel( rightModel ):
			def onRightLoftLoad( particle ):
				"""
				���ֵ���������
				"""
				if particle is None: return
				rds.effectMgr.attachObject( rightModel, loftHP, particle )
			
			self.weaponAttachEffect( rightModel, roleInfo.getRHFDict() ) 
			key = "HP_right_hand"
			rds.effectMgr.linkObject( model, key, rightModel )
			hps = []
			particles = []
			profession = roleInfo.getClass()
			if profession == csdefine.CLASS_SWORDMAN:
				loftHP = Const.LOFT_SWORDMAN_HP
				rds.effectMgr.pixieCreateBG( Const.LOFT_SWORDMAN, onRightLoftLoad )
				hps = Const.ROLE_CREATE_SWORDMAN_HP
				particles = Const.ROLE_CREATE_SWORDMAN_PATH
			elif profession == csdefine.CLASS_FIGHTER:
				loftHP = Const.LOFT_FIGHTER_HP
				rds.effectMgr.pixieCreateBG( Const.LOFT_FIGHTER, onRightLoftLoad )
				#hps = Const.ROLE_CREATE_FIGHTER_HP
				#particles = Const.ROLE_CREATE_FIGHTER_PATH
			elif profession == csdefine.CLASS_MAGE:
				hps = Const.ROLE_CREATE_MAGE_HP
				particles = Const.ROLE_CREATE_MAGE_PATH

			for hp, particle in zip( hps, particles ):
				rds.effectMgr.createParticleBG( rightModel, hp, particle, type = Define.TYPE_PARTICLE_PLAYER )

		def onLoadLeftModel( leftModel ):
			def onLeftLoftLoad( particle ):
				"""
				���ֵ���������
				"""
				if particle is None: return
				rds.effectMgr.attachObject( leftModel, loftHP, particle )
			self.weaponAttachEffect( leftModel, roleInfo.getLHFDict() ) 
			profession = roleInfo.getClass()
			key = "HP_left_shield"
			if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
				key = "HP_left_hand"
			rds.effectMgr.linkObject( model, key, leftModel )

			hps = []
			particles = []
			if profession == csdefine.CLASS_SWORDMAN:
				loftHP = Const.LOFT_SWORDMAN_HP
				rds.effectMgr.pixieCreateBG( Const.LOFT_SWORDMAN, onLeftLoftLoad )
			elif profession == csdefine.CLASS_ARCHER:
				hps = Const.ROLE_CREATE_ARCHER_HP
				particles = Const.ROLE_CREATE_ARCHER_PATH

			for hp, particle in zip( hps, particles ):
				rds.effectMgr.createParticleBG( leftModel, hp, particle, type = Define.TYPE_PARTICLE_PLAYER )

		def onHairModelLoad( hairModel ):
			key = "HP_head"
			rds.effectMgr.linkObject( model, key, hairModel )

		profession = roleInfo.getClass()
		gender = roleInfo.getGender()

		# ����
		rds.roleMaker.createHairModelBG( roleInfo.getHairNumber(), 0, profession, gender, onHairModelLoad )
		# ����������
		rds.roleMaker.createMWeaponModelBG( roleInfo.getRHFDict(), onLoadRightModel )
		rds.roleMaker.createMWeaponModelBG( roleInfo.getLHFDict(), onLoadLeftModel )
		# ����
		bodyFDict = roleInfo.getBodyFDict()
		feetFDict = roleInfo.getFeetFDict()
		
		############�ز�λ�ù�Ч######################
		intensifyLevel = bodyFDict["iLevel"]
		# ���µ����巢���âЧ��(�ز�װ��ǿ����4��ʱ����)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# ���µĸ�ְҵ����������(�ز�װ��ǿ����6��ʱ����)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# ���µ�������Χ�����������( �ز�װ��ǿ����9��ʱ���� )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# ���µ�������ת�⻷( �ز�װ��ǿ����9��ʱ���� )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
		###########Ь�ӹ�Ч#################################
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		
		# ��ʦ��������Ч��
		if roleInfo.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER  )
	
	def turnRole( self, direction ) :
		"""
		��ת��ǰ��ɫ����� direction Ϊ����������ת��Ϊ����������ת��Ϊ 0 ��ֹͣ��ת
		"""
		BigWorld.cancelCallback( self.__turnRoleCBID )
		if direction == 0 : return
		def turn() :
			delta = direction < 0 and 0.2 or - 0.2
			self.__selectRole.turnaround( delta )
			self.__turnRoleCBID = BigWorld.callback( 0.01, turn )
		turn()

	# ---------------------------------------
	def viewClose( self ) :
		"""
		��ͷ������ɫ
		"""
		self.__camHandler.closeTarget()

	def viewFar( self ) :
		"""
		��ͷԶ���ɫ
		"""
		self.__camHandler.extendTarget()

	# -------------------------------------------------
	def getRaceClass( self ) :
		"""
		��ȡ��ǰѡ�н�ɫ��ְҵ
		"""
		profession = self.__currProfession
		gender = self.__currGender
		race = csconst.RACE_CLASS_MAP[profession]
		camp = self.__currCamp<<20
		return race | profession | gender|camp

	def getDescription( self, profession ) :
		"""
		��ȡְҵ����
		"""
		camp = self.__currCamp
		try:
			desc = g_teacherData[csconst.g_chs_class[profession]][0] + g_teacherData[csconst.g_chs_class[profession]][camp]
			return g_ProfessionDspData[csconst.g_chs_class[profession]] + desc
		except:
			ERROR_MSG( "can't find profession description config file!" )
			return ""
	
	def getCampDesp( self, camp ):
		"""
		��ȡ��Ӫ����
		"""
		try:
			return g_CampDspData[camp]
		except:
			ERROR_MSG( "can't find camp description config file!" )
			return ""
	
	def getCampVoice( self, camp ):
		"""
		��ȡ��Ӫ����·��
		"""
		return ""

	def createRole( self, name ) :
		"""
		call to create a role
		@type			name : str
		@param			name : the name the the role you want to create
		"""
		if len( name ) > 14 :
			# "���ֳ��Ȳ��ܳ��� 14 ���ֽ�"
			self.showAutoHideMsg( 0x0050 )
		elif name == "" :
			# "��������û�����Ч������������"
			self.showAutoHideMsg( 0x0051 )
		elif not rds.wordsProfanity.isPureString( name ) :
			# "���Ʋ��Ϸ���"
			self.showAutoHideMsg( 0x0052 )
		elif rds.wordsProfanity.searchNameProfanity( name ) is not None :
			# "����������н��ôʻ㣡"
			self.showAutoHideMsg( 0x0053 )
		elif roleSelector.getRoleCount() >= csconst.LOGIN_ROLE_UPPER_LIMIT :
			# "���ڽ�ɫ�����Ѿ��ﵽ���ޣ�"
			self.showAutoHideMsg( 0x0054 )
		else :
			raceclass = self.getRaceClass()
			BigWorld.player().createRole( raceclass, name, self.__currHairNum, self.__currFaceNum, self.__currHeadTextureID )	
	
	def onCreateCB( self ):
		"""
		������ɫ��base��֪ͨ�ͻ��˴���OK
		"""
		self.dispose()
		#���ش�����ɫ����
		ECenter.fireEvent( "EVT_ON_ROLECREATOR_OK" )

	def showAutoHideMsg( self, msg ): 									# �����ۺϴ����ɫ����������ʾ�������ʾ����ظ����ֵ�����
		ECenter.fireEvent( "EVT_ON_LOST_CONTROL" )
		def query( rs_id ):
			if rs_id == MB_OK:
				ECenter.fireEvent( "EVT_ON_GOT_CONTROL" )
		showAutoHideMessage( 3.0, msg, mbmsgs[0x0c22], MB_OK, query )

	def cancel( self ) :
		"""
		call to back to role selector
		"""
		rds.statusMgr.changeStatus( Define.GST_ROLE_SELECT )
		loginSpaceID = loginSpaceMgr.loadLoginSpace( Define.LOGIN_TYPE_MAP )
		BigWorld.cameraSpaceID( loginSpaceID )
		BigWorld.spaceHold( True )
		self.__selectRole = None

	def cancelSelectCamp( self ):
		self.onBackToSelector = True
		loginSpaceID = loginSpaceMgr.loadLoginSpace( Define.LOGIN_TYPE_MAP )
		BigWorld.cameraSpaceID( loginSpaceID )
		BigWorld.spaceHold( True )
		self.__selectRole = None
		rds.roleSelector.onEnter()
		ECenter.fireEvent( "EVT_ON_SHOW_ROLE_SELECTOR" )
		rds.statusMgr.changeStatus( Define.GST_ROLE_SELECT )
		self.onBackToSelector = False
	
	#def cleanAvatars( self ) :
	#	"""
	#	�����н�ɫģ�����
	#	"""
	#	if self.__avatar :
	#		self.__avatar.setModel( None )


# --------------------------------------------------------------------
# implement login psace manager calss
# --------------------------------------------------------------------
class LoginMgr :
	__inst = None

	def __init__( self ) :
		assert LoginMgr.__inst is None
		self.__loginSpaceID = 0

		self.loginer = Loginer( self )					# ��¼��
		self.roleSelector = RoleSelector( self )		# ��ɫѡ����
		self.roleCreator = RoleCreator( self )			# ��ɫ������

		self.__initCallback = None						# ��ʱ���������泡����ʼ���ص�
		self.__detectCBID = 0							# �����������ص�

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = LoginMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onOffline( self ) :
		"""
		������ʱ����
		"""
		BigWorld.cancelCallback( self.__detectCBID )					# ����ڳ������ع����жϿ��˷�����
		self.__detectCBID = 0											# ��ֹͣ�������


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enter( self ) :
		"""
		��������¼�����ļ���
		"""
		#self.roleCreator.initModelBG()									# ���̼߳��ؽ�ɫ��������ģ��
		loginSpace = loginSpaceMgr.loadLoginSpace( Define.LOGIN_TYPE_MAP )
		DEBUG_MSG( "loginMgr enter space", loginSpace )
		BigWorld.cameraSpaceID( loginSpace )							# ������������򳡾�
		BigWorld.spaceHold( True )
		try:
			m = Math.Matrix()
			m.setTranslate( ( 238, 8, 110 ) )							# ���㵽 space ������� chunk ��������
			BigWorld.camera().target = m								# ʹ�ó�������ʱ������ּ���λ�ò���
		except:															# ��Ϊ�������ط�Χ�Ǹ������λ����ȷ����
			pass

	def leave( self ) :
		"""
		�����뿪��ɫѡ��ͽ�ɫ��������
		"""
		self.__initCallback = None										# ����ص�
		newStatus = rds.statusMgr.currStatus()
		if newStatus == Define.GST_LOGIN :
			self.roleSelector.cleanAvatars()
			#self.roleCreator.cleanAvatars()
		else :
			loginSpaceMgr.releaseAllLoginSpace()											# �ͷŵ�½��ͼ
			self.roleSelector.onLeave( Define.GST_ENTER_WORLD_LOADING )
			self.roleSelector.dispose()									# ɾ����ɫѡ����
			self.roleCreator.onLeave()
			self.roleCreator.dispose()									# ɾ����ɫ������


# --------------------------------------------------------------------
# global methods of login space management
# --------------------------------------------------------------------

class LoginSpaceMgr :
	__inst = None

	def __init__( self ) :
		assert LoginSpaceMgr.__inst is None
		self.__spaceID = {}
		for key in LOGIN_SPACE_TYPE_MAP.keys():
			self.__spaceID[ key ] = 0
	
	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = LoginSpaceMgr()
		return SELF.__inst

	def loadLoginSpace( self, type ):
		"""
		������ͼ
		type��int ��ͼ������
		"""
		mapN = LOGIN_SPACE_TYPE_MAP[ type ]
		loginSpaceID = self.__spaceID[ type ]
		if loginSpaceID == 0 :
			loginSpaceID = BigWorld.createSpace()			# ��������
			BigWorld.addSpaceGeometryMapping( loginSpaceID, None, mapN )	# ���س�������
			BigWorld.worldDrawEnabled( True ) # ������������
			self.__spaceID[ type ] = loginSpaceID
		return loginSpaceID

	def releaseLoginSpace( self, type ):
		"""
		�ͷŵ�ͼ
		type��int ��ͼ������
		"""
		loginSpaceID = self.__spaceID[ type ]
		BigWorld.spaceHold( False )
		BigWorld.cameraSpaceID( 0 )										# ��������� space
		BigWorld.clearSpace( loginSpaceID )							# ��� space ��Ϣ
		self.__spaceID[ type ] = 0
	
	def releaseAllLoginSpace( self ):	
		"""
		�ͷ����е�½��ͼ
		"""
		for loginSpaceID in self.__spaceID.values():
			if loginSpaceID != 0:
				BigWorld.clearSpace( loginSpaceID )							# ��� space ��Ϣ
		for key in LOGIN_SPACE_TYPE_MAP.keys():
			self.__spaceID[ key ] = 0
		BigWorld.spaceHold( False )
		BigWorld.cameraSpaceID( 0 )
	
	def getSpaceByType( self, type = Define.LOGIN_TYPE_MAP ):
		"""
		"""
		return self.__spaceID[ type ]
	
loginSpaceMgr = LoginSpaceMgr.instance()





# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
loginMgr = LoginMgr.instance()
loginer = loginMgr.loginer
roleSelector = loginMgr.roleSelector
roleCreator = loginMgr.roleCreator
