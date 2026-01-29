import exifread
import sys

def check(path):
    with open(path, 'rb') as f:
        tags = exifread.process_file(f)
        if tags:
            print(f"Metadata found in {path}:")
            for tag in tags.keys():
                if 'EXIF' in tag:
                    print(f"  {tag}: {tags[tag]}")
        else:
            print(f"No metadata in {path}")

if __name__ == "__main__":
    check(sys.argv[1])
