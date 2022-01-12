# -*- coding: gb18030 -*-

"""
�����Դ���
2010.06.04��writen by huangyongwei
"""

"""
��Ϣ����						�¼�						��Ϣ�ṹ						˵��

��Ϸ������->��̨����
								��Ϸ����������				1&��Ϸ��&����ID\r\n				����������Ϸ�ӿڵ�ip��port
								��Ϸ�������ر�				2&��Ϸ��&����ID\r\n
								��ҵ�½					3&��Ϸ��&����ID&�˺�\r\n
								��ҵǳ�					4&��Ϸ��&����ID&�˺�\r\n

��֤������->��Ϸ�������Ļظ�����
0&�ظ�����&�ظ���ֵ������У���
								����������ʱ��Ϣ�յ��ظ�	0&1\r\n
								�������ػ�ʱ��Ϣ�յ��ظ�	0&2\r\n
								������ߵ�¼�ظ�			0&3&0&ʱ��\r\n					�ظ���ֵ0��ʾ1�����棻1��ʾ������Ҫ���룻2��ʾ����Ϊ0
								������ߵ�¼�ظ�			0&4\r\n

��֤������->��Ϸ��������
								��ʾ����ʱ��				��Ϣ����0&�˺�&����ʱ��\r\n		���ԽӶ���˺ţ�����ʱ�䵥λΪ��
								�������					��Ϣ����1&�˺�&����ʱ��\r\n		���ԽӶ���˺ţ�����ʱ�䵥λΪ��
								����Ϊ0						��Ϣ����2&�˺�&����ʱ��\r\n		���ԽӶ���˺ţ�����ʱ�䵥λΪ��

��Ϸ������->��֤�������ظ�����
								ȷ����Ϣ�յ�				0&1\r\n

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
# ��Ϸ������->��̨��
_stpStartSvr		= STemplate( "1&${gname}&${groupid}\r\n" )			# ���������̨���͵�������Ϣ
_stpShutSvr			= STemplate( "2&${gname}&${groupid}\r\n" )			# ���������̨���͵Ĺر���Ϣ
_stpLogin			= STemplate( "3&${gname}&${groupid}&${aname}\r\n" )	# ��ɫ��¼ʱ���̨���͵���Ϣ
_stpLogout			= STemplate( "4&${gname}&${groupid}&${aname}\r\n" )	# ��ɫ�ǳ�ʱ���̨���͵���Ϣ

# ��Ϸ������->��̨�Ļظ���
_dataConfirm		= "0&1\r\n"											# ȷ���յ��˺�̨��Ϣ

# ��֤������->��Ϸ�������Ļظ�ǰ׺��
_prefixRStart		= "0&1"												# �����������ظ�ǰ׺
_prefixRShut		= "0&2"												# �������رջظ�ǰ׺
_prefixRLogin		= "0&3"												# ��ɫ��¼�ظ�ǰ׺
_prefixRLogout		= "0&4"												# ��ɫ�ǳ��ظ�ǰ׺

# -------------------------------------------
_gameName = Version.getGameName()										# ��Ϸ����
_BUFF_SIZE = 128														# ��Ϣ�����С(�϶����ᳬ�� 512)


# --------------------------------------------------------------------
# ��Ϣ������
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

		self.__spiccatoDatas = {}					# { connect : ( ���ݳ���, data ) }


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __combineDatas( self, connect, segData ) :
		"""
		������ݣ�������ݽ�����ϣ��򷵻�һ�����������ݣ����򷵻� None
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
		����������ʱ������
		"""
		connect, host = self.__sock.accept()
		func = Functor( self.__onReceive, connect, host )
		BigWorld.registerFileDescriptor( connect.fileno(), func )
		INFO_MSG( "%s connected with fd %d." % ( str( host ), connect.fileno() ) )

	def __onReceive( self, connect, host, fd = None ) :
		"""
		�����ݽ���ʱ������
		"""
		try :
			data = connect.recv( _BUFF_SIZE )								# �����̨�������رգ������� socket �쳣
		except socket.error, err :
			LOG_MSG( "socket error from '%s': %s!" % ( str( host ), err ) )
		else :
			if data == "" :													# �����̨ûȷ�ϻظ�ǰ�͹ر� socket������յ�һ���մ�
				LOG_MSG( "connect is closed by '%s'!" % str( host ) )
			else :
				data = self.__combineDatas( connect, data )
				if data :
					connect.send( _dataConfirm )							# �ظ�ȷ���յ�
					self.__owner.onNotify( data )
				else :
					return													# ��û������ϣ����صȴ��´ν���
		BigWorld.deregisterFileDescriptor( connect.fileno() )
		connect.close()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def close( self ) :
		"""
		�ر����Ӽ���
		"""
		BigWorld.deregisterFileDescriptor( self.__sock.fileno() )
		self.__sock.close()


# --------------------------------------------------------------------
# ��Ϣ������
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
		except Exception, err :													# ��������ʧ��
			self.__owner.sendData( self.__id, self.__data )						# ���·��������б��ȴ���һ�η���
			LOG_MSG( "receive data from anti-walow server '%s' failed:\n%s " \
				% ( str( self.__host ), err ) )
		else :
			if data == "" :														# �����̨�����ر����ӣ�����յ���һ���մ�
				LOG_MSG( "connect is closed by '%s'!" % str( self.__host ) )
			else :
				self.__owner.onRespond( self.__id, data[:-2] )					# ȥ������ġ�\r\n��
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
			if type( err.args ) is tuple and err.args[0] == 111 :			# �����Ϊ���ӷ�æ�����ܾ�
				time.sleep( 5.0 )
				self.__owner.sendData( self.__id, self.__data )				# ���Ժ򽫷����������·����������
			else :
				LOG_MSG( "connect to anti-walow server '%s' failed:\n%s " \
					% ( str( self.__host ), err ) )
		else :
			# ����Ĵ���������������
			# 1.���socket�Ļ��������ˣ���send()��������ֱ������д��һ���ֽ�Ϊֹ��
			# 2.send()д������ݣ�����ֵ����һ������len( _dataConfirm )��Ҳ����������������
			# ���ڲ��������ԭ��������Ϊ�µ�socket��д�������ǿյģ���������д������������٣�
			# �����ϲ�Ӧ�û����������˵�����⣬����Ȼд��������Ϊ���ý���������ʱ�����
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
		self.__taskMgr.startThreads( 3 )					# ���������̴߳������ݷ���


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRespond( self, id, data ) :
		"""
		���ջظ���Ϣ��Ӧ
		"""
		self.__owner.onRespond( id, data )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def sendData( self, id, data ) :
		"""
		���Ҫ���͵�����
		"""
		connector = _SendConnector( self, self.__host, id, data )
		self.__taskMgr.addBackgroundTask( connector )

	def close( self ) :
		"""
		�ر��߳�
		"""
		self.__taskMgr.stopAll()


# --------------------------------------------------------------------
# ������
# --------------------------------------------------------------------
class AntiWallowBridge( BigWorld.Base ) :
	def __init__( self ) :
		BigWorld.Base.__init__( self )
		self.registerGlobally( "AntiWallowBridge", self.__onRegisterGlobal )
		self.__running = False										# ��Ƿ������Ƿ���������
		self.__receiver = None
		self.__sender = None
		self.__isBgServicing = False								# ��̨�������Ƿ��ڷ���״̬

		self.__sendIDs = []											# ��Ϣ�������к�
		self.__marks = {}											# ��Ϣ���ͱ��
		self.__opResponds = {										# ��̨���ش�������
			_prefixRStart		: self.__respondStartServer,		# ��������������
			_prefixRShut		: self.__respondShutdownServer,		# �������رշ���
			_prefixRLogin		: self.__respondLogin,				# ��ɫ��¼����
			_prefixRLogout		: self.__respondLogout,				# ��ɫ�ǳ�����
			}														# ע�⣺��������˽������ã�����Ϊ�� entity ��פ�ڴ棬�������û���⡣���´��÷��������

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
		ע��ص�
		"""
		if not success :
			self.registerGlobally( "AntiWallowBridge", self.__onRegisterGlobal )
		else :
			BigWorld.globalData["AntiWallow_isApply"] = \
				self.__receiver and self.__sender					# �Ƿ����÷�����ϵͳ���������ã���� bw.xml �в��������������ֵΪ False��
			self.onServerStart()									# ֪ͨ��̨��Ϸ����������
			INFO_MSG( "anti-wallow server register success!" )

	def __stopWorking( self ) :
		"""
		defined
		ֹͣ����
		"""
		if self.__receiver :
			self.__receiver.close()
		if self.__sender :
			self.__sender.close()
			self.__isBgServicing = False

	# -------------------------------------------------
	def __genRequestID( self, mark ) :
		"""
		����һ������ id
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
		��������
		"""
		if self.__isBgServicing :
			id = self.__genRequestID( mark )
			self.__sender.sendData( id, data )
		else :
			LOG_MSG( "anti-wallow server is not running! it must be running before game server start!" )

	# -------------------------------------------------
	def __respondStartServer( self, mark, text ) :
		"""
		��Ϸ����֪ͨ��̨�󣬺�̨���صĻظ�
		"""
		self.__isBgServicing = True
		INFO_MSG( "start server ok..." )

	def __respondShutdownServer( self, mark, text ) :
		"""
		��Ϸ�ر�֪ͨ��̨�󣬺�̨���صĻظ�
		"""
		INFO_MSG( "shutdown server ok..." )

	def __respondLogin( self, accName, text ) :
		"""
		��ɫ��¼֪ͨ��̨�󣬺�̨���صĻظ�
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
		��ɫ�ǳ�֪ͨ��̨�󣬺�̨���صĻظ�
		"""
		INFO_MSG( "'%s' logout ok..." % accName )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onNotify( self, data ) :
		"""
		�յ�����������Ϣʱ������
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
		�յ��������ӵĻظ�ʱ������
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
		��Ϸ����������ʱ����
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
		�ر���Ϸ������
		"""
		if not self.__running :						# ��ֹ��� base app �ر�ʱ
			return									# ���̨���Ͷ�ιر���Ϣ

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
		��ɫ��¼֪ͨ
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
		��ɫ�ǳ�֪ͨ
		"""
		d = {
			"gname" : _gameName,
			"groupid" : BigWorld.globalData["serverID"] if BigWorld.globalData.has_key( "serverID" ) else "??",
			"aname" : accName,
			}
		data = _stpLogout.substitute( d )
		self.__sendData( data, accName )
