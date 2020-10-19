sourceFile= open('../src/main/java/edu/gmu/kbaral/SC2.java','r')
newFile=open('newSourceFile.java','w')

for line in sourceFile:
    print(line)
    # break
sourceFile.close()
newFile.close()
