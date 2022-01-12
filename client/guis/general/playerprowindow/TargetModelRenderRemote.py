# -*- coding: gb18030 -*-
#

from gbref import PyConfiger
from guis import *
from guis.controls.ModelRender import ModelRender
from gbref import rds
import csdefine
import Define
from RoleMaker import RoleInfo

class TargetModelRenderRemote( ModelRender ) :
	__cc_config = "config/client/uimodel_configs/role.py"

	def __init__( self, mirror ) :
		ModelRender.__init__( self, mirror )
		self.bgTexture = "guis/general/playerprowindow/equippanel/renderBg.tga"		# 背景贴图
		self.mapping = util.getGuiMapping( ( 256, 512 ), 8, 248, 104, 429 )

		self.__cfgDatas = PyConfiger().read( self.__cc_config, {} )					# 角色模型位置配置
		self.__profession = -1														# 角色职业

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onModelChanged_( self, oldModel ) :
		"""
		模型改变时被调用
		"""
		if self.__profession >= 0 :
			viewInfo = self.__cfgDatas.get( self.__profession, None )
			if viewInfo :
				self.modelPos = viewInfo["position"]
				self.pitch = viewInfo["pitch"]
			self.playAction()
		ModelRender.onModelChanged_( self, oldModel )
		
	#-----------------------------------------------------------------
	def onModelCreated_( self, model ):
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def clearModel( self ) :
		"""
		清除当前显示的模型
		"""
		self.__profession = -1
		self.setModel( None )

	def resetModel( self, roleInfoDict, fashionNum ) :
		"""
		重新设置模型
		"""
		self.setModel( None )
		def callback( model ):
			self.setModel( model )
			# 发型
			onHairChanged()
			# 左手
			onLeftHandChanged()
			# 右手
			onRightHandChanged()
			# 显示身上的装备粒子效果
			if not fashionNum:
				self.__createBodyEffectBG( model, bodyFDict, raceclass )
				self.__createFeetEffectBG( model, feetIntensifyLevel )
			self.onModelCreated_( model )	#模型加载完成回调

		def onHairChanged():
			"""
			发型改变通知
			"""
			def callback( model ):
				rds.effectMgr.linkObject( self.model, "HP_head", model )
			hairNumber = roleInfoDict["hairNumber"]
			rds.roleMaker.createHairModelBG( hairNumber, fashionNum, profession, gender, callback )

		def onLeftHandChanged():
			"""
			角色更换左手武器通知
			"""
			def callback( model ):
				BigWorld.player().weaponAttachEffect( model, roleInfoDict["lefthandFDict"], Define.TYPE_PARTICLE_OP)
				key = "HP_left_shield"
				if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
					key = "HP_left_hand"
				rds.effectMgr.linkObject( self.model, key, model )

			lefthandFDict = roleInfoDict["lefthandFDict"]
			rds.roleMaker.createMWeaponModelBG( lefthandFDict, callback )

		def onRightHandChanged():
			"""
			角色更换右手武器通知
			"""
			def callback( model ):
				BigWorld.player().weaponAttachEffect( model, roleInfoDict["righthandFDict"], Define.TYPE_PARTICLE_OP )
				key = "HP_right_hand"
				rds.effectMgr.linkObject( self.model, key, model )

			righthandFDict = roleInfoDict["righthandFDict"]
			rds.roleMaker.createMWeaponModelBG( righthandFDict, callback )
		
		raceclass = roleInfoDict["raceclass"]
		profession = raceclass & csdefine.RCMASK_CLASS
		gender = raceclass & csdefine.RCMASK_GENDER
		bodyFDict = roleInfoDict["bodyFDict"]
		feetFDict = roleInfoDict["feetFDict"]
		feetIntensifyLevel = feetFDict["iLevel"]
		bodyIntensifyLevel = bodyFDict["iLevel"]
		
		self.__profession = profession
		roleID = roleInfoDict["roleID"]
		roleInfo = RoleInfo( roleInfoDict )		#确保roleInfoDict和RoleMaker需要的信息一致
		roleInfo.update( {"fashionNum" : fashionNum } )
		showModels = rds.roleMaker.getShowModelPath( roleInfo )
		partModels = rds.roleMaker.getPartModelPath( roleInfo )
		rds.roleMaker.createPartModelBG( roleID, roleInfo, callback )
		
	def __createBodyEffectBG( self, model,bodyFDict,raceclass, callback = None ):
		"""
		胸部光效
		"""
		profession = raceclass & csdefine.RCMASK_CLASS
		gender = raceclass & csdefine.RCMASK_GENDER
		intensifyLevel = bodyFDict["iLevel"]
		# 绑定新的身体发射光芒效果(胸部装备强化至4星时出现)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, callback, self.getParticleType() )

		# 绑定新的各职业向上升光线(胸部装备强化至6星时出现)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, callback, self.getParticleType() )

		# 绑定新的身体周围盘旋上升光带( 胸部装备强化至9星时出现 )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, callback, self.getParticleType() )

		# 绑定新的龙型旋转光环( 胸部装备强化至9星时出现 )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, callback, self.getParticleType() )

	def __createFeetEffectBG( self, model, feetIntensifyLevel, callback = None ):
		"""
		鞋子光效
		"""
		intensifyLevel = feetIntensifyLevel
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, callback, self.getParticleType() )
			