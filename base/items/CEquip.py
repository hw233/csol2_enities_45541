# -*- coding: gb18030 -*-

# $Id: CEquip.py,v 1.5 2008-02-19 08:28:19 yangkai Exp $

"""
装备类基础模块
"""
import ItemTypeEnum
from CItemBase import *
from bwdebug import *
from ItemSystemExp import EquipAttrExp
g_itemPropAttrExp = EquipAttrExp.instance()

class CEquip( CItemBase ):
	"""
	装备基础类
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		
	def isEquip( self ):
		"""
		virtual method.
		判断是否是装备
		"""
		return True
		
	def getExtraEffect( self ):
		"""
		获取装备附加属性
		@return:    dict
		"""
		return self.query( "eq_extraEffect", {} )

	def createRandomEffect( self, owner = None ):
		"""
		生成装备的随机属性
		@param owner: 装备拥有者
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
		# 获取随机属性失败
		if not datas: return False
		randomEffect = datas["dic"]
		
		self.set( "eq_extraEffect", randomEffect, owner )
		return True

	def model( self ):
		"""
		获取模型编号
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

	def getFDict( self ):
		"""
		Virtual Method
		获取法宝效果类型自定义数据格式
		用于发送到客户端
		return INT32
		"""
		raise AssertionError, "I can't do this!"

	def getIntensifyLevel( self ):
		"""
		获取装备强化等级
		"""
		return self.query( "eq_intensifyLevel", 0 )

	def getBjExtraEffectCount( self ):
		"""
		获取宝石镶嵌数量
		"""
		return len( self.getBjExtraEffect() )

	def getBjExtraEffect( self ):
		"""
		获取宝石附加属性
		"""
		return self.query( "bj_extraEffect", [] )


### end of class: CEquip ###


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2007/11/24 02:59:16  yangkai
# 物品系统调整，属性更名
# 当前耐久度"endure" -- > "eq_hadriness"
# 最大耐久度"currEndureLimit" --> "eq_hardinessLimit"
# 最大耐久度上限"maxEndureLimit" --> "eq_hardinessMax"
#
# Revision 1.3  2007/08/15 07:09:49  yangkai
# 修改装备属性
# "maxEndure"----> "currEndureLimit" // 当前耐久度上限
# 增加属性 "maxEndureLimit" // 最大耐久度上限
#
# Revision 1.2  2006/08/11 02:58:48  phw
# no message
#
# Revision 1.1  2006/08/09 08:24:17  phw
# no message
#
#
