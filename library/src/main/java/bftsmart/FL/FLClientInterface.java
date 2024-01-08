package bftsmart.FL;

import java.io.*;

import bftsmart.tom.ServiceProxy;
import java.net.Socket;

import org.graalvm.compiler.bytecode.Bytes;

public class FLClientInterface {

    private static ModelClient modelClient;
    private static Socket clientSocket;
    private static DataInputStream in;
    private static int clientId;

    public static boolean handleMessage(FLMessage msg, ServiceProxy serviceProxy) throws IOException, ClassNotFoundException, InterruptedException {
        if (msg.getType().equals(MessageType.ACK)){
            System.out.println("Got ACK Message");
            String ready = in.readUTF();
            if (ready.equals("ready")){
                // read the parameters from the file
                FileReader fr = new FileReader("params" + Integer.toString(clientId));
                BufferedReader br = new BufferedReader(fr);
                String newParam = br.readLine();
                modelClient.setParameters(newParam);
                // System.out.println("Sending new params: " + newParam);
                br.close();
            }
        }
        if (msg.getType().equals(MessageType.END)) {
            return true;
        }
        
        return false;

    }
    private static boolean runTheRound(int round, int clientId, ServiceProxy serviceProxy) throws IOException, ClassNotFoundException, InterruptedException {
        String newParams = modelClient.train();
        // System.out.println("Got New Params");

        FLMessage message = new FLMessage(MessageType.NEWPARAM, newParams, round, clientId, modelClient.datasetSize);
        byte[] reply = serviceProxy.invokeOrdered(FLMessage.toBytes(message));
        if (reply == null){
            System.out.println(" ERROR! Exiting.");
            return true;
        }

        return handleMessage(FLMessage.fromBytes(reply), serviceProxy);
    }
    private static void execute(int clientId) throws IOException, ClassNotFoundException, InterruptedException {
        ServiceProxy serviceProxy = new ServiceProxy(clientId);
        boolean start = false;
        while (start == false){
            byte[] reply = serviceProxy.invokeOrdered(FLMessage.toBytes(new FLMessage(MessageType.GETSTATUS, "", 0, clientId, "non")));
            if (reply == null){
                System.out.println(" ERROR! Exiting.");
                return;
            }
            FLMessage message = FLMessage.fromBytes(reply);
            if (message.getType().equals(MessageType.START)){
                start = true;
            }
        }


        boolean exit = false;
        int round = 1;
        while(!exit){
            System.out.println("Start Round " + round + " ...");
            exit = runTheRound(round, clientId, serviceProxy);
            System.out.println("End Round " + round + " ...");
            round++;
        }
    }
    public static void main(String[] args){
        if(args.length < 7) {
            System.out.println("Usage: FL <client id> <modelClientAddress> <clientsNum> <byzNum> <aggregator> <attack> <test>");
        }
        modelClient = new ModelClient(args[1], Integer.parseInt(args[0]), Integer.parseInt(args[2]), Integer.parseInt(args[3]), args[4], args[5], args[6]);
        clientId = Integer.parseInt(args[0]);
        System.out.println("Client " + clientId + " started!");
        try {
            clientSocket = new Socket(args[1], 6100 + Integer.parseInt(args[0]));
            in = new DataInputStream(clientSocket.getInputStream());
            execute(Integer.parseInt(args[0]));
            modelClient.terminate();
            clientSocket.close();
            in.close();
            System.out.println(" END!");
            System.exit(0);
        } catch (IOException | ClassNotFoundException | InterruptedException e){
            System.out.println("Failed to send PUT request: " + e.getMessage() + "Class: " + e.getClass().toString());
        }
        return;
    }
}
