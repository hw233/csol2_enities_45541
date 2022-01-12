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


# ӳ������ű���ʵ��������
# ��ӳ����Ҫ���ڴ������г�ʼ��ʵ��ʱʹ��
# key = Ŀ�������ַ�����ȡ�Ը����͵�������;
# value = �̳���QTScript���࣬���ڸ�������ʵ��������Ķ���
quest_script_type_maps = {}

def MAP_QUEST_SCRIPT_TYPE( classObj ):
	"""
	ӳ������Ŀ��������ʵ��������
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
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		pass

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass

	def onAbandoned( self, player, questData = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass

class QTSRemoveSpecialFlag:
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._flag = section.readString( "param1" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
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
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		self.do( player )	# ��������ʱҲҪȥ����־

class QTSSetSpecialFlag:
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._flag = section.readString( "param1" )
		self._value = section.readInt( "param2" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		try:
			d = player.getMapping()["questSpecialFlag"]
		except KeyError:
			d = {}
			player.getMapping()["questSpecialFlag"] = d
		d[self._flag] = self._value

class QTAddBuff( QTScript ):
	"""
	����ʼʱ�������buff by����
	"""
	def __init__( self, *args ):
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questBuffSkillID = section.readString( "param1" )
		self.tasks = None

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
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
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._banBuffIDs = []
		for i in xrange( 1, 6 ):
			par = section.readString( "param" + str( i ) )
			if par: self._banBuffIDs.append( int( par ) )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass

class QTSGiveItems:
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._items = []
		for itemID, amount in args:
			self._items.append( itemID, amount )

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		for sec in section.values():
			self._items.append( ( sec.readInt( "itemID" ), sec.readInt( "amount" ) ) )

	def __itemFilter( self, itemList,player ):
		"""
		����itemList:
		1.��ɫ������û�и���Ʒ�������ɫ�涨�����ĸ���Ʒ
		2.��ɫ�������и���Ʒ�������������������ɫ������ֵ�ĸ���Ʒ
		3.��ɫ�������и���Ʒ���������㹻���򲻸�����Ʒ
		@return: No
		"""
		addItems = []
		for itemID, iAmount in itemList:
			kitBagItems = player.findItemsByIDFromNKCK( itemID )#�ӱ�����ȡ����ͬ����Ʒ����ֵ��ʾ��ɫû�����item������Ҫ��������
			item = items.instance().createDynamicItem( itemID, iAmount )
			amount = 0
			if not kitBagItems:
				addItems.append( item )
				continue
			else:
				for tempItem in kitBagItems:
					amount += tempItem.amount
			if item.amount > amount: #��ɫ��item�������㣬����ٸ�����
				item.setAmount( item.amount-amount )
				addItems.append( item )
		return addItems

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���
		ע�⣺�˴������κ�ִ��ǰ�ļ�顣
		@return: ��
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
		@param args: ��ʼ������
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
	ɾ��һ����Ʒ
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		self._itemID = ""
		self._amount = 1
		if len( args ) >= 2:
			self._itemID = args[0]
			self._amount = args[1]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._itemID = section.readInt( "param1" )
		self._amount = section.readInt( "param2" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True		# �����κμ�飬Ҳ����˵���ָ������Ʒ���������������ɾ��

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.removeItemTotal( self._itemID, self._amount, csdefine.DELETE_ITEM_QTSREMOVEITEM )

class QTSAfterRemoveItem( QTSRemoveItem ):
	"""
	�������ʱɾ���������
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		QTSRemoveItem.__init__( self, *args )

	def do( self, player, tasks = None ):
		"""
		���������ɾ���������
		"""
		remainAmount = player.countItemTotal_( self._itemID )
		if self._amount > remainAmount: # �������û��ô���ˣ�����Ҫ��ʣ�µ�ɾ��
			player.removeItemTotal( self._itemID, remainAmount, csdefine.DELETE_ITEM_QTSREMOVEITEM )
		else:
			player.removeItemTotal( self._itemID, self._amount, csdefine.DELETE_ITEM_QTSREMOVEITEM )

	def onAbandoned( self, player, questData = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass

class QTSSummonNPC:
	"""
	�ٻ�һ��NPC
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._position = ""
		self._direction = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( %s ) Bad format '%s' in section param2 " % ( self.__class__.__name__, position ) )
			else:
				self._position = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( %s ) Bad format '%s' in section param3" % ( self.__class__.__name__, direction ) )
			else:
				self._direction = dir

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pos = Math.Vector3( player.position )
		direction = player.direction

		pos.x = player.position.x  +  random.random() * random.randint( -3, 3 )
		pos.z = player.position.z  +  random.random() * random.randint( -3, 3 )

		if self._position:
			pos = self._position
		if self._direction:
			direction = self._direction

		# �ٻ������ʱ��Ե��������ײ����������������
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y

		entity = player.createObjectNearPlanes( self._param1, pos, direction, { "spawnPos" : tuple( pos ) } )
		# ���ٻ���������������⴦��ֱ��������bootyOwner
		getEnemyTeam = getattr( player, "getTeamMailbox", None )	# ����ж������¼����mailbox
		if getEnemyTeam and getEnemyTeam():
			entity.bootyOwner = ( player.id, getEnemyTeam().id )
		else:
			entity.bootyOwner = ( player.id, 0 )
		entity.firstBruise = 1		# ����Monster�е�һ�����˺���bootyOwner����


class QTSFallowNPC( QTSSummonNPC ):
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._position = ""
		self._direction = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )

		position = section.readString( "param3" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( %s ) Bad format '%s' in section param3 " % ( self.__class__.__name__, position ) )
			else:
				self._position = pos

		direction = section.readString( "param4" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( %s ) Bad format '%s' in section param4" % ( self.__class__.__name__, direction ) )
			else:
				self._direction = dir

	def do( self, player, tasks = None ):
		"""
		"""
		#entity = BigWorld.entities.get( player.targetID )
		# ���ȡ��ɢ��
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

		# �ٻ������ʱ��Ե��������ײ����������������
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
		�ٻ����ͬ����
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
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
		�ٻ������ģ����ְҵ��ͬ�Ĺ�
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._params = {csdefine.CLASS_FIGHTER:[],		#սʿ
			csdefine.CLASS_SWORDMAN:[],					#����
			csdefine.CLASS_MAGE:[],						#��ʦ
			csdefine.CLASS_ARCHER:[]					#����
		}

	def init( self, section ):
		"""
		����Ҫ��սʿ���͵Ĺ�����param1��Ӧ���������͵Ĺ�����param2��Ӧ��
		��ʦ���͵Ĺ�����param3��Ӧ���������͵Ĺ�����param4��Ӧ��
		@param args: ��ʼ������
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
	�����ڳ�
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._dartCarEntityID = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self.dartPropertySection = Language.openConfigSection("")

		self._dartCarEntityIDs	= section.readString( "param1" )	#Ҫ���ɵ��ڳ�ʵ��ID�б�
		self._destNPCID			= section.readString( "param2" )	#Ŀ��NPC��ID
		self._factionID			= section.readInt( "param3" )		#�ھ�����ID
		self._questID			= section.readInt( "param4" )		#����ID
		self._eventIndex		= section.readInt( "param5" )		#����Ŀ������
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
		��ѯ�ű��Ƿ���ִ��
		@return: Bool
		@rtype:  Bool
		"""
		#�����ҵ��ھ�����С��0����û�н�����ʦƾ֤
		return True

	def do( self, player, tasks = None ):
		"""
		"""
		#entity = BigWorld.entities.get( player.targetID )
		# ���ȡ��ɢ��
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
		player.set( "dartStartMapPoint", point )	# ���ý���ʱ���ھֻ��֡��������������ʧ�ܶ�Ҫ����˱��

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
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		if len( args ) > 2:
			self.itemID = int( args[0] )
			self.amount = int( args[1] )
			self.npcClassName = str( args[2] )

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self.itemID = section.readInt( "param1" )
		self.amount = section.readInt( "param2" )
		self.npcClassName = section.readString( "param3" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���
		ע�⣺�˴������κ�ִ��ǰ�ļ�顣
		@return: ��
		"""
		item = items.instance().createDynamicItem( self.itemID, self.amount )
		item.set("pictureIntentionTargetID", self.npcClassName )
		player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTSGIVEITEMS )


class QTSAfterMissionComplete:
	"""
	���������������������ͷ�������
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._factionID		= section.readInt( "param1" )		#�ھ�����id
		self._completeVal	= section.readInt( "param2" )		#����������ӵ�����ֵ
		self._abandoneVal	= section.readInt( "param3" )		#������ʧ�ܼ��ٵ�����ֵ
		self._questType		= section.readInt( "param4" )		#��������(5Ϊ���ڣ�6Ϊ����)
		self._abandonedFlag	= {37:"sm_dartNotoriousXinglong", 38:"sm_dartNotoriousChangping"}
		self._completedFlag	= {37:"sm_dartCreditXinglong", 38:"sm_dartCreditChangping"}

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		�������
		"""
		player.base.addDartData( self.getKey( self._factionID, True ), self._completeVal )
		#BigWorld.globalData['DartManager'].onReceiveDestoryCommand( player.getName() )
		player.client.updateTitlesDartRob( self._factionID )
		if self._questType == csdefine.QUEST_TYPE_DART:	# ����
			player.remove( "dartStartMapPoint" )
		elif self._questType == csdefine.QUEST_TYPE_ROB:	# ����
			dartPointDict = eval( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_DART_POINT ) )
			if player.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ):	# ���ڳɹ������ھֻ���+1���Է�-1����ʼ����50����0���ټ�
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
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		value = 0 - self._completeVal	#����һ�����������൱�ڼ���������
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
	�������ʱ�����������ӵ�buff by����
	"""
	def __init__( self, *args ):
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questBuffSkillID		= section.readInt( "param1" )		# ���������buff�ļ���IDs

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
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
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
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
	�����������Ҫ����Ʒ�Ƿ���ȫ
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._itemID	= section.readInt( "param1" )		#������Ʒ��ID
		self._itemAmount= section.readInt( "param2" )		#������Ʒ����
		self._dialog	= section.readString( "param3" )	#ȱ����Ʒ�Ķ԰�
		self._npcClassName = section.readString( "param4" )	#�������NPC className

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.removeItemTotal( self._itemID, 1, csdefine.DELETE_ITEM_QTSCHECKITEM )	#�Ƴ�������Ҫ����Ʒ

class QTSCheckLevel:
	"""
	��������ļ����Ƿ����
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._minLevel		= section.readInt( "param1" )			#����������ͼ���
		self._maxLevel		= section.readInt( "param2" )			#����������߼���
		self._minLevTalk	= section.readString( "param3" )		#���𲻹��Ķ԰�
		self._maxLevTalk	= section.readString( "param4" )		#������ߵĶ԰�
		self._npcClassName	= section.readString( "param5" )		#�������NPC className


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass


class QTSCheckDeposit:
	"""
	������Ͻ�Ǯ�Ƿ��㹻��Ѻ��
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._deposit		= section.readInt( "param1" )			#Ѻ������
		self._dialog		= section.readString( "param2" )		#Ѻ�𲻹��԰�
		self._npcClassName	= section.readString( "param3" )			#�������NPC className


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		if player.iskitbagsLocked():	# ����������by����
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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		if not player.payMoney( self._deposit, csdefine.CHANGE_MONEY_DEPOSIT ):
			player.statusMessage( csstatus.TONG_RUNTRADE_MONEY_NOTENOUGTH )
			return
		#��Ǯ��ʾ��ʽ�任 by����
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
	�����������Ƿ����ˣ��٣�������
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questType		= section.readInt( "param1" )			#��������
		self._dialog		= section.readString( "param2" )		#���д�����������ʾ�԰�
		self._dialog_op		= section.readString( "param3" )		#����ж�������������ʾ�԰�
		self._factionID		= section.readInt( "param4" )			#�ھ���������id(Ŀǰֻ���ھ���Ҫ���ô˲���)
		self._npcClassName	= section.readString( "param5" )			#�������NPC className


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass

class QTSIsCaptain:
	"""
	�����ܰ�����ڵ�����Ƿ���������ʸ�
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		questsStr			= section.readString( "param1" )		#����id
		self._dialog		= section.readString( "param2" )		#���ǰ����Ķ԰�
		self._distance		= section.readInt( "param3" )			#������Χ�ڶ��پ�������
		self._npcClassName	= section.readInt( "param4" )			#�������NPC className
		self._quests = []
		for i in questsStr.split('|'):
			self._quests.append( i.split(':') )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		#�жϽ����������Ƿ��Ǽ������

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.setTemp( "needSendTongQuest", {"dis":self._distance, "qus":self._quests} )

class QTSSetFaction:
	"""
	�����ھ�����
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questID		= section.readInt( "param1" )			#����id
		self._factionID		= section.readInt( "param2" )			#�ھ�����id

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		tasks.set( "factionID", self._factionID )
		#player.questsTable._quest( self._questID )._tasks
		#dQuest = player.getQuest( self._questID )
		#dQuest.setFaction( self._factionID )


class QTSAddDartCount:
	"""
	�������ڴ���
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._dartType		= section.readInt( "param1" )			#�ھ���������
		self._value			= section.readInt( "param2" )			#����ֵ

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.questTongDartRecord.dartCount += self._value


	def onAbandoned( self, player, questData = None ):
		"""
		"""
		player.questTongDartRecord.dartCount -= self._value


class QTSAfterFamilyComplete:
	"""
	�������������Ҫ�������¼�
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		questsStr			= section.readString( "param1" )		#����id
		#self._questID		= section.readInt( "param1" )			#����id
		self._eventIndex	= section.readInt( "param2" )			#����Ŀ������
		self._distance		= section.readInt( "param3" )			#����

		self._quests = []
		for i in questsStr.split('|'):
			self._quests.append( i.split(':') )
		self._quests.reverse()

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
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
		���峤������������ʱ��Ӧ���ǽ��˴������ȫ������Ա�����񶼱�ʧ��
		"""
		#��Ϊ�峤��������ʱ����һ�����н��˴��������Ҷ����ߣ������峤�����������������������Ҫ֪ͨ�����Ա����ʧ��
		#��ΪֻҪ�鳤���������������˿϶�Ҳ��ɲ�����
		pass

class QTSAfterTongComplete:
	"""
	������������Ҫ�������¼�
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		questsStr			= section.readString( "param1" )		#����id
		#self._questID		= section.readInt( "param1" )			#����id
		self._eventIndex	= section.readInt( "param2" )			#����Ŀ������
		self._distance		= section.readInt( "param3" )			#����

		self._quests = []
		for i in questsStr.split('|'):
			self._quests.append( i.split(':') )
		self._quests.reverse()

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
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
		���峤������������ʱ��Ӧ���ǽ��˴������ȫ������Ա�����񶼱�ʧ��
		"""
		#��Ϊ�峤��������ʱ����һ�����н��˴��������Ҷ����ߣ������峤�����������������������Ҫ֪ͨ�����Ա����ʧ��
		#��ΪֻҪ�鳤���������������˿϶�Ҳ��ɲ�����
		pass

class QTSCheckPrestige:
	"""
	�������ھ������Ƿ��㹻������
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._factionID		= section.readInt( "param1" )			#�ھ�����
		self._requestPres	= section.readInt( "param2" )			#�ܹ��Ӵ����������ھ�����
		self._dialog		= section.readString( "param3" )		#������������ʾ�԰�
		self._npcClassName	= section.readString( "param4" )			#�������NPC className


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass


class QTSAfterCompleteOpenBank:
	"""
	���������������������ͷ�������
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		�������
		"""
		player.bank_activateBag()


	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass

class QTSAfterFallowNPC:
	"""
	�����������������ɾ������ʱ���ɱ��NPC
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		�������
		"""
		# ������
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		ids = tasks.query( "follow_NPC" , [] )
		for id in ids:
			if BigWorld.entities.has_key( id ):
				# ɱ�����NPC
				BigWorld.entities[ id ].remoteCall( "destroy", () )
		# ������
		tasks.set( "follow_NPC" , [] )

class QTSAfterGiveGens:
	"""
	�����������������ɾ������ʱ���ɱ��NPC
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		�������
		"""
		# ������
		player.ptn_questActiveTrainGem()
		#player.client.showTrainGem()

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass


class QTSGiveYinpiao:
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._itemInfo = []

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		itemID = section.readInt( "param1" )
		amount = section.readInt( "param2" )
		initValue = section.readInt( "param3" )
		maxValue = section.readInt( "param4" )
		self._itemInfo = [ itemID, amount, initValue, maxValue ]

	def __itemFilter( self, itemInfoList, player ):
		"""
		����itemInfoList:
		1.��ɫ������û�и���Ʒ�������ɫ�涨�����ĸ���Ʒ
		2.��ɫ�������и���Ʒ�������������������ɫ������ֵ�ĸ���Ʒ
		3.��ɫ�������и���Ʒ���������㹻���򲻸�����Ʒ
		@return: No
		"""
		item = items.instance().createDynamicItem( itemInfoList[0], itemInfoList[1] )
		item.set( "yinpiao", itemInfoList[2] )
		item.set( "maxYinpiao", itemInfoList[3] )

		addItems = []
		kitBagItems = player.findItemsByIDFromNKCK( itemInfoList[0] )#�ӱ�����ȡ����ͬ����Ʒ����ֵ��ʾ��ɫû�����item������Ҫ��������
		amount = 0
		if not kitBagItems:
			addItems.append( item )
		else:
			for tempItem in kitBagItems:
				amount += tempItem.amount
			if item.amount > amount: # ��ɫ��item�������㣬����ٸ�����
				item.setAmount( item.amount-amount )
				addItems.append( item )
		return addItems

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���
		ע�⣺�˴������κ�ִ��ǰ�ļ�顣
		@return: ��
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
	���������ɾ����Ӧ��������Ʒ
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		self._itemID = ""
		self._amount = 1
		if len( args ) >= 2:
			self._itemID = args[0]
			self._amount = args[1]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._itemID = section.readInt( "param1" )
		self._amount = section.readInt( "param2" )

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		remainAmount = player.countItemTotal_( self._itemID )
		if self._amount > remainAmount: # �������û��ô���ˣ�����Ҫ��ʣ�µ�ɾ��
			player.removeItemTotal( self._itemID, remainAmount, csdefine.DELETE_ITEM_QTSAFTERDELETEITEM )
		else:
			player.removeItemTotal( self._itemID, self._amount, csdefine.DELETE_ITEM_QTSAFTERDELETEITEM )



class QTSBuKaoMoney:
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._money = section.readInt( "param1" )


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		if player.money < self._money:
			player.statusMessage( csstatus.BANK_MONEY_NOT_ENOUGH_TO_STORE )
			return False

		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���
		ע�⣺�˴������κ�ִ��ǰ�ļ�顣
		@return: ��
		"""
		player.payMoney( self._money, csdefine.CHANGE_MONEY_BUKAO )

class QTSAddBuff:
	"""
	�������������һ��buff
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		self._skillID = 0

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._skillID = section.readInt( "param1" )

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		Love3.g_skills[self._skillID].receiveLinkBuff( player, player )


class QTSSetQuestionType:
	"""
	���ûش���ʽ��������
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._type		= section.readInt( "param1" )			#����id


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.set("question_type", self._type )


class QTSAfterRemoveQuestionType:
	"""
	���ûش���ʽ��������
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._type		= section.readInt( "param1" )			#����id


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.remove("question_type")


class QTSRemoveQuestLog:
	"""
	ɾ��һ�������¼
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		self._questID = 0
		if len( args ) >= 1:
			self._questID = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questID = section.readInt( "param1" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True		# �����κμ�飬Ҳ����˵���ָ������Ʒ���������������ɾ��

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.questsLog.remove( self._questID )



class QTSRemoveRobFlags:
	"""
	ɾ���ٷ˱�־
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		self._leaveTime = 0
		if len( args ) >= 1:
			self._leaveTime = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._leaveTime = section.readInt( "param1" )			#��λ����

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True		# �����κμ�飬Ҳ����˵���ָ������Ʒ���������������ɾ��

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		#player.setTemp( "robDart_timerID", player.addTimer( self._leaveTime, 0, ECBExtend.REMOVE_ROB_FLAG ) )
		player.set("RobEndTime", time.time() + self._leaveTime )



class QTSAfterSetKaStone:
	"""
	����������û���ʯ
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._itemID	= section.readInt( "param1" )			# Ҫ���õĻ���ʯ��ƷID
		self._ka_count	= section.readInt( "param2" )			# Ҫ���óɵ���ֵ

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		item = player.findItemFromNKCK_( self._itemID )			# �ҵ���Ҫ���õĻ���ʯ��Ʒ
		if item:
			item.set( 'ka_count',self._ka_count, player )
		else:
			INFO_MSG( "û���ҵ������Ļ���ʯ���޷�������ֵ��" )

	def onAbandoned( self, player, tasks = None ):
		"""
		"""
		pass


class QTSTalkFunction:
	"""
	ִ�жԻ�����
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._key = section.readString( "param1" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.gossipWith(player.id, player.targetID, self._key)

class QTSWithoutBuff:
	"""
	����ɫ�Ƿ�û����Ӧ��buff
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._buffID = section.readInt( "param1" )		# buffID
		self._dialog = section.readString( "param2" )	# ��buff�Ķ԰�
		self._npcClassName	= section.readString( "param3" )	#�������NPC className

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass


class QTSRequestTeach:
	"""
	�����������Ѱ��ʦ���Ĺ㲥
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount )
		"""
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		pass

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast( cschannel_msgs.BCT_JSGX_FIND_TEACHER, [] )

	def onAbandoned( self, player, tasks = None ):
		"""
		"""
		pass


class QTSRecordLevel:
	"""
	��¼������ȼ�
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questID = section.readInt( "param1" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.set("recordQuestLevel_%i"%self._questID, player.level )



class QTSCleanRecordLevel:
	"""
	�����¼������ȼ�
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questID = section.readInt( "param1" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
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
	��ʼ����
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._className1 = section.readString( "param1" )				#����NPC
		self._className2s = section.readString( "param2" ).split(":")				#��Ҫ������NPC
		self._range		= section.readInt( "param3" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

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
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
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
	�ݻ�NPC
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._className = section.readString( "param1" )			#Ŀ��NPC
		self._range = section.readInt( "param2" )					#��Χ


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		npcs = player.entitiesInRangeExt( self._range, "NPC", player.position )
		for i in npcs:
			if i.className == self._className:
				i.destroy()


class QTSShowQuestMsg:
	"""
	��ʾ�������
	"""
	def __init__( self, *args ):
		"""
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._msg = section.readString( "param1" )				#Ŀ��NPC


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.client.showQuestMsg( self._msg )

class QTSTeleport( QTScript ):
	"""
	�����ﴫ�͵�ĳ���ռ� by mushuang
	"""
	def __init__( self, *args ):
		"""
		"""
		self.spaceType = ""
		self.direction = ( 0, 0, 0 )
		self.position = ( 0, 0, 0 )

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		# Param1: Ŀ��ռ����ͣ�����fengming
		# Param2: ���ͷ���x,y,z���������ÿո���������磺1.2 10.1 100.0
		# Param3: ����λ�ã���ʽͬ��

		self.spaceType = section.readString( "param1" )				# Ŀ��ռ�

		# ��ȡ����
		array = section.readString( "param2" ).strip().split()
		assert len( array ) == 3
		self.direction = tuple( [ float( e ) for e in array ] )

		# ��ȡλ��
		array = section.readString( "param3" ).split()
		assert len( array ) == 3
		self.position = tuple( [ float( e ) for e in array ] )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.gotoSpace( self.spaceType, self.position, self.direction )


class QTSTeleportPlane( QTScript ):
	"""
	�����ﴫ�͵�ĳ��λ�� by ganjinxing
	"""
	def __init__( self, *args ):
		"""
		"""
		self.spaceType = ""

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		# Param1: Ŀ��ռ����ͣ�����fengming
		self.spaceType = section.readString( "param1" )				# Ŀ��ռ�

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.enterPlane(self.spaceType)

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		self.do(player, tasks)


class QTSTeleportPlaneOnAbandoned( QTSTeleportPlane ):
	"""
	���������͵�ĳ��λ�� by ganjinxing
	"""
	def __init__( self, *args ):
		"""
		"""
		QTSTeleportPlane.__init__( self, *args )

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		pass

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		player.enterPlane(self.spaceType)


class QTSTeleportPlaneOnCompleted( QTSTeleportPlane ):
	"""
	��������͵�ĳ��λ�� by ganjinxing
	"""
	def __init__( self, *args ):
		"""
		"""
		QTSTeleportPlane.__init__( self, *args )

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.enterPlane(self.spaceType)

	def onAbandoned( self, player, tasks = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass


class QTSUnfoldScroll( QTScript ):
	"""
	չ��һ������ by mushuang
	"""
	def __init__( self, *args ):
		"""
		"""
		self.scrollID = 0

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		# Param1: �����ID

		self.scrollID = section.readInt( "param1" ) # �����ID

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.client.unfoldScroll( 0, self.scrollID )


class QTSAddPersistentFlag:
	"""
	���Ӵ洢��־
	"""
	def __init__( self, *args ):
		"""
		"""
		self.param1 = 0

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		# Param1: �����ID

		self.param1 = section.readInt( "param1" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.addPersistentFlag( self.param1 )


class QTSRemovePersistentFlag:
	"""
	�Ƴ��洢��־
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
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		player.removePersistentFlag( self.param1 )



class QTSOpenDoor( QTScript ):
	"""
	���� by mushuang
	"""
	def __init__( self, *args ):
		"""
		"""
		self.doorClassName = ""

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection

		"""
		self.available = True
		# Param1: �ŵ�className���ַ�����( ���磺20251051 )
		self.doorClassName = section.readString( "param1" )

		assert self.doorClassName != "", "Incorrect config in param1, entity className needed!"

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		assert self.available, "Incorrect config, quest script failed to run!"

		spaceBase = player.getCurrentSpaceBase()
		assert hasattr( spaceBase, "openDoor" ), "Current space entity doesn't have base method: \'openDoor\'! Quest script failed to run!"

		spaceBase.openDoor( { "entityName" : self.doorClassName } )

class QTSHideNPCModel( QTScript ):
	# ����/����NPC
	def __init__( self, *args ):
		self.NPCClass = ""
		self.isDestroy = False
		self.hideTime = 0

	def init( self, section ):
		"""
		@param args: ��ʼ������
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
		��ѯ�ű��Ƿ���ִ��
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
	������ɺ󣬲��ż���add by wuxo 2011-9-20
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		"""
		self._skillID = 0
		self._NPCID   = ""

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._skillID = section.readInt( "param1" )  #����ID
		self._NPCID   = section.readString( "param2" )  #�����ύNPCID

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��
		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���
		ע�⣺�˴������κ�ִ��ǰ�ļ�顣
		@return: ��
		"""
		commitTargetID = 0
		for en in player.entitiesInRangeExt( 30, None, player.position ):
			if hasattr(en,"className") and en.className == self._NPCID:
				commitTargetID = en.id
				break
		player.spellTarget( self._skillID, commitTargetID )	#ʹ�ü���,����Ŀ��ʵ�岻���ڵ����


	def onAbandoned( self, player, tasks = None ):
		"""
		��������ʱ
		ִ�нű�
		"""
		pass

class QTSUseSkill:
	"""
	��������ʱ�����ż���add by wuxo 2011-10-8
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		"""
		self._skillID = 0
		self._NPCID   = ""

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._skillID = section.readInt( "param1" )  #����ID
		self._NPCID   = section.readString( "param2" )  #������ȡNPCID
		self._type    = section.readString( "param3" )  #����Ŀ������

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��
		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���
		ע�⣺�˴������κ�ִ��ǰ�ļ�顣
		@return: ��
		"""
		acceptTargetID = 0
		if self._type == "Role":
			acceptTargetID = player.id
		else:
			for en in player.entitiesInRangeExt( 30, self._type, player.position ):
				if hasattr(en,"className") and en.className == self._NPCID:
					acceptTargetID = en.id
					break
		player.spellTarget( self._skillID, acceptTargetID )	#ʹ�ü���,����Ŀ��ʵ�岻���ڵ����


class QTSSetOffLineFailed:
	"""
	��������ʱ��������������ʧ�ܱ��add by wuxo 2011-12-29
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		"""
		self._questOffLineFail = None

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._questOffLineFail = section.readInt( "param1" )  #����ID


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��
		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���
		ע�⣺�˴������κ�ִ��ǰ�ļ�顣
		@return: ��
		"""
		quest_failFlag = player.queryTemp( "questOffLineFail", [] )
		quest_failFlag.append(self._questOffLineFail)
		player.setTemp( "questOffLineFail", quest_failFlag )

	def onAbandoned( self, player, questData = None ):
		"""
		��������
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
	������Ƶ add by wuxo 2012-1-17
	"""
	def __init__( self ):
		self._param1 = ""
		self._param2 = 0
		self._param3 = ""

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )	#��Ƶ�ļ�·��
		self._param2 = section.readInt( "param2" )	#��Ƶ���� 2D/3D
		self._param3 = section.readString( "param3" )   #NPC��className
		self._priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_QUEST


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		acceptTargetID = 0
		for en in player.entitiesInRangeExt( 30, "NPC", player.position ):
			if hasattr(en,"className") and en.className == self._param3:
				acceptTargetID = en.id
		player.client.playSound( self._param1, self._param2, acceptTargetID, self._priority )

	def onAbandoned( self, player, questData = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass


class QTSPlayVideo:
	"""
	������Ƶ
	"""
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )			#��Ƶ�ļ�����

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.client.playVideo( self._param1 )


class QTSSendAICmd( QTScript ) :
	"""
	ָ֪ͨ��NPCִ��AIָ������ڽ����񣬽�����
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._npcID = ""								# ����ָ���NPC��ID
		self._radius = 0								# �����뾶
		self._aiCmd = None								# AIָ���ʶ��Int16��

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._npcID = section.readString( "param1" )  	# ����ָ���NPC��ID
		self._radius = section.readInt( "param2" )		# �����뾶
		self._aiCmd = section.readInt( "param3" )		# AIָ���ʶ��Int16��

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		for e in player.entitiesInRangeExt( self._radius, None, player.position ):
			if e.className == self._npcID:
				e.onAICommand( e.id, e.className, self._aiCmd )					# ֱ��ʹ��onAICommand�Ƿ�ֹe��һ��ghost�������Ҳ����


class QTSSendAICmd_Abandon( QTScript ) :
	"""
	ָ֪ͨ��NPCִ��AIָ������ڷ�������
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._npcID = ""								# ����ָ���NPC��ID
		self._radius = 0								# �����뾶
		self._aiCmd = None								# AIָ���ʶ��Int16��

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._npcID = section.readString( "param1" )  	# ����ָ���NPC��ID
		self._radius = section.readInt( "param2" )		# �����뾶
		self._aiCmd = section.readInt( "param3" )		# AIָ���ʶ��Int16��

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def onAbandoned( self, player, questData = None ):
		"""
		��������
		"""
		for e in player.entitiesInRangeExt( self._radius, None, player.position ):
			if e.className == self._npcID:
				e.onAICommand( e.id, e.className, self._aiCmd )					# ֱ��ʹ��onAICommand�Ƿ�ֹe��һ��ghost�������Ҳ����


class QTSOn3C( QTScript ) :
	"""
	3C��CopyConditionChanged
	֪ͨ���ڸ��������������仯�������ڽ����񣬽�����
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._condition = ""								# ����
		self._value = ""									# �ı�ֵ

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._condition = section.readString( "param1" )
		self._value = section.readString( "param2" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.onConditionChange( { self._condition : self._value } )	# ���spaceEntity��None���Ǿ���������


class QTSOn3C_Abandon( QTScript ) :
	"""
	3C��CopyConditionChanged
	֪ͨ���ڸ��������������仯�������ڷ�������
	ע��֮���԰ѷ���������Ϊ��д������Ϊ����ͬһ��������ԣ�
	������������ͷ���������Ҫ֪ͨ���������ı���������
	�������ͷ������񶼻�ִ����ͬ��������Ϊ�ű�������޷�ʵ
	���������ͷ�������ִ�в�ͬ���ܵ�����
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self._condition = ""								# ����
		self._value = ""									# �ı�ֵ

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._condition = section.readString( "param1" )
		self._value = section.readString( "param2" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def onAbandoned( self, player, questData = None ):
		"""
		��������
		"""
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.onConditionChange( { self._condition : self._value } )	# ���spaceEntity��None���Ǿ���������

class QTSNotifySpaceCMgr( QTScript ):
	# ֪ͨ��ɽ�󷨹�����������ˢ���������
	def __init__( self ):
		QTScript.__init__( self )

	def query( self, player ):
		# ��ѯ�ű��Ƿ���ִ��
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
	�������Ѳ��
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
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self.patrolPathNode = section.readString( "param1" )
		self.patrolList = section.readString( "param2" )
		self.spaceName = section.readString( "param3" )

		position = section.readString( "param4" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( %s ) Bad format '%s' in section param4 " % ( self.__class__.__name__, position ) )
			else:
				self.pos = pos

		self.skillID = section.readInt( "param5" )

	def query( self, player ) :
		"""
		�Ƿ�ɽ�����
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		"""
		# ������������ж�����
		if player.attrIntonateSkill or\
			( player.attrHomingSpell and player.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			player.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )

		# ��¼Ҫ����ĵط�
		player.setTemp( "teleportFly_data", ( self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction ) )
		player.spellTarget( self.skillID, player.id )

class QTSProduceMonsterAndTrap( QTScript ):
	"""
	��60�����鸱����ˢ�����������
	"""
	def __init__( self ):
		QTScript.__init__( self )
		self.monsterIDLists = []

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self.monsterLists = section.readString("param1").split(":")

	def query( self, player ):
		"""
		�Ƿ�ɽ�������
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
	�ٻ�ָ��CallMonster���͵Ĺ���
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._position = ""
		self._direction = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )						# className

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( %s ) Bad format '%s' in section param2 " % ( self.__class__.__name__, position ) )
			else:
				self._position = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( %s ) Bad format '%s' in section param3" % ( self.__class__.__name__, direction ) )
			else:
				self._direction = dir


	def query( self, player ) :
		"""
		�Ƿ�ɽ�����
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""

		pos = Math.Vector3( player.position )
		direction = player.direction

		pos.x = player.position.x  +  random.random() * random.randint( -3, 3 )
		pos.z = player.position.z  +  random.random() * random.randint( -3, 3 )

		if self._position:
			pos = self._position
		if self._direction:
			direction = self._direction

		# �ٻ������ʱ��Ե��������ײ����������������
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y
		# ģ��ѡȡ�ο� ObjectScript/NPCObject.py ��createEntity �Ĵ���ʽ
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
	������������ָ��className��CallMonster���͵Ĺ���
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )						# className
		self._param2 = section.readFloat( "param2" )			#��Χ
		self._param3 = section.readString( "param3" )			# EntityType

	def query( self, player ) :
		"""
		�Ƿ�ɽ�����
		"""
		return True

	def onAbandoned( self, player, questData = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		monsterList = player.entitiesInRangeExt( self._param2, self._param3, player.position )
		for i in monsterList:
			if i.className == self._param1 and i.getOwner() and i.getOwner() == player:
				i.destroy()


class QTSDestroyMonster( QTScript ) :
	"""
	����һ����Χ�ڴ�������ҵ�ĳ����ĳclassname��entity
	"""
	def __init__( self, *args ):
		"""
		@param args: ��ʼ������
		@args  format: ( itemID, amount ), ...
		"""
		self._param1 = ""
		self._param2 = 0.0
		self._param3 = "Monster"		# Ĭ��ΪMonster
		self._param4 = 0.0
		self._aiCmd = None				# AIָ���ʶ��Int16��
		if len( args ) > 0:
			self._param1 = args[0]

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )			# className
		self._param2 = section.readFloat( "param2" )			#��Χ
		self._param3 = section.readString( "param3" )			# EntityType
		self._param4 = section.readFloat( "param4" )			# ���������ӳ�
		self._aiCmd = section.readInt( "param5" )			# AIָ���ʶ��Int16��

	def query( self, player ) :
		"""
		�Ƿ�ɽ�����
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""

		monsterList = player.entitiesInRangeExt( self._param2, self._param3, player.position )
		for i in monsterList:
			if i.className == self._param1 and i.getOwner() and i.getOwner() == player:
				i.onAICommand( i.id, i.className, self._aiCmd )					# ֱ��ʹ��onAICommand�Ƿ�ֹe��һ��ghost�������Ҳ����
				if self._param4 <= 0:
					i.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
				else:
					i.addTimer( self._param4, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

class QTSShowPatrol( QTScript ):
	"""
	�ͻ�����ʾ�ڵ�·����ͷָ��
	"""
	def __init__( self ):
		self._param1 = ""

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )	#�ڵ�·��
		self._param2 = section.readString( "param2" )

	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.client.onShowPatrol( self._param1, self._param2 )

	def onAbandoned( self, player, questData = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass

class QTSPlaySoundFromGender:
	"""
	�����Ա�ѡ�񲥷���Ƶ
	"""
	def __init__( self ):
		self._param1 = ""
		self._param2 = 0
		self._param3 = ""

	def init( self, section ):
		"""
		@param args: ��ʼ������
		@type  args: pyDataSection
		"""
		self._param1 = section.readString( "param1" )	#��Ƶ�ļ�·��(����)
		self._param2 = section.readString( "param2" )	#��Ƶ�ļ�·����Ů�ԣ�
		self._param3 = section.readInt( "param3" )	#��Ƶ���� 2D/3D
		self._param4 = section.readString( "param4" )   #NPC��className
		self._priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_QUEST


	def query( self, player ):
		"""
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
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
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass

class QTSSetAutoNextQuestFlag( QTScript ):
	"""

	"""
	def __init__( self ):
		QTScript.__init__( self )

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.setTemp( Const.QUEST_AUTO_OPEN_NEXT_KEY, tasks.getQuestID() )

class QTSShowHeadPortrait( QTScript ):
	"""
	�������ʾ������ʾ��Ϣ
	"""
	def __init__( self ):
		self.type = 0
		self.headTextureID = ""
		self.text = ""
		self.monsterName = ""
		self.lastTime = 0.0

	def init( self, section ):
		"""
		@param args: ��ʼ������
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
		��ѯ�ű��Ƿ���ִ��

		@return: Bool
		@rtype:  Bool
		"""
		return True

	def do( self, player, tasks = None ):
		"""
		ִ�нű���

		ע�⣺�˴������κ�ִ��ǰ�ļ�顣

		@return: ��
		"""
		player.client.showHeadPortraitAndText( self.type, self.monsterName, self.headTextureID, self.text, self.lastTime )
		if self.monsterName:
			player.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, self.monsterName, self.text, [] )
		else:
			player.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_MESSAGE, 0, player.getName(), self.text, [] )

	def onAbandoned( self, player, questData = None ):
		"""
		�����񱻷���ʱ�Ƿ�Ҫ����ʲô��
		"""
		pass

# ע�������
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
