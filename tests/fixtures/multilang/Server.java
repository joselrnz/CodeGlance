public class Server {
    private int port;

    public Server(int port) { this.port = port; }

    public void start() { System.out.println("start"); }

    public int getPort() { return port; }
}
