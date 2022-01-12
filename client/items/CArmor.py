# -*- coding: gb18030 -*-

# $Id: CArmor.py,v 1.7 2008-05-17 11:42:42 huangyongwei Exp $

"""

"""

import math
import BigWorld
import csdefine
import csconst
import ItemAttrClass
import ItemTypeEnum
import Const

from ItemSystemExp import ItemTypeAmendExp
from ItemSystemExp import EquipIntensifyExp
from CEquip import CEquip
from EquipSuitLoader import equipsuit
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from config.client.labels.items import lbs_CArmor
from ItemSystemExp import EquipExp
from EquipHelper import calcIntensifyInc, calcObeyInc, calcTotal

g_equipIntensify = EquipIntensifyExp.instance()


class CArmor( CEquip ):
	"""
	护甲基础类
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

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
		if not CEquip.wield( self, owner, update ):
			return False

		return True

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		if not self.isAlreadyWield(): return	# 如果没有装备效果则不用unwield

		CEquip.unWield( self, owner, update )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取防具专有描述信息
		"""
		CEquip.getProDescription( self, reference )
		attributeDes = []

		# 默认为剑客来计算防御值,如果可以由多个职业使用,那么按照剑客来计算防御值(目前不会有这种防具)
		level = self.getLevel()
		baseQualityRate = self.getBaseRate()
		addBaseRate = 1.0
		itemReqClass = csdefine.CLASS_SWORDMAN
		classlist = self.queryReqClasses()
		if len( classlist ) == 1: itemReqClass = classlist[0]
		armorAmend = ItemTypeAmendExp.instance().getArmorAmend( self.getType() , itemReqClass )
		
		
		exp = EquipExp( self, reference )
		totalPArmor = calcTotal( exp.getArmorBase )
		totalSArmor = calcTotal( exp.getMagicArmorBase )
		# 抵抗沉默
		totalResistMagicHush = calcTotal( exp.getResistMagicHushProb )
		# 抵抗眩晕
		totalResistGiddyValue = calcTotal( exp.getResistGiddyProb )
		# 抵抗定身
		totalResistFixValue = calcTotal( exp.getResistFixProb )
		# 抵抗昏睡
		totalResistSleepValue = calcTotal( exp.getResistSleepProb )
		# 招架
		totalResistHitValue = calcTotal( exp.getResistHitProb )
		# 闪避
		totalDodgeValue = calcTotal( exp.getDodgeProb )
		# 降低对方物理命中
		totalReduceTargetHitValue = calcTotal( exp.getReduceTargetHit )
		
		# 降低对方法术命中现在由项链处理，这里已经不再做任何支持

		# 装备强化附加属性
		intenPArmorValue = 0
		intenPArmorDes = ""
		intenSArmorValue = 0
		intenSArmorDes = ""
		intenChenmoDes = ""
		intenGiddyDes = ""
		intenFixDes = ""
		intenSleepDes = ""
		intenHitDes = ""
		intenDodgeDes = ""
		intenTHitDes = ""
		intenTMagicHitDes = ""
		intensify = self.getIntensifyLevel()
		if intensify != 0:
			# 强化附加物理防御值
			intenPValue =calcIntensifyInc( exp.getArmorBase )
			intenPArmorDes = "+%i" % intenPValue
			intenPArmorDes = PL_Font.getSource( intenPArmorDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加法术防御值
			intenSValue = calcIntensifyInc( exp.getMagicArmorBase )
			intenSArmorDes = "+%i" % intenSValue
			intenSArmorDes = PL_Font.getSource( intenSArmorDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加抵抗沉默
			if totalResistMagicHush:
				intenResistMagicHushValue = calcIntensifyInc( exp.getResistMagicHushProb )
				intenChenmoDes = "+%i" % intenResistMagicHushValue
				intenChenmoDes = PL_Font.getSource( intenChenmoDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加抵抗眩晕
			if totalResistGiddyValue:
				intenResistGiddyValue = calcIntensifyInc( exp.getResistGiddyProb )
				intenGiddyDes = "+%i" % intenResistGiddyValue
				intenGiddyDes = PL_Font.getSource( intenGiddyDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加抵抗定身
			if totalResistFixValue:
				intenResistFixValue = calcIntensifyInc( exp.getResistFixProb )
				intenFixDes = "+%i" % intenResistFixValue
				intenFixDes = PL_Font.getSource( intenFixDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加抵抗睡眠
			if totalResistSleepValue:
				intenResistSleepValue = calcIntensifyInc( exp.getResistSleepProb )
				intenSleepDes = "+%i" % intenResistSleepValue
				intenSleepDes = PL_Font.getSource( intenSleepDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加招架
			if totalResistHitValue:
				intenResistHitValue = calcIntensifyInc( exp.getResistHitProb )
				intenHitDes = "+%i" % intenResistHitValue
				intenHitDes = PL_Font.getSource( intenHitDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加闪避
			if totalDodgeValue:
				intenDodgeValue = calcIntensifyInc( exp.getDodgeProb )
				intenDodgeDes = "+%i" % intenDodgeValue
				intenDodgeDes = PL_Font.getSource( intenDodgeDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加降低对方物理命中
			if totalReduceTargetHitValue:
				intenReduceTargetHitValue = calcIntensifyInc( exp.getReduceTargetHit )
				intenTHitDes = "+%i" % intenReduceTargetHitValue
				intenTHitDes = PL_Font.getSource( intenTHitDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加降低对方法术命中点数 ( 此属性已经给项链了，这里不作处理 )
				
		# 灵魂锁链绑定
		addPArmorDes = ""
		addSArmorDes = ""
		addChenmoDes = ""
		addGiddyDes = ""
		addFixDes = ""
		addSleepDes = ""
		addHitDes = ""
		addDodgeDes = ""
		addTHitDes = ""
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
			# 灵魂绑定附加抵抗沉默
			if totalResistMagicHush:
				addResistMagicHush = calcObeyInc( exp.getResistMagicHushProb )
				addChenmoDes = "+%i" % addResistMagicHush
				addChenmoDes = PL_Font.getSource( addChenmoDes, fc = "c7" )
				if addResistMagicHush < 1.0: addChenmoDes = ""
			# 灵魂绑定附加抵抗眩晕
			if totalResistGiddyValue:
				addResistGiddyValue = calcObeyInc( exp.getResistGiddyProb )
				addGiddyDes = "+%i" % addResistGiddyValue
				addGiddyDes = PL_Font.getSource( addGiddyDes, fc = "c7" )
				if addResistGiddyValue < 1.0: addGiddyDes = ""
			# 灵魂绑定附加抵抗定身
			if totalResistFixValue:
				addResistFixValue = calcObeyInc( exp.getResistFixProb )
				addFixDes = "+%i" % addResistFixValue
				addFixDes = PL_Font.getSource( addFixDes, fc = "c7" )
				if addResistFixValue < 1.0: addFixDes = ""
			# 灵魂绑定附加抵抗睡眠
			if totalResistSleepValue:
				addResistSleepValue = calcObeyInc( exp.getResistSleepProb )
				addSleepDes = "+%i" % addResistSleepValue
				addSleepDes = PL_Font.getSource( addSleepDes, fc = "c7" )
				if addResistSleepValue < 1.0: addSleepDes = ""
			# 灵魂绑定附加招架
			if totalResistHitValue:
				addResistHitValue = calcObeyInc( exp.getResistHitProb )
				addHitDes = "+%i" % addResistHitValue
				addHitDes = PL_Font.getSource( addHitDes, fc = "c7" )
				if addResistHitValue < 1.0: addHitDes = ""
			# 灵魂绑定附加闪避
			if totalDodgeValue:
				addDodgeValue = calcObeyInc( exp.getDodgeProb )
				addDodgeDes = "+%i" % addDodgeValue
				addDodgeDes = PL_Font.getSource( addDodgeDes, fc = "c7" )
				if addDodgeValue < 1.0: addDodgeDes = ""
			# 灵魂绑定附加降低对方物理命中
			if totalReduceTargetHitValue:
				addReduceTargetHitValue = calcObeyInc( exp.getReduceTargetHit )
				addTHitDes = "+%i" % addReduceTargetHitValue
				addTHitDes = PL_Font.getSource( addTHitDes, fc = "c7" )
				if addReduceTargetHitValue < 1.0: addTHitDes = ""
			# 灵魂绑定附加降低对方法术命中 ( 此属性已经给项链了，这里不作处理 )

		# 物理防御
		desPArmor = lbs_CArmor[1] % totalPArmor
		if len( intenPArmorDes ) or len( addPArmorDes ):
			hasInf = ""
			hasObe = ""
			if len( intenPArmorDes ): hasInf = lbs_CArmor[2]
			if len( addPArmorDes ): hasObe = lbs_CArmor[3]
			des = PL_Font.getSource( desPArmor, fc = "c4" )
			desPArmor = "%s(%s%s)" % ( des, hasInf + intenPArmorDes, hasObe + addPArmorDes )
		attributeDes.append( desPArmor )

		# 法术防御
		desSArmor = lbs_CArmor[4] % totalSArmor
		if len( intenSArmorDes ) or len( addSArmorDes ):
			hasInf = ""
			hasObe = ""
			if len( intenSArmorDes ): hasInf = lbs_CArmor[2]
			if len( addSArmorDes ): hasObe = lbs_CArmor[3]
			des = PL_Font.getSource( desSArmor, fc = "c4" )
			desSArmor = "%s(%s%s)" % ( des, hasInf + intenSArmorDes, hasObe + addSArmorDes )
		attributeDes.append( desSArmor )

		# 抵抗沉默
		if totalResistMagicHush:
			desChenmo = lbs_CArmor[5] % totalResistMagicHush
			if len( intenChenmoDes ) or len( addChenmoDes ):
				hasInf = ""
				hasObe = ""
				if len( intenChenmoDes ): hasInf = lbs_CArmor[2]
				if len( addChenmoDes ): hasObe = lbs_CArmor[3]
				des = PL_Font.getSource( desChenmo, fc = "c4" )
				desChenmo = "%s(%s%s)" % ( des, hasInf + intenChenmoDes, hasObe + addChenmoDes )
			attributeDes.append( desChenmo )

		# 抵抗眩晕
		if totalResistGiddyValue:
			desGiddy = lbs_CArmor[6] % totalResistGiddyValue
			if len( intenGiddyDes ) or len( addGiddyDes ):
				hasInf = ""
				hasObe = ""
				if len( intenGiddyDes ): hasInf = lbs_CArmor[2]
				if len( addGiddyDes ): hasObe = lbs_CArmor[3]
				des = PL_Font.getSource( desGiddy, fc = "c4" )
				desGiddy = "%s(%s%s)" % ( des, hasInf + intenGiddyDes, hasObe + addGiddyDes )
			attributeDes.append( desGiddy )

		# 抵抗定身
		if totalResistFixValue:
			desFix = lbs_CArmor[7] % totalResistFixValue
			if len( intenFixDes ) or len( addFixDes ):
				hasInf = ""
				hasObe = ""
				if len( intenFixDes ): hasInf = lbs_CArmor[2]
				if len( addFixDes ): hasObe = lbs_CArmor[3]
				des = PL_Font.getSource( desFix, fc = "c4" )
				desFix = "%s(%s%s)" % ( des, hasInf + intenFixDes, hasObe + addFixDes )
			attributeDes.append( desFix )

		# 抵抗睡眠
		if totalResistSleepValue:
			desSleep = lbs_CArmor[8] % totalResistSleepValue
			if len( intenSleepDes ) or len( addSleepDes ):
				hasInf = ""
				hasObe = ""
				if len( intenSleepDes ): hasInf = lbs_CArmor[2]
				if len( addSleepDes ): hasObe = lbs_CArmor[3]
				des = PL_Font.getSource( desSleep, fc = "c4" )
				desSleep = "%s(%s%s)" % ( des, hasInf + intenSleepDes, hasObe + addSleepDes )
			attributeDes.append( desSleep )

		# 招架
		if totalResistHitValue:
			desHit = lbs_CArmor[9] % totalResistHitValue
			if len( intenHitDes ) or len( addHitDes ):
				hasInf = ""
				hasObe = ""
				if len( intenHitDes ): hasInf = lbs_CArmor[2]
				if len( addHitDes ): hasObe = lbs_CArmor[3]
				des = PL_Font.getSource( desHit, fc = "c4" )
				desHit = "%s(%s%s)" % ( des, hasInf + intenHitDes, hasObe + addHitDes )
			attributeDes.append( desHit )

		# 闪避
		if totalDodgeValue:
			desDodge = lbs_CArmor[10] % totalDodgeValue
			if len( intenDodgeDes ) or len( addDodgeDes ):
				hasInf = ""
				hasObe = ""
				if len( intenDodgeDes ): hasInf = lbs_CArmor[2]
				if len( addDodgeDes ): hasObe = lbs_CArmor[3]
				des = PL_Font.getSource( desDodge, fc = "c4" )
				desDodge = "%s(%s%s)" % ( des, hasInf + intenDodgeDes, hasObe + addDodgeDes )
			attributeDes.append( desDodge )

		# 降低对方物理命中
		if totalReduceTargetHitValue:
			desTHit = lbs_CArmor[11] % totalReduceTargetHitValue
			if len( intenTHitDes ) or len( addTHitDes ):
				hasInf = ""
				hasObe = ""
				if len( intenTHitDes ): hasInf = lbs_CArmor[2]
				if len( addTHitDes ): hasObe = lbs_CArmor[3]
				des = PL_Font.getSource( desTHit, fc = "c4" )
				desTHit = "%s(%s%s)" % ( des, hasInf + intenTHitDes, hasObe + addTHitDes )
			attributeDes.append( desTHit )

		# 降低对方法术命中 ( 此属性已经给项链了，这里不作处理 )
		
		self.desFrame.SetDesSeveral( "Attribute", attributeDes )

		#-----------------套装的显示--------------------------------
		if self.isGreen() and not self.query( "eq_upFlag" ):
			suitID = equipsuit.getSuitID(self.id) #获取该装备的套装列表
			if suitID:
				Equips = []
				if reference.id == BigWorld.player().id:					#如果是显示的自己的
					Equips = reference.getItems(csdefine.KB_EQUIP_ID)		#获取自己的装备的信息
				else:														#如果是显示的被观察的对方的
					Equips = BigWorld.player().targetItems					#装备列表就等于观察对方时玩家从服务器接收的ID
				EquipDatas = {}	#记录玩家自身的装备的ID和耐久度
				suitNumber = 0	#记录已经装备的套装的数量
				suitname = equipsuit.getSuitChildName(suitID)
				suitlist = equipsuit.getSuitChildID(suitID)
				for Equip in Equips:
					if Equip.isGreen():
						EquipDatas[ Equip.id ] = Equip.getHardiness() 	#记录玩家身上的装备 必须是绿装ID
						if Equip.id in suitlist:	#如果该件装备是套装之一 并且是绿装 那么记录一次
							suitNumber += 1			#记录已经装备的件数 用于显示 如( 2/7 )

				suitInfo = "%s(%s/%s)" % ( suitname ,suitNumber , len(suitlist) )
				suitInfo = PL_Font.getSource( suitInfo, fc = "c6" )
				des =""
				if suitNumber != len(suitlist):
					des = PL_Font.getSource( lbs_CArmor[13], fc = "c9" )
				self.desFrame.SetDescription ( "suitInfo", suitInfo+des )

				SuitChildNames = equipsuit.getSuitChildNames(suitID) #获取套装的所有部件名
				if len(SuitChildNames)%2 == 0:		#计算套装要占的行数
					SuitChildNumber = len(SuitChildNames)/2
				else:
					SuitChildNumber = len(SuitChildNames)/2 + 1
				NameMaxLen = len(SuitChildNames[0])	#计算套装名字的最大长度
				for equipName in SuitChildNames:
					if len(equipName) > NameMaxLen:
						NameMaxLen = len(equipName)
				strs = "%" + str(NameMaxLen) + "s"  #格式化字符串的方式
				equipPos = -1
				ketbagID = self.order / csdefine.KB_MAX_SPACE
				for index in range(SuitChildNumber):#一行一行拼凑
					try:
						name1 = SuitChildNames.pop(0)
						equipPos += 1
						id = suitlist[equipPos]
						if self.id == id :	#套装名称列表中,本身的名字颜色只能由自己的耐久度决定
							if self.getHardiness() == 0:
								name1 = PL_Font.getSource( name1, fc = "c3" )	#红色显示
							else:
								name1 = PL_Font.getSource( name1, fc = "c4" )	#绿色显示
						elif id in EquipDatas:			#如果该套装部件ID在玩家装备的绿色套装的LIST中
							if EquipDatas[ id ] == 0:
								name1 = PL_Font.getSource( name1, fc = "c3" )	#红色显示
							else:
								name1 = PL_Font.getSource( name1, fc = "c4" )	#绿色显示
						else:
							name1 = PL_Font.getSource( name1, fc = "c9" )		#灰色显示
					except:
						name1 = ""
					try:
						name2 = SuitChildNames.pop(0)
						equipPos += 1
						id = suitlist[equipPos]
						if self.id == id :	#套装名称列表中,本身的名字颜色只能由自己的耐久度决定
							if self.getHardiness() == 0:
								name2 = PL_Font.getSource( name2, fc = "c3" )	#红色显示
							else:
								name2 = PL_Font.getSource( name2, fc = "c4" )	#绿色显示
						elif id in EquipDatas:			#如果该套装部件ID在玩家装备的绿色套装的LIST中
							if EquipDatas[ id ] == 0:
								name2 = PL_Font.getSource( name2, fc = "c3" )	#红色显示
							else:
								name2 = PL_Font.getSource( name2, fc = "c4" )	#绿色显示
						else:
							name2 = PL_Font.getSource( name2, fc = "c9" )		#灰色显示
					except:
						name2 = ""
					Name = (strs % name1) + "  " + (strs % name2)
					key = "suitChild%s" % index
					Name = PL_Align.getSource("C") + Name + PL_Align.getSource("L")
					self.desFrame.SetDescription( key , Name )
