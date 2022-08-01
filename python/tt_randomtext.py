#
# Random text generation
#
# RandomText{N}
#		produce N random words, sentence capitalization and punctuation will be injected.
#
# Scan the document and replace RandomText{N}
# tag nodes with N words. Sentence capitalization
# and punctuation will be added.
#
# RandomWords{N}
#		produce N random words
#
# RandomPhrase{N}
#		produce N random words, capitalize first word
#
# ChooseTerm{ T{term1} T{term2} T{term3} ... word1 word2 }
#		Choose randomly one of the terms. a simple word may
#		be used instead of enclosing inside of T{...} tag.
#		In fact any taggedtext nodes may be given, use T{} to
#		group nodes which should be treated as a single unit.
#
# Once variants:
#	RandomTextOnce{N}
#	RandomWordsOnce{N}
#	RandomPhraseOnce{N}
#	ChooseTermOnce{N}
#
# The "once" variants will emit the same random text once. This
# only makes sense in contexts like the DEFINE{} macros.
# Consider these two similar constructions:
#
#	DEFINE{ Bob{ RandomText{10} } }
#
# versus,
#
#	DEFINE{ Bob{ RandomTextOnce{10} } }
#
# Whenever the macro Bob{} is used, you may want the same
# random text emitted each time. In that case use the "once" variant.
# The first construction will give different random text each time
# the Bob{} macro is used.
#
# How do the "once" variants work? They maintain a lookup table key'd on
# the tag filename, line number, column position.
#
import re
import random
import taggedtext

WordList = [
"lorem", "ipsum", "dolor", "sit", "amet", "consectetuer", "adipiscing", "elit", "nullam", "erat",
"nunc", "tincidunt", "non", "commodo", "ac", "bibendum", "in", "elit", "vivamus", "sit", "amet",
"velit", "etiam", "at", "leo", "in", "aliquam", "tellus", "vitae", "lobortis", "mattis", "libero",
"neque", "luctus", "justo", "a", "pulvinar", "neque", "lectus", "quis", "pede", "duis", "magna",
"suspendisse", "at", "risus", "sed", "porttitor", "ultricies", "quam", "sed", "tempus", "dui",
"duis", "feugiat", "sem", "quis", "nisl", "nullam", "consequat", "pede", "at", "odio", "curabitur",
"placerat", "quisque", "neque", "magna", "accumsan", "vel", "suscipit", "id", "hendrerit", "in",
"lectus", "suspendisse", "eu", "libero", "in", "augue", "dapibus", "facilisis", "praesent",
"sagittis", "porttitor", "massa", "aliquam", "placerat", "odio", "nec", "nulla", "phasellus",
"nunc", "mauris", "lacinia", "quis", "suscipit", "vitae", "tristique", "quis", "turpis",
"suspendisse", "et", "erat", "nam", "ornare", "nulla", "suspendisse", "vestibulum",
"adipiscing", "risus", "nullam", "adipiscing", "rutrum", "risus", "curabitur", "ut", "magna",
"vel", "nisi",  "sollicitudin", "egestas", "in", "fringilla", "turpis", "non", "dui", "integer",
"in", "tellus",  "praesent", "lacus", "donec", "luctus", "aliquam", "convallis", "est", "nec",
"purus", "vivamus", "volutpat", "turpis", "a", "elit", "proin", "congue", "sapien", "eget",
"lobortis", "varius",  "massa", "sapien", "suscipit", "elit", "vitae", "interdum", "nunc",
"sapien", "eu", "est", "quisque",  "eros", "donec", "nonummy", "viverra", "quam", "fusce",
"convallis", "enim", "eget", "vulputate",  "mattis", "risus", "enim", "blandit", "sem", "vel",
"cursus", "tortor", "diam", "in", "felis", "in",  "placerat", "pellentesque", "dictum",
"praesent", "vel", "mauris", "cras", "nisl", "etiam",  "non", "orci", "volutpat", "dui", "tincidunt",
"elementum", "aenean", "ultricies", "massa", "id",  "tellus", "venenatis", "semper", "aenean",
"urna", "urna",

"kiwanis", "frightened", "distressing", "mightier", "pasternak", "hilariously", "contaminant",
"cinemascope", "descendant", "tremulous", "pepperoni", "burner", "interrogatory", "repatriating",
"terminal", "chatterer", "louisianans", "dianna", "rhinestone", "entitle", "azores",
"quid", "comedies", "radish", "bermuda", "remiss", "tapping", "deadened", "wounder",
"locksmiths", "garbled", "directest", "sequoias", "dormant", "tangos", "citron", "catcall",
"compatriot", "miasmata", "miscarriage", "medicates", "nonconductor", "bell", "measure",
"napes", "primmest", "transacted", "boy", "recoups", "pitcairn", "peeves", "overreacts", "mindy",
"liberalizing", "martyrdom", "liquifying", "showboated", "joyed", "control", "councillor",
"gloves", "pyramidal", "seafood", "pottery", "raids", "recorder", "inhere", "install", "partings",
"datelined", "doubtless", "blasphemer", "tamps", "edna", "fraternally", "batter",
"wormwood", "sacrilegious", "mantelpieces", "sapience",
"delaying", "ragamuffins", "coriander", "nitrogen", "maisie", "unionized", "arron", "modified",
"musicology", "paperboy", "indulging", "cageyness", "chlorinate", "sturdiest", "virago",
"delivered", "distortion", "ungulate", "rudiment", "pathway", "quadrupeds", "snake", "mapper",
"pediatrics", "begins", "overdosed", "protocols", "effete", "drubbings", "patronymic", "loiter",
"yalta", "spitted", "congregated", "reparation", "mineralogists", "grainiest", "eiders",
"saloons", "manly", "gnarly", "tippler", "nostrils", "emptiest", "lurks",

"interleave",
"irruptions",
"declination",
"spotty",
"reentered",
"undergraduate",
"exposing",
"remarks",
"dozen",
"cali",
"mainline",
"mainstays",
"swashbuckling",
"whisk",
"suzhou",
"banjoist",
"misconception",
"musically",
"bacchanals",
"infielder",
"checkup",
"kazoos",
"descanting",
"nauru",
"frisian",
"bibliophile",
"payload",
"fingering",
"endurance",
"ruffian",

"pedometer",
"diacritics",
"profligacy",
"representations",
"dixie",
"idiomatic",
"portico",
"point",
"tiding",
"workstation",
"alnilam",
"measure",
"balances",
"stucco",
"plagiarist",
"consign",
"persevere",
"entertainment",
"diphtheria's",
"distincter",
"drowning",
"pleasant",
"schumann",
"giraffe",
"volstead",
"cur's",
"janitor",
"landlubber",
"valparaiso",
"smarmy",

"said", "to", "himself", "that", "it", "was", "not", "such", "a", "hollow", "world", "after", "all", "he",
"had", "discovered", "a", "great", "law", "of", "human", "action", "without", "knowing", "it", "namely",
"that", "in", "order", "to", "make", "a", "man", "or", "a", "boy", "covet", "a", "thing", "it", "is", "only", "necessary",
"to", "make", "the", "thing", "difficult", "to", "attain", "if", "he", "had", "been", "a", "great", "and",
"wise", "philosopher", "like", "the", "writer", "of", "this", "book", "he", "would", "now", "have",
"comprehended", "that", "work", "consists", "of", "whatever", "a", "body", "is", "obliged", "to", "do",
"and", "that", "play", "consists", "of", "whatever", "a", "body", "is", "not", "obliged", "to", "do", "and",
"this", "would", "help", "him", "to", "understand", "why", "constructing", "artificial", "flowers", "or",
"performing", "on", "a", "tread", "mill", "is", "work", "while", "rolling", "ten", "pins", "or", "climbing",
"mont", "blanc", "is", "only", "amusement", "there", "are", "wealthy", "gentlemen", "in", "england",
"who", "drive", "four", "horse", "passenger", "coaches", "twenty", "or", "thirty", "miles", "on", "a",
"daily", "line", "in", "the", "summer", "because", "the", "privilege", "costs", "them", "considerable",
"money", "but", "if", "they", "were", "offered", "wages", "for", "the", "service", "that", "would", "turn",
"it", "into", "work", "and", "then", "they", "would", "resign",

"mr.",
"mrs.",
"ms.",
"somebody's",

"poor", "girl", "she", "did", "not", "know", "how", "fast", "she", "was", "nearing", "trouble", "herself",
"the", "master", "dobbins", "had", "reached", "middle", "age", "with", "an", "unsatisfied",
"ambition", "the", "darling", "of", "his", "desires", "was", "to", "be", "a", "doctor", "but",
"poverty", "had", "decreed", "that", "he", "should", "be", "nothing", "higher", "than", "a", "village",
"schoolmaster", "every", "day", "he", "took", "a", "mysterious", "book", "out", "of", "his", "desk", "and",
"absorbed", "himself", "in", "it", "at", "times", "when", "no", "classes", "were", "reciting", "he", "kept",
"that", "book", "under", "lock", "and", "key", "there", "was", "not", "an", "urchin", "in", "school", "but", "was",
"perishing", "to", "have", "a", "glimpse", "of", "it", "but", "the", "chance", "never", "came", "every", "boy",
"and", "girl", "had", "a", "theory", "about", "the", "nature", "of", "that", "book", "but", "no", "two", "theories",
"were", "alike", "and", "there", "was", "no", "way", "of", "getting", "at", "the", "facts", "in", "the", "case",
"now", "as", "becky", "was", "passing", "by", "the", "desk", "which", "stood", "near", "the", "door", "she",
"noticed", "that", "the", "key", "was", "in", "the", "lock", "it", "was", "a", "precious", "moment", "she",
"glanced", "around", "found", "herself", "alone", "and", "the", "next", "instant", "she", "had", "the",
"book", "in", "her", "hands", "the", "titlepage", "professor",  "anatomy", "carried",
"no", "information", "to", "her", "mind", "so", "she", "began", "to", "turn", "the", "leaves", "she", "came", "at",
"once", "upon", "a", "handsomely", "engraved", "and", "colored", "frontispiece", "a", "human", "figure",
"stark", "naked", "at", "that", "moment", "a", "shadow", "fell", "on", "the", "page", "and", "tom", "sawyer",
"stepped", "in", "at", "the", "door", "and", "caught", "a", "glimpse", "of", "the", "picture", "becky",
"snatched", "at", "the", "book", "to", "close", "it", "and", "had", "the", "hard", "luck", "to", "tear", "the",
"pictured", "page", "half", "down", "the", "middle", "she", "thrust", "the", "volume", "into", "the", "desk",
"turned", "the", "key", "and", "burst", "out", "crying", "with", "shame", "and", "vexation",

"every", "detail", "of", "the", "damaging", "circumstances", "that", "occurred", "in", "the",
"graveyard", "upon", "that", "morning", "which", "all", "present", "remembered", "so", "well", "was",
"brought", "out", "by", "credible", "witnesses", "but", "none", "of", "them", "were", "cross", "examined",
"by", "potter's", "lawyer", "the", "perplexity", "and", "dissatisfaction", "of", "the", "house",
"expressed", "itself", "in", "murmurs", "and", "provoked", "a", "reproof", "from", "the", "bench",
"counsel", "for", "the", "prosecution", "now", "said"

]

######################################################################
######################################################################
######################################################################

def once_key(root):
	return '%s-%d-%d' % (root.filename(), root.lineno(), root.column())

######################################################################
#
# Check to see if we have computed random text already
# for node 'root'. If yes, return a list of word nodes.
# If once_data is None do nothing.
#
# Return None if no once data was found
#
def get_once(root, once_data):
	if once_data != None:
		k = once_key(root)
		if k in once_data:
			return once_data[k]
		else:
			return None
	else:
		return None

######################################################################
#
# Set once_data with new data for 'root'. If once_data is None
# then do nothing.
#
def set_once(root, once_data, result):
	if once_data != None:
		k = once_key(root)
		once_data[k] = result

######################################################################
#
# Check the root has a single child which is a word, which
# is an integer. Return that number as an integer on success.
# On error return None, and morph root into an error node.
#
def process_argument(root):
	nc = root.num_children()
	if nc != 1:
		n = taggedtext.make_error_node(
					root.filename(),
					root.lineno(),
					root.column(),
					"%s{} tag contains %d elements (should be 1)"
								% (root.tag(), nc) )

		root.morph(n)
		return None

	c = root.get_child(0)
	if not c.is_word():
		n = taggedtext.make_error_node(
					root.filename(),
					root.lineno(),
					root.column(),
					"%s{} expected to contain a single integer." % (root.tag()) )
		root.morph(n)
		return None

	count_str = c.word()

	if re.match(r'[0-9]+', count_str) == None:
		n = taggedtext.make_error_node(
				root.filename(),
				root.lineno(),
				root.column(),
				"%s{} word is not an integer [0-9]+." % (root.tag()) )
		root.morph(n)
		return None

	count = int(count_str)
	return count

######################################################################
#
# RandomText{100}
# RandomTextOnce{100}
#
# root is a RandomText{N} tag node.
# Do error check on the children.
# Append N random words to 'tmp'. Add sentence
# capitalization and punctuation.
#
# In the event of an error append an 
# error node to tmp.
#
def eval_random_text(root, once_data):

	n = get_once(root, once_data)
	if n != None:
		return n

	count = process_argument(root)
	if count == None:
		return [root]

	result = []
	capitalize = True
	for i in range(count):
		word = random.choice(WordList)

		if capitalize:
			capitalize = False
			word  = word.capitalize()

		if random.randint(0, 25) == 0 or i+1 == count:
			word += '.'
			capitalize = True
		elif random.randint(0, 20) == 0:
			if random.randint(0, 5) == 0:
				word += ';'
			else:
				word += ','

		w = taggedtext.make_word_node(
					root.filename(),
					root.lineno(),
					root.column(),
					word )

		result.append(w)

	set_once(root, once_data, result)
	return result

######################################################################
#
# RandomWords{123}
# RandomWordsOnce{123}
#
def eval_random_words(root, once_data):
	n = get_once(root, once_data)
	if n != None:
		return n

	count = process_argument(root)
	if count == None:
		return [root]

	result = []

	for i in range(count):
		word = random.choice(WordList)

		w = taggedtext.make_word_node(
					root.filename(),
					root.lineno(),
					root.column(),
					word )

		result.append(w)

	set_once(root, once_data, result)
	return result

######################################################################
#
# RandomPhrase{12}
# RandomPhraseOnce{12}
#
def eval_random_phrase(root, once_data):
	n = get_once(root, once_data)
	if n != None:
		return n

	count = process_argument(root)
	if count == None:
		return [root]

	result = []

	capitalize = True
	for i in range(count):
		word = random.choice(WordList)

		if capitalize:
			capitalize = False
			word  = word.capitalize()

		w = taggedtext.make_word_node(
					root.filename(),
					root.lineno(),
					root.column(),
					word )

		result.append(w)

	set_once(root, once_data, result)
	return result

######################################################################
#
# ChooseTerm{ e1 e2 e3 }
# ChooseTermOnce{ e1 e2 e3 }
#
def eval_choose_term(root, once_data):
	n = get_once(root, once_data)
	if n != None:
		return n

	n = random.choice( list(root.children()) )

	if n.is_tag_named("T"):
		result = []
		for child in n.children():
			result.append(child)
		set_once(root, once_data, result)
		return result
	else:
		set_once(root, once_data, [n])
		return [n]

def run(root):
	once_data = {}

	eval_functions = {
		'RandomText':			(lambda root: eval_random_text(root, None)),
		'RandomWords':			(lambda root: eval_random_words(root, None)),
		'RandomPhrase':			(lambda root: eval_random_phrase(root, None)),
		'ChooseTerm':			(lambda root: eval_choose_term(root, None)),

		'RandomTextOnce':		(lambda root: eval_random_text(root, once_data)),
		'RandomWordsOnce':		(lambda root: eval_random_words(root, once_data)),
		'RandomPhraseOnce':		(lambda root: eval_random_phrase(root, once_data)),
		'ChooseTermOnce':		(lambda root: eval_choose_term(root, once_data)),
	}

	root.eval(eval_functions)

