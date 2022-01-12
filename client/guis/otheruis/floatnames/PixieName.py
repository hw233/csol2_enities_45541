# -*- coding: gb18030 -*-

from CountName import CountName

import csconst
import ShareTexts as ST
import event.EventCenter as ECenter

from Time import Time
from LabelGather import labelGather
from DoubleName import DoubleName

class PixieName( CountName ) :

	__cc_useless = labelGather.getText( "FloatName:pixie", "useless" )
	__cc_leaveTime = labelGather.getText( "FloatName:pixie", "leaveTime" )
	__cc_ownerFmt = labelGather.getText( "FloatName:pixie", "ownerFmt" )

	def __init__( self ) :
		CountName.__init__( self )
		self.pyLbName_.leftColor = ( 0, 255, 0, 255 )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def countdown_( self, leaveTime ) :
		if leaveTime - int( leaveTime ) > 0.5 :
			leaveTime = int( leaveTime ) + 1
		else :
			leaveTime = int( leaveTime )
		if leaveTime <= 0 :								# 使用时间已过
			self.pyLbCount_.text = self.__cc_useless
			self.pyLbCount_.color = ( 255,128,0,255 )
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
		
	def onAttachEntity_( self ):
		self.pyLbName_.toggleLeftName( True )
		if self.entity_.bornTime > 0 :
			self.pyLbName_.leftName = self.__cc_ownerFmt % self.entity_.ownerName
			self.pyLbCount_.color = ( 255,255,255,255 )
			leaveTime = csconst.VIP_EIDOLON_LIVE_TIME - Time.time() + self.entity_.bornTime
			self.beginCountdown_( self.entity_, leaveTime )
		else :
			self.pyLbName_.leftName = self.entity_.getName()
			self.pyLbCount_.visible = False
		self.layout_()	


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setFName( self, name ) :
		pass

	fName = property( CountName._getFName, _setFName )
