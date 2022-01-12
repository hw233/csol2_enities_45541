# -*- coding: gb18030 -*-

# $Id: CWeapon.py,v 1.9 2008-05-17 11:42:42 huangyongwei Exp $


import math
import csconst
import Const
import ItemTypeEnum
import ItemAttrClass

from bwdebug import *
from CEquip import CEquip
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import EquipQualityExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CWeapon
from config.client.labels.items import lbs_CItemBase
from config.client.labels.items import lbs_CEquip
from skills import getSkill
from ItemSystemExp import EquipExp
from EquipHelper import *

g_equipIntensify = EquipIntensifyExp.instance()
g_equipQualityExp = EquipQualityExp.instance()

class CWeapon( CEquip ):
	"""
	������

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def wield( self, who, update = True ):
		"""
		װ������

		@param    who: ����ӵ����
		@type     who: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		if not CEquip.wield( self, who, update ):
			return False

		return True

	def unWield( self, who, update = True ):
		"""
		ж��װ��

		@param    who: ����ӵ����
		@type     who: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		if not self.isAlreadyWield(): return	# ���û��װ��Ч������unwield

		CEquip.unWield( self, who, update )

	def getGodWeaponSkillID( self ):
		"""
		��ȡ�������Լ���ID
		"""
		return self.query( "param1", 0 )

	def fullName( self ):
		"""
		��ȡ��Ʒ��ȫ�� �� ��ӥ������İ�����
		"""
		nameDes = self.name()
		proName = self.query( "propertyPrefix")
		if proName: nameDes = proName + nameDes
		prefix = self.query( "prefix" )
		excName = g_equipQualityExp.getName( prefix )
		if excName != "": nameDes = excName + nameDes
		if self.getGodWeaponSkillID() > 0:
			nameDes = lbs_CEquip[14] + nameDes
		return nameDes

	def getQualityColor( self ) :
		"""
		��ȡƷ����ɫ
		"""
		if self.getGodWeaponSkillID() > 0:
			return csconst.GOD_WEAPON_NAME_COLOR
		return g_equipQualityExp.getColorByQuality( self.getQuality() )

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡ����ר��������Ϣ
		"""
		CEquip.getProDescription( self, reference)

		exp =  EquipExp( self, reference )

		# ע��������������������﹥��ֵ��ͻ�������΢�������������ʽ�ж���˵ڶ����� by mushuang
		# ��������������
		totalDamage = calcTotal( exp.getDPSValue ) + exp.getIntensifyDamageInc()
		# �����ķ���������
		if ItemTypeEnum.ITEM_WEAPON_STAFF:
			# ��������ǿ��������������ֵ
			totalMagicDamage = calcTotal( exp.getMagicDamageValue ) + exp.getIntensifyMagicDamageInc()
		else:
			totalMagicDamage = calcTotal( exp.getMagicDamageValue )

		# ǿ����������
		intenDamageDes = ""
		intenMagicDes = ""
		intensify = self.getIntensifyLevel()
		if intensify != 0:
			# ǿ��������������
			# ע��������������������﹥��ֵ��ͻ�������΢�������������ʽ�ж���˵ڶ����� by mushuang
			intenDamageValue = calcIntensifyInc( exp.getDPSValue ) + exp.getIntensifyDamageInc()
			intenDamageDes = "+%i" % intenDamageValue
			intenDamageDes = PL_Font.getSource( intenDamageDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӷ���������
			if ItemTypeEnum.ITEM_WEAPON_STAFF:
				# ��������ǿ���󸽼�ֵ
				intenMagicValue = calcIntensifyInc( exp.getMagicDamageValue ) + exp.getIntensifyMagicDamageInc()
			calcIntensifyInc( exp.getMagicDamageValue )
			intenMagicDes = "+%i" % intenMagicValue
			intenMagicDes = PL_Font.getSource( intenMagicDes, fc = Const.EQUIP_INTENSIFY_COLOR )

		# ��������󶨸�������
		addDamageDes = ""
		addMagicDes = ""
		if self.isObey():
			# �������������������
			addDamageValue = calcObeyInc( exp.getDPSValue )
			addDamageDes = "+%i" % addDamageValue
			addDamageDes = PL_Font.getSource( addDamageDes, fc = "c7" )
			if addDamageValue < 1.0: addDamageDes = ""
			# ����������ӷ���������
			addMagicValue = calcObeyInc( exp.getMagicDamageValue )
			addMagicDes = "+%i" % addMagicValue
			addMagicDes = PL_Font.getSource( addMagicDes, fc = "c7" )
			if addMagicValue < 1.0: addMagicDes = ""

		# ������
		desDps = ""
		if totalDamage:
			desDps = lbs_CWeapon[1] % totalDamage
			if len( addDamageDes ) or len( intenDamageDes ):
				hasInf = ""
				hasObe = ""
				if len( intenDamageDes ): hasInf = lbs_CWeapon[2]
				if len( addDamageDes ): hasObe = lbs_CWeapon[3]
				des = PL_Font.getSource( desDps, fc = "c4" )
				desDps = "%s(%s%s)" % ( des, hasInf + intenDamageDes, hasObe + addDamageDes )

		# ��������
		desMgicP = ""
		if totalMagicDamage:
			desMgicP = lbs_CWeapon[4] % totalMagicDamage
			if len( addMagicDes ) or len( intenMagicDes ):
				hasInf = ""
				hasObe = ""
				if len( intenMagicDes ): hasInf = lbs_CWeapon[2]
				if len( addMagicDes ): hasObe = lbs_CWeapon[3]
				des = PL_Font.getSource( desMgicP, fc = "c4" )
				desMgicP = "%s(%s%s)" % ( des, hasInf + intenMagicDes, hasObe + addMagicDes )

		# �����Ļ������� (������ ,�������� ....)
		desAttribute = []
		if desDps: desAttribute.append( desDps )
		if desMgicP: desAttribute.append( desMgicP )
		self.desFrame.SetDesSeveral("Attribute" , desAttribute )

		# �������� ��������˵��
		skillID = self.getGodWeaponSkillID()
		if  skillID > 0:
			# gw = PL_Font.getSource( , fc = "c8" )
			desGW = PL_Font.getSource( lbs_CWeapon[5], fc = "c24" )
			skillInst = getSkill( skillID )
			desGWS = skillInst.getDescription()
			desGWS = PL_Font.getSource( desGWS, fc = "c24" )
			self.desFrame.SetDescription( "godweaponskill", desGW )
			self.desFrame.SetDescription( "godweaponskilldes", desGWS )