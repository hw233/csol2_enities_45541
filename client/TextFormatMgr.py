# -*- coding: gb18030 -*-
#
# $Id: TextFormatMgr.py,v 1.2 2008-06-27 08:57:00 zhangyuxing Exp $

import re
import BigWorld
import csstatus
import csdefine
from SmartImport import smartImport
"""
TF = { 	"c1": [(255,255,255, 255)],					#白色
				'c2': 	[(0,0,0, 255)],				#黑色
				'c3':	[(255,0,0, 255)],			#红色
				'c4':	[(0,255,0, 255)],			#绿色
				'c5':	[(0,0,255, 255)],			#深蓝色
				'c6':	[(255,255,0, 255)],			#黄色
				'c7':	[(0,255,255, 255)],			#浅蓝色
				'c8':	[(255,0,255, 255)],			#粉红色
				'c9':	[(128, 128, 128, 255)],		#灰色
				'c10':[(128, 255, 128, 255)],
				'c11':[(128, 0, 0, 255)],
				'c12':[(128,128,0, 255)],
				'c13':[(0,128,0, 255)],
				'c14':[(0,128,128, 255)],
				'c15':[(0,0,128, 255)],
				'c16':[(128,0,128, 255)],
				'c17':[(128,129,64, 255)],
				'c18':[(0,64,64, 255)],
				'c19':[(0,128,255, 255)],
				'c20':[(0,64,128, 255)],
				'c21':[(128,0,255, 255)],
				'c22':[(128,64,0, 255)],
				'c23':[(192,192,192, 255)],
				'c24':[(255,255,128, 255)],
				'c25':[(0,255,128, 255)],
				'c26':[(128,255,255, 255)],
				'c27':[(128,128,255, 255)],
				'c28':[(255,0,128, 255)],
				'c29':[(255,128,64, 255)],
				}
"""

_PL_Font = None

def _getFormator() :
	global _PL_Font
	if _PL_Font is None :
		_PL_Font = smartImport( "guis.tooluis.richtext_plugins.PL_Font:PL_Font" )
	return _PL_Font

class ItemText:
	"""
	物品描述
	"""
	def __init__( self, item, text ):
		"""
		"""

		self._text = text
		self._item = item
		#print self._text

	def makeDescription( self ):
		"""
		"""
		self.replaceDestStuCode()
		self.replaceCanNotGiveCode()
		self.replaceCanNotSellCode()
		self.replaceDesReqlevelCode()
		self.replaceCanUseCode()
		return self._text

	def replaceDestStuCode( self ):
		"""
		"""
		self._text = textFormatMgr.replaceNormal( self._text, textFormatMgr.desStuCode, 'c7' )
		return self._text

	def replaceCanNotGiveCode( self ):
		"""
		"""
		self._text = textFormatMgr.replaceNormal( self._text, textFormatMgr.canNotGiveCode, 'c24' )
		return self._text


	def replaceCanNotSellCode( self ):
		"""
		"""
		self._text = textFormatMgr.replaceNormal( self._text, textFormatMgr.canNotSellCode, 'c24' )
		return self._text


	def replaceDesReqlevelCode( self ):
		"""
		"""
		self._text = textFormatMgr.replaceNormal( self._text, textFormatMgr.reqLevelCode, 'c3' )
		return self._text


	def replaceCanUseCode( self ):
		"""
		"""
		self._text = textFormatMgr.replaceNormal( self._text, textFormatMgr.canUseCode, 'c4' )
		return self._text







class SkillText:
	"""
	技能描述
	"""
	def __init__( self, skill, text ):
		"""
		"""
		self._text = text
		self._skill = skill

	def makeDescription( self ):
		"""
		"""
		self.replaceSkillNameCode()
		self.replaceSkillRequireCode()
		self.replaceNumberCode()
		self.replaceBufferNameCode()
		return self._text

	def replaceSkillNameCode( self ):
		"""
		"""
		self._text = textFormatMgr.replaceNormal( self._text, textFormatMgr.skillCode, 'c6' )


	def replaceSkillRequireCode( self ):
		"""
		"""
		requireList = self._skill.getRequire().getRequires()		# 技能消耗
		for r in requireList:
			#if r.getType() != csdefine.SKILL_REQUIRE_TYPE_ITEM:
			#	continue
			if r.validObject( BigWorld.player() ) != csstatus.SKILL_GO_ON:
				#subRequireString = rds.textFormatMgr.makeDestStr( r.getDscription(), textFormatMgr.requireCode + r.getDscription() )
				sRequireListTuble = textFormatMgr.getSourceStr( self._text, textFormatMgr.requireCode + str(requireList.index(r)) )
				#requireString = requireString + _getFormator().getSource( r.getDscription(), fc = ( 255, 0, 0 ) )
				#print self._text
				#print sRequireListTuble
				if len(sRequireListTuble[0]) == 0:
					return
				require = sRequireListTuble[1][0]
				sRequire = _getFormator().getSource( require, fc = 'c3' )
				self._text = self._text.replace( sRequireListTuble[0][0], sRequire )
			else:
				sRequireListTuble = textFormatMgr.getSourceStr( self._text, textFormatMgr.requireCode + str(requireList.index(r)) )
				#print self._text
				#print sRequireListTuble
				if len(sRequireListTuble[0]) == 0:
					return
				require = sRequireListTuble[1][0]
				self._text = self._text.replace( sRequireListTuble[0][0], require )


	def replaceNumberCode( self ):
		numberListTuble = textFormatMgr.getSourceStr( self._text, textFormatMgr.numberCode )
		if len(numberListTuble[0]) == 0:
			return
		#number = numberListTuble[1][0]
		for iNumber in numberListTuble[1]:
			sINumber = _getFormator().getSource( iNumber, fc = 'c4' )
			self._text = self._text.replace( numberListTuble[0][numberListTuble[1].index(iNumber)], sINumber )

	def replaceBufferNameCode( self ):
		bufferNameListTuble = textFormatMgr.getSourceStr( self._text, textFormatMgr.bufferNameCode )
		if len(bufferNameListTuble[0]) == 0:
			return

		buff = self._skill.getBuffLink()

		for iBufferName in bufferNameListTuble[1]:
			if buff[bufferNameListTuble[1].index( iBufferName )].isBenign():
				sIBufferName = _getFormator().getSource( iBufferName, fc = 'c3' )
			elif buff[bufferNameListTuble[1].index( iBufferName )].isMalignant():
				sIBufferName = _getFormator().getSource( iBufferName, fc = 'c5' )
			else:
				sIBufferName = iBufferName
			self._text = self._text.replace( bufferNameListTuble[0][bufferNameListTuble[1].index(iBufferName)], sIBufferName )



class TalkText:
	"""
	和NPC对话描述
	"""
	def __init__( self, text ):
		"""
		"""
		self._text = text

	def makeDescription( self ):
		"""
		"""
		pass


class QuestText:
	"""
	任务描述
	"""
	def __init__( self, text ):
		"""
		"""
		self._text = text

	def makeDescription( self ):
		"""
		"""
		pass




class ChatText:
	"""
	聊天描述
	"""
	def __init__( self, text ):
		"""
		"""
		self._text = text

	def makeDescription( self ):
		"""
		"""
		pass

class DescriptionText:
	"""
	鼠标放到NPC，宠物，玩家，怪物等身上的描述
	"""
	def __init__( self, entity, text ):
		"""
		"""
		self._text = text
		self._entity = entity
		self._desColor = entity.getLeftNameColor()

	def makeDescription( self ):
		"""
		"""
		self.replaceNameCode()
		return self._text

	def replaceNameCode( self ):
		"""
		"""
		nameListTuble = textFormatMgr.getSourceStr( self._text, textFormatMgr.nameCode )
		if len(nameListTuble[0]) == 0:
			return
		name = nameListTuble[1][0]
		if self._desColor :
			sName = _getFormator().getSource( name, fc = self._desColor )
		else:
			sName = _getFormator().getSource( name, fc = ( 255, 255, 255 ) )

#		className = getattr( self._entity, "className", None )
#		if self._entity.getEntityType() == csdefine.ENTITY_TYPE_PET:
#			className = "11111111"
#		sName = ""
#		if className[4] == '1':
#			sName = _getFormator().getSource( name, fc = 'c1' )
#		elif className[4] == '2':
#			sName = _getFormator().getSource( name, fc = 'c13' )
#		elif className[4] == '3':
#			sName = _getFormator().getSource( name, fc = 'c4' )
#		elif className[4] == '4':
#			sName = _getFormator().getSource( name, fc = 'c25' )
#		else:
#			sName = _getFormator().getSource( name, fc = 'c6' )
		self._text = self._text.replace( nameListTuble[0][0], sName )



class TextFormatMgr:
	__inst = None

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = TextFormatMgr()
		return SELF.__inst


	def __init__( self ):
		"""
		常用编码初始化
		"""
		self.skillCode 		= "SKILL"
		self.nameCode  		= "NAME"
		self.requireCode 	= "REQUIRE"
		self.numberCode 	= "NUMBER"
		self.bufferNameCode = "BUFFERNAME"
		self.desStuCode 	= "DESSTU"
		self.canNotGiveCode = "CANNOTGIVE"
		self.canNotSellCode = "CANNOTSELL"
		self.reqLevelCode 	= "REQLEVEL"
		self.canUseCode		= "CANUSECODE"

	def makeDestStr( self, sourceString, ownCode ):
		"""
		合成数据
		"""
		return "&%s"%( ownCode ) + sourceString + "%s&"%( ownCode )

	def getSourceStr( self, destString, ownCode ):
		"""
		还原数据
		"""
		return ( re.findall( "&%s.+?%s&"%( ownCode, ownCode ), destString ) , re.findall( "(?<=&%s).+?(?=%s&)"%( ownCode, ownCode ), destString ) )


	def replaceNormal( self, text, code, color ):
		destListTuble = self.getSourceStr( text, code )
		if len(destListTuble[0]) == 0:
			return text
		dest = destListTuble[1][0]

		sDest = _getFormator().getSource( dest, fc = color )
		return text.replace( destListTuble[0][0], sDest )


textFormatMgr = TextFormatMgr.instance()