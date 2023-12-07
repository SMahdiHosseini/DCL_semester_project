package bftsmart.FL;

import bftsmart.tom.MessageContext;
import bftsmart.tom.ServiceReplica;
import bftsmart.tom.server.defaultservices.DefaultSingleRecoverable;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.concurrent.locks.ReentrantLock;

public final class FLServer extends DefaultSingleRecoverable {

    private int clientNums;
    private int numOfRounds;
    private int currentRound;
    private HashMap<Integer, String> aggregatedParams;
    private int receivedParams;
    private int byzNums;
    private ReentrantLock lock;
    private DataInputStream in;
    private DataOutputStream out;
    public FLServer(int id, int _clientNums, int _numOfRounds, String address, int byzNums, String aggregatorName, String attackName, String _test){
        this.numOfRounds = _numOfRounds;
        this.clientNums = _clientNums;
        this.receivedParams = 0;
        this.currentRound = 1;
        this.byzNums = byzNums;
        this.lock = new ReentrantLock();
        this.aggregatedParams = new HashMap<Integer, String>();
        new ServiceReplica(id, this, this);

        try {

//            ServerSocket serverSocket = new ServerSocket(6000);
            ServerSocket serverSocket = new ServerSocket(0);
            int port = serverSocket.getLocalPort();
            System.out.println("Server " + id + " Port: " + port);
            //Windows
            //  Process modelProcess = Runtime.getRuntime().exec("python ../../../../main/Server_bft.py " + address + " " + Integer.toString(port));
            //Linux
            Process modelProcess = Runtime.getRuntime().exec("python3 ../../../../main/Server_bft.py " + address + " " + Integer.toString(port) + " " + Integer.toString(id) + " " + Integer.toString(_clientNums) + " " + Integer.toString(byzNums) + " " + aggregatorName + " " + attackName + " " + _test);
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
        in.readFully(data);
        aggregatedParams.put(currentRound, new String(data, 0, data.length));
        System.out.println("**** Aggregated of round " + currentRound);
        currentRound++;
        receivedParams = 0;
        if (currentRound > numOfRounds) {
            terminateTheAggregator();
        }
    }

//     public void checkRoundEnd(int clientId) throws IOException {
//         if (sentAggParams == clientNums){
//             aggregated = false;
// //            System.out.println("Round Ended by sending to client " + clientId);
//             for (int i = 0; i < receivedParamsNextArr.size(); i++){
//                 sendParametersToAggregator(receivedParamsNextArr.get(i), receivedParamsNextDatasetSizeArr.get(i));
//             }
//             sentAggParams = 0;
//             receivedParams = receivedParamsNext;
//             receivedParamsNext = 0;
//             receivedParamsNextArr = new ArrayList<String>();
//             currentRound++;
//         }
//     }

    public FLMessage sendAggParams(int clientId, int round) throws IOException {
        lock.lock();
//        System.out.println("Send Aggregated param of round " + currentRound + " to client " + clientId);
//        System.out.println("SentAggParams = " + sentAggParams);
        FLMessage msg = new FLMessage((round == numOfRounds) ? MessageType.LASTAGGPARAM : MessageType.AGGPARAM, aggregatedParams.get(round), round, clientId, "non");
//        FLMessage msg = new FLMessage((currentRound == numOfRounds) ? MessageType.LASTAGGPARAM : MessageType.AGGPARAM, "Hello", currentRound, clientId, "non");
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
            receivedParams++;
            sendParametersToAggregator(msg.getContent(), msg.getExtension());
            if ((receivedParams >= clientNums - byzNums)){
                System.out.println("Send Aggregate to Aggregator by client " + msg.getClientId());
                aggregateParams();
                return sendAggParams(msg.getClientId(), msg.getRound());
            }
            else{
                return new FLMessage(MessageType.WAITTHIS, "", currentRound, msg.getClientId(), "non");
            }
        }
        else{
            return sendAggParams(msg.getClientId(), msg.getRound());
        }
    }

    public FLMessage handleCheckMsg(FLMessage msg) throws IOException {
        if (msg.getRound() >= currentRound){
            return new FLMessage(MessageType.WAITTHIS, "", currentRound, msg.getClientId(), "non");
        }
        else{
            return sendAggParams(msg.getClientId(), msg.getRound());
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
        if(args.length < 8) {
            System.out.println("Use: java FLServer <processId> <ClientNums> <NumOfRounds> <address> <byzNums> <aggregator> <attack> <test>");
            System.exit(-1);
        }
        new FLServer(Integer.parseInt(args[0]), Integer.parseInt(args[1]), Integer.parseInt(args[2]), args[3], Integer.parseInt(args[4]), args[5], args[6], args[7]);
    }
}
