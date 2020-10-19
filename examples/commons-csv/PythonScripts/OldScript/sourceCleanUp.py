import re
import sys

sourceFile = sys.argv[-1]

with open(sourceFile,'r') as source:
    text = source.readlines()
text=''.join(text)

manipulatedText = re.sub(r'\n+\s*\}','}',text)
with open (sourceFile, 'w') as source:
    source.write(manipulatedText)
