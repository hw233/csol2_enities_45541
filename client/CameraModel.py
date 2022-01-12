# -*- coding: gb18030 -*-
import BigWorld
import GUI
import Pixie
from interface.GameObject import GameObject
import csdefine
from gbref import rds	#add by wuxo 2011-11-2

# This implements the CameraModel on the Client.
class CameraModel( GameObject):
	
	def __init__( self ):
		GameObject.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC
		self.model = None
		self.signCallbackHandle = None

	def prerequisites( self ):
		prerequisit = []
		prerequisit.append( self.ownModelName)
		return prerequisit

	# This is called by BigWorld when the Entity enters AoI, through creation or movement.
	def enterWorld( self ):
		# could use different models for different stations
		#self.model = BigWorld.PyModelObstacle( CameraModel.modelNames[self.modelType], self.matrix, False )		
		
		# Use a secondary PyModel in order to use attachments that are not 
		# supported for PyModelObsticles
		model = BigWorld.Model( self.ownModelName )
		if model:
			self.model = model
			self.model.position = self.position
			self.model.yaw = self.yaw
			self.model.visible = False
			self.model.visibleAttachments = False


	# This is called by BigWorld when the Entity leaves AOI, through creation or movement.
	def leaveWorld( self ):
		self.model = None
		
	def cameraStartEven( self ,animTime,actionEvenName,magicGuiSound):
		#处理事件
		eventIDs = magicGuiSound.split(";")
		if magicGuiSound != "":
			try:	#支持对模型编号
				int(eventIDs[0])
			except:
				self.model = rds.npcModel.createDynamicModel( eventIDs[0] )
				eventIDs.remove(eventIDs[0])
		for id in eventIDs:
			if id != "":
				rds.cameraEventMgr.trigger(int(id),{"model":self.model,"entity":self})
			
		if self.model  != None:
			self.model.visible = True
			self.model.visibleAttachments = True
			if actionEvenName != None:
				action = self.model.action(actionEvenName)
				if animTime > 0.01:
					scale = action.duration/animTime
					self.model.actionScale = scale
				action()

	def cameraEndEven( self ):
		if self.model  != None:
			self.model.visible = False
			self.model.visibleAttachments = False
			self.model.actionScale = 1.0
			