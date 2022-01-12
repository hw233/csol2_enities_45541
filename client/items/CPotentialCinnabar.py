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
	Ǳ�ܵ�
	"""
	def description( self, reference ):
		"""
		��������
		@param reference: ���entity,��ʾ��˭����Ϊ���������Ĳ�����
		@type  reference: Entity
		@return:          ��Ʒ���ַ�������
		@rtype:           ARRAY of str
		"""
		# description��ֱ�ӷ�����ʾ�Ľ����description���self.desFrame���ã����븴�ƴ������ƴ��룬���ֱ�ӵ���description
		# Ȼ���ٶ���Ҫ���Ի��������������á�description������self.desFrameȻ�󷵻������ڽṹ����˵������Ӧ�ð����ú�
		# ��÷ֿ�����˿��Է���������������ݣ��Ժ�Ҫ�����Ż���
		# ��ʾ��Ʒ�����Ϣ
		self.getProDescription( reference )	#��ʾ��Ʒ�������Ϣ

		attrMap = ItemAttrClass.m_itemAttrMap
		# ��ʾ��Ʒ���֣�������Ʒ��Ʒ�ʾ�����Ʒ���ֵ���ɫ
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = self.getQualityColor() )
		self.desFrame.SetDescription("name" , nameDes)
		# ��Ʒ����
		desType = attrMap["type"].description( self, reference )
		self.desFrame.SetDescription( "type", desType )
		# ��������
		reqCredits = attrMap["reqCredit"].descriptionDict( self, reference )
		if reqCredits:
			reqCreditsDes = reqCredits.keys()
			for index in xrange( len( reqCreditsDes) ):
				if not reqCredits[ reqCreditsDes[index] ]:
					reqCreditsDes[ index ] = PL_Font.getSource( reqCreditsDes[ index ] , fc = "c3" )
			self.desFrame.SetDesSeveral( "reqCredit", reqCreditsDes )
		#�Ƿ������� by����
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
		#�Ƿ��
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			desBind = PL_Font.getSource( desBind , fc = "c1" )
			self.desFrame.SetDescription( "bindType", desBind )
		#�Ƿ�Ψһ
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CItemBase[1] )
		# �Ƿ�ɳ���
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CItemBase[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )
		# ȡ�ö��������1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 % self.getLevel() )	# ��Ҫ��ʾǱ�ܵ�����
		# ȡ�ö��������2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
		#	if des1 != "": des2 = g_newLine + des2
			self.desFrame.SetDescription( "describe2", des2 )
		# ȡ�ö��������3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
		#	if des1 != "" or des2 != "": des3 = g_newLine + des3
			self.desFrame.SetDescription( "describe3", des3 )

		# ʣ��ʹ��ʱ��
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

						# �޸�ʱ���������ʾ by����
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
	
	