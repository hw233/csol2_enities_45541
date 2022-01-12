# -*- coding: utf-8 -*-
import time
import struct
import BigWorld
import csdefine
import csconst
import csstatus
import ItemTypeEnum
import Const
import items
import ItemBagRole
from bwdebug import *
from Function import Functor
from Function import ipToStr
from KitbagBase import KitbagBase
from KitbagsTypeImpl import KitbagsTypeImpl
from random import choice
import funcEquip
import ItemTypeEnum

g_items = items.instance()

class RoleInfo(object):
	def __init__(self, _account, _password, _raceclass, _playerName, _hairNum = 0, _faceNum = 0):
		self.account = _account
		self.password = _password
		self.raceclass = _raceclass
		self.playerName = _playerName
		self.hairNum = _hairNum
		self.faceNum = _faceNum
	
	def createInDB(self):
		INFO_MSG( "Try create account %s." % self.account )
		BigWorld.executeRawDatabaseCommand("insert into tbl_Account set sm_playerName='%s'" % self.account, self._insertAccountCB)

	def _initKitbag(self, entity):
		"""
		"""
		kits = entity.cellData["kitbags"]
		if not kits.has_key( csdefine.KB_EQUIP_ID ):
			INFO_MSG( "init equip kitbag." )
			equip = g_items.createDynamicItem( csdefine.ITEMID_KITBAG_EQUIP )
			kits[csdefine.KB_EQUIP_ID] = equip
	
		if not kits.has_key( csdefine.KB_COMMON_ID ):
			INFO_MSG( "init normal kitbag." )
			kitbag = g_items.createDynamicItem( csdefine.ITEMID_KITBAG_NORMAL )
			kits[csdefine.KB_COMMON_ID] = kitbag
	
	def _initBankBag(self, entity ):
		"""
		"""
		if not entity.bankNameList:
			entity.bankNameList.append( "" )
	
	def _onWriteRoleToDBRollback(self, success, avatar ):
		if success:
			INFO_MSG("create role %s success" % self.playerName )
		else:
			ERROR_MSG( "%s: I can't create role anymore" % self.playerName )
		# destroy entity
		avatar.destroy( writeToDB = False )
	
	
	def _getAccountIDCB(self, rs, number, errStr):
		if rs is None:
			return
		accountDBID = int( rs[0][0] )
		INFO_MSG( "createRole for account %s id %d." % (self.account,  accountDBID) )
	
		# check validity of raceClasses
		gender = self.raceclass & csdefine.RCMASK_GENDER
		profession = self.raceclass & csdefine.RCMASK_CLASS
	
		classStr = csconst.g_en_class[profession]
		maxHP = Const.calcHPMax( profession, 1 )
		maxMP = Const.calcMPMax( profession, 1 )
	
		# create new role now
		paramDict = { "playerName":self.playerName, "parentDBID":accountDBID, "raceclass":self.raceclass, "hairNumber" : self.hairNum, "faceNumber" : self.faceNum }
		paramDict["position"] = csconst.g_default_spawn_site[self.raceclass & csdefine.RCMASK_CLASS][0]
		paramDict["direction"] = csconst.g_default_spawn_site[self.raceclass & csdefine.RCMASK_CLASS][1]
		paramDict["spaceType"] = csconst.g_default_spawn_city[self.raceclass & csdefine.RCMASK_RACE]
		paramDict["HP"] = maxHP
		paramDict["MP"] = maxMP
		paramDict["level"] = 80
		INFO_MSG( "create new role for", paramDict )
		avatar = BigWorld.createBaseLocally( "Role", paramDict )
		self._initKitbag( avatar )
		self._initBankBag( avatar )
		avatar.gold = 10
		avatar.silver = 6
		generateAll( avatar )
		avatar.writeToDB( self._onWriteRoleToDBRollback )
	
	def _insertLogonMappingCB(self, rs, number, errStr):
		if number == 0:
			DEBUG_MSG( "create LogonMapping failure for %s.", self.account )
			return
		INFO_MSG( "account %s succesfully mapped." % self.account )
		
	def _insertAccountCB(self, rs, number, errStr):
		if number == 0:
			DEBUG_MSG( "create account %s failure." % self.account )
			return
		INFO_MSG( "account %s created." % self.account )
		BigWorld.executeRawDatabaseCommand("select id from tbl_Account where sm_playerName='%s'" % self.account, self._getAccountIDCB)
		BigWorld.executeRawDatabaseCommand("insert into bigworldLogOnMapping set logOnName='%s', recordName='%s', password=md5('%s'), typeID=16" % (self.account, self.account, self.password), self._insertLogonMappingCB)		

def createRole(_account, _password, _raceclass, _playerName, _hairNum = 0, _faceNum = 0):
	roleInfo = RoleInfo(_account, _password, _raceclass, _playerName, _hairNum, _faceNum)
	roleInfo.createInDB()

gnIndex = 1
def batchCreateRole(nNumber):
	lstRace = [0x0 | 0x10, 0x0 | 0x20, 0x0 | 0x30, 0x0 | 0x40, 0x1 | 0x10, 0x1 | 0x20, 0x1 | 0x30, 0x1 | 0x40]
	global gnIndex
	nIndex = 1
	strPost = '00001'
	while nIndex <= nNumber:
		strIndex = str(gnIndex)
		strPost = strPost[:-len(strIndex)] + strIndex
		strAcct = 'aBot' + strPost
		strRole = 'Bot' + strPost
		createRole(strAcct, 'test', choice(lstRace), strRole)
		nIndex += 1
		gnIndex += 1 


# ---------------------------------------------------------------------------------------------
# 给刚创建的角色技能、装备、金钱
# ---------------------------------------------------------------------------------------------
g_newBornGratuities = {}									# 默认的初始赠送技能和物品等

g_newBornGratuities[csdefine.CLASS_FIGHTER] = {
		"skills"	: [322361002,311101001,322206001],
		"equip" : [20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008],
		"items" : [20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008,20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008,20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008],
		}

g_newBornGratuities[csdefine.CLASS_SWORDMAN] = {
		"skills"	: [322361002,311114001,322208001],
		"equip" : [20102008,20202008,20302008,20402008,20502008,20602008,20702008,10501008,30101008,30201008,30201008],
		"items" : [20102008,20202008,20302008,20402008,20502008,20602008,20702008,10501008,30101008,30201008,30201008,20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008,20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008],
		}

g_newBornGratuities[csdefine.CLASS_ARCHER] = {
		"skills"	: [322361002,311120001,322211001],
		"equip" : [20103008,20203008,20303008,20403008,20503008,20603008,20703008,10301008,30101008,30201008,30201008],
		"items" : [20103008,20203008,20303008,20403008,20503008,20603008,20703008,10301008,30101008,30201008,30201008],
		}

g_newBornGratuities[csdefine.CLASS_MAGE] = {
		"skills"	: [322361002,312108001,322221001],
		"equip" : [20104008,20204008,20304008,20404008,20504008,20604008,20704008,10401008,30101008,30201008,30201008],
		"items" : [20104008,20204008,20304008,20404008,20504008,20604008,20704008,10401008,30101008,30201008,30201008,20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008,20101008,20201008,20301008,20401008,20501008,20601008,20701008,10101008,30101008,30201008,30201008],
		}


def generateMoney( roleEntity, value ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param skillIDs: int list or tuple
	"""
	roleEntity.cellData["money"] = value

def generatePotential( roleEntity, value ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param skillIDs: int list or tuple
	"""
	roleEntity.cellData["potential"] = value

def generateSkill( roleEntity, skillIDs ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param skillIDs: int list or tuple
	"""
	roleEntity.cellData["attrSkillBox"] = list( skillIDs )

def generateEquip( roleEntity, items ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param items: like as [(itemID, amount), ...]
	"""
	kitbag = roleEntity.cellData["itemsBag"]
	index = 1
	for itemID in items:
		item = g_items.createDynamicItem( itemID )
		orders = getWieldOrders(item)
		if len( orders ) == 0: return
		orderID = orders[0]
		if len( orders ) == 2:
			item1 = kitbag.getByOrder( orders[0] )
			item2 = kitbag.getByOrder( orders[1] )
			if ( not item2 ) and item1:	# 如果右手空 且 左手已经装备
				orderID = orders[1]

		modelNum = item.model()
		type = item.getType()
		if type == ItemTypeEnum.ITEM_WEAPON_AXE1:
			roleEntity.cellData["righthandFDict"] = { "modelNum": modelNum, "iLevel" : 9, "stAmount" : 0 }
		elif type == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
			roleEntity.cellData["righthandFDict"] = { "modelNum": modelNum, "iLevel" : 9, "stAmount" : 0 }
			roleEntity.cellData["lefthandFDict"] = { "modelNum": modelNum, "iLevel" : 9, "stAmount" : 0 }
		elif type == ItemTypeEnum.ITEM_WEAPON_LONGBOW:
			roleEntity.cellData["lefthandFDict"] = { "modelNum": modelNum, "iLevel" : 9, "stAmount" : 0 }
		elif type == ItemTypeEnum.ITEM_WEAPON_STAFF:
			roleEntity.cellData["righthandFDict"] = { "modelNum": modelNum, "iLevel" : 9, "stAmount" : 0 }
		elif type == ItemTypeEnum.ITEM_ARMOR_BODY:
			roleEntity.cellData["bodyFDict"] = { "modelNum" : modelNum, "iLevel" : 9 }
		elif type == ItemTypeEnum.ITEM_ARMOR_VOLA:
			roleEntity.cellData["volaFDict"] = { "modelNum" : modelNum, "iLevel" : 9 }
		elif type == ItemTypeEnum.ITEM_ARMOR_BREECH:
			roleEntity.cellData["breechFDict"] = { "modelNum" : modelNum, "iLevel" : 9 }
		elif type == ItemTypeEnum.ITEM_ARMOR_FEET:
			roleEntity.cellData["feetFDict"] = { "modelNum" : modelNum, "iLevel" : 9 }
		
		kitbag.add( orderID, item )
		

def generateItem( roleEntity, items ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param items: like as [(itemID, amount), ...]
	"""
	kitbag = roleEntity.cellData["itemsBag"]
	orderID = csdefine.KB_COMMON_ID * csdefine.KB_MAX_SPACE
	for itemID in items:
		assert orderID is not None
		item = g_items.createDynamicItem( itemID )
		kitbag.add( orderID, item )
		orderID += 1
		print 66666666666666666666666
		
def generateAll( roleEntity ):
	"""
	角色初始化属性数据，给角色一些物品或技能等

	@param	roleEntity	: instance of role entity
	@type	roleEntity	: Entity
	"""
	classes = roleEntity.cellData["raceclass"] & csdefine.RCMASK_CLASS
	generateEquip( roleEntity,g_newBornGratuities[classes]["equip"] )
	generateItem( roleEntity,g_newBornGratuities[classes]["items"] )
	#for key, value in g_newBornGratuities[classes].iteritems():
	#	funcs[key]( roleEntity, value )
	#roleEntity.qb_initializeOnCreateRole( classes )

def getWieldOrders( item ):
	return funcEquip.m_cwt2cel[item.query( "eq_wieldType" )]

