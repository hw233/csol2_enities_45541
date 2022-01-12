# -*- coding: gb18030 -*-

# $Id: CEquip.py,v 1.37 2008-07-17 02:32:51 yangkai Exp $

"""
装备类基础模块
"""
import csdefine
import ItemAttrClass
import GUIFacade.MerchantFacade

import Define
from bwdebug import *
from funcEquip import *
from CItemBase import CItemBase
from ItemTypeEnum import WEAPON_LIST
from guis.Toolbox import toolbox

from EquipEffectLoader import EquipEffectLoader
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Image_Gui import PL_Image_Gui
from config.client.labels.items import lbs_CEquip

g_equipEffect = EquipEffectLoader.instance()

class CEquip( CItemBase ):
	"""
	装备基础类

	"""
	texture = (
		"star_yellow.gui","star_yellow.gui","star_yellow.gui",
		"star_yellow.gui","star_yellow.gui","star_yellow.gui",
		"star_orange.gui","star_orange.gui","star_orange_texanim.gui",
		)

	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )

	def fullName( self ):
		"""
		获取物品的全名 如 雄鹰的逆天的霸王弓
		"""
		#if len( self.getCreateEffect() ):
		#	return self.name()
		return CItemBase.fullName( self )

	def isAlreadyWield( self ):
		"""
		判断是否已经装备上效果了

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_wieldStatus", 0 ) > 0

	def isSuitEffectWield( self ):
		"""
		判断是否已经装备上套装属性了

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_suitEffectStatus", 0 ) > 0

	def getWieldOrders( self ):
		"""
		取得当前物品的可装备位置列表，即该物品可以放在装备栏的哪些位置上；CEL_*

		@return: tuple of int
		@rtype:  tuple of int
		"""
		return m_cwt2cel[self.query( "eq_wieldType" )]

	def getUnwieldOrders( self, equipKitbag, equipOrder ):
		"""
		用于当要装备某种类型的装备时检查装备栏需要卸下哪些位置的装备

		@param equipKitbag: 装备栏
		@type  equipKitbag: KitbagType
		@param  equipOrder: 想要装备的位置
		@type   equipOrder: INT8
		@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
		                    如果指定的装备位置与当前函数默认的类型对应的位置不符则返回None
		@rtype:             tuple of UINT8/None
		"""
		return m_unwieldCheck[self.query( "eq_wieldType" )]( equipKitbag, equipOrder )

	def wield( self, owner, update = True ):
		"""
		装备道具

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		raise "I can't support yet."

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		raise "I can't support yet."

	def canWield( self, owner ):
		"""
		检查是否能装备物品效果

		@param owner: 道具的使用者（即拥有者）
		@type  owner: Entity
		@return:    True 允许装备，False 不允许装备
		@return:    BOOL
		"""
		if not self._checkReqlevel( owner ): return False
		if not self._checkReqGender( owner ): return False
		if not self._checkClasses( owner ): return False
		if not self._checkHardiness(): return False
		if not self._checkLifeTime(): return False
		return True

	def _checkLifeTime( self ):
		"""
		检查使用时间
		"""
		lifeType = self.getLifeType()
		lifeTime = self.getLifeTime()
		if lifeType and not lifeTime: return False
		return True

	def _checkHardiness( self ):
		"""
		检查当前耐久度
		对于一个装备而言，如果当前耐久度为None，即该装备总是可以装备的
		@return: 大于0或不存在这个属性则返回True，否则返回False
		@rtype:  BOOL
		"""
		hMax = self.query( "eq_hardinessMax" )
		if hMax is None or hMax <= 0: return True
		return self.query( "eq_hardiness" ) > 0

	def _checkReqGender( self, owner ):
		"""
		检查装备需求性别

		@param owner: 物品拥有者
		@type  owner: Entity
		@return: 匹配则返回True, 否则返回False
		@rtype:  BOOL
		"""
		reqGender = self.getReqGender()
		if len( reqGender ) == 0: return True
		return owner.getGender() in reqGender

	def _getHardinessLevle( self ):
		"""
		获取目前装备的耐久度等级(崭新、完好、半旧、破损、残缺)
		"""
		hMax = self.query( "eq_hardinessLimit" )
		hCur = self.query( "eq_hardiness" )
		if int(hMax) == 0:		#如果最大耐久为0了 直接返回残缺
			return lbs_CEquip[1]
		ratio = float( hCur ) / float( hMax )
		if ratio > 0.8:
			return lbs_CEquip[2]
		elif ratio > 0.6:
			return lbs_CEquip[3]
		elif ratio > 0.4:
			return lbs_CEquip[4]
		elif ratio > 0.2:
			return lbs_CEquip[5]
		else:
			return lbs_CEquip[6]


	def _checkClasses( self, owner ):
		"""
		检查可装备职业

		@return: 匹配则返回True, 否则返回False
		@rtype:  BOOL
		"""
		return self.isMetier( owner.getClass() )

	def _checkReqlevel( self, owner ):
		"""
		检查装备等级

		@param owner: 背包拥有者
		@type  owner: Entity
		@return: 匹配则返回True, 否则返回False
		@rtype:  BOOL
		"""
		return owner.level >= self.query( "reqLevel", 0 )

	def isMetier( self, metierType ):
		"""
		判断是否可以装备在某个职业上

		@parma metierType: 职业类型; CEM_*; 可以使用“或(|)”来连接多个，表示能同时支持这么多个职业装备。
		@type  metierType: UINT16
		@return: 如果可以在某职业上装备则返回True，否则返回False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		if reqClasses is None:
			return True		# 没有classes则表示没有此需求
		return metierType in reqClasses

	def isMetierOnly( self, metierType ):
		"""
		判断是否只能装备在某个职业上

		@parma metierType: 职业类型; CEM_*
		@type  metierType: UINT16
		@return: 如果只能在指定的职业上装备则返回True，否则返回False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		if reqClasses is None:
			return True		# 没有classes则表示没有此需求
		return reqClasses == [ metierType ]

	def getProDescription( self, reference ):
		"""
		virtual method
		获取装备专有描述信息
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# 设置打造者名字
		creator = attrMap["creator"].description( self, reference)
		if creator:
			creator = PL_Font.getSource( creator, fc = "c8" )
			self.desFrame.SetDescription("creator", creator)
		# 获取装备强化信息描述
		desIntensify = attrMap["eq_intensifyLevel"].description( self, reference )
		if desIntensify and  desIntensify > 0:
			desIn = PL_Image.getSource("guis/general/Itemattribute/" + self.texture[desIntensify-1] ) * desIntensify
			desIn = toolbox.infoTip.getItemGrid( desIn , { "newline" : False } )
			self.desFrame.SetDescription("eq_intensifyLevel", desIn)	#设置星星(强化等级)
		# 获取需求职业描述，根据自己的职业确定该项文字的颜色
		desClasses = attrMap["reqClasses"].description( self, reference )
		if desClasses:
			desClasses = lbs_CEquip[10] + desClasses
			if not self._checkClasses( reference ):
				desClasses = PL_Font.getSource( desClasses , fc = ( 255, 0, 0 ) )
			self.desFrame.SetDesSeveral ("reqClasses",[[ desClasses ]])
		onlyLimit = attrMap["onlyLimit"].description( self, reference )
		if onlyLimit:
			desOnly = PL_Font.getSource( onlyLimit , fc = ( 255, 255, 255 ) )
			self.desFrame.SetDescription ( "onlyLimit",desOnly )
		# 根据自己的等级确定该项文字的颜色，设置需求等级
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if desReqlevel:
			if not self._checkReqlevel( reference ):
				desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			self.desFrame.SetDescription("reqLevel",desReqlevel )
		# 根据自己的性别确定该项文字的颜色，设置需求等级
		desReqGender = attrMap["reqGender"].description( self, reference )
		if desReqGender:
			if not self._checkReqGender( reference ):
				desReqGender = PL_Font.getSource( desReqGender, fc = ( 255, 0, 0 ) )
			self.desFrame.SetDescription("reqGender",desReqGender )
		# 获取装备的装备的位置(双手 单手...)
		deswWieldType = attrMap["eq_wieldType"].description( self, reference )
		self.desFrame.SetDescription("eq_wieldType",deswWieldType)
		# 耐久度,有一些装备没耐久，如项链，戒指
		desHardiness = attrMap["eq_hardiness"].descriptionList( self, reference )
		if desHardiness != "":
			#修改武器耐久度的现实方式 按照策划的公式进行武器耐久度显示 by姜毅
			weaponList = WEAPON_LIST
			if self.getType() in weaponList:
				lv = self.query( "reqLevel" )
				hardMax = self.query( "eq_hardinessLimit" )
				hardNow = self.query( "eq_hardiness" )
				parm = 100 * ( 154 - lv )
				hardNow = hardNow / parm
				hardMax = hardMax / parm
				desHardiness[1] = str( hardNow ) + '/' + str( hardMax )
			if not self._checkHardiness():
				deslist = desHardiness[1].split( '/' )  #因为只有前半部分显示为红色 所以 用'/'切割字符串
				deslist[0] = PL_Font.getSource( deslist[0] , fc = ( 255, 0, 0 ) )
				desHardiness[1] = deslist[0] + "/" + deslist[1]
			self.desFrame.SetDesSeveral( "eq_hardiness", [ [desHardiness[0] + " " + desHardiness[1] , self._getHardinessLevle()] ] )
		# 设置套装属性
		desSuitEffectList = attrMap["eq_suitEffect"].descriptionList( self, reference )
		colorFunc = lambda v, arg1, arg2 : v and arg1 or arg2
		if desSuitEffectList:
			des = lbs_CEquip[11]
			suitCFunc = colorFunc
			if self.isSuitEffectWield():
				suitEffectColor = "c4"
			else:
				suitEffectColor = "c9"
				suitCFunc = lambda v, arg1, arg2 : arg2
				des = des + lbs_CEquip[12]
			desSuitEffectListTemp = []
			des = PL_Font.getSource( des ,fc = suitEffectColor )
			desSuitEffectListTemp.append([des])
			for desSuitEffect in desSuitEffectList:
				color = suitCFunc( desSuitEffect[-1], "c6", suitEffectColor )	# 当属性值达到最大时显示为金黄色
				suitEfDes = PL_Font.getSource( "%s %s" % ( desSuitEffect[0], desSuitEffect[1] ), fc = color )
				desSuitEffectListTemp.append( [ suitEfDes ] )
			self.desFrame.SetDesSeveral( "eq_suitEffect", desSuitEffectListTemp )
		# 获取该效果的宝石图标
		# 如果没有图标 使用默认的
		limitSlot = self.getLimitSlot()
		extraEffect = self.getBjExtraEffect()
		des = ""
		for i in range(limitSlot):
			try:
				effectid    = extraEffect[i][0]
				effectvalue = extraEffect[i][1]
				iconName = g_equipEffect.getIcon( effectid, effectvalue )
				iconPath   = ""
				if iconName != "":
					iconPath = "icons/stone/%s.tga" % iconName
				des += PL_Image_Gui.getSource( "guis/general/Itemattribute/hole.gui",  iconPath )
			except IndexError:
				des += PL_Image_Gui.getSource( "guis/general/Itemattribute/hole.gui" )
		if des != "":
			des = toolbox.infoTip.getItemGrid( des , { "newline" : False, "align" : "C" } )
			self.desFrame.SetDescription( "bj_extraStone", des )
		# 宝石镶嵌属性
		desStuList = attrMap["bj_extraEffect"].descriptionList( self, reference )
		desStuListType = attrMap["bj_extraEffect"].descriptionListType( self, reference )
		dsltIndex = 0
		if desStuList and desStuListType:
			desStuListTemp = []
			for desStu in desStuList:
				desStuListTemp.append( [PL_Font.getSource( lbs_CEquip[13] + desStu[0] ,fc = "c27" ) + " " + PL_Font.getSource( desStu[1] ,fc = "c27" ) + " (" + PL_Font.getSource( desStuListType[dsltIndex] ,fc = "c27" ) + ")"] )
				if dsltIndex < len( desStuListType ):
					dsltIndex += 1
			self.desFrame.SetDesSeveral( "bj_extraEffect", desStuListTemp )
		# 附加属性
		desExtraEffectList = attrMap["eq_extraEffect"].descriptionList( self, reference )
		desExtraEffectListTemp = []
		for desExtraEffect in desExtraEffectList:
			color = colorFunc( desExtraEffect[-1], "c6", ( 0, 255, 0 ) )			# 当属性值达到最大时显示为金黄色
			des = PL_Font.getSource( desExtraEffect[0] + desExtraEffect[1] , fc = color )
			desExtraEffectListTemp.append( [ des ] )
		self.desFrame.SetDesSeveral( "eq_extraEffect", desExtraEffectListTemp)		#设置装备附加属性 如加多少力量,智力......

		# 灌注属性
		desCreateEffectList = attrMap["eq_createEffect"].descriptionList( self, reference )
		desCreateEffectListTemp = []
		for desCreateEffect in desCreateEffectList:
			color = colorFunc( desCreateEffect[-1], "c6", "c27" )					# 当属性值达到最大时显示为金黄色
			des = PL_Font.getSource( desCreateEffect[0] + desCreateEffect[1] , fc = color )
			desCreateEffectListTemp.append( [ des ] )
		self.desFrame.SetDesSeveral( "eq_createEffect", desCreateEffectListTemp )	#设置装备附加属性 如加多少力量,智力......

		# 装备飞升
		upperName=attrMap["eq_upper"].description( self, reference )
		if upperName != "":
			temp = upperName.split()
			upperName = PL_Font.getSource( temp[0], fc = ( 255, 255, 0) ) + " "+ PL_Font.getSource( temp[1], fc = "c8" ) + " " + PL_Font.getSource( temp[2], fc = ( 255, 255, 0) )
			self.desFrame.SetDescription( "eq_upper", upperName )	#设置装备飞升者的名字

		# 装备计时
		lifeTypeDes = attrMap["lifeType"].description( self, reference)
		if lifeTypeDes:
			lifeTypeDes = PL_Font.getSource( lifeTypeDes, fc = "c4" )
			self.desFrame.SetDescription( "lifeType", lifeTypeDes )

	def getIntensifyLevel( self ):
		"""
		获取装备强化等级activation
		"""
		return self.query( "eq_intensifyLevel", 0 )
	
	def model( self ):
		"""
		获取模型路径
		"""
		modelList = self.query( "model", "" ).split(";")
		try:
			model = modelList[0]
			if self.getIntensifyLevel() >= 5 and len( modelList ) > 1 :
				model = modelList[1] if modelList[1] else model
			if self.getIntensifyLevel() >= 8 and len( modelList ) > 2 :
				model = modelList[2] if modelList[2] else model
			return int( model )
		except:
			return 0

	def getSlot( self ):
		"""
		获取当前已镶嵌孔数
		"""
		return self.query( "eq_slot", 0 )

	def getExtraEffect( self ):
		"""
		获取装备附加属性
		@return:    dict
		"""
		return self.query( "eq_extraEffect", {} )

	def getCreateEffect( self ):
		"""
		获取装备灌注属性
		@return:    dict
		"""
		return self.query( "eq_createEffect", [] )

	def getLimitSlot( self ):
		"""
		获取当前已有装备孔数
		"""
		return self.query( "eq_limitSlot", 0 )

	def getMaxSlot( self ):
		"""
		获取最大装备孔数
		"""
		return self.query( "eq_maxSlot", 0 )

	def canRepair( self ):
		"""
		virtual method.
		判断一个物品是否能被修理
		@return: BOOL
		@rtype:  BOOL
		"""
		if not CItemBase.canRepair( self ): return False
		hMax = self.query( "eq_hardinessMax" )
		if hMax is None or hMax <= 0: return False
		return self.query("eq_hardinessLimit") > 0

	def isEquip( self ):
		"""
		virtual method.
		判断是否是装备
		"""
		return True

	def getCreator( self, creator ):
		"""
		获得打造者名字
		"""
		return self.query( "creator", "" )


	def getIntensifyValue( self ):
		"""
		获取装备的强化附加值属性
		"""
		return self.query( "intensifyValue", [ [ 0, 0 ], [ 0, 0 ] ] )

	def getHardiness( self ):
		"""
		获得当前耐久度
		@return: 当前耐久度,如果没有耐久度则为0
		@rtype: int
		"""
		return self.query( "eq_hardiness", 0 )

	def getHardinessMax( self ):
		"""
		获得最大耐久度上限(此值不变)
		@return: 最大耐久度上限,如果没有耐久度上限则为0
		@rtype: int
		"""
		return self.query( "eq_hardinessMax", 0 )

	def getHardinessLimit( self ):
		"""
		获得当前耐久度上限(此值能更改)

		@return: 最大耐久度,如果没有耐久度则为0
		@rtype: int
		"""
		return self.query( "eq_hardinessLimit", 0 )

	def getPrice( self ):
		"""
		获取装备的价格
		跟耐久度有关
		"""
		# 装备的价格 = 当前耐久度/原始最大耐久度*装备原始卖店价格
		basePrice = self.getRecodePrice()
		hardinessMax = self.getHardinessMax()
		if hardinessMax == 0: return basePrice
		newPrice = int( self.getHardiness() * 1.0 / self.getHardinessMax() * basePrice )
		if newPrice <= 0: return 1
		return newPrice

	def checkUseStatus( self, owner ) :
		"""
		检查物品的使用情况
		"""
		if not self.canWield( owner ) :
			return Define.ITEM_STATUS_USELESSNESS
		elif self.getHardinessMax() > 0 and \
			self.getHardiness() / float( self.getHardinessMax() ) < 0.1 :		# 耐久度小于10%，返回破损状态
				return Define.ITEM_STATUS_ABRASION
		return Define.ITEM_STATUS_NATURAL
