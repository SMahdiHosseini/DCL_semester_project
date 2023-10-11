package bftsmart.FL;

import bftsmart.demo.counter.CounterServer;
import bftsmart.tom.MessageContext;
import bftsmart.tom.ServiceReplica;
import bftsmart.tom.server.defaultservices.DefaultSingleRecoverable;

import javax.xml.crypto.Data;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;

public final class FLServer extends DefaultSingleRecoverable {

    private int clientNums;
    private int numOfRounds;
    private int currentRound;
    private int sentAggParams;
    private byte[] aggregatedParams;
    private int receivedParams;
    private int receivedParamsNext;
    private int port;
//    private DataInputStream in;
//    private DataOutputStream out;
    public FLServer(int id, int _clientNums, int _numOfRounds, String address){
        this.numOfRounds = _numOfRounds;
        this.clientNums = _clientNums;
        this.receivedParamsNext = 0;
        this.receivedParams = 0;
        this.sentAggParams = 0;
        this.currentRound = 1;
        new ServiceReplica(id, this, this);

//        try {
//
//            ServerSocket serverSocket = new ServerSocket(6000);
////            ServerSocket serverSocket = new ServerSocket(0);
//            this.port = serverSocket.getLocalPort();
////            System.out.println("Server " + id + " Port: " + this.port);
////            Process modelProcess = Runtime.getRuntime().exec("python ../../../../Simple_FL/Server_bft.py " + Integer.toString(id) + " " + address + " " + Integer.toString(this.port));
////            DataInputStream err = new DataInputStream(modelProcess.getErrorStream());
////            String s;
////            while((s = err.readLine()) != null)
////                System.out.println("FF: " + s);
//            Socket socket = serverSocket.accept();
//            in = new DataInputStream(socket.getInputStream());
//            out = new DataOutputStream(socket.getOutputStream());
//        } catch (IOException e) {
//            throw new RuntimeException(e);
//        }
    }

    public void aggregateParams() throws IOException {
        //TODO
        aggregatedParams = "NEW PARAM: SALAM, HI, BLABLABLA".getBytes();
//        if (currentRound == numOfRounds){
//            String terminate = "TERMINATE";
//            out.writeUTF(terminate);
//            out.flush();
//            String ack = in.readUTF();
//            if (ack.equals("ACK"))
//                System.out.println("Python process terminated");
//        }
    }

    public void checkRoundEnd(){
        if (sentAggParams == clientNums){
            sentAggParams = 0;
            receivedParamsNext = receivedParams;
            receivedParams = 0;
            currentRound++;
        }

    }
    public FLMessage sendAggParams(int clientId){
        sentAggParams++;
        FLMessage msg = new FLMessage((currentRound == numOfRounds) ? MessageType.LASTAGGPARAM : MessageType.AGGPARAM, aggregatedParams, currentRound, clientId, aggregatedParams.length);
        checkRoundEnd();
        return msg;

    }
    public void sendParameters(byte[] parameters) throws IOException {
        String newParams = "NEWPARAMS";
//        out.writeUTF(newParams);
//        String ack = in.readUTF();
//        if (ack.equals("ACK"))
//            out.writeUTF(String.valueOf(parameters.length));
//        ack = in.readUTF();
//        if (ack.equals("ACK"))
//            out.write(parameters, 0, parameters.length);
//        ack = in.readUTF();
//        out.flush();
    }
    public FLMessage handleNewParam(FLMessage msg) throws IOException {
        if (msg.getRound() == currentRound){
            //TODO: send to .py
            sendParameters(msg.getContent());
            System.out.println("newParam:" + new String(msg.getContent(), 0, msg.getContentSize()));
            receivedParams++;
        } else {
            //TODO: send to .py
            receivedParamsNext++;
        }

        if (receivedParams == clientNums){
            aggregateParams();
            return sendAggParams(msg.getClientId());
        } else {
            return new FLMessage(MessageType.WAITTHIS, new byte[0], currentRound, msg.getClientId(), 0);
        }
    }

    public FLMessage handleCheckMsg(FLMessage msg){
        if (receivedParams == clientNums){
            return sendAggParams(msg.getClientId());
        } else {
            return new FLMessage(MessageType.WAITTHIS, new byte[0], currentRound, msg.getClientId(), 0);
        }
    }
    @Override
    public void installSnapshot(byte[] state) {

    }

    @Override
    public byte[] getSnapshot() {
        return new byte[0];
    }

    @Override
    public byte[] appExecuteOrdered(byte[] command, MessageContext msgCtx) {
        try {
            FLMessage message = FLMessage.fromBytes(command);
            if (message.getType().equals(MessageType.NEWPARAM)){
                return FLMessage.toBytes(handleNewParam(message));
            } else if (message.getType().equals(MessageType.CHECK)){
                return FLMessage.toBytes(handleCheckMsg(message));
            }
            System.err.println("Not valid message type!");
            return null;

        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Invalid request received!" + e.getMessage());
            return null;
        }
    }

    @Override
    public byte[] appExecuteUnordered(byte[] command, MessageContext msgCtx) {
        try {
            FLMessage message = FLMessage.fromBytes(command);
            if (message.getType().equals(MessageType.CHECK)){
                return FLMessage.toBytes(handleCheckMsg(message));
            }
            System.err.println("Not valid message type!");
            return null;

        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Invalid request received!");
            return null;
        }
    }

    public static void main(String[] args){
        if(args.length < 3) {
            System.out.println("Use: java FLServer <processId> <ClientNums> <NumOfRounds>");
            System.exit(-1);
        }
        new FLServer(Integer.parseInt(args[0]), Integer.parseInt(args[1]), Integer.parseInt(args[2]), args[3]);
    }
}
