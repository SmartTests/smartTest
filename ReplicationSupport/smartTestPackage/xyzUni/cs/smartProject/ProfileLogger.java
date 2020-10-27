package edu.xyzUni.cs.smartProject;

import java.lang.reflect.Method;
import java.util.HashSet;

public class ProfileLogger {
	 static HashSet<String> methodsHit = new HashSet<String>();

	/**
	 * This method is called when a method is hit.
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
	
	
	

