# -*- coding: gb18030 -*-

from CountName import CountName

import ShareTexts as ST
import event.EventCenter as ECenter

from Color import cscolors
from LabelGather import labelGather


class TbTreeName( CountName ) :

	__cc_leaveTime = labelGather.getText( "FloatName:tbTree", "leaveTime" )
	__cc_ripe = labelGather.getText( "FloatName:tbTree", "ripe" )

	def __init__( self ) :
		CountName.__init__( self )
		self.visible = False
		self.pyLbName_.leftName = ""

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_FRUITTREE_BEGIN_COUNTDOWN"] = self.beginCountdown_
		self.triggers_["EVT_ON_FRUITTREE_RIPE"] = self.stopCountdown_
		CountName.registerTriggers_( self )

	def countdown_( self, leaveTime ) :
		if leaveTime - int( leaveTime ) > 0.5 :
			leaveTime = int( leaveTime ) + 1
		else :
			leaveTime = int( leaveTime )
		if leaveTime <= 0 :								# 果树已成熟
			self.pyLbCount_.text = self.__cc_ripe
			self.pyLbName_.leftName = ""
			self.pyLbCount_.color = cscolors["c4"]
		else :
			min = leaveTime / 60
			sec = leaveTime % 60
			text = ""
			if min :
				text += "%i%s" % ( min, ST.CHTIME_MINUTE )
			if sec :
				text += "%i%s" % ( sec, ST.CHTIME_SECOND )
			self.pyLbCount_.text = self.__cc_leaveTime % text
		self.layout_()

	def beginCountdown_( self, entity ) :
		"""
		"""
		if entity != self.entity_ : return
		CountName.beginCountdown_( self, entity, entity.lastTime )
		self.visible = True

	def stopCountdown_( self, entity ) :
		"""
		"""
		if entity != self.entity_ : return
		CountName.stopCountdown_( self, entity )
		self.visible = True

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setFName( self, name ) :
		pass

	fName = property( CountName._getFName, _setFName )