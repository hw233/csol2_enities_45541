# -*- coding: gb18030 -*-

from bwdebug import *
import Language
from config.item import CueItems
import ItemTypeEnum
import cschannel_msgs
import random
from config.itemBCSpecialMsgConfig import Datas as itemBCMsg

specialMsgMap = {
	# 物品获取提示 按照策划需求 改为List 并且根据字符串需求 改用_作为特定符合 by姜毅
	"BCT_ITEM_GET_PICK_NOTIFY"					: 1,
	"BCT_ITEM_GET_CARD_NOTIFY"				: 2,
	"BCT_ITEM_GET_NPCTRADE_NOTIFY"			: 3,
	"BCT_ITEM_GET_SHOP_NOTIFY"				: 4,
	"BCT_ITEM_GET_TRADE_NOTIFY"				: 5,
	"BCT_ITEM_GET_QUEST_NOTIFY"				: 6,
	"BCT_ITEM_GET_STROE_NOTIFY"				: 7,
	"BCT_ITEM_GET_NPCGIVE_NOTIFY"			: 8,

	# 装备强化提示 到达一定强化等级出现 by姜毅
	# $p:玩家  $a:地点  $m:怪物  $i:物品 $n:数量  $c:活动  $g：NPC  $t:强化/镶嵌的目标物品 $q:强化等级 $s:镶嵌材料
	"BCT_ITEM_GET_EQUIP_INSTENSIFY_NOTIFY"	: 9,
	"BCT_ITEM_GET_STUD_NOTIFY"				: 10,
	# $p:玩家 $b:己方镖局 $o:对方镖局
	# 运镖任务成功 by姜毅
	"BCT_DARTSUCCESS_NOTIFY"					: 11,
	# 劫镖任务成功 by姜毅
	"BCT_ROBSUCCESS_NOTIFY"					: 12,
}

class CueItemsLoader:
	"""
	提示物品配置加载
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
		判断物品ID是否有addType的标志
		@param itemID	: 物品ID
		@type  itemID	: INT32
		@param addType	: Flag
		@type  addType	: UINT8
		@return True/False
		"""
		if itemID not in self._datas: return False
		return addType in self._datas[itemID]

	def getCueMsg( self, addType ):
		"""
		获取addType对应的提示信息
		@param addType	: Flag
		@type  addType	: UINT8
		@return STRING
		"""
		if addType not in self._cueMaps: return None
		return random.choice( self._cueMaps[addType] )
		
	def getDartCueMsg( self, msgType ):
		"""
		获取运镖相关的广播信息
		@param msgType	: Flag
		@type  msgType	: UINT8
		@return STRING
		"""
		if itemBCMsg.has_key( msgType ):
			return random.choice( itemBCMsg[msgType] )
		return ""
		
	def getCueMsgString( self, **msgKeys ):
		"""
		策划需求改动 广播文字组织方式独立出来处理
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
		是否拾取提示
		"""
		if itemID not in self._datas: return False
		return self._maps["pickCue"] in self._datas[itemID]

	def isCardCue( self, itemID ):
		"""
		是否开锦囊提示
		"""
		if itemID not in self._datas: return False
		return self._maps["cardCue"] in self._datas[itemID]

	def isNpcTradeCue( self, itemID ):
		"""
		是否NPC交易提示
		"""
		if itemID not in self._datas: return False
		return self._maps["npcTradeCue"] in self._datas[itemID]

	def isShopCue( self, itemID ):
		"""
		是否商城购买提示
		"""
		if itemID not in self._datas: return False
		return self._maps["shopCue"] in self._datas[itemID]

	def isPTradeCue( self, itemID ):
		"""
		是否玩家交易提示
		"""
		if itemID not in self._datas: return False
		return self._maps["pTradeCue"] in self._datas[itemID]

	def isQuestCue( self, itemID ):
		"""
		是否任务奖励提示
		"""
		if itemID not in self._datas: return False
		return self._maps["questCue"] in self._datas[itemID]

	def isStroeHorseCue( self, itemID ):
		"""
		是否开宝箱提示
		"""
		if itemID not in self._datas: return False
		return self._maps["stroeHorseCue"] in self._datas[itemID]

	def isNpcGiveCue( self, itemID ):
		"""
		是否NPC给予提示
		"""
		if itemID not in self._datas: return False
		return self._maps["npcGiveCue"] in self._datas[itemID]

	def reset( self ):
		"""
		重新加载数据
		"""
		self._datas = {}
		reload( CueItems )
		self._datas = CueItems.Datas
