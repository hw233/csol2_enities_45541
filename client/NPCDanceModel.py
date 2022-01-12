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
		��entity���roleInfo������
		"""
		player = BigWorld.player()
		if player is None: return

		def onCreateModelLoad( roleInfo, model ):
			"""
			��ɫ�����������������ģ�ͼ�����ص�
			"""
			def onHairModelLoad( hairModel ):
				key = "HP_head"
				rds.effectMgr.linkObject( model, key, hairModel )
			
			profession = roleInfo.getClass()
			gender = roleInfo.getGender()
			
			# ����
			rds.roleMaker.createHairModelBG( roleInfo.getHairNumber(), roleInfo.getFashionNum(), profession, gender, onHairModelLoad )
			# ����������
			#rds.roleMaker.createMWeaponModelBG( roleInfo.getRHFDict(), onLoadRightModel )
			#rds.roleMaker.createMWeaponModelBG( roleInfo.getLHFDict(), onLoadLeftModel )
			# ����
			bodyFDict = roleInfo.getBodyFDict()
			feetFDict = roleInfo.getFeetFDict()
			
			############�ز�λ�ù�Ч######################
			intensifyLevel = bodyFDict["iLevel"]
			# ���µ����巢���âЧ��(�ز�װ��ǿ����4��ʱ����)
			fsHp = rds.equipParticle.getFsHp( intensifyLevel )
			fsGx = rds.equipParticle.getFsGx( intensifyLevel, profession, gender )
			for particle in fsGx:
				rds.effectMgr.createParticleBG( model, fsHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
			# ���µĸ�ְҵ����������(�ز�װ��ǿ����6��ʱ����)
			ssHp = rds.equipParticle.getSsHp( intensifyLevel )
			ssGx = rds.equipParticle.getSsGx( intensifyLevel, profession )
			for particle in ssGx:
				rds.effectMgr.createParticleBG( model, ssHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
			# ���µ�������Χ�����������( �ز�װ��ǿ����9��ʱ���� )
			pxHp = rds.equipParticle.getPxHp( intensifyLevel )
			pxGx = rds.equipParticle.getPxGx( intensifyLevel )
			for particle in pxGx:
				rds.effectMgr.createParticleBG( model, pxHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
			
			# ���µ�������ת�⻷( �ز�װ��ǿ����9��ʱ���� )
			longHp = rds.equipParticle.getLongHp( intensifyLevel )
			longGx = rds.equipParticle.getLongGx( intensifyLevel )
			for particle in longGx:
				rds.effectMgr.createParticleBG( model, longHp, particle, None, Define.TYPE_PARTICLE_PLAYER )
				
			###########Ь�ӹ�Ч#################################
			intensifyLevel = feetFDict["iLevel"]
			dianHp = rds.equipParticle.getDianHp( intensifyLevel )
			dianGx = rds.equipParticle.getDianGx( intensifyLevel )
			for particle in dianGx:
				rds.effectMgr.createParticleBG( model, dianHp, particle, None, Define.TYPE_PARTICLE_PLAYER )	
			# ��ʦ��������Ч��
			if roleInfo.getClass() == csdefine.CLASS_MAGE:
				rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER  )

			entity.setModel( model)
			entity.uname = roleInfo.getName() 
			entity.flushAttachments_()
			rds.actionMgr.playActions(model, ["dance"])

		#roleInfo = player.getModelInfo()
		func = Functor(onCreateModelLoad, roleInfo )
		rds.roleMaker.createPartModelBG( roleInfo.getID(), roleInfo, func )	