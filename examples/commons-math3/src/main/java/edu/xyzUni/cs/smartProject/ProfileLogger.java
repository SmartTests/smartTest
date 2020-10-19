package edu.xyzUni.cs.smartProject;

import java.lang.reflect.Method;
import java.util.HashSet;

public class ProfileLogger {
	 static HashSet<String> methodsHit = new HashSet<String>();

	/**
	 * This method is called when a method is hit.
	 * The format for 'method' should be:
	 * java/class/name/in/InternalName.methodName(Lthe/method/descriptor;IJKL)V
	 * @param method
	 */
	public static void methodHit(String method) {
		methodsHit.add(method);
	}

	/**
	 * Return the list of methods covered since the last invocation of dump()
	 * @return
	 */
	public static HashSet<String> dump() {
		HashSet<String> ret = methodsHit;
		methodsHit = new HashSet<String>();
		return ret;
	}
	
	

	

	
}
	
	
	
/*
 * // Need to Map: Test Case -> Class -> Statement Coverage public static
 * HashMap<String, HashMap<String, IntSet>> Coverages_testCase; public static
 * Object2ObjectOpenHashMap<String, IntSet> Coverage_testCase; public static
 * String Name_testCase;
 * 
 * // Called whenever executing a line public static void addMethodLine(String
 * className, Integer line){ if (Coverage_testCase == null) { return; }
 * 
 * IntSet lines = Coverage_testCase.get(className); if (lines != null) {
 * lines.add(line); } else { lines = new IntOpenHashSet(new int[]{line});
 * Coverage_testCase.put(className, lines); } } }
 */