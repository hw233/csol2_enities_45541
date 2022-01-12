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
		接收服务器返回来的状态消息
		@type				statusID : MACRO DEFINATION
		@param				statusID : 状态消息，在 common/csstatus.py 中定义
		@type				sargs	 : STRING
		@param				sargs	 : 消息附加参数
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

		if statusID in ( csstatus.ACCOUNT_LOGIN_TIME_OUT_KICK, csstatus.ACCOUNT_LOGIN_BUSY ) :	# 如果登录时间太长还没进入游戏，则踢开
			def func():
				# "提示"
				showAutoHideMessage( 600.0, msgInfo.msg, mbmsgs[0x0c22], MB_OK )
			BigWorld.callback( 1.0, func )						# 否则弹出被踢提示
			ECenter.fireEvent( "EVT_ON_KICKOUT_OVERTIME" )
			return

		def query( rs_id ):
			ECenter.fireEvent( "EVT_ON_GOT_CONTROL" ) 				# 将角色创建界面的按钮的enable值设为 True
		ECenter.fireEvent( "EVT_ON_LOST_CONTROL" ) 					# 将角色创建界面的按钮的 enable 值设为 False
		showAutoHideMessage( 3.0, msgInfo.msg, mbmsgs[0x0c22], MB_OK, query )

	def onAccountlockedNotify( self, lockTime ) :
		"""
		账号锁住时被触发
		"""
		rds.loginer.onAccountlockedNotify( lockTime )
		rds.gameMgr.accountLogoff()

	def receiveWattingTime( self, order, waitTime ):
		"""
		Define method.
		接收等待登录的时间
		"""
		DEBUG_MSG( "--->>>waitOrder( %i ), waitTime:( %f )." % ( order, waitTime ) )
		self.waitTime = waitTime
		self.waitOrder = order

		ECenter.fireEvent( "EVT_ON_LOGIN_WAIT", order + 1, waitTime )

	# -------------------------------------------------
	def onAccountLogin( self ) :
		"""
		Define method.
		登录游戏成功，加载角色选择场景
		"""
		rds.gameMgr.onAccountLogined()

	def initRolesCB( self, loginRoles ) :
		"""
		<defined/>
		接收到账号了所有的角色
		@type					loginRoles : list
		@param					locinRoles : 角色列表，角色详细信息，请观看：RoleMaker.RoleInfo 的初始化
		"""
		roleSelector.onInitRoles( loginRoles )
		ECenter.fireEvent( "EVT_ON_LOGIN_SUCCESS" )

	def addRoleCB( self, loginRole ) :
		"""
		<defined/>
		创建一个角色的服务器返回
		@type					loginRole : dict
		@param					loginRole : 角色详细信息，请观看：RoleMaker.RoleInfo 的初始化
		"""
		roleSelector.onAddRole( loginRole )
		#def query( rs_id ):
		#	ECenter.fireEvent( "EVT_ON_GOT_CONTROL" )	 			# 将角色创建界面的按钮的enable值设为True
		#	rds.statusMgr.changeStatus( Define.GST_ROLE_SELECT )
		#ECenter.fireEvent( "EVT_ON_LOST_CONTROL" ) 					# 将角色创建界面的按钮的enable值设为False
		# "创建角色成功"
		#showAutoHideMessage( 2.0, 0x0c21, mbmsgs[0x0c22], MB_OK, query )
		#这里策划要求直接进入游戏
		rds.roleCreator.onCreateCB()
		roleInfo = RoleInfo( loginRole )
		rds.gameMgr.setAccountOption( "selRoleID", roleInfo.getID() )		# 进入游戏，保存最后一次选择的角色 index，wsf
		rds.gameMgr.requestEnterGame( roleInfo )


	def deleteRoleCB( self, roleID ) :
		"""
		删除一个角色
		@type					roleID : INT64
		@param					roleID : 被删除的角色数据库 ID
		"""
		roleSelector.onDeleteRole( roleID )


	# ----------------------------------------------------------------
	# called by client
	# ----------------------------------------------------------------
	def isPlayer( self ) :
		"""
		指出是否是玩家
		@type					: bool
		@return					: 总是返回 False，表示不是 PlayerRole
		"""
		return False

	def timeSynchronization( self, serverTime ):
		"""
		同步服务器时间
		@type				serverTime : float
		@param				serverTime : 服务器时间
		"""
		Time.init( serverTime )


	# ----------------------------------------------------------------
	# 矩阵卡密保相关
	# ----------------------------------------------------------------
	def input_passwdPro_matrix( self, sites, state ):
		"""
		显示输入输入矩阵卡输入界面
		@type  sites : UINT32
		@param sites : 矩阵卡需要数据的坐标 like "112233" 表示要输入1行1列2行2列3行3列的数值
		@type  state : UINT8
		@param state : 服务器返回的矩阵卡的输入状态
		注: inputState 的状态和值分别为:
			0   : 第一次输入答案 代表之前输入过0次
			1   : 第二次输入答案 代表之前输入过1次
			2   : 第三次输入答案 代表之前输入过2次
			......
			255 : 结果正确
		"""
		INFO_MSG( "receive secrecy card information: sites = %i; state = %i" % ( sites, state ) )
		if state == 0 :											# 第一次获得密码段
			pswSegs = []
			step = 100											# 矩阵卡，每个组合包含两位数
			while sites :
				rw = sites % step
				row = rw / 10									# 行号
				col = rw % 10									# 列号
				pswSegs.insert( 0, ( row, col ) )
				sites = sites / step
			ECenter.fireEvent( "EVT_ON_SHOW_ACCOUNT_GUARDER", pswSegs, state )
		elif state == 255 :										# 输入的密码正确
			ECenter.fireEvent( "EVT_ON_PASSED_ACCOUNT_GUARDER" )
		elif state >= Const.ACC_GUARD_WRONG_TIMES :				# 输错三次
			self.base.recheck_passwdProMatrixValue()			# 则重新获取密码组段
			ECenter.fireEvent( "EVT_ON_LOST_ACCOUNT_GUARDER", state )
		else :
			ECenter.fireEvent( "EVT_ON_LOST_ACCOUNT_GUARDER", state )

	def check_passwdProMatrixValue( self, value ):
		"""
		请求服务器检测矩阵卡值是否正确
		@type  value : UINT32
		@param value : 玩家给出的密报的答案
		"""
		self.base.check_passwdProMatrixValue( value )

	def recheck_passwdProMatrixValue( self ):
		"""
		请求服务器重新给出新的坐标和值
		"""
		self.base.recheck_passwdProMatrixValue()

	def trigerImageVerify( self, imageData, count ):
		"""
		Define method.
		触发图片验证

		@param imageData : 验证图片数据，STRING
		@param count : 第几次验证
		"""
		pass

	def verifySuccess( self ):
		"""
		Define method.
		验证成功的通知
		"""
		pass

	def changeRoleNameSuccess( self, roleDBID, newName ):
		"""
		Define method.
		角色改名成功
		"""
		pass


# --------------------------------------------------------------------
# account after login, just for role selection
# --------------------------------------------------------------------
class PlayerAccount( Account ) :
	def onBecomePlayer( self ) :
		"""
		当账号创建成功时被调用
		"""
		target = BigWorld.target
		target.caps( *csconst.ENTITY_TYPE_ALL )
		target.exclude = self
		target.source = csol.CursorTargetMatrix()
		target.skeletonCheckEnabled = True
		INFO_MSG( "PlayerAccount::onBecomeAccountPlayer!" )

		self.__target = None									# 临时变量，记录当前鼠标点中的某个 entity
		self.isRequesting = False

		if rds.statusMgr.isCurrStatus( Define.GST_IN_WORLD ) :	# 如果当前是在世界状态
			rds.gameMgr.onLogout()								# 则，转变为 Account 时，意味着返回角色选择

	def onBecomeNonPlayer( self ) :
		"""
		当改变为别的状态时被引擎调用
		"""
		INFO_MSG( "PlayerAccount::onBecomeNonAccountPlayer" )
		#当进入游戏PlayerAccount还没变为PlayerRole的时候重启服务器，回到登陆界面会出现任务追踪\快捷栏界面
		if hasattr(rds.ruisMgr,"systemBar"):
			rds.ruisMgr.systemBar.onLeaveWorld() #add by wuxo 2011-12-13
		if hasattr(rds.ruisMgr,"questHelp"):
			rds.ruisMgr.questHelp.onLeaveWorld()
	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def enterWorld( self ) :
		"""
		当进入世界时被调用（这里的世界仅仅是指登录时的 space）
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
		当离开 space 时被调用
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
		当鼠标进入某个 entitiy 时被调用
		"""
		self.__target = entity
		if hasattr( entity, "onTargetFocus" ) :
			entity.onTargetFocus()

	def targetBlur( self, entity ) :
		"""
		当鼠标离开某个 entity 时被调用
		"""
		self.__target = None
		if hasattr( entity, "onTargetBlur" ) :
			entity.onTargetBlur()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enterGame( self, roleID, loginTo ) :
		"""
		请求进入世界
		@type				roleID	: INT64
		@param				roleID	: 要登录的角色数据库 ID
		@type				loginTo : str
		@param				loginTo : 要登录到的场景名称，如果是空，则采用默认（即前一次所在的场景，或固定出生点）
		"""
		GUIFacade.modelReset()
		self.base.login( roleID, loginTo )

	# -------------------------------------------------
	def createRole( self, raceclass, name, hairNum, faceNum, headTextureID ) :
		"""
		请求创建一个角色
		@type				raceclass : MACRO DEFINATION
		@param				raceclass : 职业性别的组合
		@type				name	  : str
		@param				name	  : 要创建的角色的名称
		@type				hairNum	  : INT32
		@param				hairNum	  : 要创建的角色的发型编号
		@type				faceNum	  : INT32
		@param				faceNum	  : 要创建的角色的脸型编号
		@type				headTextureID	: INT32
		@param				headTextureID	: 要创建的角色的头像编号
		"""
		self.base.createRole( raceclass, name, hairNum, faceNum, headTextureID )

	def deleteRole( self, roleID, roleName ) :
		"""
		请求删除一个角色
		@type				roleID : INT64
		@param				roleID : 要删除的角色的 ID
		"""
		self.base.deleteRole( roleID, roleName )
	
	def requestEnterGame( self ):
		"""
		请求进入游戏
		"""
		self.isRequesting = True
		self.base.requestEnterGame()
		DEBUG_MSG( "entity( id: %s ) request enter game." % self.id )

	def trigerImageVerify( self, imageData, count ):
		"""
		Define method.
		触发图片验证

		@param imageData : 验证图片数据，STRING
		@param count : 第几次验证
		"""
		DEBUG_MSG( "entity( id: %s ) receive verify image." % self.id )
		if not self.isRequesting:
			DEBUG_MSG( "entity( id: %s ) is not requesting." % self.id )
			return
		ECenter.fireEvent("EVT_ON_ANTI_RABOT_VERIFY", base64.b64decode( zlib.decompress( imageData ) ), count )

	def verifySuccess( self ):
		"""
		Define method.
		验证成功的通知
		"""
		DEBUG_MSG( "entity( id: %s ) verify success!" % self.id )
		self.isRequesting = False
		rds.roleSelector.onVerifySuccess()

	def changeRoleNameSuccess( self, roleDBID, newName ):
		"""
		Define method.
		角色改名成功
		"""
		rds.roleSelector.onNameChanged( roleDBID, newName )

