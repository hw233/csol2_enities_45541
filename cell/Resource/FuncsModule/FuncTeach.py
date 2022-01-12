# -*- coding: gb18030 -*-
#
# $Id: FuncTeach.py,v 1.2 2008-06-21 08:08:56 wangshufeng Exp $

"""
"""
import BigWorld
from Function import Function
import csdefine
import csstatus
import csconst
import cschannel_msgs
from bwdebug import *
import Const
import items
from TitleMgr import TitleMgr
import random
import utils
from ObjectScripts.GameObjectFactory import g_objFactory


titleMgr = TitleMgr.instance()
g_items = items.instance()

class TeachPrentice( Function ):
	"""
	拜师
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.teach_teachPrentice( talkEntity )
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


class TeachDisband( Function ):
	"""
	解除师徒关系
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.endGossip( talkEntity )
		if not player.hasShiTuRelation():
			player.statusMessage( csstatus.TEACH_HAS_NO_RELATION )
			return
		player.client.teach_requestDisband()
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


class TeachSuccess( Function ):
	"""
	出师
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.endGossip( talkEntity )
		if not player.hasShiTuRelation():
			player.statusMessage( csstatus.TEACH_HAS_NO_RELATION )
			return
		player.teach_masterEndTeach( talkEntity )
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


class TeachQueryTeachInfo( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass


	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return

		BigWorld.globalData["TeachMgr"].queryTeachInfo( player.base, player.level )
		player.client.showTeachInfo()


	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

class TeacherRegister( Function ):
	"""
	注册收徒
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.base.teach_registerTeacher()
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

class TeacherDeregister( Function ):
	"""
	注销收徒
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.teach_deregisterTeacher()
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True



class PrenticeRegister( Function ):
	"""
	注册拜师
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.base.teach_registerPrentice()
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

class PrenticeDeregister( Function ):
	"""
	注销拜师
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.teach_deregisterPrentice()
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

class TeachKillMonsterCopyEnter( Function ):
	"""
	"""
	def __init__( self, section ):
		self.mapName 	= section["param1"].asString					# 地图名
		
		self.pos = None													#进入位置
		position = section.readString( "param2" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param2 " % ( self.__class__.__name__, position ) )
		else:
			self.pos = pos
		
		self.direction = None
		direction = section.readString( "param3" )						#进入朝向
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param3 " % ( self.__class__.__name__, direction ) )
		else:
			self.direction = dir

		self.questID	= section["param4"].asInt					# 任务编号
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		if not player.has_quest( self.questID ):
			player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_NO_QUEST, player.getName() )
			return
		if not player.isInTeam():
			player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_NOT_TEAM )
			return
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM_CAPTAIN )
			return
		if not player.iAmMaster():
			player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_NOT_TEAM )
			return
		tammateList = talkEntity.searchTeamMember( player.teamMailbox.id, csconst.TEACH_SPACE_ENTER_TEAMMATE_DISTANCE )
		teammateCount = player.getTeamCount()
		if len( tammateList ) != teammateCount:
			player.statusMessage( csstatus.CANT_ENTER_TEACH_LACK_TEAMMATE )
			return
		if teammateCount < 2:
			player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_NOT_TEAM )
			return
		teachSpaceKillMonsterTime = player.query( "teachSpaceKillMonsterTime" )
		if teachSpaceKillMonsterTime > time.time():
			player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_TODAY )
			return
		for teammate in tammateList:
			if teammate.id == player.id:
				continue
			if not teammate.isReal():	# 如果玩家是ghost，无法检查玩家今天是否做过副本，不允许
				player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_DISTANCE )	# 你的队员距离太远了
				return
			if not teammate.has_quest( self.questID ):
				player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_NO_QUEST, teammate.getName() )
				return
			lasterEnterTime = teammate.query( "teachSpaceKillMonsterTime", 0 )
			if lasterEnterTime > time.time():
				player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_TODAY )
				return
			if not player.isPrentice( teammate.databaseID ):
				player.statusMessage( csstatus.CANT_ENTER_TEACH_SPACE_NOT_PRENTICE )
				return
		player.gotoSpace( self.mapName, self.pos, self.direction )
		members = player.getAllMemberInRange( csconst.TEACH_SPACE_ENTER_TEAMMATE_DISTANCE )
		for teamMate in members:
			teamMate.gotoSpace( self.mapName, self.pos, self.direction )
			
class TeachKillMonsterCopyBossTalk( Function ):
	"""
	师徒副本boss对话
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		self._param1 = section.readInt( "param1" )			#任务ID
		self._param2 = section.readInt( "param2" )			#任务目标索引
		self.bossMonstList = section["param3"].asString.split( ";" )
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		# 必须拥有某项任务才能对话
		quest = player.getQuest( self._param1 )
		
		if quest is None:
			return False
		
		if quest.query( player ) != csdefine.QUEST_STATE_NOT_FINISH:
			return False
		
		if player.getQuestTasks( self._param1 ).getTasks()[self._param2].isCompleted( player ):
			return False
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			ERROR_MSG( "talkEntity cannot be None." )
			return
		entityName = random.sample( self.bossMonstList, 1 )[0]
		objectScript = g_objFactory.getObject( entityName )
		if objectScript is None:
			ERROR_MSG( "no such classname: %s entity" % entityName )	# 这个应该永远都不可能到达
			return
		objectScript.createEntity( talkEntity.spaceID, talkEntity.position, talkEntity.direction, {"spawnMB":talkEntity.spawnMB,"level":player.getQuest( self._param1 ).getLevel(player)} )
		player.questTalk( talkEntity.className )
		talkEntity.destroy()
		
class TeachEverydayReward( Function ):
	"""
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity ):
		"""
		检查一个功能是否可以使用
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if not player.hasShiTuRelation():
			return False
		return True
		
	def do( self, player, talkEntity ):
		"""
		"""
		player.endGossip( talkEntity )
		if not player.hasShiTuRelation():
			return
			
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_SHI_TU ) :
			player.statusMessage( csstatus.ALREADAY_TAKE_TEACH_REWARD_TODAY )
			return
		player.addActivityCount( csdefine.ACTIVITY_SHI_TU )
		if player.iAmMaster():
			player.spellTarget( Const.TEACH_MASTER_EVERYDAY_REWARD_SKILLID, player.id )
		else:
			player.spellTarget( Const.TEACH_PRENTICE_EVERYDAY_REWARD_SKILLID, player.id )
			
		player.teachEveryDayReward()
				
class TeachCreditChangeTitle( Function ):
	"""
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		self.requireTitleID = section.readInt( "param1" )		# 请求兑换的称号id
		self.cantHadTitleList = [int( titleID ) for titleID in section.readString( "param2" ).split(";") if titleID != ""]
		
	def valid( self, player, talkEntity ):
		"""
		检查一个功能是否可以使用
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True
		
	def do( self, player, talkEntity ):
		"""
		"""
		player.endGossip( talkEntity )
		for titleID in self.cantHadTitleList:
			if player.hasTitle( titleID ):
				player.statusMessage( csstatus.EXCHANGE_TEACH_TITLE_HAD_HIGHT_LEVEL )
				return
		if player.hasTitle( self.requireTitleID ):
			player.statusMessage( csstatus.EXCHANGE_TEACH_TITLE_ALREADY_HAD )
			return
		requireTitleData = titleMgr.getTeachTitleRequire( self.requireTitleID )
		teachCreditRequire = requireTitleData["teachCreditRequire"]
		if player.teachCredit < teachCreditRequire:
			player.statusMessage( csstatus.CANT_GET_TITLE_NEED_TEACH_CREDIT )
			return
		preTitle = requireTitleData["preTitleID"]
		if preTitle != 0 and not player.hasTitle( preTitle ):
			player.statusMessage( csstatus.CANT_GET_TITLE_NEED_PRE_TITLE )
			return
		# 目前只有师徒称号是可以升级的，在此处remove旧称号，add新称号。
		# 考虑以后修改称号系统，每个称号配置数据增加前置称号，修改addTitle，支持获得新称号有可能会替代某些旧称号的规则。
		player.removeTitle( preTitle )
		player.addTeachCredit( -teachCreditRequire )
		player.addTitle( self.requireTitleID )
		if player.query( "teach_register_teachInfo", False ):
			BigWorld.globalData["TeachMgr"].onPlayerTeachTitleChange( self.databaseID, self.requireTitleID )
			
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/06/21 08:00:50  wangshufeng
# 加入师徒系统npc对话功能选项
#
#