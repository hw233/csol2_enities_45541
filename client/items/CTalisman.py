# -*- coding: gb18030 -*-

import skills
import ItemTypeEnum
import ItemAttrClass

from gbref import rds
from CEquip import CEquip
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CTalisman
import Const
from ItemSystemExp import TalismanExp
g_talisman = TalismanExp.instance()

class CTalisman( CEquip ):
	"""
	����-�̳�װ��
	"""
	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )

	def getExp( self ):
		"""
		��ȡ������ǰ����ֵ
		"""
		return self.query( "tm_exp", 0 )

	def getMaxExp( self ):
		"""
		��÷������������ֵ
		"""
		return rds.talismanEffects.getMaxExp(self.getLevel())

	def getPotential( self ):
		"""
		��ȡ������ǰǱ��ֵ
		"""
		return self.query( "tm_potential", 0 )

	def getMaxPotential( self ):
		"""
		��÷����������Ǳ��ֵ
		"""
		if 0 == self.getSkillLevel():
			return 0
		return rds.talismanEffects.getPotential(self.getSkillLevel())

	def getSkillLevel( self ):
		"""
		��÷������ܵĵȼ�
		"""
		return 	self.query( "spell", 0 ) % 1000

	def getGrade( self ):
		"""
		��ȡ������Ʒ��
		"""
		return self.query( "tm_grade", ItemTypeEnum.TALISMAN_COMMON )

	def getBaseEffect( self ):
		"""
		��ȡ�����Ļ�������
		"""
		return self.query("tm_baseEffect", {} )

	def getCommonEffect( self ):
		"""
		��ȡ�����ķ�Ʒ����
		"""
		return self.query( "tm_commonEffect", [] )

	def getImmortalEffect( self ):
		"""
		��ȡ��������Ʒ����
		"""
		return self.query( "tm_immortalEffect", [] )

	def getFlawEffect( self ):
		"""
		��ȡ��������������
		"""
		return self.query( "tm_flawEffect", {} )

	def getDeityEffect( self ):
		"""
		��ȡ��������Ʒ����
		"""
		return self.query( "tm_deityEffect", [] )

	def getSkillID( self ):
		"""
		��ȡ����ID
		"""
		return 	self.query( "spell", 0 )

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡ��Ʒר��������Ϣ
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		
		#����Ʒ��
		grade = attrMap["tm_grade"].description( self, reference )
		self.desFrame.SetDescription( "tm_grade", grade )

		# װ��ǿ����������
		intensify = self.getIntensifyLevel()
		addQualityRate = g_talisman.getIntensifyRate( self.getGrade(), intensify )
		addBaseRate = 1.0 + addQualityRate

		# ��������������Ϣ
		desBaseEffect1 = attrMap["eq_extraEffect"].description( self, reference )
		self.desFrame.SetDescription( "eq_extraEffect", desBaseEffect1 )

		# Ʒ������
		tmEffect = []
		tmDes = []
		commonEffect = self.getCommonEffect()
		immortalEffect = self.getImmortalEffect()
		deityEffect = self.getDeityEffect()
		tmEffect.extend( [( PL_Font.getSource( lbs_CTalisman[1], fc = "c7" ), "tm_temp" )] )
		tmEffect.extend( commonEffect )
		tmEffect.extend( [( PL_Font.getSource( lbs_CTalisman[2], fc = "c6" ), "tm_temp" )] )
		tmEffect.extend( immortalEffect )
		tmEffect.extend( [( PL_Font.getSource( lbs_CTalisman[3], fc = "c8" ), "tm_temp" )] )
		tmEffect.extend( deityEffect )

		for key, state in tmEffect:
			if state == "tm_temp":
				tmDes.append( [key] )
				continue
			effectKey = rds.talismanEffects.getEffectID( key )
			effectClass = rds.equipEffects.getEffect( effectKey )
			if effectClass is None: continue
			initEffectValue = rds.talismanEffects.getInitValue( key )
			param = rds.talismanEffects.getUpParam( key )
			value = initEffectValue + self.getLevel() * param
			intenDes =  ""
			if intensify != 0 and state == True:
				addVal = value * addQualityRate
				intenDes = "+%i" % ( addVal )
				intenDes = "(" + lbs_CTalisman[6] + PL_Font.getSource( intenDes, fc = Const.EQUIP_INTENSIFY_COLOR ) + ")"
				value += addVal
			des = effectClass.descriptionList( value )
			if state: colour = "c4"
			else: colour = "c9"
			desList = [PL_Font.getSource( des[0] + des[1], fc = colour ), intenDes]
			tmDes.append( desList )

		# ��Ʒ����
		if len( tmDes ):
			self.desFrame.SetDesSeveral( "tm_extraEffect", tmDes )

		# ��������
		flawDes = []
		flawEffect = self.getFlawEffect()
		if len( flawEffect ):
			flawDes.append( [PL_Font.getSource( lbs_CTalisman[7], fc = ( 0, 255, 0 ) )] )
			for key, value in flawEffect.iteritems():
				effectClass = rds.equipEffects.getEffect( key )
				if effectClass is None: continue
				desFlawEffect = effectClass.description( value )
				flawDes.append( [PL_Font.getSource( desFlawEffect , fc = ( 0, 255, 0 ) )] )
		if len( flawDes ):
			self.desFrame.SetDesSeveral( "tm_flawEffect", flawDes )

		# �����ļ�����Ϣ
		skillID = self.getSkillID()
		if skillID:
			tmSkill = skills.getSkill( skillID )
			skname = tmSkill.getName()
			des = lbs_CTalisman[4] % skname
			des = PL_Font.getSource( des, fc = "c8" )
			self.desFrame.SetDescription( "tm_skillName", des )
			sklevel = tmSkill.getLevel()
			des = lbs_CTalisman[5] % sklevel
			des = PL_Font.getSource( des, fc = "c8" )
			self.desFrame.SetDescription( "tm_skillLevel", des )

		CEquip.getProDescription( self, reference )
		self.getLevelDescription( reference )

	def getLevelDescription( self, reference ):
		"""
		�����ȼ�
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		level = attrMap["level"].description( self, reference )
		self.desFrame.SetDescription( "itemLevel", level )
