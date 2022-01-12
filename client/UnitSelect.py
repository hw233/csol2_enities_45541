# -*- coding: gb18030 -*-

"""
ʵ�ֵر��ǵĹ�Ȧ

2010.05.05: rewriten by huangyongwei
"""

import BigWorld
from bwdebug import *
import Const
from gbref import rds
from AbstractTemplates import Singleton
import csdefine

class UnitSelect( Singleton ) :
	def __init__( self ) :
		self.__moveGuideModel = None				# ��������棬ָʾ��ɫ�ƶ��Ĺ�Ȧ

		self.textureName_g = "gzawu/unitselect/unitselectcircle_g.dds"
		self.textureName_r = "gzawu/unitselect/unitselectcircle_r.dds"

		self.__targetModel = None
		self.targetSelect = BigWorld.UnitSelect()	# ѡ��Ȧ
		self.__focusModel = None
		self.focusSelect = BigWorld.UnitSelect()	# ����Ȧ
		self.__spellModel = None
		self.spellSelect = BigWorld.UnitSelect()	# ����Ȧ
		self.targetSelect.setTexture( self.textureName_g )
		self.focusSelect.setTexture( self.textureName_g )
		self.spellSelect.setTexture( self.textureName_g )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onRoleLeaveWorld( self ) :
		"""
		��ɫ�뿪����ʱ������
		"""
		self.hideMoveGuider()
		self.__moveGuideModel = None

		self.hideTarget()
		self.hideFocus()
		self.hideSpellSite()

	# -------------------------------------------------
	# ʵ�ֽ�ɫ�ƶ���Ŀ��Ĺ�Ȧ
	# -------------------------------------------------
	def showMoveGuider( self, pos ) :
		"""
		��ʾ��ɫ�ƶ���Ŀ�ĵصĹ�Ȧ
		@type			pos : tuple/Vector3
		@param			pos : ��Ȧ��ʾλ�ã���ɫ�����ƶ�����Ŀ�ĵأ�
		"""
		player = BigWorld.player()
		model = self.__moveGuideModel
		if model is None :
			model = BigWorld.Model( "gzawu/unitselect/arrow_new.model" )
			player.addModel( model )
			self.__moveGuideModel = model
		model.position = pos
		model.visible = True
		rds.actionMgr.playAction( model, Const.MODEL_ACTION_MOVE )

	def hideMoveGuider( self ) :
		"""
		�����ƶ���Ŀ�ĵصĹ�Ȧ
		"""
		if self.__moveGuideModel :
			rds.actionMgr.stopAction( self.__moveGuideModel, Const.MODEL_ACTION_MOVE )
			self.__moveGuideModel.visible = False

	# -------------------------------------------------
	# ���ܹ�Ȧ
	# -------------------------------------------------
	def setSpellSite( self, pos ):
		"""
		��ʾʩ��Ŀ��λ�ù�Ȧ
		@type			pos	   : tuple/Vector3
		@param			pos	   : ʩ��λ��
		"""
		self.hideFocus()	# �м��ܹ�Ȧ����ʾ�����Ȧ
		player = BigWorld.player()
		model = self.__spellModel
		if model is None :
			model = BigWorld.Model("")
			player.addModel( model )
			self.__spellModel = model
			self.spellSelect.setModel( model )
		model.position = pos
		self.showSpellSite()

	def showSpellSite( self ):
		"""
		��ʾ���ܹ�Ȧ
		"""
		self.spellSelect.visible = True

	def hideSpellSite( self ):
		"""
		���ؼ��ܹ�Ȧ
		"""
		self.spellSelect.visible = False
		model = self.__spellModel
		if model is None: return
		player = BigWorld.player()
		if player and model in list( player.models ):
			player.delModel( model )
		self.__spellModel = None

	def setSpellSize( self, size ):
		"""
		���ü��ܹ�Ȧ��С
		param size: ���ܹ�Ȧ��С
		type size: float
		"""
		self.spellSelect.curUnitSize = size

	def setSpellTexture( self, textureName ):
		"""
		���ü��ܹ�Ȧ��ͼ
		param textureName: ���ܹ�Ȧ��ͼ·��
		type textureName: string
		return None
		"""
		self.spellSelect.setTexture( textureName )

	def setInRangeTexture( self ):
		"""
		����ʩ����Χ֮�ڣ���ɫ��ͼ��
		"""
		self.setSpellTexture( self.textureName_g )

	def setOutOfRangeTexture( self ):
		"""
		��������ʩ����Χ����ɫ��ͼ��
		"""
		self.setSpellTexture( self.textureName_r )

	# -------------------------------------------------
	# �ŵ׹�Ȧ
	# -------------------------------------------------

	def getTexture( self, entity ):
		"""
		���ظ�entityʹ�õ�texture
		param entity: Ŀ��
		type entity: entity
		return string
		"""
		if BigWorld.player().queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE:
			texture = self.textureName_r
		else:
			texture = self.textureName_g

		return texture

	def getTargetID( self ):
		"""
		����ѡ��Ȧ��ID
		return entityID
		"""
		return self.targetSelect.entityID

	def getTargetModel( self ):
		"""
		����ѡ���Ȧ��ģ��
		return pyModel
		"""
		return self.__targetModel

	def setTarget( self, target ):
		"""
		����ѡ���ȦĿ��
		param target: �ŵ׹�ȦĿ��
		type target: entity/pyModel/none
		return	None
		"""
		if isinstance( target, BigWorld.Model ):
			if self.getFocusModel() == target:
				self.detachFocus()
			self.__targetModel = target
			self.targetSelect.setModel( target )
		elif isinstance( target, BigWorld.Entity ):
			self.__targetModel = None
			if self.getFocusID() == target.id:
				self.detachFocus()

			self.setTargetTexture( self.getTexture( target ) )
			self.targetSelect.setEntity( target )
			self.targetSelect.curUnitSize = target.getUSelectSize()
		else:
			return

		self.showTarget()

	def showTarget( self ):
		"""
		��ʾѡ���Ȧ
		return None
		"""
		self.targetSelect.visible = True

	def hideTarget( self ):
		"""
		����ѡ���Ȧ
		return None
		"""
		self.targetSelect.visible = False

	def detachTarget( self ):
		"""
		ɾ��ѡ���Ȧ
		return None
		"""
		self.hideFocus()
		self.__targetModel = None
		self.targetSelect.setEntity( None )
		self.targetSelect.setModel( None )

	def refreshTarget( self, target ):
		"""
		ˢ��ѡ���Ȧ
		param target: �ŵ׹�ȦĿ��
		type target: entity
		return None
		"""
		if isinstance( target, BigWorld.Entity ) and self.getTargetID() == target.id:
			self.detachTarget()
			self.setTarget( target )

	def setTargetTexture( self, textureName ):
		"""
		����ѡ���Ȧ��ͼ
		param textureName: �ŵ׹�Ȧ��ͼ·��
		type textureName: string
		return None
		"""
		self.targetSelect.setTexture( textureName )

	# -------------------------------------------------
	# �����Ȧ
	# -------------------------------------------------
	def getFocusID( self ):
		"""
		���ؽ����ȦID
		return entityID
		"""
		return self.focusSelect.entityID

	def getFocusModel( self ):
		"""
		���ؽ����Ȧģ��
		return pyModel
		"""
		return self.__focusModel

	def setFocus( self, target ):
		"""
		��ʾ�����Ȧ
		param target: �����ȦĿ��
		type target: entity/pyModel/none
		return	None
		"""
		if isinstance( target, BigWorld.Model ):
			if self.getTargetModel() == target:
				return
			self.__focusModel = target
			self.focusSelect.setModel( target )
		elif isinstance( target, BigWorld.Entity ):
			if self.getTargetID() == target.id:
				return
			self.setFocusTexture( self.getTexture( target ) )
			self.focusSelect.setEntity( target )
			self.focusSelect.curUnitSize = target.getUSelectSize()
		else:
			return

		if self.__spellModel: return	# �м��ܹ�Ȧ����ʾ�����Ȧ
		self.showFocus()

	def showFocus( self ):
		"""
		��ʾ�����Ȧ
		"""
		self.focusSelect.visible = True

	def hideFocus( self ):
		"""
		���ؽ����Ȧ
		"""
		self.focusSelect.visible = False

	def detachFocus( self ):
		"""
		ɾ�������Ȧ
		"""
		self.hideFocus()
		self.__focusModel = None
		self.focusSelect.setEntity( None )
		self.focusSelect.setModel( None )

	def refreshFocus( self, target ):
		"""
		ˢ�½����Ȧ
		param target: �����ȦĿ��
		type target: entity
		return None
		"""
		if isinstance( target, BigWorld.Entity ) and self.getFocusID() == target.id:
			self.detachFocus()
			self.setFocus( target )

	def setFocusTexture( self, textureName ):
		"""
		���ý����Ȧ��ͼ
		param textureName: �ŵ׽�����ͼ·��
		type textureName: string
		return None
		"""
		self.focusSelect.setTexture( textureName )

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
unitSelect = UnitSelect()
