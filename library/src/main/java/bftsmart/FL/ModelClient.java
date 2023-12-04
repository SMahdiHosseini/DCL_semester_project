package bftsmart.FL;

import javax.xml.crypto.Data;
import java.io.*;
import java.net.Socket;
import java.net.ServerSocket;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public class ModelClient {
    private DataInputStream in;
    private DataOutputStream out;
    public String datasetSize;
    public ModelClient(String address, int id, int clientsNums, int byzNums, String aggregator, String attackName, String _test){
        try {
           ServerSocket serverSocket = new ServerSocket(6100);
            // ServerSocket serverSocket = new ServerSocket(0);
            int port = serverSocket.getLocalPort();
            System.out.println("Cleint " + id + " Port: " + port);
            //Windows
            //  Process modelProcess = Runtime.getRuntime().exec("python ../../../../main/Client_bft.py " + Integer.toString(id) + " " + address + " " + Integer.toString(port));
            //Linux
            // Process modelProcess = Runtime.getRuntime().exec("python3 ../../../../main/Client_bft.py " + Integer.toString(clientsNums) + " " + Integer.toString(id) + " " + address + " " + Integer.toString(port) + " " + Integer.toString(byzNums) + " " + aggregator + " " + attackName + " " + _test);
            Socket socket = serverSocket.accept();
            in = new DataInputStream(socket.getInputStream());
            out = new DataOutputStream(socket.getOutputStream());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void setParameters(String parameters) throws IOException {
        String newParams = "NEWPARAMS";
        out.writeUTF(newParams);
        String ack = in.readUTF();
        if (ack.equals("ACK"))
            out.writeUTF(String.valueOf(parameters.getBytes().length));
        ack = in.readUTF();
        if (ack.equals("ACK"))
            out.write(parameters.getBytes(), 0, parameters.getBytes().length);
        ack = in.readUTF();
        out.flush();
    }
    public String train() throws IOException {
        String train = "TRAIN";
        out.writeUTF(train);
        out.flush();

        datasetSize = in.readUTF();
        int msg_size = Integer.parseInt(in.readUTF());
        byte[] data = new byte[msg_size];
        // in.read(data, 0, data.length);
        in.readFully(data);
        return new String(data, 0, data.length);
    }
    public void terminate() throws IOException {
        String terminate = "TERMINATE";
        out.writeUTF(terminate);
        out.flush();
        String ack = in.readUTF();
        if (ack.equals("ACK"))
            System.out.println("Python process terminated");
    }
}
