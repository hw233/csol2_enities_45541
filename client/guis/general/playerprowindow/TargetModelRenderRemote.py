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
		self.bgTexture = "guis/general/playerprowindow/equippanel/renderBg.tga"		# ������ͼ
		self.mapping = util.getGuiMapping( ( 256, 512 ), 8, 248, 104, 429 )

		self.__cfgDatas = PyConfiger().read( self.__cc_config, {} )					# ��ɫģ��λ������
		self.__profession = -1														# ��ɫְҵ

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onModelChanged_( self, oldModel ) :
		"""
		ģ�͸ı�ʱ������
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
		�����ǰ��ʾ��ģ��
		"""
		self.__profession = -1
		self.setModel( None )

	def resetModel( self, roleInfoDict, fashionNum ) :
		"""
		��������ģ��
		"""
		self.setModel( None )
		def callback( model ):
			self.setModel( model )
			# ����
			onHairChanged()
			# ����
			onLeftHandChanged()
			# ����
			onRightHandChanged()
			# ��ʾ���ϵ�װ������Ч��
			if not fashionNum:
				self.__createBodyEffectBG( model, bodyFDict, raceclass )
				self.__createFeetEffectBG( model, feetIntensifyLevel )
			self.onModelCreated_( model )	#ģ�ͼ�����ɻص�

		def onHairChanged():
			"""
			���͸ı�֪ͨ
			"""
			def callback( model ):
				rds.effectMgr.linkObject( self.model, "HP_head", model )
			hairNumber = roleInfoDict["hairNumber"]
			rds.roleMaker.createHairModelBG( hairNumber, fashionNum, profession, gender, callback )

		def onLeftHandChanged():
			"""
			��ɫ������������֪ͨ
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
			��ɫ������������֪ͨ
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
		roleInfo = RoleInfo( roleInfoDict )		#ȷ��roleInfoDict��RoleMaker��Ҫ����Ϣһ��
		roleInfo.update( {"fashionNum" : fashionNum } )
		showModels = rds.roleMaker.getShowModelPath( roleInfo )
		partModels = rds.roleMaker.getPartModelPath( roleInfo )
		rds.roleMaker.createPartModelBG( roleID, roleInfo, callback )
		
	def __createBodyEffectBG( self, model,bodyFDict,raceclass, callback = None ):
		"""
		�ز���Ч
		"""
		profession = raceclass & csdefine.RCMASK_CLASS
		gender = raceclass & csdefine.RCMASK_GENDER
		intensifyLevel = bodyFDict["iLevel"]
		# ���µ����巢���âЧ��(�ز�װ��ǿ����4��ʱ����)
		fsHp = rds.equipParticle.getFsHp( intensifyLevel )
		fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
		for particle in fsGx:
			rds.effectMgr.createParticleBG( model, fsHp, particle, callback, self.getParticleType() )

		# ���µĸ�ְҵ����������(�ز�װ��ǿ����6��ʱ����)
		ssHp = rds.equipParticle.getSsHp( intensifyLevel )
		ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
		for particle in ssGx:
			rds.effectMgr.createParticleBG( model, ssHp, particle, callback, self.getParticleType() )

		# ���µ�������Χ�����������( �ز�װ��ǿ����9��ʱ���� )
		pxHp = rds.equipParticle.getPxHp( intensifyLevel )
		pxGx = rds.equipParticle.getPxGx( intensifyLevel )
		for particle in pxGx:
			rds.effectMgr.createParticleBG( model, pxHp, particle, callback, self.getParticleType() )

		# ���µ�������ת�⻷( �ز�װ��ǿ����9��ʱ���� )
		longHp = rds.equipParticle.getLongHp( intensifyLevel )
		longGx = rds.equipParticle.getLongGx( intensifyLevel )
		for particle in longGx:
			rds.effectMgr.createParticleBG( model, longHp, particle, callback, self.getParticleType() )

	def __createFeetEffectBG( self, model, feetIntensifyLevel, callback = None ):
		"""
		Ь�ӹ�Ч
		"""
		intensifyLevel = feetIntensifyLevel
		dianHp = rds.equipParticle.getDianHp( intensifyLevel )
		dianGx = rds.equipParticle.getDianGx( intensifyLevel )
		for particle in dianGx:
			rds.effectMgr.createParticleBG( model, dianHp, particle, callback, self.getParticleType() )
			