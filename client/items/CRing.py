# -*- coding: gb18030 -*-

# $Id: CRing.py,v 1.9 2008-05-17 11:42:42 huangyongwei Exp $

import math
import csconst
import ItemTypeEnum
import Const
import ItemAttrClass

from bwdebug import *
from COrnament import COrnament
from ItemSystemExp import EquipIntensifyExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from config.client.labels.items import lbs_CRing
from ItemSystemExp import EquipExp
from EquipHelper import *

g_equipIntensify = EquipIntensifyExp.instance()


class CRing( COrnament ):
	"""
	戒指
	"""
	def __init__( self, srcData ):
		COrnament.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取戒指专有描述信息
		"""
		COrnament.getProDescription( self, reference )

		exp = EquipExp( self, reference )
		param1 = int( self.query( "param1", 0 ) )

		# 武器的DPS (攻击力)
		# 注意这里，服务器对武器的物攻加值与客户端有略微区别，所以这个公式中多出了第二个项 by mushuang
		# 武器的法术攻击力
		if param1 == 0:
			# 0代表物理戒指
			totalDamage = calcTotal( exp.getDPSValue ) + exp.getIntensifyDamageInc()
			totalMagicDamage = calcTotal( exp.getMagicDamageValue )
		if param1 == 1:
			# 1代表法术戒指
			totalDamage = calcTotal( exp.getDPSValue )
			totalMagicDamage = calcTotal( exp.getMagicDamageValue ) + exp.getIntensifyMagicDamageInc()

		# 强化附加描述
		intenDamageDes = ""
		intenMagicDes = ""
		intensify = self.getIntensifyLevel()
		if intensify != 0:
			# 强化附加物理攻击力
			# 注意这里，服务器对武器的物攻加值与客户端有略微区别，所以这个公式中多出了第二个项 by mushuang
			if param1 == 0:
				# 0代表物理戒指
				intenDamageValue = calcIntensifyInc( exp.getDPSValue ) + exp.getIntensifyDamageInc()
				intenMagicValue = calcIntensifyInc( exp.getMagicDamageValue )
			if param1 == 1:
				# 1代表法术戒指
				intenDamageValue = calcIntensifyInc( exp.getDPSValue )
				intenMagicValue = calcIntensifyInc( exp.getMagicDamageValue ) + exp.getIntensifyMagicDamageInc()
			intenDamageDes = "+%i" % intenDamageValue
			intenDamageDes = PL_Font.getSource( intenDamageDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			intenMagicDes = "+%i" % intenMagicValue
			intenMagicDes = PL_Font.getSource( intenMagicDes, fc = Const.EQUIP_INTENSIFY_COLOR )

		# 灵魂锁链绑定附加描述
		addDamageDes = ""
		addMagicDes = ""
		if self.isObey():
			# 灵魂锁链附加物理攻击力
			addDamageValue = calcObeyInc( exp.getDPSValue )
			addDamageDes = "+%i" % addDamageValue
			addDamageDes = PL_Font.getSource( addDamageDes, fc = "c7" )
			if addDamageValue < 1.0: addDamageDes = ""
			# 灵魂锁链附加法术攻击力
			addMagicValue = calcObeyInc( exp.getMagicDamageValue )
			addMagicDes = "+%i" % addMagicValue
			addMagicDes = PL_Font.getSource( addMagicDes, fc = "c7" )
			if addMagicValue < 1.0: addMagicDes = ""

		# 物理攻击
		desDps = lbs_CRing[1] % totalDamage
		if len( addDamageDes ) or len( intenDamageDes ):
			hasInf = ""
			hasObe = ""
			if len( intenDamageDes ): hasInf = lbs_CRing[2]
			if len( addDamageDes ): hasObe = lbs_CRing[3]
			des = PL_Font.getSource( desDps, fc = "c4" )
			desDps = "%s(%s%s)" % ( des, hasInf + intenDamageDes, hasObe + addDamageDes )

		# 法术攻击
		desMgicP = lbs_CRing[4] % totalMagicDamage
		if len( addMagicDes ) or len( intenMagicDes ):
			hasInf = ""
			hasObe = ""
			if len( intenMagicDes ): hasInf = lbs_CRing[2]
			if len( addMagicDes ): hasObe = lbs_CRing[3]
			des = PL_Font.getSource( desMgicP, fc = "c4" )
			desMgicP = "%s(%s%s)" % ( des, hasInf + intenMagicDes, hasObe + addMagicDes )

		# 武器的基本属性 (物理攻击 ,法术攻击 ....)
		desAttribute = []
		if desDps: desAttribute.append( desDps )
		if desMgicP: desAttribute.append( desMgicP )
		self.desFrame.SetDesSeveral("Attribute" , desAttribute )
