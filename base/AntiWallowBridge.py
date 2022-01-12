# -*- coding: gb18030 -*-

"""
防沉迷处理
2010.06.04：writen by huangyongwei
"""

"""
消息方向						事件						消息结构						说明

游戏服务器->后台程序：
								游戏服务器启动				1&游戏名&区组ID\r\n				主动发送游戏接口的ip和port
								游戏服务器关闭				2&游戏名&区组ID\r\n
								玩家登陆					3&游戏名&区组ID&账号\r\n
								玩家登出					4&游戏名&区组ID&账号\r\n

验证服务器->游戏服务器的回复包，
0&回复类型&回复数值（如果有）：
								服务器运行时消息收到回复	0&1\r\n
								服务器关机时消息收到回复	0&2\r\n
								玩家上线登录回复			0&3&0&时长\r\n					回复数值0表示1倍收益；1表示收益需要减半；2表示收益为0
								玩家离线登录回复			0&4\r\n

验证服务器->游戏服务器：
								提示在线时间				消息长度0&账号&在线时间\r\n		可以接多个账号，在线时间单位为秒
								收益减半					消息长度1&账号&在线时间\r\n		可以接多个账号，在线时间单位为秒
								收益为0						消息长度2&账号&在线时间\r\n		可以接多个账号，在线时间单位为秒

游戏服务器->验证服务器回复包：
								确认消息收到				0&1\r\n

"""

import time
import struct
import socket
import threading
import ResMgr
import BigWorld
import csdefine
import csconst
import Version
import Love3
from string import Template as STemplate
from bwdebug import *
from Function import Functor
from BackgroundTask import Manager, BackgroundTask


# -------------------------------------------
# 游戏服务器->后台：
_stpStartSvr		= STemplate( "1&${gname}&${groupid}\r\n" )			# 服务器向后台发送的启动消息
_stpShutSvr			= STemplate( "2&${gname}&${groupid}\r\n" )			# 服务器向后台发送的关闭消息
_stpLogin			= STemplate( "3&${gname}&${groupid}&${aname}\r\n" )	# 角色登录时向后台发送的消息
_stpLogout			= STemplate( "4&${gname}&${groupid}&${aname}\r\n" )	# 角色登出时向后台发送的消息

# 游戏服务器->后台的回复：
_dataConfirm		= "0&1\r\n"											# 确认收到了后台消息

# 验证服务器->游戏服务器的回复前缀：
_prefixRStart		= "0&1"												# 服务器启动回复前缀
_prefixRShut		= "0&2"												# 服务器关闭回复前缀
_prefixRLogin		= "0&3"												# 角色登录回复前缀
_prefixRLogout		= "0&4"												# 角色登出回复前缀

# -------------------------------------------
_gameName = Version.getGameName()										# 游戏名称
_BUFF_SIZE = 128														# 消息缓冲大小(肯定不会超过 512)


# --------------------------------------------------------------------
# 信息接收器
# --------------------------------------------------------------------
class _Receiver( object ) :
	def __init__( self, owner, host ) :
		assert host[1] > 1024, "port nu. must larger then 1024."
		self.__owner = owner
		self.__sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.__sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		self.__sock.bind( host )
		self.__sock.listen( 80 )
		BigWorld.registerFileDescriptor( self.__sock.fileno(), self.__onAccept )
		INFO_MSG( "start listening host: %s..." % str( host ) )

		self.__spiccatoDatas = {}					# { connect : ( 数据长度, data ) }


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __combineDatas( self, connect, segData ) :
		"""
		组合数据，如果数据接收完毕，则返回一条完整的数据，否则返回 None
		"""
		info = self.__spiccatoDatas.get( connect, None )
		if info is None :
			size = struct.unpack( "B", segData[0] )[0]
			data = segData[1:]
			if len( data ) == size :
				return data
			else :
				self.__spiccatoDatas[connect] = ( size, data )
		else :
			size, data = info
			data += segData
			if len( data ) == size :
				self.__spiccatoDatas.pop( connect )
				return data
			else :
				self.__spiccatoDatas[connect] = ( size, data )
		return None

	# -------------------------------------------------
	def __onAccept( self, fd = None ) :
		"""
		有连接请求时被调用
		"""
		connect, host = self.__sock.accept()
		func = Functor( self.__onReceive, connect, host )
		BigWorld.registerFileDescriptor( connect.fileno(), func )
		INFO_MSG( "%s connected with fd %d." % ( str( host ), connect.fileno() ) )

	def __onReceive( self, connect, host, fd = None ) :
		"""
		有数据接收时被调用
		"""
		try :
			data = connect.recv( _BUFF_SIZE )								# 如果后台服务器关闭，则会产生 socket 异常
		except socket.error, err :
			LOG_MSG( "socket error from '%s': %s!" % ( str( host ), err ) )
		else :
			if data == "" :													# 如果后台没确认回复前就关闭 socket，则会收到一个空串
				LOG_MSG( "connect is closed by '%s'!" % str( host ) )
			else :
				data = self.__combineDatas( connect, data )
				if data :
					connect.send( _dataConfirm )							# 回复确认收到
					self.__owner.onNotify( data )
				else :
					return													# 还没接收完毕，返回等待下次接收
		BigWorld.deregisterFileDescriptor( connect.fileno() )
		connect.close()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def close( self ) :
		"""
		关闭连接监听
		"""
		BigWorld.deregisterFileDescriptor( self.__sock.fileno() )
		self.__sock.close()


# --------------------------------------------------------------------
# 信息发送器
# --------------------------------------------------------------------
class _SendConnector( BackgroundTask ) :
	def __init__( self, owner, host, id, data ) :
		self.__owner = owner
		self.__host = host
		self.__id = id
		self.__data = data

	def __onReceive( self, sock, fd = None ) :
		try :
			data = sock.recv( _BUFF_SIZE )
		except Exception, err :													# 接收数据失败
			self.__owner.sendData( self.__id, self.__data )						# 重新放入任务列表，等待下一次发送
			LOG_MSG( "receive data from anti-walow server '%s' failed:\n%s " \
				% ( str( self.__host ), err ) )
		else :
			if data == "" :														# 如果后台主动关闭连接，则会收到空一个空串
				LOG_MSG( "connect is closed by '%s'!" % str( self.__host ) )
			else :
				self.__owner.onRespond( self.__id, data[:-2] )					# 去掉后面的“\r\n”
		BigWorld.deregisterFileDescriptor( sock.fileno() )
		sock.close()

	def doBackgroundTask( self, bgTaskMgr ) :
		try :
			sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
			sock.settimeout( 2.0 )
			sock.connect( self.__host )
		except socket.error, err :
			sock.close()
			if type( err.args ) is tuple and err.args[0] == 111 :			# 如果因为连接繁忙而被拒绝
				time.sleep( 5.0 )
				self.__owner.sendData( self.__id, self.__data )				# 则，稍候将发送请求重新放入任务队列
			else :
				LOG_MSG( "connect to anti-walow server '%s' failed:\n%s " \
					% ( str( self.__host ), err ) )
		else :
			# 下面的代码有以下隐患：
			# 1.如果socket的缓冲区满了，则send()会阻塞，直接至少写入一个字节为止；
			# 2.send()写入的数据（返回值）不一定等于len( _dataConfirm )，也许会少于这个数量；
			# 至于不做处理的原因，我们认为新的socket的写缓冲总是空的，而且我们写入的数据量很少，
			# 理论上不应该会产生上面所说的问题，但仍然写出来，是为了让将来有问题时借鉴。
			sock.send( self.__data )
			func = Functor( self.__onReceive, sock )
			BigWorld.registerFileDescriptor( sock.fileno(), func )


# --------------------------------------------------------------------
class _Sender( object ) :
	def __init__( self, owner, host ) :
		assert host[1] > 1024, "port nu. must larger then 1024."
		self.__owner = owner
		self.__host = host
		self.__taskMgr = Manager()
		self.__taskMgr.startThreads( 3 )					# 开启三个线程处理数据发送


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRespond( self, id, data ) :
		"""
		接收回复消息响应
		"""
		self.__owner.onRespond( id, data )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def sendData( self, id, data ) :
		"""
		添加要发送的数据
		"""
		connector = _SendConnector( self, self.__host, id, data )
		self.__taskMgr.addBackgroundTask( connector )

	def close( self ) :
		"""
		关闭线程
		"""
		self.__taskMgr.stopAll()


# --------------------------------------------------------------------
# 防沉迷
# --------------------------------------------------------------------
class AntiWallowBridge( BigWorld.Base ) :
	def __init__( self ) :
		BigWorld.Base.__init__( self )
		self.registerGlobally( "AntiWallowBridge", self.__onRegisterGlobal )
		self.__running = False										# 标记服务器是否在运行中
		self.__receiver = None
		self.__sender = None
		self.__isBgServicing = False								# 后台服务器是否处于服务状态

		self.__sendIDs = []											# 消息发送序列号
		self.__marks = {}											# 消息发送标记
		self.__opResponds = {										# 后台返回处的理方法
			_prefixRStart		: self.__respondStartServer,		# 服务器启动返回
			_prefixRShut		: self.__respondShutdownServer,		# 服务器关闭返回
			_prefixRLogin		: self.__respondLogin,				# 角色登录返回
			_prefixRLogout		: self.__respondLogout,				# 角色登出返回
			}														# 注意：这里产生了交叉引用，但因为该 entity 常驻内存，因此这里没问题。（仿此用法请谨慎）

		sect = ResMgr.openSection( "server/bw.xml" )
		strHost = sect["baseApp"]["antiWallowBridgeSVHost"].asString
		if strHost != "" :
			addr, port = strHost.split( ":" )
			self.__svrHost = addr, int( port )
			self.__receiver = _Receiver( self, self.__svrHost )

		strHost = sect["baseApp"]["antiWallowBridgeCLHost"].asString
		if strHost != "" :
			addr, port = strHost.split( ":" )
			host = addr, int( port )
			self.__sender = _Sender( self, host )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onRegisterGlobal( self, success ) :
		"""
		注册回调
		"""
		if not success :
			self.registerGlobally( "AntiWallowBridge", self.__onRegisterGlobal )
		else :
			BigWorld.globalData["AntiWallow_isApply"] = \
				self.__receiver and self.__sender					# 是否启用防沉迷系统（给调试用，如果 bw.xml 中不设置主机，则该值为 False）
			self.onServerStart()									# 通知后台游戏服务器启动
			INFO_MSG( "anti-wallow server register success!" )

	def __stopWorking( self ) :
		"""
		defined
		停止监听
		"""
		if self.__receiver :
			self.__receiver.close()
		if self.__sender :
			self.__sender.close()
			self.__isBgServicing = False

	# -------------------------------------------------
	def __genRequestID( self, mark ) :
		"""
		产生一个请求 id
		"""
		index = 0
		while True :
			if index not in self.__sendIDs :
				self.__sendIDs.append( index )
				self.__marks[index] = mark
				return index
			index += 1

	def __sendData( self, data, mark = None ) :
		"""
		发送数据
		"""
		if self.__isBgServicing :
			id = self.__genRequestID( mark )
			self.__sender.sendData( id, data )
		else :
			LOG_MSG( "anti-wallow server is not running! it must be running before game server start!" )

	# -------------------------------------------------
	def __respondStartServer( self, mark, text ) :
		"""
		游戏启动通知后台后，后台返回的回复
		"""
		self.__isBgServicing = True
		INFO_MSG( "start server ok..." )

	def __respondShutdownServer( self, mark, text ) :
		"""
		游戏关闭通知后台后，后台返回的回复
		"""
		INFO_MSG( "shutdown server ok..." )

	def __respondLogin( self, accName, text ) :
		"""
		角色登录通知后台后，后台返回的回复
		"""
		segs = text.split( "&" )
		olState = int( segs[1] )
		olTime = int( segs[2] )
		INFO_MSG( "'%s' login ok: %i, %i" % ( accName, olState, olTime ) )
		if olState not in csconst.WALLOW_STATES :
			raise TypeError( "error lucre state %i receive from anti-wallow server!" % olState )
		else :
			INFO_MSG( "receive lucre state %i from anti-wallow server!" % olState )
			accInfo = { "accName" : accName, "olState" : olState, "olTime" : olTime }
			Love3.g_baseApp.wallowNotify( [accInfo] )

	def __respondLogout( self, accName, text ) :
		"""
		角色登出通知后台后，后台返回的回复
		"""
		INFO_MSG( "'%s' logout ok..." % accName )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onNotify( self, data ) :
		"""
		收到被动连接消息时被调用
		"""
		if not self.__isBgServicing :
			LOG_MSG( "receive notify message from anti-wallow server: '%s', but it is not effective.\n" + \
				"anti-wallow server must be running before game server start!" )
			return
		accountDatas = data.split( "\r\n" )
		accInfos = []
		for aData in accountDatas :
			segs = aData.split( "&" )
			olState = int( segs[0] )
			accName = segs[1]
			olTime = int( segs[2] )
			if olState not in csconst.WALLOW_STATES :
				ERROR_MSG( "error lucre %i state receive from anti-wallow server!" % olState )
			else :
				accInfo = { "accName" : accName, "olState" : olState, "olTime" : olTime }
				accInfos.append( accInfo )
				INFO_MSG( "receive lucre state %i of account '%s' from anti-wallow server!" % ( olState, accName ) )
		Love3.g_baseApp.wallowNotify( accInfos )

	def onRespond( self, id, data ) :
		"""
		收到主动连接的回复时被调用
		"""
		self.__sendIDs.remove( id )
		mark = self.__marks.pop( id )
		for prefix, resp in self.__opResponds.iteritems() :
			if data.startswith( prefix ) :
				resp( mark, data[len( prefix ):] )
				return
		ERROR_MSG( "wrong data: %r respond from anti-wallow server!" % data )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onServerStart( self ) :
		"""
		defined.
		游戏服务器启动时调用
		"""
		if self.__running :
			return
		if self.__receiver is None :
			return

		d = {
			"gname" : _gameName,
			"groupid" : BigWorld.globalData["serverID"] if BigWorld.globalData.has_key( "serverID" ) else "??",
			"ip"	: self.__svrHost[0],
			"port"	: self.__svrHost[1],
			}
		data = _stpStartSvr.substitute( d )
		id = self.__genRequestID( None )
		self.__sender.sendData( id, data )
		self.__running = True

	def onServerShutdown( self ) :
		"""
		defined.
		关闭游戏服务器
		"""
		if not self.__running :						# 防止多个 base app 关闭时
			return									# 向后台发送多次关闭消息

		d = {
			"gname" : _gameName,
			"groupid" : BigWorld.globalData["serverID"] if BigWorld.globalData.has_key( "serverID" ) else "??",
			}
		data = _stpShutSvr.substitute( d )
		self.__sendData( data )
		self.__stopWorking()
		self.__running = False

	def onAccountLogin( self, accName ) :
		"""
		defined.
		角色登录通知
		"""
		d = {
			"gname" : _gameName,
			"groupid" : BigWorld.globalData["serverID"] if BigWorld.globalData.has_key( "serverID" ) else "??",
			"aname" : accName,
			}
		data = _stpLogin.substitute( d )
		self.__sendData( data, accName )

	def onAccountLogout( self, accName ) :
		"""
		defined.
		角色登出通知
		"""
		d = {
			"gname" : _gameName,
			"groupid" : BigWorld.globalData["serverID"] if BigWorld.globalData.has_key( "serverID" ) else "??",
			"aname" : accName,
			}
		data = _stpLogout.substitute( d )
		self.__sendData( data, accName )
