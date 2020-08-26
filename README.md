# Recogito Bulk Utils

A collection of scripts for automating document & annotation management operations in Recogito.

## Configure

1. Change into the `scripts` folder
2. Create a copy of the file `config.py.template` named `config.py`
3. Adapt `config.py` according to your environment

## Scripts

Run scripts with `python <scriptname>`. Scripts require Python 3 installed on your system.

### `upload`

Bulk-upload documents to your Recogito workspace. The script reads from a folder. Create 
__one subfolder for each document__ and add files to the subfolder. The script will create 
one document for each folder, using the folder name as the document title.

Example: the directory structure below will create two documents in Recogito ('palette-01' and 
'palette-02'), with 3 and 4 image parts, respectively.

```
- uploads
  |- palette-01
    |- image-01.jpg
    |- image-02.jpg
    |- image-03.jpg
  |- palette-02
    |- image-01.jpg
    |- image-02.jpg
    |- image-03.jpg
    |- image-04.jpg
```

In addition, the script will share each document with the configured list of user accounts, and
upload the configured tagging vocabulary.

### `check_progress`

A helper script to check annotation progress on the documents in your workspace.

### `download`

A helper script to bulk-download the annotations from the documents in your workspace

### `delete`

A helper script to bulk-delete the documents from your workspace

