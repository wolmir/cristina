This is a Python application that tranforms a set of source files
into a set of more reusable classes.

Developed as part of the author's graduation paper.

Known Bugs:
#01 - AstClassWrraper extracts instance variables from methods only. We need to
	  extract variables from the class body scope and the __init__ method as well.