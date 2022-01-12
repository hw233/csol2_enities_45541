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
	���׻�����
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def wield( self, owner, update = True ):
		"""
		װ������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ):
			return False

		return True

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		if not self.isAlreadyWield(): return	# ���û��װ��Ч������unwield

		CEquip.unWield( self, owner, update )

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡ����ר��������Ϣ
		"""
		CEquip.getProDescription( self, reference )
		attributeDes = []

		# Ĭ��Ϊ�������������ֵ,��������ɶ��ְҵʹ��,��ô���ս������������ֵ(Ŀǰ���������ַ���)
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
		# �ֿ���Ĭ
		totalResistMagicHush = calcTotal( exp.getResistMagicHushProb )
		# �ֿ�ѣ��
		totalResistGiddyValue = calcTotal( exp.getResistGiddyProb )
		# �ֿ�����
		totalResistFixValue = calcTotal( exp.getResistFixProb )
		# �ֿ���˯
		totalResistSleepValue = calcTotal( exp.getResistSleepProb )
		# �м�
		totalResistHitValue = calcTotal( exp.getResistHitProb )
		# ����
		totalDodgeValue = calcTotal( exp.getDodgeProb )
		# ���ͶԷ���������
		totalReduceTargetHitValue = calcTotal( exp.getReduceTargetHit )
		
		# ���ͶԷ����������������������������Ѿ��������κ�֧��

		# װ��ǿ����������
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
			# ǿ�������������ֵ
			intenPValue =calcIntensifyInc( exp.getArmorBase )
			intenPArmorDes = "+%i" % intenPValue
			intenPArmorDes = PL_Font.getSource( intenPArmorDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӷ�������ֵ
			intenSValue = calcIntensifyInc( exp.getMagicArmorBase )
			intenSArmorDes = "+%i" % intenSValue
			intenSArmorDes = PL_Font.getSource( intenSArmorDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӵֿ���Ĭ
			if totalResistMagicHush:
				intenResistMagicHushValue = calcIntensifyInc( exp.getResistMagicHushProb )
				intenChenmoDes = "+%i" % intenResistMagicHushValue
				intenChenmoDes = PL_Font.getSource( intenChenmoDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӵֿ�ѣ��
			if totalResistGiddyValue:
				intenResistGiddyValue = calcIntensifyInc( exp.getResistGiddyProb )
				intenGiddyDes = "+%i" % intenResistGiddyValue
				intenGiddyDes = PL_Font.getSource( intenGiddyDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӵֿ�����
			if totalResistFixValue:
				intenResistFixValue = calcIntensifyInc( exp.getResistFixProb )
				intenFixDes = "+%i" % intenResistFixValue
				intenFixDes = PL_Font.getSource( intenFixDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӵֿ�˯��
			if totalResistSleepValue:
				intenResistSleepValue = calcIntensifyInc( exp.getResistSleepProb )
				intenSleepDes = "+%i" % intenResistSleepValue
				intenSleepDes = PL_Font.getSource( intenSleepDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�������м�
			if totalResistHitValue:
				intenResistHitValue = calcIntensifyInc( exp.getResistHitProb )
				intenHitDes = "+%i" % intenResistHitValue
				intenHitDes = PL_Font.getSource( intenHitDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ����������
			if totalDodgeValue:
				intenDodgeValue = calcIntensifyInc( exp.getDodgeProb )
				intenDodgeDes = "+%i" % intenDodgeValue
				intenDodgeDes = PL_Font.getSource( intenDodgeDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӽ��ͶԷ���������
			if totalReduceTargetHitValue:
				intenReduceTargetHitValue = calcIntensifyInc( exp.getReduceTargetHit )
				intenTHitDes = "+%i" % intenReduceTargetHitValue
				intenTHitDes = PL_Font.getSource( intenTHitDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# ǿ�����ӽ��ͶԷ��������е��� ( �������Ѿ��������ˣ����ﲻ������ )
				
		# ���������
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
			# ���󶨸����������ֵ
			addPArmorValue = calcObeyInc( exp.getArmorBase )
			addPArmorDes = "+%i" % addPArmorValue
			addPArmorDes = PL_Font.getSource( addPArmorDes, fc = "c7" )
			if addPArmorValue < 1.0: addPArmorDes = ""
			# ���󶨸��ӷ�������ֵ
			addSArmorValue = calcObeyInc( exp.getMagicArmorBase )
			addSArmorDes = "+%i" % addSArmorValue
			addSArmorDes = PL_Font.getSource( addSArmorDes, fc = "c7" )
			if addSArmorValue < 1.0: addSArmorDes = ""
			# ���󶨸��ӵֿ���Ĭ
			if totalResistMagicHush:
				addResistMagicHush = calcObeyInc( exp.getResistMagicHushProb )
				addChenmoDes = "+%i" % addResistMagicHush
				addChenmoDes = PL_Font.getSource( addChenmoDes, fc = "c7" )
				if addResistMagicHush < 1.0: addChenmoDes = ""
			# ���󶨸��ӵֿ�ѣ��
			if totalResistGiddyValue:
				addResistGiddyValue = calcObeyInc( exp.getResistGiddyProb )
				addGiddyDes = "+%i" % addResistGiddyValue
				addGiddyDes = PL_Font.getSource( addGiddyDes, fc = "c7" )
				if addResistGiddyValue < 1.0: addGiddyDes = ""
			# ���󶨸��ӵֿ�����
			if totalResistFixValue:
				addResistFixValue = calcObeyInc( exp.getResistFixProb )
				addFixDes = "+%i" % addResistFixValue
				addFixDes = PL_Font.getSource( addFixDes, fc = "c7" )
				if addResistFixValue < 1.0: addFixDes = ""
			# ���󶨸��ӵֿ�˯��
			if totalResistSleepValue:
				addResistSleepValue = calcObeyInc( exp.getResistSleepProb )
				addSleepDes = "+%i" % addResistSleepValue
				addSleepDes = PL_Font.getSource( addSleepDes, fc = "c7" )
				if addResistSleepValue < 1.0: addSleepDes = ""
			# ���󶨸����м�
			if totalResistHitValue:
				addResistHitValue = calcObeyInc( exp.getResistHitProb )
				addHitDes = "+%i" % addResistHitValue
				addHitDes = PL_Font.getSource( addHitDes, fc = "c7" )
				if addResistHitValue < 1.0: addHitDes = ""
			# ���󶨸�������
			if totalDodgeValue:
				addDodgeValue = calcObeyInc( exp.getDodgeProb )
				addDodgeDes = "+%i" % addDodgeValue
				addDodgeDes = PL_Font.getSource( addDodgeDes, fc = "c7" )
				if addDodgeValue < 1.0: addDodgeDes = ""
			# ���󶨸��ӽ��ͶԷ���������
			if totalReduceTargetHitValue:
				addReduceTargetHitValue = calcObeyInc( exp.getReduceTargetHit )
				addTHitDes = "+%i" % addReduceTargetHitValue
				addTHitDes = PL_Font.getSource( addTHitDes, fc = "c7" )
				if addReduceTargetHitValue < 1.0: addTHitDes = ""
			# ���󶨸��ӽ��ͶԷ��������� ( �������Ѿ��������ˣ����ﲻ������ )

		# �������
		desPArmor = lbs_CArmor[1] % totalPArmor
		if len( intenPArmorDes ) or len( addPArmorDes ):
			hasInf = ""
			hasObe = ""
			if len( intenPArmorDes ): hasInf = lbs_CArmor[2]
			if len( addPArmorDes ): hasObe = lbs_CArmor[3]
			des = PL_Font.getSource( desPArmor, fc = "c4" )
			desPArmor = "%s(%s%s)" % ( des, hasInf + intenPArmorDes, hasObe + addPArmorDes )
		attributeDes.append( desPArmor )

		# ��������
		desSArmor = lbs_CArmor[4] % totalSArmor
		if len( intenSArmorDes ) or len( addSArmorDes ):
			hasInf = ""
			hasObe = ""
			if len( intenSArmorDes ): hasInf = lbs_CArmor[2]
			if len( addSArmorDes ): hasObe = lbs_CArmor[3]
			des = PL_Font.getSource( desSArmor, fc = "c4" )
			desSArmor = "%s(%s%s)" % ( des, hasInf + intenSArmorDes, hasObe + addSArmorDes )
		attributeDes.append( desSArmor )

		# �ֿ���Ĭ
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

		# �ֿ�ѣ��
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

		# �ֿ�����
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

		# �ֿ�˯��
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

		# �м�
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

		# ����
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

		# ���ͶԷ���������
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

		# ���ͶԷ��������� ( �������Ѿ��������ˣ����ﲻ������ )
		
		self.desFrame.SetDesSeveral( "Attribute", attributeDes )

		#-----------------��װ����ʾ--------------------------------
		if self.isGreen() and not self.query( "eq_upFlag" ):
			suitID = equipsuit.getSuitID(self.id) #��ȡ��װ������װ�б�
			if suitID:
				Equips = []
				if reference.id == BigWorld.player().id:					#�������ʾ���Լ���
					Equips = reference.getItems(csdefine.KB_EQUIP_ID)		#��ȡ�Լ���װ������Ϣ
				else:														#�������ʾ�ı��۲�ĶԷ���
					Equips = BigWorld.player().targetItems					#װ���б�͵��ڹ۲�Է�ʱ��Ҵӷ��������յ�ID
				EquipDatas = {}	#��¼��������װ����ID���;ö�
				suitNumber = 0	#��¼�Ѿ�װ������װ������
				suitname = equipsuit.getSuitChildName(suitID)
				suitlist = equipsuit.getSuitChildID(suitID)
				for Equip in Equips:
					if Equip.isGreen():
						EquipDatas[ Equip.id ] = Equip.getHardiness() 	#��¼������ϵ�װ�� ��������װID
						if Equip.id in suitlist:	#����ü�װ������װ֮һ ��������װ ��ô��¼һ��
							suitNumber += 1			#��¼�Ѿ�װ���ļ��� ������ʾ ��( 2/7 )

				suitInfo = "%s(%s/%s)" % ( suitname ,suitNumber , len(suitlist) )
				suitInfo = PL_Font.getSource( suitInfo, fc = "c6" )
				des =""
				if suitNumber != len(suitlist):
					des = PL_Font.getSource( lbs_CArmor[13], fc = "c9" )
				self.desFrame.SetDescription ( "suitInfo", suitInfo+des )

				SuitChildNames = equipsuit.getSuitChildNames(suitID) #��ȡ��װ�����в�����
				if len(SuitChildNames)%2 == 0:		#������װҪռ������
					SuitChildNumber = len(SuitChildNames)/2
				else:
					SuitChildNumber = len(SuitChildNames)/2 + 1
				NameMaxLen = len(SuitChildNames[0])	#������װ���ֵ���󳤶�
				for equipName in SuitChildNames:
					if len(equipName) > NameMaxLen:
						NameMaxLen = len(equipName)
				strs = "%" + str(NameMaxLen) + "s"  #��ʽ���ַ����ķ�ʽ
				equipPos = -1
				ketbagID = self.order / csdefine.KB_MAX_SPACE
				for index in range(SuitChildNumber):#һ��һ��ƴ��
					try:
						name1 = SuitChildNames.pop(0)
						equipPos += 1
						id = suitlist[equipPos]
						if self.id == id :	#��װ�����б���,�����������ɫֻ�����Լ����;öȾ���
							if self.getHardiness() == 0:
								name1 = PL_Font.getSource( name1, fc = "c3" )	#��ɫ��ʾ
							else:
								name1 = PL_Font.getSource( name1, fc = "c4" )	#��ɫ��ʾ
						elif id in EquipDatas:			#�������װ����ID�����װ������ɫ��װ��LIST��
							if EquipDatas[ id ] == 0:
								name1 = PL_Font.getSource( name1, fc = "c3" )	#��ɫ��ʾ
							else:
								name1 = PL_Font.getSource( name1, fc = "c4" )	#��ɫ��ʾ
						else:
							name1 = PL_Font.getSource( name1, fc = "c9" )		#��ɫ��ʾ
					except:
						name1 = ""
					try:
						name2 = SuitChildNames.pop(0)
						equipPos += 1
						id = suitlist[equipPos]
						if self.id == id :	#��װ�����б���,�����������ɫֻ�����Լ����;öȾ���
							if self.getHardiness() == 0:
								name2 = PL_Font.getSource( name2, fc = "c3" )	#��ɫ��ʾ
							else:
								name2 = PL_Font.getSource( name2, fc = "c4" )	#��ɫ��ʾ
						elif id in EquipDatas:			#�������װ����ID�����װ������ɫ��װ��LIST��
							if EquipDatas[ id ] == 0:
								name2 = PL_Font.getSource( name2, fc = "c3" )	#��ɫ��ʾ
							else:
								name2 = PL_Font.getSource( name2, fc = "c4" )	#��ɫ��ʾ
						else:
							name2 = PL_Font.getSource( name2, fc = "c9" )		#��ɫ��ʾ
					except:
						name2 = ""
					Name = (strs % name1) + "  " + (strs % name2)
					key = "suitChild%s" % index
					Name = PL_Align.getSource("C") + Name + PL_Align.getSource("L")
					self.desFrame.SetDescription( key , Name )
