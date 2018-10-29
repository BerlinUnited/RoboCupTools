package gcteamcommconverter;

import gcteamcommconverter.FileConverter.FileConverterRaw;
import gcteamcommconverter.FileConverter.FileConverterTC;
import gcteamcommconverter.FileConverter.FileConverter;
import gcteamcommconverter.FileConverter.FileConverterGTC;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.stream.Collectors;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GcTeamcommConverter
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
        a.put(45, "Naova ETS");
        a.put(46, "Recife Soccer");
        a.put(47, "Rinobot");
  
        a.put(90, "DoBerMan");
        a.put(91, "B-HULKs");
        a.put(92, "Swift-Ark");
        a.put(93, "Team USA");
        a.put(94, "B-Swift");
        a.put(95, "AstroNAOtas");
        a.put(96, "Team-Team");
        TEAM_NAMES = Collections.unmodifiableMap(a);
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // create class loaders for gamecontroller jars
        List<ClassLoader> gc = loadGameControllers();
        // vars set by the given arguments
        ArrayList<String> args_files = new ArrayList<>();
        boolean convertAll = false;
        // init converter & file container
        ArrayList<Class<? extends FileConverter>> converter = new ArrayList<>();
        ArrayList<File> files = new ArrayList<>();
        
        // parse arguments
        for (String arg : args) {
            // parse application options
            if(arg.equals("--raw")) {
                converter.add(FileConverterRaw.class);
            } else if(arg.equals("--tc")) {
                converter.add(FileConverterTC.class);
            } else if(arg.equals("--gtc")) {
                converter.add(FileConverterGTC.class);
            } else if(arg.equals("--help")||arg.equals("-h")) {
                printHelp();
                return;
            } else if(arg.equals("--all")) {
                convertAll = true;
            } else {
                // treat argument as file/directory
                args_files.add(arg);
            }
        }
        
        final boolean convertAllTmp = convertAll;
        // retrieve 'correct' files from the arguments files/directories
        args_files.forEach((file) -> {
            File f = new File(file);
            if(f.exists()) {
                if(f.isDirectory()) {
                    try (Stream<Path> paths = Files.walk(f.toPath())) {
                        paths.forEach((Path t) -> {
                            File df = t.toFile();
                            if(df.exists() && df.isFile() && df.getName().endsWith(".log")) {
                                // don't convert initial and finished logs, except it was explicitly set via argument
                                if(convertAllTmp || !(df.getName().contains("initial") || df.getName().contains("finished"))){
                                    files.add(df);
                                }                                
                            }
                        }
                        );
                    } catch (IOException e) {
                      e.printStackTrace();
                    }
                } else if(f.isFile()) {
                    files.add(f);
                }
            } else {
                System.err.println("File doesn't exists! (" + f.getName() + ") or unknown Argument.");
            }
        });
        
        if(files.isEmpty() || converter.isEmpty()) {
            printHelp();
        } else {
            // instatiate file converter
            List<FileConverter> converterObj = converter.stream().map((cls) -> {
                try { 
                    return (FileConverter) cls.getConstructor().newInstance();
                } catch (Exception ex) {
                    Logger.getLogger(GcTeamcommConverter.class.getName()).log(Level.SEVERE, null, ex);
                }
                return null;
            }).collect(Collectors.toList());
            
            // iterate through files and apply converters
            files.forEach((file) -> {
                GcLogFile lf = new GcLogFile(file, gc);
                
                if(!lf.canReadFile()) {
                    System.err.println("Can not read file: " + file.getAbsolutePath());
                } else if(!lf.canWriteFile()) {
                    System.err.println("Cannot write output file! (access rights?)");
                } else if(lf.getClassLoader() == null) {
                    System.err.println("No suitable GameController available!");
                } else if(lf.getData() == null) {
                    System.err.println("No data available!");
                } else {
                    converterObj.forEach((conv) -> {
                        System.out.println("convert '" + file.getAbsolutePath() + "' to '" + file.getAbsoluteFile() + conv.getExtension() + "'");
                        
                        // select teams, except for raw converteer
                        if(conv instanceof FileConverterRaw) {
                            conv.setTeams(lf.getTeams());
                        } else {
                            conv.setTeams(selectTeams(lf.getTeams()));
                        }
                        
                        // converted & write data
                        int counter_conv = lf.writeFile(conv);
                        
                        System.out.println("Message statistics: \n" 
                                + "\tparsing, ok = " + lf.counter_ok + "\n"
                                + "\tparsing, error =  " + lf.counter_fail + "\n"
                                + "\tfilter/convert, ok =  " + counter_conv + "\n"
                                + "\tfilter/convert, error =  " + (lf.counter_ok - counter_conv) + "\n"
                        );
                    });
                }
            });
        }
    } // END main()
    
    private static void printHelp() {
        System.out.println("Converts TeamCommunication log files of the GameController to JSON file(s).\n"
                + "Usage: java -jar GcTeamcommConverter.jar [--raw] [--tc] [--gtc] <File|Directory>\n"
                + "\t-h|--help\tshows this help message\n"
                + "\t--raw\tconverts log file 'as-is' to json with extension '.raw.json'\n"
                + "\t--tc\tconverts log file team communication to json (specific data only) with extension '.tc.json'\n"
                + "\t--gtc\tconverts log file gamecontroller and team communication to json (specific data only) with extension '.gtc.json'\n"
                + "\t--all\tby default files containing the substrings 'initial' and 'finished' are not converted, with this option they get converted too\n"
        );
    } // END printHelp()
    
    /**
     * Creates class loader for all jar files in the 'gc' directory.
     * 
     * @return a list of class loaders
     */
    private static List<ClassLoader> loadGameControllers() {
        File gc = new File("gc");
        List<ClassLoader> gamecontrollers = new ArrayList<>();
        if(gc.isDirectory()) {
            // iterate through files
            for (File jar : gc.listFiles()) {
                // 'accept' only jar files
                if(jar.isFile() && jar.getAbsolutePath().endsWith(".jar")) {
                    try {
                        gamecontrollers.add(new GcClassLoader(jar));
                        System.out.println("Found GameController: " + jar.getName());
                    } catch (SecurityException | IllegalArgumentException ex) {
                        Logger.getLogger(GcTeamcommConverter.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }
            }
        }
        return gamecontrollers;
    } // END loadGameControllers()
    
    /**
     * Asks the user to select team numbers from the given set.
     * 
     * @param teams the numbers the user can choose from.
     * @return the selected team numbers
     */
    public static Set<Integer> selectTeams(Set<Integer> teams) {
        if(teams.size() > 2) {
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
            Set<Integer> selection = teams.stream().filter((t) -> { return result.contains(t); }).collect(Collectors.toSet());
            System.out.println("Selection: " + selection);
            return selection;
        }
        return teams;
    } // END selectTeams()
}
