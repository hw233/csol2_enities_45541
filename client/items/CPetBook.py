# -*- coding: gb18030 -*-

from CItemBase import CItemBase
import ItemAttrClass
from skills.SkillTeachLoader import g_skillTeachDatas
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from ItemSystemExp import EquipQualityExp



class CPetBook( CItemBase ):
	"""
	宠物技能书
	"""

	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

