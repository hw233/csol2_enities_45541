# -*- coding:gb18030 -*-


from CItemBase import CItemBase
import ItemAttrClass
import ItemTypeEnum
equ_items_type = ItemTypeEnum.EQUIP_TYPE_SET

from Time import Time
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CItemBase


class CPotentialCinnabar( CItemBase ):
	"""
	潜能丹
	"""
	def description( self, reference ):
		"""
		产生描述
		@param reference: 玩家entity,表示以谁来做为生成描述的参照物
		@type  reference: Entity
		@return:          物品的字符串描述
		@rtype:           ARRAY of str
		"""
		# description会直接返回显示的结果，description会对self.desFrame设置，不想复制大量相似代码，因此直接调用description
		# 然后再对需要个性化的描述进行设置。description中设置self.desFrame然后返回描述在结构上来说不够灵活，应该把设置和
		# 获得分开，如此可以方便的设置描述内容，以后要进行优化。
		# 显示物品相关信息
		self.getProDescription( reference )	#显示物品本身的信息

		attrMap = ItemAttrClass.m_itemAttrMap
		# 显示物品名字，根据物品的品质决定物品名字的颜色
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = self.getQualityColor() )
		self.desFrame.SetDescription("name" , nameDes)
		# 物品类型
		desType = attrMap["type"].description( self, reference )
		self.desFrame.SetDescription( "type", desType )
		# 需求声望
		reqCredits = attrMap["reqCredit"].descriptionDict( self, reference )
		if reqCredits:
			reqCreditsDes = reqCredits.keys()
			for index in xrange( len( reqCreditsDes) ):
				if not reqCredits[ reqCreditsDes[index] ]:
					reqCreditsDes[ index ] = PL_Font.getSource( reqCreditsDes[ index ] , fc = "c3" )
			self.desFrame.SetDesSeveral( "reqCredit", reqCreditsDes )
		#是否已认主 by姜毅
		type = self.getType()
		if not type in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
			canEqu = False
			if type in equ_items_type:
				canEqu = True
			if canEqu:
				desObey = attrMap["eq_obey"].description( self, reference )
				if desObey != "":
					desObey = PL_Font.getSource( desObey, fc = "c7" )
					self.desFrame.SetDescription( "eq_obey", desObey )
		#是否绑定
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			desBind = PL_Font.getSource( desBind , fc = "c1" )
			self.desFrame.SetDescription( "bindType", desBind )
		#是否唯一
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CItemBase[1] )
		# 是否可出售
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CItemBase[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )
		# 取得额外的描述1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 % self.getLevel() )	# 需要显示潜能丹级别
		# 取得额外的描述2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
		#	if des1 != "": des2 = g_newLine + des2
			self.desFrame.SetDescription( "describe2", des2 )
		# 取得额外的描述3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
		#	if des1 != "" or des2 != "": des3 = g_newLine + des3
			self.desFrame.SetDescription( "describe3", des3 )

		# 剩余使用时间
		lifeType = self.getLifeType()
		if lifeType:
			lifeTime = self.getLifeTime()
			if lifeTime:
				deadTime = self.getDeadTime()
				if deadTime:
					sTime = int( Time.time() )
					rTime = deadTime - sTime
					if rTime > lifeTime: rTime = lifeTime
					des = lbs_CItemBase[3]
					if rTime <= 0:
						des += lbs_CItemBase[4]
					else:
						hour = rTime/3600
						min = ( rTime - hour * 3600 )/60
						sec = rTime%60

						# 修改时间的描述显示 by姜毅
						day = int( hour / 24 )

						if day:
							des += lbs_CItemBase[5] % day
						elif int( hour ):
							des += lbs_CItemBase[6] % hour
						elif int( min ):
							des += lbs_CItemBase[7] % min
						else:
							des += lbs_CItemBase[8] % sec
					des = PL_Font.getSource( des, fc = "c3" )
					self.desFrame.SetDescription( "lifeType", des )
			else:
				des = PL_Font.getSource( lbs_CItemBase[9], fc = "c3" )
				self.desFrame.SetDescription( "lifeType", des )

		return self.desFrame.GetDescription()
	
	