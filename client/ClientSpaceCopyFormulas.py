# -*- coding: gb18030 -*-

# common
from SpaceCopyFormulas import SpaceCopyFormulas, CopyCheckerLevel
import Language

# ----------------------------------------------------------------
# Create the instance of SpaceCopyFormulas in client bellow.
# ----------------------------------------------------------------
class ClientSpaceCopyFormulas( SpaceCopyFormulas ) :
	"""��������������࣬���Ϊ������"""
	__instance = None									# ���Ϊ������

	def __init__( self ) :
		assert ClientSpaceCopyFormulas.__instance is None, "You should invoke the instance method."
		SpaceCopyFormulas.__init__( self )
		self.setCheckers( [CopyCheckerLevel] )
		self.loadCopiesData( "config/matchablecopies.xml" )

	@staticmethod
	def instance() :
		if ClientSpaceCopyFormulas.__instance is None :
			ClientSpaceCopyFormulas.__instance = ClientSpaceCopyFormulas()
		return ClientSpaceCopyFormulas.__instance
