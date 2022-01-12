# -*- coding: gb18030 -*-
# $Id: PetEpitome.py,v 1.30 2008-08-19 09:40:01 huangdong Exp $
#
"""
implement pet epitome type

2007/07/01: writen by huangyongwei
2007/11/17: rewriten by huangyongwei and rename it from "PetEpitomeType.py" to "PetEpitome.py"
"""


import BigWorld
import csarithmetic
import csdefine
import csconst
import Love3
from copy import copy
from bwdebug import *
from cscollections import MapList
from PetFormulas import formulas
from CellPetDict import CellPetEpitome


# --------------------------------------------------------------------
# global
# --------------------------------------------------------------------
# -----------------------------------------------------
# def �ж��壬���ұ��浽���ݿ�����ԣ�Persistent == True��
# -----------------------------------------------------
_saveAttrs = MapList()						# ������Ҫ���������
_saveAttrs["ownerDBID"] = int				# �����Ľ�ɫ�����ݿ� ID
_saveAttrs["className"] = str				# �����ļ��е� Entity ��� ID
_saveAttrs["mapMonster"] = str				# ��Ӧ�� momnster �� entity ��� ID
_saveAttrs["modelNumber"] = str				# ģ�ͺ�
_saveAttrs["uname"] = str					# Ĭ������
_saveAttrs["name"] = str					# �Զ�������
_saveAttrs["gender"] = int					# �Ա�
_saveAttrs["species"] = int					# ���֣����

_saveAttrs["level"] = int					# �ȼ�
_saveAttrs["HP"] = int						# ����
_saveAttrs["MP"] = int						# ����
_saveAttrs["EXP"] = int						# ����

_saveAttrs["e_corporeity"] = int			# ǿ��������ֵ
_saveAttrs["e_strength"] = int				# ǿ��������ֵ
_saveAttrs["e_intellect"] = int				# ǿ��������ֵ
_saveAttrs["e_dexterity"] = int				# ǿ��������ֵ

_saveAttrs["ec_corporeity"] = int			# ����ǿ������
_saveAttrs["ec_strength"] = int				# ����ǿ������
_saveAttrs["ec_intellect"] = int			# ����ǿ������
_saveAttrs["ec_dexterity"] = int			# ����ǿ������
_saveAttrs["ec_free"] = int					# ����ǿ������

#_saveAttrs["baseNimbus"] = int				# ��ֵ����ֵ
_saveAttrs["ability"] = int					# �ɳ���
_saveAttrs["nimbus"] = int					# ��ǰ��ֵ
_saveAttrs["calcaneus"] = int				# ����
_saveAttrs["stamp"] = int					# ӡ��
_saveAttrs["isBinded"] = int				# �Ƿ�󶨣�����ʹ��bool����Ϊ��ת���Ķ�����db�ж�ȡ���ַ������ݡ�16:30 2009-11-27��wsf

_saveAttrs["character"] = int				# �Ը�
_saveAttrs["life"] = int					# ����
_saveAttrs["joyancy"] = int					# ���ֶ�
_saveAttrs["procreated"] = int				# �Ƿ��Ѿ���ֳ��csdefine.py ��������ֵ��ѡ��δ��ֳ�����ڷ�ֳ���ѷ�ֳ��

_saveAttrs["absorbableEXPLevelValue"] = int	# ������һ���Ѿ���ȡ�ľ���
_saveAttrs["absorbableEXP"] = long			# �����յľ���ֵ
_saveAttrs["absorbDate"] = long				# �ϴ����վ���ֵ������

# -----------------------------------------------------
# def ���ж��壬�������浽���ݿ�����ԣ�Persistent == False��
# -----------------------------------------------------
_unsaveAttrs = []
_unsaveAttrs.append( "takeLevel" )			# Я���ȼ�
_unsaveAttrs.append( "databaseID" )			# ���ݿ� ID
_unsaveAttrs.append( "attrSkillBox" )		# �����б�

# �����������
_secondaryAttrs = []
_secondaryAttrs.append( "corporeity" )		# ����
_secondaryAttrs.append( "strength" )		# ����
_secondaryAttrs.append( "intellect" )		# ����
_secondaryAttrs.append( "dexterity" )		# ����

# -----------------------------------------------------
# ֻ�� Epitome ���õ���Pet.def �в���Ҫ���������
# -----------------------------------------------------
_tempAttrs = []								# ������ʱ����
_tempAttrs.append( "mapPetID" )				# ��Ӧ�� entityID����������Ļ��������û������Ϊ 0
_tempAttrs.append( "isInVend" )				# �����Ƿ��ڰ�̯��
_tempAttrs.append( "vendSellPrice" )		# �����̯���ۼ۸�

# -----------------------------------------------------
# Epitome ����������
# -----------------------------------------------------
_allAttrs = \
	_saveAttrs.keys() + \
	_unsaveAttrs + \
	_secondaryAttrs + \
	_tempAttrs								# �������е�����

# -----------------------------------------------------
# ��Ҫ���͵��ͻ��ˣ���ͻ��˹���������
# -----------------------------------------------------
_sendingAttrs = copy( _allAttrs )			# Ҫ���͵��ͻ��ˣ��ͻ��˿ɼ����ĳ�������
_sendingAttrs.remove( "ownerDBID" )			# ������������ҵ����ݿ� ID ���ͻ��ˣ���Ϊ�ͻ��˿����ҵ��Լ���ɫ�� databaseID ���û�б�Ҫ��
_sendingAttrs.remove( "className" )			# �����������ļ��е� enttiy ��� ID ���ͻ���
_sendingAttrs.remove( "e_corporeity" )		# ����������ǿ��ֵ���ͻ���
_sendingAttrs.remove( "e_strength" )		# ����������ǿ��ֵ���ͻ���
_sendingAttrs.remove( "e_intellect" )		# ����������ǿ��ֵ���ͻ���
_sendingAttrs.remove( "e_dexterity" )		# ����������ǿ��ֵ���ͻ���
_sendingAttrs.remove( "absorbableEXP" )		# �����;�������ֵ���ͻ���
_sendingAttrs.remove( "absorbDate" )		# ��������һ�ξ�������ʱ�䵽�ͻ���

# -----------------------------------------------------
# ��Ҫ���µ�cell������
# -----------------------------------------------------
_sendingCellAttrs = ["databaseID", "species", "level", \
					"className", "mapMonster", "ability", \
					"life", "joyancy", "takeLevel", \
					"stamp", "procreated", "gender", \
					"isBinded",
					]

# --------------------------------------------------------------------
# exclude sql command methods
# --------------------------------------------------------------------
def _queryPetsSkills( strPetDBIDs, callback ) :
	"""
	����һ�����ļ��� ID
	"""
	def onQuery( rest, rows, errStr ) :
		if errStr :
			ERROR_MSG( "query pet's( %i ) skills fail: %s" % errStr )
			callback( {} )
		else :
			skills = {}
			for skillInfo in rest :
				petID, skillID = int( skillInfo[0] ), int( skillInfo[1] )
				if petID in skills :
					skills[petID].append( skillID )
				else :
					skills[petID] = [skillID]
			callback( skills )

	sql = "select parentID, sm_value from tbl_Pet_attrSkillBox where parentID in %s" % strPetDBIDs
	INFO_MSG( "\nquery pet's skills:\n" + sql + "\n" )
	BigWorld.executeRawDatabaseCommand( sql, onQuery )

def queryPets( ownerDBID, petDBIDs, callback ) :
	sql = "select id%s from tbl_Pet where sm_ownerDBID = %i and id in %s"
	strAttrs = ""
	for attrName, attrType in _saveAttrs.items() :
		strAttrs += ", sm_%s" % attrName
	strdbids = str( tuple( [int( id ) for id in petDBIDs] ) )			# remove character "L" in long type id
	if len( petDBIDs ) == 1 :
		strdbids = strdbids.replace( ",", "" )
	sql = sql % ( strAttrs, ownerDBID, strdbids )
	INFO_MSG( "\n\t" + sql + "\n" )

	petEpitomes = MapList()
	def onQuerySkills( skills ) :
		for id, epitome in petEpitomes.items() :
			epitome.updateAttr( "attrSkillBox", skills.get( id, [] ) )
		callback( True, petEpitomes )

	def onQuery( rest, rows, errStr ) :
		if errStr :
			ERROR_MSG( "read database fail when query pets:\n\t%s" % errStr )
			callback( False, {} )
		else :
			for petQuery in rest :
				epitome = PetEpitome.getEpitomeByQuery( petQuery )
				petEpitomes[long( petQuery[0] )] = epitome
			_queryPetsSkills( strdbids, onQuerySkills )
	BigWorld.executeRawDatabaseCommand( sql, onQuery )

def queryFosterPets( petDBIDs, callback ) :
	sql = "select id%s from tbl_Pet where id in %s"
	strAttrs = ""
	for attrName, attrType in _saveAttrs.items() :
		strAttrs += ", sm_%s" % attrName
	strdbids = str( tuple( [int( id ) for id in petDBIDs] ) )			# remove character "L" in long type id
	if len( petDBIDs ) == 1 :
		strdbids = strdbids.replace( ",", "" )
	sql = sql % ( strAttrs, strdbids )
	INFO_MSG( "\n\t" + sql + "\n" )

	petEpitomes = MapList()
	def onQuerySkills( skills ) :
		for id, epitome in petEpitomes.items() :
			epitome.updateAttr( "attrSkillBox", skills.get( id, [] ) )
		callback( True, petEpitomes )

	def onQuery( rest, rows, errStr ) :
		if errStr :
			ERROR_MSG( "read database fail when query pets:\n\t%s" % errStr )
			callback( False, {} )
		else :
			for petQuery in rest :
				epitome = PetEpitome.getEpitomeByQuery( petQuery )
				petEpitomes[long( petQuery[0] )] = epitome
			_queryPetsSkills( strdbids, onQuerySkills )
	BigWorld.executeRawDatabaseCommand( sql, onQuery )

# -----------------------------------------------------
def _updatePetAttrs( petDBID, attrs, callback ) :
	"""
	������Ҫ���ֵ����ݿ�ĳ������ԣ�ģ���ڵ��ã�
	@type			petDBID  : INT64
	@param			petDBID  : �������ݿ� ID
	@type			attrs	 : list
	@param			attrs	 : Ҫ���µ����Ժ�����ֵ�б�
	@type			callback : callable object
	@param			callback : �������Իص������������һ��������
							   1���������Գɹ�
							   0����������ʧ�ܣ�ԭ�������Բ�����
							   -1����������ʧ�ܣ�ԭ����д�����ݿ�ʧ�ܣ�δ֪ԭ�򣬺ܿ����� dbmgr ���ˣ�
	"""
	sql = "update tbl_Pet set "
	count = 0
	for name, value in attrs.items() :
		if name not in _saveAttrs : continue
		if type( value ) is str : value = "'%s'" % BigWorld.escape_string( value )
		sql += ( "sm_%s=%s," % ( name, value ) )
		count += 1
	if count == 0 :
		callback( 1 )
		return

	sql = "%s where id = %i" % ( sql[:-1], petDBID )
	INFO_MSG( "\n\t" + sql + "\n" )

	def onUpdateAttr( rest, rows, errStr ) :
		if errStr is not None :
			DEBUG_MSG( "update attribute %s fail!" % attrs.keys() )
			callback( -1 )
		elif rows <= 0 :
			DEBUG_MSG( "the pet you wanted to update its attributes( %s ) is not exist!" % attrs.keys() )
			callback( 0 )
		else :
			callback( 1 )
	BigWorld.executeRawDatabaseCommand( sql, onUpdateAttr )


# --------------------------------------------------------------------
# implement pet epitome class
# --------------------------------------------------------------------
class PetEpitome :
	def __init__( self ) :
		# -----------------------------------
		# def �ж��壬���ұ��浽���ݿ������
		# -----------------------------------
		self.__ownerDBID = 0
		self.__className = ""
		self.__mapMonster = ""
		self.__modelNumber = ""
		self.__uname = ""
		self.__name = ""
		self.__gender = csdefine.GENDER_MALE
		self.__species = csdefine.PET_HIERARCHY_GROWNUP | csdefine.PET_TYPE_STRENGTH

		self.__level = 1
		self.__HP = 0
		self.__MP = 0
		self.__EXP = 0

		self.__e_corporeity = 0
		self.__e_strength = 0
		self.__e_intellect = 0
		self.__e_dexterity = 0

		self.__ec_corporeity = 0
		self.__ec_strength = 0
		self.__ec_intellect = 0
		self.__ec_dexterity = 0
		self.__ec_free = 0

		self.__ability = 0
		self.__nimbus = 0
		self.__calcaneus = 0
		self.__stamp = 0
		self.__isBinded = False

		self.__character = csdefine.PET_CHARACTER_SUREFOOTED
		self.__life = 65535
		self.__joyancy = 100
		self.__procreated = False

		self.__absorbableEXPLevelValue = 0	# ������һ���Ѿ���ȡ�ľ���
		self.__absorbableEXP = 0	# ����ÿһ�����ȡ�ľ���ֵ����
		self.__absorbDate = 0		# ����ÿһ�����ȡ�ľ���ֵ������Ч��time.time()

		# -----------------------------------
		# def ���ж��壬�������浽���ݿ������
		# -----------------------------------
		self.__takeLevel = 0
		self.__databaseID = 0
		self.__attrSkillBox = []

		# ��������
		self.__corporeity = 0
		self.__strength = 0
		self.__intellect = 0
		self.__dexterity = 0

		# -----------------------------------
		# ֻ�� Epitome ���õ���Pet.def �в���Ҫ���������
		# -----------------------------------
		self.__mapPetID = 0
		self.__isInVend = False		# �����Ƿ��ڰ�̯��
		self.__vendSellPrice = 0	# �����̯���ۼ۸�


	@staticmethod
	def getEpitomeByQuery( petQuery ) :
		"""
		ͨ�����ݿ��в�ѯ���������ݣ�����һ�� Epitome ʵ��
		ͨ���ڽ�ɫ��������ʱ����ʼ�������ʹ��
		@type				petQuery : list
		@param				petQuery : ����������Ϣ�б�
		"""
		epitome = PetEpitome()
		for idx, ( attrName, attrType ) in enumerate( _saveAttrs.items() ) :
			value = attrType( petQuery[idx + 1] )
			epitome.updateAttr( attrName, value )
		epitome.updateAttr( "databaseID", long( petQuery[0] ) )					# �������ݿ� ID
		mapMonster = epitome.getAttr( "mapMonster" )							# ��Ӧ�Ĺ���� className
		monsterScript = Love3.g_objFactory.getObject( mapMonster )				# ��Ӧ�Ĺ���

		# 14:52 2009-10-22,wsf����ֹ�߻����������õ���ʱ����������������ò����������쳣ǰ�����־���Ա�������⡣
		if monsterScript is None:
			ERROR_MSG( "--->>>npcMonster.xml�����ڳ���( %s )����." % mapMonster )

		epitome.updateAttr( "takeLevel", monsterScript.takeLevel )				# ����Я���ȼ�
		species = epitome.getAttr( "species" )
		level = epitome.getAttr( "level" )
		nimbus = epitome.getAttr( "nimbus" )
		sndAttrValues = formulas.getSndProperties( species, level, nimbus )
		for attr in _secondaryAttrs :											# �������ж�������
			e_value = epitome.getAttr( "e_" + attr )
			sndAttrValue = sndAttrValues[attr] + e_value
			epitome.updateAttr( attr, sndAttrValue )
		return epitome


	# ----------------------------------------------------------------
	# ��������
	# ----------------------------------------------------------------
	@property
	def databaseID( self ) :
		"""
		��������ݿ� ID
		"""
		return self.__databaseID

	@property
	def level( self ):
		"""
		����ȼ�
		"""
		return self.__level

	@property
	def species( self ):
		"""
		�������ͳ���ɳ�����ȼ�
		"""
		return self.__species

	@property
	def modelNumber( self ):
		"""
		����ģ��
		"""
		return self.__modelNumber


	# ----------------------------------------------------------------
	# mathods for packing / un packing
	# ----------------------------------------------------------------
	def getDictFromObj( self, epitome ) :
		dict = {}
		for attrName in _sendingAttrs :
			dict[attrName] = epitome.getAttr( attrName )
		return dict

	def createObjFromDict( self, dict ) :
		epitome = PetEpitome()
		for attrName, value in dict.items() :
			epitome.updateAttr( attrName, value )
		return epitome

	def isSameType( self, obj ) :
		return isinstance( obj, PetEpitome )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getAttr( self, attrName ) :
		"""
		��ȡ��������
		"""
		fullName = "_PetEpitome__" + attrName
		if hasattr( self, fullName ) :
			return getattr( self, fullName )
		else :
			ERROR_MSG( "pet epitome has no attribute: '%s'" % attrName )
		return None

	def getDisplayName( self ) :
		"""
		��ȡ����ȫ����
		"""
		return formulas.getDisplayName( self.__species, self.__uname, self.__name )

	# ---------------------------------------
	def getCellPetEpitome( self ) :
		"""
		��ȡ���﹫���� cell �Ĳ������ݣ���Ӧ alias.xml �ж���ģ�CELL_PET��
		"""
		cellPetEpitome = CellPetEpitome()
		for attrName in _sendingCellAttrs:
			setattr( cellPetEpitome, attrName, getattr( self, "_PetEpitome__" + attrName ) )

		return cellPetEpitome

	def getStoredPetDict( self ) :
		"""
		��ȡҪ�洢������ֿ��еĳ��������ֵ�
		"""
		storedDict = {}
		storedDict["databaseID"] = self.databaseID
		storedDict["name"] = self.getDisplayName()
		storedDict["level"] = self.level
		storedDict["species"] = self.species
		storedDict["modelNumber"] = self.modelNumber
		return storedDict

	# -------------------------------------------------
	def updateAttr( self, attrName, value, owner = None, callback = None ) :
		"""
		���³�������
		@type				attrName : str
		@param				attrName : ��������
		@type				value	 : type of attribute
		@param				value	 : ����ֵ
		@type				owner	 : Role
		@param				owner	 : ���������Ľ�ɫ
									   ע�⣺����������ֵ�������Եĸ��½��ᷢ�͵�������ɫ�Ŀͻ��ˣ����򲻷���
											��Щ���Ա����� _sendingAttrs ���г�������
		@type				callback : callable object
		@param				callback : �������Իص�
									   ע�⣺�������һ���ص�����Ҫ�����Ը���ͬʱ���浽���ݿ�
											��Щ���Ա����� _saveAttrs ���г�������
									   callback �������һ��������
									   1���������Գɹ�
									   0����������ʧ�ܣ�ԭ�������Բ�����
									   -1����������ʧ�ܣ�ԭ����д�����ݿ�ʧ�ܣ�δ֪ԭ�򣬺ܿ����� dbmgr ���ˣ�
		"""
		if owner is None and callback is not None :									# ���ֻ���� callback �������� owner
			raise "if callback argument is not None, you must tell me the owner!"	# ���׳��쳣

		fullName = "_PetEpitome__" + attrName
		if not hasattr( self, fullName ) :											# �ж������Ƿ����
			ERROR_MSG( "pet epitome has no attribute: '%s'" % attrName )
			if callback is not None :
				callback( 0 )
			return

		if callback is None :														# ����Ҫд�����ݿ�
			setattr( self, fullName, value )
			if hasattr( owner, "client" ) and owner.client is not None :
				owner.client.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
			if hasattr( owner, "cell" ) and attrName in _sendingCellAttrs:
				owner.cell.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
			return

		def onUpdateAttr( res ) :
			callback( res )
			if res <= 0 : return
			setattr( self, fullName, value )
			if owner is not None and hasattr( owner, "client" ) :
				owner.client.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
			if hasattr( owner, "cell" ) and attrName in _sendingCellAttrs:
				owner.cell.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
		_updatePetAttrs( self.databaseID, { attrName : value }, onUpdateAttr )		# д�����ݿ�

	def updateByPet( self, pet, owner = None ) :
		"""
		���� epitome �е���������Ϊ�������������
		һ��������ʱ����
		"""
		attrsDict = pet.cellData
		if type( attrsDict ) is not dict :
			attrsDict = attrsDict.getDict()
		for attrName in _allAttrs :									# �����������Ե��ͻ���
			if attrName in _tempAttrs :								# �ų���ʱ����
				continue
			oldValue = self.getAttr( attrName )
			if attrName in attrsDict :								# cell ����
				value = pet.cellData[attrName]
				if oldValue != value :
					self.updateAttr( attrName, value, owner )
			elif hasattr( pet, attrName ) :							# base ����
				value = getattr( pet, attrName )
				if oldValue != value :
					self.updateAttr( attrName, value, owner )
			else :
				ERROR_MSG( "pet's cellData is not contain attribute: '%s'" % attrName )

	def updateByDict( self, dict, owner = None, callback = None ) :
		"""
		����һ������
		@type				owner	 : Role
		@param				owner	 : ���������Ľ�ɫ
									   ע�⣺����������ֵ�������Եĸ��½��ᷢ�͵�������ɫ�Ŀͻ��ˣ����򲻷���
											��Щ���Ա����� _sendingAttrs ���г�������
		@type				callback : �������Իص�
									   ע�⣺�������һ���ص�����Ҫ�����Ը���ͬʱ���浽���ݿ�
											��Щ���Ա����� _saveAttrs ���г�������
		@param				callback :
		"""
		if owner is None and callback is not None :
			raise "if callback argument is not None, you must tell me the owner!"

		if callback is None :
			for attrName, value in dict.items() :
				self.updateAttr( attrName, value, owner )
			return

		def onUpdateAttrs( res ) :
			callback( res )
			if res < 0 : return
			for attrName, value in dict.items() :
				self.updateAttr( attrName, value, owner )
		_updatePetAttrs( self.databaseID, dict, onUpdateAttrs )


# --------------------------------------------------------------------
# implement active pet information class
# --------------------------------------------------------------------
class ActivePet :
	def getDictFromObj( self, actPet ) :
		return actPet

	def createObjFromDict( self, dict ) :
		return dict

	def isSameType( self, obj ) :
		return True


# --------------------------------------------------------------------
# pickle instances
# --------------------------------------------------------------------
instance = PetEpitome()
actPetInstance = ActivePet()
