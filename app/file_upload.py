from flask import url_for
from pathlib import Path
from werkzeug import secure_filename

import uuid

import config


class FileUpload:
    '''
    Represents a file to be uploaded or an already uploaded file,
    provides various helper functions to deal with them. Note this
    object is not thread safe so each file should only ever have a
    single object
    '''
    UUID_LEN = len(str(uuid.uuid4()))
    UPLOAD_DIR = Path(config.STATIC_PATH) / Path(config.FILE_UPLOAD_DIR)

    def __init__(self, req=None, filename=None):
        '''
        If given a request object will treat it as a file which should
        be uploaded, will clean the path and generate an UUID for it
        Will not save the uploaded file till get_size or commit is
        called. If given a filename, treated as a file which has
        already been uploaded will verify that the file exists before
        creating the object.
        '''
        if req:
            FileUpload.UPLOAD_DIR.mkdir(exist_ok=True)
            sent_file = req.files['file']
            file_id = str(uuid.uuid4())
            sec_name = secure_filename(sent_file.filename)
            name = f'{file_id}{sec_name}'
            self.path = FileUpload.UPLOAD_DIR / Path(name)
            self.commited = False
            self.sent_file = req.files['file']
        if filename:
            name = Path(filename).name
            self.path = FileUpload.UPLOAD_DIR / Path(name)
            if not self.path.exists():
                raise LookupError(f"Path {filename} doesn't exist!")
            self.commited = True

    def commit(self):
        '''
        Will save the uploaded file
        '''
        if not self.commited:
            self.sent_file.save(str(self.get_path()))
            self.commited = True
            self.sent_file = None

    def get_original_name(self):
        '''
        Return the original name of the file, ie strip the uuid at the
        front
        '''
        return self.get_name()[FileUpload.UUID_LEN:]

    def get_name(self):
        '''
        Returns the name of the file as stored, so including the UUID
        '''
        return self.path.name

    def get_path(self):
        '''
        Return the path object which is associated with the file,
        includes the config.FILE_UPLOAD_DIR
        '''
        return self.path

    def get_url(self):
        '''
        Returns the public url for this file
        '''
        p = Path('.')
        for part in self.path.parts[1:]:
            p = p / part
        return url_for(config.STATIC_PATH, filename=p.as_posix())

    def get_size(self):
        '''
        Return the size of the file in MiB
        '''
        self.commit()
        return self.path.stat().st_size / 1024 / 1024

    def get_extention(self):
        '''
        Return the extension of the file
        '''
        return self.path.suffix

    def remove_file(self):
        '''
        Will delete the file that this object represents, shouldn't be
        used after this
        '''
        self.path.unlink()
        self.path = None
