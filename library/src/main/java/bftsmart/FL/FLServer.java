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
import java.util.concurrent.locks.ReentrantLock;

public final class FLServer extends DefaultSingleRecoverable {

    private int clientNums;
    private int numOfRounds;
    private int currentRound;
    private int sentAggParams;
    private static String aggregatedParams;
    private boolean aggregated;
    private int receivedParams;
    private int receivedParamsNext;
    private ReentrantLock lock;
    private ArrayList<String> receivedParamsNextArr;
    private ArrayList<String> receivedParamsNextDatasetSizeArr;
    private DataInputStream in;
    private DataOutputStream out;
    public FLServer(int id, int _clientNums, int _numOfRounds, String address){
        this.numOfRounds = _numOfRounds;
        this.clientNums = _clientNums;
        this.receivedParamsNext = 0;
        this.receivedParams = 0;
        this.sentAggParams = 0;
        this.currentRound = 1;
        this.aggregated = false;
        this.receivedParamsNextArr = new ArrayList<String>();
        this.receivedParamsNextDatasetSizeArr = new ArrayList<String>();
        this.lock = new ReentrantLock();
        new ServiceReplica(id, this, this);

        try {

//            ServerSocket serverSocket = new ServerSocket(6000);
            ServerSocket serverSocket = new ServerSocket(0);
            int port = serverSocket.getLocalPort();
            System.out.println("Server " + id + " Port: " + port);
            //Windows
            // Process modelProcess = Runtime.getRuntime().exec("python ../../../../Simple_FL/Server_bft.py " + address + " " + Integer.toString(port));
            //Linux
            // Process modelProcess = Runtime.getRuntime().exec("python3 ../../../../Simple_FL/Server_bft.py " + address + " " + Integer.toString(port));
            Socket socket = serverSocket.accept();
            in = new DataInputStream(socket.getInputStream());
            out = new DataOutputStream(socket.getOutputStream());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void aggregateParams() throws IOException {
        String aggregate = "AGGREGATE";
        out.writeUTF(aggregate);
        out.flush();
        System.out.println("Aggregating parameters of round " + currentRound);

        int msg_size = Integer.parseInt(in.readUTF());
        byte[] data = new byte[msg_size];
        in.read(data, 0, data.length);
        aggregatedParams = new String(data, 0, data.length);
       System.out.println("**** Aggregated of round " + currentRound);
        aggregated = true;
        if (currentRound == numOfRounds) {
            terminateTheAggregator();
        }
    }

    public void checkRoundEnd(int clientId) throws IOException {
        if (sentAggParams == clientNums){
            aggregated = false;
//            System.out.println("Round Ended by sending to client " + clientId);
            for (int i = 0; i < receivedParamsNextArr.size(); i++){
                sendParametersToAggregator(receivedParamsNextArr.get(i), receivedParamsNextDatasetSizeArr.get(i));
            }
            sentAggParams = 0;
            receivedParams = receivedParamsNext;
            receivedParamsNext = 0;
            receivedParamsNextArr = new ArrayList<String>();
            currentRound++;
        }

    }
    public FLMessage sendAggParams(int clientId) throws IOException {
        lock.lock();
        sentAggParams++;
//        System.out.println("Send Aggregated param of round " + currentRound + " to client " + clientId);
//        System.out.println("SentAggParams = " + sentAggParams);
        FLMessage msg = new FLMessage((currentRound == numOfRounds) ? MessageType.LASTAGGPARAM : MessageType.AGGPARAM, aggregatedParams, currentRound, clientId, "non");
//        FLMessage msg = new FLMessage((currentRound == numOfRounds) ? MessageType.LASTAGGPARAM : MessageType.AGGPARAM, "Hello", currentRound, clientId, "non");
        checkRoundEnd(clientId);
        lock.unlock();
        return msg;

    }
    public void terminateTheAggregator() throws IOException {
        String terminate = "TERMINATE";
        out.writeUTF(terminate);
        out.flush();
        String ack = in.readUTF();
        System.out.println("Python process terminated");
    }
    public void sendParametersToAggregator(String parameters, String datasetSize) throws IOException {
        String newParams = "NEWPARAMS";
        out.writeUTF(newParams);
        String ack = in.readUTF();
        if (ack.equals("ACK"))
            out.writeUTF(datasetSize);
        ack = in.readUTF();
        if (ack.equals("ACK"))
            out.writeUTF(String.valueOf(parameters.getBytes().length));
        ack = in.readUTF();
        if (ack.equals("ACK"))
            out.write(parameters.getBytes(), 0, parameters.getBytes().length);
        ack = in.readUTF();
        out.flush();
    }
    public FLMessage handleNewParam(FLMessage msg) throws IOException {
       System.out.println("Got new param from " + msg.getClientId() + " Curretn Round: " + currentRound + " Client round:" + msg.getRound());
        if (msg.getRound() == currentRound){
            sendParametersToAggregator(msg.getContent(), msg.getExtension());
            receivedParams++;
           System.out.println("Send Params to Aggregator by client " + msg.getClientId());
        } else {
//            System.out.println("Save Params for client " + msg.getClientId());
            receivedParamsNextArr.add(msg.getContent());
            receivedParamsNext++;
            return new FLMessage(MessageType.WAITTHIS, "", currentRound, msg.getClientId(), "non");
        }

        if ((receivedParams == clientNums) && (!aggregated)){
           System.out.println("Send Aggregate to Aggregator by client " + msg.getClientId());
            aggregateParams();
            return sendAggParams(msg.getClientId());
        } else {
            return new FLMessage(MessageType.WAITTHIS, "", currentRound, msg.getClientId(), "non");
        }
    }

    public FLMessage handleCheckMsg(FLMessage msg) throws IOException {
        if ((receivedParams == clientNums) && (aggregated)){
            return sendAggParams(msg.getClientId());
        } else {
            return new FLMessage(MessageType.WAITTHIS, "", currentRound, msg.getClientId(), "non");
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
            terminateTheAggregator();
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
            terminateTheAggregator();
            return null;

        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Invalid request received!");
            return null;
        }
    }

    public static void main(String[] args){
        if(args.length < 4) {
            System.out.println("Use: java FLServer <processId> <ClientNums> <NumOfRounds> <address>");
            System.exit(-1);
        }
        new FLServer(Integer.parseInt(args[0]), Integer.parseInt(args[1]), Integer.parseInt(args[2]), args[3]);
    }
}
