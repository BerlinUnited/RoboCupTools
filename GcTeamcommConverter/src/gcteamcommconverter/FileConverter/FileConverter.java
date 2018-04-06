package gcteamcommconverter.FileConverter;

import java.util.HashSet;
import java.util.Set;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public abstract class FileConverter
{
    /** The team numbers which can be used by subclassed FileConverter. */
    protected Set<Integer> teams = new HashSet<>();

    /**
     * Converts the given Object o to another.
     * 
     * @param t the timestamp of this log object
     * @param o the log object
     * @return a 'converted' object
     */
    abstract public Object convertAndFilter(long t, Object o);
    
    /**
     * Returns the extension, which should be used to write the converted data of this FileConverter.
     * 
     * @return the file extension
     */
    abstract public String getExtension();
    
    /**
     * Sets the team numbers, which can be used by subclassed FileConverter.
     * 
     * @param teams set of team numbers
     */
    public void setTeams(Set<Integer> teams) {
        this.teams = teams;
    }
}
