package gcteamcommconverter.FileConverter;

import gcteamcommconverter.data.DataObject;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class FileConverterRaw extends FileConverter
{
    /**
     * Returns the extension, which should be used to write the converted data of this FileConverter.
     * 
     * @return the file extension ".raw.json"
     */
    @Override
    public final String getExtension() {
        return ".raw.json";
    }

    /**
     * Returns the log object 'as is' without any filtering or modifications.
     * 
     * @param t the timestamp of this log object
     * @param o the log object
     * @return the log object as DataObject
     */
    @Override
    public Object convertAndFilter(long t, Object o) {
        return new DataObject(t, o);
    }
}
