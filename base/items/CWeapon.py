# -*- coding: gb18030 -*-

# $Id: CWeapon.py,v 1.1 2006-08-09 08:24:17 phw Exp $

"""

"""
from bwdebug import *
from CEquip import *
from config.item.GodWeaponSkillModel import Datas as gw_SM

class CWeapon( CEquip ):
	"""
	������
	
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
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
		��ȡ�������Լ���ID
		"""
		return self.query( "param1", 0 )

### end of class: CWeapon###


#
# $Log: not supported by cvs2svn $
#
