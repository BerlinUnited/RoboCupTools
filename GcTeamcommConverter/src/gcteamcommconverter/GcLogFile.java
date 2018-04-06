package gcteamcommconverter;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.stream.JsonWriter;
import gcteamcommconverter.FileConverter.FileConverter;
import gcteamcommconverter.data.DataObject;
import gcteamcommconverter.data.GameControlData;
import gcteamcommconverter.data.GameControlDataConverter;
import gcteamcommconverter.data.SplMessage;
import gcteamcommconverter.data.SplMessageConverter;
import java.io.ByteArrayInputStream;
import java.io.EOFException;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Representation of a (raw) GameController log file with some utility methods.
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GcLogFile
{
    /** The log file, which should be converted. */
    private final File file;
    
    /** The (raw) data of the log file. */
    private byte[] data;
    
    /** The (parsed) data of the log file. */
    private ArrayList<DataObject> data_parsed;
    
    /** Available class loader for parsing the log file. */
    private final List<ClassLoader> classLoader;
    
    /** The suitable class loader for this log file. */
    private ClassLoader loader;
    
    /** In the input file contained teams. */
    protected HashSet teams;
    
    /** Counter for correct messages parsing. */
    protected long counter_ok = 0;
    
    /** Counter for failed message parsing. */
    protected long counter_fail = 0;

    /**
     * 
     * @param file
     * @param cLoader 
     */
    public GcLogFile(File file, List<ClassLoader> cLoader) {
        this.file = file;
        this.classLoader = cLoader;
    }

    /**
     * Checks, whether the file can be read.
     * 
     * @return true if file is readable, false otherwise
     */
    public boolean canReadFile() {
        return file.canRead();
    }

    /**
     * creates a test file to check the write permissions.
     * 
     * @return true|false whether or not a file can be written.
     */
    public boolean canWriteFile() {
        File output = new File(file.getAbsoluteFile() + ".tmp");
        try {
            output.createNewFile();
            new FileWriter(output).close(); // trigger exception (if couldn't write)
            output.delete();
        } catch (IOException ex) {
            return false;
        }
        return true;
    }

    /**
     * Returns the data of this log file.
     * The data is read the first time the function is called.
     * 
     * @return raw data of the log file or null if there's no data or an error occured.
     */
    public byte[] getData() {
        if(data == null) {
            try {
                data = Files.readAllBytes(file.toPath());
            } catch (IOException e) {    
            }
        }
        return data;
    }

    /**
     * Returns the suitable class loader for this file
     * The class loader is determined the first time the function is called.
     * 
     * @return the class loader or null if no suitable class was found
     */
    public ClassLoader getClassLoader() {
        if(loader == null) {
            determineClassLoader();
        }
        return loader;
    }

    /**
     * Determines the suitable class loader for this file based on the available fields
     * of the 'AdvancedData' class.
     */
    private void determineClassLoader() {
        // only if there's data
        if(getData() != null) {
            ByteArrayInputStream input = new ByteArrayInputStream(getData());
            // test all available class loaders
            for (ClassLoader cl : classLoader) {
                try(GcInputStream stream = new GcInputStream(input, cl)) {
                    stream.setRequiredClass("data.AdvancedData");
                    while (stream != null) {
                        stream.readLong();
                        if (stream.readBoolean()) {
                            try {
                                stream.readObject();
                                // check, if the last read object fulfills all requirements
                                if(stream.isRequiredSatisfied()) {
                                    // found a suitable class loader
                                    loader = cl;
                                    return;
                                }
                            } catch (ClassNotFoundException ex) { /* ignore */ }
                        }
                    }
                } catch (EOFException ex) {
                /* ignore EOF and proceed */
                } catch (Exception ex) {
                    Logger.getLogger(GcLogFile.class.getName()).log(Level.SEVERE, null, ex);
                }
                // reset input stream for the next class loader
                input.reset();
            }
            // no suitable class loader found
            loader = null;
        }
    } // END determineClassLoader()
  
    /**
     * Returns the teams of this log file.
     * The teams are determined the first time the function is called.
     * 
     * @return set of team numbers of this file
     */
    public Set<Integer> getTeams() {
        if(teams == null) {
            teams = new HashSet();
            parseData();
        }
        return teams;
    }
    
    /**
     * Returns the parsed data as list of DataObjects.
     * The data is parsed the first time the function is called.
     * 
     * @return
     */
    public ArrayList<DataObject> getParsedData() {
        if(data_parsed == null) {
            parseData();
        }
        return data_parsed;
    }

    /**
     * Parses the log file data.
     * In addition, the contained teams are retrieved too.
     */
    private void parseData() {
        data_parsed = new ArrayList<>();
        // only if we have a suitable class loader for this log file
        if(getClassLoader() != null && getTeams() != null) {
            try(GcInputStream stream = new GcInputStream(new ByteArrayInputStream(getData()), loader)) {
                while (stream != null) {
                    // read "prefix"
                    final long time = stream.readLong();
                    if (stream.readBoolean()) {
                        try {
                            // parses the object; the selected class loader is used
                            Object o = stream.readObject();
                            // if we have teamcomm data, retrieve the team of this message(s)
                            if (o.getClass().getName().equals("teamcomm.net.SPLStandardMessagePackage")) {
                                try {
                                    teams.add(o.getClass().getField("team").getInt(o));
                                } catch (Exception e) { /* shouldn't happen, if we really have a SPLStandardMessagePackage! */ }
                            }
                            data_parsed.add(new DataObject(time, o));
                            counter_ok++;
                        } catch (ClassNotFoundException ex) {
                            Logger.getLogger(FileConverter.class.getName()).log(Level.SEVERE, null, ex);
                            counter_fail++;
                        }
                    } else {
                        // TODO: what's this?!?
                        System.out.println(time + " | " +  stream.readInt());
                        counter_fail++;
                    }
                }
            } catch (EOFException ex) {
                /* ignore EOF and proceed */
            } catch (IOException ex) {
                Logger.getLogger(FileConverter.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    } // END parseData()
 
    /**
     * Writes the converted data as json to the output file.
     * 
     * @param c the FileConverter, which should be applied.
     * @return number of successfull 'converted' log objects
     */
    public int writeFile(FileConverter c) {
        // use JsonWriter to write the enclosing Json-Array ...
        // configure & create GsonBuilder
        SplMessageConverter json_c = new SplMessageConverter();
        GameControlDataConverter json_gc = new GameControlDataConverter();
        Gson json = new GsonBuilder()
            .serializeSpecialFloatingPointValues() // write NaN value without throwing error/warning
            .registerTypeAdapter(SplMessage.class, json_c)
            .registerTypeAdapter(GameControlData.class, json_gc)
            .create();
        json_c.json = json;
        json_gc.json = json;
        int counter_conv = 0;

        try (JsonWriter jw = new JsonWriter(new FileWriter(file.getAbsoluteFile() + c.getExtension()))) {
            // open "global"/"enclosing" Array
            jw.beginArray();
            // write messages
            for (DataObject d : getParsedData()) {
                Object o = c.convertAndFilter(d.time, d.data);
                if(o != null) {
                    if(o instanceof SplMessage) {
                        jw.jsonValue(json.toJson(o, SplMessage.class));
                    } else if(o instanceof GameControlData) {
                        jw.jsonValue(json.toJson(o, GameControlData.class));
                    } else {
                        jw.jsonValue(json.toJson(o));
                    }
                    counter_conv++;
                }
            }
            // write post info to json output file
            jw.endArray();
        } catch (IOException ex) {
            Logger.getLogger(FileConverter.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        return counter_conv;
    } // END writeFile()
}