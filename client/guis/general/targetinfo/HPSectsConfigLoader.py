# -*- coding: gb18030 -*-

# $Id: SkillTrainerLoader.py,v 1.1 2008-01-31 07:30:27 yangkai Exp $

import Language
from bwdebug import *
import BigWorld

class HPSectionsLoader:
	"""
	怪物头像框血条段配置加载
	"""
	
	_hp_sections_config = "config/client/MonsterHPSections.xml"
	_instance = None
	
	def __init__( self ):
		assert HPSectionsLoader._instance is None
		self._datas = {}
		HPSectionsLoader._instance = self
		self.load( self._hp_sections_config )
	
	def load( self, config ):
		section = Language.openConfigSection( config )
		if section is None:return
		for node in section.values():
			className = node.readString( "className" )
			sects = node.readInt( "sections" )
			isBoss = node.readInt( "isBoss" )
			self._datas[className] = {"sections":sects, "isBoss":bool(isBoss)}
		Language.purgeConfig( self._hp_sections_config )
	
	def getSections( self, className ):
		data = self._datas.get( className, None )
		if data is not None:
			return data["sections"]
		return 0
	
	def isBoss( self, className ):
		data = self._datas.get( className, None )
		if data is not None:
			return data["isBoss"]
		return False
	
	def isInSections( self, className ):
		return className in self._datas
	
	@staticmethod
	def instance():
		"""
		"""
		if HPSectionsLoader._instance is None:
			HPSectionsLoader._instance = HPSectionsLoader()
		return HPSectionsLoader._instance

hpSectsLoader = HPSectionsLoader.instance()
	