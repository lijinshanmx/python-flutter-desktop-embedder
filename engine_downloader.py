import os
import platform
import re
import subprocess
import zipfile
from contextlib import closing

import requests

storage_china_domain = "https://storage.flutter-io.cn"
storage_default_domain = "https://storage.googleapis.com"


def create_symlink(symlink, file):
    os.symlink(file, symlink)


def unzip(src, dest):
    file_path, _ = os.path.split(dest)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    f = zipfile.ZipFile(src)
    for file in f.namelist():
        f.extract(file, dest)
    f.close()


def ask_for_confirmation():
    while True:
        response = input('Would you like to overwrite the previously downloaded engine [Y/n] : ')
        overwrite = response.lower()
        if overwrite.lower() == 'y' or overwrite == 'yes' or overwrite == '':
            return True
        elif overwrite == 'n' or overwrite == 'no':
            return False


def ask_for_location_china_confirmation():
    while True:
        response = input('Is your current location in China【你的当前位置是在中国吗?】? [Y/n] : ')
        overwrite = response.lower()
        if overwrite.lower() == 'y' or overwrite == 'yes' or overwrite == '':
            return True
        elif overwrite == 'n' or overwrite == 'no':
            return False


def download_file(file_url, file_path):
    file_parent_path, _ = os.path.split(file_path)
    if not os.path.exists(file_parent_path):
        os.makedirs(file_parent_path)
    with closing(requests.get(file_url, stream=True)) as response:
        if response.status_code != 200:
            return False
        chunk_size = 1024
        content_size = int(response.headers['content-length'])
        data_count = 0
        with open(file_path, "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                data_count = data_count + len(data)
                now_jd = (data_count / content_size) * 100
                print("\rDownload progress：%d%%(%d/%d) - %s" % (now_jd, data_count, content_size, file_path), end=" ")
        return True


def run_engine_download():
    china = ask_for_location_china_confirmation()
    if china:
        targeted_domain = storage_china_domain
    else:
        targeted_domain = storage_default_domain
    p = subprocess.Popen("flutter --version", shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    short_revision = None
    for line in out.splitlines():
        if 'Engine • revision' in line.decode():
            match = re.match('Engine • revision (\\w{10})', line.decode())
            if match:
                short_revision = match.group(1)

    if short_revision:
        print('Get Engine • revision success, the revision is : %s!' % short_revision)
    else:
        print('Get Engine • revision fail!')
        return

    r = requests.get('https://api.github.com/search/commits?q=7112b72cc2',
                     headers={'Accept': 'application/vnd.github.cloak-preview'})
    engine_sha = r.json()['items'][0]['sha']
    os_name = platform.system().lower()
    download_icu_dtl_url = '%s/flutter_infra/flutter/%s/%s/artifacts.zip'
    if os_name == 'darwin':
        download_share_library_url = '%s/flutter_infra/flutter/%s/%s/FlutterEmbedder.framework.zip'
        platform_name = 'darwin-x64'
    elif os_name == 'linux':
        download_share_library_url = '%s/flutter_infra/flutter/%s/%s/linux-x64-embedder'
        platform_name = 'linux-x64'
    elif os_name == 'windows':
        download_share_library_url = '%s/flutter_infra/flutter/%s/%s/windows-x64-embedder.zip'
        platform_name = 'windows-x64'
    else:
        print('OS not supported')
        return
    download_share_library_url = download_share_library_url % (targeted_domain, engine_sha, platform_name)
    download_icu_dtl_url = download_icu_dtl_url % (targeted_domain, engine_sha, platform_name)
    current_dir = os.getcwd()
    build_path = '%s/.build' % current_dir
    temp_file_path = os.path.join(build_path, 'temp.zip')
    success = download_file(download_share_library_url, temp_file_path)
    if success:
        print()
        print('Downloaded embedder for %s platform, matching version : %s' % (platform_name, engine_sha))
    else:
        print('Downloaded embedder error!')
        return
    artifacts_file_path = os.path.join(build_path, 'artifacts.zip')
    success = download_file(download_icu_dtl_url, artifacts_file_path)
    if success:
        print()
        print('Downloaded artifact for %s platform.' % engine_sha)
    else:
        print()
        print('Downloaded artifact error!')
        return
    dependencies_path = os.path.join(os.getcwd(), 'dependencies')
    if not os.path.exists(dependencies_path):
        os.makedirs(dependencies_path)
    # unzip files
    unzip(temp_file_path, build_path)
    if os_name == 'darwin':
        unzip(os.path.join(build_path, 'FlutterEmbedder.framework.zip'),
              os.path.join(build_path, 'FlutterEmbedder.framework'))
        os.rename(os.path.join(build_path, 'FlutterEmbedder.framework/Versions/A/FlutterEmbedder'),
                  os.path.join(os.getcwd(), 'dependencies/flutter_engine'))
    elif os_name == 'linux':
        os.rename(os.path.join(build_path, 'libflutter_engine.so'),
                  os.path.join(os.getcwd(), 'dependencies/libflutter_engine.so'))
    elif os_name == 'windows':
        os.rename(os.path.join(build_path, 'flutter_engine.dll'),
                  os.path.join(os.getcwd(), 'dependencies/flutter_engine.dll'))
    unzip(artifacts_file_path, os.path.join(build_path, 'artifacts'))
    os.rename(os.path.join(build_path, 'artifacts/icudtl.dat'), os.path.join(os.getcwd(), 'dependencies/icudtl.dat'))
    print('Unzipped files success and moved engine and icudtl files to dependencies directory.')
    print('Done.')


run_engine_download()
