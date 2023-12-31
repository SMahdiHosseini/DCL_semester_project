package bftsmart.tests.util;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * @author robin
 */
public class ProcessExecutor extends Thread {
	private final String workingDirectory;
	private final String command;
	private final boolean printOutputStream;
	private Process process;
	private ErrorPrinter errorPrinter;

	public ProcessExecutor(String workingDirectory, String command, boolean printOutputStream) {
		this.workingDirectory = workingDirectory;
		this.command = command;
		this.printOutputStream = printOutputStream;
	}

	@Override
	public void run() {
		try {
			process = Runtime.getRuntime().exec(command, null, new File(workingDirectory));
			errorPrinter = new ErrorPrinter(process.getErrorStream());
			errorPrinter.start();
			BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
			String line;
			while ((line = in.readLine()) != null) {
				if (printOutputStream)
					System.out.println(line);
				if (line.contains("Exiting BenchmarkController") || line.contains("Exiting Worker"))
					break;
			}
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			destroyProcess();
		}
	}

	private void destroyProcess() {
		if (process != null)
			process.destroy();
		if (errorPrinter != null) {
			errorPrinter.interrupt();
		}
	}

	@Override
	public void interrupt() {
		destroyProcess();
		super.interrupt();
	}
}
