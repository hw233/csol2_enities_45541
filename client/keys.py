"""This module provides utility functions for button-pressed input type.
$Id: keys.py,v 1.16 2008-06-23 07:45:52 yangkai Exp $"""


import BigWorld
import Math
import math

# ------------------------------------------------------------------------------
# The Key Definitions: This is the definition of all keys known to the client.
# They are set to the values as in the C++ files.
# ------------------------------------------------------------------------------

# Modifiers:
MODIFIER_SHIFT		= 0x1
MODIFIER_CTRL		= 0x2
MODIFIER_ALT		= 0x4
MODIFIER_ALL		= -1

# Null Keyboard Buttons:
KEY_NOT_FOUND		= 0x00	# Return values on error
KEY_NONE			= 0x00	#
KEY_NULL			= 0x00	#

# Keyboard Buttons:
KEY_ESCAPE          = 0x01	# Main Keyboard 'ESC' key
KEY_1               = 0x02	# Main Keyboard '1' '!' key
KEY_2               = 0x03	# Main Keyboard '2' '@' key
KEY_3               = 0x04	# Main Keyboard '3' '#' key
KEY_4               = 0x05	# Main Keyboard '4' '$' key
KEY_5               = 0x06	# Main Keyboard '5' '%' key
KEY_6               = 0x07	# Main Keyboard '6' '^' key
KEY_7               = 0x08	# Main Keyboard '7' '&' key
KEY_8               = 0x09	# Main Keyboard '8' '*' key
KEY_9               = 0x0A	# Main Keyboard '9' '(' key
KEY_0               = 0x0B	# Main Keyboard '0' ')' key
KEY_MINUS           = 0x0C	# Main Keyboard '-' '_' key
KEY_EQUALS          = 0x0D	# Main Keyboard '=' '+' key
KEY_BACKSPACE       = 0x0E	# Main Keyboard 'BACKSPACE' Key
KEY_TAB             = 0x0F	# Main Keyboard 'TAB' key
KEY_Q               = 0x10	# Main Keyboard 'Q' 'q' key
KEY_W               = 0x11	# Main Keyboard 'W' 'w' key
KEY_E               = 0x12	# Main Keyboard 'E' 'e' key
KEY_R               = 0x13	# Main Keyboard 'R' 'r' key
KEY_T               = 0x14	# Main Keyboard 'T' 't' key
KEY_Y               = 0x15	# Main Keyboard 'Y' 'y' key
KEY_U               = 0x16	# Main Keyboard 'U' 'u' key
KEY_I               = 0x17	# Main Keyboard 'I' 'i' key
KEY_O               = 0x18	# Main Keyboard 'O' 'o' key
KEY_P               = 0x19	# Main Keyboard 'P' 'p' key
KEY_LBRACKET        = 0x1A	# Main Keyboard '[' '{' key
KEY_RBRACKET        = 0x1B	# Main Keyboard ']' '}' key
KEY_RETURN          = 0x1C	# Main Keyboard 'ENTER' key
KEY_LCONTROL        = 0x1D	# Main Keyboard left 'CTRL' key
KEY_A               = 0x1E	# Main Keyboard 'A' 'a' key
KEY_S               = 0x1F	# Main Keyboard 'S' 's' key
KEY_D               = 0x20	# Main Keyboard 'D' 'd' key
KEY_F               = 0x21	# Main Keyboard 'F' 'f' key
KEY_G               = 0x22	# Main Keyboard 'G' 'g' key
KEY_H               = 0x23	# Main Keyboard 'H' 'h' key
KEY_J               = 0x24	# Main Keyboard 'J' 'j' key
KEY_K               = 0x25	# Main Keyboard 'K' 'k' key
KEY_L               = 0x26	# Main Keyboard 'L' 'l' key
KEY_SEMICOLON       = 0x27	# Main Keyboard ';' ':' key
KEY_APOSTROPHE      = 0x28	# Main Keyboard ''' '"' key
KEY_GRAVE           = 0x29	# Main Keyboard '`' '~' key
KEY_LSHIFT          = 0x2A	# Main Keyboard left 'SHIFT' key
KEY_BACKSLASH       = 0x2B	# Main Keyboard '\' '|' key
KEY_Z               = 0x2C	# Main Keyboard 'Z' 'z' key
KEY_X               = 0x2D	# Main Keyboard 'X' 'x' key
KEY_C               = 0x2E	# Main Keyboard 'C' 'c' key
KEY_V               = 0x2F	# Main Keyboard 'V' 'v' key
KEY_B               = 0x30	# Main Keyboard 'B' 'b' key
KEY_N               = 0x31	# Main Keyboard 'N' 'n' key
KEY_M               = 0x32	# Main Keyboard 'M' 'm' key
KEY_COMMA           = 0x33	# Main Keyboard ',' '<' key
KEY_PERIOD          = 0x34	# Main Keyboard '.' '>' key
KEY_SLASH           = 0x35	# Main Keyboard '/' '?' key
KEY_RSHIFT          = 0x36	# Main Keyboard right 'SHIFT' key
KEY_NUMPADSTAR      = 0x37	# Numeric Keypad '*' key
KEY_LALT            = 0x38	# Main Keyboard left 'ALT' key
KEY_SPACE           = 0x39	# Main Keyboard 'SPACE' bar
KEY_CAPSLOCK        = 0x3A	# Main Keyboard 'CAPS LOCK' key
KEY_F1              = 0x3B	# Main Keyboard 'F1' key
KEY_F2              = 0x3C	# Main Keyboard 'F2' key
KEY_F3              = 0x3D	# Main Keyboard 'F3' key
KEY_F4              = 0x3E	# Main Keyboard 'F4' key
KEY_F5              = 0x3F	# Main Keyboard 'F5' key
KEY_F6              = 0x40	# Main Keyboard 'F6' key
KEY_F7              = 0x41	# Main Keyboard 'F7' key
KEY_F8              = 0x42	# Main Keyboard 'F8' key
KEY_F9              = 0x43	# Main Keyboard 'F9' key
KEY_F10             = 0x44	# Main Keyboard 'F10' key
KEY_NUMLOCK         = 0x45	# Numeric Keypad 'NUM LOCK' key
KEY_SCROLL          = 0x46	# Main Keyboard 'SCROLL LOCK' key
KEY_NUMPAD7         = 0x47	# Numeric Keypad '7' key
KEY_NUMPAD8         = 0x48	# Numeric Keypad '8' key
KEY_NUMPAD9         = 0x49	# Numeric Keypad '9' key
KEY_NUMPADMINUS     = 0x4A	# Numeric Keypad '-' key
KEY_NUMPAD4         = 0x4B	# Numeric Keypad '4' key
KEY_NUMPAD5         = 0x4C	# Numeric Keypad '5' key
KEY_NUMPAD6         = 0x4D	# Numeric Keypad '6' key
KEY_ADD             = 0x4E	# Numeric Keypad '+' key
KEY_NUMPAD1         = 0x4F	# Numeric Keypad '1' key
KEY_NUMPAD2         = 0x50	# Numeric Keypad '2' key
KEY_NUMPAD3         = 0x51	# Numeric Keypad '3' key
KEY_NUMPAD0         = 0x52	# Numeric Keypad '0' key
KEY_NUMPADPERIOD    = 0x53	# Numeric Keypad '.' key
KEY_OEM_102         = 0x56	# UK/Germany Keyboard '<' '>' '|' key
KEY_F11             = 0x57	# Main Keyboard 'F11' key
KEY_F12             = 0x58	# Main Keyboard 'F12' key

KEY_F13             = 0x64	# Specific to the NEC PC98
KEY_F14             = 0x65	# Specific to the NEC PC98
KEY_F15             = 0x66	# Specific to the NEC PC98

KEY_KANA            = 0x70	# Specific to the Japanese Keyboard
KEY_ABNT_C1         = 0x73	# Portugese (Brazilian) Keyboard '/' '?' key
KEY_CONVERT         = 0x79	# Specific to the Japanese Keyboard
KEY_NOCONVERT       = 0x7B	# Specific to the Japanese Keyboard
KEY_YEN             = 0x7D	# Specific to the Japanese Keyboard
KEY_ABNT_C2         = 0x7E	# Portugese (Brazilian) Numpad '.'
KEY_NUMPADEQUALS    = 0x8D	# Specific to the NEC PC98, Numeric Keypad '=' key
KEY_PREVTRACK       = 0x90	# DIK_CIRCUMFLEX on Japanese keyboard
KEY_AT              = 0x91	# Specific to the NEC PC98
KEY_COLON           = 0x92	# Specific to the NEC PC98
KEY_UNDERLINE       = 0x93	# Specific to the NEC PC98
KEY_KANJI           = 0x94	# Specific to the Japanese Keyboard
KEY_STOP            = 0x95	# Specific to the NEC PC98
KEY_AX              = 0x96	# Specific to the Japan AX Keyboard
KEY_UNLABELED       = 0x97	# Specific to the J3100
KEY_NEXTTRACK       = 0x99	# Next Track
KEY_NUMPADENTER     = 0x9C	# Numeric Keypad 'ENTER' key
KEY_RCONTROL        = 0x9D	# Main Keyboard right 'CTRL' key
KEY_MUTE            = 0xA0	#
KEY_CALCULATOR      = 0xA1	#
KEY_PLAYPAUSE       = 0xA2	#
KEY_MEDIASTOP       = 0xA4	#
KEY_VOLUMEDOWN      = 0xAE	#
KEY_VOLUMEUP        = 0xB0	#
KEY_WEBHOME         = 0xB2	#
KEY_NUMPADCOMMA     = 0xB3	# Specific to the NEC PC98, Numeric Keypad ',' key
KEY_NUMPADSLASH     = 0xB5	# Numeric Keypad '/' key
KEY_SYSRQ           = 0xB7	#
KEY_RALT            = 0xB8	# Main Keyboard right 'ALT' key
KEY_PAUSE           = 0xC5	# Main Keyboard 'PAUSE' 'BREAK' key
KEY_HOME            = 0xC7	# Arrow Keypad 'HOME' key
KEY_UPARROW         = 0xC8	# Arrow Keypad Up-Arrow key
KEY_PGUP            = 0xC9	# Arrow Keypad 'PAGE UP' key
KEY_LEFTARROW       = 0xCB	# Arrow Keypad Left-Arrow key
KEY_RIGHTARROW      = 0xCD	# Arrow Keypad Right-Arrow key
KEY_END             = 0xCF	# Arrow Keypad 'END' key
KEY_DOWNARROW       = 0xD0	# Arrow Keypad Down-Arrow key
KEY_PGDN            = 0xD1	# Arrow Keypad 'PAGE DOWN' key
KEY_INSERT          = 0xD2	# Arrow Keypad 'INSERT' key
KEY_DELETE          = 0xD3	# Arrow Keypad 'DELETE' key
KEY_LWIN            = 0xDB	# Windows Keyboard Left Windows key
KEY_RWIN            = 0xDC	# Windows Keyboard Right Windows key
KEY_APPS            = 0xDD	# Windows Keyboard AppMenu key
KEY_POWER           = 0xDE	#
KEY_SLEEP           = 0xDF	#
KEY_WAKE            = 0xE3	#
KEY_WEBSEARCH       = 0xE5	#
KEY_WEBFAVORITES    = 0xE6	#
KEY_WEBREFRESH      = 0xE7	#
KEY_WEBSTOP         = 0xE8	#
KEY_WEBFORWARD      = 0xE9	#
KEY_WEBBACK         = 0xEA	#
KEY_MYCOMPUTER      = 0xEB	#
KEY_MAIL            = 0xEC	#
KEY_MEDIASELECT     = 0xED	#

# Mouse Buttons.
KEY_MOUSE0          = 0x100	# Left Mouse Button
KEY_LEFTMOUSE       = 0x100	# Left Mouse Button

KEY_MOUSE1          = 0x101	# Right Mouse Button
KEY_RIGHTMOUSE      = 0x101	# Right Mouse Button

KEY_MOUSE2          = 0x102	# Middle Mouse Button
KEY_MIDDLEMOUSE     = 0x102	# Middle Mouse Button

KEY_MOUSE3          = 0x103	# Additional Mouse Buttons
KEY_MOUSE4          = 0x104	#
KEY_MOUSE5          = 0x105	#
KEY_MOUSE6          = 0x106	#
KEY_MOUSE7          = 0x107	#

# Joystick Buttons.
KEY_JOY0			= 0x110	# Joystick buttons number 0 to 31
KEY_JOY1			= 0x111	#
KEY_JOY2			= 0x112	#
KEY_JOY3			= 0x113	#
KEY_JOY4			= 0x114	#
KEY_JOY5			= 0x115	#
KEY_JOY6			= 0x116	#
KEY_JOY7			= 0x117	#
KEY_JOY8			= 0x118	#
KEY_JOY9			= 0x119	#
KEY_JOY10			= 0x11A	#
KEY_JOY11			= 0x11B	#
KEY_JOY12			= 0x11C	#
KEY_JOY13			= 0x11D	#
KEY_JOY14			= 0x11E	#
KEY_JOY15			= 0x11F	#
KEY_JOY16			= 0x120	#
KEY_JOY17			= 0x121	#
KEY_JOY18			= 0x122	#
KEY_JOY19			= 0x123	#
KEY_JOY20			= 0x124	#
KEY_JOY21			= 0x125	#
KEY_JOY22			= 0x126	#
KEY_JOY23			= 0x127	#
KEY_JOY24			= 0x128	#
KEY_JOY25			= 0x129	#
KEY_JOY26			= 0x12A	#
KEY_JOY27			= 0x12B	#
KEY_JOY28			= 0x12C	#
KEY_JOY29			= 0x12D	#
KEY_JOY30			= 0x12E	#
KEY_JOY31			= 0x12F	#

AXIS_LX				= 0
AXIS_LY				= 1
AXIS_RX				= 2
AXIS_RY				= 3

VK_LBUTTON			= 0x01
VK_RBUTTON			= 0x02


# ------------------------------------------------------------------------------
KEY_MOUSE_KEYS = set( [KEY_MOUSE0, KEY_MOUSE1, KEY_MOUSE2, KEY_MOUSE3, \
	KEY_MOUSE4, KEY_MOUSE5, KEY_MOUSE6, KEY_MOUSE7,
	] )																			# mouse buttons( hyw -- 2008.06.19 )

KEY_MODIFIER_KEYS = set( [KEY_LCONTROL, KEY_RCONTROL, KEY_LSHIFT, KEY_RSHIFT, \
	KEY_LALT, KEY_RALT,
	] )																			# modifier keys( hyw -- 2009.04.24 )

KEY_9FANGINPUT_HOOK_KEYS = set( [KEY_LEFTARROW, KEY_RIGHTARROW, KEY_DOWNARROW, KEY_UPARROW,
	KEY_NUMLOCK, KEY_NUMPADPERIOD, KEY_NUMPADCOMMA, KEY_NUMPADSLASH,
	KEY_NUMPADSTAR, KEY_NUMPADMINUS, KEY_ADD, KEY_NUMPADEQUALS,
	KEY_NUMPAD0, KEY_NUMPAD1, KEY_NUMPAD2, KEY_NUMPAD3, KEY_NUMPAD4,
	KEY_NUMPAD5, KEY_NUMPAD6, KEY_NUMPAD7, KEY_NUMPAD8, KEY_NUMPAD9,
	] )

CUSTOM_KYES_STRING = {
	KEY_ESCAPE : "ESC",
	}																			# custom key string

# ------------------------------------------------------------------------------
def keyToString( keyValue ) :
	"""
	translate key to string key
	@type				keyValue : MACRO DEFINATION
	@param				keyValue : key value defined above
	@rtype						 : str
	@return						 : key name
	"""
	keyStr = CUSTOM_KYES_STRING.get( keyValue )
	if keyStr : return keyStr
	return BigWorld.keyToString( keyValue )

def modsToString( modsValue ) :
	"""
	translate modiffiers key to string modiffiers
	@type				modsValue : MACRO DEFINATION
	@param				modsValue : modiffier value define above
	@rtype						  : list of modiffier key name
	@return						  : modiffier key name
	"""
	strMods = {}
	strMods[0x1] = "SHIFT"
	strMods[0x2] = "CTRL"
	strMods[0x4] = "ALT"
	sortedStrMods = []
	for key, strMod in strMods.iteritems() :
		if key & modsValue == key :
			sortedStrMods.append( strMod )
	sortedStrMods.sort( key = lambda e : e[1], reverse = True )
	return sortedStrMods

def shortcutToString( key, mods = 0 ) :
	"""
	translate shortcut to shortcut string as format: MOD + MOD + KEY
	@type				key  : MACRO DEFINATION
	@param				key  : key value defined above
	@type				mods : MACRO DEFINATION
	@param				mods : modiffier value define above
	@rtype					 : str
	@return					 : shortcut string
	"""
	strKey = keyToString( key )
	sortedStrMods = modsToString( mods )
	strMods = "+".join( sortedStrMods )
	if strMods == "" or strKey == strMods :
		return strKey
	return "%s+%s" % ( strMods, strKey )

# ------------------------------------------------------------------------------
# Method: buildBindList
# Description: Builds a list of down-key (keys that must all be held down in
# order for a predicate to be true,) and a list of not-down keys (key
# combinations that cannot also be down for the predicate to be true.)
#
# It accepts a list of pairs, consisting of a list and some other data type
# (not important except for a not-equal comparison,) and returns a list of
# triples, consisting of the down-key list, the not-down keys list, and the
# data type.
# ------------------------------------------------------------------------------
def buildBindList( downList ):
	# Clear our return list.
	bindList = []

	# For each pair in the list of down-keys, create the list of not-down keys.
	for ( downKeys, predicate ) in downList:
		notDownLists = []

		# Now go through all the other down-keys to find ambiguity.
		# A down-key combination is ambiguous if it is contained entirely
		# within another down-key combination, unless they both happen to refer
		# to the same predicate.
		for ( otherDownKeys, otherPredicate ) in downList:
			if predicate != otherPredicate: continue
			containedEntirely = set( downKeys ).issubset( otherDownKeys )	# if otherPredicate contain downKeys, containedEntirely will be true

			# Now if there is ambiguity, build a not-down list to
			# disambiguate the two key combinations.
			if containedEntirely:
				# The not-down list is formed from the list of all keys
				# pressed down in the second list which are not already in
				# the first list. This is equivalent to listing which keys
				# are not covered by the first list and making sure the
				# second list is not thusly satisfied.
				notDownList = [ otherKey for otherKey in otherDownKeys if otherKey not in downKeys]
				notDownLists.append( notDownList )

		# Add the triple to the return list.
		# downKeys: bind keys
		# notDownLists: [[...], [...], [...], ...] keys not in myself, but in other downkeys, and i was contained other keys
		# predicate: action
		bindList.append( ( downKeys, notDownLists, predicate ) )

	return bindList
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Method: printBindList
# Description: Accepts a bind list (a triple consisting of a down-key list,
# a not-down keys list, and a predicate,) and prints it.
#
# This method uses the BigWorld module in order to keep itself compatible
# with the C++ values for the keys.
# ------------------------------------------------------------------------------

def printBindList( bindList ):
	for ( downKeys, notDownKeysList, predicate) in bindList:

		# Print the down-key list first.
		print "[ ",
		for downKey in downKeys:
			print BigWorld.keyToString( downKey ), " ",
		print "] { ",

		# Print each not-down key list next.
		for notDownKeys in notDownKeysList:
			print "[ ",
			for notDownKey in notDownKeys:
				print BigWorld.keyToString( notDownKey ), " ",
			print "] ",
		print "}"
# ------------------------------------------------------------------------------





CURSOR_CAMERA	= 0
FLEXI_CAM		= 1
FIXED_CAMERA	= 2
FREE_CAMERA		= 4

# These are the updated physics styles.
DUMMY_PHYSICS	= -1		# Does nothing. Useful for entities sitting in fixed positions on a vehicle.
STANDARD_PHYSICS = 0		# AvatarStyle, suitable for player
RIPPER_PHYSICS   = 1		# HoverStyle, for any hovering vehicle physics.
LIMPET_PHYSICS   = 2		# Causes controlled Entity to follow exact movements of Entity being chased.
TURRET_PHYSICS   = 3		# WeaponEmplacementStyle, useful for controlled turrets, guns, etc...
SIMPLE_PHYSICS   = 4		# SimpleStyle, suitable for animals
ONLYMOVE_PHYSICS = 5

CAP_NONE		= 0
CAP_NEVER		= 0	# This must be 0
CAP_CAN_HIT		= 1
CAP_CAN_USE		= 2
CAP_CAN_HACK	= 3
CAP_CAN_FEED	= 4
CAP_CAN_STUN	= 5
CAP_CAN_INHIBIT = 6
CAP_CAN_BUG		= 7
CAP_CAN_TAKE_DOWN = 8
CAP_AFTER_LAST	= 9
CAP_CAN_REVIVE	= 10

TRUE	= 1
FALSE	= 0

UPDATE_HERTZ = 10.0





# Helper function to calculate the intersection of a ray with a
#  convex polygon. Used with triangles from the collision scene.
# If passed a non-convex polygon it will return the furthest intersection
#  in the direction of rayDir.
# @args Math.Vector3 raySrc, Math.Vector3 rayDir, Sequence( Math.Vector3 ) polygon
# @returns a tuple of the position of intersection, and the yaw of the
#	vector perpendicular to the edge of the poly
#  rayDir should probably be normalised

def intersectRayWithPolygon( raySrc, rayDir, polygon ):
	# shift the origin of the polygon to the ray's start
	spoly = map( lambda pt, raySrc=raySrc: Math.Vector3( pt - raySrc ), polygon )

	# find the edges which are cut by dir (only 2 for a convex polygon)
	cands=[]
	for i in xrange(len(spoly)):
		apt = spoly[i]
		bpt = spoly[(i+1)%len(spoly)]
		across = rayDir.cross2D( apt )
		bcross = rayDir.cross2D( bpt )
		if (across > 0) != (bcross >= 0 ):
			cpt = bpt - apt
			numer = apt.cross2D( cpt )
			denom = rayDir.cross2D( cpt )
			cands.append((apt,cpt,numer/denom))

	# find the one with the biggest (positive) projection
	cands.sort( lambda s,t: -cmp( s[2], t[2] ) )

	# and that's the edge
	edge = raySrc + rayDir.scale( cands[0][2] )

	# find the vector perpendicular to the poly
	edgeParallel = cands[0][1]
	edgePerpendicular = Math.Vector3(-edgeParallel.z, 0, edgeParallel.x)
	if edgePerpendicular.dot(rayDir) < 0:
		edgePerpendicular = -edgePerpendicular
	edgeYaw = math.atan2(edgePerpendicular.x, edgePerpendicular.z)

	return (edge, edgeYaw)


# Some macros for the python console
macros = {
	"p":"BigWorld.player()",
	"t":"BigWorld.target()",
	"B":"BigWorld",
	"$":"$",
	}

#keys.py
