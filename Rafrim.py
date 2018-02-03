#coding: UTF-8
from __future__ import print_function
from sys import argv
import sys
import random
import time
from collections import defaultdict

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)		
def printList(list):
	txt = "["
	for i in list:
		txt += i + " , "
	txt = txt [:-1]
	txt += "]"
	print(txt)
def betterLower(word):
	word = word.lower()
	word = word.replace('êÈ','…')
	word = word.replace('˝','›')
	word = word.replace('˙','⁄')
	word = word.replace('Ì','Õ')
	word = word.replace('','–')
	word = word.replace('ô','î')
	word = word.replace('ç','ï')
	word = word.replace('í','ë')
	word = word.replace('ã','å')
	word = word.replace('§','†')
	return word

class poet(object):
	def __init__(self):
		self.markov = Markov(self)
		self.sylPattern = [8,5,8,5]
		self.rhymePattern = [1,2,1,2]
		self.minimumRhymeVowels = 2
		self.selfRhymeAllowed = False
		self.minorThreshold = .05
		self.relatedThreshold = .2
		self.interchangeableThreshold = .2
		self.Debug = False
		self.Status = False
	def add(self,text):
		self.markov.add(text)
	def add_file(self,file):
		F = open(file,'r')
		self.markov.add(F.read())
		F.close()
	def is_written_rhyme(self,word1,word2):
		vowels = "eyuioaÇò£°¢ëî†êóß•¶íô§!?"
		#! = ey/ei, ? = au
		forbidden = "/.!?,-:;/"
		vowelList = []
		for char in word1:
			if char in forbidden:
				word1 = word1.replace(char,'')
		for char in word2:
			if char in forbidden:
				word2 = word2.replace(char,'')
		
		if(not self.selfRhymeAllowed):
			if(word1 == word2):
				return False
		word1 = word1.replace("ei","!")
		word1 = word1.replace("ey","!")
		word1 = word1.replace("au","?")
		word2 = word2.replace("ei","!")
		word2 = word2.replace("ey","!")
		word2 = word2.replace("au","?")
		if(len(word1) < len(word2)):
			lead = word1
			follow = word2
		else:
			lead = word2
			follow = word1
		for i in range(len(lead)):
			if(lead[i] in vowels):
				vowelList.append(i)
		if(len(vowelList) < self.minimumRhymeVowels):		
			if(len(vowelList) == 0):
				firstVowel = 0
			else:
				firstVowel = vowelList[0]
		else:
			firstVowel = vowelList[-self.minimumRhymeVowels]

		ending = lead[firstVowel:]
		return follow.endswith(ending)
	def syllables(self,word):
		vowels = "eyuioaÇò£°¢ëî†êóß•¶íô§"
		c = 0
		for i in word:
			if i in vowels:
				c += 1 
		c -= word.count("au")
		c -= word.count("ey")
		c -= word.count("ei")
		return c
	def load_settings(self):
		F = open("settings.txt",'r')
		for line in F:
			M.set_setting(line)
		F.close()
	def set_setting(self,line):
		setting = line.split(':')
		if len(setting) <= 1:
			return
		
		if setting[0] == "syllables":
			self.sylPattern = []
			for num in setting[1].split():
				self.sylPattern.append(int(num))
		elif setting[0] == "rhymes":
			self.rhymePattern = []
			for num in setting[1].split():
				self.rhymePattern.append(int(num))
		elif setting[0] == "minVowelRhyme":
			self.minimumRhymeVowels = int(setting[1])
		elif setting[0] == "minorThreshold":
			self.minorThreshold = float(setting[1])
		elif setting[0] == "relatedThreshold":
			self.relatedThreshold = float(setting[1])
		elif setting[0] == "interchangeableThreshold":
			self.interchangeableThreshold = float(setting[1])
		elif setting[0] == "minVowelRhyme":
			self.minimumRhymeVowels = int(setting[1])
		elif setting[0] == "selfRhymesAllowed":
			if setting[1] == 'true':
				self.selfRhymeAllowed = True 
			elif setting[1] == 'false':
				self.selfRhymeAllowed = False 
		else:
			eprint("invalid setting  " + str(setting[0]))
	def generate(self,length):
		tries = 5
		list = self.markov.generate(length,self,tries)
		while(len(list) != length and tries > 0):
			eprint("I hit a writer block and scrapped the poem: [" + str(tries) + " attempts left]")
			list = self.markov.generate(length,self,tries)
			tries-=1
		if(len(list) < length):
			eprint("Could not create poem with these parameters this time, sorry. :(")
			return
		poem = ""
		line = 0
		for i in list:
			poem += i + "\n"
			line += 1
			if(line == len(self.rhymePattern)):
				poem += "\n"
				line = 0
		if(self.Debug or self.Status):
			print("------ POEM GENERATION FINISHED ----- \n \n")
		return poem
	def filterChoice(self,poem,newline,candidates):
		#SYLLABLE COUNT
		newFilt = [i for i in candidates if self.syllables(newline) + self.syllables(i) <= self.sylPattern[(len(poem))%len(self.sylPattern)]]
		verselength = len(self.rhymePattern)
		lastline = (len(poem) + 1) % verselength == 0
		#RHYMER
		for i in range(len(poem)+1 - verselength,len(poem)):
			if(i >= 0):
				if(i/(verselength) != len(poem) / (verselength)):
					continue
				if(self.rhymePattern[i % verselength] == self.rhymePattern[len(poem)%verselength]):
					#try rhymes
					rhymeWord = poem[i].split()[-1:][0]
					if(self.Debug):
						print("Trying to rhyme with " + rhymeWord)
					newFilt = [word for word in newFilt if self.is_written_rhyme(rhymeWord,word) or self.syllables(newline) + self.syllables(word) < self.sylPattern[(len(poem))%len(self.sylPattern)]]
				else:#avoid rhymes in off lines
					rhymeWord = poem[i].split()[-1:][0]
					newFilt = [word for word in newFilt if not self.is_written_rhyme(rhymeWord,word) or self.syllables(newline) + self.syllables(word) < self.sylPattern[(len(poem))%len(self.sylPattern)]]
				
					
			else:
				continue
		#EMPHASIZE GOOD WORDS 
		validWords = []
		for i in newFilt:
			isEnding = self.endingWord(i)
			sylLength = self.sylPattern[(len(poem))%len(self.sylPattern)]
			addSyll = self.syllables(newline) + self.syllables(i)
			if(isEnding and  addSyll == sylLength): #We want to end lines with punctuation marks
				validWords.append(i)
			if(not isEnding and addSyll < sylLength): #We don't want to have punctuation mid-sentence
				validWords.append(i)
			if(not lastline):
				if(addSyll == sylLength and self.syllables(i) > 2): #We want long words to end the lines
					for x in range(self.syllables(i)):
						validWords.append(i)
				validWords.append(i) #And the rest
			else:
				if(addSyll == sylLength and self.endingWord(i)): #We want to end the last line with punctuation
					for x in range(self.syllables(i)):
						validWords.append(i)
				if(addSyll < sylLength): #Otherwise just stick anything. 					
					for x in range(self.syllables(i)):
						validWords.append(i)
			for line in poem:
				for word in line.split():
					try:
						if word in self.markov.relatedWords[i]:
							validWords.append(i)
					except Exception:
						continue
		return validWords
	def endingWord(self,word):
		endings = '!?.:;"-/'
		return word[-1:] in endings
		

class Markov(object):
	def __init__(self,P):
		self.map = {}
		self.minorWords = []
		self.relatedWords = {}
		self.P = P
	def add(self,text):
		eprint("Analysing text...")
		split = text.split()
		minorSplit = text.split("\n\n")
		if(len(minorSplit) > 10):
			self.addMinor(minorSplit)
		if(len(split) == 0):
			return 
		eprint("Minor words identified")
		self.addRelated(minorSplit)
		last = betterLower(split[0])
		eprint("related words identified")
		first = True
		for i in split:
			if(first):
				first = False
				continue
			if(len(i) == 0):
				continue
			if(i == ' ' or i == '\n'):
				continue
			if not last in self.map.keys():
				self.map[last] = []
			self.map[last].append(betterLower(i))
			last = betterLower(i)
		
		eprint("Markov chain built.")
		eprint("Analysis done.")
	def generate(self,length,poet,T):
		timer = time.clock()
		T = 40
		last = random.choice(self.map.keys())
		poem = []
		i = -1
		while(i < length-1 and timer + T >= time.clock()):
			i+=1
			if(i < 0):
				i = 0
				poem = []
			if(poet.Debug or poet.Status):
				print("-Starting line " + str(i+1) + ", in verse " + str(1+(i / (len(poet.sylPattern)))))
			valid = False
			LLast = last
			tries = 0
			text = ""
			add = True
			while(not valid and timer + T >= time.clock()):
				if(poet.Debug):
					print("		*-STARTING NEW WORD IN LINE " + str(i))
				if last in self.map.keys():
					now = self.map[last]
				else:
					now = self.map.keys()
				
				if(poet.Debug):
					print("I WANT TO ADD : " + str(now))
				now = poet.filterChoice(poem,text,now)
				if(poet.Debug):
					print("VALD WORDS : " + str(now))
				if(len(now) == 0):
					if(poet.Debug):
						print("NO GOOD WORDS! D:")
					text = ""
					last = LLast
					tries += 1
					if(tries > 10):
						poem = poem[:-1]
						poem = poem[:-1]
						if(len(poem) > 0):
							LLast = poem[len(poem)-1].split()[-1:][0]
						else:
							LLast = random.choice(self.map.keys())
						last = LLast
						tries = 0
						valid = True
						add = False
						continue
				else:
					word = random.choice(now)
					if(poet.Debug):
						print("ADDING WORD: " + word)
					text += str(word) + " "
					last = word
					if(poet.Debug):
						print("LINE CURRENTLY IS  " + text)
					if poet.syllables(text) >= poet.sylPattern[(len(poem))%len(poet.sylPattern)]:
						valid = True
						if(poet.Debug):
							print("LINE OVER:  " + text)
					if(len(word) == 0):
						return ["ERROR:NONWORD"]
					
					if(poet.Debug):
						print("CURRENT SYLLABLES LEFT TO ADD : " + str(poet.sylPattern[(len(poem))%len(poet.sylPattern)] - poet.syllables(text)))
						print(poet.syllables(text) , str(poet.sylPattern[(len(poem))%len(poet.sylPattern)]))
						
			if(add):
				poem.append(text)
				if(poet.Status):
					print("Line completed, starting next line.")
				if(poet.Debug):
					print("POEM IS CURRENTLY  " + str(poem))
			else:
				if(poet.Status):
					print("Failed to author line, restarting last line.")
				if(poet.Debug):
					print("GOING BACK")
					print("POEM IS CURRENTLY  " + str(poem))
				i-=3
				T-=1
				if(T < 0):
					return ["CANNOT WRITE POEM"]
		if(timer + 4 <= time.clock()):
			return ["TIME OUT"]
		return poem
	def addMinor(self,verses):
		PoemCount = len(verses)
		histogram = {}
		for i in verses:
			split = set(i.split())
			for j in split:
				j = self.cleanWord(j)
				if not j in histogram.keys():
					histogram[j] = 0
				histogram[j] += 1
		for K in histogram.keys():
			if(histogram[K] / (0.00 + PoemCount) > self.P.minorThreshold):
				self.minorWords.append(K)
	def addRelated(self,verses):
		PoemCount = len(verses) 
		histogram = defaultdict(int)
		histoCount = defaultdict(int)
		for i in verses:
			split = [self.cleanWord(word) for word in i.split() if self.cleanWord(word) not in self.minorWords and word != '']
			for i in range(len(split)):
				histoCount[split[i]] += 1
				for j in range(i,len(split)):
					if(split[i] == split[j]):
						continue
					else:
						histogram[(split[i],split[j])] += 1
						histogram[(split[j],split[i])] += 1
		for Key in histogram.keys():
			Count = histoCount[Key[0]]
			if(((0.00 + histogram[Key]) / Count) > self.P.relatedThreshold):
				if(Key[0] not in self.relatedWords.keys()):
						self.relatedWords[Key[0]] = []
				self.relatedWords[Key[0]].append(Key[1])	
	def cleanWord(self,word):
		endings = '!?. :;"/-,'
		for x in word:
			if(x in endings):
				word = word.replace(x,'')
		word = betterLower(word)
		return word
		

M = poet()
M.load_settings()
M.add_file(argv[1])

while(True):
	eprint("\n")
	eprint("type in a command.")
	comm = raw_input('').split()
	if(len(comm) == 0):
		continue
	if comm[0] == "generate":
		if(len(comm) > 1):
			if(len(comm) == 2):
				print("1.")
				print(M.generate(int(comm[1])))
				sys.stdout.flush()
			else:
				if(len(comm) == 3):
					T = int(comm[2])
					while T > 0:
						eprint("Writing poem #" + str((int(comm[2]) - T) + 1) )
						print(str((int(comm[2]) - T) + 1) + ".")
						print(M.generate(int(comm[1])))
						sys.stdout.flush()
						print('\n')
						T-=1
	elif comm[0] == "settings":
		if(len(comm) > 1):
			if(comm[1] == "get"):
				M.load_settings()
	elif comm[0] == "quit":
		break
