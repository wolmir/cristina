This is a Python application that tranforms a set of source files
into a set of more reusable classes.

Developed as part of the author's graduation paper.

Known Bugs:
Bug 01 (fixed) - AstClassWrraper extracts instance variables from methods only.
                 We need to extract variables from the class body scope and the
                 __init__ method as well.
Bug 04 (fixed) - ClassNodeFinder is ignoring inner classes.
Bug 05 (fixed) - AstClassWrapper is ignoring methods with the same name.
Bug 06 - MethodMatrix has no set_metrics.
