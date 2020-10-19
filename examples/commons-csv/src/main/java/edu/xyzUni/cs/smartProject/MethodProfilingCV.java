package edu.xyzUni.cs.smartProject;

import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

import edu.xyzUni.cs.smartProject.MethodProfilingMV;
import edu.xyzUni.cs.smartProject.StatementCoverageLogger;

import static org.objectweb.asm.Opcodes.*;

import java.util.HashSet;
import java.util.Set;




public class MethodProfilingCV extends ClassVisitor {
	
	//set to False to run tests without IT end
	private static boolean integrationTest = true; 


	public MethodProfilingCV(ClassVisitor cv) {
		super(Opcodes.ASM5, cv);
	}

	String className;
	protected String callingTest = "";
	protected String callingTestClass = "";
	protected String packageName = "org/apache/commons/csv";
//	protected String packageName = "org/apache/commons/math3/analysis/function";
//	protected String packageName = "org/apache/commons/math3/analysis/integration";
//	protected String packageName = "org/apache/commons/math3/distribution";
	
	@Override
	public void visit(int version, int access, String name, String signature, String superName, String[] interfaces) {
		super.visit(version, access, name, signature, superName, interfaces);

		if (name.contains("$")) { // some package comes with $1, $2
			name = name.split("\\$")[0];

		}

		this.className = name;
	}

	@Override
	public MethodVisitor visitMethod(int access, String name, String desc, String signature, String[] exceptions) {
		
		MethodVisitor mv = super.visitMethod(access, name, desc, signature, exceptions);
		Boolean trackLine = false;
		Set<String> currentSourceClass = new HashSet<String>(); 
		  				
		if(className.startsWith(packageName)  ) {
			/*
			 * if(StatementCoverageLogger.showLog) { mv.visitFieldInsn(GETSTATIC,
			 * "java/lang/System", "out", "Ljava/io/PrintStream;");
			 * mv.visitLdcInsn(access+"------STARTED FROM ------------<------"+name+desc+
			 * signature+"---of---"+className+"----"+StatementCoverageLogger.
			 * sourceClassBeingTracked); mv.visitMethodInsn(INVOKEVIRTUAL,
			 * "java/io/PrintStream", "println", "(Ljava/lang/String;)V", false); }
			 */
			if(className.contains("Test")) {
				StatementCoverageLogger.sourceClassBeingTracked.add(className.replace("TestIT",""));
				

			}

				currentSourceClass = StatementCoverageLogger.sourceClassBeingTracked;

			
			if (className.contains("Test")) { // test method is calling

				callingTest = name;
				callingTestClass = className;
			}

			if (!className.contains("Test") && currentSourceClass.contains(className)) {//
				//trackLines  for source class only
//				if(StatementCoverageLogger.showLog) {
//				mv.visitFieldInsn(GETSTATIC, "java/lang/System", "out", "Ljava/io/PrintStream;");
//				mv.visitLdcInsn("TRACK LINE SETUP" + className + "----" + name +"--------"+trackLine);
//				mv.visitMethodInsn(INVOKEVIRTUAL, "java/io/PrintStream", "println", "(Ljava/lang/String;)V", false);
//				}
				trackLine = true;
			
			}

			if (currentSourceClass.contains(className) || className.contains("Test")) {
				
				String methodAndParam = name+desc;
				mv.visitLdcInsn(methodAndParam);
				mv.visitLdcInsn(className);
				mv.visitMethodInsn(INVOKESTATIC, "edu/gmu/cs/smartProject/StatementCoverageLogger", "addMethodHit",
						"(Ljava/lang/String;Ljava/lang/String;)V", false);
			  
				mv = new MethodProfilingMV(className, methodAndParam, desc, mv, trackLine, callingTest, callingTestClass);
			  }
			 
		}
			
		
		return mv;
	}

}
