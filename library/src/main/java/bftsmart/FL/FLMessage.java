package bftsmart.FL;

import java.io.*;
import java.util.HashSet;
import java.util.Set;

public class FLMessage {
    private MessageType type;
    private String content;
    private int round;
    private int clientId;
//    private int contentSize;
    private String extension;

    public FLMessage(MessageType t, String c, int r, int id, String ex) {
        type = t;
        content = c;
        round = r;
        clientId = id;
//        contentSize = cSize;
        extension = ex;
    }
    public FLMessage() {
    }

    public static byte[] toBytes(FLMessage message) throws IOException {
        ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
        ObjectOutputStream objOut = new ObjectOutputStream(byteOut);

        objOut.writeObject(message.getType());
        objOut.writeInt(message.getRound());
        objOut.writeInt(message.getClientId());
        objOut.writeObject(message.getExtension());
//        objOut.writeInt(message.getContentSize());
        objOut.writeObject(message.getContent());

        objOut.flush();
        byteOut.flush();

        return byteOut.toByteArray();
    }

    public static FLMessage fromBytes(byte[] rep) throws IOException, ClassNotFoundException {
        ByteArrayInputStream byteIn = new ByteArrayInputStream(rep);
        ObjectInputStream objIn = new ObjectInputStream(byteIn);

        FLMessage msg = new FLMessage();
        msg.setType((MessageType) objIn.readObject());
        msg.setRound((int) objIn.readInt());
        msg.setClientId((int) objIn.readInt());
        msg.setExtension((String) objIn.readObject());
//        msg.setContentSize((int) objIn.readInt());
//        byte[] b = new byte[msg.getContentSize()];
//        objIn.read(b, 0, msg.getContentSize());
        msg.setContent((String) objIn.readObject());

        return msg;
    }

    public MessageType getType() {
        return type;
    }
    public void setType(MessageType t) {
        type = t;
    }
    public int getClientId() {
        return clientId;
    }
    public void setClientId(int id) {
        clientId = id;
    }
    public String getContent() {
        return content;
    }
    public void setContent(String c) {
        content = c;
    }
    public int getRound(){
        return round;
    }
    public void setRound(int r){
        round = r;
    }
//    public void setContentSize(int cs){
//        contentSize = cs;
//    }
//    public int getContentSize(){
//        return contentSize;
//    }
    public String getExtension(){
        return extension;
    }
    public void setExtension(String ex){
        extension = ex;
    }
}
