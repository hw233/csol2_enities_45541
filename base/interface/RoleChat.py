# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.25 2008-08-30 09:02:16 huangyongwei Exp $
"""

09/05/2005 : created by phw
11/28/2006 : modified by huangyongwei
"""

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import ECBExtend
import Love3
import csdefine
import csconst
import csstatus
import Const
import time
import random
from bwdebug import *
from Function import Functor
import struct
import PLMChatRecorder


# --------------------------------------------------------------------
# imolement channels
# ���˼�룺
#	�� Ƶ������һ�� exposed ���ԣ����Ա�ʾ��Ƶ���Ƿ�����ͻ���ֱ�ӵ���
#	   chat_sendMessage ����������Ϣ���Ӷ���ֹ���ͻ��˲�������ڲ�����
#	   ��Ƶ������㷢����Ϣ��
#	�� Ƶ������һ�� isLimitByGBTime ���ԣ���ʾ��Ƶ���Ƿ��ܵ�ȫ�ַ���ʱ
#	   ������ƣ����������Ƶ�Ƶ����ֻҪ������һ��Ƶ���з���һ����Ϣ����
#	   ���¼�µ�ǰʱ�䣬���ʱ������û��������һ������Ƶ���з�����Ϣ
#	   ��ʱ���ᱻ�ܾ���
#	�� Ƶ������һ�� validate ��֤����������Ƶ���������ظ÷�����ʵ���Լ�
#	   ����Լ��
#	�� Ƶ������һ�� handle ��Ϣ���������÷�����Ҫ���� base ����� cell
#	   ���͵���Ϣ����Ϊ base �� cell ���͵���Ϣ���ǳ���Ա�ƶ��ģ������
#	   ���ܵ�����Լ�Ƚ��٣���������Ϣת�������Եö�������
#	�� Ƶ������һ�� send ��Ϣ���������÷�����Ҫ�����ɫ�ͻ��˷�������
#	   ��Ϣ��������Ĵ���Ƚ��Ͻ���
# --------------------------------------------------------------------
class Channel( object ) :
	"""
	Ƶ���ӿ�
	"""
	def __init__( self, id ) :
		self.id = id											# Ƶ�� ID
		self.exposed = id in csconst.CHAT_EXPOSED_CHANNELS		# ��Ƶ���Ƿ���Ա��ͻ���ֱ�ӷ���( �� cell ���õ�Ƶ������ exposed )
		self.isLimitByGBTime = self.exposed and \
			id in _limitByGBTimeChannels						# �Ƿ���ȫ��ʱ��������

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def validate( self, speaker, rcvName, msg ) :
		"""
		��Ϣ��֤
		"""
		if len( msg ) > csconst.CHAT_MESSAGE_UPPER_LIMIT :		# �������ݹ���
			speaker.statusMessage( csstatus.CHAT_WORDS_TOO_LONG )
			return False
		return True

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� base / cell ���͹�������Ϣ
		"""
		pass																			# Ĭ�ϲ�������

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		if hasattr( speaker, "cell" ) :
			speaker.cell.chat_handleMessage( self.id, rcvName, msg, blobArgs )			# Ĭ�ϴ��� cell ����
		else :
			WARNING_MSG( "cell of '%s' is not ready or has been died!" % str( speaker ) )

# -----------------------------------------------------
class CHN_Local( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� base / cell ���͹�������Ϣ
		"""
		pass

# -------------------------------------------
class CHN_Team( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		if not speaker.getTeamMailbox() :
			speaker.statusMessage( csstatus.CHAT_NOT_IN_TEAM )
		else :
			speaker.teamChat( msg, blobArgs )

# -------------------------------------------
class CHN_Tong( Channel ) :
	"""
	���
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		if not speaker.isJoinTong():
			speaker.statusMessage( csstatus.CHAT_NOT_IN_TONG )
		else :
			speaker.sendMessage2Tong( speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_Whisper( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	# ---------------------------------------
	# private
	# ---------------------------------------
	def __onReceiverFinded( self, speaker, rcvName, msg, blobArgs, receiver ) :
		"""
		ע��
			receiver == BASE MAILBOX ���ҵ�Ŀ����������
			receiver == True		 ���ҵ�Ŀ�굫δ����
			receiver == False		 ������ԭ�����޴˽�ɫ�ȣ�
		"""
		if not isinstance( receiver, bool ) :
			receiver.client.chat_onChannelMessage( self.id, speaker.id, speaker.playerName, msg, blobArgs )
			speaker.client.chat_onChannelMessage( self.id, speaker.id, rcvName, msg, blobArgs )
		elif receiver :
			speaker.statusMessage( csstatus.CHAT_WHISPER_NOT_ON_LINE, rcvName )
		else :
			speaker.statusMessage( csstatus.CHAT_WHISPER_NOT_EXIST, rcvName )

	# ---------------------------------------
	# public
	# ---------------------------------------
	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		if speaker.playerName == rcvName :
			speaker.statusMessage( csstatus.CHAT_WHISPER_YOURSELF_REFUSED )
			return
		if speaker.meInBlacklist( rcvName ) :									# �����ɫ�ڶԷ��ĺ�������
			speaker.statusMessage( csstatus.FRIEND_ME_IN_BLACKLIST )
			return
		callback = Functor( self.__onReceiverFinded, speaker, rcvName, msg, blobArgs )
		BigWorld.lookUpBaseByName( "Role", rcvName, callback )

# -------------------------------------------
class CHN_World( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )
		self.isLimitByGBTime = False		# ����Ƶ�����Լ�����ʱ�涨

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� base / cell ���͹�������Ϣ
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_Rumor( Channel ) :
	"""
	ҥ��
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� base / cell ���͹�������Ϣ
		"""
		if random.random() >= csconst.CHAT_RUMOR_PROBABILITY :					# ��ҥ��һ������ʧ�ܣ���¶��������ݣ�
			name = speaker.playerName
		else :
			name = cschannel_msgs.ROLE_INFO_6
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_WelkinYell( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� base / cell ���͹�������Ϣ
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_TunnelYell( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� base / cell ���͹�������Ϣ
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -----------------------------------------------------
class CHN_SysBroadcast( Channel ) :
	"""
	ϵͳ�㲥
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -----------------------------------------------------
class CHN_NPCWorld( Channel ) :
	"""
	NPC ����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		Love3.g_baseApp.globalChat( self.id, speaker.id, speaker.playerName, msg, blobArgs )

# -------------------------------------------
class CHN_Playmate( Channel ) :
	"""
	�������
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	# ---------------------------------------
	# private
	# ---------------------------------------
	def __addOFLMsgCB( self, speaker, rcvName, success ) :
		"""
		������Ϣ��ӵ����ݿ�ص�
		"""
		if success :
			msg = cschannel_msgs.CHAT_FRIEND_RECEIVER_OFFLINE
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )

	def __queryAmountCB( self, speaker, rcvName, msg, blobArgs, amount ) :
		"""
		��ѯ�Ѵ�����Ϣ�����Ļص�
		"""
		if amount >= Const.CHAT_FRIEND_OFL_MSG_CAPACITY :							# ��Ϣ��������
			msg = cschannel_msgs.CHAT_FRIEND_OFFLINE_MSG_OVERFLOW
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )	# spkID ����Ϊ0�Ǳ�������ϵͳ��Ϣ
		else :
			speaker.client.chat_onChannelMessage( self.id, speaker.id, rcvName, msg, blobArgs )
			callback = Functor( self.__addOFLMsgCB, speaker, rcvName )
			date = time.strftime( "%Y%m%d%H%M%S", time.localtime() )
			PLMChatRecorder.addOFLMessage( speaker.playerName, rcvName, msg, blobArgs, date, callback )

	def __onReceiverFinded( self, speaker, rcvName, msg, blobArgs, receiver ) :
		"""
		ע��
			receiver == BASE MAILBOX ���ҵ�Ŀ����������
			receiver == True		 ���ҵ�Ŀ�굫δ����
			receiver == False		 ������ԭ�����޴˽�ɫ�ȣ�
		"""
		if not isinstance( receiver, bool ) :										# �ҵ������
			receiver.client.chat_onChannelMessage( self.id, speaker.id, speaker.playerName, msg, blobArgs )
			speaker.client.chat_onChannelMessage( self.id, speaker.id, rcvName, msg, blobArgs )
		elif receiver :																# ���������
			callback = Functor( self.__queryAmountCB, speaker, rcvName, msg, blobArgs )
			PLMChatRecorder.queryMsgsAmount( speaker.playerName, rcvName, callback )
		else :																		# ��Ҳ�����
			msg = cschannel_msgs.CHAT_FRIEND_RECEIVER_NOT_EXIST
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )

	# ---------------------------------------
	# public
	# ---------------------------------------
	def send( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		if speaker.meInBlacklist( rcvName ) :										# �����ɫ�ڶԷ��ĺ�������
			msg = cschannel_msgs.CHAT_FRIEND_IN_BLACKLIST
			speaker.client.chat_onChannelMessage( self.id, 0, rcvName, msg, [] )	# spkID ����Ϊ0��֪ͨ�ͻ�������ϵͳ��Ϣ
			return
		callback = Functor( self.__onReceiverFinded, speaker, rcvName, msg, blobArgs )
		BigWorld.lookUpBaseByName( "Role", rcvName, callback )

# -------------------------------------------
class CHN_Camp( Channel ):
	"""
	��Ӫ
	"""
	def __init__( self, id ):
		Channel.__init__( self, id )
	
	def handle( self, speaker, rcvName, msg, blobArgs ):
		"""
		���� client ���͹�����Ƶ����Ϣ
		"""
		Love3.g_baseApp.campChat( speaker.getCamp(), self.id, speaker.id, speaker.playerName, msg, blobArgs )
		
class CHN_TongCityWar( Channel ) :
	"""
	���ս������ר��Ƶ��
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		���� cell ���͹�����Ƶ����Ϣ
		"""
		pass

		
# -----------------------------------------------------
_channel_maps = { \
	# ��ɫ����Ƶ��
	csdefine.CHAT_CHANNEL_NEAR			: Channel,				# ����( ���̣�base->cell->client )
	csdefine.CHAT_CHANNEL_LOCAL			: CHN_Local,			# ����( ���̣� )
	csdefine.CHAT_CHANNEL_TEAM			: CHN_Team,				# ����( ���̣�base->base �ϵĶ���ϵͳ->��Ա client )
	csdefine.CHAT_CHANNEL_TONG			: CHN_Tong,				# ���( ���̣�base->base �ϵİ��ϵͳ->��Ա client )
	csdefine.CHAT_CHANNEL_WHISPER		: CHN_Whisper,			# ����( ���̣�base->client )
	csdefine.CHAT_CHANNEL_WORLD			: CHN_World,			# ����( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_RUMOR			: CHN_Rumor,			# ҥ��( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: CHN_WelkinYell,		# ����( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: CHN_TunnelYell,		# ����( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: CHN_TunnelYell,		# ����( ���̣�base->cell->BaseappEntity-->client )
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : CHN_TongCityWar,		# ��ս( ���̣�base-->cell��

	# GM/����Ƶ��
	csdefine.CHAT_CHANNEL_SYSBROADCAST	: CHN_SysBroadcast,		# ϵͳ�㲥( ���̣�base->BaseappEntity-->client )

	# NPC ����Ƶ��
	csdefine.CHAT_CHANNEL_NPC_SPEAK		: CHN_NPCWorld,			# NPC ����( ���̣�base->cell->BaseappEntity-->client )
	#csdefine.CHAT_CHANNEL_NPC_TALK		: Channel,				# NPC �Ի���Base �в����õ��������ͻ��˿��� statusMessage ��ʾλ�õ�Ƶ����

	# ϵͳ��ʾ
	csdefine.CHAT_CHANNEL_SYSTEM		: Channel,				# ϵͳƵ������ʾ�ɷ����������ĸ��ֻ�������Ʒ/ǿ��/��Ƕ�Ȳ�����
	#csdefine.CHAT_CHANNEL_COMBAT		: CHN_Combat,			# ս����ϢƵ����base ���ò�����
	csdefine.CHAT_CHANNEL_PERSONAL		: Channel,				# ����Ƶ������ʾ��ɫ�Ĳ��������Ĵ�����Ϣ����ʾ��Ϣ��
	csdefine.CHAT_CHANNEL_MESSAGE		: Channel,				# ��Ϣ����ʽ��Ƶ����
	csdefine.CHAT_CHANNEL_SC_HINT		: Channel,				# ����Ļ�м���ʾ��Ϣ��Ƶ����û�й̶����壩
	csdefine.CHAT_CHANNEL_MSGBOX		: Channel,				# ����ʾ����ʾ��Ϣ��Ƶ����û�й̶����壩

	# �������
	csdefine.CHAT_CHANNEL_PLAYMATE		: CHN_Playmate,			# �������
	
	# ��Ӫ
	csdefine.CHAT_CHANNEL_CAMP		:CHN_Camp,
	}

# -------------------------------------------
_limitByGBTimeChannels = set( [									# ��ȫ��ʱ�������Ƶ�Ƶ��
	csdefine.CHAT_CHANNEL_LOCAL,								# ����
	csdefine.CHAT_CHANNEL_TEAM,									# ����
	csdefine.CHAT_CHANNEL_TONG,									# ���
	csdefine.CHAT_CHANNEL_WHISPER,								# ����
	csdefine.CHAT_CHANNEL_PLAYMATE,								# ���
	] )

_channels = {}													# Ƶ���б�
for chid, CLSChannel in _channel_maps.iteritems() :
	_channels[chid] = CLSChannel( chid )
del _channel_maps


# --------------------------------------------------------------------
# chating system ( inherited by Role )
# rewriten by hyw--2009.08.13
# �ر�ע�⣺
#	�����Ƶ�������н�ɫ���õģ��벻Ҫ��Ƶ���ж����ɫ��صĳ�Ա����
# --------------------------------------------------------------------
class RoleChat :
	def __init__( self ) :
		self.__lastMsgTime = 0					# �ϴη��Ե�ʱ��
		self.__lasMsg = ""						# ��һ�η�����Ϣ
		self.__repeatCount = 0					# �ظ��������
		self.__tmpOflMsgs = []					# ���͸��ҵ�������Ϣ����ʱ������

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __validate( self, channel, rcvName, msg ) :
		"""
		�����Ϣ����Ч��
		ע������������Ŀ���ǣ�ʹ������ֻ����ɫ������ص���Ч�ԣ�Ƶ����ص���Ч����Ƶ�����Դ���
		"""
		if channel.isLimitByGBTime :										# Ƶ����ʱ��������
			now = BigWorld.time()
			if self.__lastMsgTime + csconst.CHAT_GLOBAL_DELAY > now :		# �����ٶȹ���
				self.statusMessage( csstatus.CHAT_SPEAK_TOO_CLOSE )
				return False
			self.__lastMsgTime = now
		if self.__lasMsg == msg :											# ��Ϣ�����Ƿ���ǰһ����ͬ
			self.__repeatCount += 1
			if self.__repeatCount > csconst.CHAT_ESTOP_REPEAT_COUNT :		# �ظ����Գ���ָ������
				self.chat_lockMyChannels( [], csdefine.CHAT_FORBID_REPEAT, \
					csconst.CHAT_ESTOP_TIME )								# ����һ��ʱ��
				self.statusMessage( csstatus.CHAT_LOCK_REPEAT )
				return False
		else :																# ��Ϣ������ǰһ�β�һ��
			self.__lasMsg = msg												# ��¼�±�������
			self.__repeatCount = 1											# �ָ�ͳ�ƴ���
		if not channel.validate( self, rcvName, msg ) :						# Ƶ����������
			return False
		return True

	# -------------------------------------------------
	def __notifyLockReason( self, chids, reason ) :
		"""
		֪ͨ�ͻ��ˣ�����ԭ��
		"""
		if reason == csdefine.CHAT_FORBID_BY_GM :							# �� GM ����
			chName = csconst.CHAT_CHID_2_NAME[chids[0]]
			self.statusMessage( csstatus.CHAT_LOCK_ONE_LOCKED, chName )
		elif reason == csdefine.CHAT_FORBID_REPEAT :						# ���ظ������������
			self.statusMessage( csstatus.CHAT_LOCK_REPEAT )
		elif reason == csdefine.CHAT_FORBID_JAIL :							# ��������������
			self.statusMessage( csstatus.CHAT_LOCK_IN_PRISOPN )
		elif reason == csdefine.CHAT_FORBID_GUANZHAN:
			self.statusMessage( csstatus.CHAT_LOCK_IN_GUANZHAN )

	# -------------------------------------------------
	def __addForbiddance( self, chid, reason, duration ) :
		"""
		���һ��Ƶ������
		"""
		endTime = 0
		if duration > 0 : endTime = time.time() + duration		# ���ԵĽ���ʱ�䣨Ϊ 0 ���ʾ���ý��ԣ�
		rsdict = self.chat_fbds.get( chid, None )
		if rsdict is None :										# ԭ��û��Ƶ������
			self.chat_fbds[chid] = { reason : endTime }			# ���ﱣ��Ƶ����
			return
		etime = rsdict.get( reason, None )						# �ִ�ı����ԵĽ���ʱ��
		if etime is None :										# ���ԭ��������ָ��ԭ��Ľ���
			rsdict[reason] = endTime							# ������µĽ���ԭ��
		elif endTime == 0 :										# �������������ִ�ĳһԭ��һ�������ý���
			rsdict[reason] = 0									# �����ø�ԭ��Ľ���Ϊ���ý���
		elif etime > 0 :										# ���ָ��ԭ��Ľ����Ѿ����ڣ������������޵�
			rsdict[reason] = max( endTime, etime )				# ��ȡ�����ϳ��Ǹ�ʱ��

	def __removeForbiddance( self, chid, reason ) :
		"""
		ɾ��һ��Ƶ������
		"""
		rsdict = self.chat_fbds.get( chid, None )
		if rsdict is None : return								# Ƶ��û�б�����
		if reason in rsdict :									# Ƶ�������ԭ��Ľ���
			del rsdict[reason]									# ��ɾ����ԭ��Ľ���
		if len( rsdict ) == 0 :									# Ƶ�����Ѿ�û���κ�ԭ��Ľ���
			del self.chat_fbds[chid]							# ��ɾ��Ƶ��

	def __isForbident( self, chid ) :
		"""
		�ж�ָ��Ƶ���Ƿ񱻽���
		"""
		if chid not in self.chat_fbds :							# ָ��Ƶ�����ٽ����б���
			return False
		rsdict = self.chat_fbds.get( chid )						# �ҵ���Ƶ���Ľ����б�
		now = time.time()
		reason = None
		endTime = -1
		for rs, etime in rsdict.items() :						# �ҳ�����ʱ�����ԭ��
			if etime == 0 or etime > now :						# �����ý��Ի�δ�����ʱ��Ľ���
				endTime = etime
				reason = rs
				break
			else :												# �Ѿ���������ʱ��
				del rsdict[rs]
				if len( rsdict ) == 0 :
					del self.chat_fbds[chid]
		if reason :
			self.__notifyLockReason( [chid], reason )			# ֪ͨ�ͻ��ˣ�Ƶ�������Ե�ԭ��
			return True
		return False


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def chat_handleMessage( self, chid, rcvName, msg, blobArgs ) :
		"""
		defined method
		����һ��Ƶ����Ϣ��ֻ�� cell.RoleChat ����
		��Ϊ��Щ��Ϣ����Ҫͨ�� cell ��֤�������͵ģ����Ҫ����һ����Ϣʱ��
		�ܿ�������Ҫת�� cell���� cell ��֤��ϣ���ͨ��������ת������������
		��ˣ��벻Ҫ��ͼ���ø÷�������һ��Ƶ����Ϣ��
		@type				chid	: UINT32
		@param				chid	: Ƶ�� ID
		@type				rcvName	: STRING
		@param				rcvName	: ��Ϣ�����ߵ�����
		@type				msg		: STRING
		@param				msg		: ��Ϣ����
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: ��Ϣ�����б�
		"""
		_channels[chid].handle( self, rcvName, msg, blobArgs )

	# ------------------------------------------------
	def chat_lockMyChannels( self, chids, reason, duration ) :
		"""
		defined private method
		��ֹ�Լ��ķ���Ƶ��
		@type			chlist	 : list
		@param			chlist	 : Ҫ���Ե�Ƶ���б�����б�Ϊ�գ�������пɷ���Ƶ������
		@type			reason	 : MACRODEFINATION( UINT16 )
		@param			reason	 : ����ԭ���� csdefine �ж��壺CHAT_FORBID_XXXX
		@type			dulation : UINT32
		@param			dulation : ����ʱ�䣬�����Ӽ��㣨Ҫ�������Σ���Ϊ 0��
		"""
		if len( chids ) == 0 :									# ���Ƶ���б�Ϊ��
			chids = csconst.CHAT_EXPOSED_CHANNELS				# �������Ƶ������
		for chid in chids :										# ��һ�ŵ������б�
			self.__addForbiddance( chid, reason, duration )

	def chat_unlockMyChannels( self, chids, reason ) :
		"""
		defined private method
		����Լ��ķ���Ƶ��
		@type			chlist	 : list
		@param			chlist	 : Ҫ�����Ƶ���б�����б�Ϊ�գ�������пɷ���Ƶ�������ע��ֻ��ָ��ԭ������
		@type			reason	 : MACRODEFINATION( UINT16 )
		@param			reason	 : ����ԭ���� csdefine �ж��壺CHAT_FORBID_XXXX
		"""
		if len( chids ) == 0 :												# ��������Ƶ��
			chids = csconst.CHAT_EXPOSED_CHANNELS
		for chid in chids :
			self.__removeForbiddance( chid, reason )

	# ---------------------------------------
	def chat_lockOthersChannel( self, playerName, chName, dulation ) :
		"""
		defined method
		��ָֹ����ɫ�ķ���Ƶ������ GM �ã�
		@type			playerName : STRING
		@param			playerName : Ҫ�����Ķ�������
		@type			chName	   : STRING
		@param			chName	   : Ƶ�����ƣ����Ƶ������Ϊ�գ���ѡ��ȫ��Ƶ����
		@type			dulation   : UINT32
		@param			dulation   : ����ʱ�䣨Ҫ�������Σ���Ϊ 0��
		"""
		def onTargetFinded( player ) :
			if player == True :																# ��ɫ������
				self.statusMessage( csstatus.CHAT_LOCK_TARGET_OFFLINE, playerName )
			elif player == False :															# ��ɫ������
				self.statusMessage( csstatus.CHAT_LOCK_NO_TARGET, playerName )
			else :
				player.chat_lockMyChannels( chName, csdefine.CHAT_FORBID_BY_GM, dulation )	# �ҵ�Ŀ���ɫ������������˽���
				if chName == "" :
					self.statusMessage( csstatus.CHAT_LOCK_ALL_SUCCESS, playerName )
					player.client.onStatusMessage( csstatus.CHAT_LOCK_ALL_LOCKED, "" )
				else :
					self.statusMessage( csstatus.CHAT_LOCK_ONE_SUCCESS, playerName, chName )
					player.client.onStatusMessage( csstatus.CHAT_LOCK_ONE_LOCKED, str( ( chName,) ) )

		if chName == "" :															# ������Ƶ�����н���
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )
		elif chName not in csconst.CHAT_NAME_2_CHID :											# Ƶ��������
			self.statusMessage( csstatus.CHAT_LOCK_UNKNOW_CHANNEL, chName )
		elif csconst.CHAT_NAME_2_CHID[chName] not in csconst.CHAT_EXPOSED_CHANNELS :			# ���ɽ���Ƶ��
			self.statusMessage( csstatus.CHAT_LOCK_UNLOCKABLE )
		else :
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )

	def chat_unlockOthersChannel( self, playerName, chName ) :
		"""
		defined method
		���ָ����ɫ�ķ���Ƶ������ GM �ã�
		@type			playerName : STRING
		@param			playerName : Ҫ�����Ķ�������
		@type			chName	   : STRING
		@param			chName	   : Ƶ�����ƣ����Ƶ������Ϊ�գ���ѡ��ȫ��Ƶ����
		"""
		def onTargetFinded( player ) :
			if player == True :															# ��ɫ������
				self.statusMessage( csstatus.CHAT_UNLOCK_TARGET_OFFLINE, playerName )
			elif player == False :														# ��ɫ������
				self.statusMessage( csstatus.CHAT_UNLOCK_NO_TARGET, playerName )
			else :
				player.chat_unlockMyChannels( chName, csdefine.CHAT_FORBID_BY_GM )		# �ҵ�Ŀ���ɫ������������˽���
				if chName == "" :
					self.statusMessage( csstatus.CHAT_UNLOCK_ALL_SUCCESS, playerName )
					player.client.onStatusMessage( csstatus.CHAT_UNLOCK_ALL_LOCKED, "" )
				else :
					self.statusMessage( csstatus.CHAT_UNLOCK_ONE_SUCCESS, playerName, chName )
					player.client.onStatusMessage( csstatus.CHAT_UNLOCK_ALL_LOCKED, str( ( chName,) ) )

		if chName == "" :																# ������Ƶ�����н���
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )
		elif chName not in csconst.CHAT_NAME_2_CHID :									# Ƶ��������
			self.statusMessage( csstatus.CHAT_UNLOCK_UNKNOW_CHANNEL, chName )
		elif csconst.CHAT_NAME_2_CHID[chName] not in csconst.CHAT_EXPOSED_CHANNELS :	# ���ɽ���Ƶ��
			self.statusMessage( csstatus.CHAT_UNLOCK_UNLOCKABLE )
		else :
			BigWorld.lookUpBaseByName( "Role", playerName, onTargetFinded )


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def chat_sendMessage( self, chid, rcvName, msg, blobArgs ) :
		"""
		exposed method
		������Ϣ(���ͻ��˵��ã�����Ƶ����Ϣ)
		ע�⣺�� ֻ�� exposed Ϊ True ��Ƶ�����ܷ���
			  �� ������ֻ�� client ����
			  �� base �� cell ���� chat_handleMessage
		@type				chid	 : UINT32
		@param				chid	 : Ƶ�� ID
		@type				rcvName	 : STRING
		@param				rcvName	 : ��Ϣ�����ߵ�����
		@type				msg		 : STRING
		@param				msg		 : ��Ϣ����
		@type				blobArgs : BLOB_ARRAY
		@param				blobArgs : ��Ϣ�����б�
		"""
		channel = _channels[chid]
		if not channel.exposed :
			HACK_MSG( "role which dbid '%i' hacks on channel %i!" % ( self.databaseID, chid ) )
			return
		if self.__isForbident( chid ) :						# ������
			return
		if self.__validate( channel, rcvName, msg ) :
			channel.send( self, rcvName, msg, blobArgs )

	# -------------------------------------------------
	def chat_requireRoleInfo( self, roleName ) :
		"""
		exposed method
		������ָ����ҵ���Ϣ
		@type				roleName : str
		@param				roleName : ��ɫ����
		"""
		def lookResult( mbRole ) :
			if hasattr( mbRole, "cell" ) :					# ����ҵ�ָ����ң����Ҵ��� cell
				mbRole.cell.chat_sendRoleInfo( self )		# ������ҵ� cell ���뷢��
			else :											# ���Ŀ������Ѿ�����
				self.statusMessage( csstatus.CHAT_REQUIRE_ROLEINFO_NOT_ONLINE )
		Love3.g_baseApp.lookupRoleBaseByName( roleName, lookResult )

	# -------------------------------------------------
	# ������Ϣ
	# -------------------------------------------------
	def requestOFLMsgs( self ) :
		"""
		��ѯ���з��͸��ҵ����߼�¼
		"""
		def queryMsgsCB( msgs ) :
			if not len( msgs ) : return
			self.__tmpOflMsgs = msgs
			PLMChatRecorder.removeMsgsToReceiver( self.playerName )		# ������Ϣ�����ݿ��Ƴ�
			self.addTimer( 0, csconst.ROLE_INIT_INTERVAL, ECBExtend.SEND_OFFLINE_MSG_CBID )
		PLMChatRecorder.queryMsgsToReceiver( self.playerName, queryMsgsCB )

	def onTimer_initOflMsgToClient( self, timerID, cbid ) :
		"""
		����������Ϣ���ͻ���
		"""
		countPerTick = min( 3, len( self.__tmpOflMsgs ) )			# һ����෢��3����Ϣ���ͻ���
		chid = csdefine.CHAT_CHANNEL_PLAYMATE
		while countPerTick :
			senderName, msg, blobArgs, date = self.__tmpOflMsgs.pop( 0 )
			self.client.chat_onRcvOflMessage( chid, -1, senderName, msg, blobArgs, date )	# spkID ����Ϊ-1ָ����������Ϣ
			countPerTick -= 1
		if not len( self.__tmpOflMsgs ) :
			del self.__tmpOflMsgs
			self.delTimer( timerID )
			self.client.onInitialized( csdefine.ROLE_INIT_OFLMSGS )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onGetCell( self ) :
		"""
		��ʱ��һ��ʱ�䣬ɾ��ԭ����Ƶ������Ϊ key �Ľ����б�
		"""
		for ch in self.chat_fbds.keys() :
			if type( ch ) is not int :
				del self.chat_fbds[ch]


# RoleChat.py
