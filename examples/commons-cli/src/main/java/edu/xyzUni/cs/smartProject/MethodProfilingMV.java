package edu.xyzUni.cs.smartProject;

import static org.objectweb.asm.Opcodes.ASM5;
import static org.objectweb.asm.Opcodes.INVOKESTATIC;
import static org.objectweb.asm.Opcodes.GETSTATIC;
import static org.objectweb.asm.Opcodes.INVOKEVIRTUAL;

import org.objectweb.asm.Label;
import org.objectweb.asm.MethodVisitor;

import edu.gmu.cs.smartProject.StatementCoverageLogger;


public class MethodProfilingMV extends MethodVisitor {

	public String className; // invoked method's className
	public String methodName; // invoked method name
	public String methodDesc;
	protected int lastVisitedLine;

	protected static String callingTests = "";
	protected String classHit;
	protected String sourceMethodHit;
	protected boolean trackLineFlag = false;
	protected String initClass;

	protected String callingTestClass = "";
	protected boolean integrationTest = true;
	//protected static String isNew = "";

	public MethodProfilingMV(String className, String methodName, String methodDesc, MethodVisitor mv,
			Boolean trackLine, String callingTest, String callingTestClass) {
		super(ASM5, mv);
		this.className = className;
		this.methodName = methodName;
		this.methodDesc = methodDesc;
		this.trackLineFlag = trackLine;
		this.classHit = className;
		this.sourceMethodHit = methodName;
		MethodProfilingMV.callingTests = callingTest;
		this.callingTestClass = callingTestClass;
	}

	@Override
	public void visitMethodInsn(int opcode, String owner, String name, String desc, boolean itf) {
		// name is src function name that was called
		// owner is className of function called i.e. source class


		
		String sourceClassName = "org/apache/commons/cli";//analysis/FunctionUtils";
		String testClassName = "org/apache/commons/cli";//analysis/test/FunctionUtilsIT";
//		String sourceClassName = "org/apache/commons/math3/analysis/function";
//		String testClassName = "org/apache/commons/math3/analysis/function";
//		String sourceClassName = "org/apache/commons/math3/distribution";
//		String testClassName = "org/apache/commons/math3/distribution";
		if (!owner.startsWith("java/util") && !owner.startsWith("java/lang") && !owner.startsWith("java/io")
				&& owner.startsWith(sourceClassName) && className.startsWith(testClassName)
				|| (owner.startsWith("org/junit") && name.contains("assertThrows"))) {

			// callee class is source and caller class is test or callee class in junit5 and
			// assertThrows called then do this

			//classHit = owner;
			//sourceMethodHit = name+desc; //To track different method of same name

				

				if (callingTestClass.contains("Test") && !callingTestClass.startsWith(sourceClassName)) {

					callingTests = methodName;
				}
			
				if(callingTests.toString().contains("test")) {
					
					

					mv.visitLdcInsn(classHit);
					mv.visitLdcInsn(name);


					mv.visitMethodInsn(INVOKESTATIC, "edu/gmu/cs/smartProject/StatementCoverageLogger", "xyzT",
							"(Ljava/lang/String;Ljava/lang/String;)V", false);
					
				}
				else {
					mv.visitLdcInsn(classHit);
					mv.visitLdcInsn(name);


					mv.visitMethodInsn(INVOKESTATIC, "edu/gmu/cs/smartProject/StatementCoverageLogger", "xyzF",
							"(Ljava/lang/String;Ljava/lang/String;)V", false);
				}
				
				
			if(StatementCoverageLogger.showLog) {
				mv.visitFieldInsn(GETSTATIC, "java/lang/System", "out", "Ljava/io/PrintStream;");
				mv.visitLdcInsn("VISIT METHOD INSN FROM----- " + callingTests + "----hit---" + name 
						+ "---of---- " + classHit+"---");
				mv.visitMethodInsn(INVOKEVIRTUAL, "java/io/PrintStream", "println", "(Ljava/lang/String;)V", false);
			}
			 			 

				
			// Trackes if method was hit, WORKING
			String toSave = owner + "." + name + desc;
			mv.visitLdcInsn(toSave);
			mv.visitMethodInsn(INVOKESTATIC, "edu/gmu/cs/smartProject/ProfileLogger", "methodHit", "(Ljava/lang/String;)V",
					false);

			

		}

		super.visitMethodInsn(opcode, owner, name, desc, itf);

	}
	

	@Override
	public void visitLineNumber(int line, Label start) {
//		mv.visitFieldInsn(GETSTATIC, "java/lang/System", "out", "Ljava/io/PrintStream;");
//		mv.visitLdcInsn("VISIT LINE B4 " + callingTests + "----" +  " hit " + sourceMethodHit
//				+ " of " + classHit+"---at---"+StatementCoverageLogger.sourceClassBeingTracked+"-");
//		mv.visitMethodInsn(INVOKEVIRTUAL, "java/io/PrintStream", "println", "(Ljava/lang/String;)V", false);
		
		if (0 != line && trackLineFlag && StatementCoverageLogger.sourceClassBeingTracked.contains(classHit)) { // visit line only if it's source file.

			//lastVisitedLine = line;
			if(StatementCoverageLogger.showLog) {
			mv.visitFieldInsn(GETSTATIC, "java/lang/System", "out", "Ljava/io/PrintStream;");
			mv.visitLdcInsn("VISIT LINE INSN " + callingTests + "----" +  " hit " + sourceMethodHit
					+ " of " + classHit+"---at---"+line+"----firstcall?-"+StatementCoverageLogger.clearLastEdge);
			mv.visitMethodInsn(INVOKEVIRTUAL, "java/io/PrintStream", "println", "(Ljava/lang/String;)V", false);
			}

			mv.visitLdcInsn(sourceMethodHit);
			mv.visitLdcInsn(new Integer(line));
			mv.visitMethodInsn(INVOKESTATIC, "java/lang/Integer", "valueOf", "(I)Ljava/lang/Integer;", false);
			mv.visitMethodInsn(INVOKESTATIC, "edu/gmu/cs/smartProject/StatementCoverageLogger", "addLine",
					"(Ljava/lang/String;Ljava/lang/Integer;)V", false);

		
		}

		
		super.visitLineNumber(line, start);
	}

}
