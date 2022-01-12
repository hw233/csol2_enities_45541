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
# NPC模型加载
# ----------------------------------------------------------------------------------------------------

class NPCModelLoader:
	"""
	NPC模型加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：{...}}
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
		通过模型编号获取模型的发型资源
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "hairPath" ]
		except:
			return ""

	def getHairDyes( self, modelNumber ):
		"""
		通过模型编号获取发型使用Dye
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
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
		通过模型编号获取模型使用资源路径
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "sources" ]
		except:
			return []

	def getStandbyAction( self, modelNumber ):
		"""
		通过模型编号获取模型待机动作
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "standbyAction" ]
		except:
			return ""

	def getStandbyEffect( self, modelNumber ):
		"""
		通过模型编号获取模型待机光效
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "standbyEffect" ]
		except:
			return ""

	def getPreEffect( self, modelNumber ):
		"""
		通过模型编号获取模型入场光效
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "preActionEffect" ]
		except:
			return ""

	def getPreAction( self, modelNumber ):
		"""
		通过模型编号获取模型入场动作
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return List like as [ "...", "...",... ]
		"""
		try:
			return self._datas[ modelNumber ][ "preAction" ]
		except:
			return []

	def getModelAlpha( self, modelNumber ):
		"""
		通过模型编号获取模型透明度
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return Float
		"""
		data = self._datas.get( modelNumber )
		if data is None: return 1.0
		return data.get( "alpha", 1.0 )

	def getModelDyes( self, modelNumber ):
		"""
		通过模型编号获取模型使用Dye
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
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
		通过模型编号获取模型头像路径
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return String like as "maps/....."
		"""
		try:
			return self._datas[ modelNumber ][ "head" ]
		except:
			return ""

	def isStaticModel( self, modelNumber ):
		"""
		通过模型编号获取模型是否是静态模型
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
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
		通过模型编号获取模型的指定绑定点
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "hps" ]
		except:
			return []

	def getParticles( self, modelNumber ):
		"""
		通过模型编号获取模型指定绑定点的光效
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "particles" ]
		except:
			return []

	def getVehicleHps( self, modelNumber ):
		"""
		通过模型编号获取模型的指定骑宠绑定点
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "vehicleHps" ]
		except:
			return []

	def getVehicleModelIDs( self, modelNumber ):
		"""
		通过模型编号获取模型的指定骑宠附加模型ID
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@return list of string
		"""
		try:
			return self._datas[ modelNumber ][ "vehicleIDs" ]
		except:
			return []

#----------------怪物音效配置 by姜毅-----------------
	def getMonsterOnFightSound( self, modelNumber ):
		"""
		获得怪物进入战斗音效
		"""
		try:
			return self._datas[ modelNumber ]["sound_onFight"]
		except:
			return ()

	def getMonsterOnDieSound( self, modelNumber ):
		"""
		获得怪物死亡音效
		"""
		try:
			return self._datas[ modelNumber ]["sound_onDie"]
		except:
			return ()

	def getMonsterOnAttackSound( self, modelNumber ):
		"""
		获得怪物攻击音效
		"""
		try:
			return self._datas[ modelNumber ]["sound_onAttack"]
		except:
			return ()

	def getMonsterOnDamageSound( self, modelNumber ):
		"""
		获得怪物受攻击音效
		"""
		try:
			return self._datas[ modelNumber ]["sound_onDamage"]
		except:
			return ()

#----------------骑宠音效配置 by姜毅-----------------
	def getVehicleSound( self, actionNum, vehicleModelNum ):
		"""
		获得动作对应的骑宠音效
		"""
		return self.vehicleSoundMap[actionNum]( vehicleModelNum )

	def getVehicleConjureSound( self, vehicleModelNum ):
		"""
		获得骑宠召唤音效
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleConjure"]
		except:
			return ()

	def getVehicleJumpSound( self, vehicleModelNum ):
		"""
		获得骑宠跳跃音效
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleJump"]
		except:
			return ()

	def getVehicleRASound( self, vehicleModelNum ):
		"""
		获得骑宠随机动作音效 RA = Random Action
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleRA"]
		except:
			return ()

	def getVehicleWalkSound( self, vehicleModelNum ):
		"""
		获得骑宠行走音效
		"""
		try:
			return self._vDatas[ vehicleModelNum ]["sound_onVehicleWalk"]
		except:
			return ()

#----------------NPC发音音效配置 by姜毅-----------------
	def getNPCVoice( self, modelNum, id ):
		"""
		获得NPC发音音效
		"""
		try:
			return self._vData[modelNum]["sound_onClick"][id]
		except:
			return ()

# ----------------------------------------------------------------------

	def createStaticModel( self, modelNum, matrix, dynamic ):
		"""
		创建静态模型
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@type  matrix: matrix
		@param matrix: 包含该静态模型的缩放信息
		@type  dynamic: 是否动态
		@param dynamic: 动态则允许自由移动和缩放
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
		创建静态模型
		@type  itemModelID: string
		@param itemModelID: NPC模型编号
		@type  modelName: string
		@return: NPC模型名称
		"""
		try:
			return self._datas[ modelNumber ][ "name" ]
		except:
			return ""
			
	def getUSelectSize( self, modelNumber ):
		"""
		@type  modelName: string
		@return: NPC光圈大小
		"""
		try:
			return float( self._datas[ modelNumber ][ "uSelectSize" ] )
		except:
			return -1.0

	def getDieEvent( self, modelNumber ):
		"""
		获取死亡镜头事件
		"""
		try:
			return self._datas[ modelNumber ][ "dieEvent" ]
		except:
			return ""


	def createDynamicModel( self, modelNum, isReturnDeFault = True ):
		"""
		主线程创建动态模型
		@type  itemModelID	: string
		@param itemModelID	: NPC模型编号
		@type  isReturnDeFault	: Bool
		@param isReturnDeFault	: 是否返回一个默认模型
		@return 			: PyModel
		"""
		pyModel = None

		# 获取路径和dye
		paths = self.getModelSources( modelNum )
		dyes = self.getModelDyes( modelNum )
		# 创建模型
		pyModel = rds.effectMgr.createModel( paths, dyes )
		# 如果模型为空 则返回一个默认模型
		if pyModel is None:
			if isReturnDeFault:
				return self.createDefaultModel()
			return None

		# 如果有发型
		hairPath = self.getHairPath( modelNum )
		if len( hairPath ):
			hairDyes = self.getHairDyes( modelNum )
			hairModel = rds.effectMgr.createModel( [hairPath], hairDyes )
			rds.effectMgr.linkObject( pyModel, "HP_head", hairModel )

		# 光效
		hps = self.getHps( modelNum )
		particles = self.getParticles( modelNum )
		particlesscale = self.getParticlesScale( modelNum )
		for hp, particle, particlescale in zip( hps, particles, particlesscale ):
			rds.effectMgr.createParticleBG( pyModel, hp, particle, type = Define.TYPE_PARTICLE_NPC, scale = particlescale )
		# 如果是骑宠类配置
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
		后线程创建动态模型，有回调 onLoadCompleted
		@type  itemModelID		: string
		@param itemModelID		: NPC模型编号
		@param onLoadCompleted	: 创建好模型后的回调函数
		@type onLoadCompleted	: Function
		@return 				: None
		"""
		def loadCompleted( model ):
			# 如果模型为空 则返回一个默认模型
			if model is None: return self.createDefaultModel()
			# 光效
			hps = self.getHps( modelNum )
			particles = self.getParticles( modelNum )
			particlesscale = self.getParticlesScale( modelNum )
			for hp, particle, particlescale in zip( hps, particles, particlesscale ):
				rds.effectMgr.createParticleBG( model, hp, particle, type = Define.TYPE_PARTICLE_NPC, scale = particlescale )
			# 如果有发型
			hairPath = self.getHairPath( modelNum )
			if len( hairPath ):
				hairDyes = self.getHairDyes( modelNum )
				hairModel = rds.effectMgr.createModel( [hairPath], hairDyes )
				rds.effectMgr.linkObject( model, "HP_head", hairModel )
			# 如果是骑宠类配置
			vHps = self.getVehicleHps( modelNum )
			vModelIDs = self.getVehicleModelIDs( modelNum )
			for hp, modelID in zip( vHps, vModelIDs ):
				if hp == "" or modelID == "": continue
				vModel = self.createDynamicModel( modelID )
				if vModel is None: continue
				rds.effectMgr.linkObject( model, hp, vModel )

			# 设置透明度
			alpha = self.getModelAlpha( modelNum )
			rds.effectMgr.setModelAlpha( model, alpha )

			if callable( onLoadCompleted ):
				onLoadCompleted( model )

		# 获取路径和dye
		paths = self.getModelSources( modelNum )
		dyes = self.getModelDyes( modelNum )

		# 创建模型
		rds.effectMgr.createModelBG( paths, loadCompleted, dyes )

	def createDefaultModel( self, cb = None ):
		"""
		创建默认模型
		"""
		# 获取路径和dye
		paths = self.getModelSources( self.DEFAULT_MODEL_NUMBER )
		dyes = self.getModelDyes( self.DEFAULT_MODEL_NUMBER )
		rds.effectMgr.createModelBG( paths, cb, dyes)

	def reset( self ):
		"""
		重新加载数据
		此方法目前仅调试用   qiulinhui， sopportted by yangkai
		"""
		reload( NPCModelConfig )
		self._datas = NPCModelConfig.Datas

	def generateBoundingBoxFile( self, outputFile, entity ):
		"""
		此函数用于生成所有模型的bounding box并输出到指定文件；
		生成的数据用于服务器和客户端中判断entity之间的距离。

		@param outputFile: string, 生成的数据存储的路径
		@param entity: 一个用来临时绑定生成的模型的entity。原因是bounds的计算必须取entity的matrix
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
#添加接口
#createDynamicModel()
#createStaticModel()
#
#Revision 1.4  2008/03/29 08:55:31  phw
#method added: generateBoundingBoxFile()
#
#Revision 1.3  2008/02/20 04:23:16  phw
#加入转换modelNumber为小写的处理
#
#Revision 1.2  2008/02/19 02:09:19  yangkai
#添加接口getHeadTexture
#用于NPC模型头像
#
#Revision 1.1  2008/01/08 06:54:37  yangkai
#NPC模型配置加载代码
#