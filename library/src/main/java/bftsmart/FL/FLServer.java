package bftsmart.FL;

import bftsmart.tom.MessageContext;
import bftsmart.tom.ServiceReplica;
import bftsmart.tom.server.defaultservices.DefaultSingleRecoverable;

import java.io.*;
import java.lang.reflect.Array;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.locks.ReentrantLock;

public final class FLServer extends DefaultSingleRecoverable {

    private int clientNums;
    private int numOfRounds;
    private int currentRound;
    private HashMap<Integer, String> aggregatedParams;
    private int receivedParams;
    private int byzNums;
    private ReentrantLock lock, lock2;
    private DataInputStream in;
    private DataOutputStream out;
    private HashMap<Integer, ArrayList<Integer>> recevdParamIds;
    private String test;
    private String fileName;
    private ArrayList<Integer> connectedClients;
    public FLServer(int id, int _clientNums, int _numOfRounds, String address, int byzNums, String aggregatorName, String attackName, String _test){
        this.numOfRounds = _numOfRounds;
        this.clientNums = _clientNums;
        this.receivedParams = 0;
        this.connectedClients = new ArrayList<Integer>();
        this.currentRound = 1;
        this.byzNums = byzNums;
        this.lock = new ReentrantLock();
        this.lock2 = new ReentrantLock();
        this.aggregatedParams = new HashMap<Integer, String>();
        this.recevdParamIds = new HashMap<Integer, ArrayList<Integer>>();
        this.test = _test;
        if (this.test.equals("Accuracy"))
            this.fileName = "../../../../Consensus_res/" + aggregatorName + "/ncl_" + Integer.toString(_clientNums + byzNums) + "/nbyz_" + Integer.toString(byzNums) + "/Performance_3/recevdParamIds.txt";
        else if (this.test.equals("Performance"))
            this.fileName = "../../../../Consensus_res/" + aggregatorName + "/ncl_" + Integer.toString(_clientNums) + "/nbyz_" + Integer.toString(byzNums) + "/Performance/recevdParamIds.txt";
        
        createRecvdParamIds();
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

    public void createRecvdParamIds() {
        if (this.test.equals("Accuracy")){
            ArrayList<Integer> byzClients = new ArrayList<Integer>();
            for (int i = clientNums; i < clientNums + byzNums; i++){
                byzClients.add(i);
            }
            try {
                FileReader fr = new FileReader(this.fileName);
                BufferedReader br = new BufferedReader(fr);
                for (int i = 1; i <= numOfRounds; i++){
                    recevdParamIds.put(i, new ArrayList<Integer>());
                    // for (int j = 0; j < 4; j++){
                    //     recevdParamIds.get(i).add(j);
                    // }
                    String[] ids = br.readLine().split(":")[1].split(",");
                    int last = 0;
                    for (int j = 0; j < ids.length; j++){
                        int id = Integer.parseInt(ids[j].trim());
                        if (!byzClients.contains(id))
                        {
                            recevdParamIds.get(i).add(id);
                            last++;
                        }
                        if (last == clientNums - byzNums)
                            break;
                    }
                    //TODO: remove
                    System.out.println("Round " + i + ": " + recevdParamIds.get(i));
                }
                br.close();
            } catch (NumberFormatException | IOException e) {
                throw new RuntimeException(e);
            }
            
        } else if (this.test.equals("Performance")){
            for (int i = 1; i <= numOfRounds; i++){
                recevdParamIds.put(i, new ArrayList<Integer>());
           }
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

        //write recvdParamIds to file
        if (this.test.equals("Performance")){
            FileWriter fw = new FileWriter(this.fileName);
            BufferedWriter bw = new BufferedWriter(fw);
            for (int i = 1; i <= numOfRounds; i++){
                bw.write("Round " + i + ": ");
                for (int j = 0; j < recevdParamIds.get(i).size(); j++){
                    bw.write(recevdParamIds.get(i).get(j) + ",");
                }
                bw.write("\n");
            }
            bw.close();
        }
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
        if (test.equals("Accuracy") && !recevdParamIds.get(currentRound).contains(msg.getClientId())){
            return new FLMessage(MessageType.WAITTHIS, "", msg.getRound(), msg.getClientId(), "non");
        }
        else{
            if (msg.getRound() == currentRound){
                lock2.lock();
                receivedParams++;
                recevdParamIds.get(currentRound).add(msg.getClientId());
                sendParametersToAggregator(msg.getContent(), msg.getExtension());
                if ((receivedParams >= clientNums - byzNums)){
                    System.out.println("Send Aggregate to Aggregator by client " + msg.getClientId());
                    System.out.println("Received params: " + recevdParamIds.get(currentRound));
                    aggregateParams();
                    lock2.unlock();
                    return sendAggParams(msg.getClientId(), msg.getRound());
                }
                else{
                    lock2.unlock();
                    return new FLMessage(MessageType.WAITTHIS, "", currentRound, msg.getClientId(), "non");
                }
            }
            else{
                return sendAggParams(msg.getClientId(), msg.getRound());
            }
        }
    }
 
    public FLMessage handleCheckMsg(FLMessage msg) throws IOException {
        if (msg.getRound() >= currentRound){
            return new FLMessage(MessageType.WAITTHIS, "", msg.getRound(), msg.getClientId(), "non");
        }
        else{
            System.out.println("Got Check from " + msg.getClientId() + " Curretn Round: " + currentRound + " Client round:" + msg.getRound());
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
            } else if (message.getType().equals(MessageType.GETSTATUS)){
                if (connectedClients.size() == clientNums){
                    return FLMessage.toBytes(new FLMessage(MessageType.START, "", 0, message.getClientId(), "non"));
                }
                else{
                    if (!connectedClients.contains(message.getClientId())){
                        connectedClients.add(message.getClientId());
                    }
                    return FLMessage.toBytes(new FLMessage(MessageType.WAITTHIS, "", 0, message.getClientId(), "non"));
                }
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
