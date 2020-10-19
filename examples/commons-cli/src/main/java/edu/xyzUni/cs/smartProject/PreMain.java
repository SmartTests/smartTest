package edu.xyzUni.cs.smartProject;

import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;



public class PreMain {
public static void premain(String args, Instrumentation inst) {
	System.out.println("PREMAIN TRANSFORMER CALLED!!!!!!!!!!!!!!!!");

		/*
		 * JUnitCore runner = new JUnitCore(); runner.addListener(new TestListener());
		 * runner.run(MethodTraceIT.class);
		 */
		inst.addTransformer(new ClassFileTransformer() {

			@Override
			public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
				//For our purposes, skip java* and sun* internal methods
				if (className.startsWith("java") || className.startsWith("sun"))
					return null;
				ClassReader cr = new ClassReader(classfileBuffer);
				ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_FRAMES);
				try {
					ClassVisitor cv = new MethodProfilingCV(cw);
					cr.accept(cv, 0);
					return cw.toByteArray();
				} catch (Throwable t) {
					//If you don't catch exceptions yourself, JVM will silently squash them
					t.printStackTrace();
					return null;
				}
			}
		});

	}
}


