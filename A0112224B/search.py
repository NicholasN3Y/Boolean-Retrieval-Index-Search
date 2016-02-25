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
		self.tokens = shlex.split(input)
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
        if token != 'not':
            while len(self.stack) > 0:
                op = self.stack.pop()
                if op == 'not':
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
        factory = PostfixTokenFactory()
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
	with open(queries_filename, 'r') as queries:
		for line in queries:
			postfix = parser.parse(line)
			
			


def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
	
dictionary_file_d = postings_file_p = queries_file_q = output_file_r = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o')
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

