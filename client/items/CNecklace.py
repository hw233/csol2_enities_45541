# -*- coding: gb18030 -*-

# $Id: CNecklace.py,v 1.6 2008-05-17 11:42:42 huangyongwei Exp $


import math
import csdefine
import csconst
import Const
import ItemAttrClass
import ItemTypeEnum
import BigWorld

from bwdebug import *
from COrnament import COrnament
from ItemSystemExp import ItemTypeAmendExp
from ItemSystemExp import EquipIntensifyExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from config.client.labels.items import lbs_CNecklace
from EquipHelper import calcIntensifyInc, calcObeyInc, calcTotal
from ItemSystemExp import EquipExp

class CNecklace( COrnament ):
	"""
	项链
	"""
	def __init__( self, srcData ):
		COrnament.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取项链专有描述信息
		"""
		COrnament.getProDescription( self, reference )
		# 基础属性
		attributeDes = []

		exp = EquipExp( self, reference )
		
		# 物理防御总值
		totalPArmor = calcTotal( exp.getArmorBase )
		# 法术防御总值
		totalSArmor = calcTotal( exp.getMagicArmorBase )
		# 降低对方法术命中总值
		totalTMagicHitValue = calcTotal( exp.getReduceTargetMagicHit )

		# 装备强化附加属性
		intenPArmorValue = 0
		intenPArmorDes = ""
		intenSArmorValue = 0
		intenSArmorDes = ""
		intenTMagicHitDes = ""
		intensify = self.getIntensifyLevel()
		if intensify != 0:
			# 强化附加物理防御值
			intenPValue = calcIntensifyInc( exp.getArmorBase )
			intenPArmorDes = "+%i" % intenPValue
			intenPArmorDes = PL_Font.getSource( intenPArmorDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加法术防御值
			intenSValue = calcIntensifyInc( exp.getMagicArmorBase )
			intenSArmorDes = "+%i" % intenSValue
			intenSArmorDes = PL_Font.getSource( intenSArmorDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加降低对方法术命中点数
			if totalTMagicHitValue:
				intenTMagicHitValue = calcIntensifyInc( exp.getReduceTargetMagicHit )
				intenTMagicHitDes = "+%i" % intenTMagicHitValue
				intenTMagicHitDes = PL_Font.getSource( intenTMagicHitDes, fc = Const.EQUIP_INTENSIFY_COLOR )
				
		# 灵魂锁链绑定
		addPArmorDes = ""
		addSArmorDes = ""
		addTMagicHitDes = ""
		if self.isObey():
			# 灵魂绑定附加物理防御值
			addPArmorValue = calcObeyInc( exp.getArmorBase )
			addPArmorDes = "+%i" % addPArmorValue
			addPArmorDes = PL_Font.getSource( addPArmorDes, fc = "c7" )
			if addPArmorValue < 1.0: addPArmorDes = ""
			# 灵魂绑定附加法术防御值
			addSArmorValue = calcObeyInc( exp.getMagicArmorBase )
			addSArmorDes = "+%i" % addSArmorValue
			addSArmorDes = PL_Font.getSource( addSArmorDes, fc = "c7" )
			if addSArmorValue < 1.0: addSArmorDes = ""
			# 灵魂绑定附加降低对方法术命中
			if totalTMagicHitValue:
				addTMagicHitValue = calcObeyInc( exp.getReduceTargetMagicHit )
				addTMagicHitDes = "+%i" % addTMagicHitValue
				addTMagicHitDes = PL_Font.getSource( addTMagicHitDes, fc = "c7" )
				if addTMagicHitValue < 1.0: addTMagicHitDes = ""

		# 物理防御
		desPArmor = lbs_CNecklace[1] % totalPArmor
		if len( intenPArmorDes ) or len( addPArmorDes ):
			hasInf = ""
			hasObe = ""
			if len( intenPArmorDes ): hasInf = lbs_CNecklace[2]
			if len( addPArmorDes ): hasObe = lbs_CNecklace[3]
			des = PL_Font.getSource( desPArmor, fc = "c4" )
			desPArmor = "%s(%s%s)" % ( des, hasInf + intenPArmorDes, hasObe + addPArmorDes )
		attributeDes.append( desPArmor )

		# 法术防御
		desSArmor = lbs_CNecklace[4] % totalSArmor
		if len( intenSArmorDes ) or len( addSArmorDes ):
			hasInf = ""
			hasObe = ""
			if len( intenSArmorDes ): hasInf = lbs_CNecklace[2]
			if len( addSArmorDes ): hasObe = lbs_CNecklace[3]
			des = PL_Font.getSource( desSArmor, fc = "c4" )
			desSArmor = "%s(%s%s)" % ( des, hasInf + intenSArmorDes, hasObe + addSArmorDes )
		attributeDes.append( desSArmor )

		# 降低对方法术命中
		if totalTMagicHitValue:
			desTMagicHit = lbs_CNecklace[5] % totalTMagicHitValue
			if len( intenTMagicHitDes ) or len( addTMagicHitDes ):
				hasInf = ""
				hasObe = ""
				if len( intenTMagicHitDes ): hasInf = lbs_CNecklace[2]
				if len( addTMagicHitDes ): hasObe = lbs_CNecklace[3]
				des = PL_Font.getSource( desTMagicHit, fc = "c4" )
				desTMagicHit = "%s(%s%s)" % ( des, hasInf + intenTMagicHitDes, hasObe + addTMagicHitDes )
			attributeDes.append( desTMagicHit )

		self.desFrame.SetDesSeveral( "Attribute", attributeDes )
