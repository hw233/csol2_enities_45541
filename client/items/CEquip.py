# -*- coding: gb18030 -*-

# $Id: CEquip.py,v 1.37 2008-07-17 02:32:51 yangkai Exp $

"""
װ�������ģ��
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
	װ��������

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
		��ȡ��Ʒ��ȫ�� �� ��ӥ������İ�����
		"""
		#if len( self.getCreateEffect() ):
		#	return self.name()
		return CItemBase.fullName( self )

	def isAlreadyWield( self ):
		"""
		�ж��Ƿ��Ѿ�װ����Ч����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_wieldStatus", 0 ) > 0

	def isSuitEffectWield( self ):
		"""
		�ж��Ƿ��Ѿ�װ������װ������

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.queryTemp( "eq_suitEffectStatus", 0 ) > 0

	def getWieldOrders( self ):
		"""
		ȡ�õ�ǰ��Ʒ�Ŀ�װ��λ���б�������Ʒ���Է���װ��������Щλ���ϣ�CEL_*

		@return: tuple of int
		@rtype:  tuple of int
		"""
		return m_cwt2cel[self.query( "eq_wieldType" )]

	def getUnwieldOrders( self, equipKitbag, equipOrder ):
		"""
		���ڵ�Ҫװ��ĳ�����͵�װ��ʱ���װ������Ҫж����Щλ�õ�װ��

		@param equipKitbag: װ����
		@type  equipKitbag: KitbagType
		@param  equipOrder: ��Ҫװ����λ��
		@type   equipOrder: INT8
		@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
		                    ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò����򷵻�None
		@rtype:             tuple of UINT8/None
		"""
		return m_unwieldCheck[self.query( "eq_wieldType" )]( equipKitbag, equipOrder )

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
		raise "I can't support yet."

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		raise "I can't support yet."

	def canWield( self, owner ):
		"""
		����Ƿ���װ����ƷЧ��

		@param owner: ���ߵ�ʹ���ߣ���ӵ���ߣ�
		@type  owner: Entity
		@return:    True ����װ����False ������װ��
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
		���ʹ��ʱ��
		"""
		lifeType = self.getLifeType()
		lifeTime = self.getLifeTime()
		if lifeType and not lifeTime: return False
		return True

	def _checkHardiness( self ):
		"""
		��鵱ǰ�;ö�
		����һ��װ�����ԣ������ǰ�;ö�ΪNone������װ�����ǿ���װ����
		@return: ����0�򲻴�����������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		hMax = self.query( "eq_hardinessMax" )
		if hMax is None or hMax <= 0: return True
		return self.query( "eq_hardiness" ) > 0

	def _checkReqGender( self, owner ):
		"""
		���װ�������Ա�

		@param owner: ��Ʒӵ����
		@type  owner: Entity
		@return: ƥ���򷵻�True, ���򷵻�False
		@rtype:  BOOL
		"""
		reqGender = self.getReqGender()
		if len( reqGender ) == 0: return True
		return owner.getGender() in reqGender

	def _getHardinessLevle( self ):
		"""
		��ȡĿǰװ�����;öȵȼ�(ո�¡���á���ɡ����𡢲�ȱ)
		"""
		hMax = self.query( "eq_hardinessLimit" )
		hCur = self.query( "eq_hardiness" )
		if int(hMax) == 0:		#�������;�Ϊ0�� ֱ�ӷ��ز�ȱ
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
		����װ��ְҵ

		@return: ƥ���򷵻�True, ���򷵻�False
		@rtype:  BOOL
		"""
		return self.isMetier( owner.getClass() )

	def _checkReqlevel( self, owner ):
		"""
		���װ���ȼ�

		@param owner: ����ӵ����
		@type  owner: Entity
		@return: ƥ���򷵻�True, ���򷵻�False
		@rtype:  BOOL
		"""
		return owner.level >= self.query( "reqLevel", 0 )

	def isMetier( self, metierType ):
		"""
		�ж��Ƿ����װ����ĳ��ְҵ��

		@parma metierType: ְҵ����; CEM_*; ����ʹ�á���(|)�������Ӷ������ʾ��ͬʱ֧����ô���ְҵװ����
		@type  metierType: UINT16
		@return: ���������ĳְҵ��װ���򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		if reqClasses is None:
			return True		# û��classes���ʾû�д�����
		return metierType in reqClasses

	def isMetierOnly( self, metierType ):
		"""
		�ж��Ƿ�ֻ��װ����ĳ��ְҵ��

		@parma metierType: ְҵ����; CEM_*
		@type  metierType: UINT16
		@return: ���ֻ����ָ����ְҵ��װ���򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		reqClasses = self.query( "reqClasses" )
		if reqClasses is None:
			return True		# û��classes���ʾû�д�����
		return reqClasses == [ metierType ]

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡװ��ר��������Ϣ
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# ���ô���������
		creator = attrMap["creator"].description( self, reference)
		if creator:
			creator = PL_Font.getSource( creator, fc = "c8" )
			self.desFrame.SetDescription("creator", creator)
		# ��ȡװ��ǿ����Ϣ����
		desIntensify = attrMap["eq_intensifyLevel"].description( self, reference )
		if desIntensify and  desIntensify > 0:
			desIn = PL_Image.getSource("guis/general/Itemattribute/" + self.texture[desIntensify-1] ) * desIntensify
			desIn = toolbox.infoTip.getItemGrid( desIn , { "newline" : False } )
			self.desFrame.SetDescription("eq_intensifyLevel", desIn)	#��������(ǿ���ȼ�)
		# ��ȡ����ְҵ�����������Լ���ְҵȷ���������ֵ���ɫ
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
		# �����Լ��ĵȼ�ȷ���������ֵ���ɫ����������ȼ�
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if desReqlevel:
			if not self._checkReqlevel( reference ):
				desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			self.desFrame.SetDescription("reqLevel",desReqlevel )
		# �����Լ����Ա�ȷ���������ֵ���ɫ����������ȼ�
		desReqGender = attrMap["reqGender"].description( self, reference )
		if desReqGender:
			if not self._checkReqGender( reference ):
				desReqGender = PL_Font.getSource( desReqGender, fc = ( 255, 0, 0 ) )
			self.desFrame.SetDescription("reqGender",desReqGender )
		# ��ȡװ����װ����λ��(˫�� ����...)
		deswWieldType = attrMap["eq_wieldType"].description( self, reference )
		self.desFrame.SetDescription("eq_wieldType",deswWieldType)
		# �;ö�,��һЩװ��û�;ã�����������ָ
		desHardiness = attrMap["eq_hardiness"].descriptionList( self, reference )
		if desHardiness != "":
			#�޸������;öȵ���ʵ��ʽ ���ղ߻��Ĺ�ʽ���������;ö���ʾ by����
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
				deslist = desHardiness[1].split( '/' )  #��Ϊֻ��ǰ�벿����ʾΪ��ɫ ���� ��'/'�и��ַ���
				deslist[0] = PL_Font.getSource( deslist[0] , fc = ( 255, 0, 0 ) )
				desHardiness[1] = deslist[0] + "/" + deslist[1]
			self.desFrame.SetDesSeveral( "eq_hardiness", [ [desHardiness[0] + " " + desHardiness[1] , self._getHardinessLevle()] ] )
		# ������װ����
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
				color = suitCFunc( desSuitEffect[-1], "c6", suitEffectColor )	# ������ֵ�ﵽ���ʱ��ʾΪ���ɫ
				suitEfDes = PL_Font.getSource( "%s %s" % ( desSuitEffect[0], desSuitEffect[1] ), fc = color )
				desSuitEffectListTemp.append( [ suitEfDes ] )
			self.desFrame.SetDesSeveral( "eq_suitEffect", desSuitEffectListTemp )
		# ��ȡ��Ч���ı�ʯͼ��
		# ���û��ͼ�� ʹ��Ĭ�ϵ�
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
		# ��ʯ��Ƕ����
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
		# ��������
		desExtraEffectList = attrMap["eq_extraEffect"].descriptionList( self, reference )
		desExtraEffectListTemp = []
		for desExtraEffect in desExtraEffectList:
			color = colorFunc( desExtraEffect[-1], "c6", ( 0, 255, 0 ) )			# ������ֵ�ﵽ���ʱ��ʾΪ���ɫ
			des = PL_Font.getSource( desExtraEffect[0] + desExtraEffect[1] , fc = color )
			desExtraEffectListTemp.append( [ des ] )
		self.desFrame.SetDesSeveral( "eq_extraEffect", desExtraEffectListTemp)		#����װ���������� ��Ӷ�������,����......

		# ��ע����
		desCreateEffectList = attrMap["eq_createEffect"].descriptionList( self, reference )
		desCreateEffectListTemp = []
		for desCreateEffect in desCreateEffectList:
			color = colorFunc( desCreateEffect[-1], "c6", "c27" )					# ������ֵ�ﵽ���ʱ��ʾΪ���ɫ
			des = PL_Font.getSource( desCreateEffect[0] + desCreateEffect[1] , fc = color )
			desCreateEffectListTemp.append( [ des ] )
		self.desFrame.SetDesSeveral( "eq_createEffect", desCreateEffectListTemp )	#����װ���������� ��Ӷ�������,����......

		# װ������
		upperName=attrMap["eq_upper"].description( self, reference )
		if upperName != "":
			temp = upperName.split()
			upperName = PL_Font.getSource( temp[0], fc = ( 255, 255, 0) ) + " "+ PL_Font.getSource( temp[1], fc = "c8" ) + " " + PL_Font.getSource( temp[2], fc = ( 255, 255, 0) )
			self.desFrame.SetDescription( "eq_upper", upperName )	#����װ�������ߵ�����

		# װ����ʱ
		lifeTypeDes = attrMap["lifeType"].description( self, reference)
		if lifeTypeDes:
			lifeTypeDes = PL_Font.getSource( lifeTypeDes, fc = "c4" )
			self.desFrame.SetDescription( "lifeType", lifeTypeDes )

	def getIntensifyLevel( self ):
		"""
		��ȡװ��ǿ���ȼ�activation
		"""
		return self.query( "eq_intensifyLevel", 0 )
	
	def model( self ):
		"""
		��ȡģ��·��
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
		��ȡ��ǰ����Ƕ����
		"""
		return self.query( "eq_slot", 0 )

	def getExtraEffect( self ):
		"""
		��ȡװ����������
		@return:    dict
		"""
		return self.query( "eq_extraEffect", {} )

	def getCreateEffect( self ):
		"""
		��ȡװ����ע����
		@return:    dict
		"""
		return self.query( "eq_createEffect", [] )

	def getLimitSlot( self ):
		"""
		��ȡ��ǰ����װ������
		"""
		return self.query( "eq_limitSlot", 0 )

	def getMaxSlot( self ):
		"""
		��ȡ���װ������
		"""
		return self.query( "eq_maxSlot", 0 )

	def canRepair( self ):
		"""
		virtual method.
		�ж�һ����Ʒ�Ƿ��ܱ�����
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
		�ж��Ƿ���װ��
		"""
		return True

	def getCreator( self, creator ):
		"""
		��ô���������
		"""
		return self.query( "creator", "" )


	def getIntensifyValue( self ):
		"""
		��ȡװ����ǿ������ֵ����
		"""
		return self.query( "intensifyValue", [ [ 0, 0 ], [ 0, 0 ] ] )

	def getHardiness( self ):
		"""
		��õ�ǰ�;ö�
		@return: ��ǰ�;ö�,���û���;ö���Ϊ0
		@rtype: int
		"""
		return self.query( "eq_hardiness", 0 )

	def getHardinessMax( self ):
		"""
		�������;ö�����(��ֵ����)
		@return: ����;ö�����,���û���;ö�������Ϊ0
		@rtype: int
		"""
		return self.query( "eq_hardinessMax", 0 )

	def getHardinessLimit( self ):
		"""
		��õ�ǰ�;ö�����(��ֵ�ܸ���)

		@return: ����;ö�,���û���;ö���Ϊ0
		@rtype: int
		"""
		return self.query( "eq_hardinessLimit", 0 )

	def getPrice( self ):
		"""
		��ȡװ���ļ۸�
		���;ö��й�
		"""
		# װ���ļ۸� = ��ǰ�;ö�/ԭʼ����;ö�*װ��ԭʼ����۸�
		basePrice = self.getRecodePrice()
		hardinessMax = self.getHardinessMax()
		if hardinessMax == 0: return basePrice
		newPrice = int( self.getHardiness() * 1.0 / self.getHardinessMax() * basePrice )
		if newPrice <= 0: return 1
		return newPrice

	def checkUseStatus( self, owner ) :
		"""
		�����Ʒ��ʹ�����
		"""
		if not self.canWield( owner ) :
			return Define.ITEM_STATUS_USELESSNESS
		elif self.getHardinessMax() > 0 and \
			self.getHardiness() / float( self.getHardinessMax() ) < 0.1 :		# �;ö�С��10%����������״̬
				return Define.ITEM_STATUS_ABRASION
		return Define.ITEM_STATUS_NATURAL
