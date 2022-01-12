# -*- coding: gb18030 -*-

import GUI
import ResMgr
from Color import cscolors
from guis.UIFixer import uiFixer
from guis.controls.StaticText import StaticText

from FloatName import FloatName
from Counter import Counter
from DoubleName import DoubleName

LAST_TIME_VALUE = 0

class CountName( FloatName ) :

	__cc_dummySection = ResMgr.openSection( "guis/otheruis/floatnames/countname.gui" )

	def __init__( self, gui = None ) :
		if gui is None :
			gui = GUI.load( "guis/otheruis/floatnames/countname.gui" )
			uiFixer.firstLoadFix( gui )
		FloatName.__init__( self, gui )
		
		self.pyLbCount_ = StaticText( gui.st_count )
		self.pyLbCount_.setFloatNameFont()
		self.pyLbName_ = DoubleName( gui.elemName )	
		self.pyLbName_.toggleLeftName( True )
		self.counter_ = Counter()
		self.counter_.setInterval( 1.0 )
		self.counter_.setCallback( self.countdown_ )

		self.pyElements_ = [ self.pyLbName_, self.pyLbCount_ ]

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def countdown_( self, leaveTime ) :
		self.pyLbCount_.text = "%i seconds leave." % leaveTime
		self.layout_()

	def beginCountdown_( self, entity, lastTime ) :
		"""
		"""
		if entity != self.entity_ : return
		self.counter_.setTime( lastTime )
		self.counter_.countdown()

	def stopCountdown_( self, entity ) :
		if entity != self.entity_ : return
		self.counter_.setTime( LAST_TIME_VALUE )
		self.counter_.countdown()
		
	def onDetachEntity_( self ):
		self.pyLbCount_.text = ""

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def dispose( self ) :
		self.counter_.stop()
		self.counter_.setCallback( None )
		FloatName.dispose( self )
