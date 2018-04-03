package gcteamcommconverter.FileConverter;

import gcteamcommconverter.data.GameControlData;
import gcteamcommconverter.data.SplMessage;
import java.io.File;
import java.nio.ByteBuffer;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class FileConverterGTC extends FileConverter
{
    private byte currentGameState = 0;//GameControlData.STATE_INITIAL;
    
    public FileConverterGTC(File f) {
        super(f, ".gtc.json");
    }
    
    @Override
    protected Object convertAndFilter(long t, Object o) {
        
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
                return new GameControlData(t, o);
            } catch (Exception e) { /* shouldn't happen, if we have a GameControlData! */ }
        }
        // current object shouldn't be included in the json output
        return null;
    }
}