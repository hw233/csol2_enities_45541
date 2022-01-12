# -*- coding: gb18030 -*-

"""This module implements the Chapman for client.

@requires: L{ChapmanBase<ChapmanBase>}, L{Role<Role>}
"""
# $Id: Chapman.py,v 1.36 2008-08-11 02:40:55 huangyongwei Exp $

import BigWorld
from bwdebug import *
import NPC
import Math
import math
import GUI
import GUIFacade
from gbref import rds
from Function import Functor
import csdefine
import Const
import Define

from utils import *



class NPCDanceModel( NPC.NPC ):
	"""

	"""
	def __init__( self ):
		NPC.NPC.__init__( self )
		
	def onChangedModel( entity, roleInfo ):
		"""
		让entity变成roleInfo的样子
		"""
		player = BigWorld.player()
		if player is None: return

		def onCreateModelLoad( roleInfo, model ):
			"""
			角色创建画面的整个身体模型加载完回调
			"""
			def onHairModelLoad( hairModel ):
				key = "HP_head"
				rds.effectMgr.linkObject( model, key, hairModel )
			
			profession = roleInfo.getClass()
			gender = roleInfo.getGender()
			
			# 发型
			rds.roleMaker.createHairModelBG( roleInfo.getHairNumber(), roleInfo.getFashionNum(), profession, gender, onHairModelLoad )
			# 左右手武器
			#rds.roleMaker.createMWeaponModelBG( roleInfo.getRHFDict(), onLoadRightModel )
			#rds.roleMaker.createMWeaponModelBG( roleInfo.getLHFDict(), onLoadLeftModel )
			# 发光
			bodyFDict = roleInfo.getBodyFDict()
			feetFDict = roleInfo.getFeetFDict()
			
			############胸部位置光效######################
			intensifyLevel = bodyFDict["iLevel"]
			# 绑定新的身体发射光芒效果(胸部装备强化至4星时出现)
			fsHp = rds.equipParticle.getFsHp( intensifyLevel )
			fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
			for particle in fsGx:
				rds.effectMgr.createParticleBG( model, fsHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
			# 绑定新的各职业向上升光线(胸部装备强化至6星时出现)
			ssHp = rds.equipParticle.getSsHp( intensifyLevel )
			ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
			for particle in ssGx:
				rds.effectMgr.createParticleBG( model, ssHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
			# 绑定新的身体周围盘旋上升光带( 胸部装备强化至9星时出现 )
			pxHp = rds.equipParticle.getPxHp( intensifyLevel )
			pxGx = rds.equipParticle.getPxGx( intensifyLevel )
			for particle in pxGx:
				rds.effectMgr.createParticleBG( model, pxHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
			# 绑定新的龙型旋转光环( 胸部装备强化至9星时出现 )
			longHp = rds.equipParticle.getLongHp( intensifyLevel )
			longGx = rds.equipParticle.getLongGx( intensifyLevel )
			for particle in longGx:
				rds.effectMgr.createParticleBG( model, longHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
				
			###########鞋子光效#################################
			intensifyLevel = feetFDict["iLevel"]
			dianHp = rds.equipParticle.getDianHp( intensifyLevel )
			dianGx = rds.equipParticle.getDianGx( intensifyLevel )
			for particle in dianGx:
				rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )	
			# 法师特有粒子效果
			if roleInfo.getClass() == csdefine.CLASS_MAGE:
				rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER  )

			entity.setModel( model)
			entity.uname = roleInfo.getName() 
			entity.flushAttachments_()
			rds.actionMgr.playActions(model, ["dance"])

		#roleInfo = player.getModelInfo()
		func = Functor(onCreateModelLoad, roleInfo )
		rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )	