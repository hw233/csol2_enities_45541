from guis.tooluis.fulltext.FullText import FullText
from guis.controls.ComboBox import ComboItem

class VehicleComboItem( ComboItem ):
	def __init__( self ) :
		ComboItem.__init__( self )
		
	def onMouseEnter_( self ) :
		"""
		after mouse entered, will be called
		"""
		ComboItem.onMouseEnter_( self )
		if self.pyText_.width > self.width - self.pyText_.left :
			FullText.show( self, self.pyText_ )
		return True
