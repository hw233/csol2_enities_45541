# -*- coding: gb18030 -*-

"""
格式化特殊字符串

$p	职业：法师、祭师、剑客、射手、战士、巫师
$n	玩家姓名
$c	国家：炎黄、凤鸣、九黎		( 当前废弃 )
$l	等级
$s	性别：男、女
$zx{className}	-> xxx,zzz	className对应的平面坐标
$area{x,y,z}	将坐标转换为区域名称
$emote{[:)]}	插入表情符号，大括号内是表情对应的字符，可到datas/maps/emote/emotionfaces.xml文件查询
$bysex{大爷,大妈}	如果玩家是男性则替换为 大爷 ，否则替换为 大妈
$byclass{坦克,盗贼,远程,魔法}	如果玩家的职业是战士，则替换为 坦克，依次对应的是剑客、射手、法师
"""
# $Id: StringFormat.py,v 1.10 2008-07-08 01:40:00 zhangyuxing Exp $

import re
import BigWorld
import csdefine
import csconst
import ShareTexts
from bwdebug import *
from gbref import rds
from Function import Functor
from NPCDatasMgr import npcDatasMgr
from ChatFacade import emotionParser
from guis.tooluis.richtext_plugins.share import defParser
from config.client.labels import StringFormat as lbs_StringFormat


def parseXZ( player, param ):
	"""
	解析参数param为坐标
	"""
	pos = npcDatasMgr.getNPCPosition( param )
	if pos == None or pos == (0,0,0):
		return "0,0"
	return "%i, %i" % ( int( pos.x ), int( pos.z ) )

def parseArea( player, param ):
	"""
	解析参数param(xyz)为区域名称
	"""
	args = param.split( "," )
	area = rds.mapMgr.getArea( args[0], ( float( args[1] ), float( args[2] ), float( args[3] ) ) )
	if area is not None:
		if len( args ) == 5:
			if int( args[4] ) != 0:
				return area.name + args[4] + lbs_StringFormat.line
		return area.name
	ERROR_MSG( "No area found.", param )
	return lbs_StringFormat.unknow


def parseTime( player, param ):
	"""
	解析参数param(xyz)为区域名称
	args : [分, 时, 日, 月, 星]
	"""
	args = param.split( " " )
	if len(args) != 5:
		return lbs_StringFormat.syntaxError
	def getValues( sformat ):
		if sformat == '*':
			return ( 'all', [] )
		elif '\\' in sformat:
			return ( 'part', [] )
		elif '-' in sformat:
			tempRange = sformat.split('-')
			tempList = []
			for i in xrange(int(tempRange[0]), int(tempRange[1]) + 1):
				tempList.append( str(i) )
			return ( 'continue', tempList )
		else:
			tempList = sformat.split(',')
			return ( 'part', tempList )
	dayString=""
	if args[4] == '*' and args[2] == '*':
		dayString = lbs_StringFormat.perDay

	elif args[4] == '*':
		value = getValues(args[2])
		if value[0] == 'continue':
			dayFrom = value[1][0]+ lbs_StringFormat.day
			dayTo = value[1][-1] + lbs_StringFormat.day
			dayString = dayFrom + lbs_StringFormat.dateAnd + dayTo
		else:
			dayString = len(value[1]) * ( "%s%s," % ( tuple( value[1] ), lbs_StringFormat.day ) )

	elif args[2] == '*':
		value = getValues(args[4])
		if value[0] == 'continue':
			dfrom = ShareTexts.CHTIME_WEEK + value[1][0]
			dto = ShareTexts.CHTIME_WEEK + value[1][-1]
			dayString = "%s%s%s " % ( dfrom, lbs_StringFormat.dateTo, dto )
		else:
			dayString = len(value[1]) * ( "%s%s," % ( tuple( value[1] ), ShareTexts.CHTIME_WEEK ) )

	dayString = dayString[:-1] + " "
	hourString = ""
	if args[1] == '*':
		hourString = "%s:" % lbs_StringFormat.perHour
	else:
		value = getValues(args[1])
		hourString = len(value[1]) * ( tuple( value[1] ) + lbs_StringFormat.hour )

	hourString = hourString[:-1] + ":"
	minString = ""
	if args[0] == '*':
		hourString = "%s." % lbs_StringFormat.perMinue
	else:
		value = getValues(args[0])
		minString = len(value[1]) * ( tuple( value[1] ) + lbs_StringFormat.minute )
	minString = minString[:-1] + "."
	return dayString+hourString+minString

def parseEmotion( player, param ) :
	"""
	根据配置文本解释出界面显示所需的表情文本
	"""
	emAttrs = defParser.getAttrInfos( param )
	emSign = emAttrs.get( "e", "" )
	emSize = emAttrs.get( "s", "None" )
	return emotionParser.formatEmotion( emSign, size = eval( emSize ) )

def parseBySex( player, param ) :
	"""
	根据玩家性别解释出对应的显示文本
	"""
	return param.split( "," )[ ORDER_SEX.index( player.getGender() ) ]

def parseByClass( player, param ) :
	"""
	根据玩家职业解释出对应的显示文本
	"""
	return param.split( "," )[ ORDER_CLASS.index( player.getClass() ) ]


# -------------------------------------------------------------------------
# format definition
# -------------------------------------------------------------------------
ORDER_SEX = [ csdefine.GENDER_MALE, csdefine.GENDER_FEMALE ]
ORDER_CLASS = [csdefine.CLASS_FIGHTER, csdefine.CLASS_SWORDMAN,
				csdefine.CLASS_ARCHER, csdefine.CLASS_MAGE,]


# -------------------------------------------------------------------------
# functions map
# -------------------------------------------------------------------------
IDENTIFY_SET = {
					"$$"		: lambda player, param: "$",
					"$s"		: lambda player, param: csconst.g_chs_gender[ player.getGender() ],
					"$p"		: lambda player, param: csconst.g_chs_class[ player.getClass() ],
					"$n"		: lambda player, param: player.getName(),
					"$l"		: lambda player, param: str( player.level ),
					"$xz"		: parseXZ,
					"$area"		: parseArea,
					"$time"		: parseTime,
					"$emote"	: parseEmotion,
					"$bysex"	: parseBySex,
					"$byclass"	: parseByClass,
				}

def _getMatchStr():
	"""
	"""
	words = [ "\$\$", "\$s", "\$p", "\$n", "\$l", "\$xz\{\w+\}",
				"\$area\{[\w,-_]+\}","\$time\{[\w -_]+\}", "\$emote\{.+?\}", "\$bysex\{.+?\}",
				"\$byclass\{.+?\}",]
	return "|".join( words )

#_recompile = re.compile( "\\$\\$|\\$\\w+(?:\\{\\w*\\})*" )
_recompile = re.compile( _getMatchStr() )

def _dashrepl( player, matchobj ):
	"""
	@param matchobj: instance of re.match
	"""
	s = matchobj.group(0)
	pos = s.find( "{" )
	if pos != -1:
		value = s[pos + 1:s.find( "}", pos + 1 )]
		key = s[:pos]
	else:
		key = s
		value = ""
	return IDENTIFY_SET[key]( player, value )


def format( string, player = None ):
	"""
	@return: 被格式化后的字符串
	@rtype:  String
	"""
	if player is None:
		player = BigWorld.player()

	return _recompile.sub( Functor( _dashrepl, player ), string )
