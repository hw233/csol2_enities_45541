# -*- coding: gb18030 -*-

# common
from SpaceCopyFormulas import SpaceCopyFormulas, CopyCheckerBase, CopyCheckerLevel
# bigworld
import BigWorld


# ----------------------------------------------------------------
# CopyCheckerCompletion: check the copy completion of player.
# ----------------------------------------------------------------
class CopyCheckerCompletion( CopyCheckerBase ) :

	@staticmethod
	def check( player, summary ) :
		""""""
		return True


# ----------------------------------------------------------------
# CopyCheckerPeriod: check if the copy is opened now.
# ----------------------------------------------------------------
class DefaultPeriodChecker :

	@staticmethod
	def check( player, summary ) :
		return True

class CrondPeriodChecker :
	"""Verify if copy is opened now."""
	_LABEL_TO_CROND = {
		"shuijing" : "AS_shuijingStart",
	}

	@staticmethod
	def check( player, summary ) :
		crondKey = CrondPeriodChecker._LABEL_TO_CROND.get( summary["copyLabel"] )
		return BigWorld.globalData.get( crondKey, False )

class CopyCheckerPeriod( CopyCheckerBase ) :
	"""Verify if copy is opened now."""
	_PERIOD_CHECKERS = {
		"shuijing"	: CrondPeriodChecker,
	}

	@staticmethod
	def check( player, summary ) :
		checker = CopyCheckerPeriod._PERIOD_CHECKERS.get( summary["copyLabel"], DefaultPeriodChecker )
		return checker.check( player, summary )


# ----------------------------------------------------------------
# Create the instance of SpaceCopyFormulas in base bellow.
# ----------------------------------------------------------------
class BaseSpaceCopyFormulas( SpaceCopyFormulas ) :
	"""副本进入规则处理类，设计为单列类"""
	__instance = None									# 设计为单列类

	def __init__( self ) :
		assert BaseSpaceCopyFormulas.__instance is None, "You should invoke the instance method."
		SpaceCopyFormulas.__init__( self )
		self.setCheckers( [CopyCheckerLevel, CopyCheckerCompletion, CopyCheckerPeriod] )

	@staticmethod
	def instance() :
		if BaseSpaceCopyFormulas.__instance is None :
			BaseSpaceCopyFormulas.__instance = BaseSpaceCopyFormulas()
		return BaseSpaceCopyFormulas.__instance


spaceCopyFormulas = BaseSpaceCopyFormulas.instance()
