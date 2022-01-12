# -*- coding: gb18030 -*-

# $Id: ChatFacade.py,v 1.39 2008-08-30 09:15:54 huangyongwei Exp $
"""
implement chat manager

2009.04.14 : writen by huangyongwei
"""

# common
import re
import time
import string
import cPickle
import BigWorld
import ResMgr
import Language
import csdefine
import csconst
import csstatus
import csstatus_msgs
import ChatObjParser
import weakref
import keys

# client
import GUI
import csstring
import Define

# common
from bwdebug import *
from cscollections import MapList
from Weaker import WeakList
from SmartImport import smartImport
from AbstractTemplates import Singleton
from AbstractTemplates import AbstractClass
from AbstractTemplates import EventDelegate
from Function import Functor

# client
from gbref import rds
from WordsProfanity import wordsProfanity
from ViewInfoMgr import viewInfoMgr
from Color import cscolors
from event import EventCenter as ECenter
from config.client.chat_colors import Datas as chatColors
from items.ItemDataList import ItemDataList
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs
from config.client.labels import ChatFacade as lbs_ChatFacade


# --------------------------------------------------------------------
# Ƶ���б�
# ��ЩƵ���� csdefine �ж����Ƶ��
# --------------------------------------------------------------------
class Channel( object ) :
	__cg_formator = None
	__delay_status = {}									# ��Ҫ��ʱ��ʾ��״̬��Ϣ
	__delay_status[0.1] = set( [						# һ����ʱ
		csstatus.ACCOUNT_STATE_GAIN_EXP,
		csstatus.ACCOUNT_STATE_PET_GAIN_EXP,
		csstatus.ACCOUNT_STATE_UPDATE_GRADE,
		csstatus.ACCOUNT_STATE_PET_UPDATE_GRADE,
		csstatus.ACCOUNT_STATE_CURRENT_LEVEL,
		csstatus.ACCOUNT_STATE_DEAD,
		csstatus.ACCOUNT_STATE_KILL_DEAD_TO,
		csstatus.ACCOUNT_STATE_GAIN_POTENTIAL,
		] )

	def __init__( self, id, name ) :
		self.__id = id											# Ƶ�� ID
		self.__name = name										# Ƶ������
		self.__exposed = id in csconst.CHAT_EXPOSED_CHANNELS	# �Ƿ��ǿɷ���Ƶ��
		self.__shielded = False									# �Ƿ�������Ϣ
		self.__isLimitByGBTime = id in _limit_by_gbtime_chids	# �Ƿ���ȫ�ַ���ʱ��������
		self.__setable = id in _setable_chids					# �Ƿ�������ã���ҿ��Խ���Ƶ�����õ�ĳ����ҳ����ʾ��
		self.__sendable = id in _sendable_chids					# �Ƿ���������촰���з�����Ϣ�������������ط�������Ϣ��

		self.__handlers = WeakList()							# ��ʱ��Ϣ�Ĵ�����

		w = ( 255, 255, 255, 255 )								# Ĭ��Ϊ��ɫ
		self.__color = chatColors.get( name, w )				# Ƶ����ɫ
		self.__cfgSect = None									# ���Զ���Ƶ������
		
	def __delayFire2( self, spkID, spkName, msg, statusID ) :
		"""
		��ʱ��ʾ��Ϣ�������������ʱ��Χ�ڵ���Ϣ���򷵻� False
		"""
		for delayTime, statuses in self.__delay_status.iteritems() :
			if statusID in statuses :
				fn = Functor( self.onReceiveMessage, spkID, spkName, msg, statusID )
				BigWorld.callback( delayTime, fn )
				return True
		return False
		


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __resetColor( self ) :
		"""
		��������Ƶ����ɫ
		"""
		if self.__cfgSect["color"] is None :
			self.__color = chatColors.get( self.__name, ( 255, 255, 255, 255, ) )
		else :
			self.__color = self.__cfgSect.readVector4( "color" )

	def __resetShield( self ) :
		if self.__cfgSect["shield"] is None :
			self.__shielded = False
		else :
			self.__shielded = self.__cfgSect.readBool( "shield" )


	# -------------------------------------------------
	# properties
	# -------------------------------------------------
	@property
	def id( self ) :
		"""
		Ƶ�� ID
		"""
		return self.__id

	@property
	def name( self ) :
		"""
		Ƶ������
		"""
		return self.__name

	@property
	def chPrefix( self ) :
		"""
		Ƶ��ǰ׺
		"""
		return lbs_ChatFacade.channelPrefix % self.__name

	@property
	def color( self ) :
		"""
		Ƶ����ɫ
		"""
		if len( self.__color ) == 4 :
			return self.__color[:-1]
		return self.__color

	# -------------------------------------------------
	@property
	def exposed( self ) :
		"""
		�Ƿ�������ҷ�����Ϣ
		"""
		return self.__exposed

	@property
	def isLimitByGBTime( self ) :
		"""
		�Ƿ���ȫ��ʱ��������
		"""
		return self.__isLimitByGBTime

	@property
	def setable( self ) :
		"""
		�Ƿ�������ã���ҿ��Խ���Ƶ�����õ�ĳ����ҳ����ʾ��
		"""
		return self.__setable

	@property
	def sendable( self ) :
		"""
		�Ƿ��ѡ����
		"""
		return self.__sendable

	# -------------------------------------------------
	@property
	def shielded( self ) :
		"""
		�Ƿ�������Ϣ
		"""
		return self.__shielded

	# -------------------------------------------------
	@property
	def formator( self ) :
		"""
		�ı���ʽ������
		"""
		if not self.__cg_formator :
			class Formator : pass
			formator = Formator()
			from guis.tooluis.richtext_plugins.PL_Link import PL_Link
			from guis.tooluis.richtext_plugins.PL_Font import PL_Font
			formator.PL_Link = PL_Link
			formator.PL_Font = PL_Font
			self.__cg_formator = formator
		return self.__cg_formator


	# -------------------------------------------------
	# protected
	# -------------------------------------------------
	def send_( self, msg, receiver ) :
		"""
		����Ƶ����Ϣ
		@type			msg		 : str
		@param			msg		 : ���͵���Ϣ
		@type			receiver : str
		@param			receiver : ��Ϣ������
		"""
		if not self.__exposed :
			raise AttributeError( "channel '%s' is unspeakable!" )
		msg, blobArgs = chatObjParsers.parseSendMsg( msg )
		msg = csstring.toString( msg )
		if len( msg ) > csconst.CHAT_MESSAGE_UPPER_LIMIT :							# �������ݹ���
			chatFacade.rcvStatusMsg( csstatus.CHAT_WORDS_TOO_LONG )
			return
		BigWorld.player().base.chat_sendMessage( self.__id, receiver, msg, blobArgs )


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onReceiveMessage2( self, spkID, spkName, msg, *args ) :
		"""
		�յ���Ϣ
		"""
		if len( args ) == 0 :
			self.onReceiveMessage( spkID, spkName, msg, *args )
		elif not self.__delayFire2( spkID, spkName, msg, *args ):
			self.onReceiveMessage( spkID, spkName, msg, *args )
			
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		�յ���Ϣ
		"""
		if self.__shielded : return
		for handler in self.__handlers :
			handler( self, spkID, spkName, msg, *args )

	# -------------------------------------------------
	def reset( self, sect ) :
		"""
		��ɫ���������Ǳ�����
		"""
		self.__cfgSect = sect
		self.__shielded = False
		self.__resetColor()				# ���³�ʼ����ɫ
		#self.__resetShield()			# ���³�ʼ����Ϣ����״̬( �߻�Ҫ��ȡ����Ϣ���εĹ��ܣ����ע���� )


	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def shield( self ) :
		"""
		���ν�����Ϣ
		"""
		self.__shielded = True
		self.__cfgSect.writeBool( "shield", True )

	def unshield( self ) :
		"""
		�����Ϣ��������
		"""
		self.__shielded = False
		self.__cfgSect.writeBool( "shield", False )

	def resetColor( self, color = None ) :
		"""
		��������Ƶ����ɫ����� color Ϊ None������Ĭ����ɫ
		"""
		if color is None :
			w = 255, 255, 255, 255
			self.__color = chatColors.get( self.__name, w )
			self.__cfgSect.deleteSection( "color" )
			return
		if color is str :
			color = cscolors[color]
		color = tuple( color )
		if len( color ) == 3 :
			color = color + ( 255,)
		self.__color = color
		self.__cfgSect.writeVector4( "color", color )

	# -------------------------------------------------
	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		��ʽ����Ϣ�ı�
		"""
		player = BigWorld.player()
		linker = self.formator.PL_Link
		prefix = self.chPrefix									# Ƶ��ǰ׺
		if spkID == player.id :						# ����������ǽ�ɫ�Լ����򲻽����ָ�ʽ��Ϊ��������
			spkName = "[%s]: " % spkName
		elif spkName != "" :									# ���������������
			if spkID == 0 :										# �����������ϵͳ(�ǽ�ɫ)���򲻽����ָ�ʽ��Ϊ��������
				spkName = "[%s]: " % spkName
			else :
				if player.onFengQi:							# ҹս����
					entity = BigWorld.entities.get( spkID )
					if entity and entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and \
					self.id in _masked_chids:
						spkName = lbs_ChatFacade.masked
				spkName = "[%s]: " % linker.getSource( \
					spkName, "viewRoleInfo:" + spkName )		# ����������
		return "%s%s%s" % ( prefix, spkName, msg )

	# -------------------------------------------------
	def bindHandler( self, handler ) :
		"""
		��һ����Ϣ������
		"""
		if handler not in self.__handlers :
			self.__handlers.append( handler )

	def unbindHandler( self, handler ) :
		"""
		�Ƴ�һ����Ϣ������
		"""
		if handler in self.__handlers :
			self.__handlers.remove( handler )

# -----------------------------------------------------
class CH_Near( Channel ) :
	"""
	����Ƶ��
	"""
	def send_( self, msg, receiver ) :
		if BigWorld.player().state == csdefine.ENTITY_STATE_DEAD :
			chatFacade.rcvStatusMsg( csstatus.CHAT_NOT_ROUND_DEAD )
		else :
			Channel.send_( self, msg, receiver )

# -----------------------------------------------------
class CH_Whisper( Channel ) :
	"""
	����Ƶ��
	"""
	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__lastReceiver = ""
		self.__lastWhisper = ""

	# -------------------------------------------------
	# protected
	# -------------------------------------------------
	def send_( self, msg, receiver ) :
		Channel.send_( self, msg, receiver )
		self.__lastReceiver = receiver
		self.__lastWhisper = receiver


	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def reset( self, sect ) :
		"""
		��ɫ�뿪����ʱ������
		"""
		Channel.reset( self, sect )
		self.__lastReceiver = ""
		self.__lastWhisper = ""

	def getLastReceiver( self ) :
		"""
		��ȡ��һ������Ŀ��
		"""
		return self.__lastReceiver

	def getLastWhisper( self ) :
		"""
		��ȡ��������ｻ��Ŀ��
		"""
		return self.__lastWhisper

	# -------------------------------------------------
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		���յ�������Ϣ
		"""
		if self.shielded : return
		self.__lastWhisper = spkName
		Channel.onReceiveMessage( self, spkID, spkName, msg, *args )

	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		��ʽ����Ϣ�ı�
		"""
		player = BigWorld.player()
		linker = self.formator.PL_Link
		prefix = self.chPrefix									# Ƶ��ǰ׺
		nmark = "viewRoleInfo:" + spkName
		if player.onFengQi:
			spkName = lbs_ChatFacade.masked
		speaker = "[%s]" % linker.getSource( spkName, nmark )	# ��ʽ������������
		if spkID == player.id :						# ���������Լ�
			speaker = lbs_ChatFacade.preWhisperTo % speaker
		else :													# �����߲����Լ�
			speaker = lbs_ChatFacade.preWhisperFrom % speaker
		return "%s%s%s" % ( prefix, speaker, msg )

# -----------------------------------------------------
class CH_World( Channel ) :
	"""
	����Ƶ��
	"""
	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__yellVerifier = None					# �շ�ȷ�Ͽ�д�����ﲻ�Ǻܺã�����ʱ�Ҳ������õİ취��
		self.__lastSendTime = 0						# ���һ�η���������Ϣ��ʱ��
		self.__needRemind = True					# �Ƿ���Ҫ�շ���ʾ


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __sendMessage( self, msg ) :
		"""
		ֱ�ӷ�����Ϣ
		"""
		Channel.send_( self, msg, "" )
		self.__lastSendTime = time.time()

	def __remind( self, msg, res, unremind ) :
		"""
		�ź���ʾ
		"""
		if res == RS_YES :
			self.__needRemind = not unremind
			self.__sendMessage( msg )


	# -------------------------------------------------
	# protected
	# -------------------------------------------------
	def send_( self, msg, receiver ) :
		if self.__yellVerifier is None :
			self.__yellVerifier = __import__( "guis/general/chatwindow/YellVerifyBox" )

		player = BigWorld.player()
		if player.level < csconst.CHAT_YELL_LEVEL_REQUIRE :					# �ȼ�����
			chatFacade.rcvStatusMsg( csstatus.CHAT_YELL_UNDER_LEVEL )
		elif self.__lastSendTime + csconst.CHAT_YELL_DELAY > time.time() :	# ���η���ʱ�������ڹ涨ʱ����
			chatFacade.rcvStatusMsg( csstatus.CHAT_YELL_TOO_CLOSE )
		elif player.money < csconst.CHAT_YELL_USE_MONEY :					# ��Ǯ����
			chatFacade.rcvStatusMsg( csstatus.CHAT_YELL_MONEY_NOTENOUGH )
		elif self.__needRemind :											# ��Ҫ�շ���ʾ
			self.__yellVerifier.show( Functor( self.__remind, msg ) )
		else :
			self.__sendMessage( msg )


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		��ɫ��������ʱ������
		"""
		self.__needRemind = True							# ����ȷ���շ���ʾ

# -----------------------------------------------------
class CH_Broadcast( Channel ) :
	"""
	�㲥Ƶ��
	"""
	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		��ʽ����Ϣ�ı�
		"""
		return msg

# -----------------------------------------------------
class CH_NPCSpeak( Channel ) :
	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		NPC ���ֲ�������
		"""
		msgInfos = spkName.split( "\0" )		
		if len( msgInfos ) == 2 :													# ��������ǰ׺��ָ����������
			prefix, spkName = msgInfos
		else :
			prefix = "N"															# û������ǰ׺��Ĭ��Ϊ��������

		if spkName != "" :
			if prefix == "N" :														# NPC ����
				return "%s[%s]: %s" % ( self.chPrefix, spkName, msg )
			elif prefix == "M" :													# NPC ����
				return lbs_ChatFacade.npcWhisper % ( self.chPrefix, spkName, msg )
			elif prefix == "W" :													# NPC �ź�
				return lbs_ChatFacade.npcYell % ( self.chPrefix, spkName, msg )
		return "%s%s: %s" % ( self.chPrefix, lbs_ChatFacade.anoySay, msg )			# NPC �������ǲ����ܵ���������


# -----------------------------------------------------
class CH_Combat( Channel ) :
	# ---------------------------------------
	# ��ʱ��ʾ����Ϣ
	# ---------------------------------------
	__delay_status = {}									# ��Ҫ��ʱ��ʾ��״̬��Ϣ
	__delay_status[0.1] = set( [						# һ����ʱ
		] )

	__delay_status[0.2] = set( [						# ������ʱ
		] )

	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__settableStatus = {}												# ������Ϊ�Ƿ���ʾ����Ϣ
		self.__settableStatus["enemy"]	 = csstatus_msgs.enemyInjuredStatus		# ����������Ϣ
		self.__settableStatus["skill"]	 = csstatus_msgs.skillHitStatus			# ���ܹ�����Ϣ
		self.__settableStatus["revert"]  = csstatus_msgs.revertStatus			# �ظ���Ϣ
		self.__settableStatus["injured"] = csstatus_msgs.injuerdStatus			# ������Ϣ
		self.__settableStatus["buff"]	 = csstatus_msgs.buffStatus				# buff ��Ϣ
		self.__eventMacro = "EVT_ON_CHAT_COMBAT_MSG"

	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __isShielded( self, statusID ) :
		"""
		��Ϣ�Ƿ��Ѿ������ˣ�����Ϊ����ʾ�������� True ��ʾϵͳ�Ѿ���������Ϊ����ʾ
		"""
		for key, statuses in self.__settableStatus.iteritems() :
			if not statusID in statuses : continue
			if not viewInfoMgr.getSetting( "hitedInfo", key ) :
				return True
		return False

	# ---------------------------------------
	def __delayFire( self, spkID, spkName, msg, statusID ) :
		"""
		��ʱ��ʾ��Ϣ�������������ʱ��Χ�ڵ���Ϣ���򷵻� False
		"""
		for delayTime, statuses in self.__delay_status.iteritems() :
			if statusID in statuses :
				fn = Functor( Channel.onReceiveMessage, self, spkID, spkName, msg, statusID )
				BigWorld.callback( delayTime, fn )
				return True
		return False


	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		����Ƶ����Ϣ
		"""
		if len( args ) == 0 :
			Channel.onReceiveMessage( self, spkID, spkName, msg, *args )
		elif self.__isShielded( *args ) :
			return
		elif not self.__delayFire( spkID, spkName, msg, *args ) :
			Channel.onReceiveMessage( self, spkID, spkName, msg, *args )

# -----------------------------------------------------
class CH_MSGBox( Channel ) :
	def __init__( self, id, name ) :
		Channel.__init__( self, id, name )
		self.__pyInShowBoxes = {}

	# -------------------------------------------------
	# callbacks
	# -------------------------------------------------
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		def callback( statusID, res ) :
			if statusID :
				self.__pyInShowBoxes.pop( statusID )

		statusID = args[0] if len( args ) else None
		if statusID in self.__pyInShowBoxes :
			self.__pyInShowBoxes.pop( statusID ).dispose()
		func = Functor( callback, statusID )
		pyBox = showMessage( msg, "", MB_OK, func, gstStatus = Define.GST_IN_WORLD )
		if statusID : 																	# statusID �п���Ϊ None����������жϻᵼ������IDΪNone����Ϣֻ��ͬʱ��ʾһ�� --pj
			self.__pyInShowBoxes[statusID] = pyBox
		Channel.onReceiveMessage( self, spkID, spkName, msg, *args )

# -----------------------------------------------------
class CH_Playmate( Channel ) :
	"""
	�������֮��Ĵ�������
	"""

	def formatMsg( self, spkID, spkName, msg, *args ) :
		"""
		��ʽ����Ϣ�ı�
		"""
		plFont = self.formator.PL_Font
		player = BigWorld.player()
		if spkID == 0 :												# ϵͳ��Ϣ
			msg = plFont.getSource( msg, fc = (255,0,255,255) )
			return msg, ""
		elif spkID == -1 :											# ������Ϣ
			msg = lbs_ChatFacade.OFFLINE_MSG_PREFIX + msg			# ���ǰ׺
		elif spkID == player.id :						# ����Լ�����Ϣ
			spkName = player.playerName
		elif player.onFengQi:
			spkName = lbs_ChatFacade.masked
		date = args[0] if len( args ) else ""
		date = plFont.getSource( date, fc = (0,255,255,255) )
		return "[%s] %s" % ( spkName, date ), msg
		
class CH_TongCityWar( Channel ):
	"""
	���ս������ר��Ƶ��
	"""
	def onReceiveMessage( self, spkID, spkName, msg, *args ) :
		"""
		����Ƶ����Ϣ
		"""
		if BigWorld.player().getCurrentSpaceType() == csdefine.SPACE_TYPE_CITY_WAR_FINAL: #���β��ڸ����ڵĳ�Ա��Ϣ
			Channel.onReceiveMessage( self, spkID, spkName, msg, *args )


# --------------------------------------------------------------------
# Ƶ�������б�
# --------------------------------------------------------------------
_channel_maps = {
	# ��ɫ����Ƶ��						  Ƶ����
	csdefine.CHAT_CHANNEL_NEAR			: CH_Near,		# ����Ƶ��
	csdefine.CHAT_CHANNEL_LOCAL			: Channel,		# ����Ƶ��
	csdefine.CHAT_CHANNEL_TEAM			: Channel,		# ����Ƶ��
	csdefine.CHAT_CHANNEL_TONG			: Channel,		# ���Ƶ��
	csdefine.CHAT_CHANNEL_WHISPER		: CH_Whisper,	# ˽��Ƶ��
	csdefine.CHAT_CHANNEL_WORLD			: CH_World,		# ����Ƶ��
	csdefine.CHAT_CHANNEL_RUMOR			: Channel,		# ҥ��Ƶ��
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: Channel,		# �����㲥
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: Channel,		# �����㲥
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : CH_TongCityWar,		# ���ս��

	# GM/����Ƶ��
	csdefine.CHAT_CHANNEL_SYSBROADCAST	: CH_Broadcast,	# ����㲥

	# NPC ����Ƶ��
	csdefine.CHAT_CHANNEL_NPC_SPEAK		: CH_NPCSpeak,	# NPC��������������磩
	csdefine.CHAT_CHANNEL_NPC_TALK		: Channel,		# NPC �Ի�Ƶ��

	# ϵͳ��ʾƵ��
	csdefine.CHAT_CHANNEL_SYSTEM		: Channel,		# ϵͳƵ������ʾ�ɷ����������ĸ��ֻ�������Ʒ/ǿ��/��Ƕ�Ȳ�����
	csdefine.CHAT_CHANNEL_COMBAT		: CH_Combat,	# ս��Ƶ������ʾս����Ϣ��
	csdefine.CHAT_CHANNEL_PERSONAL		: Channel,		# ����Ƶ��������Ƶ����ʾ����ڻ�þ��顢Ǳ�ܡ���Ǯ����Ʒ��Ԫ������Ϣ��
	csdefine.CHAT_CHANNEL_MESSAGE		: Channel,		# ��ϢƵ������ʾ��ɫ�Ĳ��������Ĵ�����Ϣ����ʾ��Ϣ��
	csdefine.CHAT_CHANNEL_SC_HINT		: Channel,		# ����Ļ�м���ʾ��Ƶ��
	csdefine.CHAT_CHANNEL_MSGBOX		: CH_MSGBox,	# �� MessageBox ��ʾ��Ƶ��

	# ������������
	csdefine.CHAT_CHANNEL_PLAYMATE		: CH_Playmate,	# ������������
	
	csdefine.CHAT_CHANNEL_CAMP			: Channel,		# ��ӪƵ��
	}

# -------------------------------------------
# �������õ������ҳ����ʾ��Ƶ��
_setable_chids = set([
	# ��ɫ����Ƶ��
	csdefine.CHAT_CHANNEL_NEAR,				# ����Ƶ��
	csdefine.CHAT_CHANNEL_LOCAL,			# ����Ƶ��
	csdefine.CHAT_CHANNEL_TEAM,				# ����Ƶ��
	csdefine.CHAT_CHANNEL_TONG,				# ���Ƶ��
	csdefine.CHAT_CHANNEL_WHISPER,			# ˽��Ƶ��
	csdefine.CHAT_CHANNEL_WORLD,			# ����Ƶ��
#	csdefine.CHAT_CHANNEL_RUMOR,			# ҥ��Ƶ��					# �����Щ����ҥ�����ˣ�����Ҫ����ʱ����ҥ��Ƶ��
	csdefine.CHAT_CHANNEL_WELKIN_YELL,		# �����㲥
	csdefine.CHAT_CHANNEL_TUNNEL_YELL,		# �����㲥
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR,	# ���ս��

	# GM/����Ƶ��
	csdefine.CHAT_CHANNEL_SYSBROADCAST,		# ����㲥

	# NPC ����Ƶ��
	csdefine.CHAT_CHANNEL_NPC_SPEAK,		# NPC��������������磩

	# ϵͳ��ʾƵ��
	csdefine.CHAT_CHANNEL_SYSTEM,			# ϵͳƵ��
	csdefine.CHAT_CHANNEL_COMBAT,			# ս��Ƶ��
	csdefine.CHAT_CHANNEL_PERSONAL,			# ����Ƶ��
	csdefine.CHAT_CHANNEL_MESSAGE,			# ��ϢƵ��
	csdefine.CHAT_CHANNEL_MSGBOX,			# �� MessageBox ��ʾ��Ƶ��
	csdefine.CHAT_CHANNEL_CAMP,				# ��Ӫ
	])


# ��ѡ�񲢿ɷ��Ե�Ƶ�������ݼ����������촰����ѡ������Ϣ��Ƶ����
_sendable_chids = {
	csdefine.CHAT_CHANNEL_NEAR				: "S",			# ����
	csdefine.CHAT_CHANNEL_LOCAL				: "M",			# ����
	csdefine.CHAT_CHANNEL_TEAM				: "P",			# ����
	csdefine.CHAT_CHANNEL_TONG				: "G",			# ���
	csdefine.CHAT_CHANNEL_WHISPER			: "T",			# ����
	csdefine.CHAT_CHANNEL_WORLD				: "W",			# ����
	csdefine.CHAT_CHANNEL_CAMP				: "C",			# ��Ӫ
#	csdefine.CHAT_CHANNEL_RUMOR				: "E",			# ҥ��						# �����Щ����ҥ�����ˣ�����Ҫ����ʱ����ҥ��Ƶ��
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR		: "A"	# ���ս��
	}

# ��ȫ�ַ���ʱ�������Ƶ�Ƶ��
_limit_by_gbtime_chids = set( [
	csdefine.CHAT_CHANNEL_NEAR,				# ����
	csdefine.CHAT_CHANNEL_LOCAL,			# ����
	csdefine.CHAT_CHANNEL_TEAM,				# ����
	csdefine.CHAT_CHANNEL_TONG,				# ���
	csdefine.CHAT_CHANNEL_WHISPER,			# ����
	csdefine.CHAT_CHANNEL_PLAYMATE,			# ���
	csdefine.CHAT_CHANNEL_CAMP,				# ��Ӫ
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR,	# ���ս��
	] )

# ���б�����͵�Ƶ��
_emotion_chids = set( [
	csdefine.CHAT_CHANNEL_NEAR,				# ����
	csdefine.CHAT_CHANNEL_LOCAL,			# ����
	csdefine.CHAT_CHANNEL_TEAM,				# ����
	csdefine.CHAT_CHANNEL_TONG,				# ���
	csdefine.CHAT_CHANNEL_WHISPER,			# ����
	csdefine.CHAT_CHANNEL_WORLD,			# ����
	csdefine.CHAT_CHANNEL_RUMOR,			# ҥ��
	csdefine.CHAT_CHANNEL_WELKIN_YELL,		# ����
	csdefine.CHAT_CHANNEL_PLAYMATE,			# ���
	csdefine.CHAT_CHANNEL_CAMP,				# ��Ӫ
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR,	# ���ս��
	] )

#��ҹս���ܸ�����Ƶ���Ƶĵ�
_masked_chids = set( [
	csdefine.CHAT_CHANNEL_NEAR,
	csdefine.CHAT_CHANNEL_LOCAL,
	] )

# --------------------------------------------------------------------
# ����Ƶ��������
# --------------------------------------------------------------------
class ChatFacade( Singleton ) :
	def __init__( self ) :
		self.channels = MapList()				# ����Ƶ��
		self.setableChannels = []				# ������Ƶ��( �����õ�ĳ����ҳ��ʾ��Ƶ�� )
		self.__sendableChannels = {}			# ��ѡ������Ϣ��Ƶ��:{ ��ݼ��ַ� : ��Ӧ��Ƶ�� }

		self.__lastSendTime = 0					# ǰһ�η�����Ϣ��ʱ��
		self.__statusHandlers = {}				# ״̬��Ϣ��ע�������
		self.__cfgPath = ""						# ����·��
		self.__cfgSect = None					# ���� section
		self.__initialize()						# ��ʼ��Ƶ���б�

		self.__objCount = 0						# ��Ϣ�а���������������

		ECenter.registerEvent( "EVT_ON_BEFORE_GAME_QUIT", self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		global _channel_maps
		global _limit_by_gbtime_chids
		ptlist = []
		for chid, CLSChannel in _channel_maps.iteritems() :
			name = csconst.CHAT_CHID_2_NAME[chid]
			channel = CLSChannel( chid, name )
			self.channels[chid] = channel
			if channel.setable :
				self.setableChannels.append( channel )
			shortcut = _sendable_chids.get( chid, None )
			if shortcut :
				self.__sendableChannels[shortcut] = chid
		del _channel_maps											# ���Ƶ��������������Ҫ
		del _limit_by_gbtime_chids

	def __getConfigSect( self ) :
		"""
		��ȡƵ������·��
		"""
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__cfgPath = "account/%s/%s/chat_colors.xml" % ( accountName, roleName )
		self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )
		return self.__cfgSect

	# -------------------------------------------------
	@staticmethod
	def __splitCommand( msg, infos ) :
		"""
		��ȡָ��
		"""
		if msg.startswith( "/" ) :
			sps = msg[1:].split( None, 1 )
			if len( sps ) == 0 :
				return False
			infos[0] = sps[0]
			if len( sps ) == 2 :
				infos[1] = sps[1]
			else :
				infos[1] = ""
			return True
		return False

	def __handleCommand( self, cmd, args ) :
		"""
		ָ����Ϣ����
		"""
		player = BigWorld.player()
		target = player.targetEntity
		if target and BigWorld.entity( target.id ) :			# ��Ŀ��������
			player.cell.wizCommand( target.id, cmd, args )		# ָ�����Ŀ�귢��
		else :
			player.cell.wizCommand( player.id, cmd, args )		# ����ָ����Ե�ǰ��ɫ����

	# -------------------------------------------------
	def __handleRegisteredStatus( self, statusID, msg ) :
		"""
		����ע���˵�״̬��Ϣ
		"""
		if statusID in self.__statusHandlers :
			self.__statusHandlers[statusID]( statusID, msg )


	# ------------------------------------------------
	# callbacks
	# ------------------------------------------------
	def onEvent( self, macroName, *arg ) :
		if macroName == "EVT_ON_BEFORE_GAME_QUIT" :
			if self.__cfgSect is not None :
				try :
					self.__cfgSect.save()				# �˳���Ϸǰ��������
				except IOError, err :
					ERROR_MSG( "save chat channels setting failed!" )

	def onGameStart( self ) :
		"""
		��Ϸ������Ϻ󱻵���
		"""
		emotionParser.onGameStart()						# ��ʼ������
		chatObjParsers.onGameStart()						# ��ʼ����Ʒ����

	def onRoleEnterWorld( self ) :
		"""
		��ɫ���������Ǳ�����
		"""
		cfgSect = self.__getConfigSect()				# ��ȡ�û�Ƶ������
		for channel in self.channels.values() :
			chName = channel.name
			sect = cfgSect[chName]
			if sect is None :							# Ƶ�����ò�����
				sect = cfgSect.createSection( chName )	# ����Ƶ�����ƴ���һ��
			channel.reset( sect )

	def onRoleLeaveWorld( self ) :
		"""
		��ɫ�뿪����ʱ������
		"""
		if self.__cfgSect is not None :
			self.__cfgSect.save()
			ResMgr.purge( self.__cfgPath )
			self.__cfgPath = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def saveChannelConfig( self ) :
		"""
		����Ƶ�������ļ�
		"""
		self.__cfgSect.save()

	def getSetableCHIDs( self ) :
		"""
		��ȡ���п����������ҳ�����õ�Ƶ��
		"""
		return _setable_chids

	def getChannel( self, chid ) :
		"""
		��ȡָ�� ID ��Ƶ��
		"""
		return self.channels[chid]

	def shortcutToCHID( self, shortcut ) :
		"""
		��ݼ���Ӧ��Ƶ��ID
		"""
		shortcut = shortcut.upper()
		for chid, sc in _sendable_chids.iteritems() :
			if sc == shortcut : return chid
		return None

	def chidToShortcut( self, chid ) :
		"""
		Ƶ����Ӧ�Ŀ�ݼ�
		"""
		return _sendable_chids.get( chid )

	# -------------------------------------------------
	def bindChannelHandler( self, chid, handler ) :
		"""
		����Ϣ������
		"""
		self.channels[chid].bindHandler( handler )

	def unbindChannelHandler( self, chid, handler ) :
		"""
		ȡ����Ϣ�������İ�
		"""
		self.channels[chid].unbindHandler( handler )


	# ------------------------------------------------
	# Ƶ����Ϣ���
	# ------------------------------------------------
	def rcvChannelMsg( self, chid, spkID, spkName, msg, blobArgs, *args ) :
		"""
		����Ƶ����Ϣ
		"""
		if BigWorld.player() is None : return						# ��Щ��Ϣ�Ǵ��ͻ�����ʱһ���ٷ��͵ģ���������ʱ��ɫ�Ѿ��˳���Ϸ�������������
		msg_temp = msg.split("/ltime")
		msg = msg_temp[0]
		channel = self.channels[chid]
		if channel.exposed :										# �������ҿɷ���Ƶ��
			msgSegs = []
			emsgs = emotionParser.tearRcvMsg( msg )					# ���������Ǳ�����Ϣ
			for isEmote, msg in emsgs :
				if isEmote :
					msgSegs.append( ( isEmote, msg ) )
					continue
				subSegs = chatObjParsers.tearRcvMsg( msg, blobArgs )# ������Ϣ��������ͨ��Ϣ
				msgSegs.extend( subSegs )
			msg = ""
			for ignore, msgSeg in msgSegs :							# ��Ϣ����
				if ignore :
					msg += msgSeg
					continue
				msg += wordsProfanity.filterMsg( msgSeg )			# �������ͨ��Ϣ��������´ʻ����
		if chid in _emotion_chids :									# ת������
			msg = emotionParser.parseRcvMsg( msg )
		if len( blobArgs ) :
			msg = chatObjParsers.parseRcvMsg( msg, blobArgs )		# ת���������
		if len( msg_temp ) > 1 :
			msg = msg + "/ltime" + msg_temp[1]
		channel.onReceiveMessage( spkID, spkName, msg, *args )

	# ---------------------------------------
	def sendChannelMessage( self, chid, msg, receiver = "" ) :
		"""
		����Ƶ����Ϣ
		ע�⣺���������Ƶ���� send_ ���������������趨�� ChatFacade ��Ƶ������Ԫ��
		@type				chid 	 : MSCRO DEFINATION
		@pararm				chid	 : Ƶ�� ID
		@type				receiver : str
		@param				receiver : ��Ϣ����������
		@type				msg		 : str
		@param				msg		 : ��Ϣ����
		"""
		msg = csstring.toString( msg )
		msgInfo = ["", ""]
		if self.__splitCommand( msg, msgInfo ) :									# ��Ϣ�к���ָ��
			cmd, msg = msgInfo
			cmdUpper = cmd.upper()
			if cmdUpper in self.__sendableChannels :								# �����Ϣ�д���ָ����Ƶ����ݼ�
				chid = self.__sendableChannels[cmdUpper]							# ���޸�Ƶ�� ID
			else :
				self.__handleCommand( cmd, msg )									# ������Ϊ��ϵͳָ��
				return True

		channel = self.channels[chid]
		if channel.isLimitByGBTime :												# Ƶ���Ƿ���ȫ�ַ���ʱ��������
			if self.__lastSendTime + csconst.CHAT_GLOBAL_DELAY > time.time() :		# ʱ����̫��
				self.rcvStatusMsg( csstatus.CHAT_SPEAK_TOO_CLOSE )
				return False

		msg = csstring.toWideString( msg )
		self.channels[chid].send_( msg, receiver )									# ע�⣺���ø�Ƶ���� send_ Ϊ ChatFacade ����Ԫ����
																					# ������Ƶ���� send �������Ǳ����û�ֱ��ͨ��Ƶ�����ͣ�
																					# �Ӷ�������ƹ�������֮ǰ���ж�
		self.__objCount = 0															# �����Ϣ�а���������������
		self.__lastSendTime = time.time()
		return True

	# ---------------------------------------
	def activeChatWindow( self, chid, receiver = "" ) :
		"""
		�������촰�ڣ�����λ��ָ����Ϣ����Ƶ��
		"""
		if chid in _sendable_chids :
			channel = self.channels[chid]
			ECenter.fireEvent( "EVT_ON_CHAT_ACTIVE_CHAT_SENDER", channel, receiver )

	def whisperWithChatWindow( self, receiver ) :
		"""
		�������촰�ڣ�����ָ����������
		"""
		if receiver == "" :
			ERROR_MSG( "receiver must't be empty!" )
		else :
			channel = self.channels[csdefine.CHAT_CHANNEL_WHISPER]
			ECenter.fireEvent( "EVT_ON_CHAT_ACTIVE_CHAT_SENDER", channel, receiver )

	# ---------------------------------------
	def insertChatMessage( self, msg ) :
		"""
		�ڹ�괦����������Ϣ
		"""
		msgInserter.insertMessage( msg )

	def insertChatObj( self, objType, obj ) :
		"""
		����һ�����������Ϣ�����
		"""
		objCount = 3											# ���ֻ�ܷ��� 3 ��������󣨽��ͻ������ƣ�������������ﲻ�� 3 ���к궨���ˣ�ֱ��д����
		if self.__objCount < objCount :
			msg = chatObjParsers.getMaskObj( objType, obj )
			msgInserter.insertMessage( msg )
		else :
			msg = lbs_ChatFacade.chatObjOverstep % objCount
			BigWorld.player().chat_systemInfo( "(SC):" + msg )
			msgInserter.insertMessage( "" )						# �����ٲ���һ���մ�����Ŀ����ʹ����Ϣ�������Ȼ���ڼ���״̬�������佹�㽫�ᱻ����

	def onChatObjCount( self, objCount ):
		"""
		�������ı�ʱ����
		"""
		self.__objCount = objCount
	# ------------------------------------------------
	# ״̬��Ϣ���
	# ------------------------------------------------
	def rcvStatusMsg( self, statusID, *args ) :
		"""
		����״̬��Ϣ
		"""
		if BigWorld.player() is None : return							# ��Щ��Ϣ�Ǵ��ͻ�����ʱһ���ٷ��͵ģ���������ʱ��ɫ�Ѿ��Ƴ���Ϸ�������������
		statusInfo = csstatus_msgs.getStatusInfo( statusID, *args )
		self.__handleRegisteredStatus( statusID, statusInfo.msg )		# ����ע���˵�״̬��Ϣ
		for chid in statusInfo.chids :
			if chid == csdefine.CHAT_CHANNEL_SYSTEM:
				self.channels[chid].onReceiveMessage2( 0, statusInfo.spkName, statusInfo.msg, statusID )
			else:
				self.channels[chid].onReceiveMessage( 0, statusInfo.spkName, statusInfo.msg, statusID )
	
	def rcvMsgDirect( self, chids, spkName, msg ) :
		"""
		ֱ�ӽ�����Ϣ������Ƶ����������
		"""
		if BigWorld.player() is None : return							# ��Щ��Ϣ�Ǵ��ͻ�����ʱһ���ٷ��͵ģ���������ʱ��ɫ�Ѿ��Ƴ���Ϸ�������������
		
		for chid in chids :
			if chid == csdefine.CHAT_CHANNEL_SYSTEM:
				self.channels[chid].onReceiveMessage2( 0, spkName, msg )
			else:
				self.channels[chid].onReceiveMessage( 0, spkName, msg )

	# ---------------------------------------
	def bindStatus( self, statusID, fnHandler ) :
		"""
		��һ��״̬��Ϣ��������ָ������Ϣ����ʱ��fnHandler �ᱻ������
		"""
		if statusID not in self.__statusHandlers :
			self.__statusHandlers[statusID] = EventDelegate()
		self.__statusHandlers[statusID].bind( fnHandler )

	def unbindStatus( self, statusID, fnHandler ) :
		"""
		���״̬��Ϣ��
		"""
		if statusID in self.__statusHandlers :
			eventDelegate = self.__statusHandlers[statusID]
			if eventDelegate.hasHandler( fnHandler ) :
				eventDelegate.unbind( fnHandler )
				if eventDelegate.handlerCount == 0 :
					self.__statusHandlers.pop( statusID )
			else :
				ERROR_MSG( "handler '%s' is not in event delegate of status '%#0x'" % statusID )
		else :
			ERROR_MSG( "no handlers relative to status message: '%#0x'" % statusID )



# --------------------------------------------------------------------
# ��Ϣ������
# --------------------------------------------------------------------
class EmotionParser( Singleton ) :
	"""
	���������
	"""
	__cc_cfg	  = "maps/emote/emotionfaces.xml"		# ��������·��
	__cc_gui_path = "maps/emote/emote.gui"				# ����ͼ�� gui ����·��
	cc_emote_size  = 32, 32

	def __init__( self ) :
		self.__sect = None
		self.__emotions = {}							# { ת���ַ� : ( ����·��, �������� )}
		self.__rtEmotions = {}							# { ת���ַ� : CSRichText ת�� }
		self.__reTpl = re.compile("[:)]")				# ����ת���滻����ģ��
		self.__linkImage = None
		self.__titleNames = {}
		self.__emotionSigns = {}

	def __initialize( self ) :
		emote = GUI.load( self.__cc_gui_path )
		EmotionParser.cc_emote_size = emote.size		# ��ȡ����ͼ���С

		self.__linkImage = smartImport( "guis.tooluis.richtext_plugins.PL_Image:PL_Image" )
		self.__sect = ResMgr.openSection( self.__cc_cfg )
		if self.__sect is None :
			WARNING_MSG( "load chat emotion config file failed!" )
			return
		escs = []
		for pageIndex, sect in self.__sect.items() :
			if sect is None:continue
			index = int( pageIndex )
			self.__titleNames[index] = sect.asString
			if index not in self.__emotionSigns:
				self.__emotionSigns[index] = []
			emotionSigns = self.__emotionSigns[index]
			for mark, subSect in sect.items():
				sign = subSect.readString( "sign" )
				texture = subSect.readString( "path" )
				dsp = subSect.readString( "description" )
				self.__emotions[sign] = ( texture, dsp )
				self.__rtEmotions[sign] = self.__linkImage.getSource( self.__cc_gui_path, texture, text = sign )
				emotionSigns.append( sign )
				escs.append( re.escape( sign ) )
		self.__reTpl = re.compile( "|".join( escs ) )
		Language.purgeConfig( self.__cc_cfg )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def emotionIter( self ) :
		"""
		������Ϣ������
		"""
		for pageIndex, sect in self.__sect.items() :
			for mark, subSect in sect.items():
				sign = subSect.readString( "sign" )
				path = subSect.readString( "path" )
				dsp = subSect.readString( "description" )
				yield sign, path, dsp

	@property
	def reTpl( self ) :
		"""
		����ת��ģ��
		"""
		return self.__reTpl

	@property
	def titleNames( self ):
		"""
		�����ҳ����
		"""
		return self.__titleNames

	@property
	def emotionSigns( self ):
		"""
		����ת���
		"""
		return self.__emotionSigns


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onGameStart( self ) :
		"""
		��ɫ��������ʱ��ʼ��
		"""
		self.__initialize()

	# -------------------------------------------------
	def getEmotion( self, esc ) :
		"""
		��ȡ������Ϣ
		"""
		return self.__emotions[esc]

	# -------------------------------------------------
	def formatEmotion( self, esc, lmark = "", size = None ) :
		"""
		@param		esc : �������
		@type		esc : string
		@param		lmark : �����ӱ��
		@type		lmark : str
		@param		size : ����ߴ�
		@type		size : tuple
		"""
		texture = self.__emotions[esc][0]
		return self.__linkImage.getSource( self.__cc_gui_path, texture, lmark = lmark, size = size )

	# ---------------------------------------
	def tearRcvMsg( self, msg ) :
		"""
		������Ϣת�壬�������ͺ����Ϣ���ֶη��أ��Ӷ���ǳ��Ķ�Ϊ��������ı����Ķ�����ͨ�ı�:
		[( True, @I{...} ), ( False, "xxxx" ), ( False "xxxx" ), ...]
		"""
		emsgs = []
		start = 0
		end = len( msg )
		if self.__reTpl :
			emIter = self.__reTpl.finditer( msg )						# ��ȡ���б����ֶεĵ�����
			while True :
				try :
					em = emIter.next()
					eStart = em.start()
					subMsg = msg[start:eStart]
					if start != eStart :
						emsgs.append( ( False, subMsg ) )	# ��ͨ��Ϣ
					emsgs.append( ( True, em.group() ) )				# �����ֶ�
					start = em.end()
				except StopIteration :
					break
		if start != end :
			emsgs.append( ( False, msg[start:end] ) )					# ʣ��ķǱ�����Ϣ
		return emsgs

	def parseRcvMsg( self, msg ) :
		"""
		������Ϣת�壬������ RichText ʶ��Ĵ�������Ϣ
		"""
		if self.__reTpl:
			replacer = lambda esc : self.__rtEmotions[esc.group()]
			msg = self.__reTpl.sub( replacer, msg )
		return msg


# --------------------------------------------------------------------
# �������
# --------------------------------------------------------------------
class BaseObj( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self, objType, minLen, defName ) :
		"""
		@type			objType : MSCRO DEFINATION
		@param			objType : �� common/ChatObjParser.py �ж���
		@type			minLen	: int
		@param			minLen	: Ҫ���һ��������Ҫ�������ֽ���
		@type			defName : str
		@param			defName : �������ʧ�ܣ�Ĭ������������ʾ������
		"""
		self.objType = objType
		self.minLen_ = minLen
		self.defName_ = defName

	def dump( self, text ) :
		"""
		���ַ�����ʽ��������󣬽��ͳɿɴ�������Ƶ����Ϣ������ת��Ϊ���Ͳ�����BLOB��
		���� blob �� None
		"""
		pass

	def load( self, info ) :
		"""
		�����յ���Ƶ����Ϣ����ת��Ϊ�ɶ��ı���ת��Ϊ RichText ʶ����ַ�����
		���践��һ���ַ���
		"""
		pass

	# ---------------------------------------
	def getMaskText( self, item ) :
		"""
		����Ʒת��Ϊ������ʽ���ַ�����ת��Ϊ RichTextBox/MLRichTextBox ���ص��ı���
		���践��һ���ַ���
		"""
		pass

	def getViewName( self, text ) :
		"""
		���ݰ�����ʽ����Ʒ�����ı�����ȡ�û��ɿ����Ķ������ƣ�ת��Ϊ RichTextBox/MLRichTextBox ��ʾ���ı���
		���践�� None�����ַ�������ɫ��
		"""
		pass

	__abstract_methods.add( dump )
	__abstract_methods.add( load )
	__abstract_methods.add( getMaskText )
	__abstract_methods.add( getViewName )


# -----------------------------------------------------
# ��Ʒ����
# -----------------------------------------------------
class ChatItem( BaseObj ) :
	LMARK = "chat_item:"

	def __init__( self ) :
		objType = chatObjTypes.ITEM
		minLen = 9
		defName = lbs_ChatFacade.unknowItem
		BaseObj.__init__( self, objType, minLen, defName )


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __getItem( self, text ) :
		"""
		����������ʽ����Ʒ��Ϣ����ȡ�ı���Ӧ����Ʒ
		"""
		if len( text ) < self.minLen_ : return None
		try : id, extra = eval( text )
		except : return None
		item = ItemDataList.instance().createDynamicItem( id )
		item.extra = extra
		return item

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def dump( self, text ) :
		"""
		���һ��������Ϊ����������͵���Ʒ��ת��Ϊ���Ͳ�����BLOB��
		���践�� BLOB �� None
		"""
		item = self.__getItem( text )
		if item :
			info = item.id, item.extra
			return ChatObjParser.dumpObj( self.objType, info )
		return None

	def load( self, info ) :
		"""
		�����յ���Ƶ����Ϣ����ת��Ϊ�ɶ��ı���ת��Ϊ RichText ʶ����ַ�����
		���践��һ���ַ���
		"""
		try : id, extra = info
		except : return " "
		item = ItemDataList.instance().createDynamicItem( id )
		if item :
			item.extra = extra
			itemName = item.fullName()
			foreColor = item.getQualityColor()
		else :
			itemName = self.defName_
			foreColor = ChatObjParser.OBJ_COLORS[self.objType]
		lmark = self.LMARK + str( ( id, extra ) ).replace( "}", "\}" )
		linkText = ChatObjParser.viewObj( itemName )
		return chatObjParsers.plnRTLink.getSource( linkText, lmark, cfc = foreColor )

	# ---------------------------------------
	def getMaskText( self, item ) :
		"""
		����Ʒת��Ϊ������ʽ���ַ�����ת��Ϊ RichTextBox/MLRichTextBox ���ص��ı���
		���践��һ���ַ���
		"""
		itemInfo = item.id, item.extra
		return ChatObjParser.maskObj( self.objType, itemInfo )

	def getViewName( self, text ) :
		"""
		��������ʽ���������ת��Ϊ�û���ʽ���������ת��Ϊ RichTextBox/MLRichTextBox ��ʾ���ı���
		���践�� None�� ���ַ�������ɫ��
		"""
		item = self.__getItem( text )
		if item is None : return None
		vname = ChatObjParser.viewObj( item.fullName() )
		color = item.getQualityColor()
		return vname, color


# -----------------------------------------------------
# ���Ӷ���
# -----------------------------------------------------
class LItem( BaseObj ) :
	LMARK = "chat_item:"

	def __init__( self ) :
		objType = chatObjTypes.LINK
		minLen = 9
		defName = lbs_ChatFacade.unknowItem
		BaseObj.__init__( self, objType, minLen, defName )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def dump( self, text ) :
		"""
		���һ��������Ϊ����������͵���Ʒ��ת��Ϊ���Ͳ�����BLOB��
		���践�� BLOB �� None
		"""		
		info = text
		return ChatObjParser.dumpObj( self.objType, info )

	def load( self, info ) :
		"""
		�����յ���Ƶ����Ϣ����ת��Ϊ�ɶ��ı���ת��Ϊ RichText ʶ����ַ�����
		���践��һ���ַ���
		"""
		id, extra = eval( info )
		name = extra["name"]
		linkMark = extra["linkMark"]
		cfc = extra["cfc"]
		hfc = extra["hfc"]
		return chatObjParsers.plnRTLink.getSource( name , linkMark, cfc = cfc, hfc = hfc )

	# ------------------------------------------------------------
	def getMaskText( self, item ) :
		"""
		����Ʒת��Ϊ������ʽ���ַ�����ת��Ϊ RichTextBox/MLRichTextBox ���ص��ı���
		���践��һ���ַ���
		"""
		itemInfo = ( item.id,{"name":item.name, "linkMark":item.linkMark, "cfc":item.cfc, "hfc":item.hfc} )
		return ChatObjParser.maskObj( self.objType, itemInfo )

	def getViewName( self, text ) :
		"""
		��������ʽ���������ת��Ϊ�û���ʽ���������ת��Ϊ RichTextBox/MLRichTextBox ��ʾ���ı���
		���践�� None�� ���ַ�������ɫ��
		"""
		if len( text ) < self.minLen_ : return None
		id, extra = eval( text )
		name = extra["name"]
		cfc =extra["cfc"]
		return name, cfc


# --------------------------------------------------------------------
# ������������
# --------------------------------------------------------------------
class ObjParsers( Singleton ) :
	def __init__( self ) :
		self.parsers = {
			chatObjTypes.ITEM : ChatItem(),
			chatObjTypes.LINK : LItem(),
			}

		self.plnRTLink = None
		self.__objTpl = re.compile( "\$\{o\d+\}" )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def reTpl( self ) :
		return ChatObjParser.g_reObjTpl


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onGameStart( self ) :
		self.plnRTLink = smartImport( "guis.tooluis.richtext_plugins.PL_Link:PL_Link" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getMaskObj( self, objType, obj ) :
		"""
		���������ת��Ϊ RichTextBox/MLRichTextBox ���ص��ı�
		"""
		return self.parsers[objType].getMaskText( obj )

	def getViewObj( self, text ) :
		"""
		���ݰ�����ʽ�Ķ����ı�����ȡ�ɸ��û����� RichTextBox/MLRichTextBox ��ʾ��������������
		"""
		ms = ChatObjParser.getObjMatchs( text )
		if len( ms ) != 1 : return None
		strObj, objType = ms[0].groups()
		parser = self.parsers.get( int( objType ), None )
		if parser is None : return None
		return parser.getViewName( strObj )

	# -------------------------------------------------
	def parseSendMsg( self, msg ) :
		"""
		���ͽ�Ҫ���͵���Ϣ
		@type			msg : str
		@param			msg : Ҫ���͵���Ϣ
		@rtype				: tuple: ( str, str of blob )
		@return				: ����Ϣ�ֽ�Ϊ������Ϣ����Ϣ���������Ϣ
		"""
		sendMsg = ""
		dobjs = []
		parsers = self.parsers
		ms = ChatObjParser.getObjMatchs( msg )				# ��ȡ���ж���� re::Match
		start = 0
		for m in ms :
			end = m.end()
			strObj, objType = m.groups()					# ( �������, ������������ )
			parser = parsers.get( int( objType ), None )	# ��ȡ��Ӧ���������Ľ�����
			if parser is None :								# ����Ҳ�����Ӧ�Ľ�����
				sendMsg += msg[start:end]					# ��ԭ���ı�����
			else :
				dobj = parser.dump( strObj )				# ��������������д��
				if dobj :
					objMark = "${o%i}" % len( dobjs )
					sendMsg += msg[start:m.start()] + objMark
					dobjs.append( dobj )
				else :
					sendMsg += msg[start:end]
			start = end
		sendMsg += msg[start:]
		return sendMsg, dobjs

	# ---------------------------------------
	def tearRcvMsg( self, msg, blobArgs ) :
		"""
		������Ϣת�壬�������ͺ����Ϣ���ֶη��أ��Ӷ���ǳ��Ķ�Ϊ�����������ı����Ķ�����ͨ�ı�:
		[( True, @I{...} ), ( False, "xxxx" ), ( False "xxxx" ), ...]
		"""
		emsgs = []
		start = 0
		end = len( msg )
		emIter = self.__objTpl.finditer( msg )						# ��ȡ������Ϣ�ֶεĵ�����
		while True :
			try :
				em = emIter.next()
				eStart = em.start()
				if start != eStart :
					emsgs.append( ( False, msg[start:eStart] ) )	# ��ͨ��Ϣ
				emsgs.append( ( True, em.group() ) )
				start = em.end()
			except StopIteration :
				break
		if start != end :
			emsgs.append( ( False, msg[start:end] ) )				# ʣ��ķǱ�����Ϣ
		return emsgs

	def calcObjAmount( self, text ) :
		"""
		�����ı�����������������
		"""
		return len( ChatObjParser.getObjMatchs( text ) )

	def parseRcvMsg( self, msg, blobArgs ) :
		"""
		���ͽ��յ�����Ϣ
		@type			msg		 : str
		@param			msg		 : ���յ�����Ϣ
		@type			blobArgs : BLOB_ARRAY
		@param			blobArgs : ��������Ʒ�б��ԡ�[( id, extra ), ( id, extra ), ...]������ cPickle
		@rtype					 : str
		@param					 : ���ؽ�������Ϣ
		"""
		args = {}
		for idx, blobObj in enumerate( blobArgs ) :
			viewText = " "
			try :
				objType, obj = cPickle.loads( blobObj )
			except err :
				ERROR_MSG( err )
			else :
				parser = self.parsers.get( objType, None )
				if parser is None :
					ERROR_MSG( "chat object '%i' is not exist!" % objType )
					viewText = str( objType )
				else :
					viewText = parser.load( obj )
			args["o%i" % idx] = viewText
		return string.Template( msg ).safe_substitute( args )


class MessageInserter( Singleton ) :

	def __init__( self ) :
		self.__pyCurInputObj = None						# ��ǰ����Ϣ������ն���
		self.__pyDefInputObj = None						# Ĭ�ϵ���Ϣ������ն���


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onInputObjTabIn( self, pyInputObj ) :
		"""
		ĳ��������ý���
		"""
		self.__pyCurInputObj = weakref.ref( pyInputObj )

	def __onInputObjTabOut( self, pyInputObj ) :
		"""
		ĳ�������ʧȥ����
		"""
		if BigWorld.isKeyDown( keys.KEY_LCONTROL ) or \
			BigWorld.isKeyDown( keys.KEY_RCONTROL ) :	# �����ǰ���Ctrl�����򲻳���
				return									# ��ǰ����Ϣ����ؼ�
		self.__pyCurInputObj = None


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setDefInputObj( self, pyDefInputObj ) :
		"""
		����Ĭ�ϵ���Ϣ������ն���
		"""
		if pyDefInputObj is not None :
			self.__pyDefInputObj = weakref.ref( pyDefInputObj )
			self.registerInputObj( pyDefInputObj )
		else :
			if self.__pyDefInputObj :
				pyDefInputObj = self.__pyDefInputObj()
				if pyDefInputObj :
					self.disregisterInputObj( pyDefInputObj )
			self.__pyDefInputObj = None

	def registerInputObj( self, pyInputObj ) :
		"""
		��ӽ�����Ϣ����Ķ���
		ע�⣬pyInputObjһ��Ҫ��notifyInput������
		"""
		pyInputObj.onTabIn.bind( self.__onInputObjTabIn )
		pyInputObj.onTabOut.bind( self.__onInputObjTabOut )

	def disregisterInputObj( self, pyInputObj ) :
		"""
		�Ƴ�������Ϣ����Ķ���
		"""
		pyInputObj.onTabIn.unbind( self.__onInputObjTabIn )
		pyInputObj.onTabOut.unbind( self.__onInputObjTabOut )

	# -------------------------------------------------
	def insertMessage( self, msg ) :
		"""
		����һ����Ϣ
		"""
		pyPotentate = None
		if self.__pyCurInputObj is None :
			if self.__pyDefInputObj is None : return
			pyPotentate = self.__pyDefInputObj()
		else :
			pyPotentate = self.__pyCurInputObj()
			if pyPotentate is None :
				if self.__pyDefInputObj is None : return
				pyPotentate = self.__pyDefInputObj()

		if pyPotentate is not None :
			pyPotentate.notifyInput( msg )

# --------------------------------------------------------------------
# global instances
# --------------------------------------------------------------------
chatObjTypes = ChatObjParser.ObjTypes		# ���ж�������
chatFacade = ChatFacade()					# ���� Facade ��
emotionParser = EmotionParser()				# ���������
chatObjParsers = ObjParsers()				# �������ӽ�����
msgInserter = MessageInserter()				# ��Ϣ������
