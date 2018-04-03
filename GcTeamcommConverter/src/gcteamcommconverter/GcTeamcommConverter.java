package gcteamcommconverter;

import gcteamcommconverter.FileConverter.FileConverterRaw;
import gcteamcommconverter.FileConverter.FileConverterTC;
import gcteamcommconverter.FileConverter.FileConverter;
import gcteamcommconverter.FileConverter.FileConverterGTC;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GcTeamcommConverter
{
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // create class loaders for gamecontroller jars
        List<ClassLoader> gc = loadGameControllers();
        // init converter & file container
        ArrayList<Class<? extends FileConverter>> converter = new ArrayList<>();
        ArrayList<File> files = new ArrayList<>();
        
        for (String arg : args) {
            // parse application options
            if(arg.equals("--raw")) {
                converter.add(FileConverterRaw.class);
                continue;
            } else if(arg.equals("--tc")) {
                converter.add(FileConverterTC.class);
                continue;
            } else if(arg.equals("--gtc")) {
                converter.add(FileConverterGTC.class);
                continue;
            } else if(arg.equals("--help")||arg.equals("-h")) {
                files.clear();
                converter.clear();
                break;
            }
            
            // treat argument as file/directory
            File f = new File(arg);
            if(f.exists()) {
                if(f.isDirectory()) {
                    try (Stream<Path> paths = Files.walk(f.toPath())) {
                        paths.forEach((Path t) -> {
                            File df = t.toFile();
                            if(df.exists() && df.isFile() && df.getName().endsWith(".log")) {
                                files.add(df);
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
        }
        
        if(files.isEmpty() || converter.isEmpty()) {
            printHelp();
        } else {
            converter.forEach((cls) -> {
                files.forEach((file) -> {
                    try {
                        FileConverter fc = cls.getConstructor(File.class).newInstance(file);
                        fc.setGameControllers(gc);
                        fc.convertFile();
                    } catch (IllegalAccessException | IllegalArgumentException | InstantiationException | NoSuchMethodException | SecurityException | InvocationTargetException ex) {
                        Logger.getLogger(GcTeamcommConverter.class.getName()).log(Level.SEVERE, null, ex);
                    }
                });
            });
        }
    }
    
    private static void printHelp() {
        System.out.println("Converts TeamCommunication log files of the GameController to JSON file(s).\n"
                + "Usage: java -jar GcTeamcommConverter.jar [--raw] [--tc] [--gtc] <File|Directory>\n"
                + "\t-h|--help\tshows this help message\n"
                + "\t--raw\tconverts log file 'as-is' to json with extension '.raw.json'\n"
                + "\t--tc\tconverts log file team communication to json (specific data only) with extension '.tc.json'\n"
                + "\t--gtc\tconverts log file gamecontroller and team communication to json (specific data only) with extension '.gtc.json'\n"
        );
    }
    
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
                        gamecontrollers.add(new URLClassLoader(new URL[]{ jar.toURL() }));
                        System.out.println("Found GameController: " + jar.getName());
                    } catch (MalformedURLException | SecurityException | IllegalArgumentException ex) {
                        Logger.getLogger(GcTeamcommConverter.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }
            }
        }
        return gamecontrollers;
    }
}
