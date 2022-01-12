# -*- coding: gb18030 -*-

# $Id: csstatus_msgs.py,v 1.273 2008-09-05 09:26:11 yangkai Exp $

"""
locates global macros feedback from cell or base to client

2005.06.15 = designed by huangyongwei
"""

import re
import csdefine
import csconst
import csstatus
from bwdebug import *
from csstatus import *
from config.csstatusMsgs import Datas

# --------------------------------------------------------------------
#ԭcsstatus.py
# ID �÷���
#		�� ID Ϊ 4 λʮ�����ƣ��� 16 λ�����Ʊ�ʾ����
#		�� ID �����ظ���
#		�� ID ��ʮ�����Ƹ���λ��ʾ��Ϣ��ʾ�����ÿ����һ�������ֵ���� 1�����֧�� 128 �ࣩ��
#		�� ID ��ʮ�����Ƶ���λ������Ϣ��ʾ������ã����������� 128 ����Ϣ ID����
#		�� ����ڵ���Ϣ ID Ҫ���������ص�ǰ׺��������Ϣ ID �ظ����塣
#		�� ÿ�����֮����������#--------���ָ��߸������ָ���֮��д�����ע�͡�
#		�� ����ھ�����Ҫ���� 128 ����Ϣ ID �Ӷ�ʹ�� ID ��Ҫ�����������
#		  ����ǿ�ƣ������� ID ����ľ������Բ��Ϊ������ȷʵ���ܲ��ʱҲ���������������һ��
#		�� ÿ�������һ���С�
#		�� ����ڵ� ID �������з����࣬�ӷ���֮���ÿո�ֿ����������������ǰ����ע�ͣ�
#		   �����á�#--------���ָ��������������
#
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# ϵͳƵ��ǰ׺ӳ��
# Ƶ��ǰ׺˵����
#	�� ʹ�÷���
#	�������ָ�� statusMessage �������κ�һ������Ƶ������ʾ��
#	ָ�������ǣ�����Ϣ��ǰ�����Ƶ��ǰ׺��
#	ǰ׺��ʽ�ǣ�
#		"(Ƶ��ǰ׺1,Ƶ��ǰ׺2):��Ϣ����"
#	���磺
#		_svrStatusMsgs[GB_INVALID_CALLER] = "(SY,SC):�����ǺϷ��Ĳ���Ա��"
#	�������ʾ����Ϣ����ͬʱ�ڡ�ϵͳ���͡���Ļ���롱Ƶ����ʾ��
#
#	�� ����Ƶ��ǰ׺����Ϣ
#	���ĳЩ��Ϣ����Ƶ��ǰ׺�����Ĭ���ڸ���Ƶ����PA����ʾ��
#	������Ƶ��ǰ׺�����û�С�PA��ǰ׺���������ڸ���Ƶ����ʾ��
#
#	�� ��ӷ�����
#	���Զ� statusMessage ��ӷ����ߣ�������һ���ǡ�ϵͳ����
#	�����Ƶ��ǰ׺�м���ǰ׺�б��в����ڵ��ַ���������ַ�������Ϊ�Ƿ�����
#	�磺
#		_svrStatusMsgs[GB_INVALID_CALLER] = "(SY,SC,ϵͳ):�����ǺϷ��Ĳ���Ա��"
#	�����ϵͳ���������ֱ���Ϊ�Ƿ��������ơ�
# --------------------------------------------------------------------
_prefix_channels = {
	# ��ɫ����Ƶ��
	"NE" : csdefine.CHAT_CHANNEL_NEAR,				# ����Ƶ��
	"LO" : csdefine.CHAT_CHANNEL_LOCAL,				# ����Ƶ��
	"TM" : csdefine.CHAT_CHANNEL_TEAM,				# ����Ƶ��
	"FM" : csdefine.CHAT_CHANNEL_FAMILY,			# ����Ƶ��
	"TG" : csdefine.CHAT_CHANNEL_TONG,				# ���Ƶ��
	"WP" : csdefine.CHAT_CHANNEL_WHISPER,			# ˽��Ƶ��
	"WD" : csdefine.CHAT_CHANNEL_WORLD,				# ����Ƶ��
	"RM" : csdefine.CHAT_CHANNEL_RUMOR,				# ҥ��Ƶ��
	"WY" : csdefine.CHAT_CHANNEL_WELKIN_YELL,		# �����㲥
	"TY" : csdefine.CHAT_CHANNEL_TUNNEL_YELL,		# �����㲥

	# GM/����Ƶ��
	"BR" : csdefine.CHAT_CHANNEL_SYSBROADCAST,		# GM/ϵͳ�㲥

	# NPC ����Ƶ��
	"NS" : csdefine.CHAT_CHANNEL_NPC_SPEAK,			# NPC ����Ƶ��
	"NT" : csdefine.CHAT_CHANNEL_NPC_TALK,			# NPC �Ի�Ƶ��

	# ϵͳ��ʾƵ��
	"SY" : csdefine.CHAT_CHANNEL_SYSTEM,			# ϵͳƵ������ʾ�ɷ����������ĸ��ֻ�������Ʒ/ǿ��/��Ƕ�Ȳ�����
	"CB" : csdefine.CHAT_CHANNEL_COMBAT,			# ս��Ƶ������ʾս����Ϣ��
	"PA" : csdefine.CHAT_CHANNEL_PERSONAL,			# ����Ƶ��������Ƶ����ʾ����ڻ�þ��顢Ǳ�ܡ���Ǯ����Ʒ��Ԫ������Ϣ��
	"MG" : csdefine.CHAT_CHANNEL_MESSAGE,			# ��ϢƵ������ʾ��ɫ�Ĳ��������Ĵ�����Ϣ����ʾ��Ϣ��
	"SC" : csdefine.CHAT_CHANNEL_SC_HINT,			# ����Ļ�м���ʾ��Ƶ��
	"MB" : csdefine.CHAT_CHANNEL_MSGBOX,			# �� MessageBox ��ʾ��Ƶ��
	}

# -------------------------------------------
_ch_prefies = set( _prefix_channels.keys() )				# ����Ƶ��ǰ׺��
_chpfxSplitter = re.compile( "(?<=^\().+(?=\):)" )			# ����Ƶ��ǰ׺������ģ��

class MSGInfo( object ) :									# ��Ϣ��װ
	__slots__ = ["chids", "spkName", "msg"]
	def __init__( self, chs, sk, msg ) :
		self.chids = chs									# Ƶ���б�
		self.spkName = sk									# ������
		self.msg = msg										# ��Ϣ����

def getMSGInfo( msg ) :
	"""
	��ȡƵ��ǰ׺�б�
	"""
	chs = []
	spkName = ""
	match = _chpfxSplitter.search( msg )					# ����Ƶ��ǰ׺
	if match :
		prefies = match.group().split( "," )				# �������Ƶ��ǰ׺
		for prefix in prefies :
			prefix = prefix.strip()
			ch = _prefix_channels.get( prefix, None )		# ��ȡ��Ӧ��Ƶ��
			if ch :
				chs.append( ch )							# �����Ƶ��ǰ׺�б��У�����Ϊ��Ƶ��
			else :
				spkName = prefix							# �������Ƶ��ǰ׺�б��У�����Ϊ�Ƿ���������
		msg = msg[match.end() + 2:]							# �򣬷���Ƶ��ǰ׺����Ϣ
	if not chs and msg != "" :								# ����Ϣ����ӵ��κ�Ƶ��
		chs = [csdefine.CHAT_CHANNEL_PERSONAL]				# ������û��Ƶ��ǰ׺���򷵻ء����ˡ�Ƶ��
	return MSGInfo( chs, spkName, msg )


# --------------------------------------------------------------------
# global status
# --------------------------------------------------------------------
_svrStatusMsgs = {}

for id, msg in Datas.iteritems() :
	_svrStatusMsgs[id] = getMSGInfo( msg )


# --------------------------------------------------------------------
# reference method
# --------------------------------------------------------------------
def getStatusInfo( statusID, *args ) :
	"""
	����ָ�� ID ��״̬��Ϣ,���ڽ���ʧ�ܵ���Ϣ,��� debug ��Ϣ
	@type			statusID : INT32
	@param			statusID : status id defined in common/csstatus.py
	@type			args	 : all types
	@param			args	 : multi arguments
	@rtype					 : MSGInfo
	@return					 : status_msgs.MSGInfo
	"""
	msgInfo = _svrStatusMsgs.get( statusID, None )
	if msgInfo is None :													# ��Ϣû�б�����
		msgInfo = MSGInfo( [csdefine.CHAT_CHANNEL_PERSONAL], "", "" )
		ERROR_MSG( "undefined status message: %#x" % statusID )
	msg = msgInfo.msg
	try :
		msg = msgInfo.msg % args
	except :
		EXCEHOOK_MSG( "error status: '%#x'" % statusID )
	return MSGInfo( msgInfo.chids, msgInfo.spkName, msg )

def getStatusPrefix( statusID ) :
	"""
	get status name's prefix
	@type			statusID : INT32
	@param			statusID : status id defined in common/csstatus.py
	@rtype					 : str
	@return					 : prefix of the status name defined in common/csstatus.py
	"""
	for name in dir( csstatus ):
		value = getattr( csstatus, name )
		if value == statusID :
			return name.split( "_" )[0]
	return None


# --------------------------------------------------------------------
# ���������������Ϊ�Ƿ���ʾ����Ϣ
# --------------------------------------------------------------------
# ����������Ϣ
enemyInjuredStatus = set( [
	SKILL_SPELL_RESIST_HIT_FROM_SKILL,				SKILL_SPELL_DOUBLEDAMAGE_TO,				SKILL_BUFF_REBOUND_MAGIC_TO,
	SKILL_BUFF_REBOUND_PHY_TO,						SKILL_SPELL_DAMAGE_TO,
	SKILL_SPELL_DODGE_FROM_SKILL,					SKILL_SPELL_PET_RESIST_HIT_FROM_SKILL,		SKILL_SPELL_PET_DOUBLEDAMAGE_TO,
	SKILL_SPELL_PET_DAMAGE_TO,						SKILL_SPELL_PET_NO_HIT_TO,					SKILL_SPELL_PET_DODGE_TO,
	] )

# ���ܹ�����Ϣ
skillHitStatus = set( [
	SKILL_SPELL_DODGE_TO_SKILL,
	SKILL_SPELL_DODGE_TO,
	] )

# �ظ���Ϣ
revertStatus = set( [
	] )

# ������Ϣ
injuerdStatus = set( [
	SKILL_SPELL_RESIST_HIT_TO,					SKILL_SPELL_DOUBLEDAMAGE_FROM_SKILL,			SKILL_BUFF_REBOUND_MAGIC,
	SKILL_BUFF_REBOUND_PHY,						SKILL_SPELL_DAMAGE_FROM_SKILL,					SKILL_SPELL_RESIST_HIT_FROM,
	SKILL_SPELL_DOUBLEDAMAGE_FROM,				SKILL_SPELL_DAMAGE_FROM,						SKILL_SPELL_RESIST_HIT_TO_DOUBLEDAMAGE,
	] )

# buff ��Ϣ
buffStatus = set( [
	csstatus.ACCOUNT_STATE_REV_BUFF,
	] )


# --------------------------------------------------------------------
# ��ɫ���Ա����Ϣ
# --------------------------------------------------------------------
