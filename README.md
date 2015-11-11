#Cristina
This is a Python application that tranforms a set of source files
into a set of more reusable classes.

Developed as part of the author's graduation paper.

##Known Bugs:
1. (fixed) AstClassWrraper extracts instance variables from methods only.
We need to extract variables from the class body scope and the
__init__ method as well.
4. (fixed) ClassNodeFinder is ignoring inner classes.
5. (fixed) AstClassWrapper is ignoring methods with the same name.
6. (fixed) MethodMatrix has no set_metrics.
7. (fixed) Pipeline.set_data_source() is raising IndexError.
8. (fixed) The temp files used for testing are not being deleted.
9. (fixed) CrisComVariableThresholdFilter is not ignoring empty matrices.
10. (fixed) CrisMethodChainAssembler is crashing.
