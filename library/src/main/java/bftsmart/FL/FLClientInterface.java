package bftsmart.FL;

import java.io.*;

import bftsmart.tom.ServiceProxy;

public class FLClientInterface {

    private static ModelClient modelClient;

    public static boolean handleMessage(FLMessage msg, ServiceProxy serviceProxy) throws IOException, ClassNotFoundException, InterruptedException {
        while (msg.getType().equals(MessageType.WAITTHIS)){
            byte[] reply = serviceProxy.invokeUnordered(FLMessage.toBytes(new FLMessage(MessageType.CHECK, new byte[0], msg.getRound(), msg.getClientId(), 0)));
            if (reply == null){
                System.out.println(", ERROR! Exiting.");
                return true;
            }
            msg = FLMessage.fromBytes(reply);
        }
        if (msg.getType().equals(MessageType.LASTAGGPARAM)) {
            modelClient.setParameters(msg.getContent());
            return true;
        } else if (msg.getType().equals(MessageType.END)){
            return true;
        } else if (msg.getType().equals(MessageType.AGGPARAM)){
            modelClient.setParameters(msg.getContent());
        }
        return false;

    }
    private static boolean runTheRound(int round, int clientId, ServiceProxy serviceProxy) throws IOException, ClassNotFoundException, InterruptedException {
        byte[] newParams = modelClient.train();
//        System.out.println("Got HERE New Param: " + newParams);
        System.out.println("Got HERE New Param Size: " + newParams.length);
        FLMessage message = new FLMessage(MessageType.NEWPARAM, newParams, round, clientId, newParams.length);
        byte[] reply = serviceProxy.invokeOrdered(FLMessage.toBytes(message));
        if (reply == null){
            System.out.println(" ERROR! Exiting.");
            return true;
        }

        return handleMessage(FLMessage.fromBytes(reply), serviceProxy);
    }
    private static void execute(int clientId) throws IOException, ClassNotFoundException, InterruptedException {
        ServiceProxy serviceProxy = new ServiceProxy(clientId);
        boolean exit = false;
        int round = 1;
        while(!exit){
            System.out.println("Start Round " + round + " ...");
            exit = runTheRound(round, clientId, serviceProxy);
            round++;
        }
    }
    public static void main(String[] args){
        if(args.length < 1) {
            System.out.println("Usage: FL <client id> <modelClientAddress>");
        }
        modelClient = new ModelClient(args[1], Integer.parseInt(args[0]));
        try {
            execute(Integer.parseInt(args[0]));
            modelClient.terminate();
            System.out.println(" END!");
        } catch (IOException | ClassNotFoundException | InterruptedException e){
            System.out.println("Failed to send PUT request: " + e.getMessage() + "Class: " + e.getClass().toString());
        }
        return;
    }
}
