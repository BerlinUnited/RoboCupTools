package gcteamcommconverter;

import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectStreamClass;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class GcInputStream extends ObjectInputStream
{
    private final ClassLoader loader;
    private String requiredClass;
    private Set<String> requiredClassFields;
    private boolean requiredSatisfied = false;

    /**
     * 
     * @param in
     * @param gc
     * @throws IOException 
     */
    public GcInputStream(InputStream in, ClassLoader gc) throws IOException {
        super(in);
        loader = gc;
    }
    
    /**
     * 
     * @param clz
     * @throws ClassNotFoundException 
     */
    public void setRequiredClass(String clz) throws ClassNotFoundException {
        //
        Class<?> c = Class.forName(clz, false, loader);
        Set<String> fields = new HashSet<>();
        for (Field field : c.getFields()) {
            // only public non-static fields are serialized
            if(field.getDeclaringClass().getName().equals(clz)
                    && Modifier.isPublic(field.getModifiers()) 
                    && !Modifier.isStatic(field.getModifiers())) {
                fields.add(field.getName());
            }
        }
        requiredClassFields = fields;
        requiredClass = clz;
    }

    /**
     * 
     * @return 
     */
    public boolean isRequiredSatisfied() {
        return requiredSatisfied;
    }
    
    /**
     * 
     * @param desc
     * @return
     * @throws IOException
     * @throws ClassNotFoundException 
     */
    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        // only if set, check required
        if(requiredClass != null) {
            Set<String> s = Arrays.stream(desc.getFields()).map((t) -> { return t.getName(); }).collect(Collectors.toSet());
            if(s.containsAll(requiredClassFields)) {
                requiredSatisfied = true;
            }
        }
        
        return Class.forName(desc.getName(), false, loader);
    }
}
