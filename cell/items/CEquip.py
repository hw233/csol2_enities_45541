# -*- coding: gb18030 -*-

# $Id: CEquip.py,v 1.33 2008-09-04 07:44:43 kebiao Exp $

"""
װ�������ģ��
"""
from CItemBase import CItemBase
import funcEquip
from bwdebug import *
import csdefine
import Const
import random
import csconst
import SkillTypeImpl
import ItemTypeEnum
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()
from EquipSuitLoader import EquipSuitLoader
g_equipSuit = EquipSuitLoader.instance()
from ItemSystemExp import EquipIntensifyExp
g_equipIntensify = EquipIntensifyExp.instance()
from ItemSystemExp import ItemTypeAmendExp
g_typeAmend = ItemTypeAmendExp.instance()
from ItemSystemExp import EquipQualityExp
g_itemQualityExp = EquipQualityExp.instance()
from ItemSystemExp import PropertyPrefixExp
g_itemPropPrefixExp = PropertyPrefixExp.instance()
from ItemSystemExp import EquipAttrExp
g_itemPropAttrExp = EquipAttrExp.instance()

from config.server.EquipIntensifyAttr import Datas as EIA_DATA

import random
import math

from config.item.EquipAttrRebuildProb import Datas as attrRebuildProb

class CEquip( CItemBase ):
	"""
	װ��������

	@ivar wieldStatus: װ��״̬��0������Բ��������ʾû��װ��Ч����1��ʾװ����Ч����
	                   ���ֵ���ܻᱣ�棬������ȡ��ÿ����ҵ�¼��ʱ�򶼻����¸������ֵ
	                     - 0 ��ʾ��װ��û��װ����Ч��
	                     - 1 ��ʾ����װ��,����������˵��ʾ��װ�����˺��ǵ����˺�
	                     - 2 ����������˵��ʾ��װ�����˺���˫���˺�
	@type wieldStatus: UINT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )

	def fullName( self ):
		"""
		��ȡ��Ʒ��ȫ�� �� ��ӥ������İ�����
		"""
		#if len( self.getCreateEffect() ):
		#	return self.name()
		return CItemBase.fullName( self )

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return INT32
		"""
		raise AssertionError, "I can't do this!"

	def isAlreadyWield( self ):
		"""
		�ж��Ƿ��Ѿ�װ����Ч����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_wieldStatus", 0 ) > 0

	def isSuitEffectWield( self ):
		"""
		�ж��Ƿ��Ѿ�װ������װ������

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_suitEffectStatus", 0 ) > 0

	def getWieldOrders( self ):
		"""
		ȡ�õ�ǰ��Ʒ�Ŀ�װ��λ���б�������Ʒ���Է���װ��������Щλ���ϣ�CEL_*

		@return: tuple of int
		@rtype:  tuple of int
		"""
		return funcEquip.m_cwt2cel[self.query( "eq_wieldType" )]

	def getUnwieldOrders( self, equipKitbag, equipOrder ):
		"""
		���ڵ�Ҫװ��ĳ�����͵�װ��ʱ���װ������Ҫж����Щλ�õ�װ��

		@param equipKitbag: װ����
		@type  equipKitbag: KitbagType
		@param  equipOrder: ��Ҫװ����λ��
		@type   equipOrder: INT8
		@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
		                    ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò����򷵻�None
		@rtype:             tuple of UINT8/None
		"""
		return funcEquip.m_unwieldCheck[self.query( "eq_wieldType" )]( equipKitbag, equipOrder )

	def wieldExtraEffect( self, owner ):
		"""
		װ����������
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self  )

	def unWieldExtraEffect( self, owner ):
		"""
		ж�ظ�������
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

	def wieldCreateEffect( self, owner ):
		"""
		װ����ע����
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		createEffect = self.getCreateEffect()
		for key, value in createEffect:
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self  )

	def unWieldCreateEffect( self, owner ):
		"""
		ж�ع�ע����
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		createEffect = self.getCreateEffect()
		for key, value in createEffect:
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

	def wieldSuitEffect( self, owner ):
		"""
		װ����װ����
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		suitEffect = self.query( "eq_suitEffect", {} )
		for suitKey, suitValue in suitEffect.iteritems():
			effectClass = g_equipEffect.getEffect( suitKey )
			if effectClass is None: continue
			effectClass.attach( owner, suitValue, self  )

	def unWieldSuitEffect( self, owner ):
		"""
		ж����װ����
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		suitEffect = self.query( "eq_suitEffect", {} )
		for suitKey, suitValue in suitEffect.iteritems():
			effectClass = g_equipEffect.getEffect( suitKey )
			if effectClass is None: continue
			effectClass.detach( owner, suitValue, self  )

	def wieldBjEffect( self, owner ):
		"""
		װ����Ƕ����
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		bjEffect = self.getBjExtraEffect()
		for data in bjEffect:
			effectClass = g_equipEffect.getEffect( data[0] )
			if effectClass is None: continue
			effectClass.attach( owner, data[1], self  )

	def unWieldBjEffect( self, owner ):
		"""
		ж����Ƕ����
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return:    None
		"""
		bjEffect = self.getBjExtraEffect()
		for data in bjEffect:
			effectClass = g_equipEffect.getEffect( data[0] )
			if effectClass is None: continue
			effectClass.detach( owner, data[1], self  )

	def wield( self, owner, update = True ):
		"""
		װ������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		# ��װ���������ٴ�װ���������Ч���Ƿ�������⣬��װ��Ҫ�󳶲��ϣ���˲�����canWield��
		if self.isAlreadyWield(): return False
		if not self.canWield( owner ): return False

		# װ����������
		self.wieldExtraEffect( owner )

		# װ����ע����
		self.wieldCreateEffect( owner )

		# װ����Ƕ����
		self.wieldBjEffect( owner )

		# ��ǰװ��Ϊ��ɫװ�����п��ܴ�����װ�Ƿ񼤻�
		# ���ϴ�����һ����ɫ��װ������������ɫװ������װ����
		isSuitEqu = False
		if self.isGreen():
			suitEquipIDs = owner.getSuitEquipIDs()
			if g_equipSuit.isSuit( suitEquipIDs ):
				isSuitEqu = True
				for equip in owner.getAllGreenEquips():
					if equip.isSuitEffectWield(): continue
					equip.wieldSuitEffect( owner )
					equip.setTemp( "eq_suitEffectStatus", 1, owner )

		# �ж�ǿ����Ч��
		# �������������7��װ���������Ƿ��ߡ���������������7������ǿ���ȼ�Ϊ9ʱ����һ���ǿ����װЧ��1��
		# ��ɫ�����������3������ɫ�������������3%���������ֵ���3%����������ֵ���3%��ȫ����һ����Ч��
		# ���ȫ��װ����ǿ���ȼ�Ϊ9ʱ����һ���ǿ����װЧ��2��
		# ��ɫ�����������6������ɫ�������������6%���������ֵ���6%����������ֵ���6%�����һ���������Ĺ�Ч��

		# ��ʶ��װ����Ч��
		self.setTemp( "eq_wieldStatus", 1, owner )

		# ����װ�����Ч������װ����ʱ��װ����
		self.onWield( owner )
		owner.questItemAmountChanged( self, -1 )	# װ���ɹ���Ӱ������Ŀ�ꡣ
		return True

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		if not self.isAlreadyWield(): return
		self.setTemp( "eq_wieldStatus", 0, owner )		# ��ʶû��װ����Ч��
		# ж�¸�������
		self.unWieldExtraEffect( owner )

		# д�¹�ע����
		self.unWieldCreateEffect( owner )

		# ж����Ƕ����
		self.unWieldBjEffect( owner )

		# ж��һ��װ����ʱ�����ʣ�µ�װ��������װ��ֻж���Լ�����װ����
		# ���������ж�����е���װ����
		if self.isGreen():
			greenEquipIDs = owner.getSuitEquipIDs()
			if not g_equipSuit.isSuit( greenEquipIDs ):
				for equip in owner.getAllGreenEquips():
					if not equip.isSuitEffectWield(): continue
					equip.unWieldSuitEffect( owner )
					equip.setTemp( "eq_suitEffectStatus", 0, owner )

		if self.isSuitEffectWield():
			self.unWieldSuitEffect( owner )
			self.setTemp( "eq_suitEffectStatus", 0, owner )

		if update: owner.calcDynamicProperties()
		owner.questItemAmountChanged( self, 1 )		# ж��װ����Ӱ������Ŀ�ꡣ
		return

	def onWield( self, owner ):
		"""
		vitural method
		"""
		# ����װ�����ʱ��ʹ��ʱ��
		lifeType = self.getLifeType()
		if lifeType in [ItemTypeEnum.CLTT_ON_WIELD, ItemTypeEnum.CLTT_ON_WIELD_EVER]:
			self.activaLifeTime( owner )

		# װ��������
		bindType = self.getBindType()
		isBinded = self.isBinded()
		if bindType == ItemTypeEnum.CBT_EQUIP and not isBinded:
			self.setBindType( ItemTypeEnum.CBT_EQUIP, owner )

	def canWield( self, owner ):
		"""
		����Ƿ���װ����ƷЧ��

		@param owner: ���ߵ�ʹ���ߣ���ӵ���ߣ�
		@type  owner: Entity
		@return:    True ����װ����False ������װ��
		@return:    BOOL
		"""
		if not self._checkReqlevel( owner ): return False
		if not self._checkReqGender( owner ): return False
		if not self._checkClasses( owner ): return False
		if not self._checkHardiness(): return False
		if not self._checkLifeTime(): return False
		return True

	def isSystemEquip( self ):
		"""
		�ж��Ƿ�Ϊϵͳװ��

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.query( "isSystemItem" ) == 1

	def _checkLifeTime( self ):
		"""
		���ʹ��ʱ��
		"""
		lifeType = self.getLifeType()
		lifeTime = self.getLifeTime()
		if lifeType and not lifeTime: return False
		return True

	def _checkHardiness( self ):
		"""
		��鵱ǰ�;ö�
		����һ��װ�����ԣ������ǰ�;ö�ΪNone������װ�����ǿ���װ����
		@return: ����0�򲻴�����������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		hMax = self.query( "eq_hardinessMax" )
		if hMax is None or hMax <= 0: return True
		return self.query( "eq_hardiness" ) > 0

	def _checkClasses( self, owner ):
		"""
		����װ��ְҵ

		@return: ƥ���򷵻�True, ���򷵻�False
		@rtype:  BOOL
		"""
		return self.isMetier( owner.getClass() )

	def _checkReqlevel( self, owner ):
		"""
		���װ���ȼ�

		@param owner: ����ӵ����
		@type  owner: Entity
		@return: ƥ���򷵻�True, ���򷵻�False
		@rtype:  BOOL
		"""
		return owner.level >= self.query( "reqLevel", 0 )

	def _checkReqGender( self, owner ):
		"""
		���װ�������Ա�

		@param owner: ��Ʒӵ����
		@type  owner: Entity
		@return: ƥ���򷵻�True, ���򷵻�False
		@rtype:  BOOL
		"""
		reqGender = self.getReqGender()
		if len( reqGender ) == 0: return True
		return owner.getGender() in reqGender

	def isMetier( self, metierType ):
		"""
		�ж��Ƿ����װ����ĳ��ְҵ��

		@parma metierType: ְҵ����; CEM_*; ����ʹ�á���(|)�������Ӷ������ʾ��ͬʱ֧����ô���ְҵװ����
		@type  metierType: UINT16
		@return: ���������ĳְҵ��װ���򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		# û��classes���ʾû�д�����
		if reqClasses is None: return True
		return metierType in reqClasses

	def isMetierOnly( self, metierType ):
		"""
		�ж��Ƿ�ֻ��װ����ĳ��ְҵ��

		@parma metierType: ְҵ����; CEM_*
		@type  metierType: UINT16
		@return: ���ֻ����ָ����ְҵ��װ���򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		# û��classes���ʾû�д�����
		if reqClasses is None: return True
		return reqClasses  == [ metierType ]

	def getHardinessMax( self ):
		"""
		�������;ö�����(��ֵ����)
		@return: ����;ö�����,���û���;ö�������Ϊ0
		@rtype: int
		"""
		return self.query( "eq_hardinessMax", 0 )

	def getHardinessLimit( self ):
		"""
		��õ�ǰ�;ö�����(��ֵ�ܸ���)

		@return: ����;ö�,���û���;ö���Ϊ0
		@rtype: int
		"""
		return self.query( "eq_hardinessLimit", 0 )

	def getHardiness( self ):
		"""
		��õ�ǰ�;ö�
		@return: ��ǰ�;ö�,���û���;ö���Ϊ0
		@rtype: int
		"""
		return self.query( "eq_hardiness", 0 )

	def addHardiness( self, hardiness, owner = None ):
		"""
		���ӵ�ǰװ�����;ö�

		@param hardiness: �;�ֵ
		@type  hardiness: UINT16
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return: ��
		"""
		self.setHardiness( self.getHardiness() + hardiness, owner )

	def setHardiness( self, hardiness, owner = None ):
		"""
		���õ�ǰװ�����;ö�
		���������owner��ΪNone���򲻻��������

		@param hardiness: �;�ֵ
		@type  hardiness: UINT16
		@param  owner: װ��ӵ����
		@type   owner: Entity
		@return: ��
		"""
		# ����ɵ��;ú��µ��;ö���ȣ�ֱ�ӷ���
		oldHardiness = self.getHardiness()
		if hardiness < 0: hardiness = 0
		if oldHardiness == hardiness: return

		# �޶��µ��;öȲ��ܳ�����ǰ�;ö�����Ҳ����С��0
		hardinessLimit = self.getHardinessLimit()
		if hardiness > hardinessLimit:
			hardiness = hardinessLimit

		self.set( "eq_hardiness", int( hardiness ), owner )
		# phw 20091226: �����־����ս������־����Ҫ�ֲ�����ˣ���û��ʲô���������£����������
		#if owner is None:
		#	DEBUG_MSG( "None Owner set %s [%i] eq_hardiness from %i to %i" % ( self.name(), self.uid, oldHardiness, int( hardiness ) ) )
		#else:
		#	DEBUG_MSG( "%s [%i] set %s [%i] eq_hardiness from %i to %i" % ( owner.getName(), owner.id, self.name(), self.uid, oldHardiness, int( hardiness ) ) )

		# ���װ����װ�����ϣ�������Ҵ���
		if owner and self.getKitID() == csdefine.KB_EQUIP_ID:
			# ����ɵ��;ö�Ϊ0����ô������װ�ϸ�װ��
			if oldHardiness <= 0:
				self.wield( owner )
				owner.resetEquipModel( self.order, self )
			# ����µ��;ö�Ϊ0����ô��ж�¸�װ��
			if hardiness == 0:
				self.unWield( owner )
				owner.resetEquipModel( self.order, None )

	def addHardinessLimit( self, hardiness, owner = None ):
		"""
		���ӵ�ǰװ��������;ö�

		@param hardiness: �;�ֵ
		@type  hardiness: UINT16
		@return: ��
		"""
		self.setHardinessLimit( self.getHardinessLimit() + hardiness, owner )

	def setHardinessLimit( self, hardiness, owner = None ):
		"""
		���õ�ǰװ�����;ö�����
		���������owner��ΪNone���򲻻��������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param hardiness: �;�ֵ
		@type  hardiness: UINT16
		@return: ��
		"""
		hardinessMax = self.getHardinessMax()
		oldHardinessLimint = self.getHardinessLimit()
		if hardiness > hardinessMax:
			hardiness = hardinessMax
		if hardiness < 0:
			hardiness = 0
		self.set( "eq_hardinessLimit", int( hardiness ), owner )

		if owner is None:
			DEBUG_MSG( "None Owner set %s [%i] eq_hardinessLimit from %i to %i" % ( self.name(), self.uid, oldHardinessLimint, int( hardiness ) ) )
		else:
			DEBUG_MSG( "%s [%i] set %s [%i] eq_hardinessLimit from %i to %i" % ( owner.getName(), owner.id, self.name(), self.uid, oldHardinessLimint, int( hardiness ) ) )

		# �����ǰ�;öȴ��ڵ�ǰ�;ö�����
		# ǿ������ڵ�ǰ�;ö�����
		if self.getHardiness() > hardiness:
			self.setHardiness( hardiness, owner )

	def getIntensifyLevel( self ):
		"""
		��ȡװ��ǿ���ȼ�
		"""
		return self.query( "eq_intensifyLevel", 0 )
	
	def model( self ):
		"""
		��ȡģ�ͱ��
		"""
		try:
			modelList = self.srcData["model"].split(";")
			model = modelList[0]
			if self.getIntensifyLevel() >= 5 and len( modelList ) > 1:
				model = modelList[1] if modelList[1] else model
			if self.getIntensifyLevel() >= 8 and len( modelList ) > 2 :
				model = modelList[2] if modelList[2] else model
			return int ( model )
		except:
			return 0

	def addIntensifyLevel( self, intensifyLevel, owner = None ):
		"""
		���ӵ�ǰװ�����;ö�
		@param hardiness: �;�ֵ
		@type  hardiness: UINT16
		@param    owner: װ��ӵ����
		@type     owner: Entity
		@return: ��
		"""
		self.setIntensifyLevel( self.getIntensifyLevel() + intensifyLevel,  owner )

	def setIntensifyLevel( self, intensifyLevel, owner = None ):
		"""
		����װ��ǿ���ȼ�
		virtual method
		@param intensifyLevel: ǿ���ȼ�
		@type  intensifyLevel: bool
		@param    owner: װ��ӵ����
		@type     owner: Entity
		@return:    ��
		"""
		# ǿ��Ӱ���������Ʒ�ʱ���
		oldLevel = self.getIntensifyLevel()
		if oldLevel == intensifyLevel: return
		# ����ǿ���ȼ�
		self.set( "eq_intensifyLevel", intensifyLevel, owner )
		#������С��Ƶ���������
		wieldType = self.query( "eq_wieldType" )
		if EIA_DATA.has_key( intensifyLevel ) and EIA_DATA[intensifyLevel].has_key( wieldType ): #��ʼ��������
			attrInfo = EIA_DATA[intensifyLevel][wieldType]
			level = self.getLevel()
			if attrInfo[0] > 0:
				self.set( "eq_ReduceRoleD", attrInfo[0], owner )
			if attrInfo[1] > 0:
				self.set( "eq_AddRoleD", attrInfo[1], owner )
		else:
			self.set( "eq_ReduceRoleD", 0.0, owner )
			self.set( "eq_AddRoleD",    0.0, owner )

	def setQuality( self, quality, owner = None ):
		"""
		���ø���Ʒ��Ʒ��
		��Ʒ��Ʒ�ʸı�ֱ�ӵ���
		��������Ʒ�ʱ��ʺ͸�������Ʒ�ʱ��ʵĸı�
		@param    quality: ��ƷƷ��
		@type     quality: INT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		# �����������Ʒ�ʱ���
		oldQuality = self.getQuality()
		if oldQuality == quality: return

		prefix = self.getPrefix()
		

		# �����������Ʒ�ʱ���
		newQBaseRate = g_itemQualityExp.getBaseRateByQuality( quality, prefix )
		self.setBaseRate( newQBaseRate, owner )

		# ���㸽������Ʒ�ʱ���
		newExcRate = g_itemQualityExp.getexcRateByQandP( quality, prefix )
		self.setExcRate( newExcRate, owner )

		# ����Ʒ��
		CItemBase.setQuality( self, quality, owner )

		# ���¼����;ö�
		self.CalculateHardiness( owner )

		# ˢ�¼۸�
		self.updatePrice( owner )

	def setPrefix( self, prefix, owner = None ):
		"""
		���ø���Ʒ��ǰ׺
		��Ʒ��ǰ׺�ı�ֱ�ӵ��¸�������Ʒ�ʱ��ʵĸı�
		���¹�����ʾǰ׺�ĸı��Ӱ����ɫװ���Ļ�������Ʒ�ʱ���
		@param    prefix: ��Ʒǰ׺
		@type     prefix: INT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return None
		"""
		# ���¼����;ö�
		self.CalculateHardiness( owner )

		# ˢ�¼۸�
		self.updatePrice( owner )

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

	def getMagicPower( self ):
		"""
		��ȡħ��������
		"""
		return self.query( "eq_magicPower", 0 )

	def getSlot( self ):
		"""
		��ȡװ����ʹ�ÿ���
		"""
		return self.query( "eq_slot", 0 )

	def getLimitSlot( self ):
		"""
		��ȡװ����ǰӵ�п���
		"""
		return self.query( "eq_limitSlot", 0 )

	def getMaxSlot( self ):
		"""
		��ȡ��װ�������ӵ�еĿ���
		"""
		return self.query( "eq_maxSlot", 0 )

	def setLimitSlot( self, slotAmount, owner = None ):
		"""
		���õ�ǰװ��ӵ�п���
		@param    slotAmount: װ������
		@type     slotAmount: UINT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return:    ��
		"""
		self.set( "eq_limitSlot", slotAmount, owner )

	def setSlot( self, slotAmount, owner = None ):
		"""
		���õ�ǰװ������Ƕ����
		@param    slotAmount: װ������
		@type     slotAmount: UINT8
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return:    ��
		"""
		self.set( "eq_slot", slotAmount, owner )

	def updataHardiness( self, value, owner = None ):
		"""
		�����;öȵ�ֵ
		"""
		self.set( "eq_hardinessMax",   int( value ), owner )
		self.set( "eq_hardinessLimit", int( value ), owner )
		self.set( "eq_hardiness",      int( value ), owner )

	def CalculateHardiness( self , owner ):
		"""
		�����;ö�(Ʒ�ʸı�ʱҪ���¼����;ö�)
		"""
		pass

	def getExtraEffect( self ):
		"""
		��ȡװ����������
		@return:    dict
		"""
		return self.query( "eq_extraEffect", {} )

	def getCreateEffect( self ):
		"""
		��ȡװ����ע����
		@return:    dict
		"""
		return self.query( "eq_createEffect", [] )
		
	# ��ȡװ�����ѹ�ע������ by mushuang
	# @return type:[] �����������Ѿ���ע���Ե��б�
	def getPouredCreateEffect( self ):
		res = []
		for effect in self.query( "eq_createEffect", [] ):
			if effect != ( 0, 0 ):
				res.append( effect )
		return res

	def addCreateEffect( self, effect, owner = None ):
		"""
		��ӹ�ע����
		"""
		oldEffect = self.getCreateEffect()
		oldEffect.extend( effect )
		self.setCreateEffect( oldEffect, owner )

	def setCreateEffect( self, effect, owner = None ):
		"""
		���ù�ע����
		"""
		self.set( "eq_createEffect", effect, owner )

	def createRandomEffect( self, owner = None ):
		"""
		����װ�����������
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return Bool
		"""
		itemKey = self.id
		quality = self.getQuality()
		level = self.getLevel()
		type = self.getType()
		datas = {}
		if quality != ItemTypeEnum.CQT_WHITE:
			if not self.getExtraEffect():
				datas = g_itemPropAttrExp.getEquipRandomEffect( itemKey, level, type, quality )
		# ��ȡ�������ʧ��
		if not datas: return False
		randomEffect = datas["dic"]
		
		self.set( "eq_extraEffect", randomEffect, owner )
		return True

	def fixedCreateRandomEffect( self, quality, owner = None, suitEffect = False ):
		"""
		���ݹ̶���ǰ׺ Ʒ�� ����ǰ׺ ������Ʒ���������
		@param quality: Ʒ��
		@type  quality: INT
		@param prefix: ǰ׺
		@type  prefix: INT
		@param proPrefixID: ����ǰ׺
		@type  proPrefixID: INT
		@param owner: װ��ӵ����
		@type  owner: Entity
		@param suitEffect: �Ƿ������װ����
		@type  suitEffect: BOOL
		@return Bool
		"""
		datas = {}
		if not self.getExtraEffect():
			datas = g_itemPropAttrExp.getEquipRandomEffect( self.id, self.getLevel(), self.getType(), quality )
		# ��ȡ�������ʧ��
		if not datas: return False
		randomEffect = datas["dic"]
		
		self.set( "eq_extraEffect", randomEffect, owner )
		return True

	def isEquip( self ):
		"""
		virtual method.
		�ж��Ƿ���װ��
		"""
		return True

	def canRepair( self ):	# wsf add,15:30 2008-7-2
		"""
		virtual method.
		�ж�һ����Ʒ�Ƿ��ܱ�����
		@return: BOOL
		@rtype:  BOOL
		"""
		if not CItemBase.canRepair( self ): return False
		hMax = self.query( "eq_hardinessMax" )
		if hMax is None or hMax <= 0: return False
		return self.query("eq_hardinessLimit") > 0

	def setIntensifyValue( self, value, owner = None ):
		"""
		����װ����ǿ������ֵ����
		"""
		self.set( "intensifyValue", value, owner )

	def getIntensifyValue( self ):
		"""
		��ȡװ����ǿ������ֵ����

		@rtype : [ [ ǿ������������, ǿ����ħ�������� ], [ ǿ�����������ֵ, ǿ����ħ������ֵ ] ]
		"""
		return self.query( "intensifyValue", [ [ 0, 0 ], [ 0, 0 ] ] )

	def updatePrice( self, owner = None ):
		"""
		ˢ����Ʒ�ļ۸�
		����һЩ������Ʒ�۸�Ĳ����ı䣬�۸�Ҳ����Ӧ�ı���
		����װ���Ļ�������Ʒ�ʱ��ʲ��ǹ̶��ģ���ô�۸�Ҳ��������Ӧ�ı䶯
		װ������дװ����ϵͳװ��������ϵͳװ��Ʒ�ʣ�ǰ׺��ǿ���ȼ��ı��Ӱ���������Ʒ�ʱ��ʺ͸�������Ʒ�ʱ���
			1��ϵͳװ��( ��Ʒ�ʣ�ǰ׺��ǿ���ȼ�Ӱ��)��ı�۸�
			2����дװ��(ֻ��ǿ���ȼ�Ӱ��)��ı�۸�

		���㹫ʽΪ:
		��ֵ���� = ��Ʒ���������� * 1.82*��7.5*��2*�ȼ�*��������Ʒ�ʱ��ʣ�^1.54+���ȼ�^1.5*2.5+60��*��������Ʒ�ʱ��ʣ�
		�۸� = ��Ʒ����������*�����ߵȼ�^2*��������Ʒ�ʱ���+��ֵ����/3��
		"""
		# ��ȡ��Ʒ������������
		typeAmend = g_typeAmend.getGeneAmend( self.getType() )
		# ��ȡ��Ʒ�ĵȼ�
		level = self.getLevel()
		# ��ȡ��Ʒ�Ļ�������Ʒ�ʱ���( װ��ǿ�����Ӱ���ֵ )
		baseQualityRate = self.getBaseRate()
		# ��ȡ��Ʒ�ĸ�������Ʒ�ʱ���( ��Ʒ�ʺ�ǰ׺�й�)
		excQualityRate = self.getExcRate()
		# ������Ʒ�ļ�ֵ����
		priceGene = typeAmend * 1.82 * ( 7.5 * ( 2 * level * excQualityRate ) ** 1.54 + ( level ** 1.5 * 2.5 + 60 ) * excQualityRate )
		# ������Ʒ�ļ۸�
		price = typeAmend * ( level**2*baseQualityRate ) + priceGene/3
		self.setPrice( price, owner )

	def getPrice( self ):
		"""
		��ȡװ���ļ۸�
		���;ö��й�
		"""
		# װ���ļ۸� = ��ǰ�;ö�/ԭʼ����;ö�*װ��ԭʼ����۸�
		basePrice = self.getRecodePrice()
		hardinessMax = self.getHardinessMax()
		if hardinessMax == 0: return basePrice
		newPrice = int( self.getHardiness() * 1.0 / self.getHardinessMax() * basePrice )
		if newPrice <= 0: return 1
		return newPrice
	
	# ----------------------------------------------------------------
	# ����װ�������ߵ�����
	# ----------------------------------------------------------------
	def setQualityUpper( self, name, owner ) :
		"""
		@name(string): װ�������ߵ�����
		@owner: װ���ĳ�����
		"""
		self.set( "eq_upper", name, owner )
		
	# ----------------------------------------------------------------
	# װ���������� by mushuang
	# ----------------------------------------------------------------
	def attrRebuild( self, attrType, effectId, owner = None):		
		
		# ��ȡװ���ġ���ֵ���ӡ�
		priceGeneMin = g_itemPropAttrExp.getItemPriceGene( self.id, self.getLevel(), self.getType(), self.getQuality(), ItemTypeEnum.CPT_FABULOUS ) # ��˵��װ
		priceGeneMax = g_itemPropAttrExp.getItemPriceGene( self.id, self.getLevel(), self.getType(), self.getQuality(), ItemTypeEnum.CPT_MYGOD ) # ������װ
		
		# ���ÿ�����Եļ�ֵ����
		attrGeneMin = priceGeneMin * csconst.EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR
		attrGeneMax = priceGeneMax * csconst.EQUIP_ATTR_REBUILD_PER_ATTR_FACTOR
		
		
		genePerPoint = g_equipEffect.getPerGene( effectId )
		if genePerPoint == 0 : return False# ����id��Чʱ�᷵��0
		
		# ������Գ�ʼֵ
		minValue = attrGeneMin / genePerPoint
		
		# ����������ֵ
		maxValue = attrGeneMax / genePerPoint

		# ���㲽��
		step = ( maxValue - minValue ) / csconst.EQUIP_ATTR_REBUILD_STAGES
		
		# �������ʲ����ݸ��ʵõ��״�
		chance = random.random()
		for i in xrange( csconst.EQUIP_ATTR_REBUILD_STAGES -1 , -1, -1):
			if chance > attrRebuildProb[ i ]: 
				n = i + 1
				break
		
		# ���ݽ״Σ���������ʼֵ�����µ�����ֵ
		newValue = minValue + n * step
		
		# if �µ�����ֵ > ���ֵ
		if newValue > maxValue:
			# �µ�����ֵ = ���ֵ
			newValue = maxValue
		
		#��������������֣���ֵ����ȡ�����ӳɲ��� by cxm 2010.10.13
		type = g_equipEffect.getType( effectId )
		if type == ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD:
			maxValue = int( maxValue )
			newValue = int( newValue )
		
		# �����µ�����ֵ
		if attrType == "eq_extraEffect": # ��������
			extraEffect = self.query( "eq_extraEffect" ) # {k:v}
			if not effectId in extraEffect : return False
			
			# if �������Ѿ��������ֵ : return
			if extraEffect[effectId] >= maxValue : return False
			
			extraEffect[effectId] = newValue
			self.set( "eq_extraEffect", extraEffect, owner )
			return True
			
		elif attrType == "eq_createEffect": # ��ע����
			createEffect = self.query( "eq_createEffect" ) # [(k,v)]
			# �жϸù�ע�����Ƿ����
			idx = -1
			for ( k, v ) in createEffect:
				if k == effectId :
					idx = 	createEffect.index( ( k ,v ) )
					break
			
			
			# if �����Բ����� : return
			if idx == -1 : return False
			
			# if �������Ѿ��������ֵ : return
			if createEffect[idx][1] >= maxValue : return False
			
			# �����µ�ֵ
			createEffect[idx] = ( effectId, newValue )
			self.set( "eq_createEffect", createEffect, owner )
			return True
			
		elif attrType == "eq_suitEffect": # ��װ����
			suitEffect = self.query( "eq_suitEffect" ) # { k:v }
			if not effectId in suitEffect : return False
			
			# if �������Ѿ��������ֵ : return
			if suitEffect[effectId] >= maxValue : return False
				
			suitEffect[effectId] = newValue
			self.set( "eq_suitEffect", suitEffect, owner )
			return True
		
		return False
		
	
	def removeAllPrefix( self, player = None ):
		"""
		�Ƴ�װ���ĸ���ǰ׺��Ŀǰ����Ϊ��װ��ǰ׺������ǰ׺��
		@player: ���player����None����ô�˴�״̬���½������ͻ���
		"""	
		CItemBase.setPrefix( self, ItemTypeEnum.CPT_NONE, player )
		self.set( "propertyPrefix", "", player )
#
# $Log: not supported by cvs2svn $
# Revision 1.32  2008/08/13 08:55:17  qilan
# ��Ƕ��Ϊ�����������ͬ����ˮ������Ӧ����
#
# Revision 1.31  2008/07/17 02:33:18  yangkai
# �����ж�һ��װ���Ƿ���װ�����Ƿ���������ж�
#
# Revision 1.30  2008/07/02 07:36:18  wangshufeng
# add method:canRepair,�ж�һ����Ʒ�Ƿ��ܱ�����
#
# Revision 1.29  2008/05/30 03:03:14  yangkai
# װ������������Ĳ����޸�
#
# Revision 1.28  2008/04/22 10:46:13  yangkai
# no message
#
# Revision 1.27  2008/04/10 07:44:44  yangkai
# ���� createRandomEffect ���Ĭ�ϲ��� owner
#
# Revision 1.26  2008/04/03 08:57:49  yangkai
# �����Ƕ���ԵĴ���
#
# Revision 1.25  2008/04/03 08:26:27  yangkai
# ��ӽӿ�createRandomEffect
#
# Revision 1.24  2008/04/03 02:07:53  yangkai
# ����װ����Ƕ����ؽӿ�
#
# Revision 1.23  2008/04/01 00:44:36  yangkai
# ���װ�������ؽӿ�
#
# Revision 1.22  2008/03/29 08:37:28  yangkai
# װ��ǿ������
#
# Revision 1.21  2008/03/24 02:29:09  yangkai
# 1����ӽӿ� isGreen����
# 2�������װ����
#
# Revision 1.20  2008/03/18 07:39:55  yangkai
# reqlevel rename to reqLevel
#
# Revision 1.19  2008/03/15 08:17:53  yangkai
# no message
#
# Revision 1.18  2008/02/28 02:30:35  yangkai
# �޸Ĵ�����Чʱ����
#
# Revision 1.17  2008/02/22 08:16:31  yangkai
# no message
#
# Revision 1.16  2008/02/22 01:36:25  yangkai
# ��Ӷ�װ���������Ե�֧��
#
# Revision 1.15  2008/02/19 08:32:34  yangkai
# ȥ�����õĳ�ʼ��set��Ϣ
#
# Revision 1.14  2007/12/28 01:14:20  yangkai
# ��ʼ����ǿ���ȼ�Ϊ0
#
# Revision 1.13  2007/12/14 09:13:14  yangkai
# ����װ��ְҵ�ж�
#
# Revision 1.12  2007/11/24 03:06:44  yangkai
# ��Ʒϵͳ���������Ը���
# ��ǰ�;ö�"endure" -- > "eq_hadriness"
# ����;ö�"currEndureLimit" --> "eq_hardinessLimit"
# ����;ö�����"maxEndureLimit" --> "eq_hardinessMax"
#
# Revision 1.11  2007/11/08 06:20:57  yangkai
# ���ӽӿڣ�
# - intensify()
#
# Revision 1.10  2007/08/23 01:30:36  kebiao
# ���װ���޸�
#
# Revision 1.9  2007/08/15 07:52:28  yangkai
# �޸�:
#     - ���������޸�
#     - ����װ��/ж�º�������
#
# Revision 1.8  2007/08/15 04:01:07  kebiao
# ���װ��
#
# Revision 1.7  2007/06/14 09:55:52  huangyongwei
# �ᶯ�˺궨��
#
# Revision 1.6  2007/05/17 09:12:50  huangyongwei
# ԭ���� ItemBagRole �е������
# KB_COUNT
# KB_EQUIP_ID
# KB_COMMON_ID
# ���ƶ���
# L3Define ��
#
#
# ItemBagRole.ItemBagRole.KB_EQUIP_ID
# --->
# csdefine.KB_EQUIP_ID
#
# Revision 1.5  2006/12/29 07:31:15  panguankong
# ����ж�װ���ӿ�
#
# Revision 1.4  2006/10/16 10:00:55  phw
# method modified:
#     wield()
#     unwield()
#     ��װ�Ϻ�ж��װ��ʱ�����˶��Ƿ��б����ĺ�װ���йصļ����жϡ�
#
# Revision 1.3  2006/08/18 07:00:18  phw
# ɾ���ӿڣ�
#     description(); Ϊ�˱����Ժ󲻱�Ҫ�Ĳ²⣬ɾ������Ҫ�Ľӿ�
#
# Revision 1.2  2006/08/11 02:57:34  phw
# ���Ը������޸�����itemInstance.keyName��itemInstance.id()ΪitemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
