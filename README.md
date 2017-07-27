# RafRimur
Making Python compose poetry in Icelandic.

RafRímur (Lit. translation "Electro-Rhymes") is a python script I've been working on for a while in my initial
effort to practice implementing Markov-chain text generators. 

The script takes in a text file filled with Icelandic poetry, creates markov chains from it, makes some small further analysis to better 
form somewhat coherent poems, and then will generate poems as requested by the user in the format stated by the user.

Poems start with a random word from somewhere in the database, and then the Markov class generates a list of words it wants to add
depending on what are valid contiuations to the Markov chain of the current word. The M.class submits this list to the Poet class, which 
will remove words that do not fit the format of the poem, increase the odds of words it thinks are good, and further emphasize words
it believes are relevant to the poem as currently generated to try and increase the odds of the poem following a coherent theme. 

The Poet class then returns this list back to the Markov class which will then randomly select the next word from the approved list, and
repeat the process with that word until it either has a complete poem or it hits a writer block, being unable to continue the poem despite
multiple attempts. 

Note that the script will not work correctly with languages that do not have consistent phonemic orthography (They way words sound correlates 
to the way words are spelt). Languages such as English where words that look like they rhyme (Dead rhymes with led, but heart does not rhyme with beard nor heard.)
will be interpreted incorrectly and thus poems will be generated where the verses *seem* to rhyme as written but in reality don't rhyme at all.

Icelandic has extremely regular spelling and thus is easy for computers to rhyme with: if the words have similar spellings it will rhyme in a 
hyper-majority of cases. 

The following are the files in this repo:

## Rafrim.py

The main python script. Includes two classes.

### Poet 
Poet is a class that is intended to manage the Markov chain and provide guide and direction to it as it is composing.
It is in charge of issuing commands to Markov, it stores the settings it is working with, acts on the commands issued by 
the user trough the shell, and helps Markov know what words are valid, invalid or important when it is trying to select the
next word in the poem. 

### Markov 
Markov is the actual Markov generator. It is a fairly standard Markov chain generator, using various maps and lists to both
store the connections it knows, the lists of minor words it knows aren't "real" words that add meaning to the poem, and various functions
intended to create the dictionary, analyse the text presented, and of course generate the poems itself.

### The "main" code at the end of the file.

Simply a tiny shell interpreted intended to add the initial poetry file and after that take in commands from the shell and generate poems until 
the user wishes to quit. 

### Helper functions

A couple of functions at the top. Mostly self-explanatory.

## ljod.txt

A text file with real poems that Rafrimur will use to generate the markov data, learn "proper" grammar and syntax, and 
use to relate similarly themed words together. All poems are copyrighted by their authors or estates, as some poems in there
are not yet in public domain even if most are. 

## settings.txt

Settings used to control the form and function of the poems generated. 
it is possible to affect what lines rhyme, how many syllables are in each rhyme, if words
are allowed to rhyme with themself, if there is a limit on how few syllables count as "rhymes" in 
words that are long enough, and more minor things that affect how the Markov data is analysed. 

## utljod.txt

just a blank text file I use to pipe the generated poems into from the script. 

