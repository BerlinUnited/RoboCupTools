package gcteamcommconverter.data;

/**
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class SplMessage
{
    public final long timestamp;
    public final byte gameState;
    public final String address;
    public final Object message;

    public SplMessage(long timestamp, byte gameState, String address, Object spl) {
        this.timestamp = timestamp;
        this.gameState = gameState;
        this.address = address;
        this.message = spl;
    }
    
    public int getTeamNumber() {
        try {
            return this.message.getClass().getField("teamNum").getByte(message);
        } catch (Exception ex) { /* ignore */ }
        return 0;
    }
    
    public int getVersion() {
        try {
            return this.message.getClass().getField("version").getByte(message);
        } catch (Exception ex) { /* ignore */ }
        return 0;
    }
}