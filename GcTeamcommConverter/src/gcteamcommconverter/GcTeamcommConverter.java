package gcteamcommconverter;

import gcteamcommconverter.FileConverter.FileConverterRaw;
import gcteamcommconverter.FileConverter.FileConverterTC;
import gcteamcommconverter.FileConverter.FileConverter;
import gcteamcommconverter.FileConverter.FileConverterGTC;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
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
    private static final String applicationPath;
    static {
        // retrieve application path; jar file and netbeans execution are "detected"
        Matcher mt = Pattern.compile("(jar:)?(file:)?(.+)((/build/.+)|(/.+\\.jar!.+))GcTeamcommConverter.class", Pattern.CASE_INSENSITIVE)
                            .matcher(GcTeamcommConverter.class.getResource("GcTeamcommConverter.class").getPath());
        applicationPath = mt.matches() ? mt.group(3)+"/" : "";
        // load team config
        TEAM_NAMES = Collections.unmodifiableMap(loadTeams(applicationPath + "gc/teams.cfg"));
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
        Set<Integer> args_teams = new HashSet<>();
        // init converter & file container
        ArrayList<Class<? extends FileConverter>> converter = new ArrayList<>();
        ArrayList<File> files = new ArrayList<>();
        
        // parse arguments
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
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
            } else if(arg.equals("--list-gc")) {
                if(gc.isEmpty()) {
                    System.err.println("No GameController found!");
                } else {
                    gc.forEach((t) -> {
                        System.out.println("Found GameController: " + ((GcClassLoader)t).getName());
                    });
                }
                return;
            } else if(arg.equals("--list-teams")) {
                if(TEAM_NAMES.isEmpty()) {
                    System.err.println("No team infos available!");
                } else {
                    TEAM_NAMES.forEach((id, name) -> {
                        System.out.println(String.format("%3d - %s", id, name));
                    });
                }
                return;
            } else if(arg.equals("--teams")) {
                args_teams = Arrays.asList(args[++i].split(",|\\s")).stream().map((t) -> {
                    try {
                        return Integer.parseInt(t);
                    } catch (NumberFormatException e) {
                        System.err.println("Invalid team number '" + t + "', ignoring!");
                    }
                    return -1;
                }).filter((n) -> {
                    return n >= 0;
                }).collect(Collectors.toSet());
            } else {
                // treat argument as file/directory
                args_files.add(arg);
            }
        } // END for(args)
        
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
            for (File file : files) {
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
                    for (FileConverter conv : converterObj) {
                        System.out.println("convert '" + file.getAbsolutePath() + "' to '" + file.getAbsoluteFile() + conv.getExtension() + "'");
                        
                        // select teams, except for raw converteer
                        if(conv instanceof FileConverterRaw) {
                            conv.setTeams(lf.getTeams());
                        } else if(!args_teams.isEmpty()) {
                            conv.setTeams(args_teams);
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
                    } // END for(converter)
                }
            } // END for(files)
        }
    } // END main()
    
    private static void printHelp() {
        System.out.println("Converts TeamCommunication log files of the GameController to JSON file(s).\n"
                + "Usage: java -jar GcTeamcommConverter.jar [--raw] [--tc] [--gtc] <File|Directory>\n"
                + "\t-h|--help\tshows this help message\n"
                + "\t--teams\tset the team numbers, which messages should be parsed (eg. \"4,0\")\n"
                + "\t--raw\tconverts log file 'as-is' to json with extension '.raw.json'\n"
                + "\t--tc\tconverts log file team communication to json (specific data only) with extension '.tc.json'\n"
                + "\t--gtc\tconverts log file gamecontroller and team communication to json (specific data only) with extension '.gtc.json'\n"
                + "\t--all\tby default files containing the substrings 'initial' and 'finished' are not converted, with this option they get converted too\n"
                + "\t--list-gc\tlists the found gamecontroller jars\n"
                + "\t--list-teams\tlists the found teams from the team config\n"
        );
    } // END printHelp()
    
    /**
     * Creates class loader for all jar files in the 'gc' directory.
     * 
     * @return a list of class loaders
     */
    private static List<ClassLoader> loadGameControllers() {
        File gc = new File(applicationPath + "gc");
        List<ClassLoader> gamecontrollers = new ArrayList<>();
        if(gc.isDirectory()) {
            // iterate through files
            for (File jar : gc.listFiles()) {
                // 'accept' only jar files
                if(jar.isFile() && jar.getAbsolutePath().endsWith(".jar")) {
                    try {
                        gamecontrollers.add(new GcClassLoader(jar));
                    } catch (SecurityException | IllegalArgumentException ex) {
                        Logger.getLogger(GcTeamcommConverter.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }
            }
        }
        return gamecontrollers;
    } // END loadGameControllers()

    /**
     * Reads the names of all teams in the config file and returns a map of team id and team name.
     * NOTE: This was copied from "Gamecontroller.data.Teams".
     * 
     * @param file the config file with team names to read
     * @return the id/name map of the teams
     */
    private static Map<Integer, String> loadTeams(String file) {
        Map<Integer, String> teams = new HashMap<>();
        BufferedReader br = null;
        try {
            InputStream inStream = new FileInputStream(file);
            br = new BufferedReader(new InputStreamReader(inStream, "UTF-8"));
            String line;
            while ((line = br.readLine()) != null) {
                final String[] entry = line.split("=", 2);
                if (entry.length == 2) {
                    int key = -1;
                    try {
                        key = Integer.valueOf(entry[0]);
                    } catch (NumberFormatException e) { /* ignore */ }
                    if (key >= 0) {
                        final String[] values = entry[1].split(",");
                        teams.put(key, values[0]);
                    } else {
                        System.err.println("error in teams.cfg: \"" + entry[0] + "\" is not a valid team number");
                    }
                } else if (!line.trim().isEmpty()) {
                    System.err.println("malformed entry in teams.cfg: \"" + line + "\"");
                }
            }
        } catch (IOException e) {
            System.err.println("cannot load " + file);
        } finally {
            if (br != null) {
                try {
                    br.close();
                } catch (IOException e) { /* ignore */ }
            }
        }

        return teams;
    }

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
