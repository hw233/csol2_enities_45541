# -*- coding: gb18030 -*-

# $Id: CItemBase.py,v 1.52 2008-08-29 07:22:49 yangkai Exp $

"""
�Զ������͵��߻���ģ�顣

"""
import BigWorld
import cPickle
import copy
import ItemTypeEnum
import ItemAttrClass
from bwdebug import *
from MsgLogger import g_logger
import csstatus
import csdefine
import csconst
import ItemDataList
import SkillTargetObjImpl
import SkillTypeImpl
import CooldownFlyweight
from Resource.SkillLoader import g_skills
from Function import newUID
import math
import sys
from ItemSystemExp import EquipQualityExp


g_items = ItemDataList.ItemDataList.instance()
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

CANNOT_USE_DRUG_HP_SPACE = [
	csdefine.SPACE_TYPE_TONG_TURN_WAR,
	csdefine.SPACE_TYPE_CAMP_TURN_WAR,
	csdefine.SPACE_TYPE_JUE_DI_FAN_JI,
	csdefine.SPACE_TYPE_AO_ZHAN_QUN_XIONG,
]

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
		self.uid = newUID()						# ȫ��Ψһ��ID
		self.id = srcData["id"]					# ���Լ���Ӧ��ȫ��ʵ������
		self.srcData = srcData					# ���Լ���Ӧ��ȫ��ʵ�����������ڳ�ʼ��ʱ��������ʱʹ�ò���Ҫ����
		self.kitbag = None						# ��Ʒ�������ĸ�����ʵ����,��һ������
		self.order = -1							# ��Ʒ���õ�λ��
		self.amount = 1							# ��ǰ������Ĭ��ֵΪ1
		self.extra = {}							# ����Ķ�̬���ԣ����е���Ҫ���浽���ݿ��Ǩ��ʱ��Ҫ��������Զ�����������
		self.tmpExtra = {}						# ����Ķ�̬���ԣ�������extra,Ψһ�����Ǳ����ڴ˵����Բ����̣�ֻ������ʱ��Ч


	def name( self ):
		"""
		��ȡ��Ʒ����
		"""
		return self.query("name")

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
		return self.srcData["icon"]

	def model( self ):
		"""
		��ȡģ�ͱ��
		"""
		try:
			return int( self.srcData["model"] )
		except:
			return 0

	def getParticle( self ):
		"""
		��ȡԭʼ��ЧID
		"""
		return self.query( "particle", "" )

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
		
	def pop( self, attrName, default = None ):
		return self.extra.pop( attrName, default )

	def popTemp( self, attrName, default = None ):
		return self.tmpExtra.pop( attrName, default )

	def set( self, attrName, value, owner = None ):
		"""
		���ö�̬����

		@param owner: ���ֵΪNone����ֻ�������������ֵ(ֻ��)ΪRoleʵ���������entity.client.onItemAttrUpdated()����
		@return: None
		"""
		self.extra[attrName] = value
		if owner:
			if attrName not in ItemAttrClass.m_itemAttrMap:
				WARNING_MSG( "set undefine property. -->", attrName, value )
				return
			stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( value )
			# ���� attrName --> ItemAttrClass.m_itemAttrSendMap.index( attrName )
			# Ŀ����Ϊ�˼���ͨ������ 16:26 2008-3-21 yk
			owner.client.onItemAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

	def setTemp( self, attrName, value, owner = None ):
		"""
		���ö�̬����ʱ����

		@param owner: ���ֵΪNone����ֻ�������������ֵ(ֻ��)ΪRoleʵ���������entity.client.onItemAttrUpdated()����
		@return: None
		"""
		self.tmpExtra[attrName] = value
		if owner:
			if attrName not in ItemAttrClass.m_itemAttrMap:
				WARNING_MSG( "set undefine property. -->", attrName, value )
				return
			stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( value )
			# ���� attrName --> ItemAttrClass.m_itemAttrSendMap.index( attrName )
			# Ŀ����Ϊ�˼���ͨ������ 16:26 2008-3-21 yk
			owner.client.onItemTempAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )

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
		if valDict.has_key( "tmpExtra" ) and len( valDict["tmpExtra"] ):
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

	def setLifeTime( self, lifeTime, owner = None ):
		"""
		��ȡ��Ʒ���ʱ��
		"""
		return self.set( "lifeTime", int( lifeTime ), owner )

	def getDeadTime( self ):
		"""
		��ȡ��Ʒ����ʱ��
		"""
		return self.query( "deadTime", 0 )

	def setDeadTime( self, deadTime, owner = None ):
		"""
		������Ʒ����ʱ��
		"""
		self.set( "deadTime", int( deadTime ), owner )

	def isActiveLifeTime( self ):
		"""
		�ж��Ƿ񼤻�ʹ��ʱ��
		"""
		return self.query( "deadTime" ) is not None

	def activaLifeTime( self, owner = None ):
		"""
		����һ����Ʒ��ʹ��ʱ��
		���������������߼�ʱ����ôowner����ΪNone
		��Ϊ����Ӧ��֪ͨaddLifeItemsToManage
		"""
		if self.getLifeType() == 0: return
		if self.isActiveLifeTime(): return
		lifeTime = self.getLifeTime()
		if lifeTime == 0: return
		deadTime = time.time() + lifeTime
		self.setDeadTime( deadTime, owner )
		if owner is None: return
		owner.addLifeItemsToManage( [self.uid], [deadTime] )

	def isOverdue( self ):
		"""
		�жϵ�ǰ�Ƿ����
		"""
		if not self.isActiveLifeTime(): return False
		return time.time() > self.getDeadTime()

	def onAdd( self, owner ):
		"""
		��һ�ȡ��Ʒ
		"""
		if owner is None: return
		# ���ʱ�����ʹ���
		lifeType = self.getLifeType()
		if lifeType in [ItemTypeEnum.CLTT_ON_GET, ItemTypeEnum.CLTT_ON_GET_EVER]:
			self.activaLifeTime( owner )
		# ������Ʒ�Ĵ���
		bindType = self.getBindType()
		isBinded = self.isBinded()
		if not isBinded:
			# ʰȡ�
			if bindType == ItemTypeEnum.CBT_PICKUP:
				self.setBindType( ItemTypeEnum.CBT_PICKUP, owner )
			# ����
			elif bindType == ItemTypeEnum.CBT_QUEST:
				self.setBindType( ItemTypeEnum.CBT_QUEST, owner )

	def onDelete( self, owner ):
		"""
		���ɾ����Ʒ
		"""
		if owner is None: return
		# ���һ������ʹ��ʱ����Ʒ
		deadTime = self.getDeadTime()
		if deadTime <= 0: return
		owner.removeLifeItemsFromManage( [self.uid], [deadTime] )

	def onWield( self, owner ):
		"""
		vitural method
		"""
		pass

	def setKitbag( self, kitbag ):
		"""
		@param kitbag: ���ø���Ʒ�ı���ʵ��
		@type  kitbag: KitbagBase
		@return:          ��
		"""
		self.kitbag = kitbag

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
		��ȡ����ƷorderID
		"""
		return self.order

	def getUid( self ):
		"""
		��ȡ����Ʒuid
		"""
		return self.uid

	def getType( self ):
		"""
		��ȡ����Ʒ����
		"""
		return self.query( "type" )

	def isType( self, type ):
		"""
		�ж��Լ��Ƿ�Ϊĳ���͵ĵ��ߣ�

		@param type: ���жϵ�����
		@type  type: UINT32
		@return:     True == ��ָ�������ͣ�False == ����ָ��������
		@rtype:      BOOL
		"""
		return self.getType() == type

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

	def getUseDegree( self ):
		"""
		ȡ��ʹ�ô���
		"""
		return self.query( "useDegree", 0 )

	def getAmount( self ):
		"""
		ȡ����Ʒ����
		"""
		return self.amount

	def setAmount( self, amount, owner = None, reason = csdefine.ITEM_NORMAL ):
		"""
		������Ʒ����
		���ﻹ�漰һ��
		"""
		old = self.amount
		self.amount = amount
		if owner:
			if amount <= 0:
				order = self.order
				owner.itemsBag.removeByOrder( order )
				owner.client.removeItemCB( order )
				if reason == csdefine.ITEM_NORMAL:	# �����зǳ���ķ������Ʒ������setAmount����,������ֻ��Ҫ��¼������ϵ���Ʒ��setAmount����,
					return							# ���������ITEM_NORMALԭ��,�Ͳ�����¼����Ȼ���ǻᾡ����֤������ϵ�ÿһ��setAmount��������ӵ��һ�� reason.
					
			else:
				attrName = "amount"
				stream = ItemAttrClass.m_itemAttrMap[attrName].addToStream( amount )
				owner.client.onItemAttrUpdated( self.order, ItemAttrClass.m_itemAttrSendMap.index( attrName ), stream )
				if reason == csdefine.ITEM_NORMAL:
					return
		
			try:
				g_logger.itemSetAmountLog( owner.databaseID, owner.getName(), owner.grade, reason, self.uid, self.name(), old, amount )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def onSpellOver( self, owner ):
		"""
		����ʹ�ý���
		"""
		useDegree = self.getUseDegree()
		if useDegree == -1:
			pass
		elif useDegree > 1:
			self.set( "useDegree", useDegree - 1, owner )
		else:
			# self.setAmount( self.getAmount() - 1, owner )
			owner.removeItem_( self.order, 1, csdefine.DELETE_ITEM_USE )	# 2009-07-06 SPF

		owner.questIncreaseItemUsed( self.id )


	def setUseDegree( self, useDegree, owner = None ):
		"""
		����ʹ�ô���
		"""
		self.set( "useDegree", useDegree, owner )

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
		if self.isBinded(): return False
		if self.hasFlag( ItemTypeEnum.CFE_NO_TRADE ): return False
		return True

	def canExchange( self ):
		"""
		�ƿ����ж���Ʒ�Ŀɽ������� by����
		"""
		return not self.hasFlag( ItemTypeEnum.CFE_NO_TRADE )

	def getSpellID( self ):
		"""
		"""
		return self.query( "spell", 0 )

	def use( self, owner, target ):
		"""
		ʹ����Ʒ

		@param    owner: ����ӵ����
		@type     owner: Entity
		@param   target: ʹ��Ŀ��
		@type    target: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		# �����Ʒ�Ƿ����
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult

		spell = self.query( "spell" )
		target = SkillTargetObjImpl.createTargetObjEntity( target )
		# ��������Ϊ����Ҫ���浱ǰҪʹ�õ���Ʒ��Ϣ
		# ��������Ҫ��ȷ����Ʒ��������ʹ�õ�����²ż�¼��Ʒ��Ϣ
		# ������Bug
		try:
			spell = g_skills[spell]
		except:
			return  csstatus.SKILL_NOT_EXIST

		value = self.getUid()
		# ���tempһ��Ҫ��useableCheck֮ǰ���ã���ΪuseableCheck��һЩ
		# �̳нӿ���Ҫ֪������ʹ�õ���Ʒ�������Ʒ�ô����temp�в�ѯ
		if owner.intonating():
			return csstatus.SKILL_INTONATING
		# �߻�Ҫ��������״̬�¿���ʹ��ҩƷcsol-2229
		if owner.inHomingSpell() and ( not self.getType() in ItemTypeEnum.ROLE_DRUG_LIST ):
			return csstatus.SKILL_CANT_CAST
		if owner.getCurrentSpaceType() in CANNOT_USE_DRUG_HP_SPACE and ( self.getType() in ItemTypeEnum.ROLE_DRUG_HP_LIST ):
			return csstatus.SKILL_CAN_NOT_CAST_IN_CURRENT_SPACE
		owner.setTemp( "item_using", value )
		state = spell.useableCheck( owner, target )
		if state != csstatus.SKILL_GO_ON:
			owner.removeTemp( "item_using" )
			return csconst.SKILL_STATE_TO_ITEM_STATE.get( state,state )

		spell.use( owner, target )
		return csstatus.SKILL_GO_ON

	def onSetCooldownInUsed( self, caster ):
		"""
		��Ʒ��Ʒʹ�ú󴥷�
		@param    caster: ��Ʒʹ����
		@type     caster: Entity
		"""
		self.freeze()
		springUsedCD = self.query( "springUsedCD", {} )
		for cd, time in springUsedCD.iteritems():
			endTime = g_cooldowns[ cd ].calculateTime( time )
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def onSetCooldownInIntonateOver( self, caster ):
		"""
		������Ʒ���������󴥷�
		@param    owner: ��Ʒʹ����
		@type     owner: Entity
		"""
		self.unfreeze()
		springIntonateOverCD = self.query( "springIntonateOverCD", {} )
		for cd, time in springIntonateOverCD.iteritems():
			endTime = g_cooldowns[ cd ].calculateTime( time )
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def checkUse( self, owner ):
		"""
		���ʹ�����Ƿ���ʹ�ø���Ʒ

		@param owner: ����ӵ����
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		# �ж��Ƿ�����ʹ��������Ʒ����Ϊ��������Ʒʹ�ò������н���
		if not owner.queryTemp( "item_using" ) is None:
			return csstatus.CIB_MSG_ITEM_MULT_USE
		# �ж���Ʒ��Ӱ���CD��û�й�
		if owner.level < self.getReqLevel():
			return csstatus.CIB_MSG_ITEM_NOT_USED

		isLifeType = self.getLifeType()
		hasLifeTime = self.getLifeTime()
		if isLifeType and not hasLifeTime:
			return csstatus.CIB_MSG_ITEM_NO_USE_TIME

		if not self.query( "spell", 0 ):
			return csstatus.CIB_MSG_ITEM_NOT_USED

		limitCD = self.query( "limitCD", [] )
		for cd in limitCD:
			timeVal = owner.getCooldown( cd )
			if not g_cooldowns[ cd ].isTimeout( timeVal ):
				return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON

	def new( self ):
		"""
		ʹ�õ�ǰ��Ʒ�����ݴ���һ���µ���Ʒ��

		@return: �̳���CItemBase���Զ������͵���ʵ��
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		return obj

	def copy( self ):
		"""
		�����Լ���uid��Դ��Ʒһ����

		@return: �̳���CItemBase���Զ������͵���ʵ��
		@rtype:  class
		"""
		obj = g_items.createDynamicItem( self.id, self.getAmount() )
		obj.extra = copy.deepcopy( self.extra )
		obj.uid = self.uid
		return obj

	def createEntity( self, spaceID, position, direction ):
		"""
		�������Լ�������ȫ��ʵ��������һ�������Լ���Entity�ӵ���ͼ��

		@param   spaceID: ��ͼID��
		@type    spaceID: INT32
		@param  position: ���߲���������ĸ�λ��
		@type   position: VECTOR3
		@param direction: ���߲�����ŵķ���
		@type  direction: VECTOR3
		@param   srcItem: �̳���CItemBase���Զ����������ʵ����
		                  �ò���Ĭ��ֵΪNone����ʾʹ��ȫ��ʵ����Ĭ�ϲ�����ʼ����������ʹ���ṩ�Ĳ������г�ʼ��
		@type    srcItem: CItemBase
		@return:          һ���µĵ���entity
		@rtype:           Entity
		"""
		return g_items.createEntity( self.id, spaceID, position, direction, { "itemProp" : self } )

	def getPrice( self ):
		"""
		��ȡ��ǰ���߼�ֵ���п��ܻ���Ҫ����ĳЩ���Լ���
		"""
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

	def updatePrice( self, owner = None ):
		"""
		Virtual Method
		ˢ����Ʒ�ļ۸�
		����һЩ������Ʒ�۸�Ĳ����ı䣬�۸�Ҳ����Ӧ�ı���
		"""
		basePrice = self.queryBaseData( "price", 0 )
		self.setPrice( basePrice, owner )

	def getWarIntegral( self ):
		"""
		��ȡ���ߵ�ս�����ּ�ֵ
		"""
		return self.query( "warIntegral",  0)

	def setPrice( self, value, owner = None ):
		"""
		���ø���Ʒ�ļ۸�
		"""
		self.set( "price", int( value ), owner )

	def getMaxSpace( self ):
		"""
		"""
		return self.query( "kb_maxSpace", 0 )

	def setPrefix( self, prefix, owner = None ):
		"""
		���ø���Ʒ��ǰ׺
		"""
		self.set( "prefix", prefix, owner )

	def setQuality( self, quality, owner = None ):
		"""
		���ø���Ʒ��Ʒ��
		@param    quality: ��ƷƷ��
		@type     quality: INT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		self.set( "quality", quality, owner )

	def getQuestID( self ):
		"""
		��ȡ����Ʒ����������ID
		"""
		return self.query( "questID", 0 )

	def getVehicleMoveSpeed( self ):
		"""
		��ȡ����Ʒ���ƶ��ٶ�����(���)
		"""
		return self.query( "vehicle_move_speed", 0.0 )

	def getVehicleMaxMount( self ):
		"""
		��ȡ����Ʒ�Ķ���װ������(���)
		"""
		return self.query( "vehicle_max_mount", 0 )

	def getVehicleCanFight( self ):
		"""
		��ȡ������Ƿ���ս��(���)
		"""
		return self.query( "vehicle_canFight", 0 )

	def getLastBjExtraEffectID( self ):
		"""
		��ȡ���һ����ʯ��Ƕ��������
		"""
		bjEffect = self.getBjExtraEffect()
		if len( bjEffect ) == 0:
			effectID = 0
		else:
			effectID = bjEffect[-1][0]
		return effectID

	def getBjExtraEffectCount( self ):
		"""
		��ȡ��ʯ��Ƕ����
		"""
		return len( self.getBjExtraEffect() )

	def getBjExtraEffect( self ):
		"""
		��ȡ��ʯ��������
		"""
		return self.query( "bj_extraEffect", [] )

	def setBjExtraEffect( self, effect, owner = None ):
		"""
		����װ��/��ʯ��������
		����װ��/��ʯ����Ƕ����
		@param    effect: ��Ƕ����
		@type     effect: dic
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		self.set("bj_extraEffect", effect, owner )

	def addBjExtraEffect( self, effect, owner = None ):
		"""
		����װ��/��ʯ����Ƕ����
		@param    effect: ��Ƕ����
		@type     effect: ( key, value )
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		oldEffect = self.getBjExtraEffect()
		oldEffect.extend( effect )
		self.setBjExtraEffect( oldEffect, owner )

	def setLevel( self, level, owner = None ):
		"""
		������Ʒ�ĵȼ� by ����
		@param    reqLevel: ʹ�õȼ�
		@type     reqLevel: UINT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		self.set( "level", level, owner )

	def setReqLevel( self, reqLevel, owner = None ):
		"""
		������Ʒ��ʹ�õȼ�
		@param    reqLevel: ʹ�õȼ�
		@type     reqLevel: UINT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		self.set( "reqLevel", reqLevel, owner )

	def setBaseRate( self, baseRate, owner = None ):
		"""
		������Ʒ�Ļ�������Ʒ�ʱ���
		@param baseRate: ��������Ʒ�ʱ���
		@type  baseRate: Float
		@param    owner: װ��ӵ����
		@type     owner: Entity
		@return:    ��
		"""
		self.set( "baseQualityRate", baseRate, owner )

	def getBaseRate( self ):
		"""
		��ȡ��Ʒ�Ļ�����������Ʒ�ʱ���
		"""
		return self.query( "baseQualityRate", 0.0 )

	def setExcRate( self, baseRate, owner = None ):
		"""
		������Ʒ�ĸ�������Ʒ�ʱ���
		@param baseRate: ��������Ʒ�ʱ���
		@type  baseRate: Float
		@param    owner: װ��ӵ����
		@type     owner: Entity
		@return:    ��
		"""
		self.set( "excQualityRate", baseRate, owner )

	def getExcRate( self ):
		"""
		��ȡ��Ʒ�ĸ�������Ʒ�ʱ���
		"""
		return self.query( "excQualityRate", 0.0 )

	def getPrefix( self ):
		"""
		��ȡ��Ʒ��ǰ׺
		"""
		return self.query( "prefix", 0 )

	def getQuality( self ):
		"""
		��ȡ��Ʒ��Ʒ��
		"""
		return self.query( "quality", 1 )

	def setBindType( self, type, owner = None ):
		"""
		���ð�����
		"""
		bit = 1 << type
		bindType = ( bit << 4 ) | bit
		self.set( "bindType", bindType, owner )

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

	def cancelBindType( self, owner = None ):
		"""
		ȡ������Ʒ�İ󶨣��ָ�����ǰ״̬
		"""
		srcBindType = self.getSrcBindType()
		self.set( "bindType", srcBindType, owner )

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

	def isFrozen( self ):
		"""
		�ж��Լ��Ƿ񱻶���
		@return: BOOL
		"""
		return self.queryTemp( "freeze", 0 )

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

	def onDieDrop( self ):
		"""
		"""
		pass

	def isAlreadyWield( self ):
		"""
		�ж��Ƿ��Ѿ�װ����Ч����
		@return: BOOL
		@rtype:  BOOL
		"""
		# ��������Ʒ�����Ƿ�װ����Ч���Ľӿ�
		# Ĭ�Ϸ��� False
		# ����ԭ�򣬴����жദ��Ҫ�ж�ĳ����Ʒ�Ƿ��ڱ�װ���ϵ�Ч��������ʱ���������Ʒ����һ��CEquip�ͻ����
		# 2009-07-16 SPF
		return False

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
# CItemBase.py
