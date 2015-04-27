"""
Jon Sims
CS 361
Cuckoohash EC

Hash table identical to assignment 3, only with cuckoohashing now implemented. This program will attempt to 
hash a word with three different algorithms in order to determine its location in the table. When each hash 
hashes to the same number, the table is resized. When two words hash to the same three hash values, the table 
is resized. When the load factor is exceded (which never happens) the table is resized. See inline comments.
"""
#SymbolTable was written by me but seems almost identical to your Java version
#The rest of the imports are standard stuff for i/o and math operations
import SymbolTable
import fileinput
import sys
import operator
import hashlib
import re
import weakref
import time

class wordfreq:

    #parallel arrays of strings and ints for words and frequencies
    tableKeys = []
    tableVals = []
    #pointer to a regex
    isWord = weakref.ref(re.compile("[\w\d_]"))
    m = 0
    n = 0
    #load and freq are user input
    load = 0.0
    freq = 0.0


    #This method takes a number n and checks whether or not is it prime.
    #If n is prime, n is returned, if not, n=n+1 is checked again
    #This method is used when the hash table is resized to be bigger
    #or smaller.
    def primeNumber(self,n):
        werks = True
        n = int(n)
        while True: 
            for i in range(2,(n-1)/2):
                if operator.mod(n,i)==0:
                    werks = False
                    break
            if werks:
                return n
            else:
                werks = True
                n = n+1
    
    #regex check a char for being a word
    def isNotWord(self,c,end=False):
        return not self.isWord().match(c)        
    
    #Resizes the table. 
    def resizeTable(self):
        tempKeys = []
        tempVals = []
        for i in range(0,self.m):
            tempKeys.append("")
            tempVals.append(0)
        tableKeys = self.tableKeys[:]
        tableVals = self.tableVals[:]
        self.tableKeys = tempKeys
        self.tableVals = tempVals
        self.n = 0
        for i in range(len(tableKeys)-1):
            if tableVals[i]!=0:
                self.put(tableKeys[i],tableVals[i])
                
            
    #Put key with val into table. If something is at key's location (i.e. all 3 of key's hashed locations
    #are occupied), put must be called again on one of the three words which occupy key's location.
    def put(self,key,value,locs=[]):
	#load factor check
        if self.n >= ((0.55+(self.load*0.04))*self.m):
            self.m = self.primeNumber((self.m/(0.7+(self.freq*0.03)))+1)
            self.resizeTable()
            print "HI"
	#initial insertion. locs will contain the location for the current key. if locs contains more than
	#one number, then each subsequent number corrolated to the location in the table for the key at the
	#current position. I.e. theres one loc for no rehashes (when one of key's hashed locations is empty),
	#theres two locs for one rehash (when key has no empty spots and one key at one spot must be reinserted)
	#et cetera. There are checks for when a key already in the table is inserted.
        if len(locs)==0:
            locs = self.cuckooHash(key,[])
            if len(locs) == 0:
                print "fail"
                self.m = self.primeNumber((self.m/(0.7+(self.freq*0.03)))+1)
                self.resizeTable()
                print "fail"
                self.put(key,value,[])
                return
        temp = locs[0]
        oldVal = (self.tableKeys[temp],self.tableVals[temp])
	#if oldVal is not empty, then locs must contain more than one location and each oldVal corrolates to each
	#additional loc
        self.tableKeys[temp] = key
	#first insertion of an item
        if self.tableVals[temp]==0 or (self.tableKeys[temp]!=key and value==1):
            self.tableVals[temp] = value
            self.n+=1               
	#item exists in table
        else:
            self.tableVals[temp] = self.tableVals[temp] + value    
	#recall put for key having both locs filled              
        if oldVal[0]!="" and oldVal[0]!=key:
            self.put(oldVal[0],oldVal[1],locs[1:])

    #See the hash method for the reeel werk
    def get(self,key):
        temp =  self.cuckooHash(key,[])
        if len(temp)==1:
            return self.tableVals[temp[0]]
        return 0

    #Cuckoohash, get a list of locs for a given key, and if loc list is only one long, then key probably exists.
    def delete(self,key):
        temp = self.cuckooHash(key,[])
        if len(temp)==1:
	    #key must exist if next conditional is true
            if self.tableVals[temp[0]]!=0:
                self.n-=1
                self.tableVals[temp[0]] = 0
                self.tableKeys[temp[0]] = ""
                return 1
        return 0

    def hash0(self,key):
        return operator.mod(int(operator.rshift(operator.xor(hash(key[1:]),int(hashlib.sha384(key).hexdigest(),16)), 8)), self.m)

    def hash1(self,key):
        return  operator.mod(int(operator.rshift(operator.xor(int(hashlib.md5(key[::-1]).hexdigest(),16),int(hashlib.sha256(key[::-1]).hexdigest(),16)),15)), self.m)

    def hash2(self,key):
        return  operator.mod(int(operator.rshift(operator.xor(int(hashlib.md5(key[::-1]).hexdigest(),16),hash(key+key[0:int(((1.0*len(key))-0.5)/2.0)])),2)), self.m)


    #Params: key, a string, and recur, a list of past locations, for recursive purposes.
    #Same comments as 2 hash algorithm up to complex logic stuff
    def cuckooHash(self,key,past=[]):
	hashedKey0 = self.hash0(key)
        hk0 = self.tableKeys[hashedKey0]
        if hk0==key and past==[]:
            return [hashedKey0]
	hashedKey1 = self.hash1(key)
        hk1 = self.tableKeys[hashedKey1]
        if hk1==key and past==[]:
            return [hashedKey1]
        hashedKey2 = self.hash2(key)
        hk2 = self.tableKeys[hashedKey2]
        if (hashedKey0 == hashedKey1 and hashedKey1==hashedKey2) or ((hashedKey0 in past) and (hashedKey1 in past) and (hashedKey2 in past)):
            print "UBER FAIL"
            print key, past
            return []
        if hk2==key and past==[]:
            return [hashedKey2]
        if hk0=="":
            past.append(hashedKey0)
            return past
        if hk1=="":
            past.append(hashedKey1)
            return past
        if hk2=="":
            past.append(hashedKey2)
            return past
	#complex logic stuff
	#all three locs occupied
        p1 = past[:]
        p2 = past[:]
        p3 = past[:]
        p1.append(hashedKey0)
        p2.append(hashedKey1)
        p3.append(hashedKey2)
	#Three if's here are true only if not initial insertion
	#i.e. were looking for an alternative loc for something in 
	#one of the initial key's spots
        if  hashedKey0 in past:
            p1=[]
        if hashedKey1 in past:
            p2 = []
        if  hashedKey2 in past:
            p3=[]
        if hk2 == key:
            p3 = []
	    #three sub if's are to make sure that same path isnt accidentally
	    #checked twice, which can cause problems
        if hk1 == key:
            p2 = []
        if hk0 == key:
            p1 = []
	#aptly named
        if p1==[] and p2==[] and p3==[]:
            return []
        return self.complexConditional(p1,p2,p3)
        

    #params: past.append(one of the three locations)
    #each l is a list of past + one potential spot
    #this method tells us what is the best potential spot
    def complexConditional(self, l1, l2, l3):
        temp1 = []
	#see prior comments if next line makes no sense
        if len(l1)>0:
            h1 = l1[len(l1)-1]
	    #prevent circles of checking spots(i.e. stack overflow)
            #if not ((h1 in l2) or (h1 in l3)):
            hk1 = self.tableKeys[h1]
            temp1 = self.cuckooHash(hk1,l1)
        temp2 = []
        if len(l2)>0:
            h2 = l2[len(l2)-1]
            #if  not ((h2 in l1) or (h2 in l3)):
            hk2 = self.tableKeys[h2]
            temp2 = self.cuckooHash(hk2,l2)
        temp3 = []
        if len(l3)>0:
            h3 = l3[len(l3)-1]
            #if not ((h3 in l1) or (h3 in l2)):
            hk3 = self.tableKeys[h3]
            temp3 = self.cuckooHash(hk3,l3)
	#all three spot's have had their paths traversed for an open spot.
	#now, find the shortest one
	#the paths would be [] if they dont work
        if temp1!=[] and (len(temp1)<=len(temp2) or temp2==[]) and (len(temp1)<=len(temp3) or temp3==[]):
            return temp1
        elif temp2!=[] and (len(temp2)<=len(temp1) or temp1==[]) and (len(temp2)<=len(temp3) or temp3==[]):
            return temp2
        elif temp3!=[] and (len(temp3)<=len(temp1) or temp1==[]) and (len(temp3)<=len(temp2) or temp2==[]):
            return temp3
        return []
    '''

        if (len(temp1)>=len(temp2) and len(temp2)>0) or (len(temp1)==0):
            if (len(temp2)>=len(temp3) and len(temp3)>0) or (len(temp2)==0):
                return temp3
            return temp2
        if (len(temp3)>=len(temp1) and len(temp1)>0) or (len(temp3)==0):
            return temp1
        if len(temp3)>0:
            return temp3
            return []'''
        
            
    #Returns m, the capacity of the table
    def size(self):
        return self.m

    #Returns n, the number of elements in the table
    def keys(self):
        return self.n

    #public static void main(String[] args)
    #Initializes stuff; iterates throught the arg[1] file (usually a text file,
    #puts words into the table as keys with a value of one, then prints a message
    #on some statistics of the file's words. The user may then enter input which
    #will invoke a get, remove, informative message, or exit. If the input is "",
    #exit, if "!1!", informative message on what chars are allowed as input and
    #which ones are not, if "-" followed by a word, the word is removed, and if
    #simply a word, the word's value is retrived by a get.
    def __init__(self,f):
        for i in range(0,997):
            self.tableKeys.append("")
            self.tableVals.append(0)
        self.m = 997
        self.n = 0
        print "How high do you want the load factor to be (scale of 0 to 9 w/ 0 being lowest):"
        self.load = int(raw_input('--> ')) + 0.0
        print "How frequently do you want the table to resize (scale of 0 to 9 w/ 0 being least)(this actually affects the load factor more):"
        self.freq = int(raw_input('--> ')) + 0.0
        print "I hope those were low values, because large values take a while"
        file = open(f,"r")
        start = 0
        word = ""
        for line in file:
            if len(line)>1:
                start = -1
                for i in range(0,len(line)):   
                    end = False
                    if (self.isNotWord(line[i]) or i==(len(line)-1)) and i!=0:
                        if self.isNotWord(line[i-1]) is not True:
                            if i<(len(line)-1):
                                if (line[i]!="-" and line[i]!="'") or self.isNotWord(line[i+1]):
                                    end=True
                            elif line[i]=="-":
                                word = line[start:i] 
                            elif self.isNotWord(line[i-1]) is not True:
                                end = True
                    elif start==(-1) and (self.isNotWord(line[i]) is not True):
                        start = i
                    if end: 
                        word = word + line[start:i]
                        self.put(word.lower(),1,[])  
                        start = -1
                        word = ""
        if self.n == 0:
            print "Error: bad file.\nThe file provided as arg 1 is not valid"
            return 
        print "This text contains " + str(self.keys()) +  " distinct words."
        print "Current load-factor: " + str(100.0*((1.0*self.n)/(1.0*self.m)))+"% ."
        print "M = ", self.m, "; N = ", self.n
        print "Please enter a word to get its frequency, or hit enter to leave."
        s = (raw_input('--> ')).lower()
        while s!="":
            if s[0]=="-":
                dell = self.delete(s[1:])
                if dell ==1:
                    print s[1:] + " has been deleted."
                elif dell==0:
                    print "Error: " + s[1:] + " is not in the hashtable."
            else:
                if self.isNotWord(s):
                    print "\"" + str(s) + "\" is not valid input. Please enter a word."
                else:
                    temp = self.get(s)
                    if temp!=0:
                        print str(s) + " appears " + str(self.get(s)) + " times."
                    else:
                        print str(s) + " does not appear."
            s = raw_input('--> ')
        print "Goodbye!"

if len(sys.argv)!= 2:
    print "Error: bad args \nUsage: python wordfreq file where file is some file \ncontaining text readable by Python's stdio open() method"
else:
    i = wordfreq(sys.argv[1])
    
