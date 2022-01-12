# -*- coding: gb18030 -*-

# $Id: CWeapon.py,v 1.1 2006-08-09 08:24:17 phw Exp $

"""

"""
from bwdebug import *
from CEquip import *
from config.item.GodWeaponSkillModel import Datas as gw_SM

class CWeapon( CEquip ):
	"""
	武器类
	
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		获取武器效果类型自定义数据格式
		用于发送到客户端
		return WEAPON_EFFECT FDict, Define in alias.xml
		"""
		modelNum = self.model()
		gw_sk = self.getGodWeaponSkillID()
		if gw_sk in gw_SM:
			modelNum += gw_SM[gw_sk]
		data = { 	"modelNum"		:	modelNum,
					"iLevel"		:	self.getIntensifyLevel(),
					"stAmount"		:	self.getBjExtraEffectCount(),
					}

		return data

	def getGodWeaponSkillID( self ):
		"""
		获取神器属性技能ID
		"""
		return self.query( "param1", 0 )

### end of class: CWeapon###


#
# $Log: not supported by cvs2svn $
#
