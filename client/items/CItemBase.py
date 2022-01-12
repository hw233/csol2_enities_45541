# -*- coding: gb18030 -*-

# $Id: CItemBase.py,v 1.61 2008-08-13 08:57:12 qilan Exp $

"""
�Զ������͵��߻���ģ�顣
"""

# clommon
import copy
import cPickle
import BigWorld
import csdefine
import csconst
import csstatus
import ItemTypeEnum
import ItemAttrClass

# client
import Const
import Define
import ItemDataList
import skills
import SkillTargetObjImpl
import CItemDescription
import TextFormatMgr

# common
from bwdebug import *
from ItemSystemExp import EquipQualityExp

# client
from Time import Time
from gbref import rds
from EquipEffectLoader import EquipEffectLoader
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CItemBase

# global instances
g_items = ItemDataList.ItemDataList.instance()
equ_items_type = ItemTypeEnum.EQUIP_TYPE_SET
g_equipQualityExp = EquipQualityExp.instance()
g_equipEffect = EquipEffectLoader.instance()


class CItemBase:
	"""
	�Զ������͵���ʵ������Ҫ���ڱ���ʹ���һЩ���ߵ��ױ�����

	@ivar        id: ���Լ���Ӧ��ȫ��ʵ������
	@type        id: str
	@ivar    amount: ��ǰ����
	@type    amount: INT
	@ivar   srcData: ���Լ���Ӧ��ȫ�����ݣ��������ڳ�ʼ��ʱ��������ʱʹ�ò���Ҫ����
	@type   srcData: instance
	@ivar    kitbag: ��Ʒ�������ĸ�����ʵ����,��һ������
	@type    kitbag: KitbagBase
	@ivar     order: ��Ʒ���õ�λ��,��һ������
	@type     order: UINT8
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: ��Ʒ��ԭʼ����
		"""
		self.id = srcData["id"]					# ���Լ���Ӧ��ȫ��ʵ������
		self.srcData = srcData					# ���Լ���Ӧ��ȫ��ʵ�����������ڳ�ʼ��ʱ��������ʱʹ�ò���Ҫ����
		self.kitbag = None						# ��Ʒ�������ĸ�����ʵ����,��һ������
		self.order = -1							# ��Ʒ���õ�λ��
		self.amount = 1							# ��ǰ������Ĭ��ֵΪ1
		self.extra = {}							# ����Ķ�̬���ԣ����е���Ҫ���浽���ݿ��Ǩ��ʱ��Ҫ��������Զ�����������
		self.tmpExtra = {}						# ����Ķ�̬���ԣ�������extra,Ψһ�����Ǳ����ڴ˵����Բ����̣�ֻ������ʱ��Ч
		self.defaultColor = ( 255, 255, 255 ) 	# ��Ʒ������Ĭ����ɫ
		self.desFrame = CItemDescription.CItemDescription()# ��Ʒ��������Ϣ(����������Ӧ��������Ϣ������ģ��) - -add by hd

	def name( self ):
		"""
		��ȡ��Ʒ����
		"""
		return self.query("name","")

	def fullName( self ):
		"""
		��ȡ��Ʒ��ȫ�� �� ��ӥ������İ�����
		"""
		nameDes = self.name()
		proName = self.query( "propertyPrefix")
		if proName: nameDes = proName + nameDes
		instan = EquipQualityExp.instance()
		prefix = self.query( "prefix" )
		excName = instan.getName( prefix )
		if excName != "": nameDes = excName + nameDes
		return nameDes

	def icon( self ):
		"""
		��ȡͼ��·��
		"""
		iconName = self.query( "icon", Const.ITEM_DEFAULT_ICON )
		return "icons/%s.dds" % iconName

	def model( self ):
		"""
		��ȡģ��·��
		"""
		return int( self.query( "model", 0 ) )

	def credit( self ):
		"""
		��ȡ��Ʒ���������
		"""
		try:
			return self.srcData["reqCredit"]
		except:
			return {}

	def queryReqClasses( self ):
		"""
		��ȡ��Ʒ�����ְҵ�б�
		"""
		return self.query( "reqClasses", [] )

	def getReqGender( self ):
		"""
		��ȡ��Ʒ�����Ա��б�
		"""
		return self.query( "reqGender", [] )

	def queryBaseData( self, attrName, default = None ):
		"""
		��ȡһ�������ñ����ȡ������

		@param attrName: ��Ҫ��ȡ��ֵ���������ƣ�������õ�������ȡֵ��鿴common/ItemAttrClass.py
		@type  attrName: String
		@param  default: ���ָ�����Ե�ֵ�����ڣ�����ʲô��ĬΪ����None
		@type   default: any
		"""
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def query( self, attrName, default = None ):
		"""
		��ȡһ������

		@param attrName: ��Ҫ��ȡ��ֵ���������ƣ�������õ�������ȡֵ��鿴common/ItemAttrClass.py
		@type  attrName: String
		@param  default: ���ָ�����Ե�ֵ�����ڣ�����ʲô��ĬΪ����None
		@type   default: any
		"""
		if attrName in self.extra:
			return self.extra[attrName]
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def queryTemp( self, attrName, default = None ):
		"""
		��ȡһ����ʱ����

		@param attrName: ��Ҫ��ȡ��ֵ���������ƣ�������õ�������ȡֵ��鿴common/ItemAttrClass.py
		@type  attrName: String
		@param  default: ���ָ�����Ե�ֵ�����ڣ�����ʲô��ĬΪ����None
		@type   default: any
		"""
		if attrName in self.tmpExtra:
			return self.tmpExtra[attrName]
		if attrName in self.srcData:
			return self.srcData[attrName]
		return default

	def queryInt( self, attrName ):
		return self.query( attrName, 0 )

	def queryTempInt( self, attrName ):
		return self.queryTemp( attrName, 0 )

	def queryStr( self, attrName ):
		return self.query( attrName, "" )

	def queryTempStr( self, attrName ):
		return self.queryTemp( attrName, "" )

	def set( self, attrName, value, owner = None ):
		"""
		���ö�̬����

		@param owner: ���ֵΪNone����ֻ�������������ֵ(ֻ��)ΪRoleʵ���������entity.client.onItemAttrUpdated()����
		@return: None
		"""
		self.extra[attrName] = value

	def setTemp( self, attrName, value, owner = None ):
		"""
		���ö�̬����ʱ����

		@param owner: ���ֵΪNone����ֻ�������������ֵ(ֻ��)ΪRoleʵ���������entity.client.onItemAttrUpdated()����
		@return: None
		"""
		self.tmpExtra[attrName] = value

	def addToDict( self ):
		"""
		ת����ITEM type format.

		@return: dict
		@rtype:  dict
		"""
		return { 	"uid"		: self.uid,
					"id" 		: self.id,
					"amount" 	: self.amount,
					"order"		: self.order,
					"extra" 	: cPickle.dumps( self.extra, 2 ),
					"tmpExtra" 	: cPickle.dumps( self.tmpExtra, 2 ),
				}

	def loadFromDict( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self.uid = valDict["uid"]
		self.amount = valDict["amount"]
		self.order = valDict["order"]
		if valDict.has_key( "extra" ):
			self.extra = cPickle.loads( valDict["extra"] )
		if valDict.has_key( "tmpExtra" ):
			self.tmpExtra = cPickle.loads( valDict["tmpExtra"] )

	def getLifeType( self ):
		"""
		��ȡ��Ʒ�������
		"""
		return self.query( "lifeType", ItemTypeEnum.CLTT_NONE )

	def getLifeTime( self ):
		"""
		��ȡ��Ʒ���ʱ��
		"""
		return self.query( "lifeTime", 0 )

	def getDeadTime( self ):
		"""
		��ȡ��Ʒ����ʱ��
		"""
		return self.query( "deadTime", 0 )

	def getKitID( self ):
		"""
		��ȡ����Ʒ���ڰ���ID
		"""
		return self.order/csdefine.KB_MAX_SPACE

	def setOrder( self, order ):
		"""
		@param  order: ����Ʒ�����ĸ�λ��
		@type   order: UINT8
		@return:          ��
		"""
		self.order = order

	def getOrder( self ):
		"""
		��ȡ����Ʒ��orderλ��
		"""
		return self.order

	def getUid( self ):
		"""
		��ȡ����Ʒ��uidλ��
		"""
		return self.uid

	def getLevel( self ):
		"""
		��ȡ�ȼ�
		"""
		return self.query( "level", 0 )

	def getReqLevel( self ):
		"""
		��ȡʹ�õȼ�
		"""
		return self.query( "reqLevel", 0 )

	def getBaseRate( self ):
		"""
		��ȡ��Ʒ�Ļ�����������Ʒ�ʱ���
		"""
		return self.query( "baseQualityRate", 0.0 )
	
	def getExcRate( self ):
		"""
		��ȡ��Ʒ�ĸ�������Ʒ�ʱ���
		"""
		return self.query( "excQualityRate", 0.0 )

	def getType( self ):
		"""
		��ȡ����Ʒ������
		"""
		return self.query( "type" )

	def getPickUpType( self ):
		"""
		��ȡ����Ʒ��ʰȡ����
		"""
		put = self.query( "pickUpType" )
		return put if not (put is None or put == 0) else ItemTypeEnum.PICK_UP_TYPE_DEFAULT

	def isType( self, type ):
		"""
		�ж��Լ��Ƿ�Ϊĳ���͵ĵ��ߣ�

		@param type: ���жϵ����ͣ�
		@type  type: UINT32
		@return:     True == ��ָ�������ͣ�False == ����ָ��������
		@rtype:      BOOL
		"""
		return self.getType() == type

	def isCooldownType( self, cooldownType ):
		"""
		�ж������Ƿ���ĳһ���͵�cooldown��ͬ

		@param cooldownType: cooldown����
		@type  cooldownType: INT
		@return: bool
		"""
		return cooldownType in self.query( "limitCD", [] )

	def isActiveLifeTime( self ):
		"""
		�ж��Ƿ񼤻�ʹ��ʱ��
		"""
		return self.query( "deadTime" ) is not None

	def getAmount( self ):
		"""
		ȡ����Ʒ����
		"""
		return self.amount

	def setAmount( self, amount, owner = None ):
		"""
		ȡ����Ʒ����
		"""
		self.amount = amount

	def addFlag( self, flags, owner = None ):
		"""
		���ӱ�־

		@param flags: �����ӵı�־����־Ϊ���С�CFE_����ͷ�����
		@type  flags: UINT16
		@return:      ��
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		self.set( "flags", oldFlags | flags, owner )

	def removeFlag( self, flags, owner = None ):
		"""
		�Ƴ���־

		@param flags: ���Ƴ��ı�־����־Ϊ���С�CFE_����ͷ�����
		@type  flags: UINT16
		@return:      ��
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		# ��ȷ��������ֵ�������ȡ����
		self.set( "flags", (oldFlags | flags) ^ flags, owner )

	def hasFlag( self, flags ):
		"""
		�жϱ�־

		@param flags: ���жϵı�־����־Ϊ���С�CFE_����ͷ�����
		@type  flags: UINT16
		@return:      True == ����ָ���ı�־(���)��False == ������ָ���ı�־(���)
		@rtype:       BOOL
		"""
		flags = 1 << flags
		oldFlags = self.query( "flags", 0 )
		return flags & oldFlags == flags

	def getStackable( self ):
		"""
		��ȡ����Ʒ�ĵ������ޣ�Ĭ��Ϊ1
		"""
		return self.query( "stackable", 1 )

	def getOnlyLimit( self ):
		"""
		��ȡ����Ʒ�����ӵ������
		"""
		return self.query( "onlyLimit", 0 )

	def canStore( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ��洢

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_WAREHOUSE )

	def canSell( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_SELL )

	def canDestroy( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_DESTROY )

	def canRepair( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_REPAIR )

	def canConsume( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_WASTAGE )

	def canAbrasion( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�ĥ��

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_ABRASION )

	def canIntensify( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�ǿ��

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_INTENSIFY )

	def canRebuid( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_REBUILD )

	def canStiletto( self ):
		"""
		�ж�һ����Ʒ�Ƿ��ܱ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_STILETTO )

	def canGive( self ):
		"""
		�ж��Ƿ��ܸ�(��������֮�����Ʒ����)
		������ƷΪ��״̬ʱ������Ʒ���ܽ���

		@return: bool
		@rtype:  bool
		"""
		return not ( self.isBinded() or self.hasFlag( ItemTypeEnum.CFE_NO_TRADE ) )

	def getSpell( self ):
		"""
		��ȡ��Ʒ�����ļ���
		@return: SkillBase instance or None
		"""
		spellID = self.query( "spell", 0 )
		if not spellID:
			return None
		try:
			return skills.getSkill( spellID )
		except KeyError:
			return None

	def use( self, owner, target, position = (0.0, 0.0, 0.0) ):
		"""
		ʹ����Ʒ

		@param    owner: ����ӵ����
		@type     owner: Entity
		@param   target: ʹ��Ŀ��
		@type    target: Entity
		@param position: Ŀ��λ��,����ΪNone
		@type  position: tuple or VECTOR3
		@return: STATE CODE
		@rtype:  UINT16
		"""
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult

		sk = skills.getSkill( self.query( "spell" ) )
		state = sk.useableCheck( owner, SkillTargetObjImpl.createTargetObjEntity(target) )
		return csconst.SKILL_STATE_TO_ITEM_STATE.get( state,state )

	def checkUse( self, owner ):
		"""
		���ʹ�����Ƿ���ʹ�ø���Ʒ

		@param owner: ����ӵ����
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		if owner.level < self.getReqLevel():
			return csstatus.CIB_MSG_ITEM_NOT_USED

		isLifeType = self.getLifeType()
		hasLifeTime = self.getLifeTime()
		if isLifeType and not hasLifeTime:
			return csstatus.CIB_MSG_ITEM_NO_USE_TIME

		if not self.query( "spell", 0 ):
			return csstatus.CIB_MSG_ITEM_NOT_USED

		springUsedCD = self.query( "springUsedCD", {} )
		player = BigWorld.player()
		for cd in springUsedCD:
			endTime = player.getCooldown( cd )[3]
			if endTime > Time.time():
				return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON

	def copy( self ):
		"""
		�����Լ�

		@return: �̳���CItemBase���Զ������͵���ʵ��
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		return obj

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡ��Ʒר��������Ϣ
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		

		# ��ʾ��Ʒ���࣬�ȼ�����
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if reference.level < self.getReqLevel():
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		if desReqlevel != "":
			self.desFrame.SetDescription("itemreqLevel" , desReqlevel)
		useDegreeDes = attrMap["useDegree"].description( self, reference )
		if useDegreeDes != "":
			self.desFrame.SetDescription( "useDegree", useDegreeDes )
	
		# ��Ʒ����ȼ�(�߻���ʱ���������ԣ����Է����Ƿ��ڣ���ʱֻ��ע�͵������������)
	#	desLevel = attrMap["level"].description( self, reference )
	#	if desLevel != "":
	#		self.desFrame.SetDescription( "itemLevel" , desLevel )
		# ���͵��¼��Ϣ
		teleportRes = attrMap["ch_teleportRecord"].description( self, reference )
		if teleportRes != "":
			teleportRes = PL_Font.getSource( teleportRes, fc = ( 0, 255, 0 ) )
			self.desFrame.SetDescription( "ch_teleportRecord", teleportRes )
		# ս������
		warIntegralDes = attrMap["warIntegral"].description( self, reference )
		if warIntegralDes != "":
			self.desFrame.SetDescription( "warIntegral", warIntegralDes )
		# ��ʯ�ĸ�������
		desStuList = attrMap["bj_extraEffect"].descriptionList( self, reference )
		if len( desStuList ):
			desStuListTemp = [ PL_Font.getSource( des[0] ,fc = "c27" ) + " " + PL_Font.getSource( des[1] ,fc = "c27" ) for des in desStuList ]
			self.desFrame.SetDesSeveral( "bj_extraEffect", desStuListTemp )
		# ��ʯ��Ƕλ��
		deswWieldType = attrMap["bj_slotLocation"].description( self, reference )
		if deswWieldType != "":
			deswWieldType = PL_Font.getSource( deswWieldType, fc = "c27" )
			self.desFrame.SetDescription( "bj_slotLocation", deswWieldType )

	def description( self, reference ):
		"""
		��������

		@param reference: ���entity,��ʾ��˭����Ϊ���������Ĳ�����
		@type  reference: Entity
		@return:          ��Ʒ���ַ�������
		@rtype:           ARRAY of str
		"""
		# ��ʾ��Ʒ�����Ϣ
		self.getProDescription( reference )	#��ʾ��Ʒ�������Ϣ

		attrMap = ItemAttrClass.m_itemAttrMap
		# ��ʾ��Ʒ���֣�������Ʒ��Ʒ�ʾ�����Ʒ���ֵ���ɫ
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = self.getQualityColor() )
		self.desFrame.SetDescription("name" , nameDes)
		# ��Ʒ����
		desType = attrMap["type"].description( self, reference )
		self.desFrame.SetDescription( "type", desType )
		# ��������
		reqCredits = attrMap["reqCredit"].descriptionDict( self, reference )
		if reqCredits:
			reqCreditsDes = reqCredits.keys()
			for index in xrange( len( reqCreditsDes) ):
				if not reqCredits[ reqCreditsDes[index] ]:
					reqCreditsDes[ index ] = PL_Font.getSource( reqCreditsDes[ index ] , fc = "c3" )
			self.desFrame.SetDesSeveral( "reqCredit", reqCreditsDes )
	
		#�Ƿ��
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			desBind = PL_Font.getSource( desBind , fc = "c1" )
			self.desFrame.SetDescription( "bindType", desBind )
		#�Ƿ������� by����
		type = self.getType()
		if not type in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
			print self.isWhite()
			canEqu = False
			if type in equ_items_type:
				canEqu = True
			if canEqu and not self.isWhite():
				desObey = attrMap["eq_obey"].description( self, reference )
				if desObey != "":
					desObey = PL_Font.getSource( desObey, fc = "c7" )
					self.desFrame.SetDescription( "eq_obey", desObey )
		#�Ƿ�Ψһ
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CItemBase[1] )
		# �Ƿ�ɳ���
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CItemBase[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )
		# ȡ�ö��������1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 )
		# ȡ�ö��������2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
		#	if des1 != "": des2 = g_newLine + des2
			self.desFrame.SetDescription( "describe2", des2 )
		# ȡ�ö��������3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
		#	if des1 != "" or des2 != "": des3 = g_newLine + des3
			self.desFrame.SetDescription( "describe3", des3 )

		# ʣ��ʹ��ʱ��
		lifeType = self.getLifeType()
		if lifeType:
			lifeTime = self.getLifeTime()
			if lifeTime:
				deadTime = self.getDeadTime()
				if deadTime:
					sTime = int( Time.time() )
					rTime = deadTime - sTime
					if rTime > lifeTime: rTime = lifeTime
					des = lbs_CItemBase[3]
					if rTime <= 0:
						des += lbs_CItemBase[4]
					else:
						hour = rTime/3600
						min = ( rTime - hour * 3600 )/60
						sec = rTime%60

						# �޸�ʱ���������ʾ by����
						day = int( hour / 24 )

						if day:
							des += lbs_CItemBase[5] % day
						elif int( hour ):
							des += lbs_CItemBase[6] % hour
						elif int( min ):
							des += lbs_CItemBase[7] % min
						else:
							des += lbs_CItemBase[8] % sec
					des = PL_Font.getSource( des, fc = "c3" )
					self.desFrame.SetDescription( "lifeType", des )
			else:
				des = PL_Font.getSource( lbs_CItemBase[9], fc = "c3" )
				self.desFrame.SetDescription( "lifeType", des )

		return self.desFrame.GetDescription()

	def getPrice( self ):
		"""
		��ȡ��ǰ���߼�ֵ���п��ܻ���Ҫ����ĳЩ���Լ���
		"""
		# ��Ʒ�ļ۸��ʹ�ô����й�
		basePrice = self.getRecodePrice()
		baseUseDegree = self.queryBaseData( "useDegree", 0 )
		if baseUseDegree <= 1: return basePrice
		useDegree = self.getUseDegree()
		newPrice = int( useDegree * 1.0 / baseUseDegree * basePrice )
		return newPrice

	def getRecodePrice( self ):
		"""
		��ȡ��Ʒ��ǰ��¼�ļ۸񣬴����ݺͷ�������������һ����
		�������getPrice()�ӿڼ���ļ۸�һ��
		"""
		return self.query( "price", 0 )

	def getQuestID( self ):
		"""
		��ȡ����Ʒ����������ID
		"""
		return self.query( "questID", 0 )

	def getBjExtraEffect( self ):
		"""
		��ȡ��ʯ��������
		"""
		return self.query( "bj_extraEffect", [] )

	def getPrefix( self ):
		"""
		��ȡ��Ʒ��ǰ׺
		"""
		return self.query( "prefix", 0 )

	def getMaxSpace( self ):
		"""
		"""
		return self.query( "kb_maxSpace", 0 )

	def getQuality( self ):
		"""
		��ȡ��Ʒ��Ʒ��
		"""
		return self.query( "quality", 1 )

	def getBindType( self ):
		"""
		��ȡ������
		"""
		return self.query( "bindType", 0 )

	def getSrcBindType( self ):
		"""
		����ԭ�Ͱ�����
		"""
		return self.queryBaseData( "bindType", 0 )

	def isBinded( self ):
		"""
		�жϸ���Ʒ�Ƿ��
		@return Bool
		"""
		return self.getBindType() != self.getSrcBindType()

	def getUseDegree( self ):
		"""
		ȡ��ʹ�ô���
		"""
		return self.query( "useDegree", 0 )

	def isFrozen( self ):
		"""
		�ж��Լ��Ƿ񱻶���
		@return: BOOL
		"""
		return self.queryTemp( "freeze" )

	def freeze( self, owner = None ):
		"""
		�����Լ�
		@return: ����ܶ����򷵻�True, ����Ѿ��������򷵻�False
		@rtype:  bool
		"""
		if self.queryTemp( "freeze", 0 ):
			return False
		self.setTemp( "freeze", 1, owner )
		return True

	def unfreeze( self, owner = None ):
		"""
		�ⶳ�Լ�
		@return: ��
		"""
		self.setTemp( "freeze", 0, owner )

	def isEquip( self ):
		"""
		virtual method.
		�ж��Ƿ���װ��
		"""
		return False

	def isWhite( self ):
		"""
		virtual method.
		�ж��Ƿ��ǰ�ɫ��Ʒ
		"""
		return self.getQuality() == ItemTypeEnum.CQT_WHITE

	def isBlue( self ):
		"""
		virtual method.
		�ж��Ƿ�����ɫ��Ʒ
		"""
		return self.getQuality() == ItemTypeEnum.CQT_BLUE

	def isGold( self ):
		"""
		virtual method.
		�ж��Ƿ��ǽ�ɫ��Ʒ
		"""
		return self.getQuality() == ItemTypeEnum.CQT_GOLD

	def isPink( self ):
		"""
		virtual method.
		�ж��Ƿ��Ƿ�ɫ��Ʒ
		"""
		return self.getQuality() == ItemTypeEnum.CQT_PINK

	def isGreen( self ):
		"""
		virtual method.
		�ж��Ƿ�����ɫ��Ʒ
		"""
		return self.getQuality() == ItemTypeEnum.CQT_GREEN

	def isOverdue( self ):
		"""
		virtual method.
		�ж��Ƿ�
		"""
		if not self.isActiveLifeTime(): return False
		return Time.time() > self.getDeadTime()


	def yinpiao( self ):
		"""
		��ȡ��Ʊ��Ʒ��������
		"""
		return self.query( "yinpiao", 0 )


	def reqYinpiao( self ):
		"""
		��ȡ��Ʒ�������Ʊ
		"""
		return self.query( "reqYinpiao", 0 )

	def setObey( self, type, owner = None ):
		"""
		�������� by����
		"""
		self.set( "eq_obey", type, owner )

	def getObey( self ):
		"""
		��ȡ����״̬ by����
		"""
		return self.query( "eq_obey", 0 )

	def isObey( self ):
		"""
		�ж��Ƿ�����װ�� by����
		"""
		if self.getObey():
			return True
		return False

	def getVehicleMoveSpeed( self ):
		"""
		��ȡ����Ʒ���ƶ��ٶ�����(���)
		"""
		return self.query( "vehicle_move_speed", 0.0 )

	def getTsItemType( self ):
		"""
		�����Ʒ�����۷�������
		"""
		itemType = self.getType()

		if itemType in ItemTypeEnum.WEAPON_LIST:
			return csconst.TI_SHOU_WEAPON
		elif itemType in ItemTypeEnum.ARMOR_LIST:
			return csconst.TI_SHOU_ARMOR
		elif itemType == ItemTypeEnum.ITEM_PRODUCE_STUFF:
			return csconst.TI_SHOU_PRODUCE_STUFF
		else:
			return csconst.TI_SHOU_TYPE_NONE

	def getQualityColor( self ) :
		"""
		��ȡƷ����ɫ
		hyw--2010.01.28
		"""
		return g_equipQualityExp.getColorByQuality( self.getQuality() )

	def getGodWeaponSkillID( self ):
		"""
		��ȡ�������Լ���ID
		"""
		return 0

	def checkUseStatus( self, owner ) :
		"""
		�����Ʒ��ʹ�����
		"""
		if owner.level < self.getReqLevel() :
			return Define.ITEM_STATUS_USELESSNESS
		return Define.ITEM_STATUS_NATURAL
