# -*- coding: gb18030 -*-
#
# $Id: EntityAttachment.py,v 1.3 2008-06-21 07:55:25 huangyongwei Exp $

"""
implement attachment of the entity

2007/04/25 : written by huangyongwei
"""

import weakref
from bwdebug import *

output_del_info	= False

class EntityAttachment( object ) :
	"""
	abstract class
	"""
	def __init__( self ) :
		self.__type = None
		self.__object = None

	def __del__( self ) :
		if output_del_info :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getObject( self ) :
		try :
			return self.__object()
		except :
			INFO_MSG( "map object is not exist!" )
		return None

	def flush( self ) :
		pass

	# -------------------------------------------------
	def onAttached( self, obj ) :
		self.__object = weakref.ref( obj )

	def onDetached( self ) :
		pass

	# ---------------------------------------
	def onEnterWorld( self ) :
		pass

	def onLeaveWorld( self ) :
		pass

	# ---------------------------------------
	def onTargetFocus( self ) :
		pass

	def onTargetBlur( self ) :
		pass

	# ---------------------------------------
	def onBecomeTarget( self ) :
		pass

	def onLoseTarget( self ) :
		pass