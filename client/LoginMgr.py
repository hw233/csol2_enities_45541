# -*- coding: gb18030 -*-

# $Id: LoginMgr.py,v 1.46 2008-08-28 01:42:51 huangyongwei Exp $

"""
implement login module
-- 2007/10/10 : written by huangyongwei
-- 2009.03.14 : modified by hyw
				角色创建中，选择角色改为固定镜头方式
				创建职业角色改为用 callback 分步创建的方式
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
		}  #创建角色地图摄像机位置和朝向(1 天道阵营,2魔道阵营)
TAOISM_YAW_PREVIEWROLE_MAP = {
	csdefine.CLASS_FIGHTER		: ( -15* math.pi / 180, -15* math.pi / 180 ),		# 战士
	csdefine.CLASS_SWORDMAN		: ( 45* math.pi / 180, 45* math.pi / 180 ),			# 剑客
	csdefine.CLASS_ARCHER		: ( -30* math.pi / 180, -45* math.pi / 180),			# 射手
	csdefine.CLASS_MAGE		: ( 30* math.pi / 180, 30* math.pi / 180),			# 法师
	} #仙道八个角色角度值
DEMON_YAW_PREVIEWROLE_MAP = {
	csdefine.CLASS_FIGHTER		: ( 165* math.pi / 180, 165* math.pi / 180 ),		# 战士
	csdefine.CLASS_SWORDMAN		: ( -135* math.pi / 180, -135* math.pi / 180 ),			# 剑客
	csdefine.CLASS_ARCHER		: ( 150* math.pi / 180, 150* math.pi / 180),			# 射手
	csdefine.CLASS_MAGE		: ( 180* math.pi / 180, -165* math.pi / 180),			# 法师
	}#魔道八个角色角度值
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
	( 1, 1 )	: mbmsgs[0x0032],		# "登录成功。"	"The client has successfully logged in to the server."
	( 1, -2 )	: mbmsgs[0x0033],		# "无法连接到服务器。"	"The client failed to make a connection to the network."
	( 1, -3 )	: mbmsgs[0x0034],		# "无法连接到服务器。"	"The client failed to locate the server IP address via DNS."
	( 1, -4 )	: mbmsgs[0x0035],		# "CLIENT ERROR: An unknown client-side error has occurred."
	( 1, -5 )	: mbmsgs[0x0036],		# "客户端主动取消登录。"	"CLIENT ERROR: The login was cancelled by the client."
	( 1, -6 )	: mbmsgs[0x0037],		# "CLIENT ERROR: The client is already online locally (i.e. exploring a space offline). "
	( 1, -64 )	: mbmsgs[0x0038],		# "非法登录数据。"	"SERVER ERROR: The login packet sent to the server was malformed."
	( 1, -65 )	: mbmsgs[0x0039],		# "版本不匹配，请升级到最新版本。"	"SERVER ERROR: The login protocol the client used does not match the one on the server."
	( 1, -66 )	: mbmsgs[0x003a],		# "帐号或密码不正确。"	"SERVER ERROR: The server database did not contain an entry for the specified username and was running in a mode that did not allow for unknown users to connect, or could not create a new entry for the user. The database would most likely be unable to create a new entry for a user if an inappropriate entity type being listed in bw.xml as database/entityType.
	( 1, -67 )	: mbmsgs[0x003b],		# "帐号或密码不正确。"	"SERVER ERROR: A global password was specified in bw.xml, and it did not match the password with which the login attempt was made."
	( 1, -68 )	: mbmsgs[0x003c],		# "此帐号已登录。"	"SERVER ERROR: A client with this username is already logged into the server."
	( 1, -69 )	: mbmsgs[0x003d],		# "版本不匹配，请升级到最新版本。"	"SERVER ERROR: The defs and/or entities.xml are not identical on the client and the server."
	( 1, -70 )	: mbmsgs[0x003e],		# "服务器未启动"	"SERVER ERROR: A general database error has occurred, for example the database may have been corrupted."
	( 1, -71 )	: mbmsgs[0x003f],		# "服务器未启动"	"SERVER ERROR: The database is not ready yet."
	( 1, -72 )	: mbmsgs[0x0040],		# "帐号或密码不正确。"	 "SERVER ERROR: There are illegal characters in either the username or password."
	( 1, -73 )	: mbmsgs[0x0041],		# "服务器未启动（1, -73）。""SERVER ERROR: The baseappmgr is not ready yet."
	( 1, -74 )	: mbmsgs[0x0042],		# "SERVER ERROR: The updater is not ready yet."
	( 1, -75 )	: mbmsgs[0x0043],		# "服务器未启动"	"SERVER ERROR: There are no baseapps registered at present."
	( 1, -76 )	: mbmsgs[0x0044],		# "服务器负载过重，请稍后再试"	"SERVER ERROR: Baseapps are overloaded and logins are being temporarily disallowed."
	( 1, -77 )	: mbmsgs[0x0045],		# "服务器繁忙，请稍后再试"	"SERVER ERROR: Cellapps are overloaded and logins are being temporarily disallowed."
	( 1, -78 )	: mbmsgs[0x0046],		# "服务器未启动"	"SERVER ERROR: The baseapp that was to act as the proxy for the client timed out on its reply to the dbmgr. or The baseappmgr is not responding."
	( 1, -79 )	: mbmsgs[0x0047],		# "服务器负载过重"	"SERVER ERROR: The dbmgr is overloaded."
	( 1, -80 )	: mbmsgs[0x0048],		# "服务器未启动"	"SERVER ERROR: No reply from DBMgr."
	( 1, -250 )	: mbmsgs[0x0049],		# "账号已被 GM 托管！"	"账号已被 GM 托管！"
	( 1, -251 )	: mbmsgs[0x004a],		# "自动激活队列已满，请稍后再试。"	"SERVER ERROR: The auto active queue is overflow."
	( 2, 1 )	: mbmsgs[0x004b],		# "登录成功，开始接受数据"	"The client has begun to receive data from the server. This indicates that the conection process is complete."
	( 6, 1 )	: mbmsgs[0x004c],		# "从服务器断开"	"SERVER ERROR: The client has been disconnected from the server."
	}


# -----------------------------------------------------
class Loginer :
	def __init__( self, mgr ) :
		self.__lastStatus = Define.GST_NONE						# 记录下登录前的状态
		self.__lockedTime = None								# 账号是否被锁住
		self.__camHandler = LNCamHandler()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __parseDate( date ):
		"""
		将时间由数字转化成文字
		@type  date : int
		@param date : 秒数的时间
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

		if self.__lockedTime:													# 行号被封锁
			rds.resLoader.cancelCurrLoading()									# 停止资源加载
			rds.statusMgr.changeStatus( self.__lastStatus )						# 返回登录前的状态
			msg = mbmsgs[0x0023] % self.__parseDate( self.__lockedTime )
			ECenter.fireEvent( "EVT_ON_LOGIN_FAIL", msg )
			return

		if status == -254 :														# 启用 WGS Error Message
			msg = re.sub( "^[\d\s]+", "", msg )									# 去掉消息前面的号码
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
		if stage == 6 :															# 链接失败
			if not rds.statusMgr.isCurrStatus( Define.GST_LOGIN ) :
				BigWorld.resetEntityManager()
				gameMgr.onDisconnected()
		if stage == 1 and status == 1 :											# 链接成功
			# 当连接成功时，将要回调 gameMgr 的 onConnected，在 onConnected 中
			# 将会通知资源加载。而这个时候，如果账号被封，则服务器会在稍后的时间
			# 里（假设这段延时为 0.5 秒）回调这里的 onAccountlockedNotify 方法，
			# 此时，如果角色选择中的场景资源加载得足够快（即小于 0.2 秒）那么很可能
			# 将会进入到角色选择，这个时候，客户端才得知次账号是被封的。
			# 为了解决这样的问题，这里延时 0.5 秒在通知连接成功，进行角色选择的资源加载
			BigWorld.callback( 0.5, gameMgr.onConnected )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnter( self ) :
		loginSpace = loginSpaceMgr.loadLoginSpace( Define.LOGIN_TYPE_MAP )
		self.__camHandler.use()
		BigWorld.cameraSpaceID( loginSpace )		# 设置相机的照向场景
		BigWorld.spaceHold( True )
		self.__camHandler.run()

	def onLeave( self ) :
		pass

	def stopCamera( self ) :
		"""
		摄像机停止转动
		"""
		self.__camHandler.stop()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def requestLogin( self, server, userName, passwd ) :
		"""
		请求登录
		"""
		self.__lastStatus = rds.statusMgr.currStatus()
		self.__lockedTime = None						# 清除锁号标记
		gameMgr.requestLogin( server, userName, passwd, self.__onConnected )

	def onAccountlockedNotify( self, lockedTime ) :
		"""
		账号被锁住时调用
		"""
		self.__lockedTime = lockedTime


# --------------------------------------------------------------------
# implement space manager of roleselector
# --------------------------------------------------------------------
class RoleSelector :
	def __init__( self, mgr ) :
		self.__mgr = mgr
		self.__camShell = FLCShell()			# 相机
		self.__camTarget = None					# 相机对焦的 entity
		self.__faceRole = None					# 用于定位相机的 entity
		self.__vehicleEntity = None				# 用于旋转entity的圆盘entity
		self.__previewRoles = []				# 用于储存表示角色位置的entity
		self.__starePos = ( 0, 0, 0 )			# 相机凝视的点

		self.__loginRoles = []					# 每个元素是一个字典，这是服务器发过来的角色原始数据
		self.__selectable = True				# 是否允许选择角色
		self.__gpIndex = 0						# 候选角色组索引

		self.__roleModels = {}					# { 角色数据库ID : pyModel }

		self.__onPoseTime = False				# 动作施展时间，不允许进入游戏
		self.__isVerifySucess = False			# 是否通过图片认证
		self.__loadDefaultModelRoleIDs = []		# 加载相应模型失败（有可能缺少资源），使用默认模型信心加载模型的角色id
		self.__newRoleCreating = False			# 判定是否正在新建账号状态
		
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
		self.__gpIndex = 0						# 候选角色组索引


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# 初始化方法
	# -------------------------------------------------
	def __initCamTarget( self, callback ) :
		"""
		初始化相机绑定 entity
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
		初始化角色选择中间的转动圆盘及放在圆盘上的 entity
		"""
		self.__previewRoles = []
		for entity in BigWorld.entities.values() :						# 先初始化中间的转动圆盘
			flag = getattr( entity, "flag", None )
			if flag == "RS_PLATFORM":
				self.__vehicleEntity = entity
				entity.setToControl()
				break
		if self.__vehicleEntity is None:
			ERROR_MSG( "could't find entity which flag eq PLATFORM." )
			callback( 0 )
			return

		self.__previewRoles = range( 1, 10 )		# 预留9个位置，即我假设最多有9个角色，实际上当前只有3个
		for entity in BigWorld.entities.values() :
			flag = getattr( entity, "flag", None )
			if flag and flag.startswith( "RS_AVATAR_" ):
				# 注：当前直接使用name属性来表示是(非空值）否（空值）已使用，默认name属性为空。
				# 详看self.addRole()和self.__getEmptyEntity()代码
				entity.setToControl()
				entity.physics.teleportVehicle( self.__vehicleEntity )		# 使得 entity 固定在相对它 vehicle 的位置
				self.__previewRoles[int( flag[-1] )] = entity	# 以flag中的值的顺序放置
				# 初始化鼠标点击事件触发接口
				entity.onClick = self.__onClickRole
				entity.onMouseEnter = self.__onMouseEnterRole
				entity.onMouseLeave = self.__onMouseLeaveRole
				entity.oppositeTo( self.__vehicleEntity.position )
				continue

		# 去掉不存在的位置
		for i in xrange( len( self.__previewRoles ) - 1, -1, -1 ):
			if isinstance( self.__previewRoles[i], int ):
				self.__previewRoles.pop( i )

		if len( self.__previewRoles ) > 0 :
			self.__resortPreviewRoles()						# 将距离镜头最近的角色放到第一位
			callback( 1 )
		else :
			callback( 0 )

	def __initStarePos( self, callback ) :
		"""
		初始化凝视点
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
		cparam.setRadius( 1.5, True )				# 使相机与 entity 在同一地方
		cparam.stareAt( self.__starePos )
		callback( 1 )

	# ---------------------------------------
	def __initRoleModels( self, callback ) :
		"""
		加载所有候选角色模型
		"""
		loginRoles = copy.deepcopy( self.__loginRoles )
		# 如果总需要加载的角色为空，则直接通知加载完毕
		totalCount = len( loginRoles )
		if totalCount == 0: callback( 1.0 )

		for loginRole in loginRoles:
			roleInfo = RoleInfo( loginRole )
			roleID = roleInfo.getID()
			func = Functor( self.__onRoleModelLoad, callback, roleID, totalCount  )
			rds.roleMaker.createPartModelBG( roleID, roleInfo, func )

	def __initRoleDefaultModels( self, callback, roleID, totalCount ):
		"""
		加载角色的默认模型
		"""
		if roleID in self.__loadDefaultModelRoleIDs:	# 是否已经加载过默认模型
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
		模型加载玩回调
		"""
		if model is None:	# 有可能会反复加载也无法加载成功导致出错，暂时允许这个错误
			self.__initRoleDefaultModels( callback, roleID, totalCount )
			return
			
		self.__roleModels[roleID] = model
		# 通知 ResourceLoader 模型加载完毕
		currCount = len( self.__roleModels )
		callback( float( currCount/totalCount ) )
		if roleID in self.__loadDefaultModelRoleIDs:
			self.__loadDefaultModelRoleIDs.remove( roleID )
			
	def __showRoles( self, callback ) :
		"""
		显示候选角色
		"""
		roleCount = len( self.__loginRoles ) 			# 候选角色数量
		if roleCount == 0 :
			ECenter.fireEvent( "EVT_ON_DESELECT_ROLE" )
		else :
			entCount = len( self.__previewRoles )		# 每页角色数量
			count = min( roleCount, entCount )
			for idx in xrange( count ) :
				role = self.__previewRoles[idx]
				self.__resetPreviewRole( role, self.__loginRoles[idx] )
				if role.model: role.model.visible = False
		ECenter.fireEvent( "EVT_ON_RS_PAGE_CHANGED" )
		callback( 1.0 )

	# -------------------------------------------------
	# 私有 callback
	# -------------------------------------------------
	def __onClickRole( self, role ) :
		"""
		当某个角色被点击时被调用
		"""
		self.selectRole( role, True, True )

	def __onMouseEnterRole( self, role ) :
		"""
		当鼠标进入某角色时被调用
		"""
		if role == self.__getFaceEntity() : #取消鼠标移动到当前选择角色时，身上显示的高亮效果。
			try:
				role.model.enableShine = False
			except:
				pass

	def __onMouseLeaveRole( self, role ) :
		"""
		当鼠标离开某角色时被调用
		"""
		pass


	# -------------------------------------------------
	# 其它私有方法
	# -------------------------------------------------
	def __getEntity( self, roleID ) :
		"""
		根据角色 dbid，获取角色的 entity
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
		获取一个空的位置
		"""
		for e in self.__previewRoles :
			if e.name == '' :
				return e
		return None

	def __getFaceEntity( self, used = True ) :
		"""
		找出距离相机最近的一个角色，used 是否只考虑有模型的
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
		将距离镜头最近的角色放到第一位
		"""
		role = self.__getFaceEntity( False )
		self.__previewRoles.remove( role )
		self.__previewRoles.insert( 0, role )

	def __resetRolesYaw( self ):
		"""
		重新设置角色的面向
		"""
		for role in self.__previewRoles :
			role.oppositeTo( self.__vehicleEntity.position )

	# -------------------------------------------------
	def __resetPreviewRole( self, role, loginRole ) :
		"""
		设置一个 PreviewRole 的模型
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

		entity = self.__getFaceEntity()								# 获取当前选中的角色
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
		获得已经创建的角色数量
		"""
		return len( self.__loginRoles )

	def onInitRoles( self, loginRoles ) :
		"""
		when logined, informations of all roles in the account will receive
		@type			loginRoles : list of dictionary
		@param			loginRoles : [LOGIN_ROLE defined in alias.xml, ... ]
		"""
		self.__loginRoles = loginRoles
		historyID = gameMgr.getAccountOption( "selRoleID" )			# 获取上次选择的角色索引，wsf
		historyLoginRole = None										# 前一次进入游戏的角色
		for index,loginRole in enumerate( loginRoles ):				# 搜索前一次进入游戏的角色
			if loginRole["roleID"] == historyID :
				for i,v in enumerate( loginRoles[index:] ):
					historyLoginRole = loginRole
					self.__loginRoles.remove( v )				# 弹出前一次进入游戏的角色
					if historyLoginRole is not None :
						self.__loginRoles.insert( i, v )			# 将前一次进入游戏的角色放到第一位
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
			模型加载完回调
			"""
			BigWorld.callback( 0.38, self.__resetRolesYaw )
			if model is None :
				ERROR_MSG( "create role model fail which id is %i!" % roleInfo.getID() )
				return
			self.__roleModels[roleInfo.getID()] = model
			role = self.__getEmptyEntity()
			if not role : return
			self.__resetPreviewRole( role, loginRole )
			self.selectRole( role, False, False )							# 选中新创建的角色
		rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, callback )

	def onDeleteRole( self, roleID ) :
		"""
		call to delete a preview role
		"""
		for loginRole in self.__loginRoles[:] :						# 从角色列表中清除
			if loginRole['roleID'] == roleID :
				self.__loginRoles.remove( loginRole )
				break
		if roleID in self.__roleModels :
			self.__roleModels.pop( roleID )							# 从模型列表中去除角色对应的模型
		role = self.__getEntity( roleID )
		if role is None : return
		self.__resetPreviewRole( role, None )						# 清除角色模型表现
		ECenter.fireEvent( "EVT_ON_DESELECT_ROLE" )

	def onNameChanged( self, roleID, newName ) :
		"""
		角色名字改变
		"""
		for loginRole in self.__loginRoles :						# 查找角色
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
		获取初始化器，每个初始化器，初始化成功后，一定要返回 True
		"""
		return [
			self.__initCamTarget,				# 初始化相机绑定 entity
			self.__initPosList,					# 初始化导航点
			self.__initStarePos,				# 初始化相机凝视点
			self.__initCamera,					# 初始化相机
			self.__initRoleModels,				# 初始化候选角色模型（后台）
			self.__showRoles,					# 显示角色模型
			]

	# -------------------------------------------------
	def getRoleCount( self ) :
		"""
		获取候选角色个数
		"""
		return len( self.__loginRoles )

	def getPreviewCount( self ) :
		"""
		获取每页角色数量
		"""
		return len( self.__previewRoles )

	def getPageCount( self ) :
		"""
		获取分页分页数
		"""
		roleCount = len( self.__loginRoles )						# 候选角色总数
		viewCount = len( self.__previewRoles )						# 每组角色的个数
		return int( math.ceil( float( roleCount ) / viewCount ) )

	def getSelectedRoleInfo( self ) :
		"""
		获取选中角色的信息
		"""
		faceRole = self.__getFaceEntity()
		role = self.__getFaceEntity( False )
		if role == faceRole :
			return role.roleInfo
		return None

	# -------------------------------------------------
	def nextGroup( self ) :
		"""
		转到下一组候选角色
		"""
		self.setlectGroup( self.__gpIndex + 1 )
		if self.getPageCount() <= 1 :
			ECenter.fireEvent( "EVT_ON_RS_PAGE_CHANGED" )

	# -------------------------------------------------
	def setlectGroup( self, gpIdx ) :
		"""
		设置组索引
		"""
		roleCount = len( self.__loginRoles )						# 候选角色总数
		if not roleCount :											# 没有任何角色
			ECenter.fireEvent( "EVT_ON_DESELECT_ROLE" )
			return

		for role in self.__previewRoles :							# 先清除所有模型
			self.__resetPreviewRole( role, None )					# 如果不清除，后面将无法设置

		gpCount = self.getPageCount()								# 分组数
		gpIdx = gpIdx % gpCount										# 控制组索引，不要超出最大组数
		self.__gpIndex = gpIdx

		startIdx = gpIdx * len( self.__previewRoles )				# 起始索引
		for i, role in enumerate( self.__previewRoles ) :
			index = startIdx + i
			if index < roleCount :
				self.__resetPreviewRole( role, self.__loginRoles[index] )

	def selectRole( self, role, slowly, isPose = True ) :
		"""
		选择一个角色
		slowly				: 是否慢慢地转动圆台选中
		isPose				: 是否播放pose动作
		"""
		if not self.__selectable : return
		self.lockContrl()
		func = Functor( self.onSelectRoleArrived, role, slowly, isPose )
		if slowly :
			self.__vehicleEntity.sostenutoRotate( role.position, \
				self.__faceRole.position, 0.1, 0.005, func, self.rotating )	# 缓慢转动
		else :
			self.__vehicleEntity.instantRotate( role.position, self.__faceRole.position, func )

	def rotating( self, yaw ):
		"""
		正在移动中的回调
		"""
		self.__resetRolesYaw()

	def onSelectRoleArrived( self, role, slowly, isPose, success = True ):
		"""
		选择角色转盘转到目标点
		"""
		self.unlockContrl()
		if not success: return
		ECenter.fireEvent( "EVT_ON_SELECT_ROLE" )
		role.switchRandomAction( True )									# 触发随机动作
		if isPose:
			func = Functor( self.onPlayerPoseActionOver, role )
			self.__onPoseTime = True
			INFO_MSG( "set pose flag true." )
			if not role.playPoseAction( cb = func ):							# 播放选中角色动作
				self.__onPoseTime = False
				
		BigWorld.callback( 0.5, self.__resortPreviewRoles )				# 重新将靠镜头最近的角色放到列表的第一位
		if not slowly :													# 如果是瞬间转动
			self.__resetRolesYaw()										# 则转动完毕后重新设置角色面向

	def onPlayerPoseActionOver( self, role ):
		"""
		角色pose动作播放完毕回调
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
		锁住，不允许选择角色
		"""
		self.__selectable = False
		ECenter.fireEvent( "EVT_ON_LOST_CONTROL" )

	def unlockContrl( self ) :
		"""
		解锁，允许选择角色
		"""
		self.__selectable = True
		ECenter.fireEvent( "EVT_ON_GOT_CONTROL" )

	# -------------------------------------------------
	def renameSelRole( self, newName ) :
		"""
		重命名角色
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
			gameMgr.setAccountOption( "selRoleID", roleInfo.getID() )		# 进入游戏，保存最后一次选择的角色 index，wsf
			rds.gameMgr.requestEnterGame( roleInfo )

	def cleanAvatars( self ) :
		"""
		将所有角色模型清空
		"""
		for role in self.__previewRoles :
			self.__resetPreviewRole( role, None )

	def onVerifySuccess( self ):
		"""
		验证图片通过
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
	__cc_close_radius	= 1.0							# 近镜头
	__cc_far_radius		= 2.5							# 远镜头

	def __init__( self, mgr ) :
		self.__mgr = mgr
		self.__camHandler = RCCamHandler()				# 相机
		self.__dsps = {}								# 职业描述
		self.__selectRole = None
		self.__spaceID =  0
		self.__faceRole = None							# 用于定位相机的 entity
		self.__yaw = 0.0 #选中的角色的朝向改变值
		#self.__avatar = None							# 角色
		self.__camYaw = 0								# 相机 yaw 值
		self.__turnRoleCBID = 0							# 旋转角色的 callbackID
		self.__currCamp = csdefine.ENTITY_CAMP_NONE		# 当前选择的角色阵营
		self.__currGender = None						# 当前选择的角色性别
		self.__currProfession = None					# 当前选择的角色职业
		self.__roleModels = {}							# 所有职业、性别对应的模型
		self.__allModelInfo = {}						# 所有职业、性别对应的模型info
		self.__currHairNum = 0							# 当前选择的发型编号
		self.__currFaceNum = 0							# 当前选择的脸型编号
		self.__currHeadTextureID = 0					# 当前选择的头像编号 by姜毅
		self.__canSelectRoles = []
		self.cbid = 0
		self.__selectedCampEn = None #选中的阵营entity
		self.__models = {}
		self.__models[ csdefine.ENTITY_CAMP_TAOISM ] = ( BigWorld.Model( Const.EMPTY_MODEL_PATH ), Pixie.create( Sources.PARTICLE_CAMP_TAOISM ) )
		self.__models[ csdefine.ENTITY_CAMP_DEMON ]  = ( BigWorld.Model( Const.EMPTY_MODEL_PATH ), Pixie.create( Sources.PARTICLE_CAMP_DEMON ) )
		self.onBackToSelector = False #是否是退出到选择角色界面的操作

	def dispose( self ) :
		BigWorld.cancelCallback( self.cbid )
		self.__faceRole = None
		#self.__avatar = None
		self.__currCamp = csdefine.ENTITY_CAMP_NONE
		self.__currGender = None
		self.__currProfession = None
		self.__selectRole = None
		self.__canSelectRoles = []
		#在这里清理所有CameraEntity
		for en in BigWorld.entities.values():
			if en.__class__.__name__ == "CameraEntity":
				BigWorld.destroyEntity( en.id )
		self.cbid = 0

	def getSelectRole( self ):
		return self.__selectRole
	
	def loadModelSource( self ):
		"""
		预加载模型资源
		"""
		for profession in ROLE_PROFESSION:
			for gender in ROLE_GENDER:
			    roleInfo = getCommonRoleInfo( profession, gender )
			    func = Functor( self.onModelLoadCompleted2, roleInfo )
			    rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )
	
	def onModelLoadCompleted2( self, roleInfo, model ):
		"""
		模型加载完回调
		"""
		self.onCreateModelLoad( roleInfo, model )

	def showAllEntities( self ) :
		"""
		初始化所有 entity
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
		模型加载完回调
		"""
		if self.__selectRole: #如果已经选中了要创建的角色则不需要显示了
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
		检测8个role是否加载完毕
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
		获取某个角色的朝向
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
		创建界面的退出按钮也会触发本函数
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
		加载阵营选择界面、模型等相关资源
		"""
		self.preLoadSpace( Define.SELECT_CAMP_TYPE_MAP )
		spaceID = self.getSpaceID()
		self.checkCreateOver( )
	
	def checkCreateOver( self ):
		"""
		检测是否已经创建完毕
		"""
		cameraEntities = []
		for en in BigWorld.entities.values():
			if en.__class__.__name__ == "CameraEntity" and en.spaceID == self.getSpaceID() and en.getModel():
				cameraEntities.append( en )
		if len(cameraEntities) == 2 :
			for entity in cameraEntities:
				entity.isAlwaysExist = True
				entity.setSelectable( True )# 设置 targetCaps 属性
				entity.selectable = True
				entity.onMouseEnter = self.onEnterCampEntity
				entity.onMouseLeave = self.onLeaveCampEntity
				entity.onClick = self.onClickCampEntity
				model = self.__models[entity.flagID][0]
				if len( entity.models ) == 0 :
					entity.addModel( model )
					model.position = entity.position
		else:
			BigWorld.callback( 0.1, self.checkCreateOver ) #给一个延迟时间

	def cancelSelectedCamp( self ):
		"""
		取消当前的阵营选择
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
		触发的光效
		"""
		if len( self.__models[en.flagID][0].root.attachments ) == 0:
			self.__models[en.flagID][0].root.attach( self.__models[en.flagID][1] )
	
	def delEffect( self, en ):
		"""
		删除光效
		"""
		if len( self.__models[en.flagID][0].root.attachments ) == 1:
			self.__models[en.flagID][0].root.detach( self.__models[en.flagID][1] )
	
	def startEnterRoleCreator( self, camp ):
		"""
		阵营选择结束，进入创建角色地图
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
		进入选择角色地图后需要先加载一些东西
		"""
		camp = self.__currCamp
		self.preLoadSpace( camp )
		callback( 1.0 )
	
	def preLoadSpace( self, camp ):
		"""
		先加载地图
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
			m.setTranslate( pos )							# 定点到 space 里面存在 chunk 的坐标上
			cc.target = m								# 使得场景加载时不会出现加载位置不对
			self.__camHandler.disable() #摄像机无法旋转
			
			#设置角度值
			#cc.source.setRotateYPR( dir )
			self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
			self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
			self.__camHandler.cameraShell.update()
			cc.pivotMaxDist = 1.1
		except:	# 因为场景加载范围是根据相机位置来确定的
			pass
	
	def initRoleEntity( self, callback ):
		"""
		初始化地图8个角色实体
		"""
		self.showAllEntities()
		callback( 1.0 )
	
	def onEnterRoleCreate( self, camp ):
		"""
		进入创建角色界面
		"""
		self.resetCamp( camp )
		ECenter.fireEvent( "EVT_ON_ROLE_CREATOR_SHOW" )
		loginSpace = self.getSpaceID()
		DEBUG_MSG( "RoleCreator enter space", loginSpace )
		BigWorld.cameraSpaceID( loginSpace )							# 设置相机的照向场景
		BigWorld.spaceHold( True )
		try:
			pos = P_D_M_T_CAMERA[camp][0]
			dir = P_D_M_T_CAMERA[camp][1]
			self.__camHandler.use( self.__camYaw )
			cc = BigWorld.camera()
			m = Math.Matrix()
			m.setTranslate( pos )			# 定点到 space 里面存在 chunk 的坐标上
			cc.target = m				# 使得场景加载时不会出现加载位置不对
			
			self.__camHandler.disable() #摄像机无法旋转
			#设置角度值
			self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
			self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
			self.__camHandler.cameraShell.update()
			cc.pivotMaxDist = 1.1
		except:	# 因为场景加载范围是根据相机位置来确定的
			pass

	def getSpaceID( self ):
		"""
		获得spaceID
		"""
		return self.__spaceID
	
	def onBackRoleCreate( self ):
		"""
		返回选择要创建的角色界面(上一步按钮)
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
			m.setTranslate( pos )							# 定点到 space 里面存在 chunk 的坐标上
			cc.target = m								# 使得场景加载时不会出现加载位置不对
			
			self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
			self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
			self.__camHandler.cameraShell.update()
			cc.pivotMaxDist = 1.1
		except:	# 因为场景加载范围是根据相机位置来确定的
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
		当鼠标进入某角色时被调用
		"""
		if role == self.__selectRole : #取消鼠标移动到当前选择角色时，身上显示的高亮效果。
			try:
				role.model.enableShine = False
			except:
				pass

	def __onClickRole( self, role ):
		"""
		当鼠标选择某角色时被调用
		"""
		if self.__selectRole: return
		self.__selectRole = role
		self.__yaw = role.yaw
		role.clearAttachments()
		role.playPoseAction( cb = self.onSelectedOver )
		#隐藏其他角色
		for en in self.__canSelectRoles:
			if en.id != role.id and en.model:
				en.model.visible = False
		#摄像机位置改变			
		self.__camHandler.cameraShell.setEntityTarget( role )
		camp = self.__currCamp
		dir = P_D_M_T_CAMERA[camp][1]
		self.__camHandler.cameraShell.setPitch( math.pi- dir[1] ) 
		self.__camHandler.cameraShell.setYaw( math.pi + dir[0] )
		self.__camHandler.cameraShell.update()
		
	def onSelectedOver( self ):
		"""
		选中角色播完动作回调
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
		选中的角色
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
	#	获取所有初始化器，每个初始化器，初始化成功后，一定要返回 True
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
		选择发型
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
		选择脸型
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
		选择头像
		"""
		self.__currHeadTextureID = headIndex

	def onModelLoadCompleted( self, roleInfo, model ):
		"""
		模型加载完回调
		"""
		gender = roleInfo.getGender()
		profession = roleInfo.getClass()
		key = gender | profession
		self.__roleModels[key] = model
		self.__allModelInfo[key] = roleInfo
		self.onCreateModelLoad( roleInfo, model )
		# 如果回调的时候的模型不是玩家点击所要的模型就return
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
		武器附加属性效果
		@type		model 		: pyModel
		@param		model 		: 模型
		@type		weaponDict 	: FDict
		@param		weaponDict 	: 武器数据
		"""
		pType = Define.TYPE_PARTICLE_PLAYER
		# 模型Dyes
		dyes = rds.roleMaker.getMWeaponModelDyes( weaponDict )
		rds.effectMgr.createModelDye( model, dyes )
		# 自带光效
		weaponNum = weaponDict["modelNum"]

		effectIDs = rds.itemModel.getMEffects( weaponNum )
		for effectID in effectIDs:
			dictData = rds.spellEffect.getEffectConfigDict( effectID )
			if len( dictData ) == 0: continue
			effect = rds.skillEffect.createEffect( dictData, model, model, pType, pType )
			effect.start()

		# 镶嵌光效
		stAmount = weaponDict["stAmount"]
		xqHp = rds.equipParticle.getXqHp( stAmount )
		xqGx = rds.equipParticle.getXqGx( stAmount )
		for hp, particle in zip( xqHp, xqGx ):
			rds.effectMgr.createParticleBG( model, hp, particle, type = pType )
		# 强化自发光
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
		角色创建画面的整个身体模型加载完回调
		"""
		def onLoadRightModel( rightModel ):
			def onRightLoftLoad( particle ):
				"""
				右手刀光加载完成
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
				左手刀光加载完成
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

		# 发型
		rds.roleMaker.createHairModelBG( roleInfo.getHairNumber(), 0, profession, gender, onHairModelLoad )
		# 左右手武器
		rds.roleMaker.createMWeaponModelBG( roleInfo.getRHFDict(), onLoadRightModel )
		rds.roleMaker.createMWeaponModelBG( roleInfo.getLHFDict(), onLoadLeftModel )
		# 发光
		bodyFDict = roleInfo.getBodyFDict()
		feetFDict = roleInfo.getFeetFDict()
		
		############胸部位置光效######################
		intensifyLevel = bodyFDict["iLevel"]
		# 绑定新的身体发射光芒效果(胸部装备强化至4星时出现)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# 绑定新的各职业向上升光线(胸部装备强化至6星时出现)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# 绑定新的身体周围盘旋上升光带( 胸部装备强化至9星时出现 )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, None, Define.TYPE_PARTICLE_PLAYER )

		# 绑定新的龙型旋转光环( 胸部装备强化至9星时出现 )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
		###########鞋子光效#################################
		intensifyLevel = feetFDict["iLevel"]
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
		
		
		# 法师特有粒子效果
		if roleInfo.getClass() == csdefine.CLASS_MAGE:
			rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER  )
	
	def turnRole( self, direction ) :
		"""
		旋转当前角色，如果 direction 为正数则向左转，为负数则向右转，为 0 则停止旋转
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
		镜头靠近角色
		"""
		self.__camHandler.closeTarget()

	def viewFar( self ) :
		"""
		镜头远离角色
		"""
		self.__camHandler.extendTarget()

	# -------------------------------------------------
	def getRaceClass( self ) :
		"""
		获取当前选中角色的职业
		"""
		profession = self.__currProfession
		gender = self.__currGender
		race = csconst.RACE_CLASS_MAP[profession]
		camp = self.__currCamp<<20
		return race | profession | gender|camp

	def getDescription( self, profession ) :
		"""
		获取职业描述
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
		获取阵营描述
		"""
		try:
			return g_CampDspData[camp]
		except:
			ERROR_MSG( "can't find camp description config file!" )
			return ""
	
	def getCampVoice( self, camp ):
		"""
		获取阵营语音路径
		"""
		return ""

	def createRole( self, name ) :
		"""
		call to create a role
		@type			name : str
		@param			name : the name the the role you want to create
		"""
		if len( name ) > 14 :
			# "名字长度不能超过 14 个字节"
			self.showAutoHideMsg( 0x0050 )
		elif name == "" :
			# "您输入的用户名无效，请重新输入"
			self.showAutoHideMsg( 0x0051 )
		elif not rds.wordsProfanity.isPureString( name ) :
			# "名称不合法！"
			self.showAutoHideMsg( 0x0052 )
		elif rds.wordsProfanity.searchNameProfanity( name ) is not None :
			# "输入的名字有禁用词汇！"
			self.showAutoHideMsg( 0x0053 )
		elif roleSelector.getRoleCount() >= csconst.LOGIN_ROLE_UPPER_LIMIT :
			# "存在角色数量已经达到上限！"
			self.showAutoHideMsg( 0x0054 )
		else :
			raceclass = self.getRaceClass()
			BigWorld.player().createRole( raceclass, name, self.__currHairNum, self.__currFaceNum, self.__currHeadTextureID )	
	
	def onCreateCB( self ):
		"""
		创建角色从base端通知客户端创建OK
		"""
		self.dispose()
		#隐藏创建角色界面
		ECenter.fireEvent( "EVT_ON_ROLECREATOR_OK" )

	def showAutoHideMsg( self, msg ): 									# 用来综合处理角色创建界面提示，解决提示框会重复出现的问题
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
	#	将所有角色模型清空
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

		self.loginer = Loginer( self )					# 登录器
		self.roleSelector = RoleSelector( self )		# 角色选择器
		self.roleCreator = RoleCreator( self )			# 角色创建器

		self.__initCallback = None						# 临时变量，保存场景初始化回调
		self.__detectCBID = 0							# 场景加载侦测回调

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
		当离线时被调
		"""
		BigWorld.cancelCallback( self.__detectCBID )					# 如果在场景加载过程中断开了服务器
		self.__detectCBID = 0											# 则停止进度侦测


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enter( self ) :
		"""
		请求进入登录场景的加载
		"""
		#self.roleCreator.initModelBG()									# 后线程加载角色创建所有模型
		loginSpace = loginSpaceMgr.loadLoginSpace( Define.LOGIN_TYPE_MAP )
		DEBUG_MSG( "loginMgr enter space", loginSpace )
		BigWorld.cameraSpaceID( loginSpace )							# 设置相机的照向场景
		BigWorld.spaceHold( True )
		try:
			m = Math.Matrix()
			m.setTranslate( ( 238, 8, 110 ) )							# 定点到 space 里面存在 chunk 的坐标上
			BigWorld.camera().target = m								# 使得场景加载时不会出现加载位置不对
		except:															# 因为场景加载范围是根据相机位置来确定的
			pass

	def leave( self ) :
		"""
		请求离开角色选择和角色创建场景
		"""
		self.__initCallback = None										# 清除回调
		newStatus = rds.statusMgr.currStatus()
		if newStatus == Define.GST_LOGIN :
			self.roleSelector.cleanAvatars()
			#self.roleCreator.cleanAvatars()
		else :
			loginSpaceMgr.releaseAllLoginSpace()											# 释放登陆地图
			self.roleSelector.onLeave( Define.GST_ENTER_WORLD_LOADING )
			self.roleSelector.dispose()									# 删除角色选择器
			self.roleCreator.onLeave()
			self.roleCreator.dispose()									# 删除角色创建器


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
		创建地图
		type：int 地图的类型
		"""
		mapN = LOGIN_SPACE_TYPE_MAP[ type ]
		loginSpaceID = self.__spaceID[ type ]
		if loginSpaceID == 0 :
			loginSpaceID = BigWorld.createSpace()			# 创建场景
			BigWorld.addSpaceGeometryMapping( loginSpaceID, None, mapN )	# 加载场景数据
			BigWorld.worldDrawEnabled( True ) # 开启场景绘制
			self.__spaceID[ type ] = loginSpaceID
		return loginSpaceID

	def releaseLoginSpace( self, type ):
		"""
		释放地图
		type：int 地图的类型
		"""
		loginSpaceID = self.__spaceID[ type ]
		BigWorld.spaceHold( False )
		BigWorld.cameraSpaceID( 0 )										# 把相机撤出 space
		BigWorld.clearSpace( loginSpaceID )							# 清空 space 信息
		self.__spaceID[ type ] = 0
	
	def releaseAllLoginSpace( self ):	
		"""
		释放所有登陆地图
		"""
		for loginSpaceID in self.__spaceID.values():
			if loginSpaceID != 0:
				BigWorld.clearSpace( loginSpaceID )							# 清空 space 信息
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
