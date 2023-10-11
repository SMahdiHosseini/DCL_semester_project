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
    private int port;
    private String address;
    private int id;
    public ModelClient(String address, int id){
        this.address = address;
        this.id = id;
        try {
//            ServerSocket serverSocket = new ServerSocket(6000);
            ServerSocket serverSocket = new ServerSocket(0);
            this.port = serverSocket.getLocalPort();
            System.out.println("Cleint " + id + " Port: " + this.port);
//            modelProcess = Runtime.getRuntime().exec("python ../../../src/main/java/bftsmart/FL/Client.py " + Integer.toString(id) + " " + address + " " + Integer.toString(this.port));
            Process modelProcess = Runtime.getRuntime().exec("python ../../../../Simple_FL/Client_bft.py " + Integer.toString(id) + " " + address + " " + Integer.toString(this.port));
//            DataInputStream err = new DataInputStream(modelProcess.getErrorStream());
//            String s;
//            while((s = err.readLine()) != null)
//                System.out.println("FF: " + s);
            Socket socket = serverSocket.accept();
            in = new DataInputStream(socket.getInputStream());
            out = new DataOutputStream(socket.getOutputStream());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void setParameters(byte[] parameters) throws IOException, InterruptedException {
        String newParams = "NEWPARAMS";
        out.writeUTF(newParams);
        String ack = in.readUTF();
        if (ack.equals("ACK"))
            out.writeUTF(String.valueOf(parameters.length));
        ack = in.readUTF();
        if (ack.equals("ACK"))
            out.write(parameters, 0, parameters.length);
        ack = in.readUTF();
//        if (ack.equals("ACK"))
//            System.out.println("Received!");
        out.flush();

    }
    public byte[] train() throws IOException {
        String train = "TRAIN";
        out.writeUTF(train);
        out.flush();

        String fraction = in.readUTF();
        int msg_size = Integer.parseInt(in.readUTF()) * 4;
        byte[] data = new byte[msg_size];
        in.read(data, 0, data.length);
//        String result = new String(data, 0, data.length);
//        return fraction + "#" + result;
        return data;
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
