import exifread
import os

path = '/Volumes/Extended-1TB/Sony_Test_Sandbox/DSC00504.ARW'
with open(path, 'rb') as f:
    tags = exifread.process_file(f, details=False)
    
print(f"Audit for {os.path.basename(path)}:")
for tag, val in tags.items():
    if any(k in tag for k in ['JPEG', 'Thumbnail', 'Preview']):
        if 'JPEGInterchangeFormatLength' in tag:
            name = tag.replace('Length', '')
            length = int(val.values[0])
            print(f" - {name}: {length/1024:.1f} KB")
        elif tag == 'JPEGThumbnail' or tag == 'PreviewImage':
            length = len(val.values)
            print(f" - {tag}: {length/1024:.1f} KB")
