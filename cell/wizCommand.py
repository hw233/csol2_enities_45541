# -*- coding: gb18030 -*-
#
# $Id: wizCommand.py,v 1.44 2008-09-01 03:34:29 zhangyuxing Exp $

"""
调试指令,调试指令应该最大限度的避免使用eval()来解释参数,以增加安全性（误操作）；
"""

import Love3
import ChatObjParser
import Language
from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from MsgLogger import g_logger
from interface.CombatUnit import CombatUnit
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.Rewards.RewardManager import g_rewardMgr
from Love3 import g_skills
from items.EquipEffectLoader import EquipEffectLoader
from TitleMgr import TitleMgr
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import EquipGodWeaponExp
from ActivityRecCleanWiz import *
from Function import Functor
import config.server.WebServicePresentIDs
from config.item import A_PropertyPrefix
from test.content_test import AI_reload
from test.content_test import Skill_reload
from test.content_test import Item_reload
from Monster import Monster


import BigWorld
import ItemTypeEnum
import sys
import csconst
import items
import random
import time
import csdefine
import binascii
import csstatus
import SpaceDoor

import Const

g_titleLoader = TitleMgr.instance()
g_equipIntensify = EquipIntensifyExp.instance()
g_equipEffect = EquipEffectLoader.instance()
g_items = items.instance()

from ActivityRecordMgr import g_activityRecordMgr
from VehicleHelper import getCurrAttrVehicleID

from LevelEXP import TongLevelEXP as TLevelEXP

TREASURE_MAP_ID = 60101005		#藏宝图物品ID


def wizCommand_set_grade( srcEntity, dstEntity, args ):
	"""
	设置目标entity的权限,只能设置比自己权限低的人,且能设置的权限也只能比自己低；
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：grade
	"""
	try:
		grade = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_GRADE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_GRADE_MUST_INT, "" )
		return

	if srcEntity.id == dstEntity.id:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_FOR_YOURSELF, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if srcEntity.grade <= dstEntity.grade:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_BIGGER_TARGET, "" )
		return

	if srcEntity.grade <= grade:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_BIGGER_GRADE, "" )
		return

	dstEntity.grade = grade
	INFO_MSG( "%s(%i): set %s(%i) grade from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.grade, grade) )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_GRADE_SUCCESS, str(( dstEntity.getName(), dstEntity.id, grade )) )
	dstEntity.client.onStatusMessage( csstatus.WIZCOMMAND_YOUR_NEW_GRADE, str(( grade, )) )
	dstEntity.base.update_grade( dstEntity.grade )		#通知base grade的值被修改 以便base使用正确的值去写日志
	try:
		g_logger.gmCommonLog( "set_grade", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )
	return

def wizCommand_query_grade( srcEntity, dstEntity, args ):
	"""
	查询目标权限值
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：""
	"""
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_YOUR_NOW_GRADE, str(( dstEntity.grade, )) )

def wizCommand_set_attr( srcEntity, dstEntity, args ):
	"""
	设置某人的属性值；
	注意：请小心使用此功能,它有可能产生异想不到的错误,并有可能导致服务器崩溃或数据库数据损坏。
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：key value
	"""
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ATTR_FORMAT, "" )
		return

	key = cmds[0]
	if key in ["accountEntity", "parentDBID", "persistentMapping", "tempMapping", "grade"]:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_ATTR, "" )
		return

	if not hasattr( dstEntity, key ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_THIS_ATTR, "" )
		return

	value = "".join( cmds[1:] )

	INFO_MSG( "%s(%i): set %s(%i)'s %s to %s" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, key, value) )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_NEW_ATTR, str(( dstEntity.getName(), dstEntity.id, key, value )) )
	value = eval( value )
	setattr( dstEntity, key, value )

	# 判断是否是特殊属性， 这些属性需要调用特定的接口进行更新
	if key in special_attr_dict:
		getattr(dstEntity, special_attr_dict[key])()

	try:
		g_logger.gmCommonLog( "set_attr", args, srcEntity.getNameAndID(), dstEntity.getName(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )
	return

def wizCommand_set_attr_full( srcEntity, dstEntity, args ):
	"""
	当有目标的情况下，设置自身和目标的HP和MP为最大值9,999,999；
	在没有目标的情况下，设置自身的HP和MP为最大值9,999,999；
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：key value
	"""
	value = 99999999

	if dstEntity.__class__.__name__ in [ "Role", "Monster"] or isinstance( dstEntity, Monster ):
		INFO_MSG( "%s(%i): set %s(%i)'s HP/MP/HP_Max/MP_Max to %s" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
		if dstEntity != srcEntity:								# 判断目标是否为自身，若为自身暂不处理
			if dstEntity.__class__.__name__ == "Role" :
				dstEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ATTR_FULL, str(( dstEntity.getName(), dstEntity.id, value )) )
			else:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ATTR_FULL, str(( dstEntity.getName(), dstEntity.id, value )) )
			setattr( dstEntity, "HP", value )
			setattr( dstEntity, "HP_Max", value )
			setattr( dstEntity, "MP", value )
			setattr( dstEntity, "MP_Max", value )
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE_OR_MONSTER, "" )

	# 不管目标是否为自身，对自身的HP和MP进行处理
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ATTR_FULL, str(( srcEntity.getName(), srcEntity.id, value )) )
	setattr( srcEntity, "HP", value )
	setattr( srcEntity, "HP_Max", value )
	setattr( srcEntity, "MP", value )
	setattr( srcEntity, "MP_Max", value )

	try:
		g_logger.gmCommonLog( "set_attr_full", args, srcEntity.getNameAndID(), dstEntity.getName(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )
	return


def wizCommand_query_attr( srcEntity, dstEntity, args ):
	"""
	查询某人的属性值
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：key
	"""
	if len( args ) == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_ATTR_FORMAT, "" )
		return

	key = args
	if not hasattr( dstEntity, key ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_THIS_ATTR_QUERY, "" )
		return

	v = str( getattr( dstEntity, key ) )
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str(( v, )) )

def wizCommand_query_persistent( srcEntity, dstEntity, args ):
	"""
	查询某人的persistentMapping属性中的值；
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：key
	"""
	if len( args ) == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_PERSISTENT_FORMAT, "" )
		return

	v = str( dstEntity.queryStr( args ) )
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str(( v, )) )

def wizCommand_set( srcEntity, dstEntity, args ):
	"""
	设置某人的persistentMapping属性中的值；
	注意：请小心使用此功能,它有可能产生异想不到的错误,并有可能导致服务器崩溃或数据库数据损坏。
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：key value
	"""
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_KEY_FORMAT, "" )
		return

	key = cmds[0]
	value = "".join( cmds[1:] )

	INFO_MSG( "%s(%i): set %s(%i)'s persistentMapping to %s:%s" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, key, value) )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_NEW_KEY, str(( dstEntity.getName(), dstEntity.id, key, value )) )
	value = eval( value )
	dstEntity.set( key, value )
	if dstEntity.__class__.__name__ == "Role":
		try:
			g_logger.gmCommonLog( "set", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
	else:
		try:
			g_logger.gmCommonLog( "set", args, srcEntity.getNameAndID(), dstEntity.getName(), srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_query_temp( srcEntity, dstEntity, args ):
	"""
	查询某人的tempMapping属性中的值；
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：key
	"""
	if len( args ) == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_TEMP_FORMAT, "" )
		return
	v = str( dstEntity.queryTempStr( args ) )
	if not v:	v = "None"
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str((v, )) )

def wizCommand_set_temp( srcEntity, dstEntity, args ):
	"""
	设置某人的tempMapping属性中的值；
	注意：请小心使用此功能,它有可能产生异想不到的错误,并有可能导致服务器崩溃或数据库数据损坏。
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：key value
	"""
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_TEMP_FORMAT, "" )
		return

	key = cmds[0]
	value = "".join( cmds[1:] )

	INFO_MSG( "%s(%i): set %s(%i)'s tempMapping to %s:%s" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, key, value) )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_NEW_TEMP, str(( dstEntity.getName(), dstEntity.id, key, value )) )
	value = eval( value )
	dstEntity.setTemp( key, value )
	try:
		g_logger.gmCommonLog( "set_temp", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_goto( srcEntity, dstEntity, args ):
	"""
	进入一个场景
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：spaceKey px py pz dx dy dz
	"""
	cmds = args.split()
	cmdLen = len( cmds )
	if cmdLen < 7:
		direction = (0.0,0.0,0.0)
	else:
		direction = ( float(cmds[4]), float(cmds[5]), float(cmds[6]) )

	if cmdLen < 4:
		position = (0.0,0.0,0.0)
	else:
		position = ( float(cmds[1]), float(cmds[2]), float(cmds[3]) )

	if cmdLen == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTO_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTO_FORMAT_2, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTO_FORMAT_3, "" )
		return

	spaceLabel = BigWorld.getSpaceDataFirstForKey( srcEntity.spaceID, csconst.SPACE_SPACEDATA_KEY )
	if spaceLabel == cmds[0]:
		srcEntity.position = position
		return
	INFO_MSG( "%s(%i): goto %s" % (srcEntity.getName(), srcEntity.id, cmds[0]) )
	# 增加进监狱支持
	srcEntity.setTemp( "gotoPrison", True )
	srcEntity.gotoSpace( cmds[0], position, direction )
	try:
		g_logger.gmCommonLog( "goto", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_change_magic_avatar( srcEntity, dstEntity, args ):
	avatarTypes = ["chiyou", "huangdi", "houyi", "nuwo"]
	# 判断当前是否是变身状态
	cmds = args.split()
	indexType = int( cmds[0] )
	if indexType > 4 or indexType < 0:
		indexType = 0

	newAvatarType = avatarTypes[ indexType ]
	srcEntity.set( "challengeAvatar", newAvatarType )
	srcEntity.requestInitSpaceSkill( srcEntity.id )
	srcEntity.startMagicChange( newAvatarType )

def wizCommand_gotoline( srcEntity, dstEntity, args ):
	"""
	进入一个场景
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：spaceKey 线号码 px py pz
	"""
	cmds = args.split()
	cmdLen = len( cmds )

	lineNumber = int(cmds[1])
	position = ( float(cmds[2]), float(cmds[3]), float(cmds[4]) )

	if cmdLen == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTOLINE_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTOLINE_FORMAT_2, "" )
		return

	# 增加进监狱支持
	srcEntity.setTemp( "gotoPrison", True )
	srcEntity.gotoSpaceLineNumber( cmds[0], lineNumber, position, ( 0, 0, 0 ) )

	try:
		g_logger.gmCommonLog( "goto", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_clone( srcEntity, dstEntity, args ):
	"""
	在entity当前位置创建一个npc entity
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：npcKey 等级：level
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CLONE_FORMAT, "" )
		return

	npcKey = cmds[0]
	try:
		monster_level = int( cmds[1] )
	except:
		monster_level = 0
	try:
		count = int( cmds[2] )
	except:
		count = 1


	if monster_level > 150:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MOSTER_LEVEL_PARANORMAL, "" )
		return

	entity = g_objFactory.getObject( npcKey )
	if entity is None :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TARGET_NOT_EXIST, str(( npcKey, )) )
		return

	for i in xrange( 0, count ):
		if monster_level > 0:
			cloneEntity = entity.createEntity( srcEntity.spaceID, srcEntity.position, srcEntity.direction, { "spawnPos" : tuple( srcEntity.position ), "randomWalkRange" : 3, "level" : monster_level } )
		else:
			cloneEntity = entity.createEntity( srcEntity.spaceID, srcEntity.position, srcEntity.direction, { "spawnPos" : tuple( srcEntity.position ), "randomWalkRange" : 3 } )

	#except Exception, errstr:
		# notify any error
	#   return

	cloneEntity.setTemp( "cloned", 1 )

	INFO_MSG( "%s(%i): clone npc %s in" % (srcEntity.getName(), srcEntity.id, npcKey), srcEntity.spaceType, srcEntity.position, srcEntity.direction )
	try:
		g_logger.gmCommonLog( "clone", args, srcEntity.getNameAndID(), None , srcEntity.grade)
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_drop_item( srcEntity, dstEntity, args ):
	"""
	在当前位置扔一个物品
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：itemKey amount
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_DROP_ITEM_FORMAT, "" )
		return

	try:
		itemKey = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( cmds[0], )) )
		return
	amount = 1

	if len(cmds) > 1:
		try:
			amount = int( cmds[1] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
			return

	item = g_items.createEntity( itemKey, srcEntity.spaceID, srcEntity.position, srcEntity.direction )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return

	if item.itemProp.getStackable() > 1:
		item.itemProp.setAmount( amount )

	INFO_MSG( "%s(%i): clone item %s %i in" % (srcEntity.getName(), srcEntity.id, itemKey, amount), srcEntity.spaceType, srcEntity.position, srcEntity.direction )
	try:
		g_logger.gmCommonLog( "drop_item", args, srcEntity.getNameAndID(), None , srcEntity.grade)
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_add_item( srcEntity, dstEntity, args ):
	"""
	给物品栏中增加一个物品
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：itemKey amount
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_ITEM_FORMAT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if dstEntity.getNormalKitbagFreeOrderCount() < 1: # 背包空间不足
		srcEntity.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
		return

	itemKey = cmds[0]
	try:
		itemKey = int( itemKey )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return
	amount = 1

	if len(cmds) > 1:
		try:
			amount = int( cmds[1] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
			return

	item = g_items.createDynamicItem( itemKey, amount )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return

	if amount > item.getStackable():
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_IS_TOO_MUSH, "" )
		return
	#进行属性随机操作
	if item.isEquip():
		item.fixedCreateRandomEffect( item.getQuality(),dstEntity ,False )

	if not dstEntity.addItemAndNotify_( item, csdefine.ADD_ITEM_GMCOMMAND ): # 增加物品，失败则返回
		return

	if srcEntity.id != dstEntity.id:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_ITEM_SUCCESS, str(( dstEntity.getName(), item.fullName(), amount )) )
		dstEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_ITEM_SUCCESS, str(( dstEntity.getName(), item.fullName(), amount )) )
	INFO_MSG( "%s(%i): add item %s amount %i to %s(%i)" % (srcEntity.getName(), srcEntity.id, itemKey, amount, dstEntity.getName(), dstEntity.id ) )
	try:
		g_logger.gmCommonLog( "add_item", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_luckyBox( srcEntity, dstEntity, args ):
	"""
	给物品栏中增加一个指定级别的宝盒
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_LUCKYBOX_FORMAT, "" )
		return

	itemKey = cmds[0]
	try:
		itemKey = int( itemKey )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return
	level = csconst.LUCKY_BOX_MOSTER_LEVEL

	if len(cmds) > 1:
		try:
			level = int( cmds[1] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_LEVEL_MUST_BE_INT, "" )
			return
	if level < csconst.LUCKY_BOX_MOSTER_LEVEL:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_LEVEL_TOO_LESS, str(( csconst.LUCKY_BOX_MOSTER_LEVEL, )) )
		return

	item = g_items.createDynamicItem( itemKey, 1 )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return
	item.set( "level", level )

	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND )
	INFO_MSG( "%s(%i): add item %s level %i" % (srcEntity.getName(), srcEntity.id, itemKey, level) )
	try:
		g_logger.gmCommonLog( "add_luckyBox", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_equip( srcEntity, dstEntity, args ):
	"""
	给物品栏中增加一个可以指定品质,前缀,孔数的装备
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：itemKey quality prefix slot intensifyLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_EQUIP_FORMAT, "" )
		return
	try:
		itemKey = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( cmds[0], )) )
		return
	amount = 1
	quality = 1  		# 品质（1-5）
	slot = 0	 		# 开孔（0-3）
	intensifyLevel = 0  # 强化等级（0-9）

	if len( cmds ) == 2:
		try:
			quality = int( cmds[1] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
			return
	elif len( cmds ) == 3:
		try:
			quality = int( cmds[1] )
			slot = int( cmds[2] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SLOT_MUST_BE_INT, "" )
			return
	elif len( cmds ) > 3:
		try:
			quality = int( cmds[1] )
			slot = int( cmds[2] )
			intensifyLevel = int( cmds[3] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SLOT_MUST_BE_INT, "" )
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_MUST_BE_INT, "" )
			return

	if quality > ItemTypeEnum.CQT_GREEN or quality < ItemTypeEnum.CQT_WHITE:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_RANGE, "" )
		return

	item = g_items.createDynamicItem( itemKey, amount )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return
	if not item.isEquip():
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_A_EQUIP, str(( itemKey, )) )
		return

	maxSlot = item.getMaxSlot()
	if slot > maxSlot or slot < 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SLOT_RANGE, str(( maxSlot, )) )
		return
	if intensifyLevel < 0 or intensifyLevel > 9:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_RANGE, "" )
		return

	item.setQuality( quality )
	if slot != 0: item.setLimitSlot( slot )
	# 修正GM指令装备强化和相应等级范围的龙珠及其效果对应 那个龙珠的等级范围真乱七八糟 by姜毅
	if intensifyLevel != 0:
		dragonGemID = 0
		iLevel = item.getLevel()
		if iLevel > 30 and iLevel < 91:
			if iLevel < 51: dragonGemID = 80101032
			else: dragonGemID = 80101037
		else:
			case = iLevel / 30
			if case == 0 or iLevel == 30: dragonGemID = 80101031
			elif case == 3 or iLevel == 120: dragonGemID = 80101038
			else: dragonGemID = 80101039
		for i in xrange( intensifyLevel ):
			g_equipIntensify.setIntensifyValue( item, dragonGemID, i + 1 )
		item.setIntensifyLevel( intensifyLevel )
	item.fixedCreateRandomEffect( item.getQuality(),dstEntity ,False )  # 随机属性
	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND )
	INFO_MSG( "%s(%i): add item %s amount %i" % (srcEntity.getName(), srcEntity.id, itemKey, amount) )
	try:
		g_logger.gmCommonLog( "add_equip", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_equip_ten( srcEntity, dstEntity, args ):
	"""
	给物品栏中增加一个可以指定品质,前缀,孔数的需要等级取整十的装备 modified by 姜毅
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：itemKey quality prefix slot intensifyLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_EQUIP_T_FORMAT, "" )
		return
	try:
		itemKey = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( cmds[0], )) )
		return
	amount = 1
	quality = 1
	slot = 0
	intensifyLevel = 0

	if len( cmds ) == 2:
		try:
			quality = int( cmds[1] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
			return
	elif len( cmds ) == 3:
		try:
			quality = int( cmds[1] )
			slot = int( cmds[2] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SLOT_MUST_BE_INT, "" )
			return
	elif len( cmds ) > 3:
		try:
			quality = int( cmds[1] )
			slot = int( cmds[2] )
			intensifyLevel = int( cmds[3] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SLOT_MUST_BE_INT, "" )
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_MUST_BE_INT, "" )
			return

	if quality > ItemTypeEnum.CQT_GREEN or quality < ItemTypeEnum.CQT_WHITE:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_RANGE, "" )
		return

	item = g_items.createDynamicItem( itemKey, amount )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return
	if not item.isEquip():
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_A_EQUIP, str(( itemKey, )) )
		return
	maxSlot = item.getMaxSlot()
	if slot > maxSlot or slot < 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SLOT_RANGE, str(( maxSlot, )) )
		return
	if intensifyLevel < 0 or intensifyLevel > 9:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_RANGE, "" )
		return

	item.setQuality( quality )
	if slot != 0: item.setLimitSlot( slot )
	# 修正GM指令装备强化和相应等级范围的龙珠及其效果对应 那个龙珠的等级范围真乱七八糟 by姜毅
	if intensifyLevel != 0:
		dragonGemID = 0
		iLevel = item.getLevel()
		if iLevel > 30 and iLevel < 91:
			if iLevel < 51: dragonGemID = 80101032
			else: dragonGemID = 80101037
		else:
			case = iLevel / 30
			if case == 0 or iLevel == 30: dragonGemID = 80101031
			elif case == 3 or iLevel == 120: dragonGemID = 80101038
			else: dragonGemID = 80101039
		for i in xrange( intensifyLevel ):
			g_equipIntensify.setIntensifyValue( item, dragonGemID, i + 1 )
		item.setIntensifyLevel( intensifyLevel )

	newReqLevel = item.getReqLevel()/10*10
	if newReqLevel <= 0: newReqLevel = 1
	item.setReqLevel( newReqLevel )
	item.fixedCreateRandomEffect( item.getQuality(),dstEntity ,False )  # 随机属性
	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND )
	INFO_MSG( "%s(%i): add item %s amount %i" % (srcEntity.getName(), srcEntity.id, itemKey, amount) )
	try:
		g_logger.gmCommonLog( "add_equip_t", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_skill( srcEntity, dstEntity, args ):
	"""
	给某人或宠物增加一个技能
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：skillID
	"""
	try:
		skillID = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_SKILL_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SKILLID_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role" and dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_R_P, "" )
		return

	INFO_MSG( "%s(%i): add skill %i to %s(%i)" % (srcEntity.getName(), srcEntity.id, skillID, dstEntity.getName(), dstEntity.id) )
	dstEntity.addSkill( skillID )
	try:
		g_logger.gmCommonLog( "add_skill", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_remove_skill( srcEntity, dstEntity, args ):
	"""
	删除某人或宠物的一个技能
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：skillID
	"""
	try:
		skillID = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_REMOVE_SKILL_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SKILLID_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role" and dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_R_P, "" )
		return

	INFO_MSG( "%s(%i): remove skill %i from %s(%i)" % (srcEntity.getName(), srcEntity.id, skillID, dstEntity.getName(), dstEntity.id) )
	dstEntity.removeSkill( skillID )
	try:
		g_logger.gmCommonLog( "remove_skill", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_level( srcEntity, dstEntity, args ):
	"""
	给某人设置等级
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LEVEL_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_LEVEL_MUST_BE_INT, "" )
		return

	if value > 150 or value < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INVALID_PARAM, "" )
		return

	if dstEntity.__class__.__name__ in [ "Role", "Pet", "Monster", "SlaveMonster", "BossCityWar", "TreasureMonster", "NPCYayu" ]:
		INFO_MSG( "%s(%i): set %s(%i) level from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.level, value) )
		if dstEntity.__class__.__name__ == "Role":
			try:
				g_logger.gmCommonLog( "set_level", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade, "oldlevle = %s " % dstEntity.level )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			try:
				g_logger.gmCommonLog( "set_level", args, srcEntity.getNameAndID(), dstEntity.getName(), srcEntity.grade, "oldlevle = %s " % dstEntity.level )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		dstEntity.setLevel( value )
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ENTITY_CANNOT_SET_LEVEL, "" )
		return

def wizCommand_set_camp( srcEntity, dstEntity, args ):
	"""
	设置某人的所属阵营
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_CAMP, "" )
		return

	if value not in  [ csdefine.ENTITY_CAMP_NONE, csdefine.ENTITY_CAMP_TAOISM, csdefine.ENTITY_CAMP_DEMON ]:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_CAMP, "" )
		return

	dstEntity.raceclass = dstEntity.raceclass & ( csdefine.RCMASK_GENDER| csdefine.RCMASK_CLASS | csdefine.RCMASK_RACE |csdefine.RCMASK_FACTION )
	dstEntity.raceclass = dstEntity.raceclass | value << 20
	try:
		g_logger.gmCommonLog( "set_camp", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_adult( srcEntity, dstEntity, args ):
	"""
	设置某人为成年人或未成年人
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ADULT_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ADULT_FORMAT_2, "" )
		return

	if not dstEntity.__class__.__name__ == "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ENTITY_CANNOT_SET, "" )
		return
	else:
		cIndu_isAdult = dstEntity.cWallow_isAdult
		dstEntity.base.wallow_setAgeState( value )
		INFO_MSG( "%s(%i): set %s(%i) adult from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, cIndu_isAdult, value) )
		if value:
			dstEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADULT_NOT_LIMIT, "" )
		else:
			dstEntity.client.onStatusMessage( csstatus.WIZCOMMAND_NOT_ADULT, "" )
			if cIndu_isAdult:
				dstEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AVOID_WALLOW_CLOSE, "" )
			else :
				dstEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AVOID_WALLOW_OPEN, "" )
	try:
		g_logger.gmCommonLog( "set_adult", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.excepLog( "error")

def wizCommand_set_anti( srcEntity, dstEntity, args ):
	"""
	给某人设置等级
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ANTI_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ANTI_FORMAT_2, "" )
		return

	BigWorld.globalData["AntiIndulgenceOpen"] = value
	INFO_MSG( "%s(%i): 将当前游戏的防沉迷系统开关设置为 %i" % ( srcEntity.getName(), srcEntity.id, value) )
	if value:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AVOID_WALLOW_IS_OPENED, "" )
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AVOID_WALLOW_IS_CLOSED, "" )
	try:
		g_logger.gmCommonLog( "set_anti", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_money( srcEntity, dstEntity, args ):
	"""
	给某人设置金钱
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_MONEY_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) money from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.money, value) )
	dstEntity.gainMoney( value-dstEntity.money, csdefine.CHANGE_MONEY_WIZCOMMAND_SET_MONEY  )
	try:
		g_logger.gmCommonLog( "set_money", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_exp( srcEntity, dstEntity, args ):
	"""
	给某人设置经验
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_EXP_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and not dstEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_R_P, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) exp from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.EXP, value) )
	if dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		dstEntity.addExp( value-dstEntity.EXP, csdefine.CHANGE_EXP_COMMAND )
	if dstEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) :
		dstEntity.addEXP( value-dstEntity.EXP )
	try:
		g_logger.gmCommonLog( "set_exp", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_potential( srcEntity, dstEntity, args ):
	"""
	给某人设置潜能
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_POTENTIAL_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) potential from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.potential, value) )
	dstEntity.potential = value
	try:
		g_logger.gmCommonLog( "set_potential", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_speed( srcEntity, dstEntity, args ):
	"""
	给某人设置移动速度
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = float( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_SPEED_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_FLOAT, "" )
		return

	if not isinstance( dstEntity, CombatUnit ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_WAR_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) move speed from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, float( dstEntity.move_speed_value ) / csconst.FLOAT_ZIP_PERCENT, value) )
	dstEntity.move_speed_value = int( value * csconst.FLOAT_ZIP_PERCENT )
	dstEntity.calcMoveSpeed()
	if dstEntity.__class__.__name__ == "Role":
		try:
			g_logger.gmCommonLog( "set_speed", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade ) #玩家
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
	else:
		try:
			g_logger.gmCommonLog( "set_speed", args, srcEntity.getNameAndID(), None, srcEntity.grade ) #非玩家
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_model( srcEntity, dstEntity, args ):
	"""
	给某人设置模型
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_MODEL_FORMAT, "" )
		return

	modelNum = cmds[0]
	if dstEntity.__class__.__name__ == "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_ROLE, "" )
		return
	dstEntity.modelNumber = modelNum

def wizCommand_set_lefthand( srcEntity, dstEntity, args ):
	"""
	给某人设置左手模型
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()

	entityType = dstEntity.getEntityType()
	if entityType == csdefine.ENTITY_TYPE_MONSTER:
		if len( cmds ) != 1 :
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LEFTHAND_FORMAT_1, "" )
			return
		try:
			modelNum = int( cmds[0] )
		except:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MODELNUM_MUST_BE_INT, "" )
			return
		dstEntity.lefthandNumber = modelNum
	elif entityType == csdefine.ENTITY_TYPE_ROLE:
		if len( cmds ) < 1 or len( cmds ) > 3:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LEFTHAND_FORMAT_2, "" )
			return

		modelNum = 0
		iLevel = 0
		stAmount = 0

		if len( cmds ) >= 1:
			try:
				modelNum = int( cmds[0] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MODELNUM_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 2:
			try:
				iLevel = int( cmds[1] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ILEVEL_MUST_BE_INT, "" )
				return

		if len( cmds ) == 3:
			try:
				stAmount = int( cmds[2] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_STAMOUNT_MUST_BE_INT, "" )
				return

		LHFDict  = {	"modelNum"		: modelNum,
						"iLevel"		: iLevel,
						"stAmount"		: stAmount,
						}

		dstEntity.lefthandFDict= LHFDict
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

def wizCommand_set_righthand( srcEntity, dstEntity, args ):
	"""
	给某人设置右手模型
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()

	entityType = dstEntity.getEntityType()
	if entityType == csdefine.ENTITY_TYPE_MONSTER:
		if len( cmds ) != 1 :
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_RIGHTHAND_FORMAT_1, "" )
			return
		try:
			modelNum = int( cmds[0] )
		except:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MODELNUM_MUST_BE_INT, "" )
			return
		dstEntity.righthandNumber = modelNum

	elif entityType == csdefine.ENTITY_TYPE_ROLE:
		if len( cmds ) < 1 or len( cmds ) > 4:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_RIGHTHAND_FORMAT_2, "" )
			return

		modelNum = 0
		iLevel = 0
		stAmount = 0

		if len( cmds ) >= 1:
			try:
				modelNum = int( cmds[0] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MODELNUM_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 2:
			try:
				iLevel = int( cmds[1] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ILEVEL_MUST_BE_INT, "" )
				return

		if len( cmds ) == 3:
			try:
				stAmount = int( cmds[2] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_STAMOUNT_MUST_BE_INT, "" )
				return

		RHFDict  = {	"modelNum"		: modelNum,
						"iLevel"		: iLevel,
						"stAmount"		: stAmount,
						}

		dstEntity.righthandFDict = RHFDict
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

def wizCommand_set_body( srcEntity, dstEntity, args ):
	"""
	给某人设置身体模型
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()

	entityType = dstEntity.getEntityType()
	if entityType == csdefine.ENTITY_TYPE_ROLE:
		if len( cmds ) < 1 or len( cmds ) > 3:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_BODY_FORMAT, "" )
			return

		itemID = 0
		quality = 1
		intensifyLevel = 0

		if len( cmds ) >= 1:
			try:
				itemID = int( cmds[0] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEMID_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 2:
			try:
				quality = int( cmds[1] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 3:
			try:
				intensifyLevel = int( cmds[2] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_MUST_BE_INT, "" )
				return

		bodyFDict  = {  "itemID"			: itemID,
						"quality"		   : quality,
						"intensifyLevel"	: intensifyLevel,
						}

		dstEntity.bodyFDict= bodyFDict
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

def wizCommand_set_vola( srcEntity, dstEntity, args ):
	"""
	给某人设置手套模型
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()

	entityType = dstEntity.getEntityType()
	if entityType == csdefine.ENTITY_TYPE_ROLE:
		if len( cmds ) < 1 or len( cmds ) > 3:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VOLA_FORMAT, "" )
			return

		itemID = 0
		quality = 1
		intensifyLevel = 0

		if len( cmds ) >= 1:
			try:
				itemID = int( cmds[0] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEMID_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 2:
			try:
				quality = int( cmds[1] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 3:
			try:
				intensifyLevel = int( cmds[2] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_MUST_BE_INT, "" )
				return

		volaFDict  = {  "itemID"			: itemID,
						"quality"		   : quality,
						"intensifyLevel"	: intensifyLevel,
						}

		dstEntity.volaFDict= volaFDict
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

def wizCommand_set_breech( srcEntity, dstEntity, args ):
	"""
	给某人设置裤子模型
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()

	entityType = dstEntity.getEntityType()
	if entityType == csdefine.ENTITY_TYPE_ROLE:
		if len( cmds ) < 1 or len( cmds ) > 3:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_BREECH_FORMAT, "" )
			return

		itemID = 0
		quality = 1
		intensifyLevel = 0

		if len( cmds ) >= 1:
			try:
				itemID = int( cmds[0] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEMID_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 2:
			try:
				quality = int( cmds[1] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 3:
			try:
				intensifyLevel = int( cmds[2] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_MUST_BE_INT, "" )
				return

		breechFDict  = {	"itemID"			: itemID,
							"quality"		   : quality,
							"intensifyLevel"	: intensifyLevel,
						}

		dstEntity.breechFDict= breechFDict
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return


def wizCommand_set_feet( srcEntity, dstEntity, args ):
	"""
	给某人设置鞋子模型
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()

	entityType = dstEntity.getEntityType()
	if entityType == csdefine.ENTITY_TYPE_ROLE:
		if len( cmds ) < 1 or len( cmds ) > 3:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FEET_FORMAT, "" )
			return

		itemID = 0
		quality = 1
		intensifyLevel = 0

		if len( cmds ) >= 1:
			try:
				itemID = int( cmds[0] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEMID_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 2:
			try:
				quality = int( cmds[1] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUALITY_MUST_BE_INT, "" )
				return

		if len( cmds ) >= 3:
			try:
				intensifyLevel = int( cmds[2] )
			except ValueError, errStr:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_MUST_BE_INT, "" )
				return

		feetFDict  = {  "itemID"			: itemID,
						"quality"		   : quality,
						"intensifyLevel"	: intensifyLevel,
						}

		dstEntity.feetFDict= feetFDict
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

def wizCommand_set_model_visible( srcEntity, dstEntity, args ):
	"""
	设置目标entity的模型透明度

	MODEL_VISIBLE_TYPE_FALSE		= 0		# 模型不显示
	MODEL_VISIBLE_TYPE_TRUE			= 1		# 模型显示
	MODEL_VISIBLE_TYPE_FBUTBILL	 	= 2		# 模型不显示但显示附加物
	MODEL_VISIBLE_TYPE_SNEAK	 	= 3		# 模型半透明显示
	"""
	if dstEntity.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
		params = args.split()
		if len( params ) !=  1:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_MODEL_VISIBLE_FORMAT, "" )
			return
		try:
			visibleType = int( params[0] )
		except ValueError:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INTENSIFYLEVEL_MUST_BE_INT, "" )
			return
		if visibleType not in [ 0, 1, 2, 3 ]:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_MODEL_VISIBLE_FORMAT, "" )
			return
		dstEntity.client.remoteCall( "setModelVisible", ( visibleType, ) )
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )

def wizCommand_tong_create( srcEntity, dstEntity, args ):
	"""
	设置tong相关
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_CREATE_FORMAT, "" )
		return
	srcEntity.createTong( dstEntity.id, str(cmds[0]),csdefine.TONG_CREATE_REASON_GM )
	try:
		g_logger.gmCommonLog( "tong_create", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_tong_quit( srcEntity, dstEntity, args ):
	"""
	设置家族相关 接受或拒绝加入家族
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：modelNum
	"""
	srcEntity.tong_quit( srcEntity.id )
	try:
		g_logger.gmCommonLog( "tong_quit", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_specialShop_update( srcEntity, dstEntity, args ):
	"""
	更新道具商城数据
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		BigWorld.globalData[ "SpecialShopMgr" ].updateConfig2DB( True )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SPECIALSHOP_UPDATE_SUCCESS, "" )
		return
	if cmds[ 0 ] == "1":
		BigWorld.globalData[ "SpecialShopMgr" ].updateConfig2DB( False )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SPECIALSHOP_UPDATE_SUCCESS, "" )
	elif cmds[ 0 ] == "0":
		BigWorld.globalData[ "SpecialShopMgr" ].updateConfig2DB( True )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SPECIALSHOP_UPDATE_SUCCESS, "" )
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_PARAM_IS_WRONG, "" )
	try:
		g_logger.gmCommonLog( "specialShop_update", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_destroy_NPC( srcEntity, dstEntity, args ):
	"""
	摧毁指定NPC
	"""
	type = dstEntity.utype
	inValidType = [csdefine.ENTITY_TYPE_PET,csdefine.ENTITY_TYPE_ROLE]
	if type in inValidType :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return
	dstEntity.destroy()
	try:
		g_logger.gmCommonLog( "destroy_NPC", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_accept_quest( srcEntity, dstEntity, args ):
	"""
	给实体添加指定的任务
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,任务ID
	"""
	try:
		questID = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_QUEST_FORMAT, "" )
		return

	from Resource.QuestLoader import QuestsFlyweight
	questIns = QuestsFlyweight.instance()
	try:
		quest = questIns[questID]
	except KeyError:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUESTID_IS_WRONG, "" )
		return
	quest.accept(srcEntity)
	try:
		g_logger.gmCommonLog( "add_quest", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_quest_flag( srcEntity, dstEntity, args ):
	"""
	设置/清除实体身上某个任务的完成标记
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,args[0]为任务ID,args[1]为设置或清除操作的控制标记
	"""
	cmds = args.split()
	if len(cmds) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_QUEST_FLAG_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_QUEST_FLAG_FORMAT_2, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_QUEST_FLAG_FORMAT_3, "" )
		return

	try:
		questID = int( cmds[0] )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUESTID_MUST_BE_INT, "" )
		return

	flag = ""
	tag = cmds[1]
	if tag in ["a","add"]:
		flag = "a"
	elif tag in ["r","remove"]:
		flag = "r"
	else:
		flag = "N/A"

	if not srcEntity.has_quest( questID ): return
	if flag == "r" and questID != 0:				# 清除quest的完成标记
		questData = srcEntity.questsTable[questID]
		for task in questData.getTasks().itervalues():
			task.val1 = 0
			srcEntity.client.onTaskStateUpdate( questID, task )
		try:
			g_logger.gmCommonLog( "set_quest_flag", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return
	elif flag == "r" and questID == 0:			  # 清除所有任务的完成标记
		for qID,quest in srcEntity.questsTable.iteritems():
			for task in quest.getTasks().itervalues():
				if task.val1 == task.val2:
					task.val1 = 0
					srcEntity.client.onTaskStateUpdate( qID, task )
		try:
			g_logger.gmCommonLog( "set_quest_flag", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return
	elif flag == "a" and questID != 0:			  # 给quest添加一个完成标记
		questData = srcEntity.questsTable[questID]
		for task in questData.getTasks().itervalues():
			task.val1 = task.val2
			srcEntity.client.onTaskStateUpdate( questID, task )
		try:
			g_logger.gmCommonLog( "set_quest_flag", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return
	elif flag == "a" and questID == 0:			  # 没有questID则无法添加标记
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_THIS_WORK, "" )
		return
	else:
		return

def wizCommand_set_quest_group( srcEntity, dstEntity, args ):
	cmds = args.split()
	if len( cmds ) != 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_QUEST_GROUP_FORMAT, "" )

	try:
		questID = int( cmds[0] )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUESTID_MUST_BE_INT, "" )
		return

	num  = int( cmds[1] )
	srcEntity.setSubQuestCount( questID, num )

def wizCommand_remove_completed_quest( srcEntity, dstEntity, args ):
	"""
	清掉玩家的已完成任务标志
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,任务ID
	"""
	try:
		questID = int( args, 10 )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_REMOVE_COMPLETED_QUEST_FORMAT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if not dstEntity.isReal():
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ENTITY_NOT_REAL, "" )
		return

	if questID <= 0:
		dstEntity.questsLog.clear()
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_REMOVE_ALL_COMPLETED_QUEST_SUCCESS, "" )
	else:
		dstEntity.questsLog.remove( questID )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_REMOVE_ONE_COMPLETED_QUEST_SUCCESS, str(( questID, )) )

	try:
		g_logger.gmCommonLog( "remove_completed_quest", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_tong_addMoney( srcEntity, dstEntity, args ):
	"""
	增加帮会的金钱
	"""
	try:
		money = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_ADDMONEY_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return
	tong = srcEntity.tong_getTongEntity( tongDBID )
	if tong is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_FIND, str(( srcEntity.getName(), )) )
		return

	if money > 0:
		tong.addMoney( money, csdefine.TONG_CHANGE_MONEY_GMCOMMAND )
	else:
		tong.payMoney( money*-1, True, csdefine.TONG_CHANGE_MONEY_GMCOMMAND )

	try:
		g_logger.gmCommonLog( "tong_addMoney", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_tong_addPrestige( srcEntity, dstEntity, args ):
	"""
	增加帮会声望
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_ADDPRESTIGE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return
	tong = srcEntity.tong_getTongEntity( tongDBID )
	if tong is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_FIND, str(( srcEntity.getName(), )) )
		return

	tong.addPrestige( value, csdefine.TONG_PRESTIGE_CHANGE_GM )
	try:
		g_logger.gmCommonLog( "tong_addPrestige", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_tong_addBasePrestige( srcEntity, dstEntity, args ):
	"""
	增加帮会基础声望
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_ADDPRESTIGE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return
	tong = srcEntity.tong_getTongEntity( tongDBID )
	if tong is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_FIND, str(( srcEntity.getName(), )) )
		return

	tong.addBasePrestige( value )
	try:
		g_logger.gmCommonLog( "tong_addBasePrestige", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_tong_addLevel( srcEntity, dstEntity, args ):
	"""
	增加帮会等级
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_ADDLEVEL_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_ADDLEVEL_FORMAT_2, "" )
		return

	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return
	tong = srcEntity.tong_getTongEntity( tongDBID )
	if tong is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_FIND, str(( srcEntity.getName(), )) )
		return

	if srcEntity.tong_level + value > TLevelEXP.getMaxLevel():
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_LEVEL_TOO_MUSH, str( (TLevelEXP.getMaxLevel(),) ) )
		return
	elif value < 0 and srcEntity.tong_level + value < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_LEVEL_TOO_LESS, "" )
		return
	tong.addLevel( value, csdefine.TONG_LEVEL_CHANGE_REASON_GM )
	try:
		g_logger.gmCommonLog( "tong_addLevel", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_tong_degrade( srcEntity, dstEntity, args ):
	"""
	降低帮会等级
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_DEGRADE_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_DEGRADE_FORMAT_2, "" )
		return

	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return
	tong = srcEntity.tong_getTongEntity( tongDBID )
	if tong is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_FIND, str(( srcEntity.getName(), )) )
		return

	if srcEntity.tong_level + -value < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_LEVEL_TOO_LESS, "" )
		return
	tong.degrade( value, csdefine.TONG_LEVEL_CHANGE_REASON_GM )
	try:
		g_logger.gmCommonLog( "tong_degrade", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_tong_cancelDismiss( srcEntity, dstEntity, args ):
	"""
	取消帮会解散指令
	"""
	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return

	if not srcEntity.checkDutyRights( csdefine.TONG_RIGHT_DISMISS_TONG ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ENTITY_NOT_CHAIRMAN, "" )
		return

	srcEntity.tong_cancelDismissTong( srcEntity.id )
	try:
		g_logger.gmCommonLog( "tong_cancelDismiss", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_tong_addActivityPoint( srcEntity, dstEntity, args ):
	"""
	设置帮会活跃度
	"""
	try:
		point = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_ACTIVITYPOINT_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return
	tong = srcEntity.tong_getTongEntity( tongDBID )
	if tong is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_FIND, str(( srcEntity.getName(), )) )
		return

	tong.AddTongActivityPoint( point )
	try:
		g_logger.gmCommonLog( "tong_addActivityPoint", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_del_city_master( srcEntity, dstEntity, args ):
	argsList = args.split()
	cityName = ""
	if len(argsList) == 1:
		cityName = str(argsList[0])

	if cityName:
		BigWorld.globalData[ "TongManager" ].cityWarDelMaster( cityName )

	try:
		g_logger.gmCommonLog( "del_city_master", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizcommand_activity_control( srcEntity, dstEntity, args ):
	"""
	打开/关闭 一个活动
	"""
	msg = args.split()

	if len( msg ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_CONTROL_FORMAT, "" )
		return

	if not activity_dict.has_key( msg[0] ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_NAME_IS_WRONG, "" )
		keys = ""
		for key in activity_dict:
			keys += ( key + "," )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CURRENT_SUPPORT_ACTIVITY, str(( keys, )) )
		return


	tempInfo = activity_dict[msg[0]]

	if msg[1] == '1':
		#知识问答活动特殊处理//
		if tempInfo[0] == "QuizGameMgr":
			if BigWorld.globalData.has_key( "QuizGame_start" ) and BigWorld.globalData[ "QuizGame_start" ] == True:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_ALREADY_OPEN, "" )
				return
		getattr( BigWorld.globalData[tempInfo[0]], tempInfo[1] )()
		INFO_MSG( "%s(%i): 调用调用打开活动的指令%s" % ( srcEntity.getName(), srcEntity.id, tempInfo[0]) )

	elif msg[1] == '0':
		if tempInfo[2] != "":
			getattr( BigWorld.globalData[tempInfo[0]], tempInfo[2] )()
		else:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_CANNOT_CLOSE, "" )

	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_CONTROL_FORMAT, "" )

	try:
		g_logger.gmCommonLog( "activity_control", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_broadcast( srcEntity, dstEntityID, args ) :
	"""
	系统广播消息
	hyw--2009.03.16
	"""
	msg = args.strip()
	if msg == "" :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_BROADCAST_FORMAT, "" )
	else :
		srcEntity.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, [] )

def wizCommand_lock_speach( srcEntity, dstEntityID, args ) :
	"""
	禁言
	"""
	args = args.split()
	if len( args ) == 1 :
		targetName = args[0]
		chName = ""
	elif len( args ) == 2 :
		targetName, chName = args
	else :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_LOCK_SPEACH_FORMAT, "" )
		return
	srcEntity.base.chat_lockOthersChannel( targetName, chName, 0 )

def wizCommand_unlock_speach( srcEntity, dstEntityID, args ) :
	"""
	解禁发言
	"""
	args = args.split()
	if len( args ) == 1 :
		targetName = args[0]
		chName = ""
	elif len( args ) == 2 :
		targetName, chName = args
	else :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UNLOCK_SPEACH_FORMAT, "" )
		return
	srcEntity.base.chat_unlockOthersChannel( targetName, chName )

def wizCommand_set_silver( srcEntity, dstEntity, args ):
	"""
	给某人设置元宝
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_SILVER_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if value < 0 or value > csconst.ROLE_SILVER_UPPER_LIMIT:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_TREASURE, "" )
		return
	dstEntity.base.remoteCall( "setSilver", ( value, csdefine.CHANGE_SILVER_GMCOMMAND ) )
	INFO_MSG( "%s(%i): set %s(%i) silver to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	try:
		g_logger.gmCommonLog( "set_silver", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_gold( srcEntity, dstEntity, args ):
	"""
	给某人设置元宝
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_GOLD_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if value < 0 or value > csconst.ROLE_GOLD_UPPER_LIMIT:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_TREASURE, "" )
		return
	dstEntity.base.remoteCall( "setGold", ( value, csdefine.CHANGE_GOLD_GMCOMMAND, ) )
	INFO_MSG( "%s(%i): set %s(%i) gold to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	try:
		g_logger.gmCommonLog( "set_gold", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_antiRobotRate( srcEntity, dstEntity, args ):
	"""
	给某人设置元宝
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = float( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ANTIROBOTRATE_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ANTIROBOTRATE_FORMAT_2, "" )
		return

	BigWorld.globalData["AntiRobotVerify_rate"] = value
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ANTIROBOTRATE_SUCCESS, "" )
	INFO_MSG( "%s(%i): set %s(%i) gold to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	try:
		g_logger.gmCommonLog( "set_antiRobotRate", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_pet_calcaneus( srcEntity, dstEntity, args ):
	"""
	增加根骨
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_PET_CALCANEUS_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_PET, "" )
		return

	INFO_MSG( "%s(%i): add %s(%i) calcaneus  %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	dstEntity.remoteCall( "addCalcaneus", ( value, ) )
	try:
		g_logger.gmCommonLog( "add_pet_calcaneus", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_pet_nimbus( srcEntity, dstEntity, args ):
	"""
	设置宠物灵性值
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_NIMBUS_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_PET, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) nimbus from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.nimbus, value) )
	dstEntity.setNimbus( value )
	try:
		g_logger.gmCommonLog( "set_pet_nimbus", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_pet_life( srcEntity, dstEntity, args ):
	"""
	设置宠物寿命
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_LIFE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_PET, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) life from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.life, value) )
	dstEntity.setLife( value )
	try:
		g_logger.gmCommonLog( "set_pet_life", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_pet_joyancy( srcEntity, dstEntity, args ):
	"""
	设置宠物快乐度
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_JOYANCY_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_PET, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) joyancy from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.joyancy, value) )
	dstEntity.setJoyancy( value )
	try:
		g_logger.gmCommonLog( "set_pet_joyancy", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_pet_propagate_finish( srcEntity, dstEntity, args ):
	"""
	宠物繁殖完成
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	msg = args.split()
	if msg != []:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_PROPAGATE_FINISH_FORMAT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) propagate finish" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id ) )
	BigWorld.globalData["PetProcreationMgr"].setProcreated( dstEntity.databaseID )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_PROPAGATE_FINISH_SUCCESS, "" )
	try:
		g_logger.gmCommonLog( "set_pet_propagate_finish", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_pet_storage_time( srcEntity, dstEntity, args ):
	"""
	设置宠物仓库剩余时间
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_STORAGE_TIME_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_REMAINTIME_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) pet remainTime %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	dstEntity.base.set_storageEndTime( value )
	try:
		g_logger.gmCommonLog( "set_pet_storage_time", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_pet_ability(  srcEntity, dstEntity, args ):
	"""
	设置宠物成长度
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_ABILITY_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_PET, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) pet ability %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	dstEntity.setAbility( value )
	try:
		g_logger.gmCommonLog( "wizCommand_set_pet_ability", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_dismiss_tong( srcEntity, dstEntity, args ):
	"""
	立刻解散帮会
	@param srcEntity: Entity; 执行指令的人；
	"""
	msg = args.strip()
	if msg != "" :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_DISMISS_TONG_FORMAT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if dstEntity.tong_getSelfTongEntity() is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TARGET_HAS_NOT_TONG, "" )
		return

	if not srcEntity.checkDutyRights( csdefine.TONG_RIGHT_DISMISS_TONG ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TARGET_IS_NOT_CHAIRMAN, "" )
		return

	INFO_MSG( "%s(%i): dismiss %s(%i) tong" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id ) )
	dstEntity.tong_getSelfTongEntity().onDismissTong( 0, csdefine.TONG_DELETE_REASON_GM )
	try:
		g_logger.gmCommonLog( "dismiss_tong", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_xinglong_prestige( srcEntity, dstEntity, args ):
	"""
	设置兴隆镖局声望
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_XINGLONG_PRESTIGE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) xinglong prestige from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.getPrestige( csconst.FACTION_XL ), value) )
	dstEntity.setPrestige( csconst.FACTION_XL, value )
	try:
		g_logger.gmCommonLog( "set_xinglong_prestige", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_changping_prestige( srcEntity, dstEntity, args ):
	"""
	设置昌平镖局声望
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_CHANGPING_PRESTIGE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) cangping prestige from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.getPrestige( csconst.FACTION_CP ), value) )
	dstEntity.setPrestige( csconst.FACTION_CP, value )
	try:
		g_logger.gmCommonLog( "set_changping_prestige", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_teachCredit( srcEntity, dstEntity, args ):
	"""
	增加功勋值
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_TEACHCREDIT_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): add %s(%i) teach credit: %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	dstEntity.addTeachCredit( value )
	try:
		g_logger.gmCommonLog( "add_teachCredit", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_pk_value( srcEntity, dstEntity, args ):
	"""
	增加PK值
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PK_VALUE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) pk-value from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.pkValue, value) )
	dstEntity.setPkValue( value )
	try:
		g_logger.gmCommonLog( "set_pk_value", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_treasure_map( srcEntity, dstEntity, args ):
	"""
	获得指定等级的藏宝图
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		level = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_TREASURE_MAP_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_LEVEL_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	item = g_items.createDynamicItem( TREASURE_MAP_ID, 1 )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( TREASURE_MAP_ID, )) )
		return

	item.set( 'level',level )
	item.generateLocation( dstEntity, level )

	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND  )
	INFO_MSG( "%s(%i): add item %s amount %i" % (srcEntity.getName(), srcEntity.id, TREASURE_MAP_ID, 1) )
	try:
		g_logger.gmCommonLog( "add_treasure_map", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_title( srcEntity, dstEntity, args ):
	"""
	增加称号
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：称号名
	"""
	if len(args.split()) != 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_TITLE_FORMAT, "" )
		return
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return
	title_dict = {}
	for i in g_titleLoader._datas:
		title_dict[g_titleLoader._datas[i]["name"]] = i

	if args.strip() not in title_dict or args.strip() == "":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TITLE_IS_WRONG, "" )
		return
	INFO_MSG( "%s(%i): add title %s to %s(%i)" % (srcEntity.getName(), srcEntity.id, args.strip(), dstEntity.getName(), dstEntity.id ) )
	dstEntity.addTitle( title_dict[args.strip()] )
	try:
		g_logger.gmCommonLog( "add_title", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_remove_title( srcEntity, dstEntity, args ):
	"""
	清除称号
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：称号名
	"""
	if len(args.split()) != 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_REMOVE_TITLE_FORMAT, "" )
		return
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return
	title_dict = {}
	for i in g_titleLoader._datas:
		title_dict[g_titleLoader._datas[i]["name"]] = i
	if args.strip() not in title_dict:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TITLE_IS_WRONG, "" )
		return
	INFO_MSG( "%s(%i): remove title %s from %s(%i)" % (srcEntity.getName(), srcEntity.id, args.strip(), dstEntity.getName(), dstEntity.id ) )
	dstEntity.removeTitle( title_dict[args.strip()] )
	try:
		g_logger.gmCommonLog( "remove_title", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_clean_activity_record( srcEntity, dstEntity, args ):
	"""
	清除活动标记
	@param srcEntity: Entity; 执行指令的人；
	"""
	msg = args.split()
	if len(msg) != 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CLEAN_ACTIVITY_RECORD_FORMAT, "" )
		return

	if not activityRecord_dict.has_key( msg[0] ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_NOT_SUPPORTED, "" )
		keys = ""
		for key in activityRecord_dict:
			keys += ( key + "," )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CURRENT_SUPPORT_ACTIVITY, str(( keys, )) )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	flag = activityRecord_dict[msg[0]]
	dstEntity.removeActivityFlag( flag )
	key = g_activityRecordMgr.flagsDict[flag].recordKey
	if key in dstEntity.roleRecord:
		dstEntity.roleRecord.pop( key )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CLEAN_ACTIVITY_RECORD_SUCCESS, str(( dstEntity.getName(), msg[0] )) )

	INFO_MSG( "%s(%i): clean %s(%i) %s record!" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, msg[0] ) )
	# setattr( dstEntity, activityRecord_dict[msg[0]], 0 )
	try:
		g_logger.gmCommonLog( "clean_activity_record", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_query_Info( srcEntity, dstEntity, args ):
	"""
	信息查询
	@param srcEntity: Entity; 执行指令的人；
	"""
	BigWorld.globalData['GMMgr'].query_Info( srcEntity.base, args, {} )



def wizCommand_query_Pet_Info( srcEntity, dstEntity, args ):
	"""
	信息查询
	@param srcEntity: Entity; 执行指令的人；
	"""
	BigWorld.globalData['GMMgr'].query_Pet_Info( srcEntity.base, dstEntity.base, args )



def wizCommand_catch( srcEntity, dstEntity, args ):
	"""
	抓人
	@param srcEntity: Entity; 执行指令的人；
	"""
	params = {}
	params['pos'] = srcEntity.position
	params['spaceType'] = srcEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
	params['lineNumber'] = srcEntity.getCurrentSpaceLineNumber()
	BigWorld.globalData['GMMgr'].catch( srcEntity.base, args, params )
	try:
		g_logger.gmCommonLog( "catch", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_cometo( srcEntity, dstEntity, args ):
	"""
	到达他身边
	@param srcEntity: Entity; 执行指令的人；
	"""
	# 增加进监狱支持
	srcEntity.setTemp( "gotoPrison", True )
	BigWorld.globalData['GMMgr'].cometo( srcEntity.base, args, {} )
	try:
		g_logger.gmCommonLog( "cometo", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_kick( srcEntity, dstEntity, args ):
	"""
	踢人
	@param srcEntity: Entity; 执行指令的人；
	"""
	BigWorld.globalData['GMMgr'].kick( srcEntity.base, args, {} )
	try:
		g_logger.gmCommonLog( "kick", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_query_player_amount( srcEntity, dstEntity, args ):
	"""
	人数查询
	@param srcEntity: Entity; 执行指令的人；
	"""
	BigWorld.globalData['GMMgr'].queryPlayerAmount( srcEntity.base, args, {} )


def wizCommand_block_account( srcEntity, dstEntity, args ):
	"""
	封锁帐号
	@param srcEntity: Entity; 执行指令的人；
	"""
	params = {}
	params['name'] = srcEntity.playerName
	BigWorld.globalData['GMMgr'].block_account( srcEntity.base, args, params )
	try:
		g_logger.gmCommonLog( "block_account", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_unBlock_account( srcEntity, dstEntity, args ):
	"""
	解封帐号
	@param srcEntity: Entity; 执行指令的人；
	"""
	params = {}
	params['name'] = srcEntity.playerName
	BigWorld.globalData['GMMgr'].unBlock_account( srcEntity.base, args, params )
	try:
		g_logger.gmCommonLog( "unBlock_account", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_block_role( srcEntity, dstEntity, args ):
	"""
	封锁帐号
	@param srcEntity: Entity; 执行指令的人；
	"""
	return

def wizCommand_query_players_name( srcEntity, dstEntity, args ):
	"""
	封锁帐号
	@param srcEntity: Entity; 执行指令的人；
	"""
	BigWorld.globalData['GMMgr'].queryPlayersName( srcEntity.base, args, {} )


def wizCommand_set_respawn_rate( srcEntity, dstEntity, args ):
	"""
	更新刷怪速度
	@param srcEntity: Entity; 执行指令的人；
	"""
	BigWorld.globalData['GMMgr'].setRespawnRate( srcEntity.base, args, {} )
	try:
		g_logger.gmCommonLog( "set_respawn_rate", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_loginAttemper( srcEntity, dstEntity, args ):
	"""
	设置登录排队调度状态

	@param state : -1,登录调度排队关闭；0，不允许任何登录；>0，允许同时登录的数量。
	"""
	try:
		state = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LOGINATTEMPER_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_STATE_MUST_BE_INT, "" )
		return
	BigWorld.globalData["loginAttemper_count_limit"] = state
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LOGINATTEMPER_SUCCESS, str(( state, )) )

	# 调度状态更改，触发调度
	for key, value in BigWorld.globalData.items():
		if isinstance( key, str ) and key.startswith( "GBAE" ):
			value.loginAttemperTrigger()

	try:
		g_logger.gmCommonLog( "set_loginAttemper", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_baseAppPlayerLimit( srcEntity, dstEntity, args ):
	"""
	设置baseApp最大人数上限
	"""
	try:
		state = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_BASEAPPPLAYERLIMIT_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_STATE_MUST_BE_INT, "" )
		return
	BigWorld.globalData["baseApp_player_count_limit"] = state
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_BASEAPPPLAYERLIMIT_SUCCESS, str(( state, )) )

	# baseApp最大人数上限更改，触发调度
	for key, value in BigWorld.globalData.items():
		if isinstance( key, str ) and key.startswith( "GBAE" ):
			value.loginAttemperTrigger()

	try:
		g_logger.gmCommonLog( "set_baseAppPlayerLimit", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_waitQueue( srcEntity, dstEntity, args ):
	"""
	设置登录调度排队队列上限
	"""
	try:
		state = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_WAITQUEUE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_STATE_MUST_BE_INT, "" )
		return
	BigWorld.globalData["login_waitQueue_limit"] = state
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_WAITQUEUE_SUCCESS, str(( state, )) )

def wizCommand_set_stone( srcEntity, dstEntity, args ):
	"""
	设置魂魄石
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_STONE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

	kastone = dstEntity.getItem_( 12 )

	if kastone.__class__.__name__ != "CKaStone":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_FAIL_TO_SET, "" )
		ERROR_MSG( "该物品不是魂魄石，查看是否魂魄石装备已换位置。" )
		return

	if dstEntity == None or kastone == None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MUST_BE_HAS_STONE, "" )
		return

	if value > kastone.query( "ka_totalCount", 0 ) or value < 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MUST_BE_HAS_OVERRUN, "" )
		return

	kastone.set( 'ka_count',value, dstEntity )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SUCCESS_TO_SET, "" )
	try:
		g_logger.gmCommonLog( "set_stone", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_tong_contribute( srcEntity, dstEntity, args ):
	"""
	设置帮会贡献度
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_TONG_CONTRIBUTE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

	dstTongMailBox = dstEntity.tong_getSelfTongEntity()

	if dstEntity == None or dstTongMailBox == None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TARGET_HAS_NOT_TONG, "" )
		return

	if value > 100000 or value < 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_CONTRIBUTE_OVERRUN, "" )
		return

	offset = value - dstEntity.tong_contribute
	if offset > 0:
		dstEntity.tong_addContribute( offset )
	elif offset < 0:
		offset = 0 - offset
		dstEntity.tong_payContribute( offset )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SUCCESS_TO_SET, "" )
	try:
		g_logger.gmCommonLog( "set_tong_contribute", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_fabao_naijiu( srcEntity, dstEntity, args ):
	"""
	调整法宝耐久
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FABAO_NAIJIU_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

	fabao = dstEntity.getItem_( 13 )

	if dstEntity == None or fabao == None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MUST_HAS_TALISMAN, "" )
		return

	if fabao.__class__.__name__ != "CTalisman":
		ERROR_MSG( "该物品不是法宝，查看是否法宝装备已换位置。" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_FAIL_TO_SET, "" )
		return

	value = value * 1000
	if value > fabao.query( "eq_hardinessLimit", 0 ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HARDINESS_OVERRUN, "" )
		return

	fabao.set( 'eq_hardiness',value, dstEntity )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SUCCESS_TO_SET, "" )
	try:
		g_logger.gmCommonLog( "set_fabao_naijiu", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_fabao_max_naijiu( srcEntity, dstEntity, args ):
	"""
	调整法宝最大耐久上限
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FABAO_MAX_NAIJIU_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

	fabao = dstEntity.getItem_( 13 )

	if dstEntity == None or fabao == None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MUST_HAS_TALISMAN, "" )
		return

	if fabao.__class__.__name__ != "CTalisman":
		ERROR_MSG( "该物品不是法宝，查看是否法宝装备已换位置。" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_FAIL_TO_SET, "" )
		return

	value = value * 1000
	fabao.set( 'eq_hardinessMax',value, dstEntity )
	if value < fabao.query( "eq_hardinessLimit", 0 ):
		fabao.set( 'eq_hardinessLimit',value, dstEntity )
		fabao.set( 'eq_hardiness',value, dstEntity )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SUCCESS_TO_SET, "" )
	try:
		g_logger.gmCommonLog( "set_fabao_max_naijiu", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_fabao_lim_naijiu( srcEntity, dstEntity, args ):
	"""
	调整法宝当前耐久度上限
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FABAO_LIM_NAIJIU_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

	fabao = dstEntity.getItem_( 13 )

	if dstEntity == None or fabao == None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MUST_HAS_TALISMAN, "" )
		return

	value = value * 1000
	fabao.set( 'eq_hardinessLimit',value, dstEntity )
	if value > fabao.query( "eq_hardinessMax", 0 ):
		fabao.set( 'eq_hardinessMax',value, dstEntity )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SUCCESS_TO_SET, "" )
	try:
		g_logger.gmCommonLog( "set_fabao_lim_naijiu", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_fabao_level( srcEntity, dstEntity, args ):
	"""
	调整法宝等级
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FABAO_LEVEL_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

	fabao = dstEntity.getItem_( 13 )

	if dstEntity == None or fabao == None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MUST_HAS_TALISMAN, "" )
		return

	fabao.set( 'level',value, dstEntity )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SUCCESS_TO_SET, "" )
	try:
		g_logger.gmCommonLog( "set_fabao_level", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_fabao_skill_level( srcEntity, dstEntity, args ):
	"""
	调整法宝技能等级
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FABAO_SKILL_LEVEL_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_TARGET, "" )
		return

	fabao = dstEntity.getItem_( 13 )

	if dstEntity == None or fabao == None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MUST_HAS_TALISMAN, "" )
		return

	skillID = fabao.getSpellID()
	if skillID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TALISMAN_HAS_NOT_SKILL, "" )
		return
	else:
		skillID = int( str(skillID)[0:6])*1000 + value
		if not g_skills.has( skillID ):
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TALISMAN_LEVEL_IS_WRONG, "" )
			return
		fabao.setSKillID( skillID, dstEntity )
		dstEntity.addSkill( skillID )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SUCCESS_TO_SET, "" )
	try:
		g_logger.gmCommonLog( "set_fabao_skill_level", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_query_Tong_Info( srcEntity, dstEntity, args ):
	"""
	帮会信息查询
	@param srcEntity: Entity; 执行指令的人；
	"""

	tongDBID = srcEntity.tong_dbID
	if tongDBID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_EXIST, str(( srcEntity.getName(), )) )
		return
	tong = srcEntity.tong_getTongEntity( tongDBID )
	if tong is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TONG_NOT_FIND, str(( srcEntity.getName(), )) )
		return

	tong.queryTongInfo( srcEntity, args )


def wizCommand_query_CellServerPort( srcEntity, dstEntity, args ):
	"""
	查询entity所在cellapp的Python调试端口
	"""
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_CELLSERVERPORT_FORMAT, str(( BigWorld.getWatcher("nub/address").split(":")[0], ":", BigWorld.getWatcher("pythonServerPort") )) )


def wizCommand_cleanBags( srcEntity, dstEntity, args ):
	"""
	清空自身背包(装备栏除外)
	"""
	for item in srcEntity.itemsBag.getDatas():
		if item.getKitID() != csdefine.KB_EQUIP_ID:
			srcEntity.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_COMMAND_CLEANBAGS )

def wizCommand_getTCRItem( srcEntity, dstEntity, args ):
	"""
	获得组队竞赛物品
	"""
	g_rewardMgr.rewards( srcEntity, csdefine.REWARD_TEAMCOMPETITION_ITEMS )

def wizCommand_shutdown(  srcEntity, dstEntity, args ):
	"""
	关闭服务器
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		if args == "now":
			value = 0
		else:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SHUTDOWN_FORMAT_1, "" )
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SHUTDOWN_FORMAT_2, "" )
			return

	try:
		g_logger.gmCommonLog( "shutdown", args, srcEntity.getNameAndID(), srcEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )
	BigWorld.globalData['GMMgr'].shutdown( value )


def wizCommand_watch( srcEntity, dstEntity, args ):
	"""
	设置自身观察者身份
	@param srcEntity: Entity; 执行指令的人；
	"""
	if not srcEntity.queryTemp( "watch_state", False ):
		actPet = srcEntity.pcg_getActPet()
		if actPet: actPet.entity.withdraw( csdefine.PET_WITHDRAW_GMWATCHER )
		srcEntity.effectStateInc( csdefine.EFFECT_STATE_WATCHER )
		srcEntity.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		srcEntity.setTemp( "watch_state", True )
	else:
		srcEntity.effectStateDec( csdefine.EFFECT_STATE_WATCHER )
		srcEntity.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		srcEntity.setTemp( "watch_state", False )


def wizCommand_dropBox( srcEntity, dstEntity, args ):
	"""
	设置自身观察者身份
	@param srcEntity: Entity; 执行指令的人；
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_DROPBOX_FORMAT, "" )
		return

	itemKey = cmds[0]
	try:
		itemKey = int( itemKey )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return
	amount = 1

	if len(cmds) > 1:
		try:
			amount = int( cmds[1] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
			return

	item = g_items.createDynamicItem( itemKey, amount )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, str(( itemKey, )) )
		return

	params = { "dropType" : csdefine.DROPPEDBOX_TYPE_MONSTER, "droperName" : item.name() }
	itemBox = BigWorld.createEntity( "DroppedBox", srcEntity.spaceID, srcEntity.position, srcEntity.direction, params )
	itemBox.init( ( srcEntity.id, 0 ), [item] )

def wizCommand_set_vehicle_level( srcEntity, dstEntity, args ):
	"""
	给当前激活坐骑设置等级
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：vehicleLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VEHICLE_LEVEL_FORMAT, "" )
		return
	try:
		level = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_LEVEL_IS_OVERRUN, "" )
		return

	currVehicleID = getCurrAttrVehicleID( srcEntity )
	if currVehicleID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_VEHICLE, "" )
		return

	if level < 1:level = 1
	if level > 150: level = 150
	srcEntity.base.setVehicleLevel( currVehicleID, level )

	INFO_MSG( "%s(%i): set vehicle(id = %i) level(%i)" % (srcEntity.getName(), srcEntity.id, currVehicleID, level) )
	try:
		g_logger.gmCommonLog( "set_vehicle_level", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_vehicle_growth( srcEntity, dstEntity, args ):
	"""
	给当前激活坐骑设置成长度
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：vehicleLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VEHICLE_GROWTH_FORMAT, "" )
		return
	try:
		growth = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VEHICLE_GROWTH_FORMAT, "" )
		return

	currVehicleID = getCurrAttrVehicleID( srcEntity )
	if currVehicleID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_VEHICLE, "" )
		return

	if growth < 0: growth = 0
	maxGrowth = 2**8 - 1
	if growth > maxGrowth: growth = maxGrowth
	srcEntity.base.setVehicleGrowth( currVehicleID, growth )

	INFO_MSG( "%s(%i): set vehicle(id = %i) growth(%i)" % (srcEntity.getName(), srcEntity.id, currVehicleID, growth) )
	try:
		g_logger.gmCommonLog( "set_vehicle_growth", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_vehicle_exp( srcEntity, dstEntity, args ):
	"""
	给当前激活坐骑设置经验
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：vehicleLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VEHICLE_EXP_FORMAT, "" )
		return
	try:
		exp = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VEHICLE_EXP_FORMAT, "" )
		return

	currVehicleID = getCurrAttrVehicleID( srcEntity )
	if currVehicleID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_VEHICLE, "" )
		return

	if exp < 0:exp = 0
	srcEntity.base.setVehicleExp( currVehicleID, exp )

	INFO_MSG( "%s(%i): set vehicle(id = %i) exp(%i)" % (srcEntity.getName(), srcEntity.id, currVehicleID, exp) )
	try:
		g_logger.gmCommonLog( "set_vehicle_exp", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_vehicle_skPoint( srcEntity, dstEntity, args ):
	"""
	给当前激活坐骑设置技能点
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：vehicleLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VEHICLE_SKPOINT_FORMAT, "" )
		return
	try:
		skPoint = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SKPOINT_IS_OVERRUN, "" )
		return

	currVehicleID = getCurrAttrVehicleID( srcEntity )
	if currVehicleID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_VEHICLE, "" )
		return

	if skPoint < 0: skPoint = 0
	maxSkPoint = 2**32 - 1
	if skPoint > maxSkPoint: skPoint = maxSkPoint
	srcEntity.base.setVehicleSkPoint( currVehicleID, skPoint )

	INFO_MSG( "%s(%i): set vehicle(dbid = %i) skPoint(%i)" % ( srcEntity.getName(), srcEntity.id, currVehicleID, skPoint ) )
	try:
		g_logger.gmCommonLog( "set_vehicle_skPoint", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_vehicle_deadTime( srcEntity, dstEntity, args ):
	"""
	给当前激活坐骑设置死亡时间
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：vehicleLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VEHICLE_DEADTIME_FORMAT, "" )
		return
	try:
		deadTime = int( cmds[0] )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_DEADTIME_IS_OVERRUN, "" )
		return

	currVehicleID = getCurrAttrVehicleID( srcEntity )
	if currVehicleID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_VEHICLE, "" )
		return

	deadTime += int( time.time() )
	srcEntity.base.setVehicleDeadTime( currVehicleID, deadTime )

	INFO_MSG( "%s(%i): set vehicle(dbid = %i) deadTime(%i)" % ( srcEntity.getName(), srcEntity.id, currVehicleID, deadTime ) )
	try:
		g_logger.gmCommonLog( "set_vehicle_deadTime", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_vehicle_fulldegree( srcEntity, dstEntity, args ):
	"""
	给当前激活坐骑增加饱食度
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：vehicleLevel
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_VEHICLE_FULLDEGREE_FORMAT, "" )
		return
	try:
		number = cmds[0]
		unit = number[-1]
		digit = number.replace( unit, "" )
		if unit == "s":
			fullDegree = int( digit )
		elif unit == "m":
			fullDegree = int( digit ) * 60
		elif unit == "h":
			fullDegree = int( digit ) * 60 * 60
		elif unit == "d":
			fullDegree = int( digit ) * 60 * 60 * 24
		else:
			fullDegree = int( number )
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_VEHICLE_FULLDEGREE_FORMAT, "" )
		return

	currVehicleID = getCurrAttrVehicleID( srcEntity )
	if currVehicleID == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_HAS_NOT_VEHICLE, "" )
		return

	minFullDegree = -2**32 + 1
	maxFullDegree = 2**32 - 1
	if fullDegree > maxFullDegree: fullDegree = maxFullDegree
	elif fullDegree < minFullDegree: fullDegree = minFullDegree
	srcEntity.base.addVehicleFullDegree( currVehicleID, fullDegree )

	INFO_MSG( "%s(%i): add vehicle(dbid = %i) fulldegree(%i)" % ( srcEntity.getName(), srcEntity.id, currVehicleID, fulldegree ) )
	try:
		g_logger.gmCommonLog( "add_vehicle_fulldegree", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_update_presentIds( srcEntity, dstEntity, args ):
	"""
	更新webservice奖品ID列表
	TRUNCATE TABLE custom_presents
	使用方式: /update_presentIds 无参数
	"""
	reload(config.server.WebServicePresentIDs)
	def mysqlCallBack( firstStep, srcEntity, result, rows, errstr ):
		"""
		数据库操作回调
		@type	firstStep : bool
		@param	firstStep : 用以区分是哪一条数据库语句进行的回调
		@type	srcEntity : entity
		@param	srcEntity : 使用GM命令的角色
		"""
		if errstr:
			# 生成表格错误的处理
			ERROR_MSG( "update custom_presents table fault! %s" % errstr  )
			return
		if firstStep:
			sql = "INSERT INTO custom_presents(present_id) VALUES"
			valuseDes = ""
			for key in config.server.WebServicePresentIDs.Datas:
				valuseDes += "('%s')," % (key )
			sql += valuseDes[:-1]								# 这里到-1是因为最后多余一个逗号。
			BigWorld.executeRawDatabaseCommand( sql, Functor( mysqlCallBack, False, srcEntity ) )
		else:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_PRESENTIDS_SUCCESS, "" )
			try:
				g_logger.gmCommonLog( "update_presentIds", None, srcEntity.getNameAndID(), None, srcEntity.grade )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
	sql = "TRUNCATE TABLE custom_presents;"
	BigWorld.executeRawDatabaseCommand( sql, Functor( mysqlCallBack, True, srcEntity ) )

def wizCommand_clearBuff( srcEntity, dstEntity, args ):
	"""
	清除自身所有buff
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数
	"""
	srcEntity.clearBuff( [0] )

def wizCommand_add_dance_point( srcEntity, dstEntity, args ):
	"""
	增加跳舞积分 by姜毅
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_DANCE_POINT_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) add_dance_point from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.dancePoint, value) )

	dstEntity.dancePoint += value
	if dstEntity.dancePoint > Const.JING_WU_SHI_KE_MAX_POINT:		# 如果角色跳舞积分没有达到最大累积量
		dstEntity.dancePoint = Const.JING_WU_SHI_KE_MAX_POINT
	dstEntity.dancePointDailyRecord.incrDegree()
	dstEntity.statusMessage( csstatus.JING_WU_SHI_KE_GET_POINT )

	try:
		g_logger.gmCommonLog( "add_dance_point", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_item_life_time( srcEntity, dstEntity, args ):
	"""
	设置首格物品的存活时间 by姜毅
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ITEM_LIFE_TIME_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if value <= 0: return

	item = dstEntity.getItem_( 255 )
	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_FIND_LIFE_ITEM, "" )
		return

	if not item.isActiveLifeTime():
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_HAS_NOT_LIFE_TIME, "" )
		return

	lifeTime = item.getLifeTime()
	deadTime = item.getDeadTime()

	if lifeTime <= 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_IS_DEAD, "" )
		return

	realTime = time.time()
	if value > lifeTime:
		value = lifeTime

	uids = []
	deadTimes = []
	uids.append(item.uid)
	deadTimes.append(deadTime)
	dstEntity.removeLifeItemsFromManage( uids, deadTimes  )

	newDeadTime = value + realTime
	item.setDeadTime( newDeadTime, dstEntity )
	deadTimes = [newDeadTime]
	dstEntity.addLifeItemsToManage( uids, deadTimes )

	INFO_MSG( "%s(%i): set %s(%i) wizCommand_set_item_life_time from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, item.getDeadTime(), value) )
	try:
		g_logger.gmCommonLog( "set_item_life_time", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_full_stone( srcEntity, dstEntity, args ):
	"""
	获得各种类型的满值魂魄石 by姜毅
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_FULL_STONE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEMID_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	item = g_items.createDynamicItem( value, 1 )

	if item is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_EXIST, value )
		return

	if item.getType() != ItemTypeEnum.ITEM_SYSTEM_KASTONE:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_IS_NOT_STONE, "" )
		return

	item.set( 'ka_count', item.query( "ka_totalCount", 0 ), dstEntity )	# 设置魂魄石为满值

	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND )

	INFO_MSG( "%s(%i): add item %s amount %i" % (srcEntity.getName(), srcEntity.id, item.id, 1) )
	try:
		g_logger.gmCommonLog( "add_full_stone", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_vim( srcEntity, dstEntity, args ):
	"""
	设置活力值 by 姜毅
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_VIM_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	dstEntity.setVim( value )

	try:
		g_logger.gmCommonLog( "set_vim", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_lvs_sle( srcEntity, dstEntity, args ):
	"""
	设置生活技能熟练度 by 姜毅
	"""
	cmds = args.split()
	if len( cmds ) <= 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LVS_SLE_FORMAT, "" )
		return
	try:
		skillID = int( cmds[0] )
		value = int( cmds[1] )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LVS_SLE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	dstEntity.setSleight( skillID, value )

	try:
		g_logger.gmCommonLog( "set_lvs_sle", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_tishouSystem( srcEntity, dstEntity, args ):
	"""
	关闭替售功能
	"""
	cmds = args.split()
	if len( cmds ) <= 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_TISHOUSYSTEM_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_FORMAT, "" )
		return
	try:
		value = cmds[0]
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_TISHOUSYSTEM_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_FORMAT, "" )
		return
	if value == "1":
		BigWorld.globalData["TiShouSystemIsAllow"] = "1"
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_TISHOUSYSTEM_OPEN, "" )
	elif value == "0":
		BigWorld.globalData["TiShouSystemIsAllow"] = "0"
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_TISHOUSYSTEM_CLOSE, "" )
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_FORMAT, "" )

def wizCommand_setItemUID( srcEntity, dstEntity, args ):
	"""
	设置物品UID
	"""
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SETITEMUID_FORMAT, "" )
		return
	try:
		pos = int(cmds[0])
		uid = int(cmds[1])
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SETITEMUID_FORMAT, "" )
		return
	item = srcEntity.getItem_( pos )
	if not item:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SETITEMUID_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_FIND, "" )
		return
	if uid < 0 or uid > 2**63:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UID_OVERRUN, "" )
		return
	oldUid = item.uid
	item.uid = uid

	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_UID, str(( item.name(), oldUid, item.uid )) )
	try:
		g_logger.gmCommonLog( "setItemUID", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_queryItemUID( srcEntity, dstEntity, args ):
	"""
	查询物品UID
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERYITEMUID_FORMAT, "" )
		return
	try:
		pos = int(cmds[0])
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERYITEMUID_FORMAT, "" )
		return
	item = srcEntity.getItem_( pos )
	if not item:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERYITEMUID_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ITEM_NOT_FIND, "" )
		return
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_UID, str(( item.name(), item.uid )) )

def wizCommand_sysExpReward( srcEntity, dstEntity, args ):
	"""
	打开系统经验奖励
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SYSEXPREWARD_FORMAT, "" )
		return
	try:
		isOpen = int(cmds[0])
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SYSEXPREWARD_FORMAT, "" )
		return

	if isOpen:
		try:
			mult = float(cmds[1])
		except:
			BigWorld.globalData["SysMultExpMgr"].open( 0 )
			return
		BigWorld.globalData["SysMultExpMgr"].open( mult )
	else:
		BigWorld.globalData["SysMultExpMgr"].onEnd2()

def wizCommand_ybSwitch( srcEntity, dstEntity, args ):
	"""
	开闭元宝交易系统
	"""
	cmds = args.split()
	if len( cmds ) <= 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SWITCH_YBT_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_FORMAT, "" )
		return
	value = cmds[0]
	if value == '0' or value == '1':
		srcEntity.ybt_switch( int( value ) )
	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SWITCH_YBT_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_FORMAT, "" )
		return

def wizCommand_setPBook( srcEntity, dstEntity, args ):
	"""
	设置潜能书潜能点 by 姜毅
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_POTENTIAL_BOOK_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return
	ptb = dstEntity.getItem_( ItemTypeEnum.CEL_POTENTIAL_BOOK )
	if ptb is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_POTENTIAL_BOOK_EMPETY, "" )
		return
	ptb.addPotential( value, dstEntity )

	try:
		g_logger.gmCommonLog( "set_potential_book", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_setGodWeapon( srcEntity,  dstEntity, args ):
	"""
	给背包第一格的武器设置为神器 by 姜毅
	"""
	if dstEntity is None:
		dstEntity = srcEntity
	if dstEntity.iskitbagsLocked():
		srcEntity.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
		return
	weaponItem = dstEntity.getItem_( 255 )
	if weaponItem is None or not weaponItem.getType() in ItemTypeEnum.WEAPON_LIST:
		srcEntity.statusMessage( csstatus.WIZCOMMAND_SET_GOD_WEAPON_NEED_ITEM )
		return
	level = weaponItem.getReqLevel()
	equipGodExp = EquipGodWeaponExp.instance()
	maxLevel = equipGodExp.getGodWeaponMaxLevel()
	minLevel = equipGodExp.getGodWeaponMinLevel()
	if level >= maxLevel:
		srcEntity.statusMessage( csstatus.GW_LEVEL_MAX, maxLevel )
		return
	if level < minLevel:
		srcEntity.statusMessage( csstatus.GW_LEVEL_NOT_ENOUTH, minLevel )
		return
	if weaponItem.getQuality() != ItemTypeEnum.CQT_GREEN:
		srcEntity.statusMessage( csstatus.GW_LEVEL_NOT_ENOUTH, minLevel )
		return
	skillID = equipGodExp.getGodWeaponSkill( level )	# 制作出来的神器在指定的技能列表中进行随机，属性可以向下兼容。
	weaponItem.setGodWeapon( skillID, dstEntity )
	d_item = ChatObjParser.dumpItem( weaponItem )	# 用于物品消息链接
	dstEntity.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", cschannel_msgs.BCT_GOD_WEAPON%( dstEntity.getName(), "${o0}" ), [d_item,] )

def wizCommand_addTeamMember( srcEntity, dstEntity, args ):
	"""
	增加1个队伍人数（把自己再次增加到自己的队伍中）。
	注：
		主要是方便角色一个人组起来进入副本做一些简单测试。
	使用这个指令需要自己先建立队伍。
	"""
	if srcEntity.isInTeam():
		srcEntity.teamMembers.append( srcEntity.teamMembers[0] )
	else:
		srcEntity.client.onStatusMessage( csstatus.SPACE_MISS_NOTTEAM, "" )



def wizCommand_addIECollectCount( srcEntity, dstEntity, args ):
	"""
	科举答题正确几次。

	通过这个主要是造成多次答题正确的现象，让测试检查科举随机奖励是否合理。

	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_POTENTIAL_BOOK_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return
	m = BigWorld.globalData["ImperialExaminationsMgr"]
	for i in xrange( 0, value ):
		m.requestIEExpReward( srcEntity.base, srcEntity.playerName, srcEntity.level, 1.0, 20, 1.0)

def wizCommand_query_ID( srcEntity, dstEntity, args ):
	"""
	查询对象ID
	"""
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str((dstEntity.id, )) )

def wizCommand_checkSeverTime( srcEntity, dstEntity, args ):
	"""
	查询服务器时间
	"""
	TT = time.localtime()
	result = str( TT[0] ) + "/" + str( TT[1] ) + "/" + str( TT[2] ) + " " + str( TT[3] ) + ":" + str( TT[4] ) + ":" + str( TT[5] )
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str((result, )) )


def wizCommand_addWuDaoGuanJunRewardCount( srcEntity, dstEntity, args ):
	"""
	武道大会获得几次冠军奖励

	通过这个主要是造成多次获得武道大会冠军的现象，让测试检查武道大会冠军的奖励是否合理。

	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_POTENTIAL_BOOK_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return
	for i in xrange( 0, value ):
		awarder = Love3.g_rewards.fetch( csdefine.RCG_WD_FORE_LEVEL, srcEntity )
		awarder.award( srcEntity, csdefine.ADD_ITEM_ADDWUDAOAWARD )


def wizCommand_cleanActivityRecord( srcEntity, dstEntity, args ):
	"""
	清理玩家活动记录
	包括所有副本活动和运镖等记录
	"""
	srcEntity.activityFlags = 0
	srcEntity.questNormalDartRecord.dartCount = 0
	srcEntity.questExpDartRecord.dartCount = 0
	srcEntity.questTongDartRecord.dartCount = 0 # 繁体版1.2、1.1没有srcEntity.questTongDartRecord.dartCount 2011-2-23 12:04 by mushuang
	if srcEntity.tong_dbID > 0: srcEntity.base.clearTongDartRecord() # 繁体版1.2、1.1没有 srcEntity.base.clearTongDartRecord 2011-2-23 12:04 by mushuang
	srcEntity.loopQuestLogs = []
	srcEntity.suanGuaZhanBuDailyRecord.reset()
	srcEntity.roleRecord.clear()
	g_activityRecordMgr.initAllActivitysJoinState( srcEntity )

def wizCommand_cleanFeichengwuraoDatas( srcEntity, dstEntity, args ):
	"""
	清理非诚勿扰数据记录
	"""
	BigWorld.globalData["FeichengwuraoMgr"].cleanAllDatas()

def wizCommand_makeFeichengwuraoResult( srcEntity, dstEntity, args ):
	"""
	产生非诚勿扰投票结果
	"""
	if BigWorld.globalData.has_key( "AS_Feichengwurao" ):
		del BigWorld.globalData[ "AS_Feichengwurao" ]
	BigWorld.globalData["FeichengwuraoMgr"].onHandle_result()

def wizCommand_addAFETime( srcEntity, dstEntity, args ):
	"""
	增加自己的自动战斗物品充值的额外时间 by 姜毅
	"""
	value = 0
	try:
		value = int( args )
	except ValueError, errStr:
		return
	srcEntity.base.autoFightExtraTimeCharge( value )

def wizCommand_addAFTime( srcEntity, dstEntity, args ):
	"""
	增加自己的自动战斗物品充值的额外时间 by 姜毅
	"""
	value = 0
	try:
		value = int( args )
	except ValueError, errStr:
		return
	srcEntity.base.autoFightTimeCharge( value )

def wizCommand_openTongFete( srcEntity, dstEntity, args ):
	"""
	设置帮会祭祀开启
	"""
	BigWorld.globalData[ "TongManager" ].requestFete( srcEntity.tong_dbID, srcEntity.tong_grade, srcEntity.base )

def wizCommand_addTongFete( srcEntity, dstEntity, args ):
	"""
	设置帮会祭祀开启
	"""
	try:
		value = int( args )
	except:
		DEBUG_MSG( "指令参数( %s )不正确。" % str( args ) )
		return
	BigWorld.globalData[ "TongManager" ].addTongFeteValue( srcEntity.tong_dbID, value )

def wizCommand_testCmd( srcEntity, dstEntity, args ):
	"""
	夸父神殿第一层BOSS AI 测试。
	"""
	cmds = args.split()
	if cmds[0] == "kfb3":
		kuafu.whiteAIs( srcEntity )
	if cmds[0] == "hsml":
		kuafu.darkSkillManli( srcEntity, dstEntity )

def wizCommand_spell( srcEntity, dstEntity, args ):
	"""
	根据技能ID施放技能
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SKILLID_MUST_BE_INT, "" )
		return
	srcEntity.spellTarget( value, dstEntity.id )

def wizCommand_remove_all_skill( srcEntity, dstEntity, args ):
	"""
	删除某人或宠物的所有技能
	@param srcEntity: Entity; 执行指令的人；
	"""
	if dstEntity.__class__.__name__ != "Role" and dstEntity.__class__.__name__ != "Pet":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_R_P, "" )
		return

	INFO_MSG( "%s(%i): remove all skill from %s(%i)" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id) )
	dstEntity.removeAllSkill()
	try:
		g_logger.gmCommonLog( "remove_all_skill", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_goodness_value( srcEntity, dstEntity, args ):
	"""
	设置善恶值
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_GOODNESS_VALUE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) goodness-value from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.goodnessValue, value) )
	dstEntity.setGoodnessValue( value )
	try:
		g_logger.gmCommonLog( "set_goodness_value", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_i_can_fly( srcEntity, dstEntity, args ):
	"""
	设置角色的飞行标志
	"""
	testSkillID = 922258001

	if srcEntity.hasFlag( csdefine.ROLE_FLAG_FLY ):
		return

	#srcEntity.client.onEnterFlyState() # 不用手动调用，buff会自动处理
	try:
		spell = g_skills[ testSkillID ]
	except:
		ERROR_MSG( "Failed to load test skill!" )
		ERROR_MSG( "ican_fly ignored!" )
		return

	# 判断是否有不允许骑乘标志
	if srcEntity.actionSign( csdefine.ACTION_FORBID_VEHICLE ):
		srcEntity.actCounterDec( csdefine.ACTION_FORBID_VEHICLE )		#去掉飞行的行为限制，实现在有骑乘限制的副本里飞行
		srcEntity.setTemp( "fobid_cehicle",True )
	spell.receiveLinkBuff( srcEntity, srcEntity )

	try:
		g_logger.gmCommonLog( "i_can_fly", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_let_me_down( srcEntity, dstEntity, args ):
	"""
	删除角色的飞行标志
	"""
	if not srcEntity.hasFlag( csdefine.ROLE_FLAG_FLY ):
		ERROR_MSG( "Role is not flying, let_me_down ignored!" )
		return

	testBuffID = 92225800101

	srcEntity.removeBuffByID( testBuffID, [ csdefine.BUFF_INTERRUPT_REQUEST_CANCEL ] )
	if srcEntity.queryTemp( "fobid_cehicle",False ):
		srcEntity.actCounterInc( csdefine.ACTION_FORBID_VEHICLE )
		srcEntity.removeTemp( "fobid_cehicle" )

	# srcEntity.client.onLeaveFlyState() # 不用手动调用，buff会自动处理
	try:
		g_logger.gmCommonLog( "let_me_down", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_add_prestige( srcEntity, dstEntity, args ):
	"""
	增加势力声望
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_PRESTIGE_FORMAT, "" )
		return

	curPrestige = dstEntity.getPrestigeByName( cmds[0] )
	if curPrestige is None:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_FIND_PRESTIGE_NAME, "" )
		return

	try:
		value = int(cmds[1])
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_VALUE_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): add %s(%i) prestige from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, curPrestige, curPrestige + value ) )
	dstEntity.addPrestigeByName( cmds[0], value )
	try:
		g_logger.gmCommonLog( "add_prestige", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_reset_prestige( srcEntity, dstEntity, args ):
	"""
	重置所有声望
	@param srcEntity: Entity; 执行指令的人；
	"""
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): reset prestige from %s(%i)" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id) )
	dstEntity.resetPrestige()
	try:
		g_logger.gmCommonLog( "reset_prestige", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_refresh_TSCquest( srcEntity, dstEntity, args ):
	"""
	强制刷新本服务器的帮会副本任务
	@param srcEntity: Entity; 执行指令的人；
	"""

	INFO_MSG( "Forcing to refresh tong spacecopy quest by ( %s, %s )"%( srcEntity.getName(), srcEntity.id ) )

	from Resource.QuestLoader import QuestsFlyweight
	inst = QuestsFlyweight.instance()
	tscquestGrp = [ q for q in inst._quests.values() if q._style == csdefine.QUEST_STYLE_TONG_SPACE_COPY  ]

	for q in tscquestGrp:
		q.forceRefresh(srcEntity)

	srcEntity.statusMessage( csstatus.TSC_QUEST_REFRESHED )

	try:
		g_logger.gmCommonLog( "refreshTSCquest", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_potential_map( srcEntity, dstEntity, args ):
	"""
	设置潜能副本进入固定地图
	"""
	srcEntity.setTemp( "gmSetPotentialMap", args )



def wizCommand_set_onlineTime( srcEntity, dstEntity, args ):
	"""
	给某人设置在线时间
	@param srcEntity: Entity;
	@param args: 指令参数，字符串数组，amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ONLINETIME_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if value < 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_TRUE, "" )
		return

	dstEntity.base.remoteCall( "setOnlineTime", ( value, ) )
	INFO_MSG( "%s(%i): set %s(%i) online time to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	try:
		g_logger.gmCommonLog( "set_onlineTime", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_lastweekTime( srcEntity, dstEntity, args ):
	"""
	给某人设置上周在线时间
	@param srcEntity: Entity;
	@param args: 指令参数，字符串数组，amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LASTWEEKTIME_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if value < 0 or value > 7*24*3600:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_TRUE, "" )
		return

	dstEntity.base.remoteCall( "setLastWeekOnlineTime", ( value, ) )
	INFO_MSG( "%s(%i): set %s(%i) lastweek online time to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	try:
		g_logger.gmCommonLog( "set_lastweekTime", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_signUpTime( srcEntity, dstEntity, args ):
	"""
	设置活动剩余报名时间
	@param srcEntity: Entity;
	@param args: 指令参数，字符串数组，amount
	"""
	msg = args.split()

	if len( msg ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_CONTROL_FORMAT, "" )
		return

	try:
		value = int( msg[1] )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_SIGNUPTIME_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if value % 60 != 0 or value < 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_SET_TRUE, "" )
		return

	if msg[0] == cschannel_msgs.WIZCOMMAND_ZU_DUI_JING_SAI:
		BigWorld.globalData["TeamCompetitionMgr"].setSignUpTime( value )

		INFO_MSG( "%s(%i): 调用设置组队竞赛剩余报名时间的指令" % ( srcEntity.getName(), srcEntity.id ) )
		try:
			g_logger.gmCommonLog( "set_signUpTime", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	elif msg[0] == cschannel_msgs.WIZCOMMAND_BANG_HUI_JING_JI:
		BigWorld.globalData["TongCompetitionMgr"].setSignUpTime( value )
		INFO_MSG( "%s(%i): 调用设置帮会竞技剩余报名时间的指令" % ( srcEntity.getName(), srcEntity.id ) )
		try:
			g_logger.gmCommonLog( "set_signUpTime", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	else:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_NAME_IS_WRONG, "" )
		return

	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_SIGNUPTIME_SUCCESS,str(( value/60, )) )

def wizCommand_set_tongCompetitionScore( srcEntity, dstEntity, args ):
	"""
	设置帮会竞技积分
	@param srcEntity: Entity;
	@param args: 指令参数，字符串数组，amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_POTENTIAL_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	INFO_MSG( "%s(%i): set %s(%i) tongCompetitionScore from %i to %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, dstEntity.tongCompetitionScore, value) )
	dstEntity.tongCompetitionScore = value
	try:
		g_logger.gmCommonLog( "set_tongCompetitionScore", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_updateAI( srcEntity, dstEntity, args ):
	"""
	更新AI
	"""
	try:
		cmds = args.split()
		floder = cmds[0]
		className = cmds[1]
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_AI_FORMAT, "" )
		return
	AI_reload.updateMonsterAI( srcEntity, cmds[0], cmds[1] )

def wizCommand_updateSkill( srcEntity, dstEntity, args ):
	"""
	更新技能
	"""
	try:
		cmds = args.split()
		floder = cmds[0]
		className = cmds[1]
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_SKILL_FORMAT, "" )
		return
	Skill_reload.updateSkill( srcEntity, cmds[0], int(cmds[1]) )
	srcEntity.client.updateSkill( cmds[0], int(cmds[1]) )

def wizCommand_updateItem( srcEntity, dstEntity, args ):
	"""
	更新物品
	"""
	try:
		cmds = args.split()
		floder = cmds[0]
		className = cmds[1]
	except:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_ITEM_FORMAT, "" )
		return
	Item_reload.updateItem( srcEntity, cmds[0], int(cmds[1]) )
	srcEntity.client.updateItem( cmds[0], int(cmds[1]) )

def wizCommand_upgradeSkill( srcEntity, dstEntity, args ):
	"""
	升级技能
	"""
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPGRADE_SKILL_FORMAT, "" )
		return
	oldSkId = int(cmds[0])
	newSkId = int(cmds[1])
	INFO_MSG( "%s(%i): remove all skill from %s(%i)" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id) )
	if dstEntity.updateSkill( oldSkId, newSkId ):
		try:
			g_logger.gmCommonLog( "upgradeSkill", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_viewerEnter( srcEntity, dstEntity, args ):
	# 以观察者模式进入指定副本
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SPACE_VIEWER_ENTER_FORMAT, "" )
		return
	spaceKey = cmds[0]
	spaceID = int(cmds[1])
	srcEntity.spaceViewerEnter( spaceKey, spaceID )
	try:
		g_logger.gmCommonLog( "viewerEnter", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_global_data( srcEntity, dstEntity, args ):
	"""
	设置globalData
	"""
	cmds = args.split()
	if len( cmds ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GLOBAL_DATA_FORMAT, "" )
		return
	key = cmds[0]
	value = int(cmds[1])
	BigWorld.globalData[ key ] = value
	try:
		g_logger.gmCommonLog( "set_global_data", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_fhlt_join( srcEntity, dstEntity, args ):
	argsList = args.split()
	cityName = ""
	if len(argsList) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FHLT_JOIN_FORMAT, "" )
		return

	cityName = str(argsList[0])
	tongNameList = argsList[1:]

	if cityName and cityName in csconst.TONG_CITYWAR_CITY_MAPS.iterkeys():
		BigWorld.globalData[ "TongManager" ].setFHLTJoin( cityName, tongNameList )
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_FHLT_JOIN_SUCCESS, str( ( cityName, ) ) )

	try:
		g_logger.gmCommonLog( "set_fhlt_join", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_del_fhlt_join( srcEntity, dstEntity, args ):
	argsList = args.split()
	cityName = ""
	if len(argsList) == 1:
		cityName = str(argsList[0])

	if cityName:
		BigWorld.globalData[ "TongManager" ].clearFHLTJoin( cityName )

	try:
		g_logger.gmCommonLog( "del_fhlt_join", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_gotoPosition( srcEntity, dstEntity, args ):
	"""
	进入一个场景
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：spaceKey px py pz
	"""
	cmds = args.split()
	cmdLen = len( cmds )

	if cmdLen == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTOLINE_FORMAT_2, "" )
		return
	position = ( float(cmds[0]), float(cmds[1]), float(cmds[2]) )
	# 增加进监狱支持
	srcEntity.setTemp( "gotoPrison", True )
	spaceName = srcEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
	srcEntity.gotoSpace( spaceName, position, ( 0, 0, 0 ) )

	try:
		g_logger.gmCommonLog( "goto", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_switchFengQi( srcEntity, dstEntity, args ):
	"""
	客户端解锁聊天框
	@param srcEntity: Entity; 执行指令的人；
	@param args:
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_PET_NIMBUS_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return
	unLocked = bool( value )
	srcEntity.chat_onSwitchFengQi( unLocked )

def wizCommand_set_jiyuan( srcEntity, dstEntity, args ):
	"""
	给某人设置机缘值
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_JIYUAN_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	dstEntity.base.remoteCall( "set_jiyuan", ( value, ) )
	INFO_MSG( "%s(%i): add %s(%i) jiyuan %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	try:
		g_logger.gmCommonLog( "set_jiyuan", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_ZDScore( srcEntity, dstEntity, args ):
	"""
	给某人设置证道积分
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ZDSCORE_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_AMOUNT_MUST_BE_INT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	dstEntity.base.remoteCall( "set_ZDScore", ( value, ) )
	INFO_MSG( "%s(%i): add %s(%i) ZDScore %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
	try:
		g_logger.gmCommonLog( "set_ZDScore", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_daofa( srcEntity, dstEntity, args ):
	"""
	给普通道心中增加一个道法
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	args = args.split()
	if len( args ) < 2:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_DAOFA_FORMAT, "" )
		return

	quality, type = int( args[ 0 ] ), int( args[ 1 ] )
	level = 1
	if len( args ) == 3:
		try:
			 level = int( args[2] )
		except ValueError, errStr:
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_DAOFA_FORMAT, "" )
			return

	if quality not in [ 2, 3, 4, 5]:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_DAOFA_QUALITY_FORMAT, "" )
		return

	from ZDDataLoader import DaofaDataLoader
	g_daofa = DaofaDataLoader.instance()
	if type not in g_daofa.getAllTypeByQuality( quality ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_DAOFA_TYPE_NOT_EXIST, ( quality, type ) )
		return

	if level > csconst.DAOFA_MAX_LEVEL[ quality ]:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_DAOFA_LEVEL_WRONG, ( quality, csconst.DAOFA_MAX_LEVEL[ quality ] ) )
		return

	dstEntity.base.remoteCall( "dynamicCreateDaofa", ( quality, type, level ) )
	INFO_MSG( "%s(%i): add %s(%i) daofa: quality %i, type %i, level %i" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, quality, type, level ) )
	try:
		g_logger.gmCommonLog( "add_daofa", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_open_campActivity( srcEntity, dstEntity, args ):
	"""
	开启特定地图特定类型的阵营活动
	@param srcEntity: Entity; 执行指令的人；
	@param args: 指令参数,字符串数组：amount
	"""
	args = args.split()
	if len( args ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_INVALID_PARAM, "" )
		return

	type = 0
	spaces = []
	camp = 0

	if len( args ) < 1:
		BigWorld.globalData[ "CampMgr" ].onEnd()
		BigWorld.globalData[ "CampMgr" ].onStart()		#改为如果不填入参数则自动开启活动，填入参数则按填入值：GRL
		return
	else:
		type= int( args[ 0 ] )

	if len( args ) >= 2:
		spaces = str( args[ 1 ] ).split( "," )

	if len( args ) >= 3:
		camp = int( args[ 2 ] )

	BigWorld.globalData[ "CampMgr" ].start( type, spaces, camp )
	try:
		g_logger.gmCommonLog( "open_campActivity", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_bovineDevil_map( srcEntity, dstEntity, args ):
	"""
	设置牛魔王活动在特定地图刷新
	"""
	newArgs = args.strip()
	if newArgs:
		BigWorld.globalData[ "BovineDevilMgr" ].setGMSpaceName( newArgs )
	try:
		g_logger.gmCommonLog( "set_bovineDevil_map", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_spaceDoor( srcEntity, dstEntity, args ):
	"""
	设置传送门的开放时间
	参数参考csol-2042传送门的时间参数的写
	如 8:00-10:00
	1|8:00-10:00
	1
	如果参数为空，表示此传送门与以前的传送门一样，成为无限制传送门，可以自由传送
	"""
	for entity in srcEntity.entitiesInRangeExt(50):
		if isinstance(entity, SpaceDoor.SpaceDoor):
			entity.opentime = str(args)
	try:
		g_logger.gmCommonLog( "spacedoor", args, srcEntity )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_set_liuwangmu_floortimelimit( srcEntity, dstEntity, args ):
	"""
	"""
	minutes = int(args)
	BigWorld.globalData["LiuWangMuMgr"].set_floorTimeLimit(minutes)
	try:
		g_logger.gmCommonLog( "gm test set liuwangmu floortimelimit", args, srcEntity )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_liuwangmu_openfloor( srcEntity, dstEntity, args ):
	"""
	"""
	floorNum = int(args)
	BigWorld.globalData["LiuWangMuMgr"].set_openFloor(floorNum)
	try:
		g_logger.gmCommonLog( "gm test set liuwangmu floornum", args, srcEntity )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_test_danceActivity( srcEntity, dstEntity, args ):
	"""
	"""
	args = args.split()
	personLimit = 	int(args[0])
	timeLimit 	=	int(args[1])
	flag = 			int(args[2])
	if flag:
		BigWorld.globalData["DanceMgr"].testDanceActivity(personLimit, timeLimit, True)
	else:
		BigWorld.globalData["DanceMgr"].testDanceActivity(personLimit, timeLimit, False)


def wizCommand_moveto(srcEntity, dstEntity, args):
	"""
	移动到某个目标点，添加这个的原因是客户端机器人
	移动不方便，可能会动不了，所以允许机器人走到
	服务器端控制移动。但是这个命令不限于机器人使用
	"""
	try:
		# 位置是浮点数3元组
		position = tuple([float(i) for i in args.split()][:3])
	except ValueError, err:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MOVE_TO_ARGS_ERROR, str((args, )) )
		return

	DEBUG_MSG("----->>> position is %s, args is %s" % (position, args))

	# 检查参数个数
	if len(position) != 3:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MOVE_TO_ARGS_ERROR, str((args, )) )
		return

	# 开始移动.
	dstEntity.gotoPosition(position)

	try:
		g_logger.gmCommonLog( "moveto", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


g_wizCommandDict = {}
def ADD_COMMAND( cmd, grade, func ):
	assert cmd not in g_wizCommandDict
	g_wizCommandDict[cmd] = ( grade, func )

# 指令索引集,值为( 使用权限,命令入口 )
# 玩家的默认权限：30
# 应北京运营要求，禁止所有会给玩家角色带来利益的指令
# 以后所有会给玩家带来利益的指令必须设为110以上方可上传。
# 在开发中有需要用到调试指令的，请在自己的服务器上手动修改相关指令权限，
# 且坚决不允许上传。
ADD_COMMAND( "set_grade",                      120, wizCommand_set_grade )                  # targetID grade
ADD_COMMAND( "query_grade",                    120, wizCommand_query_grade )                # targetID grade
ADD_COMMAND( "set_attr",                       110, wizCommand_set_attr )                   # targetID key value
ADD_COMMAND( "set_attr_full",                  120, wizCommand_set_attr_full )              # targetID value
ADD_COMMAND( "query_attr",                     70,  wizCommand_query_attr )                 # targetID key value
ADD_COMMAND( "set",                            110, wizCommand_set )                        # targetID key value
ADD_COMMAND( "query",                          110, wizCommand_query_persistent )           # targetID key
ADD_COMMAND( "set_temp",                       110, wizCommand_set_temp )                   # targetID key value
ADD_COMMAND( "query_temp",                     110, wizCommand_query_temp )                 # targetID key

ADD_COMMAND( "clone",                          80,  wizCommand_clone )                      # npcKey
ADD_COMMAND( "drop_item",                      110, wizCommand_drop_item )                  # itemKey amount
ADD_COMMAND( "add_item",                       110, wizCommand_add_item )                   # itemKey amount
ADD_COMMAND( "add_luckyBox",                   110, wizCommand_add_luckyBox )               # itemKey amount
ADD_COMMAND( "add_skill",                      110, wizCommand_add_skill )                  # [targetID] skillID
ADD_COMMAND( "remove_skill",                   110, wizCommand_remove_skill )               # [targetID] skillID
ADD_COMMAND( "set_level",                      110, wizCommand_set_level )                  # [targetID] level
ADD_COMMAND( "set_camp",                       110, wizCommand_set_camp )                  # [targetID] level
ADD_COMMAND( "set_adult",                      110, wizCommand_set_adult )                  # [targetID] adult
ADD_COMMAND( "set_anti",                       110, wizCommand_set_anti )                   # [targetID] adult
ADD_COMMAND( "set_money",                      110, wizCommand_set_money )                  # [targetID] amount
ADD_COMMAND( "set_exp",                        110, wizCommand_set_exp )                    # [targetID] amount
ADD_COMMAND( "set_potential",                  110, wizCommand_set_potential )              # [targetID] amount

ADD_COMMAND( "set_model",                      110, wizCommand_set_model )                  # [targetID] modelNum
ADD_COMMAND( "set_lefthand",                   110, wizCommand_set_lefthand )               # [targetID] itemID [quality][intensifyLevel][lastStuddedID][StuddedAmount]
ADD_COMMAND( "set_righthand",                  110, wizCommand_set_righthand )              # [targetID] itemID [quality][intensifyLevel][lastStuddedID][StuddedAmount]
ADD_COMMAND( "set_body",                       110, wizCommand_set_body )                   # [targetID] itemID [quality][intensifyLevel]
ADD_COMMAND( "set_vola",                       110, wizCommand_set_vola )                   # [targetID] itemID [quality][intensifyLevel]
ADD_COMMAND( "set_breech",                     110, wizCommand_set_breech )                 # [targetID] itemID [quality][intensifyLevel]
ADD_COMMAND( "set_feet",                       110, wizCommand_set_feet )                   # [targetID] itemID [quality][intensifyLevel]
ADD_COMMAND( "set_model_visible",              110, wizCommand_set_model_visible )          # [targetID] visibleType

ADD_COMMAND( "add_equip",                      110, wizCommand_add_equip )                  # itemKey [quality] [prefix] [slot]
ADD_COMMAND( "add_equip_t",                    110, wizCommand_add_equip_ten )              # itemKey [quality] [prefix] [slot]

ADD_COMMAND( "tong_create",                    110, wizCommand_tong_create )                # tongName
ADD_COMMAND( "tong_quit",                      110, wizCommand_tong_quit )                  # ""
ADD_COMMAND( "tong_addMoney",                  110, wizCommand_tong_addMoney )              # money
ADD_COMMAND( "tong_addPrestige",               110, wizCommand_tong_addPrestige )           # prestige value
ADD_COMMAND( "tong_addBasePrestige",               110, wizCommand_tong_addBasePrestige )           # prestige value
ADD_COMMAND( "tong_addLevel",                  110, wizCommand_tong_addLevel )              # level
ADD_COMMAND( "tong_degrade",                   110, wizCommand_tong_degrade )               # level
ADD_COMMAND( "tong_cancelDismiss",             110, wizCommand_tong_cancelDismiss )         # 取消解散
ADD_COMMAND( "tong_addContribute",             110, wizCommand_set_tong_contribute )        # 设置帮会贡献度
ADD_COMMAND( "tong_addActivityPoint",          110, wizCommand_tong_addActivityPoint )      # 设置帮会活跃度
ADD_COMMAND( "del_city_master",				   110, wizCommand_del_city_master )     		# 删除城主

ADD_COMMAND( "smash",                          80,  wizCommand_destroy_NPC )                # targetID
ADD_COMMAND( "dismiss_tong",                   110, wizCommand_dismiss_tong )               # 立刻解散帮会

ADD_COMMAND( "accept_quest",                   80,  wizCommand_accept_quest )               # questID
ADD_COMMAND( "set_quest_flag",                 110, wizCommand_set_quest_flag )             # questID
ADD_COMMAND( "set_quest_group",                110, wizCommand_set_quest_group )             # questID
ADD_COMMAND( "remove_completed_quest",         110, wizCommand_remove_completed_quest )     # questID

ADD_COMMAND( "lock_speach",                    50,  wizCommand_lock_speach )                # 禁言（hyw--2009.09.16）
ADD_COMMAND( "unlock_speach",                  50,  wizCommand_unlock_speach )              # 禁言（hyw--2009.09.16）

ADD_COMMAND( "set_silver",                     110, wizCommand_set_silver )                 # 设置银元宝
ADD_COMMAND( "set_gold",                       110, wizCommand_set_gold )                   # 设置金元宝

ADD_COMMAND( "add_pet_calcaneus",              110, wizCommand_add_pet_calcaneus )          # 增加宠物根骨
ADD_COMMAND( "set_pet_nimbus",                 110, wizCommand_set_pet_nimbus )             # 设置宠物灵性值
ADD_COMMAND( "set_pet_life",                   110, wizCommand_set_pet_life )               # 设置宠物寿命
ADD_COMMAND( "set_pet_joyancy",                110, wizCommand_set_pet_joyancy )            # 设置宠物快乐度
ADD_COMMAND( "set_pet_propagate_finish",       110, wizCommand_set_pet_propagate_finish )   # 完成宠物繁殖
ADD_COMMAND( "set_pet_storage_time",           110, wizCommand_set_pet_storage_time )       # 设置宠物仓库剩余时间
ADD_COMMAND( "set_pet_ability",                110, wizCommand_set_pet_ability )            # 设置宠物成长度

ADD_COMMAND( "set_stone",                      110, wizCommand_set_stone )                  # 设置魂魄石
ADD_COMMAND( "set_fabao_lim_naijiu",           110, wizCommand_set_fabao_lim_naijiu )       # 设置法宝当前最大耐久
ADD_COMMAND( "set_fabao_max_naijiu",           110, wizCommand_set_fabao_max_naijiu )       # 设置法宝最大耐久上限
ADD_COMMAND( "set_fabao_naijiu",               110, wizCommand_set_fabao_naijiu )           # 设置法宝耐久
ADD_COMMAND( "set_fabao_level",                110, wizCommand_set_fabao_level )            # 设置法宝级别
ADD_COMMAND( "set_fabao_skill_level",          110, wizCommand_set_fabao_skill_level )      # 设置法宝技能级别

ADD_COMMAND( "set_xinglong_prestige",          110, wizCommand_set_xinglong_prestige )      # 设置兴隆镖局声望
ADD_COMMAND( "set_changping_prestige",         110, wizCommand_set_changping_prestige )     # 设置昌平镖局声望

ADD_COMMAND( "add_teachCredit",                110, wizCommand_add_teachCredit )            # 增加功勋值
ADD_COMMAND( "set_pk_value",                   110, wizCommand_set_pk_value )               # 设置PK值

ADD_COMMAND( "add_treasure_map",               110, wizCommand_add_treasure_map )           # 增加指定等级藏宝图物品

ADD_COMMAND( "add_title",                      110, wizCommand_add_title )                  # 增加指定等级藏宝图物品
ADD_COMMAND( "remove_title",                   110, wizCommand_remove_title )               # 增加指定等级藏宝图物品

ADD_COMMAND( "query_Info",                     70,  wizCommand_query_Info )                 # 查询角色信息
ADD_COMMAND( "block_role",                     40,  wizCommand_block_role )                 # 封锁角色
ADD_COMMAND( "query_players_name",             80,  wizCommand_query_players_name )         # 查询所有玩家的名字
ADD_COMMAND( "set_respawn_rate",               40,  wizCommand_set_respawn_rate )           # 更新一类怪物的刷新速度
ADD_COMMAND( "set_loginAttemper",              110, wizCommand_set_loginAttemper )          # 登录调度登录队列设置
ADD_COMMAND( "set_baseAppPlayerLimit",         110, wizCommand_set_baseAppPlayerLimit )     # 设置单baseApp的最大玩家数量限制
ADD_COMMAND( "set_waitQueue",                  110, wizCommand_set_waitQueue )              # 登录调度排队队列设置
ADD_COMMAND( "clearBuff",                      50,  wizCommand_clearBuff )                  # 清除自身buff
ADD_COMMAND( "query_Pet_Info",                 70,  wizCommand_query_Pet_Info )             # 查询宠物信息
ADD_COMMAND( "query_Tong_Info",                70,  wizCommand_query_Tong_Info )            # 查询帮会信息
ADD_COMMAND( "clean_activity_record",          110, wizCommand_clean_activity_record )      # 清除某个活动的记录
ADD_COMMAND( "query_CellServerPort",           110, wizCommand_query_CellServerPort )       # 查询cellapp服务器端口
ADD_COMMAND( "cleanBags",                      110, wizCommand_cleanBags )                  # 清空背包(装备栏除外)
ADD_COMMAND( "getTCRItem",                     110, wizCommand_getTCRItem )                 # 获得组队竞赛奖励
ADD_COMMAND( "shutdown",                       40,  wizCommand_shutdown )                   # 关闭服务器
ADD_COMMAND( "watch",                          110, wizCommand_watch )                      # 观察者
ADD_COMMAND( "dropBox",                        110, wizCommand_dropBox )                    # 掉落箱子

ADD_COMMAND( "set_vehicle_level",              110, wizCommand_set_vehicle_level )          # 设置骑宠等级
ADD_COMMAND( "set_vehicle_growth",             110, wizCommand_set_vehicle_growth )         # 设置骑宠成长度
ADD_COMMAND( "set_vehicle_skPoint",            110, wizCommand_set_vehicle_skPoint )        # 设置骑宠技能点
ADD_COMMAND( "set_vehicle_deadTime",           110, wizCommand_set_vehicle_deadTime )       # 设置骑宠剩余时间
ADD_COMMAND( "add_vehicle_fulldegree",         110, wizCommand_add_vehicle_fulldegree )     # 增加骑宠饱食度
ADD_COMMAND( "set_vehicle_exp",        		   110, wizCommand_set_vehicle_exp )      		# 设置骑宠经验

ADD_COMMAND( "update_presentIds",              110, wizCommand_update_presentIds )          # 更新webservice奖品ID列表
ADD_COMMAND( "add_dance_point",                110, wizCommand_add_dance_point )            # 增加跳舞积分
ADD_COMMAND( "add_full_stone",                 110, wizCommand_add_full_stone )             # 获得各种类型的满值魂魄石
ADD_COMMAND( "set_item_life_time",             110, wizCommand_set_item_life_time )         # 设置首格物品的存活时间
ADD_COMMAND( "set_antiRobotRate",              110, wizCommand_set_antiRobotRate )          # 设置反外挂验证触发概率
ADD_COMMAND( "set_vim",                        110, wizCommand_set_vim )                    # 设置活力值 by 姜毅
ADD_COMMAND( "set_lvs_sle",                    110, wizCommand_set_lvs_sle )                # 设置生活技能熟练度 by 姜毅
ADD_COMMAND( "set_tishouSystem",               110, wizCommand_set_tishouSystem )           # 关闭替售功能
ADD_COMMAND( "setItemUID",                     120, wizCommand_setItemUID )                 # 设置物品的uid
ADD_COMMAND( "queryItemUID",                   120, wizCommand_queryItemUID )               # 查询物品的uid
ADD_COMMAND( "sysExpReward",                   120, wizCommand_sysExpReward )               # 打开系统经验奖励
ADD_COMMAND( "ybtSwitch",                      120, wizCommand_ybSwitch )                   # 开闭元宝交易系统
ADD_COMMAND( "set_potential_book",             120, wizCommand_setPBook )                   # 设置潜能书潜能点
ADD_COMMAND( "addTeamMember",                  120, wizCommand_addTeamMember )              # 增加自己建立的队伍人数
ADD_COMMAND( "addIEAnswerRight",               120, wizCommand_addIECollectCount )          # 科举考试答题正确。
ADD_COMMAND( "query_id",                       30, wizCommand_query_ID )                    # 查看对象ID。
ADD_COMMAND( "query_serverTime",               110, wizCommand_checkSeverTime )             # 查看当前服务器时间
ADD_COMMAND( "addWuDaoGJRC",                   120, wizCommand_addWuDaoGuanJunRewardCount ) # 获得武道大会冠军奖励次数。
ADD_COMMAND( "cleanActivityRecord",            110, wizCommand_cleanActivityRecord ) 		# 清除活动，运镖参与记录。
ADD_COMMAND( "cleanFeichengwuraoDatas",        120, wizCommand_cleanFeichengwuraoDatas ) 	# 清除非诚勿扰活动数据
ADD_COMMAND( "makeFeichengwuraoResult",        120, wizCommand_makeFeichengwuraoResult ) 	# 产生非诚勿扰测试结果
ADD_COMMAND( "addAFETime",                         120, wizCommand_addAFETime )	# 增加自动战斗充值时间
ADD_COMMAND( "addAFTime",                         120, wizCommand_addAFTime )	# 增加自动战斗赠送时间
ADD_COMMAND( "openTongFete",                   120, wizCommand_openTongFete )	# 开启帮会祭祀
ADD_COMMAND( "addTongFete",                    120, wizCommand_addTongFete )	# 设置帮会祭祀进度，大于200则成功完成祭祀活动
ADD_COMMAND( "testCmd",         	      120, wizCommand_testCmd )	# 测试命令
ADD_COMMAND( "setGodWeapon",               120, wizCommand_setGodWeapon )	# 把某武器设为神器 by 姜毅
ADD_COMMAND( "spell",               110, wizCommand_spell )	# 根据技能ID施放技能 by 姜毅
ADD_COMMAND( "remove_all_skill",               120, wizCommand_remove_all_skill )			# 删除目标所有已学技能
ADD_COMMAND( "set_goodness_value",             120, wizCommand_set_goodness_value )         # 设置善恶值
ADD_COMMAND( "ican_fly",             110, wizCommand_i_can_fly )         # 设置角色为飞行状态 by 姜毅
ADD_COMMAND( "let_me_down",                    110, wizCommand_let_me_down )
ADD_COMMAND( "add_prestige",                   120, wizCommand_add_prestige )               # 增加声望
ADD_COMMAND( "reset_prestige",                 120, wizCommand_reset_prestige )             # 重置声望
ADD_COMMAND( "refreshTSCquest",                80, wizCommand_refresh_TSCquest )            # 强制刷新本服务器的帮会副本任务
ADD_COMMAND( "set_potential_map",   80, wizCommand_set_potential_map )           			# 强制潜能副本只进入设定好的副本
ADD_COMMAND( "change_magic_avatar",   80, wizCommand_change_magic_avatar )           			# 改变当前变身的类型
ADD_COMMAND( "set_onlineTime",                 110, wizCommand_set_onlineTime )				# 设置玩家在线时间
ADD_COMMAND( "set_lastweekTime",               110, wizCommand_set_lastweekTime )			# 设置玩家上周在线时间
ADD_COMMAND( "set_signUpTime",               110, wizCommand_set_signUpTime )				# 调用设置帮会竞技剩余报名时间
ADD_COMMAND( "set_tongCompetitionScore",      110, wizCommand_set_tongCompetitionScore )              # [targetID] amount
ADD_COMMAND( "updateAI",                  110, wizCommand_updateAI )              # 更新AI
ADD_COMMAND( "updateSkill",                  110, wizCommand_updateSkill )              # 更新技能
ADD_COMMAND( "updateItem",                  110, wizCommand_updateItem )               # 更新物品
ADD_COMMAND( "upgradeSkill",                110, wizCommand_upgradeSkill )             # 升级技能
ADD_COMMAND( "viewerEnter",                110, wizCommand_viewerEnter )             # 以观察者模式进入指定副本
ADD_COMMAND( "set_global_data",            120, wizCommand_set_global_data )             # 设置全局变量
ADD_COMMAND( "set_fhlt_join",				   110, wizCommand_set_fhlt_join )     		# 设置对应城市的帮会夺城战复赛可参加帮会
ADD_COMMAND( "del_fhlt_join",				   110, wizCommand_del_fhlt_join )     		# 清空对应城市的帮会夺城战复赛可参加帮会
ADD_COMMAND( "switchFengQi",				   110, wizCommand_switchFengQi )
ADD_COMMAND( "set_jiyuan",				 		110, wizCommand_set_jiyuan )			# 增加机缘值
ADD_COMMAND( "set_ZDScore",				 		110, wizCommand_set_ZDScore )			# 增加证道积分
ADD_COMMAND( "add_daofa",				 		110, wizCommand_add_daofa )				# 添加道法
ADD_COMMAND( "open_campActivity",				110, wizCommand_open_campActivity)		# 开启特定地图特定类型的阵营活动
ADD_COMMAND( "set_bovineDevil_map",				   110, wizCommand_set_bovineDevil_map )     		# 清空对应城市的帮会夺城战复赛可参加帮会
ADD_COMMAND( "set_spaceDoorOpenTime", 					110, wizCommand_set_spaceDoor )				# 设置传送门开启时间
ADD_COMMAND( "set_liuwangmu_floortimelimit",						110, wizCommand_set_liuwangmu_floortimelimit ) 	# 测试六王墓,设置每层开放时间间隔
ADD_COMMAND( "set_liuwangmu_openfloor",								110, wizCommand_set_liuwangmu_openfloor )       # 测试六王墓开放到第几层
ADD_COMMAND( "testDanceActivity" , 									110, wizCommand_test_danceActivity )	#测试劲舞时刻
ADD_COMMAND( "moveto",							120, wizCommand_moveto)					# 走到某个点


if Language.LANG == Language.LANG_GBK:
	ADD_COMMAND( "goto",                       70,  wizCommand_goto )                       # spaceKey position [direction]
	ADD_COMMAND( "gotoline",                   70,  wizCommand_gotoline )
	ADD_COMMAND( "gotoPosition",               70,  wizCommand_gotoPosition )				# 飞到同地图任意位置
	ADD_COMMAND( "cometo",                     40,  wizCommand_cometo )                     # 飞过去
	ADD_COMMAND( "set_speed",                  110, wizCommand_set_speed )                  # [targetID] value
	ADD_COMMAND( "broadcast",                  50,  wizCommand_broadcast )                  # 系统广播( hyw--09.03.16 )
	ADD_COMMAND( "activity_control",           80,  wizcommand_activity_control )           # 打开/关闭 活动
	ADD_COMMAND( "kick",                       50,  wizCommand_kick )                       # 踢人
	ADD_COMMAND( "catch",                      50,  wizCommand_catch )                      # 抓过来
	ADD_COMMAND( "query_player_amount",        80,  wizCommand_query_player_amount )        # 查询在线人数
	ADD_COMMAND( "block_account",              50,  wizCommand_block_account )              # 封锁帐号
	ADD_COMMAND( "unBlock_account",            60,  wizCommand_unBlock_account )            # 解除封锁
else:    # for LANG_BIG5
	ADD_COMMAND( "goto",                       35,  wizCommand_goto )                       # spaceKey position [direction]
	ADD_COMMAND( "gotoline",                   35,  wizCommand_gotoline )
	ADD_COMMAND( "gotoPosition",               35,  wizCommand_gotoPosition )				# 飞到同地图任意位置
	ADD_COMMAND( "cometo",                     35,  wizCommand_cometo )                     # 飞过去
	ADD_COMMAND( "set_speed",                  35,  wizCommand_set_speed )                  # [targetID] value
	ADD_COMMAND( "broadcast",                  35,  wizCommand_broadcast )                  # 系统广播( hyw--09.03.16 )
	ADD_COMMAND( "activity_control",           35,  wizcommand_activity_control )           # 打开/关闭 活动
	ADD_COMMAND( "kick",                       35,  wizCommand_kick )                       # 踢人
	ADD_COMMAND( "catch",                      35,  wizCommand_catch )                      # 抓过来
	ADD_COMMAND( "query_player_amount",        35,  wizCommand_query_player_amount )        # 查询在线人数
	ADD_COMMAND( "block_account",              35,  wizCommand_block_account )              # 封锁帐号
	ADD_COMMAND( "unBlock_account",            35,  wizCommand_unBlock_account )            # 解除封锁

# end of ADD_COMMAND //////////////////////////////////////////////////////////////////////////////////////////





activity_dict = { cschannel_msgs.ACTIVITY_SAI_MA	: ("RacehorseManager","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_BING_LIN_CHENG_XIA  : ("MonsterActivityManager","onStart", "onEnd" ),
				cschannel_msgs.KE_JU_KE_JU_XIANG_SHI  : ("ImperialExaminationsMgr", "onXiangshiStart", "onXiangshiEnd" ),
				cschannel_msgs.KE_JU_KE_JU_HUI_SHI  : ("ImperialExaminationsMgr", "onHuishiStart", "onHuishiEnd" ),
				cschannel_msgs.KE_JU_KE_JU_DIAN_SHI  : ("ImperialExaminationsMgr", "onDianshiStart", "onDianshiEnd" ),
				cschannel_msgs.TIAN_GUAN_MONSTER_DEF_1	: ("TianguanMgr", "onStart", "onEnd" ),
				cschannel_msgs.ACTIVITY_QIAN_NENG_LUAN_DOU  : ("PotentialMeleeMgr", "onStart", "onEnd" ),
				cschannel_msgs.ACTIVITY_JING_YAN_LUAN_DOU  : ("ExpMeleeMgr", "onStart", "onEnd" ),
				cschannel_msgs.ACTIVITY_SHUIJING  : ("ShuijingManager", "onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_HEI_SHI_SHANG_REN	: ("DarkTraderMgr", "onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_JIA_ZU_LEI_TAI	: ("FamilyManager", "onFamilyAbattoirWarSignUpStart", "onFamilyAbattoirWarSignUpEnd" ),
				cschannel_msgs.WIZCOMMAND_GUO_YUN_HUO_DONG	: ("DartManager", "onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_JIA_ZU_ZHAN_ZHENG_BAO_MING	: ("FamilyManager", "onFamilyWarSignUpStart", "onFamilyWarSignUpEnd"),
				cschannel_msgs.ACTIVITY_WU_DAO_DA_HUI	: ("WuDaoMgr", "onStartNotice", "onEndNotice" ),
				cschannel_msgs.WIZCOMMAND_BANG_HUI_CHENG_SHI_ZHAN_SIGN_UP: ("TongManager", "onTongCityWarSignUpStart", "onTongCityWarSignUpEnd" ),
				cschannel_msgs.TONGCITYWAR_BANG_HUI_CHENG_SHI_ZHAN_PRE: ("TongManager", "onTongCityWarStart", "onTongCityWarEnd" ),
				cschannel_msgs.TONGCITYWAR_BANG_HUI_CHENG_SHI_ZHAN_FINAL: ("TongManager", "onTongCityWarFinalStart", "onTongCityWarEnd" ),
				cschannel_msgs.WIZCOMMAND_BANG_HUI_LUE_DUO_ZHAN: ("TongManager", "onTongRobWarManagerStart", "onTongRobWarManagerEnd"),
				cschannel_msgs.WIZCOMMAND_BANG_HUI_LUE_DUO_ZHAN_BAO_MING: ("TongManager", "onTongRobWarManagerSignUpStart", "onTongRobWarManagerSignUpEnd"),
				cschannel_msgs.WIZCOMMAND_TIAN_JIANG_BAO_HE	: ("LuckyBoxActivityMgr", "onStartLuckyBox", "onEndLuckyBox" ),
				cschannel_msgs.WIZCOMMAND_MAT	: ( "LuckyBoxActivityMgr", "onStartMidAut", "onEndMidAut" ),
				cschannel_msgs.WIZCOMMAND_BIAN_SHEN_DA_SAI	: ("BCGameMgr", "onStartNotice", "" ),
				cschannel_msgs.WIZCOMMAND_JIA_ZU_ZHAN_ZHENG	: ( "FamilyManager", "onFamilyWarStart", "" ),
				cschannel_msgs.WIZCOMMAND_ZHI_SHI_WEN_DA : ( "QuizGameMgr", "onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_ZU_DUI_JING_SAI : ( "TeamCompetitionMgr", "onSignupStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_XI_TONG_SHUANG_BEI	:( "SysMultExpMgr","onStart2", "onEnd2" ),
				cschannel_msgs.WIZCOMMAND_HUN__RU_QIN : ( "HundunMgr", "onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_BAO_HU_BANG_PAI_ZHUN_BEI	:( "ProtectTong","onStartNotice", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_BAO_HU_BANG_PAI	:( "ProtectTong","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_TIAN_JIANG_QI_SHOU	:( "TianjiangqishouMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_FENG_YIN_BAI_SHE_YAO	:( "SealSnakeMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_FENG_YIN_JU_LING_MO	:( "SealJuLingMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_AN_YING_ZHI_MENG	:( "ToxinFrogMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_NIU_MO_WANG_HUO_DONG	:( "BovineDevilMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_DU_DU_ZHU	:( "DuDuZhuMgr","onStart", "onEnd" ),
				cschannel_msgs.YA_YU_VOICE6	:( "YayuMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_DUO_LUO_LIE_REN	:( "DuoLuoHunterMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_FENG_KUANG_JI_SHI	:( "CrazyJiShiMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_HAN_DI_DA_JIANG	:( "HanDiDaJiangMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_XIAO_TIAN_DA_JIANG	:( "XiaoTianDaJiangMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_GE_REN_JING_JI	:( "RoleCompetitionMgr","onGMStartNotice", "onEndNotice" ),
				cschannel_msgs.WIZCOMMAND_BANG_HUI_JING_JI	:( "TongCompetitionMgr","onStartNotice", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_GUAI_WU_GONG_CHENG	:( "MonsterAttackMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_FEI_CHENG_WU_RAO	:( "FeichengwuraoMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_TANABATA_QUIZ	:( "TanabataQuizMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_TEAM_COLLECT	:("CollectPointManager","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_FRUITTREE	:("FruitMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_PROTECT_TONG_MID_AUTUMN_READY	:( "ProtectTong","onStartNoticeMidAutumn", "onEndMidAutumn" ),
				cschannel_msgs.WIZCOMMAND_PROTECT_TONG_MID_AUTUMN	:( "ProtectTong","onStartMidAutumn", "onEndMidAutumn" ),
				cschannel_msgs.MID_AUTUMIN_RABBIT_RUN	:( "ActivityBroadcastMgr","onMidAutumnRabbitRunStart", "onMidAutumnRabbitRunEnd" ),
				cschannel_msgs.MID_AUTUMIN_TONG_QUEST	:( "ActivityBroadcastMgr","onTongAutummQuestStart", "onTongAutummQuestEnd" ),
				cschannel_msgs.MID_AUTUMIN_KILL_MOON_CAKE	:( "ActivityBroadcastMgr","onTongAutummMonsterStart", "onTongAutummMonsterEnd" ),
				cschannel_msgs.CHRISMAS_RACE_HORSE	:( "RacehorseManager","onChristmasRaceHorse_Start", "onChristmasRaceHorse_End" ),
				cschannel_msgs.CHRISMAS_SPAWN	:( "ActivityBroadcastMgr", "xmanStartCB", "xmanEndCB" ),
				cschannel_msgs.WIZCOMMAND_BANG_HUI_LEI_TAI	:( "TongManager", "onTongAbattoirWarStartNotice", "onInputEndGM" ),
				cschannel_msgs.WIZCOMMAND_YEAR_MONSTER	:("ActivityBroadcastMgr","yearMonsterStartCB","yearMonsterEndCB"),
				cschannel_msgs.WIZCOMMAND_HAPPINESS_ROSE	:("ActivityBroadcastMgr","minAutStartCB","minAutEndCB"),
				cschannel_msgs.ACTIVITY_TEAM_CHALLENGE		:("TeamChallengeMgr","onStart","onEnd"),
				cschannel_msgs.WIZCOMMAND_YE_ZHAN_FENG_QI		:("YeZhanFengQiMgr","onStart","onEnd"),
				cschannel_msgs.WIZCOMMAND_TONG_TURN_WAR		:("TongManager","onSignUpStart","allWarOver"),
				cschannel_msgs.WIZCOMMAND_TONG_FENG_HUO_LIAN_TIAN_NOTIFY: ("TongManager", "onTongFengHuoLianTianNoticeStart", "onTongFengHuoLianTianNoticeEnd" ),
				cschannel_msgs.WIZCOMMAND_TONG_FENG_HUO_LIAN_TIAN: ("TongManager", "onTongFengHuoLianTianStart", "onTongFengHuoLianTianEnd" ),
				cschannel_msgs.WIZCOMMAND_TONG_FENG_HUO_LIAN_TIAN_ALL_OVER: ("TongManager", "", "onTongFengHuoLianTianAllOver" ),
				cschannel_msgs.WIZCOMMAND_CAMP_ACTIVITY : ("CampMgr", "onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_TAOISM_AND_DEMON_BATTLE_ACTIVITY: ("TaoismAndDemonBattleMgr", "onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_LIU_WANG_MU_ACTIVITY:("LiuWangMuMgr", "onStart", "onEnd"),
				cschannel_msgs.WIZCOMMAND_AO_ZHAN_QUN_XIONG:("AoZhanQunXiongMgr", "onStart", "onEnd"),
				cschannel_msgs.WIZCOMMAND_AO_ZHAN_QUN_XIONG_SIGN:("AoZhanQunXiongMgr", "startSignUp", "endSignUp"),
				cschannel_msgs.WIZCOMMAND_JUE_DI_FAN_JI	:( "JueDiFanJiMgr","onStart", "onEnd" ),
				cschannel_msgs.WIZCOMMAND_CAMP_TURN_WAR	:( "CampMgr","turnWar_onSignUpStart", "turnWar_allWarOver" ),
				cschannel_msgs.WIZCOMMAND_CAMP_FENG_HUO_NOTIFY: ("CampMgr", "fengHuo_onStartNotify", "fengHuo_onSignUpStart" ),
				cschannel_msgs.WIZCOMMAND_CAMP_FENG_HUO: ("CampMgr", "fengHuo_onStart", "fengHuo_onEnd" ),
				cschannel_msgs.WIZCOMMAND_TONG_CITY_WAR_FINAL : ( "TongManager", "onCityWarFinalStart", "onCityWarFinalEnd"),
				cschannel_msgs.WIZCOMMAND_YI_JIE_ZHAN_CHANG  : ("YiJieZhanChangMgr", "onStart", "onEnd" ),
				}

"""
智力问答

系统双倍经验
"""

activityRecord_dict = {
						cschannel_msgs.ACTIVITY_SAI_MA		:	csdefine.ACTIVITY_SAI_MA,
						cschannel_msgs.TIAN_GUAN_MONSTER_DEF_1	:	csdefine.ACTIVITY_CHUANG_TIAN_GUAN,
						cschannel_msgs.ACTIVITY_SHUIJING	:	csdefine.ACTIVITY_SHUI_JING,
						cschannel_msgs.YA_YU_VOICE6	:	csdefine.ACTIVITY_ZHENG_JIU_YA_YU,
						}


"""
由于set_attr 设置entity的一些属性 例如：HP_Max， 只能设置单一最终值， 但底层会根据公式和其他参考值进行计算得到最终值
那么此时如果中了buff就会导致设置的值会被还原. 这里提供一个属性表， 每个属性都对应一个接口， 这个接口可以完成一些相关计算获得最终值。
"""
special_attr_dict = {
						"strength_extra"					: "calcDynamicProperties",
						"dexterity_extra"					: "calcDynamicProperties",
						"intellect_extra"					: "calcDynamicProperties",
						"corporeity_extra"					: "calcDynamicProperties",
						"HP_regen_extra"					: "calcHPCureSpeed",
						"MP_regen_extra"					: "calcMPCureSpeed",
						"magic_damage_extra"				: "calcMagicDamage",
						"damage_min_extra"					: "calcDamageMin",
						"damage_max_extra"					: "calcDamageMax",
						"double_hit_probability_extra"		: "calcDoubleHitProbability",
						"magic_double_hit_probability_extra": "calcMagicDoubleHitProbability",
						"resist_hit_probability_extra"		: "calcResistHitProbability",
						"dodge_probability_extra"			: "calcDodgeProbability",
						"HP_Max_extra"						: "calcHPMax",
						"MP_Max_extra"						: "calcMPMax",
						"armor_extra"						: "calcArmor",
						"magic_armor_extra"					: "calcMagicArmor",
						"move_speed_extra"					: "calcMoveSpeed",
						"hit_speed_extra"					: "calcHitSpeed",
						"range_extra"						: "calcRange",
						"damage_derate_extra"				: "calcDamageDerate",
						"magic_damage_derate_extra"			: "calcMagicDamageDerate",
						"damage_derate_ratio_extra"			: "calcDamageDerateRatio",
						"magic_damage_derate_ratio_extra"	: "calcMagicDamageDerateRatio",
						"hitProbability_extra"				: "calcHitProbability",
						"magic_hitProbability_extra"		: "calcMagicHitProbability",
						"resist_giddy_probability_extra"	: "calcResistGiddyProbability",
						"resist_fix_probability_extra"		: "calcResistFixProbability",
						"resist_chenmo_probability_extra"	: "calcResistChenmoProbability",
						"resist_sleep_probability_extra"	: "calcResistSleepProbability",
						"double_hit_multiple_extra"			: "calcDoubleHitMultiple",
						"magic_double_hit_multiple_extra"	: "calcMagicDoubleHitMultiple",
						"resist_hit_derate_extra"			: "calcResistHitDerate",
						"elem_huo_damage_extra"				: "calcElemHuoDamage",
						"elem_xuan_damage_extra"			: "calcElemXuanDamage",
						"elem_lei_damage_extra"				: "calcElemLeiDamage",
						"elem_bing_damage_extra"			: "calcElemBingDamage",
						"elem_huo_derate_ratio_extra"		: "calcElemHuoDerateRatio",
						"elem_xuan_derate_ratio_extra"		: "calcElemXuanDerateRatio",
						"elem_lei_derate_ratio_extra"		: "calcElemLeiDerateRatio",
						"elem_bing_derate_ratio_extra"		: "calcElemBingDerateRatio",
					}

def wizCommand( srcEntity, dstEntityID, command, args ):
	"""
	执行一条命令
	@param   srcEntity: 指行使用的人
	@type	srcEntity: Entity
	@param dstEntityID: 目标entityID
	@type  dstEntityID: OBJECT_ID
	@param	 command: 命令字关键字
	@type	  command: STRING
	@param		args: 命令参数表,根据不同命令有不同的格式,各命令自行解释；
	@type		 args: STRING
	"""
	# get dst entity
	if dstEntityID == srcEntity.id:
		dstEntity = srcEntity
	else:
		if not BigWorld.entities.has_key( dstEntityID ):
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_FIND_TARGET, str(( dstEntityID, )) )
			return

		dstEntity = BigWorld.entities[dstEntityID]

		if not dstEntity.isReal():
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TARGET_NOT_IN_YOUR_CELL, "" )
			return

	if not g_wizCommandDict.has_key( command ):
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_NOT_FIND, str(( command, )) )
		return

	grade, cmd = g_wizCommandDict[command]
	if srcEntity.grade < grade:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GRADE_NO_ENOUGH, str(( grade, )) )
		return

	cmd( srcEntity, dstEntity, args )


# wizCommand.py
