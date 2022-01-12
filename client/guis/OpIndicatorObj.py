# -*- coding: gb18030 -*-

from bwdebug import EXCEHOOK_MSG
from Toolbox import toolbox

class OpIndicatorObj :

	def __init__( self ) :
		self.__visibleIdts = []
		self._opIdtHandlers = {}
		self._initOpIndicationHandlers()

	def showOpIndication( self, idtId, *args ) :
		"""
		约定的管理器调用接口
		"""
		try :
			self._opIdtHandlers[idtId]( idtId, *args )
		except Exception :
			EXCEHOOK_MSG( "Indication(ID:%i) handle fails.(%s)" % ( idtId, str( self ) ) )

	def addVisibleOpIdt( self, idtId ) :
		"""
		"""
		if idtId not in self.__visibleIdts :
			self.__visibleIdts.append( idtId )

	def removeVisibleOpIdt( self, idtId ) :
		"""
		"""
		if idtId in self.__visibleIdts :
			self.__visibleIdts.remove( idtId )

	def relocateIndications( self ) :
		"""
		"""
		for idtId in self.__visibleIdts :
			toolbox.infoTip.moveHelpTips( idtId )

	def hideIndications( self ) :
		"""
		"""
		for idtId in self.__visibleIdts :
			toolbox.infoTip.hideHelpTips( idtId )

	def clearIndications( self ) :
		"""
		"""
		self.hideIndications()
		self.__visibleIdts = []
		
	def clearIndicationsById( self, idtId ):
		"""
		"""
		if idtId in self.__visibleIdts:
			toolbox.infoTip.hideHelpTips( idtId )
			self.__visibleIdts.remove( idtId )

	def clearOpIndicationHandlers( self ) :
		"""
		在窗口需要销毁时可调用此方法解除自身的引用
		"""
		self._opIdtHandlers.clear()

	def _initOpIndicationHandlers( self ) :
		"""
		"""
		pass