# -*- coding: gb18030 -*-
#
# $Id: QTScript.py,v 1.46 2008-09-05 08:54:40 songpeifang Exp $

"""
"""

import items
import cschannel_msgs
import ShareTexts as ST
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.SkillLoader import g_skills
import BigWorld
import Math
import math
import random
from bwdebug import *
import csdefine
import csstatus
import Language
import ECBExtend
import csconst
import ItemTypeEnum
import sys
import Love3
import time
import Const
from utils import vector3TypeConvert
from Domain_Fight import g_fightMgr


# 映射任务脚本与实例化类型
# 此映射主要用于从配置中初始化实例时使用
# key = 目标类型字符串，取自各类型的类名称;
# value = 继承于QTScript的类，用于根据类型实例化具体的对像；
quest_script_type_maps = {}

def MAP_QUEST_SCRIPT_TYPE( classObj ):
	"""
	映射任务目标类型与实例化类型
	"""
	quest_script_type_maps[classObj.__name__] = classObj

def createScript( strType ):
	"""
	"""
	try:
		return quest_script_type_maps[strType]()
	except KeyError:
		ERROR_MSG( "can't create instance by %s type." % strType )
		return None


# ------------------------------------------------------------>
# Abstract class
# ------------------------------------------------------------>
class QTScript:
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		pass

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass

	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass

class QTSRemoveSpecialFlag:
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._flag = section.readString( "param1" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		try:
			d = player.getMapping()["questSpecialFlag"]
		except KeyError:
			return
		try:
			del d[self._flag]
		except KeyError, errstr:
			ERROR_MSG( "Remove flag error.", errstr )

	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		self.do( player )	# 放弃任务时也要去掉标志

class QTSSetSpecialFlag:
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._flag = section.readString( "param1" )
		self._value = section.readInt( "param2" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		try:
			d = player.getMapping()["questSpecialFlag"]
		except KeyError:
			d = {}
			player.getMapping()["questSpecialFlag"] = d
		d[self._flag] = self._value

class QTAddBuff( QTScript ):
	"""
	任务开始时添加配置buff by姜毅
	"""
	def __init__( self, *args ):
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questBuffSkillID = section.readString( "param1" )
		self.tasks = None

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		if self._questBuffSkillID is None or self._questBuffSkillID == 0: return
		self.tasks = tasks
		Love3.g_skills[int( self._questBuffSkillID )].receiveLinkBuff( None, player )
		if tasks is not None:
			for task in tasks._tasks.itervalues():
				if task.getType() == csdefine.QUEST_OBJECTIVE_HASBUFF:
					if len( player.findBuffsByBuffID( task.getBuffID() ) ) > 0:
						task.val1 = 1


class QTBuffBanTask:
	def __init__( self, *args ):
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._banBuffIDs = []
		for i in xrange( 1, 6 ):
			par = section.readString( "param" + str( i ) )
			if par: self._banBuffIDs.append( int( par ) )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		buffs = player.getBuffs()
		if len( self._banBuffIDs ) == 0 or len( buffs ) == 0: return True
		for buff in buffs:
			buffID = buff['skill']._buffID
			if buffID is None or buffID == 0: continue
			if buffID in self._banBuffIDs:
				player.statusMessage( csstatus.ROLE_QUEST_BUFF_BAN )
				return False
		return True

	def do( self, player, task = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass

class QTSGiveItems:
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._items = []
		for itemID, amount in args:
			self._items.append( itemID, amount )

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		for sec in section.values():
			self._items.append( ( sec.readInt( "itemID" ), sec.readInt( "amount" ) ) )

	def __itemFilter( self, itemList,player ):
		"""
		过滤itemList:
		1.角色背包中没有该物品，则给角色规定数量的该物品
		2.角色背包中有该物品，但数量不够，则给角色数量差值的该物品
		3.角色背包中有该物品，且数量足够，则不给该物品
		@return: No
		"""
		addItems = []
		for itemID, iAmount in itemList:
			kitBagItems = player.findItemsByIDFromNKCK( itemID )#从背包中取出相同的物品，空值表示角色没有这个item，不空要计算数量
			item = items.instance().createDynamicItem( itemID, iAmount )
			amount = 0
			if not kitBagItems:
				addItems.append( item )
				continue
			else:
				for tempItem in kitBagItems:
					amount += tempItem.amount
			if item.amount > amount: #角色的item数量不足，差多少给多少
				item.setAmount( item.amount-amount )
				addItems.append( item )
		return addItems

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		tempItems =  self.__itemFilter( self._items,player )
		if not tempItems:
			return True
		state = player.checkItemsPlaceIntoNK_( tempItems )
		if  state == csdefine.KITBAG_NO_MORE_SPACE:
			player.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_ACCEPT )
			return False
#		if state == csdefine.KITBAG_ITEM_COUNT_LIMIT:
#			player.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
#			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；
		注意：此处不做任何执行前的检查。
		@return: 无
		"""
		tempItems =  self.__itemFilter( self._items,player )
		if not tempItems:
			return
		for item in tempItems:
			player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTSGIVEITEMS )
			if tasks:
				tasks.addDeliverAmount( player, item, item.getAmount() )

class QTSGiveProperityItems( QTSGiveItems ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTSGiveItems.__init__( self, args )

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		for sec in section.values():
			itemID = sec.readInt( "itemID" )
			amount = sec.readInt( "amount" )
			property = sec.readString( "property" )
			value = sec.readInt( "value" )
			item = items.instance().createDynamicItem( itemID, amount )
			item.set( property, value )
			self._items.append( item )


class QTSRemoveItem:
	"""
	删除一个物品
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		self._itemID = ""
		self._amount = 1
		if len( args ) >= 2:
			self._itemID = args[0]
			self._amount = args[1]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._itemID = section.readInt( "param1" )
		self._amount = section.readInt( "param2" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True		# 不作任何检查，也就是说如果指定的物品不存在玩家身上则不删除

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.removeItemTotal( self._itemID, self._amount, csdefine.DELETE_ITEM_QTSREMOVEITEM )

class QTSAfterRemoveItem( QTSRemoveItem ):
	"""
	完成任务时删除任务道具
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		QTSRemoveItem.__init__( self, *args )

	def do( self, player, tasks = None ):
		"""
		完成任务是删除任务道具
		"""
		remainAmount = player.countItemTotal_( self._itemID )
		if self._amount > remainAmount: # 如果身上没那么多了，还是要把剩下的删除
			player.removeItemTotal( self._itemID, remainAmount, csdefine.DELETE_ITEM_QTSREMOVEITEM )
		else:
			player.removeItemTotal( self._itemID, self._amount, csdefine.DELETE_ITEM_QTSREMOVEITEM )

	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass

class QTSSummonNPC:
	"""
	召唤一个NPC
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._position = ""
		self._direction = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section param2 " % ( self.__class__.__name__, position ) )
			else:
				self._position = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section param3" % ( self.__class__.__name__, direction ) )
			else:
				self._direction = dir

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pos = Math.Vector3( player.position )
		direction = player.direction

		pos.x = player.position.x  +  random.random() * random.randint( -3, 3 )
		pos.z = player.position.z  +  random.random() * random.randint( -3, 3 )

		if self._position:
			pos = self._position
		if self._direction:
			direction = self._direction

		# 召唤怪物的时候对地面进行碰撞检测避免怪物陷入地下
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y

		entity = player.createObjectNearPlanes( self._param1, pos, direction, { "spawnPos" : tuple( pos ) } )
		# 对召唤出来的任务怪特殊处理，直接设置其bootyOwner
		getEnemyTeam = getattr( player, "getTeamMailbox", None )	# 如果有队伍则记录队伍mailbox
		if getEnemyTeam and getEnemyTeam():
			entity.bootyOwner = ( player.id, getEnemyTeam().id )
		else:
			entity.bootyOwner = ( player.id, 0 )
		entity.firstBruise = 1		# 避免Monster中第一次受伤害对bootyOwner处理


class QTSFallowNPC( QTSSummonNPC ):
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._position = ""
		self._direction = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )

		position = section.readString( "param3" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section param3 " % ( self.__class__.__name__, position ) )
			else:
				self._position = pos

		direction = section.readString( "param4" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section param4" % ( self.__class__.__name__, direction ) )
			else:
				self._direction = dir

	def do( self, player, tasks = None ):
		"""
		"""
		#entity = BigWorld.entities.get( player.targetID )
		# 随机取点散走
		rad = math.pi * 2.0 * random.random()
		pos = Math.Vector3( player.position )
		distance = 2 + 2 * random.random()
		pos.x += distance * math.sin( rad )
		pos.z += distance * math.cos( rad )

		direction = player.direction

		if self._position:
			pos = self._position
		if self._direction:
			direction = self._direction

		# 召唤怪物的时候对地面进行碰撞检测避免怪物陷入地下
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y

		newEntity = player.createObjectNearPlanes( self._param1, pos, direction, { "spawnPos" : tuple( pos ) } )
		newEntity.setTemp( "npc_ownerBase", player.base )
		newEntity.setOwner( player.id )
		npcids = tasks.query( "follow_NPC" , [] )
		npcids.append(newEntity.id)
		tasks.set( "follow_NPC" , npcids )

class QTSSummonOwnMonster( QTSSummonNPC ):
	def __init__( self, *args ):
		"""
		召唤玩家同级怪
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )

	def do( self, player, tasks = None ):
		"""
		"""
		pid = player.id
		m_datas = {}
		m_datas["spawnPos"] = tuple( player.position )
		m_datas["level"] 	= player.level
		m_datas["bootyOwner"]	= ( pid, 0 )
		newEntity = player.createObjectNearPlanes( self._param1, player.position, player.direction, m_datas )
		newEntity.bootyOwner = ( pid, 0 )
		g_fightMgr.buildEnemyRelation( newEntity, player )

		if newEntity.targetID != pid:
			newEntity.changeAttackTarget( pid )

class QTSSummonRoleTypeMonsters( QTSSummonNPC ):
	def __init__( self, *args ):
		"""
		召唤与玩家模型与职业相同的怪
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._params = {csdefine.CLASS_FIGHTER:[],		#战士
			csdefine.CLASS_SWORDMAN:[],					#剑客
			csdefine.CLASS_MAGE:[],						#法师
			csdefine.CLASS_ARCHER:[]					#射手
		}

	def init( self, section ):
		"""
		按照要求：战士类型的怪物与param1对应，剑客类型的怪物与param2对应，
		法师类型的怪物与param3对应，射手类型的怪物与param4对应，
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._params[csdefine.CLASS_FIGHTER]	= section.readString( "param1" ).split("|")
		self._params[csdefine.CLASS_SWORDMAN]	= section.readString( "param2" ).split("|")
		self._params[csdefine.CLASS_MAGE]		= section.readString( "param3" ).split("|")
		self._params[csdefine.CLASS_ARCHER]		= section.readString( "param4" ).split("|")
	def do( self, player, tasks = None ):
		"""
		"""
		pid = player.id
		m_datas = {}
		m_datas["spawnPos"] 	= tuple( player.position )
		m_datas["level"] 		= player.level
		m_datas["bootyOwner"]	= ( pid, 0 )
		for npcID in self._params[ player.getClass() ]:
			newEntity = player.createObjectNearPlanes( npcID, player.position, player.direction, m_datas.copy() )
			g_fightMgr.buildEnemyRelation( newEntity, player )
			if newEntity.targetID != pid:
				newEntity.changeAttackTarget( pid )

class QTSGnerateDart( QTSSummonNPC ):
	"""
	生成镖车
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._dartCarEntityID = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self.dartPropertySection = Language.openConfigSection("")

		self._dartCarEntityIDs	= section.readString( "param1" )	#要生成的镖车实体ID列表
		self._destNPCID			= section.readString( "param2" )	#目的NPC的ID
		self._factionID			= section.readInt( "param3" )		#镖局势力ID
		self._questID			= section.readInt( "param4" )		#任务ID
		self._eventIndex		= section.readInt( "param5" )		#任务目标索引
		self._dartPos			= ( 0, 0, 0 )


		#idList = self._dartCarEntityIDs.split('|')
		#b = 0
		#self._idRate = {}
		#for i in idList:
		#	l = i.split(':')
		#	self._idRate[l[0]] = ( b, b+int(l[1]) )
		#	b += int(l[1])

	def query( self, player ):
		"""
		查询脚本是否能执行
		@return: Bool
		@rtype:  Bool
		"""
		#如果玩家的镖局声望小于0而且没有金牌镖师凭证
		return True

	def do( self, player, tasks = None ):
		"""
		"""
		#entity = BigWorld.entities.get( player.targetID )
		# 随机取点散走
		pos = self._dartPos
		if pos == ( 0, 0, 0 ):
			rad = math.pi * 2.0 * random.random()
			pos = Math.Vector3( player.position )
			distance = 2 + 2 * random.random()
			pos.x += distance * math.sin( rad )
			pos.z += distance * math.cos( rad )
		dartCarEntityID = self._dartCarEntityIDs

		dartPointDict = eval( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_DART_POINT ) )
		if player.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ):
			point = dartPointDict[csdefine.ROLE_FLAG_XL_DARTING]
		else:
			point = dartPointDict[csdefine.ROLE_FLAG_CP_DARTING]
		player.set( "dartStartMapPoint", point )	# 设置接镖时的镖局积分。任务结束或任务失败都要清除此标记

		player.setTemp( "Dart_uname" , cschannel_msgs.QUEST_INFO_17 + player.getName() + ")" )
		player.setTemp( "Dart_destNpcClassName" , self._destNPCID )
		player.setTemp( "Dart_questID" , self._questID )
		player.setTemp( "Dart_eventIndex" , self._eventIndex )
		player.setTemp( "Dart_factionID" , self._factionID )
		player.setTemp( "Dart_start_time" , BigWorld.time() )
		player.setTemp( "Dart_level" , player.level )
		player.setTemp( "Dart_callMonstersTotal" , 3 )
		player.setTemp( "Dart_callMonstersTimeTotal" , 5 )
		player.setTemp( "acceptDartQuestTime", BigWorld.time() )
		player.setTemp("Dart_type",self._dartType )
		tasks.set( "factionID", self._factionID  )
		mapName =player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.createNPCObjectFormBase( mapName, str(dartCarEntityID), pos, player.direction, {"ownerID": player.id, "ownerName":player.getName() } )


class QTSGivePictures:
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		if len( args ) > 2:
			self.itemID = int( args[0] )
			self.amount = int( args[1] )
			self.npcClassName = str( args[2] )

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self.itemID = section.readInt( "param1" )
		self.amount = section.readInt( "param2" )
		self.npcClassName = section.readString( "param3" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		item = items.instance().createDynamicItem( self.itemID, self.amount )
		state = player.checkItemsPlaceIntoNK_( [item] )
		if  state == csdefine.KITBAG_NO_MORE_SPACE:
			player.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_ACCEPT )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；
		注意：此处不做任何执行前的检查。
		@return: 无
		"""
		item = items.instance().createDynamicItem( self.itemID, self.amount )
		item.set("pictureIntentionTargetID", self.npcClassName )
		player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTSGIVEITEMS )


class QTSAfterMissionComplete:
	"""
	任务结束，这包括完成任务和放弃任务
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._factionID		= section.readInt( "param1" )		#镖局势力id
		self._completeVal	= section.readInt( "param2" )		#完成任务增加的声望值
		self._abandoneVal	= section.readInt( "param3" )		#放弃或失败减少的声望值
		self._questType		= section.readInt( "param4" )		#任务类型(5为运镖，6为劫镖)
		self._abandonedFlag	= {37:"sm_dartNotoriousXinglong", 38:"sm_dartNotoriousChangping"}
		self._completedFlag	= {37:"sm_dartCreditXinglong", 38:"sm_dartCreditChangping"}

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		完成任务
		"""
		player.base.addDartData( self.getKey( self._factionID, True ), self._completeVal )
		#BigWorld.globalData['DartManager'].onReceiveDestoryCommand( player.getName() )
		player.client.updateTitlesDartRob( self._factionID )
		if self._questType == csdefine.QUEST_TYPE_DART:	# 运镖
			player.remove( "dartStartMapPoint" )
		elif self._questType == csdefine.QUEST_TYPE_ROB:	# 劫镖
			dartPointDict = eval( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_DART_POINT ) )
			if player.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ):	# 劫镖成功己方镖局积分+1，对方-1，初始都是50，到0不再减
				if dartPointDict[csdefine.ROLE_FLAG_CP_DARTING] <= 0:
					return
				dartPointDict[csdefine.ROLE_FLAG_CP_DARTING] -= 1
				dartPointDict[csdefine.ROLE_FLAG_XL_DARTING] += 1
			else:
				if dartPointDict[csdefine.ROLE_FLAG_XL_DARTING] <= 0:
					return
				dartPointDict[csdefine.ROLE_FLAG_XL_DARTING] -= 1
				dartPointDict[csdefine.ROLE_FLAG_CP_DARTING] += 1
			BigWorld.setSpaceData( player.spaceID, csconst.SPACE_SPACEDATA_DART_POINT, str( dartPointDict ) )
		else:
			ERROR_MSG( "wrong quest type( %i ), player( %s )" % ( self._questType, player.getName() ) )

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		value = 0 - self._completeVal	#增加一个负声望就相当于减少了声望
		if value + player.getPrestige( self._factionID ) >= 0 or player.getPrestige( self._factionID ) < 0:
			player.addPrestige( self._factionID, value )
		else:
			player.setPrestige( self._factionID, 0 )
		player.base.addDartData( self.getKey( self._factionID, False ), value )
		player.client.updateTitlesDartRob( self._factionID )

		BigWorld.globalData['DartManager'].requestToDestoryDartRelation( player.getName() )
		if self._questType == csdefine.QUEST_TYPE_DART:
			player.remove( "dartStartMapPoint" )

	def getKey( self, factionID, complete ):
		"""
		"""
		if complete == True:
			return self._completedFlag[self._factionID]
		else:
			return self._abandonedFlag[self._factionID]

class QTRemoveBuff:
	"""
	任务结束时解除任务所添加的buff by姜毅
	"""
	def __init__( self, *args ):
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questBuffSkillID		= section.readInt( "param1" )		# 任务所添加buff的技能IDs

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		if self._questBuffSkillID is None or self._questBuffSkillID == 0: return
		skill = g_skills[self._questBuffSkillID]
		if skill is None: return
		buffLink = skill._buffLink
		for l in xrange( len( buffLink ) ):
			id = self._questBuffSkillID * 100 + l + 1
			player.removeBuffByID( id,  [csdefine.BUFF_INTERRUPT_NONE] )

	def do( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		if self._questBuffSkillID is None or self._questBuffSkillID == 0: return
		skill = g_skills[self._questBuffSkillID]
		if skill is None: return
		buffLink = skill._buffLink
		for l in xrange( len( buffLink ) ):
			id = self._questBuffSkillID * 100 + l + 1
			player.removeBuffByID( id,  [csdefine.BUFF_INTERRUPT_NONE] )

class QTSCheckItem:
	"""
	检查任务所需要的物品是否齐全
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._itemID	= section.readInt( "param1" )		#所需物品的ID
		self._itemAmount= section.readInt( "param2" )		#所需物品数量
		self._dialog	= section.readString( "param3" )	#缺少物品的对白
		self._npcClassName = section.readString( "param4" )	#接任务的NPC className

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		item = player.findItemFromNKCK_( self._itemID )
		if not item:
			npcs = player.entitiesInRangeExt( 30, "NPC", player.position )
			id = 0
			for i in npcs:
				if i.className == self._npcClassName:
					id = i.id
			player.setGossipText( self._dialog )
			player.sendGossipComplete( id )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.removeItemTotal( self._itemID, 1, csdefine.DELETE_ITEM_QTSCHECKITEM )	#移除掉所需要的物品

class QTSCheckLevel:
	"""
	检查接任务的级别是否符合
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._minLevel		= section.readInt( "param1" )			#任务所需最低级别
		self._maxLevel		= section.readInt( "param2" )			#任务所需最高级别
		self._minLevTalk	= section.readString( "param3" )		#级别不够的对白
		self._maxLevTalk	= section.readString( "param4" )		#级别过高的对白
		self._npcClassName	= section.readString( "param5" )		#接任务的NPC className


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		npcs = player.entitiesInRangeExt( 30, "NPC", player.position )
		id = 0
		for i in npcs:
			if i.className == self._npcClassName:
				id = i.id

		if player.level < self._minLevel:
			player.setGossipText( self._minLevTalk )
			player.sendGossipComplete( id )
			return False
		elif player.level > self._maxLevel and self._maxLevel != 0:
			player.setGossipText( self._maxLevTalk )
			player.sendGossipComplete( id )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass


class QTSCheckDeposit:
	"""
	检查身上金钱是否足够交押金
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._deposit		= section.readInt( "param1" )			#押金数量
		self._dialog		= section.readString( "param2" )		#押金不够对白
		self._npcClassName	= section.readString( "param3" )			#接任务的NPC className


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		if player.money < self._deposit:
			npcs = player.entitiesInRangeExt( 30, "NPC", player.position )
			id = 0
			for i in npcs:
				if i.className == self._npcClassName:
					id = i.id
			player.setGossipText( self._dialog )
			player.sendGossipComplete( id )
			player.statusMessage( csstatus.TONG_RUNTRADE_MONEY_NOTENOUGTH )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		if not player.payMoney( self._deposit, csdefine.CHANGE_MONEY_DEPOSIT ):
			player.statusMessage( csstatus.TONG_RUNTRADE_MONEY_NOTENOUGTH )
			return
		#金钱显示方式变换 by姜毅
		dep = int( self._deposit )
		if dep < 100:
			moe2 = dep
			dep = cschannel_msgs.QUEST_INFO_18%( moe2 )
		elif dep >= 100 and dep < 10000:
			moe1 = dep / 100
			moe2 = dep - moe1 * 100
			if moe2 == 0:
				dep = cschannel_msgs.QUEST_INFO_19%( moe1 )
			else:
				dep = cschannel_msgs.QUEST_INFO_20%( moe1, moe2 )
		else:
			moe0 = dep / 10000
			moebuf = dep - moe0 * 10000
			moe1 = moebuf / 100
			moe2 = moebuf - moe1 * 100
			if moe2 == 0 and moe1 == 0:
				dep = cschannel_msgs.QUEST_INFO_21%( moe0 )
			elif moe2 == 0:
				dep = cschannel_msgs.QUEST_INFO_22%( moe0, moe1 )
			else:
				dep = cschannel_msgs.QUEST_INFO_23%( moe0, moe1, moe2 )
		player.statusMessage( csstatus.ROLE_QUEST_DEPOSIT_PAY, dep )


class QTSNotHasQuestType:
	"""
	检查玩家身上是否有运（劫）镖任务
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questType		= section.readInt( "param1" )			#任务类型
		self._dialog		= section.readString( "param2" )		#已有此类型任务提示对白
		self._dialog_op		= section.readString( "param3" )		#如果有对立任务类型提示对白
		self._factionID		= section.readInt( "param4" )			#镖局所属势力id(目前只有镖局需要配置此参数)
		self._npcClassName	= section.readString( "param5" )			#接任务的NPC className


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		npcs = player.entitiesInRangeExt( 30, "NPC", player.position )
		id = 0
		for i in npcs:
			if i.className == self._npcClassName:
				id = i.id

		for qID in player.questsTable._quests:
			if player.getQuest( qID ).getType() == self._questType:
				if self._factionID == player.questsTable[qID].query( 'factionID', -1 ):
					player.setGossipText( self._dialog )
				else:
					player.setGossipText( self._dialog_op )
				player.sendGossipComplete( id )
				return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass

class QTSIsCaptain:
	"""
	检查接受帮会运镖的玩家是否具有申请资格
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		questsStr			= section.readString( "param1" )		#任务id
		self._dialog		= section.readString( "param2" )		#不是帮主的对白
		self._distance		= section.readInt( "param3" )			#帮主范围内多少距离的玩家
		self._npcClassName	= section.readInt( "param4" )			#接任务的NPC className
		self._quests = []
		for i in questsStr.split('|'):
			self._quests.append( i.split(':') )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		#判断接任务的玩家是否是家族帮主

		npcs = player.entitiesInRangeExt( 30, "NPC", player.position )
		id = 0
		for i in npcs:
			if str( i.className ) == str( self._npcClassName ):
				id = i.id

		if player.tong_grade < csdefine.TONG_DUTY_TONG:
			dailog = self._dialog
			if 's' in dailog:
				player.tong_getSelfTongEntity().sendDailogByTongDutyName( csdefine.TONG_DUTY_TONG, dailog, id, player )
			else:
				player.setGossipText( dailog )
				player.sendGossipComplete( id )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.setTemp( "needSendTongQuest", {"dis":self._distance, "qus":self._quests} )

class QTSSetFaction:
	"""
	设置镖局势力
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questID		= section.readInt( "param1" )			#任务id
		self._factionID		= section.readInt( "param2" )			#镖局势力id

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		tasks.set( "factionID", self._factionID )
		#player.questsTable._quest( self._questID )._tasks
		#dQuest = player.getQuest( self._questID )
		#dQuest.setFaction( self._factionID )


class QTSAddDartCount:
	"""
	增加运镖次数
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._dartType		= section.readInt( "param1" )			#镖局任务类型
		self._value			= section.readInt( "param2" )			#次数值

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.questTongDartRecord.dartCount += self._value


	def onAbandoned( self, player, questData = None ):
		"""
		"""
		player.questTongDartRecord.dartCount -= self._value


class QTSAfterFamilyComplete:
	"""
	家族任务完成需要触发的事件
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		questsStr			= section.readString( "param1" )		#任务id
		#self._questID		= section.readInt( "param1" )			#任务id
		self._eventIndex	= section.readInt( "param2" )			#任务目标索引
		self._distance		= section.readInt( "param3" )			#距离

		self._quests = []
		for i in questsStr.split('|'):
			self._quests.append( i.split(':') )
		self._quests.reverse()

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		#
		for e in player.family_onlineMemberMailboxs.itervalues():
			if BigWorld.entities.has_key( e.id ) and \
			BigWorld.entities[ e.id ].spaceID == player.spaceID and \
			BigWorld.entities[ e.id ].position.flatDistTo( player.position ) <= self._distance :
				for i in self._quests:
					if BigWorld.entities[ e.id ].questsTable._quests.has_key( int(i[0]) ):
						BigWorld.entities[e.id].questTaskIncreaseState( int(i[0]), self._eventIndex )
		return


	def onAbandoned( self, player, tasks = None ):
		"""
		当族长放弃家族任务时，应该是接了此任务的全体家族成员的任务都被失败
		"""
		#因为族长放弃任务时，不一定所有接了此任务的玩家都在线，所以族长放弃任务就让他放弃，不需要通知家族成员任务失败
		#因为只要组长放弃了任务，其他人肯定也完成不了了
		pass

class QTSAfterTongComplete:
	"""
	帮会任务完成需要触发的事件
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		questsStr			= section.readString( "param1" )		#任务id
		#self._questID		= section.readInt( "param1" )			#任务id
		self._eventIndex	= section.readInt( "param2" )			#任务目标索引
		self._distance		= section.readInt( "param3" )			#距离

		self._quests = []
		for i in questsStr.split('|'):
			self._quests.append( i.split(':') )
		self._quests.reverse()

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		#
		g = BigWorld.entities.get
		for e in player.tong_onlineMemberMailboxs.itervalues():
			member = g( e.id )
			if member is not None and member.spaceID == player.spaceID and member.position.flatDistTo( player.position ) <= self._distance:
				for i in self._quests:
					if member.questsTable._quests.has_key( int(i[0]) ):
						member.questTaskIncreaseState( int(i[0]), self._eventIndex )

	def onAbandoned( self, player, tasks = None ):
		"""
		当族长放弃家族任务时，应该是接了此任务的全体家族成员的任务都被失败
		"""
		#因为族长放弃任务时，不一定所有接了此任务的玩家都在线，所以族长放弃任务就让他放弃，不需要通知家族成员任务失败
		#因为只要组长放弃了任务，其他人肯定也完成不了了
		pass

class QTSCheckPrestige:
	"""
	检查玩家镖局声望是否足够接任务
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._factionID		= section.readInt( "param1" )			#镖局势力
		self._requestPres	= section.readInt( "param2" )			#能够接此任务的最低镖局声望
		self._dialog		= section.readString( "param3" )		#声望不够的提示对白
		self._npcClassName	= section.readString( "param4" )			#接任务的NPC className


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""

		npcs = player.entitiesInRangeExt( 30, "NPC", player.position )
		id = 0
		for i in npcs:
			if i.className == self._npcClassName:
				id = i.id

		if player.isPrestigeOpen( self._factionID ) and player.getPrestige( self._factionID ) < self._requestPres:
			player.setGossipText( self._dialog )
			player.sendGossipComplete( id )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass


class QTSAfterCompleteOpenBank:
	"""
	任务结束，这包括完成任务和放弃任务
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		完成任务
		"""
		player.bank_activateBag()


	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass

class QTSAfterFallowNPC:
	"""
	护送任务结束，负责删除任务时完成杀掉NPC
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		完成任务
		"""
		# 清除标记
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		ids = tasks.query( "follow_NPC" , [] )
		for id in ids:
			if BigWorld.entities.has_key( id ):
				# 杀了这个NPC
				BigWorld.entities[ id ].remoteCall( "destroy", () )
		# 清除标记
		tasks.set( "follow_NPC" , [] )

class QTSAfterGiveGens:
	"""
	护送任务结束，负责删除任务时完成杀掉NPC
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		完成任务
		"""
		# 清除标记
		player.ptn_questActiveTrainGem()
		#player.client.showTrainGem()

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass


class QTSGiveYinpiao:
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._itemInfo = []

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		itemID = section.readInt( "param1" )
		amount = section.readInt( "param2" )
		initValue = section.readInt( "param3" )
		maxValue = section.readInt( "param4" )
		self._itemInfo = [ itemID, amount, initValue, maxValue ]

	def __itemFilter( self, itemInfoList, player ):
		"""
		过滤itemInfoList:
		1.角色背包中没有该物品，则给角色规定数量的该物品
		2.角色背包中有该物品，但数量不够，则给角色数量差值的该物品
		3.角色背包中有该物品，且数量足够，则不给该物品
		@return: No
		"""
		item = items.instance().createDynamicItem( itemInfoList[0], itemInfoList[1] )
		item.set( "yinpiao", itemInfoList[2] )
		item.set( "maxYinpiao", itemInfoList[3] )

		addItems = []
		kitBagItems = player.findItemsByIDFromNKCK( itemInfoList[0] )#从背包中取出相同的物品，空值表示角色没有这个item，不空要计算数量
		amount = 0
		if not kitBagItems:
			addItems.append( item )
		else:
			for tempItem in kitBagItems:
				amount += tempItem.amount
			if item.amount > amount: # 角色的item数量不足，差多少给多少
				item.setAmount( item.amount-amount )
				addItems.append( item )
		return addItems

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		tempItems =  self.__itemFilter( self._itemInfo, player )
		if not tempItems:
			return True
		state = player.checkItemsPlaceIntoNK_( tempItems )
		if state == csdefine.KITBAG_NO_MORE_SPACE:
			player.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_ACCEPT )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；
		注意：此处不做任何执行前的检查。
		@return: 无
		"""
		tempItems =  self.__itemFilter( self._itemInfo, player )
		if not tempItems:
			return
		for item in tempItems:
			player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTSGIVEYINPIAO )
			if tasks:
				tasks.addDeliverAmount( player, item, item.getAmount() )

class QTSAfterDeleteItem:
	"""
	放弃任务后，删除相应的任务物品
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		self._itemID = ""
		self._amount = 1
		if len( args ) >= 2:
			self._itemID = args[0]
			self._amount = args[1]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._itemID = section.readInt( "param1" )
		self._amount = section.readInt( "param2" )

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		remainAmount = player.countItemTotal_( self._itemID )
		if self._amount > remainAmount: # 如果身上没那么多了，还是要把剩下的删除
			player.removeItemTotal( self._itemID, remainAmount, csdefine.DELETE_ITEM_QTSAFTERDELETEITEM )
		else:
			player.removeItemTotal( self._itemID, self._amount, csdefine.DELETE_ITEM_QTSAFTERDELETEITEM )



class QTSBuKaoMoney:
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._money = section.readInt( "param1" )


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		if player.money < self._money:
			player.statusMessage( csstatus.BANK_MONEY_NOT_ENOUGH_TO_STORE )
			return False

		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；
		注意：此处不做任何执行前的检查。
		@return: 无
		"""
		player.payMoney( self._money, csdefine.CHANGE_MONEY_BUKAO )

class QTSAddBuff:
	"""
	放弃任务后，增加一个buff
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		self._skillID = 0

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._skillID = section.readInt( "param1" )

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		Love3.g_skills[self._skillID].receiveLinkBuff( player, player )


class QTSSetQuestionType:
	"""
	设置回答形式问题类型
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._type		= section.readInt( "param1" )			#任务id


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.set("question_type", self._type )


class QTSAfterRemoveQuestionType:
	"""
	设置回答形式问题类型
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._type		= section.readInt( "param1" )			#任务id


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.remove("question_type")


class QTSRemoveQuestLog:
	"""
	删除一个任务记录
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		self._questID = 0
		if len( args ) >= 1:
			self._questID = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questID = section.readInt( "param1" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True		# 不作任何检查，也就是说如果指定的物品不存在玩家身上则不删除

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.questsLog.remove( self._questID )



class QTSRemoveRobFlags:
	"""
	删除劫匪标志
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		self._leaveTime = 0
		if len( args ) >= 1:
			self._leaveTime = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._leaveTime = section.readInt( "param1" )			#单位：秒

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True		# 不作任何检查，也就是说如果指定的物品不存在玩家身上则不删除

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		#player.setTemp( "robDart_timerID", player.addTimer( self._leaveTime, 0, ECBExtend.REMOVE_ROB_FLAG ) )
		player.set("RobEndTime", time.time() + self._leaveTime )



class QTSAfterSetKaStone:
	"""
	任务完成设置魂魄石
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._itemID	= section.readInt( "param1" )			# 要设置的魂魄石物品ID
		self._ka_count	= section.readInt( "param2" )			# 要设置成的数值

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		item = player.findItemFromNKCK_( self._itemID )			# 找到需要设置的魂魄石物品
		if item:
			item.set( 'ka_count',self._ka_count, player )
		else:
			INFO_MSG( "没有找到奖励的魂魄石，无法设置数值。" )

	def onAbandoned( self, player, tasks = None ):
		"""
		"""
		pass


class QTSTalkFunction:
	"""
	执行对话功能
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._key = section.readString( "param1" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.gossipWith(player.id, player.targetID, self._key)

class QTSWithoutBuff:
	"""
	检查角色是否没有相应的buff
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._buffID = section.readInt( "param1" )		# buffID
		self._dialog = section.readString( "param2" )	# 有buff的对白
		self._npcClassName	= section.readString( "param3" )	#接任务的NPC className

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		npcs = player.entitiesInRangeExt( 30, "NPC", player.position )
		id = 0
		for i in npcs:
			if i.className == self._npcClassName:
				id = i.id

		if len( player.findBuffsByBuffID( self._buffID ) ) > 0:
			player.setGossipText( self._dialog )
			player.sendGossipComplete( id )
			return False
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass


class QTSRequestTeach:
	"""
	玩家完成任务后，寻找师父的广播
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount )
		"""
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast( cschannel_msgs.BCT_JSGX_FIND_TEACHER, [] )

	def onAbandoned( self, player, tasks = None ):
		"""
		"""
		pass


class QTSRecordLevel:
	"""
	记录接任务等级
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questID = section.readInt( "param1" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.set("recordQuestLevel_%i"%self._questID, player.level )



class QTSCleanRecordLevel:
	"""
	清理记录接任务等级
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questID = section.readInt( "param1" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		try:
			player.remove( "recordQuestLevel_%i"%self._questID )
		except:
			ERROR_MSG( "Remove player mapping value(%s) error."%"recordQuestLevel_%i"%self._questID  )


	def onAbandoned( self, player, tasks = None ):
		"""
		"""
		try:
			player.remove( "recordQuestLevel_%i"%self._questID )
		except:
			ERROR_MSG( "Remove player mapping value(%s) error."%"recordQuestLevel_%i"%self._questID  )


class QTSStartHelpNPC:
	"""
	开始护法
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._className1 = section.readString( "param1" )				#任务NPC
		self._className2s = section.readString( "param2" ).split(":")				#需要护法的NPC
		self._range		= section.readInt( "param3" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		npc = BigWorld.entities.get( player.targetID, None )
		if npc is not None:
			if npc.hasFlag( csdefine.ENTITY_FLAG_QUEST_WORKING ):
				npc.say( cschannel_msgs.QUEST_INFO_48 )
				return False
			else:
				return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		npcs = player.entitiesInRangeExt( self._range, "NPC", player.position )
		npc1 = None
		npc2s = []
		for i in npcs:
			if i.className == self._className1:
				npc1 = i
			if i.className in self._className2s:
				npc2s.append( i )
		npc1.setQuestWorkingFlag( 60 )
		for i in npc2s:
			i.setDefaultAILevel( 1 )
			i.setNextRunAILevel( 1 )


class QTSDestroyNPC:
	"""
	摧毁NPC
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._className = section.readString( "param1" )			#目标NPC
		self._range = section.readInt( "param2" )					#范围


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		npcs = player.entitiesInRangeExt( self._range, "NPC", player.position )
		for i in npcs:
			if i.className == self._className:
				i.destroy()


class QTSShowQuestMsg:
	"""
	显示任务情节
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._msg = section.readString( "param1" )				#目标NPC


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.client.showQuestMsg( self._msg )

class QTSTeleport( QTScript ):
	"""
	将人物传送到某个空间 by mushuang
	"""
	def __init__( self, *args ):
		"""
		"""
		self.spaceType = ""
		self.direction = ( 0, 0, 0 )
		self.position = ( 0, 0, 0 )

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		# Param1: 目标空间类型，比如fengming
		# Param2: 传送方向，x,y,z三个分量用空格隔开，比如：1.2 10.1 100.0
		# Param3: 传送位置，格式同上

		self.spaceType = section.readString( "param1" )				# 目标空间

		# 获取方向
		array = section.readString( "param2" ).strip().split()
		assert len( array ) == 3
		self.direction = tuple( [ float( e ) for e in array ] )

		# 获取位置
		array = section.readString( "param3" ).split()
		assert len( array ) == 3
		self.position = tuple( [ float( e ) for e in array ] )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.gotoSpace( self.spaceType, self.position, self.direction )


class QTSTeleportPlane( QTScript ):
	"""
	将人物传送到某个位面 by ganjinxing
	"""
	def __init__( self, *args ):
		"""
		"""
		self.spaceType = ""

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		# Param1: 目标空间类型，比如fengming
		self.spaceType = section.readString( "param1" )				# 目标空间

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.enterPlane(self.spaceType)

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		self.do(player, tasks)


class QTSTeleportPlaneOnAbandoned( QTSTeleportPlane ):
	"""
	放弃任务传送到某个位面 by ganjinxing
	"""
	def __init__( self, *args ):
		"""
		"""
		QTSTeleportPlane.__init__( self, *args )

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		player.enterPlane(self.spaceType)


class QTSTeleportPlaneOnCompleted( QTSTeleportPlane ):
	"""
	完成任务传送到某个位面 by ganjinxing
	"""
	def __init__( self, *args ):
		"""
		"""
		QTSTeleportPlane.__init__( self, *args )

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.enterPlane(self.spaceType)

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass


class QTSUnfoldScroll( QTScript ):
	"""
	展开一副画卷 by mushuang
	"""
	def __init__( self, *args ):
		"""
		"""
		self.scrollID = 0

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		# Param1: 画卷的ID

		self.scrollID = section.readInt( "param1" ) # 画卷的ID

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.client.unfoldScroll( 0, self.scrollID )


class QTSAddPersistentFlag:
	"""
	增加存储标志
	"""
	def __init__( self, *args ):
		"""
		"""
		self.param1 = 0

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		# Param1: 画卷的ID

		self.param1 = section.readInt( "param1" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.addPersistentFlag( self.param1 )


class QTSRemovePersistentFlag:
	"""
	移除存储标志
	"""
	def __init__( self, *args ):
		"""
		"""
		self.param1 = 0

	def init( self, section ):
		"""
		"""
		self.param1 = section.readInt( "param1" )

	def query( self, player ):
		"""
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		"""
		player.removePersistentFlag( self.param1 )

	def onAbandoned( self, player, tasks = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		player.removePersistentFlag( self.param1 )



class QTSOpenDoor( QTScript ):
	"""
	开门 by mushuang
	"""
	def __init__( self, *args ):
		"""
		"""
		self.doorClassName = ""

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection

		"""
		self.available = True
		# Param1: 门的className，字符串，( 比如：20251051 )
		self.doorClassName = section.readString( "param1" )

		assert self.doorClassName != "", "Incorrect config in param1, entity className needed!"

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		assert self.available, "Incorrect config, quest script failed to run!"

		spaceBase = player.getCurrentSpaceBase()
		assert hasattr( spaceBase, "openDoor" ), "Current space entity doesn't have base method: \'openDoor\'! Quest script failed to run!"

		spaceBase.openDoor( { "entityName" : self.doorClassName } )

class QTSHideNPCModel( QTScript ):
	# 销毁/隐藏NPC
	def __init__( self, *args ):
		self.NPCClass = ""
		self.isDestroy = False
		self.hideTime = 0

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self.NPCClass = section.readString( "param1" )
		self.isDestroy = section.readInt( "param2" )
		if self.isDestroy:
			self.hideTime = 0
		else:
			self.hideTime = section.readInt( "param3" )

		assert self.NPCClass != "", "Incorrect config in param1, entity className needed!"

	def query( self, player ):
		"""
		查询脚本是否能执行
		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		entities = player.entitiesInRangeExt( 30, None, player.position )
		for e in entities:
			if hasattr( e, "className" ):
				if e.className == self.NPCClass:
					if self.isDestroy:
						e.destroy()
					else:
						e.clientEntity( player.id ).hideTheirFewTimeForQuest( self.hideTime )

class QTSAfterUseSkill:
	"""
	任务完成后，播放技能add by wuxo 2011-9-20
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		"""
		self._skillID = 0
		self._NPCID   = ""

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._skillID = section.readInt( "param1" )  #技能ID
		self._NPCID   = section.readString( "param2" )  #任务提交NPCID

	def query( self, player ):
		"""
		查询脚本是否能执行
		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；
		注意：此处不做任何执行前的检查。
		@return: 无
		"""
		commitTargetID = 0
		for en in player.entitiesInRangeExt( 30, None, player.position ):
			if hasattr(en,"className") and en.className == self._NPCID:
				commitTargetID = en.id
				break
		player.spellTarget( self._skillID, commitTargetID )	#使用技能,允许目标实体不存在的情况


	def onAbandoned( self, player, tasks = None ):
		"""
		放弃任务时
		执行脚本
		"""
		pass

class QTSUseSkill:
	"""
	接受任务时，播放技能add by wuxo 2011-10-8
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		"""
		self._skillID = 0
		self._NPCID   = ""

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._skillID = section.readInt( "param1" )  #技能ID
		self._NPCID   = section.readString( "param2" )  #任务领取NPCID
		self._type    = section.readString( "param3" )  #作用目标类型

	def query( self, player ):
		"""
		查询脚本是否能执行
		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；
		注意：此处不做任何执行前的检查。
		@return: 无
		"""
		acceptTargetID = 0
		if self._type == "Role":
			acceptTargetID = player.id
		else:
			for en in player.entitiesInRangeExt( 30, self._type, player.position ):
				if hasattr(en,"className") and en.className == self._NPCID:
					acceptTargetID = en.id
					break
		player.spellTarget( self._skillID, acceptTargetID )	#使用技能,允许目标实体不存在的情况


class QTSSetOffLineFailed:
	"""
	接受任务时，设置任务下线失败标记add by wuxo 2011-12-29
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		"""
		self._questOffLineFail = None

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._questOffLineFail = section.readInt( "param1" )  #任务ID


	def query( self, player ):
		"""
		查询脚本是否能执行
		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；
		注意：此处不做任何执行前的检查。
		@return: 无
		"""
		quest_failFlag = player.queryTemp( "questOffLineFail", [] )
		quest_failFlag.append(self._questOffLineFail)
		player.setTemp( "questOffLineFail", quest_failFlag )

	def onAbandoned( self, player, questData = None ):
		"""
		放弃任务
		"""
		quest_failFlag = player.queryTemp( "questOffLineFail", [] )
		for i in quest_failFlag:
			if i == self._questOffLineFail:
				quest_failFlag.remove(i)
				break
		if len(quest_failFlag) == 0:
			player.removeTemp("questOffLineFail")
		else:
			player.setTemp( "questOffLineFail", quest_failFlag )


class QTSPlaySound:
	"""
	播放音频 add by wuxo 2012-1-17
	"""
	def __init__( self ):
		self._param1 = ""
		self._param2 = 0
		self._param3 = ""

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )	#音频文件路径
		self._param2 = section.readInt( "param2" )	#音频类型 2D/3D
		self._param3 = section.readString( "param3" )   #NPC的className
		self._priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_QUEST


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		acceptTargetID = 0
		for en in player.entitiesInRangeExt( 30, "NPC", player.position ):
			if hasattr(en,"className") and en.className == self._param3:
				acceptTargetID = en.id
		player.client.playSound( self._param1, self._param2, acceptTargetID, self._priority )

	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass


class QTSPlayVideo:
	"""
	播放视频
	"""
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )			#视频文件名字

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.client.playVideo( self._param1 )


class QTSSendAICmd( QTScript ) :
	"""
	通知指定NPC执行AI指令（可用于接任务，交任务）
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._npcID = ""								# 接收指令的NPC的ID
		self._radius = 0								# 搜索半径
		self._aiCmd = None								# AI指令标识（Int16）

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._npcID = section.readString( "param1" )  	# 接收指令的NPC的ID
		self._radius = section.readInt( "param2" )		# 搜索半径
		self._aiCmd = section.readInt( "param3" )		# AI指令标识（Int16）

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		for e in player.entitiesInRangeExt( self._radius, None, player.position ):
			if e.className == self._npcID:
				e.onAICommand( e.id, e.className, self._aiCmd )					# 直接使用onAICommand是防止e是一个ghost这个方法也能用


class QTSSendAICmd_Abandon( QTScript ) :
	"""
	通知指定NPC执行AI指令（仅用于放弃任务）
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._npcID = ""								# 接收指令的NPC的ID
		self._radius = 0								# 搜索半径
		self._aiCmd = None								# AI指令标识（Int16）

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._npcID = section.readString( "param1" )  	# 接收指令的NPC的ID
		self._radius = section.readInt( "param2" )		# 搜索半径
		self._aiCmd = section.readInt( "param3" )		# AI指令标识（Int16）

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def onAbandoned( self, player, questData = None ):
		"""
		放弃任务
		"""
		for e in player.entitiesInRangeExt( self._radius, None, player.position ):
			if e.className == self._npcID:
				e.onAICommand( e.id, e.className, self._aiCmd )					# 直接使用onAICommand是防止e是一个ghost这个方法也能用


class QTSOn3C( QTScript ) :
	"""
	3C：CopyConditionChanged
	通知所在副本有条件发生变化（可用于接任务，交任务）
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._condition = ""								# 条件
		self._value = ""									# 改变值

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._condition = section.readString( "param1" )
		self._value = section.readString( "param2" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.onConditionChange( { self._condition : self._value } )	# 如果spaceEntity是None，那就让它出错


class QTSOn3C_Abandon( QTScript ) :
	"""
	3C：CopyConditionChanged
	通知所在副本有条件发生变化（可用于放弃任务）
	注：之所以把放弃任务行为重写，是因为对于同一个任务而言，
	会出现完成任务和放弃任务都需要通知副本条件改变的情况，而
	完成任务和放弃任务都会执行相同的任务行为脚本，因此无法实
	现完成任务和放弃任务执行不同功能的需求。
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._condition = ""								# 条件
		self._value = ""									# 改变值

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._condition = section.readString( "param1" )
		self._value = section.readString( "param2" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def onAbandoned( self, player, questData = None ):
		"""
		放弃任务
		"""
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.onConditionChange( { self._condition : self._value } )	# 如果spaceEntity是None，那就让它出错

class QTSNotifySpaceCMgr( QTScript ):
	# 通知华山阵法管理器，沉香刷出任务完成
	def __init__( self ):
		QTScript.__init__( self )

	def query( self, player ):
		# 查询脚本是否能执行
		if player.isInTeam():
			return self.isTeamCaptain()
		else:
			return True

	def do( self, player, tasks = None ):
		spaceChallengeKey = player.spaceChallengeKey
		if spaceChallengeKey:
			BigWorld.globalData[ "SpaceChallengeMgr" ].callPiShanEnterNpc( spaceChallengeKey )


class QTSFlyPatrol( QTScript ) :
	"""
	接任务后巡逻
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self.patrolPathNode = ""
		self.patrolList = ""
		self.spaceName = ""
		self.pos = None
		self.direction = ( 0, 0, 0 )
		self.skillID = 0

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self.patrolPathNode = section.readString( "param1" )
		self.patrolList = section.readString( "param2" )
		self.spaceName = section.readString( "param3" )

		position = section.readString( "param4" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section param4 " % ( self.__class__.__name__, position ) )
			else:
				self.pos = pos

		self.skillID = section.readInt( "param5" )

	def query( self, player ) :
		"""
		是否可接任务
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		"""
		# 如果在吟唱则中断吟唱
		if player.attrIntonateSkill or\
			( player.attrHomingSpell and player.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			player.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )

		# 记录要到达的地方
		player.setTemp( "teleportFly_data", ( self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction ) )
		player.spellTarget( self.skillID, player.id )

class QTSProduceMonsterAndTrap( QTScript ):
	"""
	在60级剧情副本中刷出怪物和陷阱
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self.monsterIDLists = []

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self.monsterLists = section.readString("param1").split(":")

	def query( self, player ):
		"""
		是否可接受任务
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		"""
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		for list in self.monsterLists:
			className = str(eval(list)[0])
			num = eval(list)[1]
			j = 0
			while j < num :
				player.createObjectNearPlanes( className, eval(list)[2][j], (0, 0, 0), { "spawnPos": eval(list)[2][j]} )
				j = j + 1

class QTSSummonMonster( QTScript ) :
	"""
	召唤指定CallMonster类型的怪物
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._position = ""
		self._direction = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )						# className

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section param2 " % ( self.__class__.__name__, position ) )
			else:
				self._position = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section param3" % ( self.__class__.__name__, direction ) )
			else:
				self._direction = dir


	def query( self, player ) :
		"""
		是否可接任务
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""

		pos = Math.Vector3( player.position )
		direction = player.direction

		pos.x = player.position.x  +  random.random() * random.randint( -3, 3 )
		pos.z = player.position.z  +  random.random() * random.randint( -3, 3 )

		if self._position:
			pos = self._position
		if self._direction:
			direction = self._direction

		# 召唤怪物的时候对地面进行碰撞检测避免怪物陷入地下
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y
		# 模型选取参考 ObjectScript/NPCObject.py 中createEntity 的处理方式
		modelNumbers = g_objFactory.getObject( self._param1 ).getEntityProperty( "modelNumber" )
		modelScales = g_objFactory.getObject( self._param1 ).getEntityProperty( "modelScale" )
		if len( modelNumbers ):
			index = random.randint( 0, len(modelNumbers) - 1 )
			modelNumber = modelNumbers[ index ]
			if len( modelScales ) ==  1:
				modelScale = float( modelScales[ 0 ] )
			elif len( modelScales ) >= ( index + 1 ):
				modelScale = float( modelScales[ index ] )
			else:
				modelScale = 1.0
		else:
			modelNumber = ""
			modelScale = 1.0
		m_datas = { "spawnPos" : tuple( pos ), "modelScale" : modelScale, "modelNumber" : modelNumber, }
		entity = player.callEntity( self._param1, m_datas, pos, direction )


class QTSSummonMonster_Abandon( QTScript ) :
	"""
	放弃任务销毁指定className的CallMonster类型的怪物
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )						# className
		self._param2 = section.readFloat( "param2" )			#范围
		self._param3 = section.readString( "param3" )			# EntityType

	def query( self, player ) :
		"""
		是否可接任务
		"""
		return True

	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		monsterList = player.entitiesInRangeExt( self._param2, self._param3, player.position )
		for i in monsterList:
			if i.className == self._param1 and i.getOwner() and i.getOwner() == player:
				i.destroy()


class QTSDestroyMonster( QTScript ) :
	"""
	销毁一定范围内从属于玩家的某类型某classname的entity
	"""
	def __init__( self, *args ):
		"""
		@param args: 初始化参数
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._param2 = 0.0
		self._param3 = "Monster"		# 默认为Monster
		self._param4 = 0.0
		self._aiCmd = None				# AI指令标识（Int16）
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )			# className
		self._param2 = section.readFloat( "param2" )			#范围
		self._param3 = section.readString( "param3" )			# EntityType
		self._param4 = section.readFloat( "param4" )			# 怪物销毁延迟
		self._aiCmd = section.readInt( "param5" )			# AI指令标识（Int16）

	def query( self, player ) :
		"""
		是否可接任务
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""

		monsterList = player.entitiesInRangeExt( self._param2, self._param3, player.position )
		for i in monsterList:
			if i.className == self._param1 and i.getOwner() and i.getOwner() == player:
				i.onAICommand( i.id, i.className, self._aiCmd )					# 直接使用onAICommand是防止e是一个ghost这个方法也能用
				if self._param4 <= 0:
					i.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
				else:
					i.addTimer( self._param4, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

class QTSShowPatrol( QTScript ):
	"""
	客户端显示摆点路径箭头指引
	"""
	def __init__( self ):
		self._param1 = ""

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )	#摆点路径
		self._param2 = section.readString( "param2" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.client.onShowPatrol( self._param1, self._param2 )

	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass

class QTSPlaySoundFromGender:
	"""
	根据性别选择播放音频
	"""
	def __init__( self ):
		self._param1 = ""
		self._param2 = 0
		self._param3 = ""

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )	#音频文件路径(男性)
		self._param2 = section.readString( "param2" )	#音频文件路径（女性）
		self._param3 = section.readInt( "param3" )	#音频类型 2D/3D
		self._param4 = section.readString( "param4" )   #NPC的className
		self._priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_QUEST


	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		acceptTargetID = 0
		for en in player.entitiesInRangeExt( 30, "NPC", player.position ):
			if hasattr(en,"className") and en.className == self._param4:
				acceptTargetID = en.id
		if player.getGender() == csdefine.GENDER_MALE:
			player.client.playSound( self._param1, self._param3, acceptTargetID, self._priority )
		elif player.getGender() == csdefine.GENDER_FEMALE:
			player.client.playSound( self._param2, self._param3, acceptTargetID, self._priority )
	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass

class QTSSetAutoNextQuestFlag( QTScript ):
	"""

	"""
	def __init__( self ):
		QTScript.__init__( self )

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.setTemp( Const.QUEST_AUTO_OPEN_NEXT_KEY, tasks.getQuestID() )

class QTSShowHeadPortrait( QTScript ):
	"""
	让玩家显示界面提示信息
	"""
	def __init__( self ):
		self.type = 0
		self.headTextureID = ""
		self.text = ""
		self.monsterName = ""
		self.lastTime = 0.0

	def init( self, section ):
		"""
		@param args: 初始化参数
		@type  args: pyDataSection
		"""
		self.type = section.readInt( "param1" )
		self.headTextureID = section.readString( "param2" )
		param3 = section.readString( "param3" ).split( ";" )
		self.text = param3[0]
		if len( param3 ) > 1:
			self.monsterName = param3[1]
		self.lastTime = section.readFloat( "param4" )

	def query( self, player ):
		"""
		查询脚本是否能执行

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		执行脚本；

		注意：此处不做任何执行前的检查。

		@return: 无
		"""
		player.client.showHeadPortraitAndText( self.type, self.monsterName, self.headTextureID, self.text, self.lastTime )
		if self.monsterName:
			player.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, self.monsterName, self.text, [] )
		else:
			player.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_MESSAGE, 0, player.getName(), self.text, [] )

	def onAbandoned( self, player, questData = None ):
		"""
		当任务被放弃时是否要做点什么事
		"""
		pass

# 注册各类型
MAP_QUEST_SCRIPT_TYPE( QTSRemoveSpecialFlag )	# flag
MAP_QUEST_SCRIPT_TYPE( QTSSetSpecialFlag )		# flag, value
MAP_QUEST_SCRIPT_TYPE( QTSGiveItems )			# <value>	itemID, amount	</value>	...... more
MAP_QUEST_SCRIPT_TYPE( QTSSummonNPC )			# npcID
MAP_QUEST_SCRIPT_TYPE( QTSSummonOwnMonster)		# npcID
MAP_QUEST_SCRIPT_TYPE( QTSSummonRoleTypeMonsters )	# npcID's set
MAP_QUEST_SCRIPT_TYPE( QTSRemoveItem )			# itemID, amount
MAP_QUEST_SCRIPT_TYPE( QTSFallowNPC )			# itemID, amount
MAP_QUEST_SCRIPT_TYPE( QTSGivePictures )		# itemID, amount
MAP_QUEST_SCRIPT_TYPE( QTSGnerateDart )			# itemID, amount
MAP_QUEST_SCRIPT_TYPE( QTSAfterMissionComplete )
MAP_QUEST_SCRIPT_TYPE( QTSCheckItem )
MAP_QUEST_SCRIPT_TYPE( QTSCheckLevel )
MAP_QUEST_SCRIPT_TYPE( QTSCheckDeposit )
MAP_QUEST_SCRIPT_TYPE( QTSNotHasQuestType )
MAP_QUEST_SCRIPT_TYPE( QTSIsCaptain )
MAP_QUEST_SCRIPT_TYPE( QTSSetFaction )
MAP_QUEST_SCRIPT_TYPE( QTSAfterFamilyComplete )
MAP_QUEST_SCRIPT_TYPE( QTSAfterTongComplete )
MAP_QUEST_SCRIPT_TYPE( QTSAddDartCount )
MAP_QUEST_SCRIPT_TYPE( QTSCheckPrestige )
MAP_QUEST_SCRIPT_TYPE( QTSAfterCompleteOpenBank )
MAP_QUEST_SCRIPT_TYPE( QTSAfterFallowNPC )
MAP_QUEST_SCRIPT_TYPE( QTSAfterGiveGens )
MAP_QUEST_SCRIPT_TYPE( QTSGiveYinpiao )
MAP_QUEST_SCRIPT_TYPE( QTSAfterDeleteItem )
MAP_QUEST_SCRIPT_TYPE( QTSBuKaoMoney )
MAP_QUEST_SCRIPT_TYPE( QTSAddBuff )
MAP_QUEST_SCRIPT_TYPE( QTSAfterRemoveQuestionType )
MAP_QUEST_SCRIPT_TYPE( QTSSetQuestionType )
MAP_QUEST_SCRIPT_TYPE( QTSRemoveQuestLog )
MAP_QUEST_SCRIPT_TYPE( QTSRemoveRobFlags )
MAP_QUEST_SCRIPT_TYPE( QTSAfterSetKaStone )
MAP_QUEST_SCRIPT_TYPE( QTAddBuff )
MAP_QUEST_SCRIPT_TYPE( QTRemoveBuff )
MAP_QUEST_SCRIPT_TYPE( QTBuffBanTask )
MAP_QUEST_SCRIPT_TYPE( QTSTalkFunction )
MAP_QUEST_SCRIPT_TYPE( QTSWithoutBuff )
MAP_QUEST_SCRIPT_TYPE( QTSRequestTeach )
MAP_QUEST_SCRIPT_TYPE( QTSRecordLevel )
MAP_QUEST_SCRIPT_TYPE( QTSCleanRecordLevel )
MAP_QUEST_SCRIPT_TYPE( QTSStartHelpNPC )
MAP_QUEST_SCRIPT_TYPE( QTSShowQuestMsg )
MAP_QUEST_SCRIPT_TYPE( QTSDestroyNPC )
MAP_QUEST_SCRIPT_TYPE( QTSTeleport )
MAP_QUEST_SCRIPT_TYPE( QTSUnfoldScroll )
MAP_QUEST_SCRIPT_TYPE( QTSAddPersistentFlag )
MAP_QUEST_SCRIPT_TYPE( QTSRemovePersistentFlag )
MAP_QUEST_SCRIPT_TYPE( QTSOpenDoor )
MAP_QUEST_SCRIPT_TYPE( QTSHideNPCModel )
MAP_QUEST_SCRIPT_TYPE( QTSAfterUseSkill )	#add by wuxo 2011-9-21
MAP_QUEST_SCRIPT_TYPE( QTSUseSkill )	#add by wuxo 2011-10-8
MAP_QUEST_SCRIPT_TYPE( QTSSetOffLineFailed )	#add by wuxo 2011-12-29
MAP_QUEST_SCRIPT_TYPE( QTSPlaySound ) #add by wuxo 2012-1-17
MAP_QUEST_SCRIPT_TYPE( QTSPlayVideo )
MAP_QUEST_SCRIPT_TYPE( QTSSendAICmd )
MAP_QUEST_SCRIPT_TYPE( QTSSendAICmd_Abandon )
MAP_QUEST_SCRIPT_TYPE( QTSOn3C )
MAP_QUEST_SCRIPT_TYPE( QTSOn3C_Abandon )
MAP_QUEST_SCRIPT_TYPE( QTSAfterRemoveItem ) # add by dqh
MAP_QUEST_SCRIPT_TYPE( QTSNotifySpaceCMgr ) # add by dqh
MAP_QUEST_SCRIPT_TYPE( QTSFlyPatrol ) # add by ganjinxing
MAP_QUEST_SCRIPT_TYPE( QTSProduceMonsterAndTrap ) # add by hezhiming
MAP_QUEST_SCRIPT_TYPE( QTSSummonMonster ) # add by hezhiming
MAP_QUEST_SCRIPT_TYPE( QTSDestroyMonster ) # add by hezhiming
MAP_QUEST_SCRIPT_TYPE( QTSSummonMonster_Abandon ) # add by hezhiming
MAP_QUEST_SCRIPT_TYPE( QTSShowPatrol ) #add by wuxo 2013-12-18
MAP_QUEST_SCRIPT_TYPE( QTSPlaySoundFromGender )
MAP_QUEST_SCRIPT_TYPE( QTSTeleportPlane )	#add by gjx
MAP_QUEST_SCRIPT_TYPE( QTSSetAutoNextQuestFlag )
MAP_QUEST_SCRIPT_TYPE( QTSShowHeadPortrait )
MAP_QUEST_SCRIPT_TYPE( QTSTeleportPlaneOnAbandoned )
MAP_QUEST_SCRIPT_TYPE( QTSTeleportPlaneOnCompleted )
