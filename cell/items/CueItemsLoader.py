# -*- coding: gb18030 -*-

from bwdebug import *
import Language
from config.item import CueItems
import ItemTypeEnum
import cschannel_msgs
import random
from config.itemBCSpecialMsgConfig import Datas as itemBCMsg

specialMsgMap = {
	# ��Ʒ��ȡ��ʾ ���ղ߻����� ��ΪList ���Ҹ����ַ������� ����_��Ϊ�ض����� by����
	"BCT_ITEM_GET_PICK_NOTIFY"					: 1,
	"BCT_ITEM_GET_CARD_NOTIFY"				: 2,
	"BCT_ITEM_GET_NPCTRADE_NOTIFY"			: 3,
	"BCT_ITEM_GET_SHOP_NOTIFY"				: 4,
	"BCT_ITEM_GET_TRADE_NOTIFY"				: 5,
	"BCT_ITEM_GET_QUEST_NOTIFY"				: 6,
	"BCT_ITEM_GET_STROE_NOTIFY"				: 7,
	"BCT_ITEM_GET_NPCGIVE_NOTIFY"			: 8,

	# װ��ǿ����ʾ ����һ��ǿ���ȼ����� by����
	# $p:���  $a:�ص�  $m:����  $i:��Ʒ $n:����  $c:�  $g��NPC  $t:ǿ��/��Ƕ��Ŀ����Ʒ $q:ǿ���ȼ� $s:��Ƕ����
	"BCT_ITEM_GET_EQUIP_INSTENSIFY_NOTIFY"	: 9,
	"BCT_ITEM_GET_STUD_NOTIFY"				: 10,
	# $p:��� $b:�����ھ� $o:�Է��ھ�
	# ��������ɹ� by����
	"BCT_DARTSUCCESS_NOTIFY"					: 11,
	# ��������ɹ� by����
	"BCT_ROBSUCCESS_NOTIFY"					: 12,
}

class CueItemsLoader:
	"""
	��ʾ��Ʒ���ü���
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert CueItemsLoader._instance is None, "instance already exist in"
		self._datas = CueItems.Datas	# like as { itemID : {"pickCue", 1,  ......}, ...}
		self._maps = {
						"pickCue"	:	ItemTypeEnum.ITEM_GET_PICK,
						"cardCue"	:	ItemTypeEnum.ITEM_GET_CARD,
						"npcTradeCue"	:	ItemTypeEnum.ITEM_GET_NPCTRADE,
						"shopCue"	:	ItemTypeEnum.ITEM_GET_SHOP,
						"pTradeCue"	:	ItemTypeEnum.ITEM_GET_PTRADE,
						"questCue"	:	ItemTypeEnum.ITEM_GET_QUEST,
						"stroeHorseCue"	:	ItemTypeEnum.ITEM_GET_STROE,
						"npcGiveCue"	:	ItemTypeEnum.ITEM_GET_NPCGIVE,
						"equInstCue"	:	ItemTypeEnum.ITEM_GET_EQUIP_INSTENSIFY,
						"equStud"	:	ItemTypeEnum.ITEM_GET_STUD,
						}
		self._cueMaps = {
						ItemTypeEnum.ITEM_GET_PICK		:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_PICK_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_CARD		:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_CARD_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_NPCTRADE	:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_NPCTRADE_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_SHOP		:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_SHOP_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_PTRADE	:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_TRADE_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_QUEST		:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_QUEST_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_STROE		:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_STROE_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_NPCGIVE	:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_NPCGIVE_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_EQUIP_INSTENSIFY	:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_EQUIP_INSTENSIFY_NOTIFY"]],
						ItemTypeEnum.ITEM_GET_STUD		:	itemBCMsg[specialMsgMap["BCT_ITEM_GET_STUD_NOTIFY"]],
						}

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = CueItemsLoader()
		return self._instance

	def hasCueFlag( self, itemID, addType ):
		"""
		�ж���ƷID�Ƿ���addType�ı�־
		@param itemID	: ��ƷID
		@type  itemID	: INT32
		@param addType	: Flag
		@type  addType	: UINT8
		@return True/False
		"""
		if itemID not in self._datas: return False
		return addType in self._datas[itemID]

	def getCueMsg( self, addType ):
		"""
		��ȡaddType��Ӧ����ʾ��Ϣ
		@param addType	: Flag
		@type  addType	: UINT8
		@return STRING
		"""
		if addType not in self._cueMaps: return None
		return random.choice( self._cueMaps[addType] )
		
	def getDartCueMsg( self, msgType ):
		"""
		��ȡ������صĹ㲥��Ϣ
		@param msgType	: Flag
		@type  msgType	: UINT8
		@return STRING
		"""
		if itemBCMsg.has_key( msgType ):
			return random.choice( itemBCMsg[msgType] )
		return ""
		
	def getCueMsgString( self, **msgKeys ):
		"""
		�߻�����Ķ� �㲥������֯��ʽ������������
		"""
		msg = msgKeys["_keyMsg"]
		if msg is None:
			return ""
		for key in msgKeys:
			if msgKeys[key] is None: continue
			if msg.find( key ) < 0: continue
			msg = msg.replace( key, msgKeys[key] )
		return msg

	def isPickCue( self, itemID ):
		"""
		�Ƿ�ʰȡ��ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["pickCue"] in self._datas[itemID]

	def isCardCue( self, itemID ):
		"""
		�Ƿ񿪽�����ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["cardCue"] in self._datas[itemID]

	def isNpcTradeCue( self, itemID ):
		"""
		�Ƿ�NPC������ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["npcTradeCue"] in self._datas[itemID]

	def isShopCue( self, itemID ):
		"""
		�Ƿ��̳ǹ�����ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["shopCue"] in self._datas[itemID]

	def isPTradeCue( self, itemID ):
		"""
		�Ƿ���ҽ�����ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["pTradeCue"] in self._datas[itemID]

	def isQuestCue( self, itemID ):
		"""
		�Ƿ���������ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["questCue"] in self._datas[itemID]

	def isStroeHorseCue( self, itemID ):
		"""
		�Ƿ񿪱�����ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["stroeHorseCue"] in self._datas[itemID]

	def isNpcGiveCue( self, itemID ):
		"""
		�Ƿ�NPC������ʾ
		"""
		if itemID not in self._datas: return False
		return self._maps["npcGiveCue"] in self._datas[itemID]

	def reset( self ):
		"""
		���¼�������
		"""
		self._datas = {}
		reload( CueItems )
		self._datas = CueItems.Datas
