package gcteamcommconverter.FileConverter;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.stream.JsonWriter;
import gcteamcommconverter.data.GameControlData;
import gcteamcommconverter.data.GameControlDataConverter;
import gcteamcommconverter.data.SplMessage;
import gcteamcommconverter.data.SplMessageConverter;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.EOFException;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.stream.Collectors;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public abstract class FileConverter
{
    /**
     * The id and the names of all known teams.
     */
    public static final Map<Integer, String> TEAM_NAMES;
    static {
        Map<Integer, String> a = new HashMap<>();
        a.put(0, "Invisibles");
        a.put(1, "UT Austin Villa");
        a.put(2, "Austrian Kangaroos");
        a.put(3, "Bembelbots");
        a.put(4, "Berlin United");
        a.put(5, "B-Human");
        a.put(6, "Cerberus");
        a.put(7, "DAInamite");
        a.put(8, "Dutch Nao Team");
        a.put(9, "Edinferno");
        a.put(10, "Kouretes");
        a.put(11, "MiPal");
        a.put(12, "Nao Devils Dortmund");
        a.put(13, "Nao-Team HTWK");
        a.put(14, "Northern Bites");
        a.put(15, "NTU RoboPAL");
        a.put(16, "RoboCanes");
        a.put(17, "RoboEireann");
        a.put(18, "UNSW Sydney");
        a.put(19, "SPQR Team");
        a.put(20, "TJArk");
        a.put(21, "UChile Robotics Team");
        a.put(22, "UPennalizers");
        a.put(23, "Crude Scientists");
        a.put(24, "HULKs");
        a.put(26, "MRL-SPL");
        a.put(27, "Philosopher");
        a.put(28, "Rimal Team");
        a.put(29, "SpelBots");
        a.put(30, "Team-NUST");
        a.put(31, "UnBeatables");
        a.put(32, "UTH-CAR");
        a.put(33, "NomadZ");
        a.put(34, "SPURT");
        a.put(35, "Blue Spider");
        a.put(36, "Camellia Dragons");
        a.put(37, "JoiTech-SPL");
        a.put(38, "Linköping Humanoids");
        a.put(39, "WrightOcean");
        a.put(40, "Mars");
        a.put(41, "Aztlan Team");
        a.put(42, "CMSingle");
        a.put(43, "TeamSP");
        a.put(44, "Luxembourg United");
        a.put(90, "DoBerMan");
        a.put(91, "B-HULKs");
        a.put(92, "Swift-Ark");
        a.put(93, "Team USA");
        TEAM_NAMES = Collections.unmodifiableMap(a);
    }
    
    /**
     * Input file
     */
    protected File file;
    
    /**
     * Suffix for the output file
     */
    protected String suffix = ".json";
    
    /**
     * Counter for correct messages parsing
     */
    protected long counter_ok = 0;
    
    /**
     * Counter for failed message parsing
     */
    protected long counter_fail = 0;
    
    /**
     * Counter for failed message parsing
     */
    protected long counter_conv = 0;
    
    /**
     * In the input file contained teams.
     */
    protected HashSet teams = new HashSet();
    
    /**
     * 
     */
    protected ArrayList<DataObject> data = new ArrayList<>();
    
    /**
     * 
     */
    protected boolean selectTeams = true;

    
    protected List<ClassLoader> gamecontrollers;

    /**
     * Constructor.
     * @param f 
     */
    public FileConverter(File f) {
        file = f;
    }
    
    /**
     * Constructor.
     * @param f
     * @param s 
     */
    public FileConverter(File f, String s) {
        file = f;
        suffix = s;
    }
    
    public void setGameControllers(List<ClassLoader> gc) {
        gamecontrollers = gc;
    }
    
    protected String getOutputFile() {
        return file.getAbsoluteFile() + suffix;
    }
    
    private boolean canWriteFile() {
        File output = new File(getOutputFile());
        try {
            output.createNewFile();
            new FileWriter(output).close(); // trigger exception (if couldn't write)
        } catch (IOException ex) {
            System.err.println("Cannot write output file! (access rights?)");
            return false;
        }
        return true;
    }
    
    private boolean canReadFile() {
        return file.canRead();
    }
    
    public void convertFile() {
        // read check
        if(!canReadFile()) {
            System.err.println("Can not read file: " + file.getAbsolutePath());
            return;
        }
        
        // write check
        if(!canWriteFile()) {
            System.err.println("Can not write output file: " + getOutputFile());
            return;
        }

        System.out.println("convert '" + file.getAbsolutePath() + "' to '" + getOutputFile() + "'");

        ByteArrayInputStream buf = readFile();
        ClassLoader loader = determineClassLoader(buf);
        if(loader != null) {
            parseData(buf, loader);
            selectTeams();
            writeFile();
        } else {
            System.err.println("No suitable GameController available!");
        }
            
        System.out.println("Message statistics: \n" 
                + "\tparsing, ok = " + counter_ok + "\n"
                + "\tparsing, error =  " + counter_fail + "\n"
                + "\tfilter/convert, ok =  " + counter_conv + "\n"
                + "\tfilter/convert, error =  " + (counter_ok - counter_conv) + "\n"
        );
    }
    
    protected void selectTeams() {
        if(selectTeams && teams.size() > 2) {
            System.out.println("Messages of more than two teams are in this log file:\n" + teams.stream().map(n->{return "- "+String.format("%3d", n) +": "+TEAM_NAMES.getOrDefault(n, "");}).collect(Collectors.joining("\n")));
            System.out.print("Type comma seperated team numbers, which you like to include: ");
            HashSet result = new HashSet();
            BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
            try {
                String s = br.readLine();
                String[] nums = s.split(",");
                for (String num : nums) {
                    try {
                        result.add(Integer.parseInt(num.trim()));
                    } catch (NumberFormatException e) { /* ignore */ }
                }
            } catch (IOException ex) {
                Logger.getLogger(FileConverter.class.getName()).log(Level.SEVERE, null, ex);
            }
            teams.retainAll(result);
            System.out.println("Selection: " + teams);
        }
    }
    
    /**
     * Writes the converted data as json to the output file.
     */
    protected void writeFile() {
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

        try (JsonWriter jw = new JsonWriter(new FileWriter(getOutputFile()))) {
            // open "global"/"enclosing" Array
            jw.beginArray();
            // write messages
            for (DataObject d : data) {
                Object o = convertAndFilter(d.time, d.data);
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
    } // END writeFile()
    
    /**
     * 
     * @return 
     */
    protected ByteArrayInputStream readFile() {
        try {
            return new ByteArrayInputStream(Files.readAllBytes(file.toPath()));
        } catch (IOException ex) {
            System.out.println(ex);
        }
        return null;
    } // END readFile()
    
    /**
     * 
     * @param input
     * @param loader 
     */
    protected void parseData(ByteArrayInputStream input, ClassLoader loader) {
        try(GamecontrollerInputStream stream = new GamecontrollerInputStream(input, loader)) {
            while (stream != null) {
                // read "prefix"
                final long time = stream.readLong();
                if (stream.readBoolean()) {
                    try {
                        Object o = stream.readObject();
                        if (o.getClass().getName().equals("teamcomm.net.SPLStandardMessagePackage")) {
                            try {
                                teams.add(o.getClass().getField("team").getInt(o));
                            } catch (Exception e) { /* shouldn't happen, if we really have a SPLStandardMessagePackage! */ }
                        }
                        // TODO: add teams! otherwise can not select teams?!
                        data.add(new DataObject(time, o));
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
    } // END parseData()
    
    /**
     * 
     * @param input
     * @return 
     */
    private ClassLoader determineClassLoader(ByteArrayInputStream input) {
        for (ClassLoader gamecontroller : gamecontrollers) {
            try(GamecontrollerInputStream stream = new GamecontrollerInputStream(input, gamecontroller)) {
                stream.setRequiredClass("data.AdvancedData");
                while (stream != null) {
                    stream.readLong();
                    if (stream.readBoolean()) {
                        try {
                            stream.readObject();
                            if(stream.isRequiredSatisfied()) {
                                input.reset();
                                return gamecontroller;
                            }
                        } catch (ClassNotFoundException ex) {
                        }
                    }
                }
            } catch (EOFException ex) {
            /* ignore EOF and proceed */
            } catch (Exception ex) {
                Logger.getLogger(FileConverter.class.getName()).log(Level.SEVERE, null, ex);
            }
            input.reset();
        }
        return null;
    } // END determineClassLoader()
  
    /**
     * 
     * @param t
     * @param o
     * @return 
     */
    abstract protected Object convertAndFilter(long t, Object o);
    // TODO: error during converting??
    
}

class DataObject {
    final long   time;
    final Object data;

    public DataObject(long t, Object d) {
        time = t;
        data = d;
    }
}