# -*- coding: gb18030 -*-

# $Id: Account.py,v 1.58 2008-08-20 01:45:33 yangkai Exp $

"""
-- 2005/10/28 : written by phw
-- 2006/08/28 : rewritten by huangyw
"""

import zlib
import base64
import BigWorld
import Math
import csol
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
import Define
import Const
import GUIFacade
import event.EventCenter as ECenter

from Function import Functor
from bwdebug import *
from keys import *
from gbref import rds
from LoginMgr import roleSelector
from RoleMaker import RoleModelMaker
from RoleMaker import RoleInfo
from Time import Time
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs

# --------------------------------------------------------------------
# account before login, just for connection
# --------------------------------------------------------------------
class Account( BigWorld.Entity ) :
	def __init__( self ) :
		BigWorld.Entity.__init__( self )
		self.waitTime = 0
		self.waitOrder = 0

	# ----------------------------------------------------------------
	# called by base
	# ----------------------------------------------------------------
	def onStatusMessage( self, statusID, sargs ) :
		"""
		<defined/>
		���շ�������������״̬��Ϣ
		@type				statusID : MACRO DEFINATION
		@param				statusID : ״̬��Ϣ���� common/csstatus.py �ж���
		@type				sargs	 : STRING
		@param				sargs	 : ��Ϣ���Ӳ���
		@return						 : None
		"""
		args = sargs == "" and () or eval( sargs )
		ECenter.fireEvent( "EVT_ON_RECEIVE_STATUS_MESSAGE", statusID, *args )

		if statusID == csstatus.ACCOUNT_STATE_FORCE_LOGOUT:
			rds.gameMgr.changeKickoutStatus( True )
			return

		if statusID == csstatus.ACCOUNT_STATE_CREATE_FAIL:
			BigWorld.callback( 3, BigWorld.disconnect )
		if args:
			msgInfo = StatusMsgs.getStatusInfo( statusID, args )
		else:
			msgInfo = StatusMsgs.getStatusInfo( statusID )

		if statusID in ( csstatus.ACCOUNT_LOGIN_TIME_OUT_KICK, csstatus.ACCOUNT_LOGIN_BUSY ) :	# �����¼ʱ��̫����û������Ϸ�����߿�
			def func():
				# "��ʾ"
				showAutoHideMessage( 600.0, msgInfo.msg, mbmsgs[0x0c22], MB_OK )
			BigWorld.callback( 1.0, func )						# ���򵯳�������ʾ
			ECenter.fireEvent( "EVT_ON_KICKOUT_OVERTIME" )
			return

		def query( rs_id ):
			ECenter.fireEvent( "EVT_ON_GOT_CONTROL" ) 				# ����ɫ��������İ�ť��enableֵ��Ϊ True
		ECenter.fireEvent( "EVT_ON_LOST_CONTROL" ) 					# ����ɫ��������İ�ť�� enable ֵ��Ϊ False
		showAutoHideMessage( 3.0, msgInfo.msg, mbmsgs[0x0c22], MB_OK, query )

	def onAccountlockedNotify( self, lockTime ) :
		"""
		�˺���סʱ������
		"""
		rds.loginer.onAccountlockedNotify( lockTime )
		rds.gameMgr.accountLogoff()

	def receiveWattingTime( self, order, waitTime ):
		"""
		Define method.
		���յȴ���¼��ʱ��
		"""
		DEBUG_MSG( "--->>>waitOrder( %i ), waitTime:( %f )." % ( order, waitTime ) )
		self.waitTime = waitTime
		self.waitOrder = order

		ECenter.fireEvent( "EVT_ON_LOGIN_WAIT", order + 1, waitTime )

	# -------------------------------------------------
	def onAccountLogin( self ) :
		"""
		Define method.
		��¼��Ϸ�ɹ������ؽ�ɫѡ�񳡾�
		"""
		rds.gameMgr.onAccountLogined()

	def initRolesCB( self, loginRoles ) :
		"""
		<defined/>
		���յ��˺������еĽ�ɫ
		@type					loginRoles : list
		@param					locinRoles : ��ɫ�б���ɫ��ϸ��Ϣ����ۿ���RoleMaker.RoleInfo �ĳ�ʼ��
		"""
		roleSelector.onInitRoles( loginRoles )
		ECenter.fireEvent( "EVT_ON_LOGIN_SUCCESS" )

	def addRoleCB( self, loginRole ) :
		"""
		<defined/>
		����һ����ɫ�ķ���������
		@type					loginRole : dict
		@param					loginRole : ��ɫ��ϸ��Ϣ����ۿ���RoleMaker.RoleInfo �ĳ�ʼ��
		"""
		roleSelector.onAddRole( loginRole )
		#def query( rs_id ):
		#	ECenter.fireEvent( "EVT_ON_GOT_CONTROL" )	 			# ����ɫ��������İ�ť��enableֵ��ΪTrue
		#	rds.statusMgr.changeStatus( Define.GST_ROLE_SELECT )
		#ECenter.fireEvent( "EVT_ON_LOST_CONTROL" ) 					# ����ɫ��������İ�ť��enableֵ��ΪFalse
		# "������ɫ�ɹ�"
		#showAutoHideMessage( 2.0, 0x0c21, mbmsgs[0x0c22], MB_OK, query )
		#����߻�Ҫ��ֱ�ӽ�����Ϸ
		rds.roleCreator.onCreateCB()
		roleInfo = RoleInfo( loginRole )
		rds.gameMgr.setAccountOption( "selRoleID", roleInfo.getID() )		# ������Ϸ���������һ��ѡ��Ľ�ɫ index��wsf
		rds.gameMgr.requestEnterGame( roleInfo )


	def deleteRoleCB( self, roleID ) :
		"""
		ɾ��һ����ɫ
		@type					roleID : INT64
		@param					roleID : ��ɾ���Ľ�ɫ���ݿ� ID
		"""
		roleSelector.onDeleteRole( roleID )


	# ----------------------------------------------------------------
	# called by client
	# ----------------------------------------------------------------
	def isPlayer( self ) :
		"""
		ָ���Ƿ������
		@type					: bool
		@return					: ���Ƿ��� False����ʾ���� PlayerRole
		"""
		return False

	def timeSynchronization( self, serverTime ):
		"""
		ͬ��������ʱ��
		@type				serverTime : float
		@param				serverTime : ������ʱ��
		"""
		Time.init( serverTime )


	# ----------------------------------------------------------------
	# �����ܱ����
	# ----------------------------------------------------------------
	def input_passwdPro_matrix( self, sites, state ):
		"""
		��ʾ������������������
		@type  sites : UINT32
		@param sites : ������Ҫ���ݵ����� like "112233" ��ʾҪ����1��1��2��2��3��3�е���ֵ
		@type  state : UINT8
		@param state : ���������صľ��󿨵�����״̬
		ע: inputState ��״̬��ֵ�ֱ�Ϊ:
			0   : ��һ������� ����֮ǰ�����0��
			1   : �ڶ�������� ����֮ǰ�����1��
			2   : ����������� ����֮ǰ�����2��
			......
			255 : �����ȷ
		"""
		INFO_MSG( "receive secrecy card information: sites = %i; state = %i" % ( sites, state ) )
		if state == 0 :											# ��һ�λ�������
			pswSegs = []
			step = 100											# ���󿨣�ÿ����ϰ�����λ��
			while sites :
				rw = sites % step
				row = rw / 10									# �к�
				col = rw % 10									# �к�
				pswSegs.insert( 0, ( row, col ) )
				sites = sites / step
			ECenter.fireEvent( "EVT_ON_SHOW_ACCOUNT_GUARDER", pswSegs, state )
		elif state == 255 :										# �����������ȷ
			ECenter.fireEvent( "EVT_ON_PASSED_ACCOUNT_GUARDER" )
		elif state >= Const.ACC_GUARD_WRONG_TIMES :				# �������
			self.base.recheck_passwdProMatrixValue()			# �����»�ȡ�������
			ECenter.fireEvent( "EVT_ON_LOST_ACCOUNT_GUARDER", state )
		else :
			ECenter.fireEvent( "EVT_ON_LOST_ACCOUNT_GUARDER", state )

	def check_passwdProMatrixValue( self, value ):
		"""
		���������������ֵ�Ƿ���ȷ
		@type  value : UINT32
		@param value : ��Ҹ������ܱ��Ĵ�
		"""
		self.base.check_passwdProMatrixValue( value )

	def recheck_passwdProMatrixValue( self ):
		"""
		������������¸����µ������ֵ
		"""
		self.base.recheck_passwdProMatrixValue()

	def trigerImageVerify( self, imageData, count ):
		"""
		Define method.
		����ͼƬ��֤

		@param imageData : ��֤ͼƬ���ݣ�STRING
		@param count : �ڼ�����֤
		"""
		pass

	def verifySuccess( self ):
		"""
		Define method.
		��֤�ɹ���֪ͨ
		"""
		pass

	def changeRoleNameSuccess( self, roleDBID, newName ):
		"""
		Define method.
		��ɫ�����ɹ�
		"""
		pass


# --------------------------------------------------------------------
# account after login, just for role selection
# --------------------------------------------------------------------
class PlayerAccount( Account ) :
	def onBecomePlayer( self ) :
		"""
		���˺Ŵ����ɹ�ʱ������
		"""
		target = BigWorld.target
		target.caps( *csconst.ENTITY_TYPE_ALL )
		target.exclude = self
		target.source = csol.CursorTargetMatrix()
		target.skeletonCheckEnabled = True
		INFO_MSG( "PlayerAccount::onBecomeAccountPlayer!" )

		self.__target = None									# ��ʱ��������¼��ǰ�����е�ĳ�� entity
		self.isRequesting = False

		if rds.statusMgr.isCurrStatus( Define.GST_IN_WORLD ) :	# �����ǰ��������״̬
			rds.gameMgr.onLogout()								# ��ת��Ϊ Account ʱ����ζ�ŷ��ؽ�ɫѡ��

	def onBecomeNonPlayer( self ) :
		"""
		���ı�Ϊ���״̬ʱ���������
		"""
		INFO_MSG( "PlayerAccount::onBecomeNonAccountPlayer" )
		#��������ϷPlayerAccount��û��ΪPlayerRole��ʱ���������������ص���½������������׷��\���������
		if hasattr(rds.ruisMgr,"systemBar"):
			rds.ruisMgr.systemBar.onLeaveWorld() #add by wuxo 2011-12-13
		if hasattr(rds.ruisMgr,"questHelp"):
			rds.ruisMgr.questHelp.onLeaveWorld()
	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def enterWorld( self ) :
		"""
		����������ʱ�����ã���������������ָ��¼ʱ�� space��
		"""
		self.physics = STANDARD_PHYSICS										# defined in keys.py
		self.physics.velocity = ( 0.0, 0.0, 0.0 )
		self.physics.velocityMouse = "Direction"
		self.physics.angular = 0
		self.physics.angularMouse = "MouseX"
		self.physics.collide = False
		self.physics.gravity = 0
		self.physics.fall = False

	def leaveWorld( self ) :
		"""
		���뿪 space ʱ������
		"""
		pass

	# ----------------------------------------------------------------
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if down and key == KEY_LEFTMOUSE and mods == 0 :
			if hasattr( self.__target, "onTargetClick" ) :
				self.__target.onTargetClick( self )
				return True
		return False

	def targetFocus( self, entity ) :
		"""
		��������ĳ�� entitiy ʱ������
		"""
		self.__target = entity
		if hasattr( entity, "onTargetFocus" ) :
			entity.onTargetFocus()

	def targetBlur( self, entity ) :
		"""
		������뿪ĳ�� entity ʱ������
		"""
		self.__target = None
		if hasattr( entity, "onTargetBlur" ) :
			entity.onTargetBlur()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enterGame( self, roleID, loginTo ) :
		"""
		�����������
		@type				roleID	: INT64
		@param				roleID	: Ҫ��¼�Ľ�ɫ���ݿ� ID
		@type				loginTo : str
		@param				loginTo : Ҫ��¼���ĳ������ƣ�����ǿգ������Ĭ�ϣ���ǰһ�����ڵĳ�������̶������㣩
		"""
		GUIFacade.modelReset()
		self.base.login( roleID, loginTo )

	# -------------------------------------------------
	def createRole( self, raceclass, name, hairNum, faceNum, headTextureID ) :
		"""
		���󴴽�һ����ɫ
		@type				raceclass : MACRO DEFINATION
		@param				raceclass : ְҵ�Ա�����
		@type				name	  : str
		@param				name	  : Ҫ�����Ľ�ɫ������
		@type				hairNum	  : INT32
		@param				hairNum	  : Ҫ�����Ľ�ɫ�ķ��ͱ��
		@type				faceNum	  : INT32
		@param				faceNum	  : Ҫ�����Ľ�ɫ�����ͱ��
		@type				headTextureID	: INT32
		@param				headTextureID	: Ҫ�����Ľ�ɫ��ͷ����
		"""
		self.base.createRole( raceclass, name, hairNum, faceNum, headTextureID )

	def deleteRole( self, roleID, roleName ) :
		"""
		����ɾ��һ����ɫ
		@type				roleID : INT64
		@param				roleID : Ҫɾ���Ľ�ɫ�� ID
		"""
		self.base.deleteRole( roleID, roleName )
	
	def requestEnterGame( self ):
		"""
		���������Ϸ
		"""
		self.isRequesting = True
		self.base.requestEnterGame()
		DEBUG_MSG( "entity( id: %s ) request enter game." % self.id )

	def trigerImageVerify( self, imageData, count ):
		"""
		Define method.
		����ͼƬ��֤

		@param imageData : ��֤ͼƬ���ݣ�STRING
		@param count : �ڼ�����֤
		"""
		DEBUG_MSG( "entity( id: %s ) receive verify image." % self.id )
		if not self.isRequesting:
			DEBUG_MSG( "entity( id: %s ) is not requesting." % self.id )
			return
		ECenter.fireEvent("EVT_ON_ANTI_RABOT_VERIFY", base64.b64decode( zlib.decompress( imageData ) ), count )

	def verifySuccess( self ):
		"""
		Define method.
		��֤�ɹ���֪ͨ
		"""
		DEBUG_MSG( "entity( id: %s ) verify success!" % self.id )
		self.isRequesting = False
		rds.roleSelector.onVerifySuccess()

	def changeRoleNameSuccess( self, roleDBID, newName ):
		"""
		Define method.
		��ɫ�����ɹ�
		"""
		rds.roleSelector.onNameChanged( roleDBID, newName )

