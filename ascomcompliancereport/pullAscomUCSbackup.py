import requests
import time
import shutil
import tarfile
import gzip
import os
import tempfile
import copy
from pathlib import Path

loginUri = "https://AscomServer/phpgui/login.php"
backupUri = "https://AscomServer/cgi-bin/admin/getbackup"
payload = {"username": "", "password": ""}
# headers = {"Content-Type":"multipart/form-data"}
filename = "{}_unite_communication_server-1.5.0-backup".format(time.strftime("%Y%m%d%H%M%S"))
downloadDir = "download/src/"
gzip_suffix = ".gzip"
tar_suffix = ".tar"
gzipRaw = None

def main():
    local_filename = Path(downloadDir, filename).with_suffix(gzip_suffix)
    # print("DownloadFile: {}".format(local_filename))
    # print(loginUri)
    with tempfile.TemporaryDirectory() as tmpdir:
        with requests.Session() as session:
            post = session.post(loginUri, data=payload, verify=False)
            with session.get(backupUri, verify=False, stream=True) as r:
                with open(Path(tmpdir,filename).with_suffix(gzip_suffix), "wb") as f:
                    shutil.copyfileobj(r.raw, f)

                with gzip.open(Path(tmpdir,filename).with_suffix(gzip_suffix), 'rb') as gz:
                    content = gz.read()

                    with open(Path(tmpdir,filename).with_suffix(tar_suffix), 'wb') as f:
                        f.write(content)

                    tar = tarfile.open(Path(tmpdir,filename).with_suffix(tar_suffix), mode='r')
                    def is_within_directory(directory, target):
                        
                        abs_directory = os.path.abspath(directory)
                        abs_target = os.path.abspath(target)
                    
                        prefix = os.path.commonprefix([abs_directory, abs_target])
                        
                        return prefix == abs_directory
                    
                    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                    
                        for member in tar.getmembers():
                            member_path = os.path.join(path, member.name)
                            if not is_within_directory(path, member_path):
                                raise Exception("Attempted Path Traversal in Tar File")
                    
                        tar.extractall(path, members, numeric_owner=numeric_owner) 
                        
                    
                    safe_extract(tar, path=Path(downloadDir,filename))
          
        requests.session().close()
# Mount sqlite

# query sqlite

# process query results


if __name__ == "__main__":
    main()
