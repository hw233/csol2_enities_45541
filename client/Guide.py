# -*- coding: gb18030 -*-
import BigWorld
import csarithmetic
import csconst
import csdefine
import Const
from gbref import rds
import Math
 
class Guide:
	"""
	����ָ������
	"""
	def __init__( self ):
		self.fubenGuideModel = None

	def setGuideModelVisible( self, visible ):
		"""
		����ָ��ģ����Ӱ
		"""
		if self.fubenGuideModel:
			self.fubenGuideModel.visible = visible
		
	def setModelInNode( self ):
		"""
		���������ģ��
		"""
		def loadCompleted( model ):
			self.fubenGuideModel = model
			rds.effectMgr.attachObject( self.getModel(), Const.FUBEN_GUIDE_HARD_POINT, model )
			model.canRotate = True
			if self.state == csdefine.ENTITY_STATE_FIGHT :
				self.setGuideModelVisible(False)
			self.setFubenProgressYaw()
			if model.hasAction( Const.FUBEN_GUIDE_MODEL_ACTION ):
				rds.actionMgr.playAction( model, Const.FUBEN_GUIDE_MODEL_ACTION )
		rds.effectMgr.createModelBG( [ Const.FUBEN_GUIDE_MODEL_PATH ], loadCompleted )
	
	def disModelInNode( self ):
		"""
		ȡ��ָ��ģ��
		"""
		if not self.fubenGuideModel:return
		rds.effectMgr.detachObject( self.getModel(), Const.FUBEN_GUIDE_HARD_POINT, self.fubenGuideModel )
		self.fubenGuideModel = None

	def setFubenProgressYaw( self ):
		"""
		��ȡ��ǰ��������λ�ó���,������ģ�ͳ���
		"""
		if not self.canShowGuideModel():
			self.disModelInNode()
			return
		pos = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_PROGRESS )
		yaw = csarithmetic.getYawOfV3( Math.Vector3( eval( pos ) ) - self.position )
		self.fubenGuideModel.yaw = yaw
	
	def canShowGuideModel( self ):
		"""
		�Ƿ���ʾָ��ģ��
		"""
		try:
			if BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_PROGRESS ):
				return True
		except:
			pass
		return False
	
	def setFubenGuideYaw( self ):
		"""
		���ø���ָ��ģ�ͳ���
		"""
		if not self.canShowGuideModel():
			self.disModelInNode()
			return
		if self.fubenGuideModel:
			self.setFubenProgressYaw()
		else:
			self.setModelInNode()

	def guideModelDetect_( self ):
		"""
		Ѱ·ָ���͸���ָ�����tick����
		"""
		if self.modeList_:
			model = self.modeList_[0]
			pos = ( self.position - model.position )
			pos.y = 0.0
			if pos.length < 2.4:
				self.modeList_.remove( model )
				self.delModel( model )
			if pos.length > 5.0:
				for i in self.modeList_:
					self.delModel( i )
				self.modeList_ = []
		if self.canShowGuideModel():
			self.setFubenGuideYaw()
		else:self.disModelInNode()
