# -*- coding: gb18030 -*-

# $Id: BaseappEntity.py,v 1.8 2008-08-30 09:02:43 huangyongwei Exp $
"""
目的：希望每个baseapp都能知道其它的baseapp，以便广播一些包，
因此我们需要在每个baseapp上产生一个BaseEntity并把它注册成为globalBase，
以此来标识每一个baseapp，那么，我们就可以通过这个baseEntity广播一些数据到所有的baseapp上，
如：全局聊天

对于全局聊天的流程详看CS_OL.MDL

因为目前“_localPlayers”这个列表里面存放了所以在线角色的entity；
所以现在的聊天广播(_localBroadcast()方法)中不需要再遍历所有BigWorld.entities，从而提高了效率。
"""

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import csstatus
from bwdebug import *
from Role import Role
from Love3 import loginAttemper
import Const
from MsgLogger import g_logger


TIMER_LOOKUP_ROLE_BASE = 123
TIMER_SHUTDOWN_SERVER = 124
TIMER_DELAY_SHUTDOWN = 125


class ShutdownTimer:
	"""
	（CSOL-6602）需要增加服务器关机倒计时，15分钟开始倒计时。前10分钟每分钟系统提示一次玩家，后5分钟30秒一次系统提示关服时间。
	"""
	def __init__( self, baseappEntity, delay ):
		"""
		@param parent: instance of baseapp entity
		@param delay: 延迟多长时间执行shutdown行为。单位：秒
		"""
		self.baseappEntity = baseappEntity
		self.delay = int( delay )

		self.__call__()

	def __call__( self ):
		"""
		"""
		if self.delay <= 0:
			self.baseappEntity.shutdownAll( 0 )
			self.baseappEntity = None
			return

		d = self.delay
		if d <= 30:
			msg = cschannel_msgs.BASEAPPENTITY_NOTICE_0 % d
		elif d <= 300:
			m = d % 60
			if m:
				msg = cschannel_msgs.BASEAPPENTITY_NOTICE_1 % ( d / 60, m )
			else:
				msg = cschannel_msgs.BASEAPPENTITY_NOTICE_2 % ( d / 60 )
			d = 30	# 最后5分钟每30秒提示一次
		else:
			msg = cschannel_msgs.BASEAPPENTITY_NOTICE_3 % ( d / 60 )
			d = 60	# 前面的每分钟提示一次
		self.delay -= d
		self.baseappEntity.anonymityBroadcast( msg, [] )
		self.baseappEntity.addTimer( d, 0, TIMER_DELAY_SHUTDOWN )

class BaseappEntity( BigWorld.Base ):
	"""
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )

		# 记录所有和自己同一类型的其它baseApp mailbox
		# 这样每次广播的时候就可以直接使用，而不需要再次到BigWorld.globalBases里去查询比较
		self.globalData = {}

		# entity创建队全，值为任意的本地spaceEntity，
		# 第一个为当前正在创建的space，最后一个为最后加入的space，以此类推
		self.spawnQueue = []

		# 使用自己的entityID加上前缀形成唯一的名字
		# GBAE is global baseApp Entity, don't use "GBAE*" on other globalBases Key
		self.globalName = "%s%i" % ( csconst.C_PREFIX_GBAE, self.id )
		self.registerGlobally( self.globalName, self.registerCallback )

		# 通过在此baseapp上线的玩家的名称与entity实例的对应表
		# { "玩家名称" : instance of entity which live in BigWorld.entities, ... }
		self._localPlayers = {}
		self._localCampPlayers = {}

		# 临时列表，用于实现lookupRoleBaseByName()的回调机制
		# { 临时唯一ID : [ 预期回复数量, 超时时间, callback ], ...}
		# “预期回复数量”：指的是当前向几个baseapp发送了请求，每收到一个回复，该值将减一
		# “超时时间”：单位“秒”，float；每秒检测一次，如果超时则中断并回调通知目标未找到。会产生此问题的原因很可能是运行过程中某台baseapp崩溃了
		# callback: function；由调用者提供的回调函数
		self._tmpSearchCache = {}
		self._tmpSearchCurrentID = 0	# 用于记录最后一次分配的ID值，值 0 用于表示没有或失败，因此不作为可用ID分配
		self._searchTimerID = 0			# 用于检查某个lookupRoleBaseByName()请求是否过期的timer

		self._shutdownTimerID = 0		# 用于记录当前是否已处于shutdown过程中，以避免重复执行
		# 运行状态：
		#   0 正常运行，
		#   1 处于踢人状态中，
		#   2 处于保存服务其它数据状态中，
		#   3 处于数据处理完毕，准备关闭服务器的状态中，
		#   4 应该可以关闭服务器了
		self.runState = 0

		# RelationMgr给本baseApp分配的uid列表，当剩余uid少于10个时，需向RelationMgr重新申请100个uid
		# 新的uid列表申请需要一个tick的时间，在一个tick之内有大于10个玩家的结为关系的请求，那么会做一个延时处理，例如会执行0.1秒后的一个timer
		self.maxRelationUID = 0
		self.currentRelationUID = 0

		# 账号列表。用以搜索当前登录的账号,在元宝充值部分适用。
		self._localAccounts = {}

	def registerCallback( self, status ):
		if not status:
			raise "I can't register %s into BigWorld.globalBases." % self.globalName

		BigWorld.globalData[ self.globalName ] = self		# 同时注册到BigWorld.globalData中
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ] = self			# 注册一个没 BaseappEntity，cell 用它来给非角色 entity 广播消息
															# 注意：这样写没错，globalData 中只有随便一个 BaseappEntity 即可
															# 因此不怕冲掉 hyw--2009.06.30
		# 轮循一次BigWorld.globalBases以查找所有的同类数据
		for k, v in BigWorld.globalBases.items():
			if not isinstance( k, str ) or not k.startswith( csconst.C_PREFIX_GBAE ):
				continue
			self.globalData[k] = v					# 自身内部引用
			v.addRef( self.globalName, self )		# 通知其它baseapp entity引用自已

		# 15:11 2009-10-8，wsf
		# 申请玩家关系UID资源，如果RelationMgr还没注册好，
		# 那么在RelationMgr注册好时会主动把UID资源发送过来。
		try:
			BigWorld.globalBases["RelationMgr"].requestRelationUID( self )
		except KeyError:
			INFO_MSG( "RelationMgr has not been ready yet." )

	def addRef( self, globalName, baseMailbox ):
		"""
		defined method.
		通知加入引用

		@param globalName: 全局base标识名
		@type  globalName: STRING
		@param baseMailbox: 被引用者的mailbox
		@type  baseMailbox: MAILBOX
		@return: 一个声明了的方法，没有返回值
		"""
		self.globalData[globalName] = baseMailbox

	def removeRef( self, globalName ):
		"""
		defined method.
		通知删除引用

		@param baseMailbox: 被引用者的mailbox
		@type  baseMailbox: MAILBOX
		@return: 一个声明了的方法，没有返回值
		"""
		try:
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ] = self				# globalData 中保存的是挂掉的 base，则重新设置
																	# globalData[C_PREFIX_GBAE] (hyw--2009.06.30)
			del self.globalData[globalName]
		except KeyError:
			WARNING_MSG( "no global base entity %s." % globalName )
			pass

	def loginAttemperTrigger( self ):
		"""
		Define method.
		登录调度状态改变了
		"""
		loginAttemper.loginAttemperTrigger()

	def getBaseAppCount( self ):
		"""
		获得游戏当前的baseApp个数
		"""
		return len( self.globalData )

	def getPlayerCount( self ):
		"""
		获得当前baseApp游戏中的玩家个数
		"""
		return len( self._localPlayers )

	# -----------------------------------------------------------------
	# 在线玩家登录相关
	# -----------------------------------------------------------------
	def registerPlayer( self, entity ):
		"""
		登记一个玩家的entity，所有被登记的玩家都被认为是在线的
		"""
		self._localPlayers[entity.getName()] = entity
		
		camp = entity.getCamp()
		if self._localCampPlayers.has_key( camp ):
			self._localCampPlayers[ camp ].append( entity )
		else:
			self._localCampPlayers[ camp ] = [ entity ]
			
		BigWorld.baseAppData[ loginAttemper.playerCountKey ] += 1

	def deregisterPlayer( self, entity ):
		"""
		取消对一个玩家entity的登记
		"""
		del self._localPlayers[entity.getName()]
		camp = entity.getCamp()
		for index, e in enumerate( self._localCampPlayers[ camp ] ):
			if e.id == entity.id:
				del self._localCampPlayers[ camp ][ index ]
				break
				
		BigWorld.baseAppData[ loginAttemper.playerCountKey ] -= 1
		loginAttemper.loginAttemperTrigger()
		

	def iterOnlinePlayers( self ):
		"""
		获取一个在线玩家的iterator

		@return: iterator
		"""
		return self._localPlayers.itervalues()

	# -----------------------------------------------------------------
	# 聊天消息广播相关
	# -----------------------------------------------------------------
	def _localBroadcast( self, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		广播玩家的发言内容到当前BaseApp的所有 client
		@param				chid	: 广播频道 ID
		@type				chid	: INT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: 发言者 entityID
		@param				spkName : 源说话者名字
		@type				spkName : STRING
		@param				msg		: 消息内容
		@type				msg		: STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		@return						: 一个声明了的方法，没有返回值
		"""
		for e in self._localPlayers.itervalues():							# 广播给每个在线的 client
			# 防止某个baseApp崩掉后广播消息失败，出现异常
			try:
				e.client.chat_onChannelMessage( chid, spkID, spkName, msg, blobArgs )
			except:
				EXCEHOOK_MSG( "check role's validity error" )

	def globalChat( self, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		广播玩家的发言内容到所有的BaseApp( 通知每个baseApp, 包括自己 )
		@param				chid	: 广播频道 ID
		@type				chid	: UINT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: 发言者 entityID
		@param				spkName : 源说话者名字
		@type				spkName : STRING
		@param				msg		: 消息内容
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		@type				msg		: STRING
		@return						: 一个声明了的方法，没有返回值
		"""
		for e in self.globalData.itervalues():
			e._localBroadcast( chid, spkID, spkName, msg, blobArgs )
	
	def campChat( self, campID, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		阵营发言
		@param				campID	: 阵营ID
		@type				chid	: UINT8
		@param				chid	: 广播频道 ID
		@type				chid	: UINT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: 发言者 entityID
		@param				spkName : 源说话者名字
		@type				spkName : STRING
		@param				msg		: 消息内容
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		@type				msg		: STRING
		@return						: 一个声明了的方法，没有返回值
		"""
		for e in self.globalData.itervalues():
			e.campChatLocal( campID, chid, spkID, spkName, msg, blobArgs )
	
	def campChatLocal( self, campID, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		广播玩家的发言内容到当前同阵营BaseApp的所有 client
		@param				chid	: 广播频道 ID
		@type				chid	: INT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: 发言者 entityID
		@param				spkName : 源说话者名字
		@type				spkName : STRING
		@param				msg		: 消息内容
		@type				msg		: STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		@return						: 一个声明了的方法，没有返回值
		"""
		chatList = self._localCampPlayers.get( campID, [] )
		for e in chatList:
			try:
				e.client.chat_onChannelMessage( chid, spkID, spkName, msg, blobArgs )
			except:
				EXCEHOOK_MSG( "check role's validity error" )

	def anonymityBroadcast( self, msg, blobArgs ) :
		"""
		defined method
		匿名广播
		注意：广播的频道是：csdefine.CHAT_CHANNEL_SYSBROADCAST
		hyw--2009.09.15
		@param					msg : 消息内容
		@type					msg : STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		"""
		for e in self.globalData.itervalues():
			e._localBroadcast( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, blobArgs )
			
	def campActivity_broadcast( self, msgDict, blobArgs ):
		"""
		define method
		阵营活动广播
		"""
		self.campChatLocal( csdefine.ENTITY_CAMP_TAOISM, csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msgDict.get( csdefine.ENTITY_CAMP_TAOISM ), blobArgs )
		self.campChatLocal( csdefine.ENTITY_CAMP_DEMON, csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msgDict.get( csdefine.ENTITY_CAMP_DEMON ), blobArgs )
		
	# ----------------------------------------------------------------
	# 防沉迷（hyw--2010.06.10）
	# ----------------------------------------------------------------
	def _localWallowNotify( self, accInfos ) :
		"""
		防沉迷本地服务器通知
		@type				accInfos : list
		@param				accInfos : a list of :
			{
				aname  : STRING: 账号名
				state  : MACRO DEFINATION: 收益状态，在 csdefine 中定义：WALLOW_XXX
				olTime : INT64: 在线时间
			}
		"""
		dInfos = {}
		for accInfo in accInfos :
			dInfos[accInfo['accName']] = ( accInfo["olState"], accInfo["olTime"] )
		for e in self._localPlayers.itervalues() :
			eAccount = getattr( e, "accountEntity", None )
			if not eAccount : continue
			info = dInfos.pop( eAccount.playerName, None )
			if info :
				e.wallow_onWallowNotify( *info )
			if len( dInfos ) == 0 :
				break

	def wallowNotify( self, accInfos ) :
		"""
		沉迷通知
		@type				accInfos : list
		@param				accInfos : a list of :
			{
				aname  : STRING: 账号名
				state  : MACRO DEFINATION: 收益状态，在 csdefine 中定义：WALLOW_XXX
				olTime : INT64: 在线时间
			}
		"""
		for e in self.globalData.itervalues() :
			e._localWallowNotify( accInfos )


	# ----------------------------------------------------------------
	# 远程调用封装
	# ----------------------------------------------------------------
	def globalRemoteCallClient( self, methodName ):
		"""
		调用所有玩家的client远程方法，必须是无参数的方法。16:40 2009-4-11，wsf

		@param methodName : 远程方法名
		@type methodName : STRING
		"""
		for e in self.globalData.itervalues():
			e.remoteCallPlayerClient( methodName )

	def remoteCallPlayerClient( self, methodName ):
		"""
		Define method.
		通过mailbox调用当前baseapp所有玩家的远程方法，方法不能有参数。16:51 2009-4-11，wsf

		@param methodName : 远程方法名
		@type methodName : STRING
		"""
		for e in self._localPlayers.itervalues():
			if not isinstance( e, Role ) or not hasattr( e, "client" ): continue
			try:
				method = getattr( e.client, methodName )
			except AttributeError, errstr:
				ERROR_MSG( "player's mailbox has no this attribut( %s ).%s" % ( methodName, errstr ) )
				return
			method()
	
	def globalRemoteCallCampClient( self, camp, methodName, args ):
		"""
		调用某阵营玩家的client远程方法
		
		@param camp : 阵营
		@type camp : UINT8
		@param methodName : 远程方法名
		@type methodName : STRING
		@param args :  参数
		@type args : PY_ARGS
		"""
		for e in self.globalData.itervalues():
			e.remoteCallCampPlayerClient( camp, methodName, args )
	
	def remoteCallCampPlayerClient( self, camp, methodName, args ):
		"""
		Define method.
		通过mailbox调用当前baseapp某阵营所有玩家的client远程方法，方法可以带参数。

		@param camp : 阵营
		@type camp : UINT8
		@param methodName : 远程方法名
		@type methodName : STRING
		@param args :  参数
		@type args : PY_ARGS
		"""
		for e in self._localCampPlayers.get( camp, [] ):
			if not isinstance( e, Role ) or not hasattr( e, "client" ): continue
			try:
				method = getattr( e.client, methodName )
			except AttributeError, errstr:
				ERROR_MSG( "player's mailbox has no this attribut( %s ).%s" % ( methodName, errstr ) )
				return
			method( *args )
	
	def globalRemoteCallCampCell( self, camp, methodName, args ):
		"""
		调用某阵营玩家的cell远程方法
		
		@param camp : 阵营
		@type camp : UINT8
		@param methodName : 远程方法名
		@type methodName : STRING
		@param args :  参数
		@type args : PY_ARGS
		"""
		for e in self.globalData.itervalues():
			e.remoteCallCampPlayerCell( camp, methodName, args )
	
	def remoteCallCampPlayerCell( self, camp, methodName, args ):
		"""
		Define method.
		通过mailbox调用当前baseapp某阵营所有玩家的远程cell方法，方法带参数。

		@param camp : 阵营
		@type camp : UINT8
		@param methodName : 远程方法名
		@type methodName : STRING
		@param args :  参数
		@type args : PY_ARGS
		"""
		for e in self._localCampPlayers.get( camp, [] ):
			if not isinstance( e, Role ) or not hasattr( e, "cell" ): continue
			try:
				method = getattr( e.cell, methodName )
			except AttributeError, errstr:
				ERROR_MSG( "player's mailbox has no this attribut( %s ).%s" % ( methodName, errstr ) )
				return
			method( *args )
	
	def globalCallEntityCellMothod( self, roleID, methodName, args ):
		"""
		Define mthod.
		通过玩家的ID调用指定entity的cell的方法
		@ roleID ：role id 
		@ methodName ：远程Cell方法名 STRING
		@ args ：参数 PY_DICT
		"""
		if BigWorld.entities.has_key( roleID ):
			self.remoteCallEntityCellMothod( roleID, methodName, args )
		else:
			for e in self.globalData.itervalues():
				e.remoteCallEntityCellMothod( roleID, methodName, args )
	
	def remoteCallEntityCellMothod( self, roleID, methodName, args ):
		"""
		Define mthod.
		通过mailbox调用当前某entity的cell方法
		"""
		if BigWorld.entities.has_key( roleID ):
			roleBase = BigWorld.entities[ roleID ]
			if hasattr( roleBase, "cell" ):
				if hasattr( roleBase.cell, methodName ):
					method = getattr( roleBase.cell, methodName )
					method( *args )
			else:
				INFO_MSG( "Can't find Entity by id %i, maybe it had been destroyed or in other baseapp!" % roleID )

	def queryAllPlayerAmount( self, queryerMB, params ):
		"""
		查询玩家总人数
		"""
		for e in self.globalData.itervalues():
			e.queryLocalPlayerAmount( queryerMB, params )

	def queryLocalPlayerAmount( self, queryerMB, params ):
		"""
		define method
		查询本BASSAPP人数
		"""
		queryerMB.client.onStatusMessage( csstatus.BASEAPP_ROLE_AMOUNT, str(( len(self._localPlayers), )) )


	def queryAllPlayerName( self, queryerMB, params ):
		"""
		查询玩家名字
		"""
		for e in self.globalData.itervalues():
			e.queryLocalPlayersName( queryerMB, params )

	def queryLocalPlayersName( self, queryerMB, params ):
		"""
		define method
		查询本BASSAPP玩家名字
		"""
		info = ""
		for i in self._localPlayers:
			info += i + ", "
		queryerMB.client.onStatusMessage( csstatus.BASEAPP_ROLE_NAME, str(( info, )) )


	# -----------------------------------------------------------------
	# timer
	# -----------------------------------------------------------------
	def onTimer( self, timerID, userData ):
		"""
		"""
		# 详看lookupRoleBaseByName()里调用的addTimer()
		# 处理超时的请求
		if userData == TIMER_LOOKUP_ROLE_BASE:
			time = BigWorld.time()
			for k, v in self._tmpSearchCache.items():	# 使用items()，直接复制列表，这样在循环里可以直接删除字典数据，此方法只适用于少量数据的地方
				if time >= v[1]:
					del self._tmpSearchCache[k]
					v[2]( None )

			# 如果没有其它请求了，必须停止timer
			if len( self._tmpSearchCache ) == 0:
				self.delTimer( self._searchTimerID )
				self._searchTimerID = 0
		elif userData == TIMER_SHUTDOWN_SERVER:
			self.shutdown()
		elif userData == TIMER_DELAY_SHUTDOWN:
			self.delayShutdownTimer()
		else:
			assert False, "unknow timer, timerID = %s, userData = %s" % ( timerID, userData )

	# -----------------------------------------------------------------
	# about lookupRoleBaseByName() mechanism
	# -----------------------------------------------------------------
	def lookupRoleBaseByName( self, name, callback ):
		"""
		根据名字查找在线主角的base mailbox
		@param name: string; 要查找的在线主角的名字。
		@param callback: function; 该回调函数必须有一个参数，用于给回调者提供查找到的在线主角的base mailbox，如果未找到则参数值为None。
		@return: None
		"""
		resultID = self._getLookupResultID()
		self._tmpSearchCache[resultID] = [ len( self.globalData ), BigWorld.time() + 2, callback ]	# [ 预期回复数量, 超时时间写死2秒, callback ]
		for v in self.globalData.itervalues():
			v._broadcastLookupRoleBaseByName( self, resultID, name )

		if self._searchTimerID == 0:
			self._searchTimerID = self.addTimer( 1, 1, TIMER_LOOKUP_ROLE_BASE )

	def _broadcastLookupRoleBaseByName( self, resultBase, resultID, name ):
		"""
		defined method.
		用于BaseappEntity内部调用，用于实现lookupRoleBaseByName()的回调功能

		@param resultBase: BASE MAILBOX
		@param resultID: int32
		@param name: string
		"""
		resultBase._broadcastLookupRoleBaseByNameCB( resultID, self._localPlayers.get( name ) )

	def _broadcastLookupRoleBaseByNameCB( self, resultID, baseMailbox ):
		"""
		defined method.
		用于BaseappEntity内部调用，用于实现lookupRoleBaseByName()的回调功能
		如果baseMailbox不为None，则表示找到，从_tmpSearchCache中清除，并回调；
		如果baseMailbox为None，且所有的baseapp已回复，表示没有找到，从_tmpSearchCache中清除，并回调；
		如果baseMailbox为None，且回复的baseapp还没有全部回复，baseapp的回复数减一，直接返回

		@param baseMailbox: 被找到的目标entity base mailbox
		"""
		if resultID not in self._tmpSearchCache: return		# 未找到表示已经被回复了，不再作处理
		r, time, callback = self._tmpSearchCache[resultID]
		r -= 1
		if baseMailbox is None and r > 0:	# 还有其它的未回复，改变计数器后直接返回
			self._tmpSearchCache[resultID][0] = r
			return

		del self._tmpSearchCache[resultID]
		# 如果没有其它请求了，必须停止timer
		if len( self._tmpSearchCache ) == 0:
			self.delTimer( self._searchTimerID )
			self._searchTimerID = 0

		# 回调
		callback( baseMailbox )

	def _getLookupResultID( self ):
		"""
		获得一个用于广播lookupRoleBaseByName()的唯一的id值
		@return: INT32
		"""
		self._tmpSearchCurrentID += 1
		if self._tmpSearchCurrentID >= 0x7FFFFFFF:
			self._tmpSearchCurrentID = 1

		# 循环判断并获取一个不在_tmpSearchCache中存在的ID值
		while self._tmpSearchCurrentID in self._tmpSearchCache:
			self._tmpSearchCurrentID += 1
			if self._tmpSearchCurrentID >= 0x7FFFFFFF:
				self._tmpSearchCurrentID = 1
		return self._tmpSearchCurrentID

	# --------------------------------------------------------------------------
	# 服务器关闭前做的事情
	# 之所以做这个功能是因为bigworld的服务器关闭机制还不完善，
	# 在大多数情况下都有可能导致玩家回档。
	# --------------------------------------------------------------------------
	def kickoutPlayer( self, amount ):
		"""
		目标：踢出当前baseapp所有的玩家角色及帐号。

		@param amount: 期望最多处理多少个，达到这个数量则不再处理。
		@return: 返回实际处理的entity的数量
		"""
		INFO_MSG( "%s: begin kickout player. target amount = %i." % ( self.globalName, amount ) )
		i = 0
		for e in BigWorld.entities.values():
			if e.isDestroyed:
				continue
			name = e.__class__.__name__
			if name == "Role":
				# 这里只处理Role entity
				try:
					e.logoff()
				except:
					# 仅仅写个日志，不做任何处理
					EXCEHOOK_MSG( "kickout role error" )
			elif name == "Account" and e.avatar is None:
				# 上面的not e.isDestroyed必须判断，因为如果Role只有base时会直接把它的Account也destroy()，
				# 这时再调用则会出ValueError的异常。
				# 因为上面的BigWorld.entities.values()已经把这个被中途destroyed的entity引用了。

				# 这里只处理avatar属性为None的Account entity，
				# 对于avatar不为None的Account entity会由Role entity触发退出行为
				try:
					e.logoff()
				except:
					# 仅仅写个日志，不做任何处理
					EXCEHOOK_MSG( "kickout account error" )
			else:
				continue

			i += 1
			# 每次最多关闭踢出一定量的角色，以避免负载过高而被强行kill掉
			if i >= amount: break
		return i

	def saveManagersBeforeShutdown( self ):
		"""
		在shutdown当前baseapp之前处理那些需要存储到数据的管理器。
		"""
		INFO_MSG( "%s: save other datas before shutdown" % self.globalName )
		# 在server停机之前保存道具商城数据
		if BigWorld.globalBases.has_key( "SpecialShopMgr" ):
			entity = BigWorld.entities.get( BigWorld.globalBases[ "SpecialShopMgr" ].id )
			entity and entity.save()

		# 这里可以加入更多的关机前处理
		if BigWorld.globalData.has_key( "TongManager" ):
			BigWorld.globalData[ "TongManager" ].save()

	def shutdown( self ):
		"""
		defined method.
		关闭服务器的前置函数，清除当前baseapp进程的所有角色和其它需要写入数据库的数据。
		此函数会在关闭服务器前由外面的工具调用。一般被shutdownAll()调用
		此接口处理以下行为：
		1.踢出本baseapp所有登录的玩家；
		2.处理所有本baseapp的其它需要储存的数据及entity处理。
		"""
		# 如果没有起动timer则起动一个，一次踢一点
		# 注意：addTimer()里的间隔不能太短，否则会
		# 出现一个角色或帐号被踢多次的问题。
		# 如果run state不为0，那表示当前服务器已处于被关闭状态，
		# 不应该继续处理了。
		if self._shutdownTimerID == 0 and self.runState == 0:
			# timer的间隔不宜太小，太小会引起重复logout entity的问题。
			self._shutdownTimerID = self.addTimer( 0.5, 0.5, TIMER_SHUTDOWN_SERVER )
			INFO_MSG( "%s: shutdown server now." % self.globalName )
			self.runState = 1

		if self.runState == 1:		# 处于踢玩家状态
			# 一次只踢一定数量的人，以避免因数据风暴引起的高消耗，从而导致服务器被强行kill掉。
			# 如果本次踢出的人少于一定量，则表示本baseapp已无玩家，因此要开始执行下一步聚。
			if self.kickoutPlayer( 50 ) < 50:
				self.runState = 2
				INFO_MSG( "%s: kickout player over." % self.globalName )

		elif self.runState == 2:	# 处于处理其它需要储存的数据状态
			self.saveManagersBeforeShutdown()

			# 虽然当前我们一次性清除所有其它需要储存的数据，
			# 但是我们仍然会等待一次timer的触发，
			# 以确保需要写入数据库的数据全部被写入。
			self.runState = 3
		elif self.runState == 3:
			self.runState = 4
			self.delTimer( self._shutdownTimerID )
			self._shutdownTimerID = 0

			# 向防沉迷后台发送服务器关闭信息（2010.06.09－－hyw）
			if BigWorld.globalBases.has_key( "AntiWallowBridge" ) :
				BigWorld.globalBases["AntiWallowBridge"].onServerShutdown()

			INFO_MSG( "%s: server was shutdown." % self.globalName )
		else:
			assert False, "Here has bug. shutdownTimerID = %i, run state = %i." % ( self._shutdownTimerID, self.runState )

	def shutdownAll( self, delay ):
		"""
		defined method.
		关闭服务器的前置函数，清除当前baseapp进程的所有角色和其它需要写入数据库的数据。
		此函数会在关闭服务器前由外面的工具调用，或者被GM指令调用。
		（如：bigworld/tools/server/runscript）。此接口处理以下行为：

		1.踢出所有登录的玩家；
		2.所有其它需要储存的数据及entity处理。

		@param delay: 延时多长时间后关闭；0 == 立即关闭
		"""
		if delay <= 0:
			INFO_MSG( "%s: shutdown all server now." % self.globalName )
			for e in self.globalData.itervalues():
				e.shutdown()
		else:
			self.delayShutdownTimer = ShutdownTimer( self, delay )

	# ----------------------------------------------------------------
	# 系统远程给一个目标施放某个技能
	# ----------------------------------------------------------------
	def castSpellBroadcast( self, targetEntityID, skillID ) :
		"""
		defined method.
		@param	targetEntityID		: entity 的id
		@type	targetEntityID		: int32
		@param	skillID				: 技能ID
		@type	skillID				: int64
		@return			None
		"""
		for e in self.globalData.itervalues() :
			e.remoteCastSpell( targetEntityID, skillID )

	def remoteCastSpell( self, targetEntityID, skillID ) :
		"""
		defined method.
		添加此方法的原因：
			角色从一个地图跳到另一个地图时，系统会先把角色从当前地图销毁，如果此刻
			刚好要对该玩家施放某个技能，则cell上会出现找不到玩家的情况，而且这个技
			能通常是由系统施放的，不需要某个实在的entity（虽然实际上是从某个entity
			处触发该行为，但此类技能实际上并不需要源目标，像禁止PK技能），因此把施
			放技能的行为通过base找到技能施展目标的cell再继续施放动作。
		@param	targetEntityID		: entity 的id
		@type	targetEntityID		: int32
		@param	skillID				: 技能ID
		@type	skillID				: int64
		@return			None
		"""
		target = BigWorld.entities.get( targetEntityID, None )
		if hasattr( target, "cell" ) :
			if hasattr( target.cell, "systemCastSpell" ) :
				target.cell.systemCastSpell( skillID )
		else :
			INFO_MSG( "Can't find target by id %i, maybe it had been destroyed or in other baseapp!" % targetEntityID )

	def getRelationUID( self ):
		"""
		请求玩家关系uid
		"""
		uid = self.currentRelationUID
		if uid == self.maxRelationUID:
			uid = -1
		else:
			self.currentRelationUID += 1
		if self.maxRelationUID - self.currentRelationUID < 10:	# relationUID个数小于10时向uidFactory申请新的uid资源
			BigWorld.globalBases["RelationMgr"].requestRelationUID( self )
		return uid

	def receiveRelationUID( self, startUID ):
		"""
		Define method.
		接收玩家关系uid

		uid开始的编号，往后Const.RELATION_UID_SAND_MAX_COUNT个
		"""
		self.currentRelationUID = startUID
		self.maxRelationUID = startUID + Const.RELATION_UID_SAND_MAX_COUNT

	# ----------------------------------------------------------------
	# 在线玩家账号记录
	# ----------------------------------------------------------------
	def registerAccount( self, account ):
		"""
		登记一个激活了的账号
		"""
		self._localAccounts[account.playerName] = account


	def deregisterAccount( self, account ):
		"""
		取消对一个账号的登记
		"""
		try:
			self._localAccounts.pop(account.playerName)
		except:
			EXCEHOOK_MSG()

	def fetchGold( self, accountName ):
		"""
		领取元宝
		"""
		try:
			account = self._localAccounts[accountName]
			if not account.isDestroyed:
				if account.avatar is not None:
					account.avatar.pcu_takeThings( csconst.PCU_TAKECHARGE, 0 )
		except:
			return

	def kickoutAccount( self, accountName ):
		"""
		踢出指定账号
		"""
		try:
			account = self._localAccounts[accountName]
			if not account.isDestroyed:
				account.logoff()
		except:
			return

	def addAllBasePlayerCountLogs( self, pType, aType, action, param1, param2, param3, param4, param5 ):
		"""
		define method
		记录当前玩家数量日志。
		"""
		for e in self.globalData.itervalues():
			e.addPlayerCountLog(  pType, aType, action, param1, param2, param3, param4, param5 )
	
	
	def addPlayerCountLog( self, pType, aType, action, param1, param2, param3, param4, param5 ):
		"""
		define method
		记录当前玩家数量日志。
		"""
		try:
			g_logger.countOnlineAccountLog( len( self._localAccounts ), param1, param2, param3, param4, param5 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	# ----------------------------------------------------------------
	# 查询玩家装备
	# ----------------------------------------------------------------
	def queryRoleEquipItems( self, playerMB, queryName ):
		for e in self.globalData.itervalues():
			e.remoteQueryRoleEquipItems( playerMB, queryName )

	def remoteQueryRoleEquipItems( self, playerMB, queryName ):
		"""
		define method.
		"""
		if self._localPlayers.get( queryName ):
			self._localPlayers.get( queryName ).cell.onQueryRoleEquipItems( playerMB )

# BaseappEntity
