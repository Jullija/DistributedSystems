package sr.thrift.client;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.apache.thrift.TException;
import org.apache.thrift.async.AsyncMethodCallback;
import org.apache.thrift.transport.TTransport;

import sr.rpc.thrift.AdvancedCalculator;
import sr.rpc.thrift.Calculator;
import sr.rpc.thrift.Calculator.AsyncClient.add_call;
import sr.rpc.thrift.OperationType;

import org.apache.thrift.transport.TSocket;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TCompactProtocol;
import org.apache.thrift.protocol.TJSONProtocol;
import org.apache.thrift.protocol.TMultiplexedProtocol;
import org.apache.thrift.protocol.TProtocol;

//8. json 97 bytes TCP
//   binary 82 bytes TCP
//   compact 64 bytes TCP



public class ThriftClient 
{
	public static void main(String [] args) 
	{

		String opt = "simple"; //"simple"; //simple | multiplex | non-block | asyn | multi-thread

		String host = "127.0.0.1";

		TProtocol protocol = null;
		TTransport transport = null;
		
		Calculator.Client synCalc1 = null;
		Calculator.Client synCalc2 = null;
		AdvancedCalculator.Client synAdvCalc1 = null;

		System.out.println("Running client in the " + opt + " mode");
		try {
			if (opt.contains("simple")) 
			{
				transport = new TSocket(host, 9080);

				//protocol = new TBinaryProtocol(transport);
				//protocol = new TJSONProtocol(transport);
				protocol = new TCompactProtocol(transport);
				
				synCalc1 = new Calculator.Client(protocol);
				synAdvCalc1 = new AdvancedCalculator.Client(protocol); //wskazuje na ten sam zdalny obiekt - dlaczego?
			}
			else if(opt.contains("multiplex"))
			{
				transport = new TSocket(host, 9090);
				
				//protocol = new TBinaryProtocol(transport);
				//protocol = new TJSONProtocol(transport);
				protocol = new TCompactProtocol(transport);

				synCalc1 = new Calculator.Client(new TMultiplexedProtocol(protocol, "S1"));
				synCalc2 = new Calculator.Client(new TMultiplexedProtocol(protocol, "S2"));
				synAdvCalc1 = new AdvancedCalculator.Client(new TMultiplexedProtocol(protocol, "A1"));
			}
			
			if(transport != null) transport.open();
			
			String line = null;
			java.io.BufferedReader in = new java.io.BufferedReader(new java.io.InputStreamReader(System.in)); 
			do
			{
				try
				{
					System.out.print("==> ");
					System.out.flush();
					line = in.readLine();
					if (line == null)
					{
						break;
					}
					else if(line.equals("add1a"))
					{
						int arg1 = 44;
						int arg2 = 55;
						int res = synCalc1.add(arg1, arg2);
						System.out.println("add(" + arg1 + "," + arg2 + ") returned " + res);
					}
					else if(line.equals("add1b"))
					{
						int arg1 = 4400;
						int arg2 = 5500;
						int res = synCalc1.add(arg1, arg2);
						System.out.println("add(" + arg1 + "," + arg2 + ") returned " + res);
					}
					else if(line.equals("add2"))
					{
						int arg1 = 44;
						int arg2 = 55;
						int res = synCalc2.add(arg1, arg2);
						System.out.println("add(" + arg1 + "," + arg2 + ") returned " + res);
					}
					else if(line.equals("add3"))
					{
						int arg1 = 44;
						int arg2 = 55;
						int res = synAdvCalc1.add(arg1, arg2);
						System.out.println("add(" + arg1 + "," + arg2 + ") returned " + res);
					}
					else if(line.equals("op3a"))
					{
						double res = synAdvCalc1.op(OperationType.AVG, new HashSet<Double>(Arrays.asList(4.0, 5.0, 3.1415926)));
						System.out.println("op(AVG, (4.0,5.0,3.1415926)) returned " + res);
					}
					else if(line.equals("op3b"))
					{
						double res = synAdvCalc1.op(OperationType.AVG, new HashSet<Double>());
						System.out.println("op(AVG, ()) returned " + res);
					}
					else if (line.equals("x"))
					{
						// Nothing to do
					}
					else if(line.startsWith("median")) {
						String[] parts = line.split(" ");
						ArrayList<Double> numbers = new ArrayList<>();
						for (int i = 1; i < parts.length; i++) {
							numbers.add(Double.parseDouble(parts[i]));
						}
						double result = synAdvCalc1.median(numbers);
						System.out.println(result);
					}
					else
					{
						System.out.println("???");
					}
				}
				catch (Exception ex)
				{
					System.err.println(ex);
				}
			}
			while (!line.equals("x"));
			
			transport.close();
			
		} catch (TException ex) {
			ex.printStackTrace();
		} 
	}
}

class AddMethodCallback implements AsyncMethodCallback<Integer> 
{

	@Override
	public void onError(Exception e) {
		System.out.println("Error : ");
		e.printStackTrace();
	}

	@Override
	public void onComplete(Integer arg0) {
		System.out.println("Result (callback): " + arg0.intValue());
	}
}
