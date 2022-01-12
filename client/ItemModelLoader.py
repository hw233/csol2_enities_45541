# -*- coding: gb18030 -*-

#$Id: ItemModelLoader.py,v 1.6 2008-08-20 09:04:14 yangkai Exp $

from bwdebug import *
import Language
from gbref import rds
import Const
import csdefine
from config.client import ItemModel
import Define


# ----------------------------------------------------------------------------------------------------
# ��Ʒģ�ͼ���
# ----------------------------------------------------------------------------------------------------
class ItemModelLoader:
	"""
	��Ʒģ�ͼ���
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��{...}}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert ItemModelLoader._instance is None, "instance already exist in"
		self._datas = ItemModel.Datas # {modelID : {"model_drop": ..., "model_rweapon": ...}...}

		self.fashionMapIndex = {	csdefine.CLASS_FIGHTER 	| csdefine.GENDER_MALE 		:	1,
									csdefine.CLASS_FIGHTER 	| csdefine.GENDER_FEMALE	:	2,
									csdefine.CLASS_SWORDMAN | csdefine.GENDER_MALE 		:	3,
									csdefine.CLASS_SWORDMAN | csdefine.GENDER_FEMALE	:	4,
									csdefine.CLASS_ARCHER 	| csdefine.GENDER_MALE 		:	5,
									csdefine.CLASS_ARCHER 	| csdefine.GENDER_FEMALE	:	6,
									csdefine.CLASS_MAGE 	| csdefine.GENDER_MALE 		:	7,
									csdefine.CLASS_MAGE 	| csdefine.GENDER_FEMALE	:	8,
									}

		self.armorMapIndex = {		csdefine.GENDER_MALE 	:	1,
									csdefine.GENDER_FEMALE	:	2,
									}

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = ItemModelLoader()
		return self._instance

	def __getSData( self, itemModelID, key ):
		"""
		"""
		data = self._datas.get( itemModelID )
		if data is None: return []
		source = data.get( key )
		if source is None: return []
		return list( source )

	def getDropModelByID( self, itemModelID, isReturnDeFault = True ):
		"""
		����ģ�ͱ��ID��ȡ����ģ��·��
		����Ҳ����򷵻�Ĭ��ģ��

		@type  itemModelID: string
		@param itemModelID: ��Ʒģ�ͱ��
		"""
		dropModelPath = ""
		if isReturnDeFault:
			dropModelPath = "dlwp/dm_fj_tb_00001.model"
		dropModelPaths = self.__getSData( itemModelID, "model_drop" )
		if len( dropModelPaths ): return dropModelPaths[0]
		return dropModelPath

	def getGSource( self, itemModelID, gender ):
		"""
		����ģ�ͱ�ź��Ա��ȡ��������Դ
		"""
		if gender is None: return []
		index = self.armorMapIndex.get( gender )
		if index is None: return []
		return self.__getSData( itemModelID, "model_source%s" % index )

	def getGDyes( self, itemModelID, gender ):
		"""
		����ģ�ͱ�ź��Ա��ȡ������Dyes

		@type  itemModelID: string
		@param itemModelID: ��Ʒģ�ͱ��
		"""
		if gender is None: return []
		index = self.armorMapIndex.get( gender )
		if index is None: return []
		return self.__getSData( itemModelID, "model_tint%s" % index )

	def getSHeadSource( self, itemModelID, gender, profession ):
		"""
		������Ʒģ�ͱ�ţ�ְҵ�Ա𣬻�ȡʱװ��Դ����ͷ��·��

		@type  itemModelID	: string
		@param itemModelID	: ��Ʒģ�ͱ��
		@type  gender		: Uint8
		@param gender		: �Ա�
		@type  profession	: Uint8
		@param profession	: ְҵ
		@return list of string
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_headSource%s" % index
		return self.__getSData( itemModelID, key )

	def getSHeadDyes( self, itemModelID, gender, profession ):
		"""
		����ģ�ͱ��ID��ȡʱװ��Դ����ͷ��Dyes

		@type  itemModelID	: string
		@param itemModelID	: ��Ʒģ�ͱ��
		@type  gender		: Uint8
		@param gender		: �Ա�
		@type  profession	: Uint8
		@param profession	: ְҵ
		@return list of (tint, dye)
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_tint%s" % index
		return self.__getSData( itemModelID, key )

	def getSSource( self, itemModelID, gender, profession ):
		"""
		������Ʒģ�ͱ�ţ�ְҵ�Ա𣬻�ȡʱװ��Դ·��

		@type  itemModelID	: string
		@param itemModelID	: ��Ʒģ�ͱ��
		@type  gender		: Uint8
		@param gender		: �Ա�
		@type  profession	: Uint8
		@param profession	: ְҵ
		@return list of string
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_source%s" % index
		return self.__getSData( itemModelID, key )

	def getSDyes( self, itemModelID, gender, profession ):
		"""
		����ģ�ͱ��ID��ȡ��ģ��Tint��

		@type  itemModelID	: string
		@param itemModelID	: ��Ʒģ�ͱ��
		@type  gender		: Uint8
		@param gender		: �Ա�
		@type  profession	: Uint8
		@param profession	: ְҵ
		@return list of (tint, dye)
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_tint%s" % index
		return self.__getSData( itemModelID, key )

	def getSEffects( self, itemModelID, gender, profession ):
		"""
		������Ʒģ�ͱ�ţ�ְҵ�Ա𣬻�ȡʱװ�󶨵�
		@type  itemModelID	: string
		@param itemModelID	: ��Ʒģ�ͱ��
		@type  gender		: Uint8
		@param gender		: �Ա�
		@type  profession	: Uint8
		@param profession	: ְҵ
		@return list of string
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_effect%s" % index
		return self.__getSData( itemModelID, key )

	def getMSource( self, itemModelID ):
		"""
		��ȡ��Ҫ�ı���ģ��
		����Ƿ����࣬���ȡ�������Է���ģ��
		����������࣬���ȡ������������ģ��
		"""
		return self.__getSData( itemModelID, "model_source1" )

	def getMDyes( self, itemModelID ):
		"""
		����ģ�ͱ��ID��ȡ��ģ��Dyes

		@type  itemModelID: string
		@param itemModelID: ��Ʒģ�ͱ��
		"""
		return self.__getSData( itemModelID, "model_tint1" )

	def getMEffects( self, itemModelID ):
		"""
		��ȡ��Ҫ�ı���ģ��Ч��
		"""
		return self.__getSData( itemModelID, "model_effect1" )

	def getFSource( self, itemModelID ):
		"""
		��ȡ��Ҫ�ı���ģ��
		����Ƿ����࣬���ȡ����Ů�Է���ģ��
		����������࣬���ȡ������������ģ��
		"""
		return self.__getSData( itemModelID, "model_source2" )

	def getFDyes( self, itemModelID ):
		"""
		����ģ�ͱ��ID��ȡ��ģ��Dyes

		@type  itemModelID: string
		@param itemModelID: ��Ʒģ�ͱ��
		"""
		return self.__getSData( itemModelID, "model_tint1" )
		
	def getActionsName( self, itemModelID ):
		"""
		����ģ�ͱ��ID��ȡ��ģ�Ͷ���

		@type  itemModelID: string
		@param itemModelID: ��Ʒģ�ͱ��
		"""
		actionsList = self.__getSData( itemModelID, "model_action" )
		if len( actionsList ):return actionsList[0]
		
	def getTimetick( self, itemModelID ):
		"""
		����ģ�ͱ��ID��ȡ��ģ�Ͷ������

		@type  itemModelID: string
		@param itemModelID: ��Ʒģ�ͱ��
		"""
		timeList = self.__getSData( itemModelID, "model_timetick" )
		if len( timeList ):return timeList[0]

	def isShine( self, itemModelID ):
		"""
		����ģ�ͱ��ID�ж��Ƿ��Է���

		@type  itemModelID: string
		@param itemModelID: ��Ʒģ�ͱ��
		"""
		try:
			return self._datas[itemModelID]["model_isShine"]
		except:
			return False

	def reset( self ):
		"""
		���¼��� itemModel ����
		"""
		reload( ItemModel )
		self._datas = ItemModel.Datas

	def createModel( self, itemModelID, callback = None ):
		"""
		�����̸߳���itemModelID ��������ģ��
		@type  itemModelID	: string
		@param itemModelID	: ��Ʒģ�ͱ��
		@return				��PyModel
		"""
		# ��ȡ·����Ϣ
		paths = self.getMSource( itemModelID )
		dyes = self.getMDyes( itemModelID )
		# ����ģ��
		model = rds.effectMgr.createModel( paths, dyes )
		
		# �Է���
		isShine = self.isShine( itemModelID )
		if isShine:
			weaponKey = paths[0]
			type = rds.equipParticle.getWType( weaponKey )
			texture = rds.equipParticle.getWTexture( weaponKey )
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, Const.NPC_SHINE_INTENSIFY )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )
		if callable( callback ):
			callback( model )
		return model

	def createModelBG( self, itemModelID, onLoadCompleted ):
		"""
		�ں��̸߳���itemModelID ��������ģ��
		@type  itemModelID	: string
		@param itemModelID	: ��Ʒģ�ͱ��
		@return				��None
		"""
		def loadCompleted( model ):
			# �Է���
			isShine = self.isShine( itemModelID )
			if isShine:
				weaponKey = paths[0]
				type = rds.equipParticle.getWType( weaponKey )
				texture = rds.equipParticle.getWTexture( weaponKey )
				colour = rds.equipParticle.getWColour( weaponKey )
				scale = rds.equipParticle.getWScale( weaponKey, Const.NPC_SHINE_INTENSIFY )
				offset = rds.equipParticle.getWOffset( weaponKey )
				rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )
			if callable( onLoadCompleted ):
				onLoadCompleted( model )

		# ��ȡ·����Ϣ
		paths = self.getMSource( itemModelID )
		dyes = self.getMDyes( itemModelID )
		# ����ģ��
		rds.effectMgr.createModelBG( paths, loadCompleted, dyes )

#$Log: not supported by cvs2svn $
#Revision 1.5  2008/07/08 09:36:33  yangkai
#������ʼ����ʽ��
#
#Revision 1.4  2008/03/20 03:31:35  yangkai
#no message
#
#Revision 1.3  2007/12/14 07:55:21  yangkai
#��������ģ��Dye��ͼ��Сbug
#
#Revision 1.2  2007/11/27 01:52:30  phw
#����ְҵ��������ǰ׺'CLASS_'�������Ա��������ǰ׺'GENDER_'����ԭ����սʿ'FIGHTER'��Ϊ'CLASS_FIGHTER'��������ͬ
#
#Revision 1.1  2007/11/23 07:40:46  yangkai
#�����µ���Ʒ����ģ�ͱ����޸ĵ�����Ʒģ�ͼ��ط�ʽ
#