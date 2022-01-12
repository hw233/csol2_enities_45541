# -*- coding: gb18030 -*-

from DroppedBox import DroppedBox
from interface.GameObject import *
import event.EventCenter as ECenter
import BigWorld
import ItemTypeEnum
from bwdebug import *
import csdefine
import GUI
import Define

modelPath = "monster/dm_bxiang_00002/dm_bxiang_00002.model"

class DroppedBoxForMonsterAttack( DroppedBox ):
	"""
	"""
	def __init__( self ):
		DroppedBox.__init__( self )



	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		return [modelPath]

	def receiveDropState( self, visibleState ):
		"""
		"""
		if visibleState:
			if (self.model == None):
				self.canPickUp = True
				rds.effectMgr.createModelBG( [modelPath], self.__onModelLoad )
				self.selectable = True	# �����ܹ���ѡ��
				BigWorld.player().onItemDrop( self )
				self.flushAttachments_()
		else:
			self.model = None
			
	def  __onModelLoad( self, model ):
		"""
		ģ�ͼ��ػص�
		"""
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		self.model = model
		rds.effectMgr.createParticleBG( self.model, "HP_sfx1", "particles/tong_tong/diaoluowupin.xml", type = Define.TYPE_PARTICLE_NPC  )