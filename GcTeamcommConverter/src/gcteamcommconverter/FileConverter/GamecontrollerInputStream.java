package gcteamcommconverter.FileConverter;

import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectStreamClass;
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GamecontrollerInputStream extends ObjectInputStream
{
    List<ClassLoader> loaders = new ArrayList<>();
    ClassLoader usedLoader = null;

    public GamecontrollerInputStream(InputStream in) throws IOException {
        super(in);
    }
    
    public void setGameControllers(List<ClassLoader> gc) {
        loaders = gc;
    }
    
    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        Class<?> c = null;
        if(usedLoader == null) {
            c = findLoaderFor(desc.getName());
        } else {
            c = loadWith(usedLoader, desc.getName());
        }
        
        if(c != null) {
            return c;
        }
        
        // non of "our" loaders
        usedLoader = null;
        
        // try to use default loader(s)
        return super.resolveClass(desc);
    }
    
    private Class<?> findLoaderFor(String name) {
        for (ClassLoader loader : loaders) {
            Class<?> c = loadWith(loader, name);
            if(c != null) {
                usedLoader = loader;
                return c;
            }
        }
        return null;
    }
    
    private Class<?> loadWith(ClassLoader l, String n) {
        try {
            return Class.forName(n, false, l);
        } catch (ClassNotFoundException ex) { /* ignore */ }
        return null;
    }
}
