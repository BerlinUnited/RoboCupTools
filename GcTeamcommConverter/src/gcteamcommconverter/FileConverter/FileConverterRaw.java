package gcteamcommconverter.FileConverter;

import java.io.File;

/**
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
public class FileConverterRaw extends FileConverter
{
    public FileConverterRaw(File f) {
        super(f, ".raw.json");
        selectTeams = false;
    }

    @Override
    protected Object convertAndFilter(long t, Object o) {
        return new DataObject(t, o);
    }
}
