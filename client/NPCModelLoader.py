# -*- coding: gb18030 -*-

#$Id: NPCModelLoader.py,v 1.6 2008-07-25 07:55:19 yangkai Exp $

import BigWorld
from bwdebug import *
import ResMgr
import time
import Math
import csdefine
from gbref import rds
from config.client import NPCModelConfig
from config.client import vehicleSound
import Define
# ----------------------------------------------------------------------------------------------------
# NPCģ�ͼ���
# ----------------------------------------------------------------------------------------------------

class NPCModelLoader:
	"""
	NPCģ�ͼ���
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��{...}}
	@type _data: dict
	"""
	_instance = None
	DEFAULT_MODEL_PATH = "monster1/gw1257/gw1257.model"
	DEFAULT_MODEL_NUMBER = "gw1257_4"

	def __init__( self ):
		assert NPCModelLoader._instance is None, "instance already exist in"
		self._datas = NPCModelConfig.Datas
		self._vDatas = vehicleSound.Datas
		self.vehicleSoundMap = {
								csdefine.VEHICLE_ACTION_TYPE_CONJURE	: self.getVehicleConjureSound,
								csdefine.VEHICLE_ACTION_TYPE_JUMP		: self.getVehicleJumpSound,
								csdefine.VEHICLE_ACTION_TYPE_RANDOM		: self.getVehicleRASound,
								csdefine.VEHICLE_ACTION_TYPE_WALK		: self.getVehicleWalkSound,
								}
		# self._datas like as { "model_number" : { "dyes" : [(dye,tintName)...] ,"sources" : [....], "head": "" }

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = NPCModelLoader()
		return self._instance

	def getHairPath( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ�͵ķ�����Դ
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "hairPath" ]
		except:
			return ""

	def getHairDyes( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡ����ʹ��Dye
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return List like as [ ( dyeName, tintName) ... ]
		"""
		dyes = []
		data = self._datas.get( modelNumber.lower() )
		if data is None: return dyes

		dyeConfig = data.get("hairTint")
		if dyeConfig is None: return dyes
		return list( dyeConfig )

	def getModelSources( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ��ʹ����Դ·��
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "sources" ]
		except:
			return []

	def getStandbyAction( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ�ʹ�������
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "standbyAction" ]
		except:
			return ""

	def getStandbyEffect( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ�ʹ�����Ч
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "standbyEffect" ]
		except:
			return ""

	def getPreEffect( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ���볡��Ч
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "preActionEffect" ]
		except:
			return ""

	def getPreAction( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ���볡����
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "preAction" ]
		except:
			return []

	def getModelAlpha( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ��͸����
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return Float
		"""
		data = self._datas.get( modelNumber )
		if data is None: return 1.0
		return data.get( "alpha", 1.0 )

	def getModelDyes( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ��ʹ��Dye
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return List like as [ ( dyeName, tintName) ... ]
		"""
		dyes = []
		data = self._datas.get( modelNumber.lower() )
		if data is None: return dyes

		dyeConfig = data.get("dyes")
		if dyeConfig is None: return dyes
		return list( dyeConfig )

	def getHeadTexture( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ��ͷ��·��
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return String like as "maps/....."
		"""
		try:
			return self._datas[ modelNumber ][ "head" ]
		except:
			return ""

	def isStaticModel( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ���Ƿ��Ǿ�̬ģ��
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return String like as "maps/....."
		"""
		data = self._datas.get( modelNumber )
		if data is None: return False

		isStatic = data.get( "isStatic" )
		if isStatic is None: return False

		if not isStatic.isdigit(): return False

		return bool( int( isStatic ) )

	def getHps( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ�͵�ָ���󶨵�
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "hps" ]
		except:
			return []

	def getParticles( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ��ָ���󶨵�Ĺ�Ч
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "particles" ]
		except:
			return []

	def getVehicleHps( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ�͵�ָ�����󶨵�
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "vehicleHps" ]
		except:
			return []

	def getVehicleModelIDs( self, modelNumber ):
		"""
		ͨ��ģ�ͱ�Ż�ȡģ�͵�ָ����踽��ģ��ID
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "vehicleIDs" ]
		except:
			return []

#----------------������Ч���� by����-----------------
	def getMonsterOnFightSound( self, modelNumber ):
		"""
		��ù������ս����Ч
		"""
		try:
			return self._datas[ modelNumber ]["sound_onFight"]
		except:
			return ()

	def getMonsterOnDieSound( self, modelNumber ):
		"""
		��ù���������Ч
		"""
		try:
			return self._datas[ modelNumber ]["sound_onDie"]
		except:
			return ()

	def getMonsterOnAttackSound( self, modelNumber ):
		"""
		��ù��﹥����Ч
		"""
		try:
			return self._datas[ modelNumber ]["sound_onAttack"]
		except:
			return ()

	def getMonsterOnDamageSound( self, modelNumber ):
		"""
		��ù����ܹ�����Ч
		"""
		try:
			return self._datas[ modelNumber ]["sound_onDamage"]
		except:
			return ()

#----------------�����Ч���� by����-----------------
	def getVehicleSound( self, actionNum, vehicleModelNum ):
		"""
		��ö�����Ӧ�������Ч
		"""
		return self.vehicleSoundMap[actionNum]( vehicleModelNum )

	def getVehicleConjureSound( self, vehicleModelNum ):
		"""
		�������ٻ���Ч
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleConjure"]
		except:
			return ()

	def getVehicleJumpSound( self, vehicleModelNum ):
		"""
		��������Ծ��Ч
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleJump"]
		except:
			return ()

	def getVehicleRASound( self, vehicleModelNum ):
		"""
		���������������Ч RA = Random Action
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleRA"]
		except:
			return ()

	def getVehicleWalkSound( self, vehicleModelNum ):
		"""
		������������Ч
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleWalk"]
		except:
			return ()

#----------------NPC������Ч���� by����-----------------
	def getNPCVoice( self, modelNum, id ):
		"""
		���NPC������Ч
		"""
		try:
			return self._vData[modelNum]["sound_onClick"][id]
		except:
			return ()

# ----------------------------------------------------------------------

	def createStaticModel( self, modelNum, matrix, dynamic ):
		"""
		������̬ģ��
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@type  matrix: matrix
		@param matrix: �����þ�̬ģ�͵�������Ϣ
		@type  dynamic: �Ƿ�̬
		@param dynamic: ��̬�����������ƶ�������
		@return PyModelObStacle
		"""
		PyModelObStacle = None
		paths = self.getModelSources( modelNum )
		if len( paths ) == 0:
			paths = [self.DEFAULT_MODEL_PATH]

		params = list( paths )
		params.extend( [matrix, dynamic] )
		try:
			PyModelObStacle= BigWorld.PyModelObstacle( *params )
		except:
			params = [self.DEFAULT_MODEL_PATH]
			params.extend( [matrix, dynamic] )
			PyModelObStacle = BigWorld.PyModelObstacle( *params )
			WARNING_MSG( "Can't find subModel by %s, it use Default Model" % modelNum )
		return PyModelObStacle

	def getKeys( self ):
		"""
		"""
		return self._datas.keys()

	def getModelName( self, modelNumber ):
		"""
		������̬ģ��
		@type  itemModelID: string
		@param itemModelID: NPCģ�ͱ��
		@type  modelName: string
		@return: NPCģ������
		"""
		try:
			return self._datas[ modelNumber ][ "name" ]
		except:
			return ""
			
	def getUSelectSize( self, modelNumber ):
		"""
		@type  modelName: string
		@return: NPC��Ȧ��С
		"""
		try:
			return float( self._datas[ modelNumber ][ "uSelectSize" ] )
		except:
			return -1.0

	def getDieEvent( self, modelNumber ):
		"""
		��ȡ������ͷ�¼�
		"""
		try:
			return self._datas[ modelNumber ][ "dieEvent" ]
		except:
			return ""


	def createDynamicModel( self, modelNum, isReturnDeFault = True ):
		"""
		���̴߳�����̬ģ��
		@type  itemModelID	: string
		@param itemModelID	: NPCģ�ͱ��
		@type  isReturnDeFault	: Bool
		@param isReturnDeFault	: �Ƿ񷵻�һ��Ĭ��ģ��
		@return 			: PyModel
		"""
		pyModel = None

		# ��ȡ·����dye
		paths = self.getModelSources( modelNum )
		dyes = self.getModelDyes( modelNum )
		# ����ģ��
		pyModel = rds.effectMgr.createModel( paths, dyes )
		# ���ģ��Ϊ�� �򷵻�һ��Ĭ��ģ��
		if pyModel is None:
			if isReturnDeFault:
				return self.createDefaultModel()
			return None

		# ����з���
		hairPath = self.getHairPath( modelNum )
		if len( hairPath ):
			hairDyes = self.getHairDyes( modelNum )
			hairModel = rds.effectMgr.createModel( [hairPath], hairDyes )
			rds.effectMgr.linkObject( pyModel, "HP_head", hairModel )

		# ��Ч
		hps = self.getHps( modelNum )
		particles = self.getParticles( modelNum )
		particlesscale = self.getParticlesScale( modelNum )
		for hp, particle, particlescale in zip( hps, particles, particlesscale ):
			rds.effectMgr.createParticleBG( pyModel, hp, particle, type = Define.TYPE_PARTICLE_NPC, scale = particlescale )
		# ��������������
		vHps = self.getVehicleHps( modelNum )
		vModelIDs = self.getVehicleModelIDs( modelNum )
		for hp, modelID in zip( vHps, vModelIDs ):
			if hp == "" or modelID == "": continue
			vModel = self.createDynamicModel( modelID )
			if vModel is None: continue
			rds.effectMgr.linkObject( pyModel, hp, vModel )

		return pyModel

	def createDynamicModelBG( self, modelNum, onLoadCompleted ):
		"""
		���̴߳�����̬ģ�ͣ��лص� onLoadCompleted
		@type  itemModelID		: string
		@param itemModelID		: NPCģ�ͱ��
		@param onLoadCompleted	: ������ģ�ͺ�Ļص�����
		@type onLoadCompleted	: Function
		@return 				: None
		"""
		def loadCompleted( model ):
			# ���ģ��Ϊ�� �򷵻�һ��Ĭ��ģ��
			if model is None: return self.createDefaultModel()
			# ��Ч
			hps = self.getHps( modelNum )
			particles = self.getParticles( modelNum )
			particlesscale = self.getParticlesScale( modelNum )
			for hp, particle, particlescale in zip( hps, particles, particlesscale ):
				rds.effectMgr.createParticleBG( model, hp, particle, type = Define.TYPE_PARTICLE_NPC, scale = particlescale )
			# ����з���
			hairPath = self.getHairPath( modelNum )
			if len( hairPath ):
				hairDyes = self.getHairDyes( modelNum )
				hairModel = rds.effectMgr.createModel( [hairPath], hairDyes )
				rds.effectMgr.linkObject( model, "HP_head", hairModel )
			# ��������������
			vHps = self.getVehicleHps( modelNum )
			vModelIDs = self.getVehicleModelIDs( modelNum )
			for hp, modelID in zip( vHps, vModelIDs ):
				if hp == "" or modelID == "": continue
				vModel = self.createDynamicModel( modelID )
				if vModel is None: continue
				rds.effectMgr.linkObject( model, hp, vModel )

			# ����͸����
			alpha = self.getModelAlpha( modelNum )
			rds.effectMgr.setModelAlpha( model, alpha )

			if callable( onLoadCompleted ):
				onLoadCompleted( model )

		# ��ȡ·����dye
		paths = self.getModelSources( modelNum )
		dyes = self.getModelDyes( modelNum )

		# ����ģ��
		rds.effectMgr.createModelBG( paths, loadCompleted, dyes )

	def createDefaultModel( self, cb = None ):
		"""
		����Ĭ��ģ��
		"""
		# ��ȡ·����dye
		paths = self.getModelSources( self.DEFAULT_MODEL_NUMBER )
		dyes = self.getModelDyes( self.DEFAULT_MODEL_NUMBER )
		rds.effectMgr.createModelBG( paths, cb, dyes)

	def reset( self ):
		"""
		���¼�������
		�˷���Ŀǰ��������   qiulinhui�� sopportted by yangkai
		"""
		reload( NPCModelConfig )
		self._datas = NPCModelConfig.Datas

	def generateBoundingBoxFile( self, outputFile, entity ):
		"""
		�˺���������������ģ�͵�bounding box�������ָ���ļ���
		���ɵ��������ڷ������Ϳͻ������ж�entity֮��ľ��롣

		@param outputFile: string, ���ɵ����ݴ洢��·��
		@param entity: һ��������ʱ�����ɵ�ģ�͵�entity��ԭ����bounds�ļ������ȡentity��matrix
		"""
		section = ResMgr.openSection( outputFile, True )
		if section == None:
			ERROR_MSG( "can't create file", outputFile )
			return

		m2 = Math.Matrix( entity.matrix )
		for key in self._datas.iterkeys():
			path = self.getModelSources( key )
			if len( path ) == 0: continue
			try:
				model = BigWorld.Model( *path )
			except ValueError, errstr:
				ERROR_MSG( "ValueError:", errstr )
				ERROR_MSG( "ErrorModel:", key, path )
				continue
			entity.model = model
			m1 = Math.Matrix( model.bounds )
			x = m1.get(0,0) / m2.get(0,0)
			y = m1.get(1,1) / m2.get(1,1)
			z = m1.get(2,2) / m2.get(2,2)
			INFO_MSG( key, "-->", ( x, y, z ) )
			section.writeVector3( key, ( x, y, z ) )
		section.save()
		ResMgr.purge( outputFile )
		
	def getParticlesScale(self, modelNumber):
		if self._datas.has_key(modelNumber):
			if self._datas[modelNumber].has_key("particlesscale"):
				return self._datas[ modelNumber ][ "particlesscale" ]
		return self.getDefaultParticlesScale(modelNumber)
			
	def getDefaultParticlesScale(self, modelNumber):
		if self._datas.has_key(modelNumber):
			if not self._datas[modelNumber].has_key("particlesscale"):
				length = len(self.getParticles(modelNumber))
				return [1.0 for i in range(length)]
		return []

					
					

#$Log: not supported by cvs2svn $
#Revision 1.5  2008/07/08 09:37:51  yangkai
#��ӽӿ�
#createDynamicModel()
#createStaticModel()
#
#Revision 1.4  2008/03/29 08:55:31  phw
#method added: generateBoundingBoxFile()
#
#Revision 1.3  2008/02/20 04:23:16  phw
#����ת��modelNumberΪСд�Ĵ���
#
#Revision 1.2  2008/02/19 02:09:19  yangkai
#��ӽӿ�getHeadTexture
#����NPCģ��ͷ��
#
#Revision 1.1  2008/01/08 06:54:37  yangkai
#NPCģ�����ü��ش���
#