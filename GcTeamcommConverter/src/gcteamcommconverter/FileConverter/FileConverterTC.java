package gcteamcommconverter.FileConverter;

import gcteamcommconverter.data.SplMessage;
import java.nio.ByteBuffer;

/**
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class FileConverterTC extends FileConverter
{
    /** Tracks the last active game state in the log file. */
    private byte currentGameState = 0; //GameControlData.STATE_INITIAL;
    
    /**
     * Returns the extension, which should be used to write the converted data of this FileConverter.
     * 
     * @return the file extension ".tc.json"
     */
    @Override
    public final String getExtension() {
        return ".tc.json";
    }

    /**
     * Converts & filters the given log Object o to a SplMessage object.
     * If the given log object wasn't of type 'SPLStandardMessagePackage', couldn't be converted
     * or the team number isn't in the team selection, "null" is returned.
     * 
     * @param t the timestamp of this log object
     * @param o the log object
     * @return a SplMessage object or null
     */
    @Override
    public Object convertAndFilter(long t, Object o) {
        
        if (o.getClass().getName().equals("teamcomm.net.SPLStandardMessagePackage")) {
            try {
                // load class & instantiate
                Class<?> cls = o.getClass().getClassLoader().loadClass("data.SPLStandardMessage");
                Object spl = cls.newInstance();
                
                // parse data to SPLStandardMessage and return it only if it is one of the selected teams
                boolean valid = (boolean) cls.getMethod("fromByteArray", ByteBuffer.class).invoke(spl, ByteBuffer.wrap((byte[]) o.getClass().getField("message").get(o)));
                
                // use the 'extended' SplMessage as container
                SplMessage message = new SplMessage(t, currentGameState, (String)o.getClass().getField("host").get(o), spl);
                
                // if we have a valid message, check teamnumber and return the message if it is a selected teamnumber
                if(valid && teams.contains(message.getTeamNumber())) {
                    return message;
                }
            } catch (Exception e) { /* shouldn't happen, if we have a SPLStandardMessagePackage! */ }
            
        } else if (o.getClass().getName().equals("data.AdvancedData") || o.getClass().getName().equals("data.GameControlData")) {
            try {
                currentGameState = o.getClass().getField("gameState").getByte(o);
            } catch (Exception e) { /* shouldn't happen, if we have a GameControlData! */ }
        }
        
        // current object shouldn't be included in the json output
        return null;
    }
}