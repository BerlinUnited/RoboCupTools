package gcteamcommconverter.data;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class DataObject {

    public final long time;
    public final Object data;

    public DataObject(long t, Object d) {
        time = t;
        data = d;
    }
}
