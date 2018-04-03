package gcteamcommconverter.data;

import com.google.gson.Gson;
import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GameControlDataConverter extends TypeAdapter<GameControlData>
{
    /**
     * The global gson object, should be set by the caller to get consistent json value formats.
     */
    public Gson json;
    
    /**
     * Field selection for the SPLMessage version 6.
     */
    private final List<String> fields = Arrays.asList(
              "packetNumber"
            , "playersPerTeam"
            , "gameType"
            , "gameState"
            , "firstHalf"
            , "kickOffTeam"
            , "secGameState"
            , "secsRemaining"
            , "secondaryTime"
    );
    
    /**
     * Calls different writer methods for the different SPLStandardMessage versions.
     * @param writer    the json writer object
     * @param msg       'abstract' SPLStandardMessage
     * @throws IOException 
     */
    @Override
    public void write(JsonWriter writer, GameControlData msg) throws IOException {
        // the fields/values of a SPLStandardMessage are wrapped in a json object.
        writer.beginObject();
        writer.name("timestamp").jsonValue(json.toJson(msg.timestamp));
        // iterate through all fields of the GameControlData and convert only the fields defined above to json.
        for (Field field : msg.data.getClass().getFields()) {
            if(fields.contains(field.getName())) {
                field.setAccessible(true);
                try {
                    writer.name(field.getName()).jsonValue(json.toJson(field.get(msg.data)));
                } catch (IllegalArgumentException | IllegalAccessException ex) {
                    /* shouldn't happen */
                    Logger.getLogger(SplMessageConverter.class.getName()).log(Level.SEVERE, field.getName(), ex);
                }
            }
        }
        writer.endObject();
    }
    
    @Override
    public GameControlData read(JsonReader reader) throws IOException {
        // currently not needed ...
        return null;
    }
    
}
