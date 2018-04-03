package gcteamcommconverter.data;

/**
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GameControlData
{
    public final long timestamp; 
    public final Object data;

    public GameControlData(long timestamp, Object data) {
        this.timestamp = timestamp;
        this.data = data;
    }
}
