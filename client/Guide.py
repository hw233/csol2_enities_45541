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
	副本指引功能
	"""
	def __init__( self ):
		self.fubenGuideModel = None

	def setGuideModelVisible( self, visible ):
		"""
		设置指引模型显影
		"""
		if self.fubenGuideModel:
			self.fubenGuideModel.visible = visible
		
	def setModelInNode( self ):
		"""
		骨骼点绑上模型
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
		取消指引模型
		"""
		if not self.fubenGuideModel:return
		rds.effectMgr.detachObject( self.getModel(), Const.FUBEN_GUIDE_HARD_POINT, self.fubenGuideModel )
		self.fubenGuideModel = None

	def setFubenProgressYaw( self ):
		"""
		获取当前副本进度位置朝向,并设置模型朝向
		"""
		if not self.canShowGuideModel():
			self.disModelInNode()
			return
		pos = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_PROGRESS )
		yaw = csarithmetic.getYawOfV3( Math.Vector3( eval( pos ) ) - self.position )
		self.fubenGuideModel.yaw = yaw
	
	def canShowGuideModel( self ):
		"""
		是否显示指引模型
		"""
		try:
			if BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_PROGRESS ):
				return True
		except:
			pass
		return False
	
	def setFubenGuideYaw( self ):
		"""
		设置副本指引模型朝向
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
		寻路指引和副本指引侦测tick函数
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
