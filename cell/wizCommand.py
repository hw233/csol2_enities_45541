# -*- coding: gb18030 -*-
#
# $Id: wizCommand.py,v 1.44 2008-09-01 03:34:29 zhangyuxing Exp $

"""
����ָ��,����ָ��Ӧ������޶ȵı���ʹ��eval()�����Ͳ���,�����Ӱ�ȫ�ԣ����������
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

TREASURE_MAP_ID = 60101005		#�ر�ͼ��ƷID


def wizCommand_set_grade( srcEntity, dstEntity, args ):
	"""
	����Ŀ��entity��Ȩ��,ֻ�����ñ��Լ�Ȩ�޵͵���,�������õ�Ȩ��Ҳֻ�ܱ��Լ��ͣ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺grade
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
	dstEntity.base.update_grade( dstEntity.grade )		#֪ͨbase grade��ֵ���޸� �Ա�baseʹ����ȷ��ֵȥд��־
	try:
		g_logger.gmCommonLog( "set_grade", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )
	return

def wizCommand_query_grade( srcEntity, dstEntity, args ):
	"""
	��ѯĿ��Ȩ��ֵ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺""
	"""
	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_YOUR_NOW_GRADE, str(( dstEntity.grade, )) )

def wizCommand_set_attr( srcEntity, dstEntity, args ):
	"""
	����ĳ�˵�����ֵ��
	ע�⣺��С��ʹ�ô˹���,���п��ܲ������벻���Ĵ���,���п��ܵ��·��������������ݿ������𻵡�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺key value
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

	# �ж��Ƿ����������ԣ� ��Щ������Ҫ�����ض��Ľӿڽ��и���
	if key in special_attr_dict:
		getattr(dstEntity, special_attr_dict[key])()

	try:
		g_logger.gmCommonLog( "set_attr", args, srcEntity.getNameAndID(), dstEntity.getName(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )
	return

def wizCommand_set_attr_full( srcEntity, dstEntity, args ):
	"""
	����Ŀ�������£����������Ŀ���HP��MPΪ���ֵ9,999,999��
	��û��Ŀ�������£����������HP��MPΪ���ֵ9,999,999��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺key value
	"""
	value = 99999999

	if dstEntity.__class__.__name__ in [ "Role", "Monster"] or isinstance( dstEntity, Monster ):
		INFO_MSG( "%s(%i): set %s(%i)'s HP/MP/HP_Max/MP_Max to %s" % (srcEntity.getName(), srcEntity.id, dstEntity.getName(), dstEntity.id, value) )
		if dstEntity != srcEntity:								# �ж�Ŀ���Ƿ�Ϊ������Ϊ�����ݲ�����
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

	# ����Ŀ���Ƿ�Ϊ�����������HP��MP���д���
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
	��ѯĳ�˵�����ֵ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺key
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
	��ѯĳ�˵�persistentMapping�����е�ֵ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺key
	"""
	if len( args ) == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_PERSISTENT_FORMAT, "" )
		return

	v = str( dstEntity.queryStr( args ) )
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str(( v, )) )

def wizCommand_set( srcEntity, dstEntity, args ):
	"""
	����ĳ�˵�persistentMapping�����е�ֵ��
	ע�⣺��С��ʹ�ô˹���,���п��ܲ������벻���Ĵ���,���п��ܵ��·��������������ݿ������𻵡�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺key value
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
	��ѯĳ�˵�tempMapping�����е�ֵ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺key
	"""
	if len( args ) == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_TEMP_FORMAT, "" )
		return
	v = str( dstEntity.queryTempStr( args ) )
	if not v:	v = "None"
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str((v, )) )

def wizCommand_set_temp( srcEntity, dstEntity, args ):
	"""
	����ĳ�˵�tempMapping�����е�ֵ��
	ע�⣺��С��ʹ�ô˹���,���п��ܲ������벻���Ĵ���,���п��ܵ��·��������������ݿ������𻵡�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺key value
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
	����һ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺spaceKey px py pz dx dy dz
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
	# ���ӽ�����֧��
	srcEntity.setTemp( "gotoPrison", True )
	srcEntity.gotoSpace( cmds[0], position, direction )
	try:
		g_logger.gmCommonLog( "goto", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_change_magic_avatar( srcEntity, dstEntity, args ):
	avatarTypes = ["chiyou", "huangdi", "houyi", "nuwo"]
	# �жϵ�ǰ�Ƿ��Ǳ���״̬
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
	����һ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺spaceKey �ߺ��� px py pz
	"""
	cmds = args.split()
	cmdLen = len( cmds )

	lineNumber = int(cmds[1])
	position = ( float(cmds[2]), float(cmds[3]), float(cmds[4]) )

	if cmdLen == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTOLINE_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTOLINE_FORMAT_2, "" )
		return

	# ���ӽ�����֧��
	srcEntity.setTemp( "gotoPrison", True )
	srcEntity.gotoSpaceLineNumber( cmds[0], lineNumber, position, ( 0, 0, 0 ) )

	try:
		g_logger.gmCommonLog( "goto", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_clone( srcEntity, dstEntity, args ):
	"""
	��entity��ǰλ�ô���һ��npc entity
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺npcKey �ȼ���level
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
	�ڵ�ǰλ����һ����Ʒ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺itemKey amount
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
	����Ʒ��������һ����Ʒ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺itemKey amount
	"""
	cmds = args.split()
	if len( cmds ) < 1:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ADD_ITEM_FORMAT, "" )
		return

	if dstEntity.__class__.__name__ != "Role":
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_CANNOT_TO_NOT_ROLE, "" )
		return

	if dstEntity.getNormalKitbagFreeOrderCount() < 1: # �����ռ䲻��
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
	#���������������
	if item.isEquip():
		item.fixedCreateRandomEffect( item.getQuality(),dstEntity ,False )

	if not dstEntity.addItemAndNotify_( item, csdefine.ADD_ITEM_GMCOMMAND ): # ������Ʒ��ʧ���򷵻�
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
	����Ʒ��������һ��ָ������ı���
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
	����Ʒ��������һ������ָ��Ʒ��,ǰ׺,������װ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺itemKey quality prefix slot intensifyLevel
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
	quality = 1  		# Ʒ�ʣ�1-5��
	slot = 0	 		# ���ף�0-3��
	intensifyLevel = 0  # ǿ���ȼ���0-9��

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
	# ����GMָ��װ��ǿ������Ӧ�ȼ���Χ�����鼰��Ч����Ӧ �Ǹ�����ĵȼ���Χ�����߰��� by����
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
	item.fixedCreateRandomEffect( item.getQuality(),dstEntity ,False )  # �������
	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND )
	INFO_MSG( "%s(%i): add item %s amount %i" % (srcEntity.getName(), srcEntity.id, itemKey, amount) )
	try:
		g_logger.gmCommonLog( "add_equip", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_equip_ten( srcEntity, dstEntity, args ):
	"""
	����Ʒ��������һ������ָ��Ʒ��,ǰ׺,��������Ҫ�ȼ�ȡ��ʮ��װ�� modified by ����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺itemKey quality prefix slot intensifyLevel
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
	# ����GMָ��װ��ǿ������Ӧ�ȼ���Χ�����鼰��Ч����Ӧ �Ǹ�����ĵȼ���Χ�����߰��� by����
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
	item.fixedCreateRandomEffect( item.getQuality(),dstEntity ,False )  # �������
	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND )
	INFO_MSG( "%s(%i): add item %s amount %i" % (srcEntity.getName(), srcEntity.id, itemKey, amount) )
	try:
		g_logger.gmCommonLog( "add_equip_t", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_add_skill( srcEntity, dstEntity, args ):
	"""
	��ĳ�˻��������һ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺skillID
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
	ɾ��ĳ�˻�����һ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺skillID
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
	��ĳ�����õȼ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	����ĳ�˵�������Ӫ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	����ĳ��Ϊ�����˻�δ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	��ĳ�����õȼ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ANTI_FORMAT_1, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_ANTI_FORMAT_2, "" )
		return

	BigWorld.globalData["AntiIndulgenceOpen"] = value
	INFO_MSG( "%s(%i): ����ǰ��Ϸ�ķ�����ϵͳ��������Ϊ %i" % ( srcEntity.getName(), srcEntity.id, value) )
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
	��ĳ�����ý�Ǯ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	��ĳ�����þ���
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	��ĳ������Ǳ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	��ĳ�������ƶ��ٶ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
			g_logger.gmCommonLog( "set_speed", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade ) #���
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
	else:
		try:
			g_logger.gmCommonLog( "set_speed", args, srcEntity.getNameAndID(), None, srcEntity.grade ) #�����
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_model( srcEntity, dstEntity, args ):
	"""
	��ĳ������ģ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	��ĳ����������ģ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	��ĳ����������ģ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	��ĳ����������ģ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	��ĳ����������ģ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	��ĳ�����ÿ���ģ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	��ĳ������Ь��ģ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	����Ŀ��entity��ģ��͸����

	MODEL_VISIBLE_TYPE_FALSE		= 0		# ģ�Ͳ���ʾ
	MODEL_VISIBLE_TYPE_TRUE			= 1		# ģ����ʾ
	MODEL_VISIBLE_TYPE_FBUTBILL	 	= 2		# ģ�Ͳ���ʾ����ʾ������
	MODEL_VISIBLE_TYPE_SNEAK	 	= 3		# ģ�Ͱ�͸����ʾ
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
	����tong���
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
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
	���ü������ ���ܻ�ܾ��������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺modelNum
	"""
	srcEntity.tong_quit( srcEntity.id )
	try:
		g_logger.gmCommonLog( "tong_quit", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_specialShop_update( srcEntity, dstEntity, args ):
	"""
	���µ����̳�����
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
	�ݻ�ָ��NPC
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
	��ʵ�����ָ��������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,����ID
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
	����/���ʵ������ĳ���������ɱ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,args[0]Ϊ����ID,args[1]Ϊ���û���������Ŀ��Ʊ��
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
	if flag == "r" and questID != 0:				# ���quest����ɱ��
		questData = srcEntity.questsTable[questID]
		for task in questData.getTasks().itervalues():
			task.val1 = 0
			srcEntity.client.onTaskStateUpdate( questID, task )
		try:
			g_logger.gmCommonLog( "set_quest_flag", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return
	elif flag == "r" and questID == 0:			  # ��������������ɱ��
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
	elif flag == "a" and questID != 0:			  # ��quest���һ����ɱ��
		questData = srcEntity.questsTable[questID]
		for task in questData.getTasks().itervalues():
			task.val1 = task.val2
			srcEntity.client.onTaskStateUpdate( questID, task )
		try:
			g_logger.gmCommonLog( "set_quest_flag", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return
	elif flag == "a" and questID == 0:			  # û��questID���޷���ӱ��
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
	�����ҵ�����������־
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,����ID
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
	���Ӱ��Ľ�Ǯ
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
	���Ӱ������
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
	���Ӱ���������
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
	���Ӱ��ȼ�
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
	���Ͱ��ȼ�
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
	ȡ������ɢָ��
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
	���ð���Ծ��
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
	��/�ر� һ���
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
		#֪ʶ�ʴ����⴦��//
		if tempInfo[0] == "QuizGameMgr":
			if BigWorld.globalData.has_key( "QuizGame_start" ) and BigWorld.globalData[ "QuizGame_start" ] == True:
				srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_ACTIVITY_ALREADY_OPEN, "" )
				return
		getattr( BigWorld.globalData[tempInfo[0]], tempInfo[1] )()
		INFO_MSG( "%s(%i): ���õ��ô򿪻��ָ��%s" % ( srcEntity.getName(), srcEntity.id, tempInfo[0]) )

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
	ϵͳ�㲥��Ϣ
	hyw--2009.03.16
	"""
	msg = args.strip()
	if msg == "" :
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_BROADCAST_FORMAT, "" )
	else :
		srcEntity.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, [] )

def wizCommand_lock_speach( srcEntity, dstEntityID, args ) :
	"""
	����
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
	�������
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
	��ĳ������Ԫ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	��ĳ������Ԫ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	��ĳ������Ԫ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���Ӹ���
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ó�������ֵ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ó�������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ó�����ֶ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ﷱֳ���
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ó���ֿ�ʣ��ʱ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ó���ɳ���
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���̽�ɢ���
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	������¡�ھ�����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ò�ƽ�ھ�����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ӹ�ѫֵ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	����PKֵ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ָ���ȼ��Ĳر�ͼ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	���ӳƺ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺�ƺ���
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
	����ƺ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺�ƺ���
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
	�������
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	��Ϣ��ѯ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	BigWorld.globalData['GMMgr'].query_Info( srcEntity.base, args, {} )



def wizCommand_query_Pet_Info( srcEntity, dstEntity, args ):
	"""
	��Ϣ��ѯ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	BigWorld.globalData['GMMgr'].query_Pet_Info( srcEntity.base, dstEntity.base, args )



def wizCommand_catch( srcEntity, dstEntity, args ):
	"""
	ץ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	���������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	# ���ӽ�����֧��
	srcEntity.setTemp( "gotoPrison", True )
	BigWorld.globalData['GMMgr'].cometo( srcEntity.base, args, {} )
	try:
		g_logger.gmCommonLog( "cometo", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_kick( srcEntity, dstEntity, args ):
	"""
	����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	BigWorld.globalData['GMMgr'].kick( srcEntity.base, args, {} )
	try:
		g_logger.gmCommonLog( "kick", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_query_player_amount( srcEntity, dstEntity, args ):
	"""
	������ѯ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	BigWorld.globalData['GMMgr'].queryPlayerAmount( srcEntity.base, args, {} )


def wizCommand_block_account( srcEntity, dstEntity, args ):
	"""
	�����ʺ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	����ʺ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	�����ʺ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	return

def wizCommand_query_players_name( srcEntity, dstEntity, args ):
	"""
	�����ʺ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	BigWorld.globalData['GMMgr'].queryPlayersName( srcEntity.base, args, {} )


def wizCommand_set_respawn_rate( srcEntity, dstEntity, args ):
	"""
	����ˢ���ٶ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	"""
	BigWorld.globalData['GMMgr'].setRespawnRate( srcEntity.base, args, {} )
	try:
		g_logger.gmCommonLog( "set_respawn_rate", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_loginAttemper( srcEntity, dstEntity, args ):
	"""
	���õ�¼�Ŷӵ���״̬

	@param state : -1,��¼�����Ŷӹرգ�0���������κε�¼��>0������ͬʱ��¼��������
	"""
	try:
		state = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LOGINATTEMPER_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_STATE_MUST_BE_INT, "" )
		return
	BigWorld.globalData["loginAttemper_count_limit"] = state
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_LOGINATTEMPER_SUCCESS, str(( state, )) )

	# ����״̬���ģ���������
	for key, value in BigWorld.globalData.items():
		if isinstance( key, str ) and key.startswith( "GBAE" ):
			value.loginAttemperTrigger()

	try:
		g_logger.gmCommonLog( "set_loginAttemper", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_baseAppPlayerLimit( srcEntity, dstEntity, args ):
	"""
	����baseApp�����������
	"""
	try:
		state = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_BASEAPPPLAYERLIMIT_FORMAT, "" )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_STATE_MUST_BE_INT, "" )
		return
	BigWorld.globalData["baseApp_player_count_limit"] = state
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SET_BASEAPPPLAYERLIMIT_SUCCESS, str(( state, )) )

	# baseApp����������޸��ģ���������
	for key, value in BigWorld.globalData.items():
		if isinstance( key, str ) and key.startswith( "GBAE" ):
			value.loginAttemperTrigger()

	try:
		g_logger.gmCommonLog( "set_baseAppPlayerLimit", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_waitQueue( srcEntity, dstEntity, args ):
	"""
	���õ�¼�����ŶӶ�������
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
	���û���ʯ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
		ERROR_MSG( "����Ʒ���ǻ���ʯ���鿴�Ƿ����ʯװ���ѻ�λ�á�" )
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
	���ð�ṱ�׶�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	���������;�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
		ERROR_MSG( "����Ʒ���Ƿ������鿴�Ƿ񷨱�װ���ѻ�λ�á�" )
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
	������������;�����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
		ERROR_MSG( "����Ʒ���Ƿ������鿴�Ƿ񷨱�װ���ѻ�λ�á�" )
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
	����������ǰ�;ö�����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	���������ȼ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	�����������ܵȼ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺level
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
	�����Ϣ��ѯ
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	��ѯentity����cellapp��Python���Զ˿�
	"""
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_QUERY_CELLSERVERPORT_FORMAT, str(( BigWorld.getWatcher("nub/address").split(":")[0], ":", BigWorld.getWatcher("pythonServerPort") )) )


def wizCommand_cleanBags( srcEntity, dstEntity, args ):
	"""
	���������(װ��������)
	"""
	for item in srcEntity.itemsBag.getDatas():
		if item.getKitID() != csdefine.KB_EQUIP_ID:
			srcEntity.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_COMMAND_CLEANBAGS )

def wizCommand_getTCRItem( srcEntity, dstEntity, args ):
	"""
	�����Ӿ�����Ʒ
	"""
	g_rewardMgr.rewards( srcEntity, csdefine.REWARD_TEAMCOMPETITION_ITEMS )

def wizCommand_shutdown(  srcEntity, dstEntity, args ):
	"""
	�رշ�����
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
	��������۲������
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	��������۲������
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	����ǰ�����������õȼ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺vehicleLevel
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
	����ǰ�����������óɳ���
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺vehicleLevel
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
	����ǰ�����������þ���
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺vehicleLevel
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
	����ǰ�����������ü��ܵ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺vehicleLevel
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
	����ǰ����������������ʱ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺vehicleLevel
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
	����ǰ�����������ӱ�ʳ��
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺vehicleLevel
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
	����webservice��ƷID�б�
	TRUNCATE TABLE custom_presents
	ʹ�÷�ʽ: /update_presentIds �޲���
	"""
	reload(config.server.WebServicePresentIDs)
	def mysqlCallBack( firstStep, srcEntity, result, rows, errstr ):
		"""
		���ݿ�����ص�
		@type	firstStep : bool
		@param	firstStep : ������������һ�����ݿ������еĻص�
		@type	srcEntity : entity
		@param	srcEntity : ʹ��GM����Ľ�ɫ
		"""
		if errstr:
			# ���ɱ�����Ĵ���
			ERROR_MSG( "update custom_presents table fault! %s" % errstr  )
			return
		if firstStep:
			sql = "INSERT INTO custom_presents(present_id) VALUES"
			valuseDes = ""
			for key in config.server.WebServicePresentIDs.Datas:
				valuseDes += "('%s')," % (key )
			sql += valuseDes[:-1]								# ���ﵽ-1����Ϊ������һ�����š�
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
	�����������buff
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����
	"""
	srcEntity.clearBuff( [0] )

def wizCommand_add_dance_point( srcEntity, dstEntity, args ):
	"""
	����������� by����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	if dstEntity.dancePoint > Const.JING_WU_SHI_KE_MAX_POINT:		# �����ɫ�������û�дﵽ����ۻ���
		dstEntity.dancePoint = Const.JING_WU_SHI_KE_MAX_POINT
	dstEntity.dancePointDailyRecord.incrDegree()
	dstEntity.statusMessage( csstatus.JING_WU_SHI_KE_GET_POINT )

	try:
		g_logger.gmCommonLog( "add_dance_point", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_item_life_time( srcEntity, dstEntity, args ):
	"""
	�����׸���Ʒ�Ĵ��ʱ�� by����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	��ø������͵���ֵ����ʯ by����
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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

	item.set( 'ka_count', item.query( "ka_totalCount", 0 ), dstEntity )	# ���û���ʯΪ��ֵ

	srcEntity.addItem( item, csdefine.ADD_ITEM_GMCOMMAND )

	INFO_MSG( "%s(%i): add item %s amount %i" % (srcEntity.getName(), srcEntity.id, item.id, 1) )
	try:
		g_logger.gmCommonLog( "add_full_stone", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_set_vim( srcEntity, dstEntity, args ):
	"""
	���û���ֵ by ����
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
	��������������� by ����
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
	�ر����۹���
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
	������ƷUID
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
	��ѯ��ƷUID
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
	��ϵͳ���齱��
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
	����Ԫ������ϵͳ
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
	����Ǳ����Ǳ�ܵ� by ����
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
	��������һ�����������Ϊ���� by ����
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
	skillID = equipGodExp.getGodWeaponSkill( level )	# ����������������ָ���ļ����б��н�����������Կ������¼��ݡ�
	weaponItem.setGodWeapon( skillID, dstEntity )
	d_item = ChatObjParser.dumpItem( weaponItem )	# ������Ʒ��Ϣ����
	dstEntity.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", cschannel_msgs.BCT_GOD_WEAPON%( dstEntity.getName(), "${o0}" ), [d_item,] )

def wizCommand_addTeamMember( srcEntity, dstEntity, args ):
	"""
	����1���������������Լ��ٴ����ӵ��Լ��Ķ����У���
	ע��
		��Ҫ�Ƿ����ɫһ�������������븱����һЩ�򵥲��ԡ�
	ʹ�����ָ����Ҫ�Լ��Ƚ������顣
	"""
	if srcEntity.isInTeam():
		srcEntity.teamMembers.append( srcEntity.teamMembers[0] )
	else:
		srcEntity.client.onStatusMessage( csstatus.SPACE_MISS_NOTTEAM, "" )



def wizCommand_addIECollectCount( srcEntity, dstEntity, args ):
	"""
	�ƾٴ�����ȷ���Ρ�

	ͨ�������Ҫ����ɶ�δ�����ȷ�������ò��Լ��ƾ���������Ƿ����

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
	��ѯ����ID
	"""
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str((dstEntity.id, )) )

def wizCommand_checkSeverTime( srcEntity, dstEntity, args ):
	"""
	��ѯ������ʱ��
	"""
	TT = time.localtime()
	result = str( TT[0] ) + "/" + str( TT[1] ) + "/" + str( TT[2] ) + " " + str( TT[3] ) + ":" + str( TT[4] ) + ":" + str( TT[5] )
	srcEntity.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, str((result, )) )


def wizCommand_addWuDaoGuanJunRewardCount( srcEntity, dstEntity, args ):
	"""
	�������ü��ιھ�����

	ͨ�������Ҫ����ɶ�λ��������ھ��������ò��Լ��������ھ��Ľ����Ƿ����

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
	������һ��¼
	�������и���������ڵȼ�¼
	"""
	srcEntity.activityFlags = 0
	srcEntity.questNormalDartRecord.dartCount = 0
	srcEntity.questExpDartRecord.dartCount = 0
	srcEntity.questTongDartRecord.dartCount = 0 # �����1.2��1.1û��srcEntity.questTongDartRecord.dartCount 2011-2-23 12:04 by mushuang
	if srcEntity.tong_dbID > 0: srcEntity.base.clearTongDartRecord() # �����1.2��1.1û�� srcEntity.base.clearTongDartRecord 2011-2-23 12:04 by mushuang
	srcEntity.loopQuestLogs = []
	srcEntity.suanGuaZhanBuDailyRecord.reset()
	srcEntity.roleRecord.clear()
	g_activityRecordMgr.initAllActivitysJoinState( srcEntity )

def wizCommand_cleanFeichengwuraoDatas( srcEntity, dstEntity, args ):
	"""
	����ǳ��������ݼ�¼
	"""
	BigWorld.globalData["FeichengwuraoMgr"].cleanAllDatas()

def wizCommand_makeFeichengwuraoResult( srcEntity, dstEntity, args ):
	"""
	�����ǳ�����ͶƱ���
	"""
	if BigWorld.globalData.has_key( "AS_Feichengwurao" ):
		del BigWorld.globalData[ "AS_Feichengwurao" ]
	BigWorld.globalData["FeichengwuraoMgr"].onHandle_result()

def wizCommand_addAFETime( srcEntity, dstEntity, args ):
	"""
	�����Լ����Զ�ս����Ʒ��ֵ�Ķ���ʱ�� by ����
	"""
	value = 0
	try:
		value = int( args )
	except ValueError, errStr:
		return
	srcEntity.base.autoFightExtraTimeCharge( value )

def wizCommand_addAFTime( srcEntity, dstEntity, args ):
	"""
	�����Լ����Զ�ս����Ʒ��ֵ�Ķ���ʱ�� by ����
	"""
	value = 0
	try:
		value = int( args )
	except ValueError, errStr:
		return
	srcEntity.base.autoFightTimeCharge( value )

def wizCommand_openTongFete( srcEntity, dstEntity, args ):
	"""
	���ð����뿪��
	"""
	BigWorld.globalData[ "TongManager" ].requestFete( srcEntity.tong_dbID, srcEntity.tong_grade, srcEntity.base )

def wizCommand_addTongFete( srcEntity, dstEntity, args ):
	"""
	���ð����뿪��
	"""
	try:
		value = int( args )
	except:
		DEBUG_MSG( "ָ�����( %s )����ȷ��" % str( args ) )
		return
	BigWorld.globalData[ "TongManager" ].addTongFeteValue( srcEntity.tong_dbID, value )

def wizCommand_testCmd( srcEntity, dstEntity, args ):
	"""
	�丸����һ��BOSS AI ���ԡ�
	"""
	cmds = args.split()
	if cmds[0] == "kfb3":
		kuafu.whiteAIs( srcEntity )
	if cmds[0] == "hsml":
		kuafu.darkSkillManli( srcEntity, dstEntity )

def wizCommand_spell( srcEntity, dstEntity, args ):
	"""
	���ݼ���IDʩ�ż���
	"""
	try:
		value = int( args )
	except ValueError, errStr:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_SKILLID_MUST_BE_INT, "" )
		return
	srcEntity.spellTarget( value, dstEntity.id )

def wizCommand_remove_all_skill( srcEntity, dstEntity, args ):
	"""
	ɾ��ĳ�˻��������м���
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	�����ƶ�ֵ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	���ý�ɫ�ķ��б�־
	"""
	testSkillID = 922258001

	if srcEntity.hasFlag( csdefine.ROLE_FLAG_FLY ):
		return

	#srcEntity.client.onEnterFlyState() # �����ֶ����ã�buff���Զ�����
	try:
		spell = g_skills[ testSkillID ]
	except:
		ERROR_MSG( "Failed to load test skill!" )
		ERROR_MSG( "ican_fly ignored!" )
		return

	# �ж��Ƿ��в�������˱�־
	if srcEntity.actionSign( csdefine.ACTION_FORBID_VEHICLE ):
		srcEntity.actCounterDec( csdefine.ACTION_FORBID_VEHICLE )		#ȥ�����е���Ϊ���ƣ�ʵ������������Ƶĸ��������
		srcEntity.setTemp( "fobid_cehicle",True )
	spell.receiveLinkBuff( srcEntity, srcEntity )

	try:
		g_logger.gmCommonLog( "i_can_fly", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_let_me_down( srcEntity, dstEntity, args ):
	"""
	ɾ����ɫ�ķ��б�־
	"""
	if not srcEntity.hasFlag( csdefine.ROLE_FLAG_FLY ):
		ERROR_MSG( "Role is not flying, let_me_down ignored!" )
		return

	testBuffID = 92225800101

	srcEntity.removeBuffByID( testBuffID, [ csdefine.BUFF_INTERRUPT_REQUEST_CANCEL ] )
	if srcEntity.queryTemp( "fobid_cehicle",False ):
		srcEntity.actCounterInc( csdefine.ACTION_FORBID_VEHICLE )
		srcEntity.removeTemp( "fobid_cehicle" )

	# srcEntity.client.onLeaveFlyState() # �����ֶ����ã�buff���Զ�����
	try:
		g_logger.gmCommonLog( "let_me_down", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


def wizCommand_add_prestige( srcEntity, dstEntity, args ):
	"""
	������������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	������������
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	ǿ��ˢ�±��������İ�ḱ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	����Ǳ�ܸ�������̶���ͼ
	"""
	srcEntity.setTemp( "gmSetPotentialMap", args )



def wizCommand_set_onlineTime( srcEntity, dstEntity, args ):
	"""
	��ĳ����������ʱ��
	@param srcEntity: Entity;
	@param args: ָ��������ַ������飬amount
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
	��ĳ��������������ʱ��
	@param srcEntity: Entity;
	@param args: ָ��������ַ������飬amount
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
	���ûʣ�౨��ʱ��
	@param srcEntity: Entity;
	@param args: ָ��������ַ������飬amount
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

		INFO_MSG( "%s(%i): ����������Ӿ���ʣ�౨��ʱ���ָ��" % ( srcEntity.getName(), srcEntity.id ) )
		try:
			g_logger.gmCommonLog( "set_signUpTime", args, srcEntity.getNameAndID(), None, srcEntity.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	elif msg[0] == cschannel_msgs.WIZCOMMAND_BANG_HUI_JING_JI:
		BigWorld.globalData["TongCompetitionMgr"].setSignUpTime( value )
		INFO_MSG( "%s(%i): �������ð�Ὰ��ʣ�౨��ʱ���ָ��" % ( srcEntity.getName(), srcEntity.id ) )
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
	���ð�Ὰ������
	@param srcEntity: Entity;
	@param args: ָ��������ַ������飬amount
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
	����AI
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
	���¼���
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
	������Ʒ
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
	��������
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
	# �Թ۲���ģʽ����ָ������
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
	����globalData
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
	����һ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺spaceKey px py pz
	"""
	cmds = args.split()
	cmdLen = len( cmds )

	if cmdLen == 0:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_GOTOLINE_FORMAT_2, "" )
		return
	position = ( float(cmds[0]), float(cmds[1]), float(cmds[2]) )
	# ���ӽ�����֧��
	srcEntity.setTemp( "gotoPrison", True )
	spaceName = srcEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
	srcEntity.gotoSpace( spaceName, position, ( 0, 0, 0 ) )

	try:
		g_logger.gmCommonLog( "goto", args, srcEntity.getNameAndID(), None, srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )

def wizCommand_switchFengQi( srcEntity, dstEntity, args ):
	"""
	�ͻ��˽��������
	@param srcEntity: Entity; ִ��ָ����ˣ�
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
	��ĳ�����û�Եֵ
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	��ĳ������֤������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	����ͨ����������һ������
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
	�����ض���ͼ�ض����͵���Ӫ�
	@param srcEntity: Entity; ִ��ָ����ˣ�
	@param args: ָ�����,�ַ������飺amount
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
		BigWorld.globalData[ "CampMgr" ].onStart()		#��Ϊ���������������Զ���������������������ֵ��GRL
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
	����ţħ������ض���ͼˢ��
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
	���ô����ŵĿ���ʱ��
	�����ο�csol-2042�����ŵ�ʱ�������д
	�� 8:00-10:00
	1|8:00-10:00
	1
	�������Ϊ�գ���ʾ�˴���������ǰ�Ĵ�����һ������Ϊ�����ƴ����ţ��������ɴ���
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
	�ƶ���ĳ��Ŀ��㣬��������ԭ���ǿͻ��˻�����
	�ƶ������㣬���ܻᶯ���ˣ���������������ߵ�
	�������˿����ƶ����������������ڻ�����ʹ��
	"""
	try:
		# λ���Ǹ�����3Ԫ��
		position = tuple([float(i) for i in args.split()][:3])
	except ValueError, err:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MOVE_TO_ARGS_ERROR, str((args, )) )
		return

	DEBUG_MSG("----->>> position is %s, args is %s" % (position, args))

	# ����������
	if len(position) != 3:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_MOVE_TO_ARGS_ERROR, str((args, )) )
		return

	# ��ʼ�ƶ�.
	dstEntity.gotoPosition(position)

	try:
		g_logger.gmCommonLog( "moveto", args, srcEntity.getNameAndID(), dstEntity.getNameAndID(), srcEntity.grade )
	except:
		g_logger.logExceptLog( GET_ERROR_MSG() )


g_wizCommandDict = {}
def ADD_COMMAND( cmd, grade, func ):
	assert cmd not in g_wizCommandDict
	g_wizCommandDict[cmd] = ( grade, func )

# ָ��������,ֵΪ( ʹ��Ȩ��,������� )
# ��ҵ�Ĭ��Ȩ�ޣ�30
# Ӧ������ӪҪ�󣬽�ֹ���л����ҽ�ɫ���������ָ��
# �Ժ����л����Ҵ��������ָ�������Ϊ110���Ϸ����ϴ���
# �ڿ���������Ҫ�õ�����ָ��ģ������Լ��ķ��������ֶ��޸����ָ��Ȩ�ޣ�
# �Ҽ���������ϴ���
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
ADD_COMMAND( "tong_cancelDismiss",             110, wizCommand_tong_cancelDismiss )         # ȡ����ɢ
ADD_COMMAND( "tong_addContribute",             110, wizCommand_set_tong_contribute )        # ���ð�ṱ�׶�
ADD_COMMAND( "tong_addActivityPoint",          110, wizCommand_tong_addActivityPoint )      # ���ð���Ծ��
ADD_COMMAND( "del_city_master",				   110, wizCommand_del_city_master )     		# ɾ������

ADD_COMMAND( "smash",                          80,  wizCommand_destroy_NPC )                # targetID
ADD_COMMAND( "dismiss_tong",                   110, wizCommand_dismiss_tong )               # ���̽�ɢ���

ADD_COMMAND( "accept_quest",                   80,  wizCommand_accept_quest )               # questID
ADD_COMMAND( "set_quest_flag",                 110, wizCommand_set_quest_flag )             # questID
ADD_COMMAND( "set_quest_group",                110, wizCommand_set_quest_group )             # questID
ADD_COMMAND( "remove_completed_quest",         110, wizCommand_remove_completed_quest )     # questID

ADD_COMMAND( "lock_speach",                    50,  wizCommand_lock_speach )                # ���ԣ�hyw--2009.09.16��
ADD_COMMAND( "unlock_speach",                  50,  wizCommand_unlock_speach )              # ���ԣ�hyw--2009.09.16��

ADD_COMMAND( "set_silver",                     110, wizCommand_set_silver )                 # ������Ԫ��
ADD_COMMAND( "set_gold",                       110, wizCommand_set_gold )                   # ���ý�Ԫ��

ADD_COMMAND( "add_pet_calcaneus",              110, wizCommand_add_pet_calcaneus )          # ���ӳ������
ADD_COMMAND( "set_pet_nimbus",                 110, wizCommand_set_pet_nimbus )             # ���ó�������ֵ
ADD_COMMAND( "set_pet_life",                   110, wizCommand_set_pet_life )               # ���ó�������
ADD_COMMAND( "set_pet_joyancy",                110, wizCommand_set_pet_joyancy )            # ���ó�����ֶ�
ADD_COMMAND( "set_pet_propagate_finish",       110, wizCommand_set_pet_propagate_finish )   # ��ɳ��ﷱֳ
ADD_COMMAND( "set_pet_storage_time",           110, wizCommand_set_pet_storage_time )       # ���ó���ֿ�ʣ��ʱ��
ADD_COMMAND( "set_pet_ability",                110, wizCommand_set_pet_ability )            # ���ó���ɳ���

ADD_COMMAND( "set_stone",                      110, wizCommand_set_stone )                  # ���û���ʯ
ADD_COMMAND( "set_fabao_lim_naijiu",           110, wizCommand_set_fabao_lim_naijiu )       # ���÷�����ǰ����;�
ADD_COMMAND( "set_fabao_max_naijiu",           110, wizCommand_set_fabao_max_naijiu )       # ���÷�������;�����
ADD_COMMAND( "set_fabao_naijiu",               110, wizCommand_set_fabao_naijiu )           # ���÷����;�
ADD_COMMAND( "set_fabao_level",                110, wizCommand_set_fabao_level )            # ���÷�������
ADD_COMMAND( "set_fabao_skill_level",          110, wizCommand_set_fabao_skill_level )      # ���÷������ܼ���

ADD_COMMAND( "set_xinglong_prestige",          110, wizCommand_set_xinglong_prestige )      # ������¡�ھ�����
ADD_COMMAND( "set_changping_prestige",         110, wizCommand_set_changping_prestige )     # ���ò�ƽ�ھ�����

ADD_COMMAND( "add_teachCredit",                110, wizCommand_add_teachCredit )            # ���ӹ�ѫֵ
ADD_COMMAND( "set_pk_value",                   110, wizCommand_set_pk_value )               # ����PKֵ

ADD_COMMAND( "add_treasure_map",               110, wizCommand_add_treasure_map )           # ����ָ���ȼ��ر�ͼ��Ʒ

ADD_COMMAND( "add_title",                      110, wizCommand_add_title )                  # ����ָ���ȼ��ر�ͼ��Ʒ
ADD_COMMAND( "remove_title",                   110, wizCommand_remove_title )               # ����ָ���ȼ��ر�ͼ��Ʒ

ADD_COMMAND( "query_Info",                     70,  wizCommand_query_Info )                 # ��ѯ��ɫ��Ϣ
ADD_COMMAND( "block_role",                     40,  wizCommand_block_role )                 # ������ɫ
ADD_COMMAND( "query_players_name",             80,  wizCommand_query_players_name )         # ��ѯ������ҵ�����
ADD_COMMAND( "set_respawn_rate",               40,  wizCommand_set_respawn_rate )           # ����һ������ˢ���ٶ�
ADD_COMMAND( "set_loginAttemper",              110, wizCommand_set_loginAttemper )          # ��¼���ȵ�¼��������
ADD_COMMAND( "set_baseAppPlayerLimit",         110, wizCommand_set_baseAppPlayerLimit )     # ���õ�baseApp����������������
ADD_COMMAND( "set_waitQueue",                  110, wizCommand_set_waitQueue )              # ��¼�����ŶӶ�������
ADD_COMMAND( "clearBuff",                      50,  wizCommand_clearBuff )                  # �������buff
ADD_COMMAND( "query_Pet_Info",                 70,  wizCommand_query_Pet_Info )             # ��ѯ������Ϣ
ADD_COMMAND( "query_Tong_Info",                70,  wizCommand_query_Tong_Info )            # ��ѯ�����Ϣ
ADD_COMMAND( "clean_activity_record",          110, wizCommand_clean_activity_record )      # ���ĳ����ļ�¼
ADD_COMMAND( "query_CellServerPort",           110, wizCommand_query_CellServerPort )       # ��ѯcellapp�������˿�
ADD_COMMAND( "cleanBags",                      110, wizCommand_cleanBags )                  # ��ձ���(װ��������)
ADD_COMMAND( "getTCRItem",                     110, wizCommand_getTCRItem )                 # �����Ӿ�������
ADD_COMMAND( "shutdown",                       40,  wizCommand_shutdown )                   # �رշ�����
ADD_COMMAND( "watch",                          110, wizCommand_watch )                      # �۲���
ADD_COMMAND( "dropBox",                        110, wizCommand_dropBox )                    # ��������

ADD_COMMAND( "set_vehicle_level",              110, wizCommand_set_vehicle_level )          # �������ȼ�
ADD_COMMAND( "set_vehicle_growth",             110, wizCommand_set_vehicle_growth )         # �������ɳ���
ADD_COMMAND( "set_vehicle_skPoint",            110, wizCommand_set_vehicle_skPoint )        # ������輼�ܵ�
ADD_COMMAND( "set_vehicle_deadTime",           110, wizCommand_set_vehicle_deadTime )       # �������ʣ��ʱ��
ADD_COMMAND( "add_vehicle_fulldegree",         110, wizCommand_add_vehicle_fulldegree )     # ������豥ʳ��
ADD_COMMAND( "set_vehicle_exp",        		   110, wizCommand_set_vehicle_exp )      		# ������辭��

ADD_COMMAND( "update_presentIds",              110, wizCommand_update_presentIds )          # ����webservice��ƷID�б�
ADD_COMMAND( "add_dance_point",                110, wizCommand_add_dance_point )            # �����������
ADD_COMMAND( "add_full_stone",                 110, wizCommand_add_full_stone )             # ��ø������͵���ֵ����ʯ
ADD_COMMAND( "set_item_life_time",             110, wizCommand_set_item_life_time )         # �����׸���Ʒ�Ĵ��ʱ��
ADD_COMMAND( "set_antiRobotRate",              110, wizCommand_set_antiRobotRate )          # ���÷������֤��������
ADD_COMMAND( "set_vim",                        110, wizCommand_set_vim )                    # ���û���ֵ by ����
ADD_COMMAND( "set_lvs_sle",                    110, wizCommand_set_lvs_sle )                # ��������������� by ����
ADD_COMMAND( "set_tishouSystem",               110, wizCommand_set_tishouSystem )           # �ر����۹���
ADD_COMMAND( "setItemUID",                     120, wizCommand_setItemUID )                 # ������Ʒ��uid
ADD_COMMAND( "queryItemUID",                   120, wizCommand_queryItemUID )               # ��ѯ��Ʒ��uid
ADD_COMMAND( "sysExpReward",                   120, wizCommand_sysExpReward )               # ��ϵͳ���齱��
ADD_COMMAND( "ybtSwitch",                      120, wizCommand_ybSwitch )                   # ����Ԫ������ϵͳ
ADD_COMMAND( "set_potential_book",             120, wizCommand_setPBook )                   # ����Ǳ����Ǳ�ܵ�
ADD_COMMAND( "addTeamMember",                  120, wizCommand_addTeamMember )              # �����Լ������Ķ�������
ADD_COMMAND( "addIEAnswerRight",               120, wizCommand_addIECollectCount )          # �ƾٿ��Դ�����ȷ��
ADD_COMMAND( "query_id",                       30, wizCommand_query_ID )                    # �鿴����ID��
ADD_COMMAND( "query_serverTime",               110, wizCommand_checkSeverTime )             # �鿴��ǰ������ʱ��
ADD_COMMAND( "addWuDaoGJRC",                   120, wizCommand_addWuDaoGuanJunRewardCount ) # ���������ھ�����������
ADD_COMMAND( "cleanActivityRecord",            110, wizCommand_cleanActivityRecord ) 		# ���������ڲ����¼��
ADD_COMMAND( "cleanFeichengwuraoDatas",        120, wizCommand_cleanFeichengwuraoDatas ) 	# ����ǳ����Ż����
ADD_COMMAND( "makeFeichengwuraoResult",        120, wizCommand_makeFeichengwuraoResult ) 	# �����ǳ����Ų��Խ��
ADD_COMMAND( "addAFETime",                         120, wizCommand_addAFETime )	# �����Զ�ս����ֵʱ��
ADD_COMMAND( "addAFTime",                         120, wizCommand_addAFTime )	# �����Զ�ս������ʱ��
ADD_COMMAND( "openTongFete",                   120, wizCommand_openTongFete )	# ����������
ADD_COMMAND( "addTongFete",                    120, wizCommand_addTongFete )	# ���ð�������ȣ�����200��ɹ���ɼ���
ADD_COMMAND( "testCmd",         	      120, wizCommand_testCmd )	# ��������
ADD_COMMAND( "setGodWeapon",               120, wizCommand_setGodWeapon )	# ��ĳ������Ϊ���� by ����
ADD_COMMAND( "spell",               110, wizCommand_spell )	# ���ݼ���IDʩ�ż��� by ����
ADD_COMMAND( "remove_all_skill",               120, wizCommand_remove_all_skill )			# ɾ��Ŀ��������ѧ����
ADD_COMMAND( "set_goodness_value",             120, wizCommand_set_goodness_value )         # �����ƶ�ֵ
ADD_COMMAND( "ican_fly",             110, wizCommand_i_can_fly )         # ���ý�ɫΪ����״̬ by ����
ADD_COMMAND( "let_me_down",                    110, wizCommand_let_me_down )
ADD_COMMAND( "add_prestige",                   120, wizCommand_add_prestige )               # ��������
ADD_COMMAND( "reset_prestige",                 120, wizCommand_reset_prestige )             # ��������
ADD_COMMAND( "refreshTSCquest",                80, wizCommand_refresh_TSCquest )            # ǿ��ˢ�±��������İ�ḱ������
ADD_COMMAND( "set_potential_map",   80, wizCommand_set_potential_map )           			# ǿ��Ǳ�ܸ���ֻ�����趨�õĸ���
ADD_COMMAND( "change_magic_avatar",   80, wizCommand_change_magic_avatar )           			# �ı䵱ǰ���������
ADD_COMMAND( "set_onlineTime",                 110, wizCommand_set_onlineTime )				# �����������ʱ��
ADD_COMMAND( "set_lastweekTime",               110, wizCommand_set_lastweekTime )			# ���������������ʱ��
ADD_COMMAND( "set_signUpTime",               110, wizCommand_set_signUpTime )				# �������ð�Ὰ��ʣ�౨��ʱ��
ADD_COMMAND( "set_tongCompetitionScore",      110, wizCommand_set_tongCompetitionScore )              # [targetID] amount
ADD_COMMAND( "updateAI",                  110, wizCommand_updateAI )              # ����AI
ADD_COMMAND( "updateSkill",                  110, wizCommand_updateSkill )              # ���¼���
ADD_COMMAND( "updateItem",                  110, wizCommand_updateItem )               # ������Ʒ
ADD_COMMAND( "upgradeSkill",                110, wizCommand_upgradeSkill )             # ��������
ADD_COMMAND( "viewerEnter",                110, wizCommand_viewerEnter )             # �Թ۲���ģʽ����ָ������
ADD_COMMAND( "set_global_data",            120, wizCommand_set_global_data )             # ����ȫ�ֱ���
ADD_COMMAND( "set_fhlt_join",				   110, wizCommand_set_fhlt_join )     		# ���ö�Ӧ���еİ����ս�����ɲμӰ��
ADD_COMMAND( "del_fhlt_join",				   110, wizCommand_del_fhlt_join )     		# ��ն�Ӧ���еİ����ս�����ɲμӰ��
ADD_COMMAND( "switchFengQi",				   110, wizCommand_switchFengQi )
ADD_COMMAND( "set_jiyuan",				 		110, wizCommand_set_jiyuan )			# ���ӻ�Եֵ
ADD_COMMAND( "set_ZDScore",				 		110, wizCommand_set_ZDScore )			# ����֤������
ADD_COMMAND( "add_daofa",				 		110, wizCommand_add_daofa )				# ��ӵ���
ADD_COMMAND( "open_campActivity",				110, wizCommand_open_campActivity)		# �����ض���ͼ�ض����͵���Ӫ�
ADD_COMMAND( "set_bovineDevil_map",				   110, wizCommand_set_bovineDevil_map )     		# ��ն�Ӧ���еİ����ս�����ɲμӰ��
ADD_COMMAND( "set_spaceDoorOpenTime", 					110, wizCommand_set_spaceDoor )				# ���ô����ſ���ʱ��
ADD_COMMAND( "set_liuwangmu_floortimelimit",						110, wizCommand_set_liuwangmu_floortimelimit ) 	# ��������Ĺ,����ÿ�㿪��ʱ����
ADD_COMMAND( "set_liuwangmu_openfloor",								110, wizCommand_set_liuwangmu_openfloor )       # ��������Ĺ���ŵ��ڼ���
ADD_COMMAND( "testDanceActivity" , 									110, wizCommand_test_danceActivity )	#���Ծ���ʱ��
ADD_COMMAND( "moveto",							120, wizCommand_moveto)					# �ߵ�ĳ����


if Language.LANG == Language.LANG_GBK:
	ADD_COMMAND( "goto",                       70,  wizCommand_goto )                       # spaceKey position [direction]
	ADD_COMMAND( "gotoline",                   70,  wizCommand_gotoline )
	ADD_COMMAND( "gotoPosition",               70,  wizCommand_gotoPosition )				# �ɵ�ͬ��ͼ����λ��
	ADD_COMMAND( "cometo",                     40,  wizCommand_cometo )                     # �ɹ�ȥ
	ADD_COMMAND( "set_speed",                  110, wizCommand_set_speed )                  # [targetID] value
	ADD_COMMAND( "broadcast",                  50,  wizCommand_broadcast )                  # ϵͳ�㲥( hyw--09.03.16 )
	ADD_COMMAND( "activity_control",           80,  wizcommand_activity_control )           # ��/�ر� �
	ADD_COMMAND( "kick",                       50,  wizCommand_kick )                       # ����
	ADD_COMMAND( "catch",                      50,  wizCommand_catch )                      # ץ����
	ADD_COMMAND( "query_player_amount",        80,  wizCommand_query_player_amount )        # ��ѯ��������
	ADD_COMMAND( "block_account",              50,  wizCommand_block_account )              # �����ʺ�
	ADD_COMMAND( "unBlock_account",            60,  wizCommand_unBlock_account )            # �������
else:    # for LANG_BIG5
	ADD_COMMAND( "goto",                       35,  wizCommand_goto )                       # spaceKey position [direction]
	ADD_COMMAND( "gotoline",                   35,  wizCommand_gotoline )
	ADD_COMMAND( "gotoPosition",               35,  wizCommand_gotoPosition )				# �ɵ�ͬ��ͼ����λ��
	ADD_COMMAND( "cometo",                     35,  wizCommand_cometo )                     # �ɹ�ȥ
	ADD_COMMAND( "set_speed",                  35,  wizCommand_set_speed )                  # [targetID] value
	ADD_COMMAND( "broadcast",                  35,  wizCommand_broadcast )                  # ϵͳ�㲥( hyw--09.03.16 )
	ADD_COMMAND( "activity_control",           35,  wizcommand_activity_control )           # ��/�ر� �
	ADD_COMMAND( "kick",                       35,  wizCommand_kick )                       # ����
	ADD_COMMAND( "catch",                      35,  wizCommand_catch )                      # ץ����
	ADD_COMMAND( "query_player_amount",        35,  wizCommand_query_player_amount )        # ��ѯ��������
	ADD_COMMAND( "block_account",              35,  wizCommand_block_account )              # �����ʺ�
	ADD_COMMAND( "unBlock_account",            35,  wizCommand_unBlock_account )            # �������

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
�����ʴ�

ϵͳ˫������
"""

activityRecord_dict = {
						cschannel_msgs.ACTIVITY_SAI_MA		:	csdefine.ACTIVITY_SAI_MA,
						cschannel_msgs.TIAN_GUAN_MONSTER_DEF_1	:	csdefine.ACTIVITY_CHUANG_TIAN_GUAN,
						cschannel_msgs.ACTIVITY_SHUIJING	:	csdefine.ACTIVITY_SHUI_JING,
						cschannel_msgs.YA_YU_VOICE6	:	csdefine.ACTIVITY_ZHENG_JIU_YA_YU,
						}


"""
����set_attr ����entity��һЩ���� ���磺HP_Max�� ֻ�����õ�һ����ֵ�� ���ײ����ݹ�ʽ�������ο�ֵ���м���õ�����ֵ
��ô��ʱ�������buff�ͻᵼ�����õ�ֵ�ᱻ��ԭ. �����ṩһ�����Ա� ÿ�����Զ���Ӧһ���ӿڣ� ����ӿڿ������һЩ��ؼ���������ֵ��
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
	ִ��һ������
	@param   srcEntity: ָ��ʹ�õ���
	@type	srcEntity: Entity
	@param dstEntityID: Ŀ��entityID
	@type  dstEntityID: OBJECT_ID
	@param	 command: �����ֹؼ���
	@type	  command: STRING
	@param		args: ���������,���ݲ�ͬ�����в�ͬ�ĸ�ʽ,���������н��ͣ�
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
