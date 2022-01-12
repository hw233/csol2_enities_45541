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
		self.tongEntity = None		# 由于角色的base是固定的，因此可以直接设置
		self.tong_dbID = self.cellData[ "tong_dbID" ]
		self.tong_grade = self.cellData[ "tong_grade" ]
		self._tong_sign_string_req_list = []	# 具体到该角色的帮会会标获得请求队列
		self.signSending = False		# 是否正在向客户端传送会标
		self.isSignSendReady = False	# 是否已完成发送准备

		try:
			self.cellData[ "tong_level" ] = BigWorld.baseAppData[ "tong.%i" % self.tong_dbID ][ "level" ]
		except:
			pass
			
	def tong_logonInTerritory( self, position, direction ):
		"""
		define method.
		在领地中登陆
		"""
		DEBUG_MSG( "because not found spaceCopy， so is login to tong territory。", position, direction )
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
		在领地中登陆错误， 可能某帮会被解散或者是一个不存在的帮会领地
		"""
		WARNING_MSG( "player login find a not exist the territory[%i]， begin goto spawnpoint。" % self.cellData[ "lastTongTerritoryDBID" ] )
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

		# 如果还没有cell 那么写到celldata中
		if not hasattr( self, "cell" ):
			self.cellData[ "tong_dbID" ] = 0
			self.cellData[ "tong_grade" ] = 0
			self.writeToDB()
		else:
			self.cell.tong_reset()

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

	def tong_setGrade( self, grade ):
		"""
		define method.
		设置该player grade
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
		设置该player grade
		"""
		if self.tong_scholium != scholium:
			self.tong_scholium = scholium

	def tong_onLogin( self ):
		"""
		define method.
		登陆帮会
		"""
		if self.tong_dbID > 0:
			self.getTongManager().onMemberLoginTong( self.tong_dbID, self, self.databaseID )

	def tong_onLogout( self ):
		"""
		下线帮会
		"""
		if self.tong_dbID > 0:
			self.getTongManager().onMemberLogoutTong( self.tong_dbID, self.databaseID )

	def tong_onLoginCB( self, tongEntity ):
		"""
		define method.
		登陆完毕回调
		@param tongEntity: 帮会entity的baseEntity 如果登陆失败返回的是none
		"""
		if tongEntity:
			self.tongEntity = tongEntity
			self.cell.tong_onLoginCB( tongEntity )
		else:
			# 登陆失败了
			ERROR_MSG( "player %s:%i >>cannot login to tong dbid=%i!" % ( self.playerName, self.id, self.tong_dbID ) )

	#-------------------------------------------------------------------------------------------------------
	def tong_sendMessage( self, memberDBID, msg ):
		"""
		Exposed method.
		对某成员发送消息
		"""
		self.tongEntity.onSendMessage( self.playerName, memberDBID, msg )

	def tong_onLevelChanged( self ):
		"""
		自身级别被改变了
		"""
		if self.tongEntity:
			self.tongEntity.onMemberLevelChanged( self.databaseID, self.level )

	def tong_requestMemberMapInfos( self ):
		"""
		Exposed method.
		对某成员发送消息
		"""
		if self.tongEntity:
			self.tongEntity.requestMemberMapInfo( self, self.databaseID )

	def isJoinTong(self):
		"""
		判断玩家是否加入帮会
		tong_grade 不为0 表示玩家一定加入了帮会
		"""
		return self.tong_grade!=0


	def sendMessage2Tong(self, playerID, playerName, msg, blobArgs ):
		"""
		发送消息给帮会所有玩家
		"""
		if self.tongEntity:
			self.tongEntity.onSendChatMessageAll( self.databaseID, msg, playerID, playerName, blobArgs )

	def onTeleportCityWar( self, spaceMailbox, position, direction ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "TongManager" ].onTeleportCityWar( spaceMailbox, position, direction, self, self.tong_dbID )


	# ------------------------------------------------ 帮会仓库 -----------------------------------------------------
	def tong_requestStorageItem( self, count ):
		"""
		Exposed method.
		请求仓库物品数据

		@param count : 请求的次数
		@type count : INT8
		"""
		if count > 11:	# 每次申请40个物品格的数据,帮会仓库一共6个包裹,超过11说明此参数不正确
			return
		if self.tongEntity:
			self.tongEntity.requestStorageItem( self.databaseID, count )


	def tong_requestStorageLog( self, count ):
		"""
		Exposed method.
		请求仓库log信息

		@param count : 请求的次数
		@type count : INT8
		"""
		if self.tongEntity:
			self.tongEntity.requestStorageLog( self.databaseID, count )

	# ------------------------------------------------ 帮会会标 by 姜毅-----------------------------------------------------
	def tong_submitSignReady( self, iconMD5, iconstrlen, packs_num ):
		"""
		Exposed method.
		上传帮会图标预备

		@param iconMD5 : 图标转换成的MD5,用于完成上传后校验
		@type  iconMD5 : STRING
		@param iconstrlen : 会标字符串长度,用于校验too
		@type  iconstrlen : INT32
		@param packs_num : 会标分开包的个数,用于校验three
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
		上传帮会图标

		@param iconString : 图标转换成的字符串
		@type  iconString : STRING
		@param index : 分包图标的包序号
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
		上传会标成功回调
		
		@param iconMD5 : 图标生成的MD5码
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
		更换帮会图标

		@param isSysIcon : 是否系统图标
		@type  isSysIcon : BOOL
		@param reqMoney  : 所需金钱
		@type  reqMoney  : INT32
		@param iconMD5 : 图标生成的MD5码
		@type  iconMD5 : INT64
		"""
		self.tongEntity.changeTongSing( isSysIcon, reqMoney, iconMD5, self )

	def tong_cancleSing( self ):
		"""
		Exposed method.
		取消帮会图标
		"""
		self.tongEntity.setTongSignMD5( "" )
		self.statusMessage( csstatus.TONG_SIGN_CANCLE_SUCCESS )

	def getTongSignMD5( self, tongDBID ):
		"""
		Exposed method
		根据DBID获取其它帮会的帮会会标DBID
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
		客户端请求获得帮会会标string数据
		"""
		if tongDBID <= 0:
			ERROR_MSG( "get tong sign string tong dbid error %i ."%tongDBID )
			return
		self._tong_sign_string_req_list.append( tongDBID )
		
	def sendTongSignString( self ):
		"""
		处理会标发送给客户端
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
		开始分包传输会标字符串
		"""
		self.iconStringList = iconStringList
		self.iconSendingTongDBID = tongDBID
		self.client.clientGetTongSignReady( tongDBID, len( self.iconStringList ), iconMD5 )
		
	def onClientGetTongSignReady( self ):
		"""
		Exposed
		客户端已准备好接受图标的回调
		"""
		self.isSignSendReady = True
		
	def sendIconPackToClient( self ):
		"""
		发送会标包到客户端
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
		通过玩家名字邀请玩家加入帮会
		"""
		if self.playerName == playerName:
			self.statusMessage( csstatus.TONG_TARGET_SELF )
			return

		if self.tong_dbID > 0 and self.tongEntity:
			Love3.g_baseApp.lookupRoleBaseByName( playerName, self.tong_findBeInvitedPlayerBaseCB )

	def tong_findBeInvitedPlayerBaseCB( self, baseMailbox ):
		"""
		@param baseMailbox : 如果目标玩家在线则是其base mailbox，否则为None
		"""
		if baseMailbox:
			baseMailbox.tong_onPlayerRequestJoinByMyName( self.tongEntity, self, self.databaseID, self.getCamp() )
		else:
			self.statusMessage( csstatus.TONG_TARGET_NO_FIND )
			
	def tong_onPlayerRequestJoinByMyName( self, tongEntity, user, userDBID, userCamp ):
		"""
		有人通过我的名称远程邀请我加入tong
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
		加帮会成功，设置帮会数据
		
		@param tongDBID : 帮会的dbid
		@type tongDBID : DATABASE_ID
		@param grade : 帮会职位
		@type grade : UINT8
		@param tongBaseMailbox : 帮会的base mailbox
		@type tongBaseMailbox : MAILBOX
		"""
		self.tongEntity = tongBaseMailbox
		self.tong_dbID = tongDBID
		self.tong_grade = grade
		self.tong_totalSignInRecord = 0

	def tong_leave( self ):
		"""
		Define method.
		离开帮会的处理
		"""
		self.tong_dbID = 0
		self.tong_grade = 0
		self.tong_totalSignInRecord = 0
		self.tongEntity = None
		
	def clearTongDartRecord( self ):
		"""
		Define method
		清楚帮会运镖记录
		"""
		self.tongEntity.clearTongDartRecord()
		
	def setTongFactionCount( self, count ):
		"""
		Define method
		设置帮会时装标余量
		"""
		self.tongEntity.setTongFactionCount( count )

	#---------------------------------------- 帮会俸禄相关 ---------------------------------------------------
	def tong_requestMemberContributeInfos( self ):
		"""
		Exposed method.
		对某成员发送帮贡相关消息
		"""
		if self.tongEntity:
			self.tongEntity.requestMemberContributeInfos( self.databaseID )

	#---------------------------------------- 帮会签到相关 ---------------------------------------------------
	def tong_requestSignInRecord( self ):
		"""
		define method
		打开帮会界面，请求帮会签到数据
		"""
		if not self.tong_dailySignInRecord.checklastTime():
			self.tong_dailySignInRecord.reset()
		
		self.client.tong_onSetSignInRecord( self.tong_dailySignInRecord.getDegree(), self.tong_totalSignInRecord )
		
	def tong_requestSignIn( self ):
		"""
		Exposed method
		帮会签到
		"""
		if not self.tongEntity:
			return
		
		if not self.tong_dailySignInRecord.checklastTime():
			self.tong_dailySignInRecord.reset()
		
		if self.tong_dailySignInRecord.getDegree() >= Const.TONG_SIGN_UP_TIMES_LIMIT:
			return

		# 签到次数增加
		self.tong_dailySignInRecord.incrDegree()
		self.tong_totalSignInRecord += 1
		INFO_MSG( "TONG: %s sign in , his totoal sign in record is %i " % ( self.getNameAndID(), self.tong_totalSignInRecord ) )
		# 帮会获得经验
		self.tongEntity.addExp( Const.TONG_SIGN_UP_GAIN_EXP, csdefine.TONG_CHANGE_EXP_SIGN_IN )
		self.statusMessage( csstatus.TONG_SIGN_IN_SUCCESS, Const.TONG_SIGN_UP_GAIN_EXP )

		self.client.tong_onSetSignInRecord( self.tong_dailySignInRecord.getDegree(), self.tong_totalSignInRecord )
	
	def requestTongExp( self ):
		"""
		Exposed method
		玩家请求帮会经验数据
		"""
		self.tongEntity.roleRequestTongExp( self.databaseID )

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/07/22 03:43:42  huangdong
# 修改了帮会聊天一个接口名
#
# Revision 1.4  2008/07/22 01:58:33  huangdong
# 完善帮派聊天
#
# Revision 1.3  2008/06/16 09:13:04  kebiao
# 增加权衡关系
#
# Revision 1.2  2008/06/14 09:18:51  kebiao
# 新增帮会功能
#
# Revision 1.1  2008/06/09 09:24:33  kebiao
# 加入帮会相关
#
#