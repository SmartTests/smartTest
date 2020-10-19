package edu.xyzUni.cs.smartProject;

import java.nio.file.FileAlreadyExistsException;
import java.util.*;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

//SET testPackageName, showLog, removeRepeatedEdges and noLoops before use
public class StatementCoverageLogger {

	static LinkedHashMap<String, LinkedHashMap<String, LinkedHashMap<String, String>>> coverageMap = new LinkedHashMap<String, LinkedHashMap<String, LinkedHashMap<String, String>>>();
	static LinkedHashMap<String, LinkedHashMap<String, LinkedHashMap<String, List<String>>>> edgeCoverageMap = new LinkedHashMap<String, LinkedHashMap<String, LinkedHashMap<String, List<String>>>>();

	static TreeSet<String> testMethods = new TreeSet<String>();

	static String testPackageName = "org.apache.commons.cli".replace(".", "/");
//	static String testPackageName = "org.apache.commons.math3.analysis.function".replace(".", "/");
//	static String testPackageName = "org.apache.commons.math3.distribution".replace(".", "/");
	static Set<String> sourceClassBeingTracked = new HashSet<String>();

	static Map<String, List<String>> storedPath = new HashMap<String, List<String>>();
	static boolean showLog = false;
	static boolean removeRepeatedEdges = true;
	static boolean noLoops = false;

	static Map<String, String> lastEdge = new HashMap<String, String>();

	static String deleteLastEdge = "";
	static boolean clearLastEdge = false;
	static Map<String, List<String>> sourceMethodCalledFromTest = new HashMap<String, List<String>>();
	static List<String> xyz = new ArrayList<String>();
	static int previousSize;
	static Map<String, String> firstLineOfMethod = new HashMap<String, String>();

	static {
		Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {

			@Override
			public void run() {
				try {
					dump();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				//System.out.println("EDGE COVERAGE MAP" + edgeCoverageMap.toString());
			}
		}));
	}

	public static void dump() throws IOException {
		// if (StatementCoverageLogger.showLog) {
		//		System.out.println("EDGE COVERAGE MAP" + edgeCoverageMap.toString());

		// }

		for (String sourceToBeTracked : sourceClassBeingTracked) {
			String info = "";

			if (noLoops) {
				for (String value : testMethods) {
					String statementInfo = coverageMap.get(value).toString();
					if (statementInfo.contains("={")) { // to check if test method called any source method
						if (statementInfo.contains(sourceToBeTracked)) {
							String[] coverageDetails = statementInfo.split("=\\{", 0);
							// String sourceTracked = coverageDetails[0];
							statementInfo = coverageDetails[1].replace("}}", "").replace(", ", ";");
							statementInfo = value + " : " + statementInfo + "\n";
							info += statementInfo;
						}
					}

				}
			}
			if (removeRepeatedEdges) {
				for (String value : testMethods) {
					String statementInfo = edgeCoverageMap.get(value).toString();
					if (statementInfo.contains("={")) { // to check if test method called any source method
						if (statementInfo.contains(sourceToBeTracked)) { // if relevant source
							String[] coverageDetails = statementInfo.split("=\\{", 0);
							// String sourceTracked = coverageDetails[0];
							statementInfo = coverageDetails[1].replace("}}", "").replace("], ", "];;").replace("\n, ",
									"\n");
							statementInfo = value + " : " + statementInfo + "\n";
							info += statementInfo;
						}
					}

				}
			}

			String coverageContentToWrite = info;
			String currentDirectory = System.getProperty("user.dir");
			String[] sourceNameExtractor = sourceToBeTracked.split("/");
			String sourceFileName = sourceNameExtractor[sourceNameExtractor.length - 1];
			String txtFileName = currentDirectory + "/output/" + sourceFileName + "-StatementsCovered.txt";

			Path path = Paths.get(txtFileName); // Output saved here

			if (!Files.exists(path)) {
				try {
					Files.createDirectories(path.getParent());
				} catch (IOException e) {
					// fail to create directory
					e.printStackTrace();
				}
			}

			try {
				Files.createFile(path);
			} catch (FileAlreadyExistsException e) {
				System.err.println("Exisiting file" + e.getMessage() + " was overwritten ");
			}

			Files.write(path, coverageContentToWrite.getBytes());

		}

	}

	public static void addMethodHit(String callingTest, String classOfMethod) {

		// if (StatementCoverageLogger.showLog) {

		// System.out.println("ADD METHOD HIT!!!!!!!!!!!!!!!!!!!!" + coverageMap);
		//			System.out.println(callingTest + "-----CALLING TEST---------FROM-------"+classOfMethod);

		// }
		if (!callingTest.contains("access")) { // methods name access for class calls
			if (noLoops) { // to avoid recurrent loops USE: for primepath tracking
				LinkedHashMap<String, LinkedHashMap<String, String>> classAndMethodMap = new LinkedHashMap<String, LinkedHashMap<String, String>>();
				LinkedHashMap<String, String> methodAndLineMap = new LinkedHashMap<String, String>();

				// if the call is from test, add to coverageMap's outer map
				if (classOfMethod.startsWith(testPackageName) && classOfMethod.contains("Test")) {
					coverageMap.put("\n" + callingTest, classAndMethodMap); // \n is there to format output in txt file

				} else {// add source method to the last testmethod added to the coverageMap
					String testMethodName = (String) coverageMap.keySet().toArray()[coverageMap.size() - 1];
					testMethods.add(testMethodName);
					classAndMethodMap = coverageMap.get(testMethodName);
					if (classOfMethod.contains("$")) { // some package comes with $1, $2
						classOfMethod = classOfMethod.split("\\$")[0];

					}
					if (callingTest.contains("$")) {
						callingTest = callingTest.split("\\$")[0];
					}
					if (classAndMethodMap.containsKey(classOfMethod)) {
						methodAndLineMap = classAndMethodMap.get(classOfMethod);
						if (!methodAndLineMap.containsKey(callingTest)) {
							methodAndLineMap.put(callingTest, null);
							classAndMethodMap.put(classOfMethod, methodAndLineMap);
						}
					} else {
						methodAndLineMap.put(callingTest, null);

						classAndMethodMap.put(classOfMethod, methodAndLineMap);
					}
					coverageMap.put(testMethodName, classAndMethodMap);

				}
			}
			if (removeRepeatedEdges) { // to store one edge only once USE: for edge coverage tracking

				LinkedHashMap<String, LinkedHashMap<String, List<String>>> classAndMethodMap = new LinkedHashMap<String, LinkedHashMap<String, List<String>>>();
				LinkedHashMap<String, List<String>> methodAndLineMap = new LinkedHashMap<String, List<String>>();

				// if the call is from test, add to coverageMap's outer map
				if (classOfMethod.startsWith(testPackageName) && classOfMethod.contains("Test")) {
					if (callingTest.contains("(")) {
						callingTest = callingTest.split("\\(")[0];
					}
					edgeCoverageMap.put("\n" + callingTest, classAndMethodMap); // \n is there to format output in txt
					// file

				} else {// add source method to the last testmethod added to the coverageMap
					String testMethodName = (String) edgeCoverageMap.keySet().toArray()[edgeCoverageMap.size() - 1];
					testMethods.add(testMethodName);
					classAndMethodMap = edgeCoverageMap.get(testMethodName);
					if (classOfMethod.contains("$")) { // some package comes with $1, $2
						classOfMethod = classOfMethod.split("\\$")[0];

					}
					if (callingTest.contains("$")) {
						callingTest = callingTest.split("\\$")[0];
					}
					if (classAndMethodMap.containsKey(classOfMethod)) {
						methodAndLineMap = classAndMethodMap.get(classOfMethod);
						if (!methodAndLineMap.containsKey(callingTest)) {
							methodAndLineMap.put(callingTest, null);
							classAndMethodMap.put(classOfMethod, methodAndLineMap);
						}
					} else {
						methodAndLineMap.put(callingTest, null);

						classAndMethodMap.put(classOfMethod, methodAndLineMap);
					}
					edgeCoverageMap.put(testMethodName, classAndMethodMap);

				}
			}
			if (StatementCoverageLogger.showLog) {

				System.out.println("MEHTOD    FINAL!!!!!!!!!!!!!!!!!!!!" + coverageMap);
			}
		}

	}

	public static void xyzT(String callingTests, String name) {

		clearLastEdge = true;

	}

	public static void xyzF(String callingTests, String name) {

		clearLastEdge = false;

	}

	public static void addLine(String sourceMethodHit, Integer line) {

		//		if (StatementCoverageLogger.showLog) {
		//			System.out.println("Current source class" + StatementCoverageLogger.sourceClassBeingTracked);
		//			System.out.println("=================ADD LINE!!!!!!!!!!!!!!!!");
		//			System.out.println(sourceMethodHit + "-----SRC METHOD-------------");
//		if(sourceMethodHit.contains("<init>"))
//		System.out.println(line + "----------LINE--------" + sourceMethodHit + "------------");
		//		}
		if (!sourceMethodHit.contains("access")) {

			if (noLoops) { // for Primepath tracking
				String callingTest = (String) coverageMap.keySet().toArray()[coverageMap.size() - 1];
				LinkedHashMap<String, LinkedHashMap<String, String>> classAndWithinMap = new LinkedHashMap<String, LinkedHashMap<String, String>>();
				LinkedHashMap<String, String> methodAndLineMap = new LinkedHashMap<String, String>();

				classAndWithinMap = coverageMap.get(callingTest);
				if (classAndWithinMap.isEmpty()) {
					classAndWithinMap.put(testPackageName, methodAndLineMap);
				} else {
					String classHit = (String) classAndWithinMap.keySet().toArray()[classAndWithinMap.size() - 1];

					methodAndLineMap = classAndWithinMap.get(classHit);
				}
				if (methodAndLineMap.get(sourceMethodHit) == null) { // if the source method isn't present in the map
					Integer previousLine = line - 1;

					String linesExecuted = previousLine.toString() + "," + line.toString(); // because call starts from
					// first line inside method
					List<String> tempList = new ArrayList<String>();

					tempList.add(previousLine.toString());
					tempList.add(line.toString());
					storedPath.put(sourceMethodHit, tempList);
					methodAndLineMap.put(sourceMethodHit, linesExecuted);

				} else { // if sourceMethod already added, append new line but avoid any recurring loops

					// String newStringOfStmts = "";
					// String oldStringOfStmts = methodAndLineMap.get(sourceMethodHit);
					String newNodeToBeAdded = line.toString();

					methodAndLineMap = makePathsLoopLess(sourceMethodHit, storedPath, newNodeToBeAdded,
							methodAndLineMap);

				}
			}
			if (removeRepeatedEdges) { // for edge coverage tracking
				String callingTest = (String) edgeCoverageMap.keySet().toArray()[edgeCoverageMap.size() - 1];
				String lastNode = "";
				Integer previousLine = line - 1; // find previous line to account for the line with method name

				LinkedHashMap<String, LinkedHashMap<String, List<String>>> classAndWithinMap = new LinkedHashMap<String, LinkedHashMap<String, List<String>>>();
				LinkedHashMap<String, List<String>> methodAndLineMap = new LinkedHashMap<String, List<String>>();

				classAndWithinMap = edgeCoverageMap.get(callingTest);
				if (classAndWithinMap.isEmpty()) {
					classAndWithinMap.put(testPackageName, methodAndLineMap);
				} else {
					String classHit = (String) classAndWithinMap.keySet().toArray()[classAndWithinMap.size() - 1];

					methodAndLineMap = classAndWithinMap.get(classHit);
				}
				String newNodeToBeAdded = line.toString();
				String newEdge = "";
				if (methodAndLineMap.get(sourceMethodHit) == null) {// if the source
					// method isn't present in the map

					if (clearLastEdge) { // new call from test method so reset last Edges tracker
						lastEdge.clear();
						clearLastEdge = false; // unless it's changed from visitMethodInsn, once cleared, don't clear in
						// another line

					}
					lastEdge.put(sourceMethodHit, line.toString());
					List<String> tempList = new ArrayList<String>();

					if (sourceMethodHit.contains("init") && sourceMethodHit.contains(";")) {
						newEdge = newNodeToBeAdded + "\n";
						firstLineOfMethod.put(sourceMethodHit, newNodeToBeAdded);

					} else {
						lastNode = previousLine.toString();
						newEdge = lastNode + "," + newNodeToBeAdded + "\n";
						firstLineOfMethod.put(sourceMethodHit, newNodeToBeAdded);

					}
					tempList.add(newEdge);
					methodAndLineMap.put(sourceMethodHit, tempList);

				} else { // if sourceMethod already added, append new line but avoid any recurring edges

					if (clearLastEdge) {
						lastEdge.clear();
						clearLastEdge = false; // unless it's changed from visitMethodInsn, once cleared, don't clear in
						// another line

						lastEdge.put(sourceMethodHit, newNodeToBeAdded);
						List<String> oldListOfEdges = methodAndLineMap.get(sourceMethodHit);

						if (sourceMethodHit.contains("init") && sourceMethodHit.contains(";")) {
							newEdge = newNodeToBeAdded + "\n";

						}

						else {
							lastNode = previousLine.toString();
							newEdge = lastNode + "," + newNodeToBeAdded + "\n";

						}
						if (!oldListOfEdges.contains(newEdge)) {
							oldListOfEdges.add(newEdge);
							methodAndLineMap.put(sourceMethodHit, oldListOfEdges);

						}

					} else {

						lastNode = lastEdge.get(sourceMethodHit);
						String firstNode = firstLineOfMethod.get(sourceMethodHit);

						List<String> oldListOfEdges = methodAndLineMap.get(sourceMethodHit);

						if (lastNode == null) {
							if (sourceMethodHit.contains("init") && sourceMethodHit.contains(";")) {
								newEdge = newNodeToBeAdded + "\n";
							} else {
								lastNode = previousLine.toString();
								newEdge = lastNode + "," + newNodeToBeAdded + "\n";// }

							}
						} else {

							if (!newNodeToBeAdded.equals(firstNode)) { // to avoid loops when call isn't from test

								if (sourceMethodHit.contains("init") && sourceMethodHit.contains(";")) {
									int found = 0;
									for (int i = 0; i < oldListOfEdges.size(); i++) {
										String edge = oldListOfEdges.get(i);

										if (!edge.contains(",")) {
											lastNode = edge.trim();
											found = i;
										}

									}

									oldListOfEdges.remove(found);
								}

								newEdge = lastNode + "," + newNodeToBeAdded + "\n";
							} else {

								newEdge = previousLine + "," + newNodeToBeAdded + "\n";
							}
						}

						lastEdge.put(sourceMethodHit, newNodeToBeAdded);
						if (!oldListOfEdges.contains(newEdge)) {
							oldListOfEdges.add(newEdge);
							methodAndLineMap.put(sourceMethodHit, oldListOfEdges);

						}

					}

				}
			}
		}

	}

	public static LinkedHashMap<String, String> makePathsLoopLess(String sourceMethodHit,
			Map<String, List<String>> storedPath, String newNodeToBeAdded,
			LinkedHashMap<String, String> methodAndLineMap) {
		List<String> tempList = new ArrayList<String>();
		String oldStringOfStmts = methodAndLineMap.get(sourceMethodHit);

		String newStringOfStmts = "";

		tempList = storedPath.get(sourceMethodHit);
		List<Integer> matchingIndices = new ArrayList<>();
		for (int i = 0; i < tempList.size(); i++) {
			String element = tempList.get(i);

			if (newNodeToBeAdded.equals(element)) {
				matchingIndices.add(i);
			}
		}

		int nodeOccurrence = matchingIndices.size();

		if (nodeOccurrence >= 2) {

			Integer lastOccurrenceIndex = matchingIndices.get(nodeOccurrence - 1);

			Integer secondLastOccurrenceIndex = matchingIndices.get(nodeOccurrence - 2);

			String firstSequence = tempList.subList(secondLastOccurrenceIndex + 1, lastOccurrenceIndex).toString();
			String secondSequence = tempList.subList(lastOccurrenceIndex + 1, tempList.size()).toString();

			if (!firstSequence.equals(secondSequence)) {
				tempList.add(newNodeToBeAdded);
				storedPath.put(sourceMethodHit, tempList);

				newStringOfStmts = oldStringOfStmts.concat("," + newNodeToBeAdded); // concat to existing string
				methodAndLineMap.put(sourceMethodHit, newStringOfStmts);
			} else {
				int sequenceSize = firstSequence.split(",").length;
				for (int i = 0; i < sequenceSize; i++) {
					tempList.remove(tempList.size() - 1);

				}
				methodAndLineMap.put(sourceMethodHit,
						tempList.toString().replace("[", "").replace("]", "").replace(", ", ","));
			}

		} else {
			tempList.add(newNodeToBeAdded);
			storedPath.put(sourceMethodHit, tempList);

			newStringOfStmts = oldStringOfStmts.concat("," + newNodeToBeAdded); // concat to existing string
			methodAndLineMap.put(sourceMethodHit, newStringOfStmts);

		}

		return methodAndLineMap;
	}

//	public static String makeLinesExecutedUnique(String linesExecuted) {
//		String str[] = linesExecuted.split(",");
//		List<String> al = new ArrayList<String>();
//		al = Arrays.asList(str);
//		Set<String> setOfLines = new TreeSet<String>(al);
//		String uniqueString = setOfLines.toString().replace("]", "").replace("[", "").replace(", ", ",").trim();
//		return uniqueString;
//
//	}

}
