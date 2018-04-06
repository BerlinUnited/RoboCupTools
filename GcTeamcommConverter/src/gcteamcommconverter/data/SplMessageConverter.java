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
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class SplMessageConverter extends TypeAdapter<SplMessage>
{
    /**
     * The global gson object, should be set by the caller to get consistent json value formats.
     */
    public Gson json;
    
    /**
     * Calls different writer methods for the different SPLStandardMessage versions.
     * @param writer    the json writer object
     * @param msg       'abstract' SPLStandardMessage
     * @throws IOException 
     */
    @Override
    public void write(JsonWriter writer, SplMessage msg) throws IOException {
        // the fields/values of a SPLStandardMessage are wrapped in a json object.
        writer.beginObject();
        
        writer.name("timestamp").jsonValue(json.toJson(msg.timestamp));
        writer.name("gameState").jsonValue(json.toJson(msg.gameState));
        writer.name("address").jsonValue(json.toJson(msg.address));
        
        switch(msg.getVersion()) {
            case 6:
                write_v6(writer, msg.message);
                break;
            case 7:
                write_v7(writer, msg.message);
                break;
        }
        
        writer.endObject();
    }
    
    /**
     * Field selection for the SPLMessage version 6.
     */
    private final List<String> fields_v6 = Arrays.asList(
              "header"
            , "version"
            , "playerNum"
            , "teamNum"
            , "fallen"
            , "pose"
            , "walkingTo"
            , "shootingTo"
            , "ballAge"
            , "ball"
            , "ballVel"
            , "suggestion"
            , "intention"
            , "averageWalkSpeed"
            , "data"
            , "maxKickDistance"
            , "currentPositionConfidence"
            , "currentSideConfidence"
    );
    
    /**
     * Json writer for the SPLMessage version 6.
     * 
     * @param writer    the json writer object
     * @param msg       the SPLStandardMessage verion 6
     * @throws IOException 
     */
    private void write_v6(JsonWriter writer, Object msg) throws IOException {
        // iterate through all fields of the SPLMessage version 7 and convert only the fields defined above to json.
        for (Field field : msg.getClass().getFields()) {
            if(fields_v6.contains(field.getName())) {
                // intention and suggestion needs 'special' attention
                switch(field.getName()) {
                    case "intention":
                        try {
                            Object intention = field.get(msg);
                            writer.name(field.getName()).value((int)intention.getClass().getMethod("ordinal").invoke(intention));
                        } catch (Exception e) {}
                        break;
                    case "suggestion":
                        writer.name(field.getName());
                        writer.beginArray();
                        try {
                            Object[] objs = (Object[]) field.get(msg);
                            for (Object obj : objs) {
                                writer.value((int)obj.getClass().getMethod("ordinal").invoke(obj));
                            }
                        } catch (Exception e) {}
                        writer.endArray();
                        break;
                    default:
                        field.setAccessible(true);
                        try {
                            writer.name(field.getName()).jsonValue(json.toJson(field.get(msg)));
                        } catch (IllegalArgumentException | IllegalAccessException ex) {
                            Logger.getLogger(SplMessageConverter.class.getName()).log(Level.SEVERE, field.getName(), ex);
                        }
                        break;
                }
            }
        }
    }

    /**
     * Field selection for the SPLMessage version 7.
     */
    private final List<String> fields_v7 = Arrays.asList(
              "header"
            , "version"
            , "playerNum"
            , "teamNum"
            , "fallen"
            , "pose"
            , "ballAge"
            , "ball"
            , "data"
    );

    /**
     * Json writer for the SPLMessage version 7.
     * 
     * @param writer    the json writer object
     * @param msg       the SPLStandardMessage verion 7
     * @throws IOException 
     */
    private void write_v7(JsonWriter writer, Object msg) throws IOException {
        // iterate through all fields of the SPLMessage version 7 and convert only the fields defined above to json.
        for (Field field : msg.getClass().getFields()) {
            if(fields_v7.contains(field.getName())) {
                field.setAccessible(true);
                try {
                    writer.name(field.getName()).jsonValue(json.toJson(field.get(msg)));
                } catch (IllegalArgumentException | IllegalAccessException ex) {
                    /* shouldn't happen */
                    Logger.getLogger(SplMessageConverter.class.getName()).log(Level.SEVERE, field.getName(), ex);
                }
            }
        }
    }

    @Override
    public SplMessage read(JsonReader reader) throws IOException {
        // currently not needed ...
        return null;
    }
}
