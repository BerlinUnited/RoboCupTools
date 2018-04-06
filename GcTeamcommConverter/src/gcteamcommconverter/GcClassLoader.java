package gcteamcommconverter;

import java.io.File;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLClassLoader;

/**
 * Wrapper for the URLClassLoader.
 * Just to add some useful fields/methods.
 * 
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GcClassLoader extends URLClassLoader
{
    /** The name of the used jar file. */
    private String name;

    /**
     * Constructor.
     * In addition to the URLClassLoader, the name of this file, the url is pointing to, is set.
     * 
     * @param u url to the jar file which should be used by this class loader
     */
    public GcClassLoader(URL u) {
        super(new URL[]{ u });
        
        try {
            name = (new File(u.toURI())).getName();
        } catch (URISyntaxException ex) {}
    }

    /**
     * Constructor.
     * In addition to the URLClassLoader, the name of this file is set.
     * 
     * @param f jar file which should be used by this class loader
     */
    public GcClassLoader(File f) {
        super(new URL[]{});
        try {
            addURL(f.toURL());
        } catch (Exception e) {}
        
        name = f.getName();
    }
    
    /**
     * Returns the name of the underlying jar file for this class loader.
     * 
     * @return name of the jar file
     */
    public final String getName() {
        return name;
    }
}
