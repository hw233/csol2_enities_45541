# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.17 2008-08-30 09:03:04 huangyongwei Exp $
"""
implement chat system

09/05/2005 : created by phw
11/28/2006 : modified by huangyongwei
"""

import time
import struct
import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
import wizCommand
from MsgLogger import g_logger


# --------------------------------------------------------------------
# implement channels
# --------------------------------------------------------------------
class Channel( object ) :
	def __init__( self, id ) :
		self.id = id										# Ƶ�� ID

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		virtual method
		����Ƶ����Ϣ
		"""
		raise TypeError( "channel '%s' must implement method 'handle'" % self.__class__.__name__ )

# -----------------------------------------------------
class CHN_Near( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		����Ƶ����Ϣ
		"""
		speaker.planesAllClients( "chat_onChannelMessage", ( csdefine.CHAT_CHANNEL_NEAR, speaker.id, speaker.getName(), msg, blobArgs ) )

# -------------------------------------------
class CHN_World( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		����Ƶ����Ϣ
		"""
		if speaker.iskitbagsLocked():	# ����������by����
			speaker.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		if speaker.level < csconst.CHAT_YELL_LEVEL_REQUIRE :
			speaker.statusMessage( csstatus.CHAT_YELL_MONEY_NOTENOUGH )
		elif speaker.queryTemp( "chat_last_yell_time", 0 ) + csconst.CHAT_YELL_DELAY > time.time() :
			speaker.statusMessage( csstatus.CHAT_YELL_TOO_CLOSE )
		elif speaker.payMoney( csconst.CHAT_YELL_USE_MONEY, csdefine.CHANGE_MONEY_CHAT_YELL ) :
			speaker.base.chat_handleMessage( csdefine.CHAT_CHANNEL_WORLD, "", msg, blobArgs )
			speaker.setTemp( "chat_last_yell_time", time.time() )
		else :
			speaker.statusMessage( csstatus.CHAT_YELL_MONEY_NOTENOUGH )

# -------------------------------------------
class CHN_Rumor( Channel ) :
	"""
	ҥ��
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		����Ƶ����Ϣ
		"""
		now = time.time()
		lastTime = speaker.queryTemp( "chat_last_rumor_time", 0 )			# �ϴη���ҥ�Ե�ʱ��
		if lastTime + csconst.CHAT_RUMOR_DELAY > now :						# ��û������ʱ��
			speaker.statusMessage( csstatus.CHAT_RUMOR_TOO_CLOSE )
			return
		wasteMP = int( csconst.CHAT_RUMOR_MP_DECREMENT * speaker.MP_Max )	# MP ���ֵ
		if speaker.MP < wasteMP :											# ��ǰ MP ����
			speaker.statusMessage( csstatus.CHAT_RUMOR_MP_NOT_ENOUGH )
			return
		speaker.setTemp( "chat_last_rumor_time", now )						# ��¼�±��η���ʱ��
		speaker.addMP( -wasteMP )											# ��� MP
		speaker.base.chat_handleMessage( self.id, "", msg, blobArgs )		# �� base �й㲥ҥ��
		try:
			g_logger.sendRumorLog( speaker.databaseID, speaker.getName(), msg )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

# -------------------------------------------
class CHN_Welkin( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		����Ƶ����Ϣ
		"""
		if speaker.iskitbagsLocked():	# ����������by����
			speaker.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		welkinItemID = csconst.CHAT_WELKIN_ITEM
		welkinItem = speaker.findItemFromNKCK_( welkinItemID )							# ���ұ������Ƿ���������
		if welkinItem :
			speaker.removeItem_( welkinItem.order, 1, csdefine.DELETE_ITEM_WELKINYELL )	# ������ڱ������ҵ�����������ɾ��һ��������
			speaker.base.chat_handleMessage( self.id, "", msg, blobArgs )
		else :																			# ���������û��������
			speaker.base.spe_onAutoUseYell( welkinItemID, csdefine.SPECIALSHOP_MONEY_TYPE_GOLD, msg, blobArgs )

# -------------------------------------------
class CHN_Tunnel( Channel ) :
	"""
	����
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		����Ƶ����Ϣ
		"""
		if speaker.iskitbagsLocked():	# ����������by����
			speaker.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		tunnelItemID = csconst.CHAT_TUNNEL_ITEM
		tunnelItem = speaker.findItemFromNKCK_( tunnelItemID )							# ���ұ������Ƿ��е�����
		if tunnelItem is None:	# �����Žǵ��۵ظ������Ʒ�� �������԰󶨰�Ĵ��� by����
			tunnelItemID = csconst.CHAT_TUNNEL_ITEM_BINDED
			tunnelItem = speaker.findItemFromNKCK_( tunnelItemID )
		if tunnelItem :
			speaker.removeItem_( tunnelItem.order, 1, csdefine.DELETE_ITEM_TUNNELYELL )	# ������ڱ������ҵ�����������ɾ��һ��������
			speaker.base.chat_handleMessage( self.id, "", msg, blobArgs )
		else :																			# ���������û�е�����
			tunnelItemID = csconst.CHAT_TUNNEL_ITEM
			speaker.base.spe_onAutoUseYell( tunnelItemID, csdefine.SPECIALSHOP_MONEY_TYPE_SILVER, msg, blobArgs )

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
		spaceBase = speaker.getCurrentSpaceBase()
		spaceBase.onChatChannelMessage( self.id, speaker.id, speaker.getName(), msg, blobArgs )


# -------------------------------------------
class CHN_Camp( Channel ) :
	"""
	��Ӫ
	"""
	def __init__( self, id ) :
		Channel.__init__( self, id )

	def handle( self, speaker, rcvName, msg, blobArgs ) :
		"""
		����Ƶ����Ϣ
		"""
		if speaker.queryTemp( "chat_last_camp_time", 0 ) + csconst.CHAT_CMAP_DELAY > time.time() :
			speaker.statusMessage( csstatus.CHAT_SPEAK_TOO_CLOSE )
		else:
			speaker.base.chat_handleMessage( csdefine.CHAT_CHANNEL_CAMP, "", msg, blobArgs )
			speaker.setTemp( "chat_last_camp_time", time.time() )
			
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
		tong_grade = speaker.tong_grade
		tong_dbID = speaker.tong_dbID
		if speaker.getCurrentSpaceType() == csdefine.SPACE_TYPE_CITY_WAR_FINAL and tong_grade in csdefine.TONG_CITY_WAR_SPEAK:
			# �㲥��ҵķ������ݵ�ͬ�˳�Ա�� client
			BigWorld.globalData[ "TongManager" ].sendMessage2Alliance( tong_dbID, speaker.id, speaker.getName(), msg, blobArgs )

# -----------------------------------------------------
_channel_maps = {
	csdefine.CHAT_CHANNEL_NEAR			: CHN_Near,				# ���������̣�base->cell��
	csdefine.CHAT_CHANNEL_LOCAL			: CHN_Local,			# ���أ����̣�base->cell��
	csdefine.CHAT_CHANNEL_WORLD			: CHN_World,			# ���磨���̣�base->cell->base��
	csdefine.CHAT_CHANNEL_RUMOR			: CHN_Rumor,			# ҥ�ԣ����̣�base->cell->base��
	csdefine.CHAT_CHANNEL_WELKIN_YELL	: CHN_Welkin,			# ���������̣�base->cell->base��
	csdefine.CHAT_CHANNEL_TUNNEL_YELL	: CHN_Tunnel,			# ���������̣�base->cell->base��
	csdefine.CHAT_CHANNEL_CAMP			: CHN_Camp,				# ��Ӫ�����̣�base->cell->base��
	csdefine.CHAT_CHANNEL_TONG_CITY_WAR : CHN_TongCityWar,		# ��ս �����̣�base-->cell-->TongCityWarFialManger-->ͬ�˳�Աclient��
	}

_channels = {}													# ����Ƶ���б�
for channelID, CLSCannel in _channel_maps.iteritems() :
	_channels[channelID] = CLSCannel( channelID )
del _channel_maps


# --------------------------------------------------------------------
# implement chat system for role inheriting
# �ر����ѣ�
#	�����Ƶ�������н�ɫ���õģ��벻Ҫ��Ƶ���ж����ɫ��صĳ�Ա����
# --------------------------------------------------------------------
class RoleChat :
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# defined mehods.
	# ----------------------------------------------------------------
	def chat_handleMessage( self, channelID, rcvName, msg, blobArgs ) :
		"""
		defined method
		����һ��Ƶ����Ϣ�����Ը����� base �� cell ����
		@type				channelID : UINT32
		@param				channelID : Ƶ�� ID
		@type				rcvName	  : STRING
		@param				rcvName	  : ��Ϣ�����ߵ�����
		@type				msg		  : STRING
		@param				msg		  : ��Ϣ����
		@type				blobArgs  : BLOB_ARRAY
		@param				blobArgs  : ��Ϣ�����б�
		"""
		_channels[channelID].handle( self, rcvName, msg, blobArgs )

	# -------------------------------------------------
	def chat_sendRoleInfo( self, mbBase ) :
		"""
		defined method
		���ͽ�ɫ��Ϣ��ָ���ͻ���( hyw -- 2008.08.29 )
		@type				mbBase : MAILBOX
		@param				mbBase : Ҫ���͵��Ŀͻ��˶�Ӧ�� base mailbox
		"""
		if hasattr( mbBase, "client" ) :
			roleInfo = {}
			roleInfo["name"] = self.getName()
			roleInfo["level"] = self.level
			roleInfo["tong"] = self.tongName
			roleInfo["spaceLabel"] = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			mbBase.client.chat_onReceiveRoleInfo( roleInfo )
	
	def chat_switchFengQi( self, srcEntityID, unLocked ):
		"""
		/Exposed method
		����ҹս���������
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.onFengQi:
			return
		wizCommand.wizCommand( self, self.id, "switchFengQi", "%d"%int( unLocked ) )
	
	def chat_onSwitchFengQi( self, unLocked ):
		"""
		GM���ûص�
		"""
		self.client.chat_onSwitchFengQi( unLocked )

# RoleChat.py
