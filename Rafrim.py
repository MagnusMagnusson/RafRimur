#coding: UTF-8
from __future__ import print_function
from sys import argv
import sys
import random
import time
from collections import defaultdict

def eprint(line):
	line = line.strip()
	print(line, file=sys.stderr)		
def printList(list):
	txt = "["
	for i in list:
		txt += i + " , "
	txt = txt [:-1]
	txt += "]"
	print(txt)
def betterLower(word):
	word = word.lower()
	word = word.replace('É','é')
	word = word.replace('Ý','ý')
	word = word.replace('Ú','ú')
	word = word.replace('Í','í')
	word = word.replace('Ð','ð')
	word = word.replace('Ö','ö')
	word = word.replace('Á','á')
	word = word.replace('Æ','æ')
	word = word.replace('Þ','þ')
	word = word.replace('Ó','ó')
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
		vowels = "eyuioaöéýúíóáæ"
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
		word1 = word1.replace("ei","!").replace("ey","!").replace("au","?")
		word2 = word2.replace("ei","!").replace("ey","!").replace("au","?")
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
		vowels = "eyuioaöéýúíóáæ"
		c = 0
		for i in word:
			if i in vowels:
				c += 1 
		c -= word.count("au")
		c -= word.count("ey")
		c -= word.count("ei")
		return c
	def load_settings(self):
		F = open("stillingar.txt",'r')
		for line in F:
			M.set_setting(line)
		F.close()
	def set_setting(self,line):
		setting = line.split(':')
		if len(setting) <= 1:
			return
		
		if setting[0] == "Atkvæði":
			self.sylPattern = []
			for num in setting[1].split():
				self.sylPattern.append(int(num))
		elif setting[0] == "Rím":
			self.rhymePattern = []
			for num in setting[1].split():
				self.rhymePattern.append(int(num))
		elif setting[0] == "MinniMörk":
			self.minorThreshold = float(setting[1])
		elif setting[0] == "TengdMörk":
			self.relatedThreshold = float(setting[1])
		elif setting[0] == "ÚtskiptalegMörk":
			self.interchangeableThreshold = float(setting[1])
		elif setting[0] == "LámarksAtkvæðaRím":
			self.minimumRhymeVowels = int(setting[1])
		elif setting[0] == "SjálfRímLeyft":
			if setting[1] == 'rétt':
				self.selfRhymeAllowed = True 
			elif setting[1] == 'rangt':
				self.selfRhymeAllowed = False 
		else:
			eprint("stilling ógild  " + str(setting[0]))
	def generate(self,length):
		tries = 5
		list = self.markov.generate(length,self,tries)
		while(len(list) != length and tries > 0):
			list = self.markov.generate(length,self,tries)
			tries-=1
		if(len(list) < length):
			eprint("Gat ekki ort ljóð með þessum stillingum þetta sinn. Fyrirgefðu.")
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
			print("------ LJÓÐSKÖPUN LOKIÐ ----- \n \n")
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
		eprint("Greini texta...")
		split = text.split()
		minorSplit = text.split("\n\n")
		if(len(minorSplit) > 10):
			self.addMinor(minorSplit)
		if(len(split) == 0):
			return 
		eprint("smáorð greind")
		self.addRelated(minorSplit)
		last = betterLower(split[0])
		eprint("skyld orð fundin")
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
		
		eprint("Markov keðja sköpuð.")
		eprint("Greiningu lokið.")
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
				print("-Hef línu " + str(i+1) + ", í erindi " + str(1+(i / (len(poet.sylPattern)))))
			valid = False
			LLast = last
			tries = 0
			text = ""
			add = True
			while(not valid and timer + T >= time.clock()):
				if(poet.Debug):
					print("		*-Hef nýtt ljóð í línu " + str(i))
				if last in self.map.keys():
					now = self.map[last]
				else:
					now = self.map.keys()
				
				if(poet.Debug):
					print("Ég vill bæta við : " + str(now))
				now = poet.filterChoice(poem,text,now)
				if(poet.Debug):
					print("Gild orð : " + str(now))
				if(len(now) == 0):
					if(poet.Debug):
						print("Engin góð orð fundust")
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
						print("Bæti við orði : " + word)
					text += str(word) + " "
					last = word
					if(poet.Debug):
						print("Núverandi lína er  " + text)
					if poet.syllables(text) >= poet.sylPattern[(len(poem))%len(poet.sylPattern)]:
						valid = True
						if(poet.Debug):
							print("Línu lokið:  " + text)
					if(len(word) == 0):
						return ["Villa: Engin orð gild"]
					
					if(poet.Debug):
						print("Atkvæði enn ósamin : " + str(poet.sylPattern[(len(poem))%len(poet.sylPattern)] - poet.syllables(text)))
						print(poet.syllables(text) , str(poet.sylPattern[(len(poem))%len(poet.sylPattern)]))
						
			if(add):
				poem.append(text)
				if(poet.Status):
					print("Línu lokið, hef næstu línu.")
				if(poet.Debug):
					print("Núverandi ljóð er " + str(poem))
			else:
				if(poet.Status):
					print("Ekki tókst að semja línu, byrja aftur frá fyrri línu.")
				if(poet.Debug):
					print("Bakka")
					print("Núverandi ljóð er  " + str(poem))
				i-=3
				T-=1
				if(T < 0):
					return ["Get ekki skrifað ljóð"]
		if(timer + 4 <= time.clock()):
			return ["Tími upprunninn"]
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
		
eprint("Velkomin. Rafrímur virkur.")
M = poet()
M.load_settings()
M.add_file(argv[1])

while(True):
	eprint("\n")
	eprint("Sláið inn skipun.")
	comm = raw_input('').split()
	if(len(comm) == 0):
		continue
	if comm[0] == "yrkja":
		if(len(comm) > 1):
			if(len(comm) == 2):
				print("1.")
				print(M.generate(int(comm[1])))
				sys.stdout.flush()
			else:
				if(len(comm) == 3):
					T = int(comm[2])
					while T > 0:
						eprint("yrki ljóð #" + str((int(comm[2]) - T) + 1) )
						print(str((int(comm[2]) - T) + 1) + ".")
						print(M.generate(int(comm[1])))
						sys.stdout.flush()
						print('\n')
						T-=1
	elif comm[0] == "stillingar":
		if(len(comm) > 1):
			if(comm[1] == "sækja"):
				M.load_settings()
	elif comm[0] == "hætta":
		break
