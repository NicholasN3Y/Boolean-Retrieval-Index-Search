#!/usr/bin/python
import nltk
import sys
import getopt
import os
import cPickle as pickle

''' Code below is credited to https://msoulier.wordpress.com/2009/08/01/dijkstras-shunting-yard-algorithm-in-python/ '''
class QueryParser(object):
	'''implementation of parser to have infix notation of the query to
		be changed to postfix, uses Dijkstra's Shunting-Yard Algorithm'''
	def __init__(self):
		self.tokens = []
		self.stack = []
		self.postfix = []
	
	def tokenize(self, input):
		self.tokens = input.split(" ");
		tokened = []
		for token in self.tokens:
			r_paren = False
			if token[0] == "(":
				tokened.append("(")
				token = token[1:]
			if len(token) > 0 and token[-1] == ")":
				token = token[:-1]
				r_paren = True
			tokened.append(token)
			if r_paren:
				tokened.append(")")
		self.tokens = tokened
	
	def is_operator(self, token):
		if token == "AND" or token == "OR" or token == "NOT":
			return True
	
	def manage_precedence(self, token):
		if token != 'NOT':
			while len(self.stack) > 0:
				op = self.stack.pop()
				if op == 'NOT':
					self.postfix.append(op)
				else:
					self.stack.append(op)
					break

		self.stack.append(token)

	def right_paren(self):
		found_left = False
		while len(self.stack) > 0:
			top_op = self.stack.pop()
			if top_op != "(":
				self.postfix.append(top_op)
			else:
				found_left = True
				break
		if not found_left:
			raise ParseError, "Parse error: Mismatched parens"

		if len(self.stack) > 0:
			top_op = self.stack.pop()
			if self.is_operator(top_op):
				self.postfix.append(top_op)
			else:
				self.stack.append(top_op)

	def parse(self, input):
		if len(self.tokens) > 0:
			self.__init__()
		#factory = PostfixTokenFactory()
		self.tokenize(input)
		for token in self.tokens:
			if self.is_operator(token):
				self.manage_precedence(token)
			else:
				# Look for parens.
				if token == "(":
					self.stack.append(token)
				elif token == ")":
					self.right_paren()
				else:
					self.postfix.append(token)
		while len(self.stack) > 0:
			operator = self.stack.pop()
			if operator == "(" or operator == ")":
				raise ParseError, "Parse error: mismatched parens"
			self.postfix.append(operator)
		return self.postfix
		
''' above code credited to https://msoulier.wordpress.com/2009/08/01/dijkstras-shunting-yard-algorithm-in-python/ '''
		
def loadDictionary(filename):
	dictFile = open(filename, 'r')
	term_count_pos = pickle.load(dictFile)
	dictFile.close()
	return term_count_pos

def evaluateQueries(dictionary, posting_filename, queries_filename, output_filename):
	parser = QueryParser()
	outputfile = open(output_filename, 'w')
	postingsfile = open(posting_filename, 'rb')
	with open(queries_filename, 'r') as queries:
		for line in queries:
			print line
			postfix = parser.parse(line)
			evalquery(postfix, dictionary, postingsfile, outputfile)
	outputfile.close()
	postingsfile.close()
			
def evalquery(query, dictionary, postingsfile, outputfile):
	if (len(query) > 2 ):
		opstack = []
		waitToEvaluate = True
		while len(query) >= 0:
			while(term = query.pop()):
				if term == "NOT": 
					opstack.append(term)
				elif term == "OR" or term == "AND":
					WaitToEvaluate = True
					opstack.append(term)
				else:
					#is a term 
					if waitToEvaluate:
						waitToEvaluate = False
						opstack.append(term)
					else:
						list1 = term
						list2 = -1
						Notlist1 = False
						Notlist2 = False
						term = opstack.pop()
						#pop until we get a AND or "OR"
						while (term != "AND" and  term != "OR"):
							if term == "NOT":
								if list2 == -1:
									Notlist1 = True
								else:
									Notlist2 = True
							else:
								list2 = term
							term = opstack.pop()
					
						assert(term=="AND" or term =="OR")
						assert(list1 != -1) 
						assert(list2 != -1)
						if (term == "AND"):
							intermediate_list = evalAnd(list1, Notlist1, list2, Notlist2, dictionary, postingsfile)
						elif(term == "OR")
							intermediate_list = evalOr(list1, Notlist1, list2, Notlist2, dictionary, postingsfile)
						query.append(intermediate_list)
						while (len(opstack) > 0):
							query.append(opstack.pop())
						assert(len(opstack) == 0)
						evalquery(query, dictionary, postingsfile, outputfile)
	else:
		if(len(query) == 2):
			assert(query[1] == "NOT")
			res = evalNot(query[0])
		else:
			res = query[0]
		write_result(res, outputfile)
		
def evalAnd(list1, Notlist1, list2, Notlist2, dictionary, postingsfile):
		'''get posting lists'''
		if type(list1) is str:
			list1 = dictionary.get(list1, "None")
			if (list1 == "None"):
			 	list1 == list()
			else:	
				list1 = getDataFromPostings(list1[1], postingsfile)
		if type(list2) is str:
			list2 = dictionary.get(list1, "None")
			if (list2 == "None"):
			 	list2 == list()
			else:	
				list2 = getDataFromPostings(list1[1], postingsfile)
		
		res_list = list()
		#case Not A and Not B -> Not(A or B)
		if (Notlist1 == True and Notlist2 == True):
			res_list = evalOr(list1, False, list2, False, dictionary, postingsfile)
			return evalNot(res_list)
		#case not A and B
		elif(Notlist1 == True and Notlist2 == False):
			return evalAnd(list2, Notlist2, list1, Notlist1, dictionary, postingsfile)
		
		else:
			if(Notlist1 == False and Notlist2 == False):
				#enforce list1 shorter than list2
				if (len(list1) > len(list2)):
					temp = list1
					list1 = list2
					list2 = temp
					del temp
			ptr_list1 = 0;
			ptr_list2 = 0;
			while ptr_list1 < len(ptr_list1):
				if (list1[ptr_list1][0] == list2[ptr_list2][0]):
					# case A and B
					if (Notlist2 == False):
						res_list.append(ptr_list1)
					ptr_list1++
					ptr_list2++
				elif (list1[ptr_list1][0] < list2[ptr_list2][0]):
					if (len(list1[ptr_list1]) == 2):
						init = ptr_list1
						while (list1[list1[ptr_list1][1]] <= list[ptr_list2]):
							ptr_list1 = list1[ptr_list1][1]
						# case A and not B
						if (Notlist2 == True):
							res_list.append(list1[init:ptr_list1])
					else:
						#case A and not B
						if (Notlist2 == True):
							res_list.append(list1[ptr_list1])
							ptr_list1++
				elif(list1[ptr_list1][0] > list2[ptr_list2][0]):	
					if (len(list2[ptr_list2]) == 2):
						init = ptr_list2
						while (list2[list2[ptr_list2][1]] <= list[ptr_list1]):
							ptr_list2 = list2[ptr_list2][1]
					else:
						ptr_list2++
				
			return skipify(res_list)
					
def evalOr(list1, Notlist1, list2, Notlist2, dictionary, postingsfile):
		'''get posting lists'''
		if type(list1) is str:
			list1 = dictionary.get(list1, "None")
			if (list1 == "None"):
			 	list1 == list()
			else:	
				list1 = getDataFromPostings(list1[1], postingsfile)
		if type(list2) is str:
			list2 = dictionary.get(list1, "None")
			if (list2 == "None"):
			 	list2 == list()
			else:	
				list2 = getDataFromPostings(list1[1], postingsfile)

		#case A or B
		if (Notlist1 == False and Notlist2 == False):
			if (len(list1) == 0):
				return list2;
			elif (len(list2) == 0):
				return list1
			
			#enforce that list 2 be shorter than list1
			if (len(list1) < len(list2)):
				temp = list1
				list1 = list2
				list2 = temp
				del temp
			
			ptr_list1 = 0
			ptr_list2 = 0
			res_list = list()
			while (ptr_list2 < len(list2) and ptr_list1 < len(list1)): 
				if (list1[ptr_list1][0] == list2[ptr_list2][0]):
					res_list.append(list1[ptr_list1])
					ptr_list1++
					ptr_list2++
				elif(list1[ptr_list1][0] < list2[ptr_list2][0]):
					if (len(list1[ptr_list1]) == 2):
						init = ptr_list1
						while (list1[list1[ptr_list1][1]] <= list[ptr_list2]):
							ptr_list1 = list1[ptr_list1][1]
						res_list.append(list1[init:ptr_list1])
					else:
						res_list.append(list1[ptr_list1])
						ptr_list1++
				elif(list1[ptr_list1][0] > list2[ptr_list2][0]):	
					if (len(list2[ptr_list2]) == 2):
						init = ptr_list2
						while (list2[list2[ptr_list2][1]] <= list[ptr_list1]):
							ptr_list2 = list2[ptr_list2][1]
						res_list.append(list2[init:ptr_list2])
					else:
						res_list.append(list2[ptr_list2])
						ptr_list2++
			#append remainder to the list
			if (ptr_list1 < len(list1)):
				res_list.append(list1[ptr_list1:len(list1)])
			elif (ptr_list2 < len(list2):
				res_list.append(list2[ptr_list2:len(list2)])
			return skipify(res_list)
			
		#case not A or not B -> not (A and B)
		elif (Notlist1 == True and Notlist2 == True):
			res_list = evalAnd(list1, False, list2, False, dictionary, postingsfile)
			return evalNot(res_list, dictionary, postingsfile)
		
		#case not a or b
		elif (Notlist1 == True and Notlist2 == False):
			list1 = evalNot(list1, dictionary, postingsfile)
			Notlist1 == False
			return evalOr(list1, Notlist1, list2, Notlist2, dictionary, postingsfile)
			
		#case not b or a  (interchange a and b)
		elif (Notlist1 != False and Notlist2 != True):
			return evalOr(list2, Notlist2, list1, Notlist1, dictionary, postingsfile)		




def evalNot(list, dictionary, postingsfile):
	doclist = getDataFromPostings(dictionary['LIST_OF_DOC'][1], postingsfile)
	if type(list) is str:
		list = dictionary.get(list, "None")
		if (list == "None"):
			#hence the term is not present in any of the documents, so we take all documents
			return doclist
		else:	
			list = getDataFromPostings(list[1], postingsfile)

	#negate list from doclist to get NOT list
	ptr_doclist = 0
	ptr_list = 0
	res_list = list()
	
	while (ptr_list < len(list)):
		
		if (list[ptr_list][0] > doclist[ptr_doclist][0]):
			
			#if has skip ptr
			if (len(doclist[ptr_doclist]) == 2):
				init = ptr_doclist
				while (doclist[doclist[ptr_doclist][1]] <= list[ptr_list]):
					 ptr_doclist = doclist[ptr_doclist][1]
				res_list.append(doclist[init:ptr_doclist])
			else:
				res_list.append(doclist[ptr_doclist])
				ptr_doclist++

		elif(list[ptr_list][0] == doclist[ptr_doclist][0]):
			#advance pointers by 1
			ptr_doclist++
			ptr_list++			
		
		else:
			assert (False), "Should be impossible to enter such state" 		
	
	#append the rest of doclist to the res
	res_list.append(doclist[ptr_doclist:len(doclist)])
	
	return skipify(res_list) 
	
def skipify(alist):
	#clear rubbish skip data due to merge 
	for item in alist:
		assert(type(item) is tuple), "it is not a tuple!"
		if len(item) == 2:
			item = (item[0], )
			
	post_length = len(alist)
	val = int(math.floor(math.sqrt(post_length)))	
	#add skip pointer
	for i in range (0, post_length, val):
		if (i + val < post_length):
			postings[i] = (postings[i][0], i+val)
		elif (i != post_length-1):
			postings[i] = (postings[i][0], post_length - 1)

def getDataFromPostings(position, postingsfile):
	postingsfile.seek(position, 0)
	return pickle.load(postingsfile)
			
def write_result(resultlist, outputfile):
	resultstring = ""
	for item in resultlist:
		resultstring.append(item[0])
		resultstring.append(" ");
	resultstring = resultstring[0:len(resultstring)-1]
	outputfile.write(resultstring+"\n")
		 				
def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
	
dictionary_file_d = postings_file_p = queries_file_q = output_file_r = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-d':
        dictionary_file_d = a
    elif o == '-p':
        postings_file_p = a
    elif o == '-q':
        queries_file_q = a
    elif o == '-o':
        output_file_r = a	
    else:
        assert False, "unhandled option"
if dictionary_file_d == None or postings_file_p == None or queries_file_q == None or output_file_r == None:
    usage()
    sys.exit(2)
	
termDictionary = loadDictionary(dictionary_file_d)
evaluateQueries(termDictionary, postings_file_p, queries_file_q, output_file_r)

