This is the README file for A0112224B's submission
contactable at a0112224@u.nus.edu

== General Notes about this assignment ==

Place your comments or requests here for Min to read.  Discuss your
architecture or experiments in general.  A paragraph or two is usually
sufficient.

The documents are index in memory, then posting list and (term with doc count) are stored
seperately in two file: postings.txt and dictionary.txt.

The postings list have skip pointers implemented. They are stored as tuples: the docid is stored
at index 0 and the skip pointer if present is stored at index 1.

The each postings list for each term are pickled individually into the postings.txt. And the position
is recorded using tell() and stored in the dictionary together with the term and doc count.

For querying, the query is postfixed using the code credited to  https://msoulier.wordpress.com/2009/08/01/dijkstras-shunting-yard-algorithm-in-python/.
Only relavant postings list are unpickled from postings.txt.

Upon merging of posting lists during AND and OR operations, I first check the length of inidvidual postings list to 
find out the short list such that certain operations such as x AND y can be optimized using the shorter list as the point of reference when incrementing\
pointers.

Upon each successful merge, the skip pointers are recomputed.

The try - except block is used to catch exceptions due to possible bug in the code, such that the program will not crash, and all queries can be tested for.
 

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py
ESSAY.txt
search.py
queries.txt
postings.txt
dictionary.txt
README.txt
output.txt - output upon running the program.


== Statement of individual work ==

Please initial one of the following statements.

** ATTENTION**
** the code relating to parsing the query into postfix notation is not my own work. **
** the code was borrowed from https://msoulier.wordpress.com/2009/08/01/dijkstras-shunting-yard-algorithm-in-python/ **
** with minimal alteration to fit the program. Duly credited in the source file *** 

[X] I, A0112224B, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

To check on the correct syntax and on how to use pickle 
http://www.tutorialspoint.com/python/
